from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from models import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    due_at: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title is required")
        if len(v.strip()) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return v.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_at: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("title is required")
        if len(v.strip()) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return v.strip()


class TaskListItem(BaseModel):
    # description 제외 — 목록 성능 최적화 (02-specs 참고)
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TaskStatus
    due_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    due_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
