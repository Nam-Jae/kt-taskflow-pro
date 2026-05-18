import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from database import Base


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo, nullable=False)
    due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, nullable=False)
