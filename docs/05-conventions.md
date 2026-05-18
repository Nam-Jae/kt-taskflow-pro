# 05-conventions — 협업 규칙

## 폴더 구조

```
taskflow-pro/
├── backend/
│   ├── main.py            # FastAPI 앱 진입점, CORS 설정
│   ├── database.py        # SQLAlchemy 엔진·세션·Base
│   ├── models.py          # ORM 모델 (Task)
│   ├── schemas.py         # Pydantic 스키마
│   └── routers/
│       └── tasks.py       # /api/tasks 라우터
├── frontend/
│   ├── index.html         # 단일 HTML 진입점
│   └── app.js             # 전체 Vanilla JS 로직
├── docs/
│   ├── 00-overview.md
│   ├── 01-product.md
│   ├── 02-specs.md
│   ├── 03-design.md
│   ├── 04-tasks.md
│   └── 05-conventions.md
├── .env.example           # 환경 변수 템플릿 (값 없음, 커밋 허용)
├── .gitignore
├── requirements.txt
└── CLAUDE.md
```

> 이 구조는 `docs/03-design.md` 의존성 정책에 따라 사전 승인 없이 변경하지 않는다.

---

## 명명 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| Python 변수·함수·파일명 | `snake_case` | `task_id`, `get_task_list`, `database.py` |
| JS 변수·함수 | `camelCase` | `taskId`, `getTaskList`, `dueAt` |
| JS/HTML 컴포넌트 함수 | `PascalCase` | `TaskCard()`, `EditModal()` |
| CSS 클래스 (커스텀) | `kebab-case` | `.task-card`, `.status-badge` |
| 환경 변수 | `SCREAMING_SNAKE_CASE` | `DATABASE_URL`, `SECRET_KEY` |

- **식별자는 영어**로만 작성한다 (변수명·함수명·파일명·클래스명 모두 포함).
- **주석은 한국어**로만 작성한다. 영어 주석은 허용하지 않는다.
- 주석은 WHY(왜)를 설명할 때만 작성한다. WHAT(무엇)은 코드 자체로 표현한다.

---

## 금지 사항

| 금지 | 이유 | 대안 |
|------|------|------|
| `print()` 디버깅 | 운영 환경 노이즈, 민감 정보 노출 위험 | `logging` 모듈 + 레벨 (`DEBUG`/`INFO`/`ERROR`) 사용 |
| `bare except:` | 모든 예외를 삼켜 디버깅 불가 | `except SpecificError as e:` 로 예외 범위 명시 |
| 비밀번호·API 키 하드코딩 | 깃 히스토리에 영구 기록 → 보안사고 | `.env` 파일 + `os.getenv("KEY")` 사용, `.env`는 `.gitignore` 등록 |
| TypeScript `any` 타입 | 타입 검사 무력화, 의미 상실 | 명시적 타입 또는 `unknown` 후 타입 가드 사용 |
| CSS `!important` | 우선순위 충돌·디버깅 불가 | Tailwind 유틸리티 클래스 조합 또는 셀렉터 구체성 개선 |

---

## 테스트 규칙

- **프레임워크**: `pytest` + FastAPI `TestClient`
- 모든 API 엔드포인트는 아래 두 케이스를 **반드시** 포함한다:

| 케이스 | 확인 항목 |
|--------|-----------|
| 정상 케이스 | 올바른 HTTP 상태코드 + 응답 필드 검증 |
| 400 케이스 | 잘못된 입력 시 `400 Bad Request` + `"error"` 키 존재 확인 |
| 404 케이스 | 존재하지 않는 `id` 요청 시 `404 Not Found` 확인 |

- 테스트 파일 위치: `backend/tests/test_tasks.py`
- 테스트 없이 구현 완료로 간주하지 않는다 (절대 규칙 #3).

---

## Git 커밋 규칙

### 커밋 메시지 형식

```
<type>: <한국어 요약>
```

### 타입 목록

| 타입 | 사용 상황 |
|------|-----------|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 작성·수정 |
| `refactor` | 동작 변경 없는 코드 개선 |
| `test` | 테스트 추가·수정 |
| `chore` | 빌드·설정·의존성 관리 |

### 예시

```
feat: Task 삭제 API 구현
fix: due_at 시간대 변환 오류 수정
docs: 02-specs API 응답 예시 보완
test: Task 생성 400 케이스 테스트 추가
chore: requirements.txt sqlalchemy 버전 고정
```

### 브랜치 전략 (MVP)

- `main` — 항상 동작하는 상태 유지
- 기능 개발은 `feat/<작업명>` 브랜치에서 진행 후 `main`에 병합
- MVP 기간에는 직접 `main` 푸시 허용 (1인 개발 기준)
