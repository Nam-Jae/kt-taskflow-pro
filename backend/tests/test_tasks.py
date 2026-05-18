import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main import app
from database import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

# StaticPool: 모든 세션이 동일한 in-memory 연결을 공유 (연결별 독립 DB 문제 방지)
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ── POST /api/tasks ──────────────────────────────────────────────────────────

def test_create_task_success():
    res = client.post("/api/tasks", json={
        "title": "디자인 검토",
        "description": "피그마 확인",
        "status": "todo",
        "due_at": "2026-05-12T18:00:00Z",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "디자인 검토"
    assert data["description"] == "피그마 확인"
    assert data["status"] == "todo"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_without_optional_fields():
    res = client.post("/api/tasks", json={"title": "최소 태스크"})
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "todo"
    assert data["due_at"] is None
    assert data["description"] is None


def test_create_task_missing_title_returns_400():
    res = client.post("/api/tasks", json={"status": "todo"})
    assert res.status_code == 400
    assert "error" in res.json()


def test_create_task_empty_title_returns_400():
    res = client.post("/api/tasks", json={"title": "   "})
    assert res.status_code == 400
    assert res.json()["error"] == "title is required"


def test_create_task_title_too_long_returns_400():
    res = client.post("/api/tasks", json={"title": "a" * 201})
    assert res.status_code == 400
    assert "error" in res.json()


def test_create_task_invalid_status_returns_400():
    res = client.post("/api/tasks", json={"title": "태스크", "status": "invalid"})
    assert res.status_code == 400
    assert "error" in res.json()


def test_create_task_invalid_due_at_returns_400():
    res = client.post("/api/tasks", json={"title": "태스크", "due_at": "not-a-date"})
    assert res.status_code == 400
    assert "error" in res.json()


# ── GET /api/tasks ───────────────────────────────────────────────────────────

def test_list_tasks_empty():
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert res.json() == []


def test_list_tasks_excludes_description():
    client.post("/api/tasks", json={"title": "태스크", "description": "설명"})
    res = client.get("/api/tasks")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert "description" not in items[0]


def test_list_tasks_returns_newest_first():
    client.post("/api/tasks", json={"title": "첫 번째"})
    client.post("/api/tasks", json={"title": "두 번째"})
    res = client.get("/api/tasks")
    assert res.json()[0]["title"] == "두 번째"


# ── GET /api/tasks/{id} ──────────────────────────────────────────────────────

def test_get_task_includes_description():
    create_res = client.post("/api/tasks", json={"title": "태스크", "description": "상세 설명"})
    task_id = create_res.json()["id"]
    res = client.get(f"/api/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["description"] == "상세 설명"


def test_get_task_not_found_returns_404():
    res = client.get("/api/tasks/9999")
    assert res.status_code == 404
    assert res.json()["error"] == "task not found"


# ── PUT /api/tasks/{id} ──────────────────────────────────────────────────────

def test_update_task_partial():
    create_res = client.post("/api/tasks", json={"title": "원본 제목", "status": "todo"})
    task_id = create_res.json()["id"]
    res = client.put(f"/api/tasks/{task_id}", json={"status": "in_progress"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "in_progress"
    assert data["title"] == "원본 제목"  # 변경하지 않은 필드 유지


def test_update_task_updated_at_changes():
    create_res = client.post("/api/tasks", json={"title": "태스크"})
    task = create_res.json()
    res = client.put(f"/api/tasks/{task['id']}", json={"status": "done"})
    assert res.json()["updated_at"] >= task["updated_at"]


def test_update_task_not_found_returns_404():
    res = client.put("/api/tasks/9999", json={"status": "done"})
    assert res.status_code == 404
    assert res.json()["error"] == "task not found"


# ── DELETE /api/tasks/{id} ───────────────────────────────────────────────────

def test_delete_task_success():
    create_res = client.post("/api/tasks", json={"title": "삭제 대상"})
    task_id = create_res.json()["id"]
    res = client.delete(f"/api/tasks/{task_id}")
    assert res.status_code == 204
    # 삭제 후 단건 조회 시 404
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_delete_task_not_found_returns_404():
    res = client.delete("/api/tasks/9999")
    assert res.status_code == 404
    assert res.json()["error"] == "task not found"
