# 04-tasks — MVP 작업 계획

## 진행 규칙

> 1. **순서대로만** 진행한다. 이전 단계 검증이 통과되지 않으면 다음 단계로 넘어가지 않는다.
> 2. **병렬 금지** — 두 단계를 동시에 진행하지 않는다.
> 3. **단계별 검증 필수** — 검증 방법을 직접 실행해 통과를 확인한 뒤 체크한다.
> 4. **확장 단계 미포함** — Phase 4 이후(JWT·팀·Kanban·채팅·CI/CD)는 별도 문서에서 다룬다.

---

## Phase 1 — 설계 `[완료]`

**목표**: 모든 구현의 기준이 되는 문서 완성 및 저장소 초기화

| # | 작업 | 검증 방법 |
|---|------|-----------|
| 1 | GitHub 저장소 초기화 + git 로컬 설정 (`user.name`, `user.email`) | `git log --oneline` 에서 첫 커밋 확인 |
| 2 | `CLAUDE.md` 작성 (역할 · 절대규칙 5개 · 모호한 요청 처리) | 파일 열어 5개 규칙 항목 육안 확인 |
| 3 | `docs/00-overview.md` 작성 (문서 지도 · 읽기 순서 · 관심사 분리) | 매핑표 6행 확인 |
| 4 | `docs/01-product.md` 작성 (목표 · 페르소나 · MVP 범위 · 성공 기준) | 성공 기준 5개 항목 확인 |
| 5 | `docs/02-specs.md` 작성 (Task 모델 · 검증 규칙 · API 5개 · 화면 명세) | API 엔드포인트 5개 전부 기재 확인 |
| 6 | `docs/03-design.md` 작성 (설계 결정 8개 · 디자인 토큰 · 의존성 정책) | 결정 표 8행 확인 |
| 7 | `docs/04-tasks.md` 작성 (이 파일 — Phase 1/2/3 체크리스트) | Phase 3 마지막 행까지 존재 확인 |
| 8 | `docs/05-conventions.md` 작성 (폴더 구조 · 네이밍 · Git 전략) | 폴더 트리 섹션 존재 확인 |
| 9 | `CLAUDE.md` docs 참조 파일명을 실제 파일명(`00-overview` … `05-conventions`)으로 정렬 | `CLAUDE.md` 내 파일명 6개 일치 확인 |
| 10 | `git push` + GitHub에서 `docs/` 6개 파일 모두 확인 | GitHub 웹에서 파일 목록 육안 확인 |

---

## Phase 2 — 백엔드 `[ ]`

**목표**: FastAPI 기반 CRUD API 5개 완성 및 Swagger UI에서 전 엔드포인트 동작 확인

| # | 작업 | 검증 방법 |
|---|------|-----------|
| 1 | `backend/` 폴더 구조 생성 (`main.py` · `models.py` · `schemas.py` · `database.py` · `routers/tasks.py`) | `ls backend/` 로 파일 목록 확인 |
| 2 | Python 가상환경 생성 + `requirements.txt` 작성 (fastapi · uvicorn · sqlalchemy · pydantic) | `pip install -r requirements.txt` 오류 없음 |
| 3 | `database.py` — SQLAlchemy 엔진(SQLite) + `SessionLocal` + `Base` 정의 | `python -c "from database import Base"` 오류 없음 |
| 4 | `models.py` — Task 모델 7개 필드 정의 + `Base.metadata.create_all()` 실행 | `taskflow.db` 파일 생성 확인 |
| 5 | `schemas.py` — `TaskCreate` · `TaskUpdate` · `TaskResponse` · `TaskListItem` Pydantic 스키마 정의 | `python -c "from schemas import TaskResponse"` 오류 없음 |
| 6 | `POST /api/tasks` 구현 + 유효성 검증 (title 필수 · status 허용값 · due_at ISO 8601) | Swagger에서 정상 요청 `201`, title 빈값 `400` 확인 |
| 7 | `GET /api/tasks` 목록 구현 (description 필드 제외) | Swagger에서 `200` 응답, description 키 없음 확인 |
| 8 | `GET /api/tasks/{id}` 단건 구현 (description 포함) + 없는 id `404` | Swagger에서 존재 id `200`, 없는 id `404` 확인 |
| 9 | `PUT /api/tasks/{id}` 부분 수정 구현 (전달 필드만 갱신) + `updated_at` 자동 갱신 | Swagger에서 status만 변경 후 나머지 필드 유지 확인 |
| 10 | `DELETE /api/tasks/{id}` 구현 + Swagger UI에서 5개 엔드포인트 전부 동작 확인 후 `git push` | Swagger `/docs` 에서 5개 엔드포인트 녹색 응답 확인 |

---

## Phase 3 — 프론트엔드 `[ ]`

**목표**: HTML + Vanilla JS + Tailwind CDN으로 메인 화면 완성 및 API 연결 후 성공 기준 5개 통과

| # | 작업 | 검증 방법 |
|---|------|-----------|
| 1 | `frontend/` 폴더 생성 + `index.html` 기본 틀 (DOCTYPE · meta viewport · Tailwind CDN · 시스템 폰트) | 브라우저에서 빈 화면 오류 없이 열림 확인 |
| 2 | 테마 초기화 스크립트 (`<head>` 인라인) — `localStorage` → `prefers-color-scheme` 순 초기값 설정 | 시스템 다크모드 ON 상태에서 새로고침 시 다크 배경 적용 확인 |
| 3 | 라이트/다크 토글 버튼 구현 — 클릭 시 `<html>` class 전환 + `localStorage('theme')` 저장 | 토글 후 새로고침 시 상태 유지 확인 |
| 4 | Task 목록 카드 UI 구현 — `GET /api/tasks` 폴링(3초) + status 배지 색상 + `D-N HH:MM` 마감 표시 | 브라우저 네트워크 탭에서 3초 간격 요청 확인, 카드 렌더링 확인 |
| 5 | Task 추가 폼 구현 — title · due_at · status 입력 + `POST /api/tasks` 연결 + 성공 시 목록 즉시 갱신 | 폼 제출 후 새 카드 목록에 나타남 확인 |
| 6 | Task 수정 모달 구현 — 카드 클릭 시 모달 오픈 + `PUT /api/tasks/:id` 연결 + ESC/외부클릭 닫기 | 수정 저장 후 카드 내용 갱신 확인, ESC 닫기 확인 |
| 7 | Task 삭제 흐름 구현 — 휴지통 아이콘 → 인라인 확인 메시지 → `DELETE /api/tasks/:id` → 카드 제거 | 삭제 후 카드 사라짐 확인, [취소] 시 카드 유지 확인 |
| 8 | 성공 기준 5개 전체 통과 확인 후 `git push` | 아래 성공 기준 체크리스트 모두 ✅ |

---

## Phase 3 완료 체크리스트 (성공 기준)

| 기준 | 확인 방법 | 통과 |
|------|-----------|------|
| 새로고침 후 데이터 유지 | 태스크 추가 → F5 → 목록 그대로 | `[ ]` |
| 360px 레이아웃 깨짐 없음 | Chrome DevTools → 360px 시뮬레이터 전체 화면 확인 | `[ ]` |
| API 응답 200ms 이하 | 네트워크 탭 → 각 요청 Time 열 확인 | `[ ]` |
| CRUD 4종 화면 동작 | 추가 → 목록 확인 → 수정 → 삭제 순서로 직접 수행 | `[ ]` |
| 라이트/다크 테마 토글 작동 | 토글 → 새로고침 → 상태 유지 확인 | `[ ]` |
