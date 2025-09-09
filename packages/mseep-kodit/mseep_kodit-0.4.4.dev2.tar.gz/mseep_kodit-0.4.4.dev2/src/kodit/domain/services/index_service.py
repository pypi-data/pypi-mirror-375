"""Pure domain service for Index aggregate operations."""

from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

import structlog
from pydantic import AnyUrl

import kodit.domain.entities as domain_entities
from kodit.application.factories.reporting_factory import create_noop_operation
from kodit.application.services.reporting import ProgressTracker
from kodit.domain.services.enrichment_service import EnrichmentDomainService
from kodit.domain.value_objects import (
    EnrichmentIndexRequest,
    EnrichmentRequest,
    FileProcessingStatus,
    LanguageMapping,
)
from kodit.infrastructure.cloning.git.working_copy import GitWorkingCopyProvider
from kodit.infrastructure.cloning.metadata import FileMetadataExtractor
from kodit.infrastructure.git.git_utils import is_valid_clone_target
from kodit.infrastructure.ignore.ignore_pattern_provider import GitIgnorePatternProvider
from kodit.infrastructure.slicing.slicer import Slicer
from kodit.utils.path_utils import path_from_uri


class LanguageDetectionService(ABC):
    """Abstract interface for language detection service."""

    @abstractmethod
    async def detect_language(self, file_path: Path) -> str:
        """Detect the programming language of a file."""


class IndexDomainService:
    """Pure domain service for Index aggregate operations.

    This service handles the full lifecycle of code indexing:
    - Creating indexes for source repositories
    - Cloning and processing source files
    - Extracting and enriching code snippets
    - Managing the complete Index aggregate
    """

    def __init__(
        self,
        language_detector: LanguageDetectionService,
        enrichment_service: EnrichmentDomainService,
        clone_dir: Path,
    ) -> None:
        """Initialize the index domain service."""
        self._clone_dir = clone_dir
        self._language_detector = language_detector
        self._enrichment_service = enrichment_service
        self.log = structlog.get_logger(__name__)

    async def prepare_index(
        self,
        uri_or_path_like: str,  # Must include user/pass, etc
        step: ProgressTracker | None = None,
    ) -> domain_entities.WorkingCopy:
        """Prepare an index by scanning files and creating working copy."""
        step = step or create_noop_operation()
        self.log.info("Preparing index")
        sanitized_uri, source_type = self.sanitize_uri(uri_or_path_like)
        self.log.info("Preparing source", uri=str(sanitized_uri))

        if source_type == domain_entities.SourceType.FOLDER:
            local_path = path_from_uri(str(sanitized_uri))
        elif source_type == domain_entities.SourceType.GIT:
            source_type = domain_entities.SourceType.GIT
            git_working_copy_provider = GitWorkingCopyProvider(self._clone_dir)
            local_path = await git_working_copy_provider.prepare(uri_or_path_like, step)
        else:
            raise ValueError(f"Unsupported source: {uri_or_path_like}")

        return domain_entities.WorkingCopy(
            remote_uri=sanitized_uri,
            cloned_path=local_path,
            source_type=source_type,
            files=[],
        )

    async def extract_snippets_from_index(
        self,
        index: domain_entities.Index,
        step: ProgressTracker | None = None,
    ) -> domain_entities.Index:
        """Extract code snippets from files in the index."""
        step = step or create_noop_operation()
        file_count = len(index.source.working_copy.files)

        self.log.info(
            "Extracting snippets",
            index_id=index.id,
            file_count=file_count,
        )

        # Only create snippets for files that have been added or modified
        files = index.source.working_copy.changed_files()
        index.delete_snippets_for_files(files)

        # Filter out deleted files - they don't exist on disk anymore
        files = [
            f for f in files if f.file_processing_status != FileProcessingStatus.DELETED
        ]

        # Create a set of languages to extract snippets for
        extensions = {file.extension() for file in files}
        lang_files_map: dict[str, list[domain_entities.File]] = defaultdict(list)
        for ext in extensions:
            try:
                lang = LanguageMapping.get_language_for_extension(ext)
                lang_files_map[lang].extend(
                    file for file in files if file.extension() == ext
                )
            except ValueError as e:
                self.log.debug("Skipping", error=str(e))
                continue

        self.log.info(
            "Languages to process",
            languages=lang_files_map.keys(),
        )

        # Calculate snippets for each language
        slicer = Slicer()
        await step.set_total(len(lang_files_map.keys()))
        for i, (lang, lang_files) in enumerate(lang_files_map.items()):
            await step.set_current(i, f"Extracting snippets for {lang}")
            s = slicer.extract_snippets(lang_files, language=lang)
            index.snippets.extend(s)

        return index

    async def enrich_snippets_in_index(
        self,
        snippets: list[domain_entities.Snippet],
        reporting_step: ProgressTracker | None = None,
    ) -> list[domain_entities.Snippet]:
        """Enrich snippets with AI-generated summaries."""
        reporting_step = reporting_step or create_noop_operation()
        if not snippets or len(snippets) == 0:
            await reporting_step.skip("No snippets to enrich")
            return snippets

        await reporting_step.set_total(len(snippets))
        snippet_map = {snippet.id: snippet for snippet in snippets if snippet.id}

        enrichment_request = EnrichmentIndexRequest(
            requests=[
                EnrichmentRequest(snippet_id=snippet_id, text=snippet.original_text())
                for snippet_id, snippet in snippet_map.items()
            ]
        )

        processed = 0
        async for result in self._enrichment_service.enrich_documents(
            enrichment_request
        ):
            snippet_map[result.snippet_id].add_summary(result.text)

            processed += 1
            await reporting_step.set_current(
                processed, f"Enriching snippets for {processed} snippets"
            )

        return list(snippet_map.values())

    def sanitize_uri(
        self, uri_or_path_like: str
    ) -> tuple[AnyUrl, domain_entities.SourceType]:
        """Convert a URI or path-like string to a URI."""
        # First, check if it's a local directory (more reliable than git check)
        if Path(uri_or_path_like).is_dir():
            return (
                domain_entities.WorkingCopy.sanitize_local_path(uri_or_path_like),
                domain_entities.SourceType.FOLDER,
            )

        # Then check if it's git-clonable
        if is_valid_clone_target(uri_or_path_like):
            return (
                domain_entities.WorkingCopy.sanitize_git_url(uri_or_path_like),
                domain_entities.SourceType.GIT,
            )

        raise ValueError(f"Unsupported source: {uri_or_path_like}")

    async def refresh_working_copy(
        self,
        working_copy: domain_entities.WorkingCopy,
        step: ProgressTracker | None = None,
    ) -> domain_entities.WorkingCopy:
        """Refresh the working copy."""
        step = step or create_noop_operation()
        metadata_extractor = FileMetadataExtractor(working_copy.source_type)
        if working_copy.source_type == domain_entities.SourceType.GIT:
            git_working_copy_provider = GitWorkingCopyProvider(self._clone_dir)
            await git_working_copy_provider.sync(str(working_copy.remote_uri), step)

        current_file_paths = working_copy.list_filesystem_paths(
            GitIgnorePatternProvider(working_copy.cloned_path)
        )

        previous_files_map = {file.as_path(): file for file in working_copy.files}

        # Calculate different sets of files
        deleted_file_paths = set(previous_files_map.keys()) - set(current_file_paths)
        new_file_paths = set(current_file_paths) - set(previous_files_map.keys())
        modified_file_paths = set(current_file_paths) & set(previous_files_map.keys())
        num_files_to_process = (
            len(deleted_file_paths) + len(new_file_paths) + len(modified_file_paths)
        )
        self.log.info(
            "Refreshing working copy",
            num_deleted=len(deleted_file_paths),
            num_new=len(new_file_paths),
            num_modified=len(modified_file_paths),
            num_total_changes=num_files_to_process,
            num_dirty=len(working_copy.dirty_files()),
        )

        # Setup reporter
        processed = 0
        await step.set_total(num_files_to_process)

        # First check to see if any files have been deleted
        for file_path in deleted_file_paths:
            processed += 1
            await step.set_current(processed, f"Deleting file {file_path}")
            previous_files_map[
                file_path
            ].file_processing_status = domain_entities.FileProcessingStatus.DELETED

        # Then check to see if there are any new files
        for file_path in new_file_paths:
            processed += 1
            await step.set_current(processed, f"Adding new file {file_path}")
            try:
                working_copy.files.append(
                    await metadata_extractor.extract(file_path=file_path)
                )
            except (OSError, ValueError) as e:
                self.log.debug("Skipping file", file=str(file_path), error=str(e))
                continue

        # Finally check if there are any modified files
        for file_path in modified_file_paths:
            processed += 1
            await step.set_current(processed, f"Modifying file {file_path}")
            try:
                previous_file = previous_files_map[file_path]
                new_file = await metadata_extractor.extract(file_path=file_path)
                if previous_file.sha256 != new_file.sha256:
                    previous_file.file_processing_status = (
                        domain_entities.FileProcessingStatus.MODIFIED
                    )
            except (OSError, ValueError) as e:
                self.log.info("Skipping file", file=str(file_path), error=str(e))
                continue

        return working_copy

    async def delete_index(self, index: domain_entities.Index) -> None:
        """Delete an index."""
        # Delete the working copy
        index.source.working_copy.delete()
