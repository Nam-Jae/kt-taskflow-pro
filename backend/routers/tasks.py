import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        due_at=_to_naive_utc(task_in.due_at),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info("태스크 생성: id=%s title=%s", task.id, task.title)
    return task


@router.get("", response_model=List[TaskListItem])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.created_at.desc()).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, task_id)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    update_data = task_in.model_dump(exclude_unset=True)
    if "due_at" in update_data:
        update_data["due_at"] = _to_naive_utc(update_data["due_at"])
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    db.delete(task)
    db.commit()
    logger.info("태스크 삭제: id=%s", task_id)


def _get_or_404(db: Session, task_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


def _to_naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    # 타임존 정보가 있으면 UTC로 변환 후 naive datetime으로 저장
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt
