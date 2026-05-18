# 03-design — 기술 설계 결정

## 의존성 추가 정책

> **이 파일에 사유를 먼저 기록하지 않은 패키지는 절대 도입하지 않는다.**
> 새 의존성이 필요하면 아래 결정 표에 행을 추가하고 사용자 승인을 받은 뒤 설치한다.

---

## 설계 결정 8가지

| # | 항목 | **선택** | 대안 | 근거 | 트레이드오프 |
|---|------|----------|------|------|-------------|
| 1 | **백엔드** | FastAPI | Django, Express | 타입 힌트 기반 자동 문서화(Swagger), 비동기 지원, 경량 구조로 MVP 속도 최적 | Django 대비 내장 기능(ORM·Admin·Auth) 없음 — 필요 시 직접 구성 |
| 2 | **프론트엔드** | Vanilla JS + Tailwind CDN | React, Vue | 빌드 도구 없이 즉시 실행, 번들러·컴파일 단계 제거로 학습 곡선 최소화 | 컴포넌트 재사용·상태 추적이 규모 커질수록 복잡해짐 — Phase 3 이후 React 전환 고려 |
| 3 | **데이터베이스** | SQLite → PostgreSQL + SQLAlchemy | MySQL, MongoDB | 로컬 개발은 SQLite(파일 1개), 운영은 PostgreSQL로 마이그레이션 — SQLAlchemy가 양쪽 방언 추상화 | SQLite는 동시 쓰기 제한 있음 — 운영 전 반드시 PostgreSQL 전환 필요 |
| 4 | **CSS 방식** | Tailwind CSS (CDN) | styled-components, CSS Modules | 유틸리티 클래스로 빠른 UI 구성, 별도 빌드 불필요, 일관된 디자인 토큰 강제 | CDN 버전은 미사용 클래스 제거(purge) 안 됨 — 운영 최적화 시 CLI 버전으로 전환 |
| 5 | **실시간 동기화** | 폴링 (3초 간격) | WebSocket, SSE | 구현 복잡도 최소화, 서버 인프라 추가 없음, MVP 규모(10인 팀)에서 충분 | 3초 지연 존재, 불필요한 요청 발생 — WebSocket 전환은 Phase 5(채팅) 단계에서 진행 |
| 6 | **프론트 상태 관리** | 모듈 변수 + DOM 직접 갱신 | Redux, Zustand, Pinia | 빌드 도구 없는 Vanilla JS 환경에서 외부 상태 라이브러리 사용 불가, 단순 CRUD에 충분 | 상태 추적·디버깅이 수동이라 규모 커지면 관리 어려움 — React 전환 시 함께 교체 |
| 7 | **디자인 시스템** | macOS UI 톤 (자체 토큰) | Material Design, Ant Design | 서드파티 컴포넌트 라이브러리 없이 Tailwind 토큰만으로 일관된 감성 유지 | 컴포넌트 직접 구현 필요 — 단, MVP 범위(카드·모달·배지)는 구현 부담 낮음 |
| 8 | **테마 (라이트/다크)** | Tailwind `dark:` + `localStorage` | CSS 변수, 외부 테마 라이브러리 | Tailwind `dark:` 변형으로 클래스 한 줄 추가, `localStorage('theme')` 영속화, `prefers-color-scheme`으로 초기값 자동 설정 | `class` 전략 필요 (`tailwind.config`의 `darkMode: 'class'`), JS 1회 실행으로 초기 깜빡임(FOUC) 방지 처리 필요 |

---

## 디자인 토큰

Tailwind 유틸리티 클래스로 표현하며, 아래 토큰 외 임의 스타일은 사용하지 않는다.

| 토큰 | Tailwind 클래스 | 용도 |
|------|----------------|------|
| 둥근 모서리 | `rounded-xl` | 카드·모달·버튼 |
| 그림자 | `shadow-lg` | 카드·모달 부유감 |
| 반투명 배경 | `backdrop-blur-md` + `bg-white/80` (라이트) / `bg-gray-900/80` (다크) | 카드 배경 |
| 시스템 폰트 | `font-sans` (→ `-apple-system, BlinkMacSystemFont, Segoe UI`) | 전체 body |
| 터치 타깃 | `min-h-[44px] min-w-[44px]` | 모든 버튼·아이콘 버튼 |

---

## 테마 전환 구현 규칙

```html
<!-- <html> 태그에 class="dark" 추가/제거로 전환 -->
<html class="dark">
```

```js
// 초기 테마 결정 순서
// 1순위: localStorage('theme') 값
// 2순위: window.matchMedia('(prefers-color-scheme: dark)')
// 3순위: 라이트 모드 기본값
```

- `localStorage` 키: `'theme'`, 값: `'light'` | `'dark'`
- FOUC 방지를 위해 테마 초기화 스크립트는 `<head>` 최상단 `<script>` 인라인으로 실행

---

## 현재 승인된 의존성 목록

| 패키지 | 버전 | 용도 | 승인 근거 |
|--------|------|------|-----------|
| `fastapi` | 최신 안정 | 백엔드 프레임워크 | 결정 #1 |
| `uvicorn` | 최신 안정 | ASGI 서버 | FastAPI 실행 필수 런타임 |
| `sqlalchemy` | 최신 안정 | ORM | 결정 #3 |
| `pydantic` | v2 | 요청/응답 검증 | FastAPI 내장 의존성 |
| Tailwind CSS CDN | 최신 | 스타일 | 결정 #4 |
| `httpx` | 최신 안정 | FastAPI TestClient 의존성 | pytest에서 TestClient 사용 시 필수 |
| `pytest` | 최신 안정 | 테스트 프레임워크 | 절대 규칙 #3 (테스트 없이 완료 금지) |
| `aiofiles` | 최신 안정 | FastAPI 정적 파일 서빙 | frontend/ 를 백엔드에서 직접 서빙해 CORS 불필요 |
