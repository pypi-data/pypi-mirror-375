"""Task repository for the task queue."""

from collections.abc import Callable

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kodit.domain.entities import Task
from kodit.domain.protocols import TaskRepository
from kodit.domain.value_objects import TaskType
from kodit.infrastructure.mappers.task_mapper import TaskMapper, TaskTypeMapper
from kodit.infrastructure.sqlalchemy import entities as db_entities
from kodit.infrastructure.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork


def create_task_repository(
    session_factory: Callable[[], AsyncSession],
) -> TaskRepository:
    """Create an index repository."""
    uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
    return SqlAlchemyTaskRepository(uow)


class SqlAlchemyTaskRepository(TaskRepository):
    """Repository for task persistence using the existing Task entity."""

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        """Initialize the repository."""
        self.uow = uow
        self.log = structlog.get_logger(__name__)

    async def add(
        self,
        task: Task,
    ) -> None:
        """Create a new task in the database."""
        async with self.uow:
            self.uow.session.add(TaskMapper.from_domain_task(task))

    async def get(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        async with self.uow:
            stmt = select(db_entities.Task).where(db_entities.Task.dedup_key == task_id)
            result = await self.uow.session.execute(stmt)
            db_task = result.scalar_one_or_none()
            if not db_task:
                return None
            return TaskMapper.to_domain_task(db_task)

    async def take(self) -> Task | None:
        """Take a task for processing and remove it from the database."""
        async with self.uow:
            stmt = (
                select(db_entities.Task)
                .order_by(db_entities.Task.priority.desc(), db_entities.Task.created_at)
                .limit(1)
            )
            result = await self.uow.session.execute(stmt)
            db_task = result.scalar_one_or_none()
            if not db_task:
                return None
            await self.uow.session.delete(db_task)
            return TaskMapper.to_domain_task(db_task)

    async def update(self, task: Task) -> None:
        """Update a task in the database."""
        async with self.uow:
            stmt = select(db_entities.Task).where(db_entities.Task.dedup_key == task.id)
            result = await self.uow.session.execute(stmt)
            db_task = result.scalar_one_or_none()

            if not db_task:
                raise ValueError(f"Task not found: {task.id}")

            db_task.priority = task.priority
            db_task.payload = task.payload

    async def list(self, task_type: TaskType | None = None) -> list[Task]:
        """List tasks with optional status filter."""
        async with self.uow:
            stmt = select(db_entities.Task)

            if task_type:
                stmt = stmt.where(
                    db_entities.Task.type == TaskTypeMapper.from_domain_type(task_type)
                )

            stmt = stmt.order_by(
                db_entities.Task.priority.desc(), db_entities.Task.created_at
            )

            result = await self.uow.session.execute(stmt)
            records = result.scalars().all()

            # Convert to domain entities
            return [TaskMapper.to_domain_task(record) for record in records]
