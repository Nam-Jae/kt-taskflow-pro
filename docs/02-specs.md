# 02-specs — 기술 명세

## 데이터 모델

### Task

| 필드 | 타입 | 제약 | 비고 |
|------|------|------|------|
| `id` | INTEGER | PK, AUTO INCREMENT | |
| `title` | VARCHAR(200) | NOT NULL | 빈 문자열 불허 |
| `description` | TEXT | NULL 허용 | |
| `status` | ENUM | NOT NULL, DEFAULT `todo` | `todo` / `in_progress` / `done` |
| `due_at` | DATETIME | NULL 허용 | UTC 저장, ISO 8601 입력 |
| `created_at` | DATETIME | NOT NULL, DEFAULT NOW() | UTC 자동 기록 |
| `updated_at` | DATETIME | NOT NULL, DEFAULT NOW() | 수정 시 자동 갱신 |

---

## 유효성 검증 규칙

| 조건 | HTTP 상태 | 오류 메시지 예시 |
|------|-----------|-----------------|
| `title` 누락 또는 빈 문자열 | `400 Bad Request` | `"title is required"` |
| `title` 200자 초과 | `400 Bad Request` | `"title must be 200 characters or fewer"` |
| `status` 허용값 외 | `400 Bad Request` | `"status must be one of: todo, in_progress, done"` |
| `due_at` ISO 8601 형식 위반 | `400 Bad Request` | `"due_at must be ISO 8601 format (e.g. 2026-05-12T18:00:00Z)"` |
| 존재하지 않는 `id` 조회/수정/삭제 | `404 Not Found` | `"task not found"` |

오류 응답 공통 형식:
```json
{
  "error": "오류 메시지"
}
```

---

## REST API

### 공통

- Base URL: `/api/tasks`
- Content-Type: `application/json`
- 날짜·시간: ISO 8601 UTC (`2026-05-12T18:00:00Z`)

---

### 1. 태스크 생성

```
POST /api/tasks
```

**Request Body**
```json
{
  "title": "디자인 시안 검토",
  "description": "피그마 링크 확인 후 피드백 작성",
  "status": "todo",
  "due_at": "2026-05-12T18:00:00Z"
}
```

**Response `201 Created`**
```json
{
  "id": 1,
  "title": "디자인 시안 검토",
  "description": "피그마 링크 확인 후 피드백 작성",
  "status": "todo",
  "due_at": "2026-05-12T18:00:00Z",
  "created_at": "2026-05-10T09:00:00Z",
  "updated_at": "2026-05-10T09:00:00Z"
}
```

---

### 2. 태스크 목록 조회

```
GET /api/tasks
```

> `description` 필드 **제외** — 목록 성능 최적화

**Response `200 OK`**
```json
[
  {
    "id": 1,
    "title": "디자인 시안 검토",
    "status": "todo",
    "due_at": "2026-05-12T18:00:00Z",
    "created_at": "2026-05-10T09:00:00Z",
    "updated_at": "2026-05-10T09:00:00Z"
  }
]
```

---

### 3. 태스크 단건 조회

```
GET /api/tasks/:id
```

> `description` 필드 **포함**

**Response `200 OK`**
```json
{
  "id": 1,
  "title": "디자인 시안 검토",
  "description": "피그마 링크 확인 후 피드백 작성",
  "status": "todo",
  "due_at": "2026-05-12T18:00:00Z",
  "created_at": "2026-05-10T09:00:00Z",
  "updated_at": "2026-05-10T09:00:00Z"
}
```

---

### 4. 태스크 수정 (부분 수정)

```
PUT /api/tasks/:id
```

> 전달한 필드만 수정한다. 누락된 필드는 기존 값 유지.

**Request Body** (모든 필드 선택)
```json
{
  "status": "in_progress",
  "due_at": "2026-05-13T12:00:00Z"
}
```

**Response `200 OK`** — 수정된 전체 태스크 반환 (`description` 포함)
```json
{
  "id": 1,
  "title": "디자인 시안 검토",
  "description": "피그마 링크 확인 후 피드백 작성",
  "status": "in_progress",
  "due_at": "2026-05-13T12:00:00Z",
  "created_at": "2026-05-10T09:00:00Z",
  "updated_at": "2026-05-10T10:30:00Z"
}
```

---

### 5. 태스크 삭제

```
DELETE /api/tasks/:id
```

**Response `204 No Content`** — 본문 없음

---

## 화면 명세 (CRUD 4종)

### C — 태스크 추가

- 화면 우상단 **"+ 추가"** 버튼 클릭 시 폼 표시
- 폼 필드:
  - `title` — 텍스트 입력 (필수, placeholder: "태스크 이름")
  - `due_at` — 날짜+시간 피커 (선택, `YYYY-MM-DD HH:MM` 형식으로 표시)
  - `status` — 드롭다운 (`todo` / `in_progress` / `done`, 기본 `todo`)
- 제출 시 `POST /api/tasks` 호출 → 성공 시 목록 갱신

---

### R — 태스크 목록

- 카드 그리드 레이아웃 (모바일 1열 / 데스크탑 2~3열)
- 카드 표시 항목:
  - `title`
  - `status` 배지 (색상 구분: `todo` 회색 / `in_progress` 파랑 / `done` 초록)
  - `due_at` — **D-N HH:MM** 형식으로 표시
    - 예: 오늘 마감 `D-0 18:00`, 내일 `D-1 09:00`, 기한 없음 `—`
    - 마감 초과 시 빨간색으로 표시

---

### U — 태스크 수정

- 카드 클릭 → **모달** 팝업
- 모달 내 필드: `title`, `description`, `due_at`, `status` 편집 가능
- 저장 버튼 클릭 시 `PUT /api/tasks/:id` 호출 → 성공 시 모달 닫힘 + 카드 갱신
- 모달 외부 클릭 또는 ESC 키로 취소 (변경 사항 미저장 경고 없음)

---

### D — 태스크 삭제

- 카드 우상단 **휴지통 아이콘** 버튼
- 클릭 시 **인라인 확인 메시지** 표시: "정말 삭제할까요? [삭제] [취소]"
- [삭제] 클릭 시 `DELETE /api/tasks/:id` 호출 → 성공 시 카드 제거
- [취소] 클릭 시 확인 메시지 숨김, 카드 유지
