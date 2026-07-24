# 🤖 skills-md

> **하위 AI 모델에서도 Fable 5 수준의 결과물을 끌어내는 프롬프트 가이드 & 스킬 모음**

Claude Fable 5 한도를 다 쓴 뒤 하위 모델(Sonnet, Haiku 등)을 사용할 때,  
이 레포의 파일을 대화에 첨부하거나 프로젝트에 복사해두면 동일한 품질의 결과물을 얻을 수 있습니다.

---

## 📦 파일 구성

```
skills-md/
├── AI_GUIDE_PLANNING.md          # 서비스 기획 / 요구사항 정의
├── AI_GUIDE_BACKEND.md           # 백엔드 개발 (Spring Boot / NestJS / FastAPI)
├── AI_GUIDE_FRONTEND.md          # 프론트엔드 개발 (Next.js / React / Vue 3)
├── AI_GUIDE_ARCHITECTURE.md      # 시스템 아키텍처 설계
├── AI_GUIDE_GIT_SECURITY_SCAN.md # 커밋 전 보안 검사 (첨부용)
└── .agents/
    └── skills/
        └── git-security-scan/
            └── SKILL.md          # /git-security-scan 명령어 스킬
```

---

## 🚀 사용 방법

### 방법 1 — 대화에 파일 직접 첨부 (모든 AI 환경)

원하는 `.md` 파일을 다운로드해서 Claude / ChatGPT / Gemini 대화창에 첨부합니다.  
AI가 해당 가이드의 역할로 작동합니다.

```
"백엔드 API 짜줘" + AI_GUIDE_BACKEND.md 첨부
→ 시니어 백엔드 엔지니어 역할로 Spring Boot / NestJS / FastAPI 수준 코드 생성
```

### 방법 2 — `/git-security-scan` 명령어 (Claude Code / AWS Code / Kiro)

`.agents/` 폴더를 프로젝트 루트에 복사하면 어떤 환경에서든 명령어로 사용할 수 있습니다.

```bash
# 1. 이 레포 클론 또는 .agents 폴더만 복사
git clone https://github.com/2001056/skills-md.git

# 2. .agents 폴더를 내 프로젝트 루트에 복사
cp -r skills-md/.agents /내-프로젝트/.agents

# 3. git add 후 AI 채팅창에서 명령어 실행
/git-security-scan
```

### 방법 3 — CLAUDE.md에 include (프로젝트 상시 적용)

자주 쓰는 가이드를 프로젝트에 영구 등록합니다.

```markdown
<!-- 프로젝트 루트 CLAUDE.md -->
@AI_GUIDE_BACKEND.md
@AI_GUIDE_FRONTEND.md
```

---

## 📋 가이드 상세

<details>
<summary><strong>🗂️ AI_GUIDE_PLANNING.md — 서비스 기획 / 요구사항 정의</strong></summary>

<br>

**AI 역할:** 프로덕트 오너(PO) 역할의 기획 전문가

비즈니스 목표 → 사용자 문제 → 기능 요구사항 → 기술 제약 순서로 사고하며,  
개발자가 바로 구현 착수할 수 있는 수준의 기획서를 작성합니다.

**포함 내용:**

| 섹션 | 내용 |
|---|---|
| 요구사항 정의서(RDS) | 문서 구조, Given-When-Then 인수 조건 작성법 |
| 유저 스토리 | As a / I want to / So that 형식, 스토리 포인트 기준 |
| IA 설계 | 화면 목록 정의, 메뉴 계층 구조 (3depth 이내) |
| User Flow | Mermaid 다이어그램, Happy Path / Error Path / Edge Case |
| API 정책 정의 | 엔드포인트 · 요청 · 응답 · 에러 케이스 정의 형식 |
| 우선순위 | MoSCoW 프레임워크 (Must/Should/Could/Won't) |
| 보안 기획 | 데이터 등급 분류 · 권한 매트릭스 · 감사 로그 요구사항 |

**언제 사용:**
- 신규 서비스 / 기능 기획서 작성
- 요구사항 정의서(RDS) 초안 작성
- IA 구조도 / User Flow 다이어그램 작성
- 개인정보 처리 방침 기획

</details>

---

<details>
<summary><strong>⚙️ AI_GUIDE_BACKEND.md — 백엔드 개발 (Spring Boot / NestJS / FastAPI)</strong></summary>

<br>

**AI 역할:** 시니어 백엔드 엔지니어

확장성·보안·성능·유지보수성을 모두 고려한 프로덕션 수준의 코드를 작성합니다.  
기존 코드베이스의 패턴과 컨벤션을 먼저 파악하고 새 코드를 작성합니다.

**포함 내용:**

| 섹션 | 내용 |
|---|---|
| 코드 품질 기준 | 단일 책임 · 예외 처리 · 응답 형식 표준화 |
| Java / Spring Boot | 레이어 구조 · 어노테이션 패턴 · JPA · 동시성 처리 |
| Node.js / NestJS | 모듈 구조 · DTO 검증 · 인터셉터 · 비동기 에러 처리 |
| Python / FastAPI | 프로젝트 구조 · 타입 힌팅 · 비동기 원칙 · LLM 연동 |
| REST API 설계 | URL 설계 규칙 · HTTP 상태 코드 기준 |
| 테스트 | AAA 패턴 · 범위 우선순위 · 명명 규칙 |
| 시크릿 보안 | 하드코딩 금지 · .env 관리 · CI/CD 시크릿 · 유출 대응 |

**언제 사용:**
- REST API 개발 (Spring Boot / NestJS / FastAPI)
- DB 쿼리 최적화, N+1 문제 해결
- 인증/인가 구현
- 코드 리뷰 체크리스트 적용

</details>

---

<details>
<summary><strong>🖥️ AI_GUIDE_FRONTEND.md — 프론트엔드 개발 (Next.js / React / Vue 3)</strong></summary>

<br>

**AI 역할:** 시니어 프론트엔드 엔지니어

UX·접근성·성능·유지보수성을 고려한 프로덕션 수준의 컴포넌트를 작성합니다.

**포함 내용:**

| 섹션 | 내용 |
|---|---|
| 컴포넌트 설계 | Page / Layout / Feature / UI / Primitive 분류 기준 |
| TypeScript | 타입 정의 원칙 · any 금지 · API 응답 타입 관리 |
| 상태 관리 | useState → Context → Zustand 결정 트리 · React Query |
| 비동기 처리 | Loading / Error / Empty 상태 3종 세트 필수 |
| 폼 처리 | React Hook Form + Zod 조합 |
| 접근성 | alt 텍스트 · aria-label · role="alert" · 키보드 포커스 |
| 성능 최적화 | memo · useCallback · useMemo · next/image · dynamic import |
| 모바일/웹뷰 | Safe Area · 터치 영역 · 인앱 브라우저 이슈 |
| 시크릿 보안 | NEXT_PUBLIC_ 분류 · localStorage 금지 · API Route 프록시 |

**언제 사용:**
- Next.js / React 컴포넌트 개발
- 폼 유효성 검증 구현
- 서버 상태(React Query) / 클라이언트 상태(Zustand) 설계
- 웹뷰(토스, 카카오 앱 등) 개발

</details>

---

<details>
<summary><strong>🏗️ AI_GUIDE_ARCHITECTURE.md — 시스템 아키텍처 설계</strong></summary>

<br>

**AI 역할:** 시스템 아키텍트

비즈니스 요구사항 → 기술 제약 → 트레이드오프 분석 → 최적 선택 순서로 사고합니다.  
모든 결정에 ADR(Architecture Decision Record)을 함께 기록합니다.

**포함 내용:**

| 섹션 | 내용 |
|---|---|
| 모놀리스 vs MSA | 팀 규모 · 트래픽 · 도메인 성숙도 기준 결정 트리 |
| DB 선택 | RDBMS vs NoSQL vs Redis vs Elasticsearch 결정 트리 |
| 캐싱 전략 | Cache-Aside · TTL 설계 · Redis 분산 락 |
| 메시징 아키텍처 | 동기(REST/gRPC) vs 비동기(Kafka/Redis Queue) |
| 인증/인가 | JWT vs Session · Refresh Token Rotation · RBAC |
| CI/CD | GitHub Actions 표준 파이프라인 · 환경 분리 원칙 |
| 모니터링 | Metrics / Logs / Traces 3 Pillars |
| ADR 작성 | 아키텍처 결정 기록 템플릿 |
| 규모별 추천 스택 | 소규모(1인) / 중규모(팀) / 대규모(MSA) |
| 시크릿 아키텍처 | AWS Secrets Manager / Vault / K8s External Secrets |

**언제 사용:**
- 신규 서비스 기술 스택 결정
- MSA 전환 검토
- 인프라 보안 설계
- DB 스키마 · 캐싱 전략 설계

</details>

---

<details>
<summary><strong>🔐 AI_GUIDE_GIT_SECURITY_SCAN.md — 커밋 전 보안 검사 (첨부용)</strong></summary>

<br>

**AI 역할:** 시니어 보안 엔지니어 (코드 리뷰어)

`git diff --staged` 출력을 분석해 커밋 직전 보안 취약점을 4단계로 분류해 보고합니다.

**탐지 항목:**

| 심각도 | 항목 |
|---|---|
| 🔴 CRITICAL | API 키 하드코딩 (OpenAI/AWS/GitHub 등) · 프라이빗 키 · 민감 파일 스테이징 (`.env`, `*.pem` 등) · 클라우드 자격증명 |
| 🟠 HIGH | 내부 IP/호스트명 노출 · 디버그 모드 프로덕션 활성화 · 민감 정보 로그 출력 · CORS 전체 허용 · SSL 검증 비활성화 |
| 🟡 MEDIUM | 보안 TODO 미해결 · MD5/SHA1 취약 알고리즘 · SQL 인젝션 패턴 · NEXT_PUBLIC_ 시크릿 |
| 🔵 LOW | .gitignore 미설정 가능성 · 대용량 이진 파일 · 주석 처리된 인증 코드 |

**사용 방법 (Claude Code / AWS Code / Kiro 이외 환경):**
```
1. git diff --staged 실행 후 출력 복사
2. AI 대화창에 AI_GUIDE_GIT_SECURITY_SCAN.md 첨부
3. 복사한 diff 텍스트 붙여넣기
→ CRITICAL/HIGH 발견 시 커밋 차단, 전체 없으면 커밋 승인
```

</details>

---

<details>
<summary><strong>⚡ .agents/skills/git-security-scan — /git-security-scan 명령어 스킬</strong></summary>

<br>

Claude Code / AWS Code / Kiro 환경에서 `/git-security-scan` 명령어로 바로 실행할 수 있는 스킬입니다.  
`AI_GUIDE_GIT_SECURITY_SCAN.md`와 동일한 검사를 수행하지만, **파일 첨부 없이 명령어 한 줄로 실행** 가능합니다.

**설치 방법:**
```bash
# 이 레포 클론
git clone https://github.com/2001056/skills-md.git

# .agents 폴더를 내 프로젝트 루트에 복사
cp -r skills-md/.agents /내-프로젝트/

# 이후 프로젝트에서 git add 후 실행
/git-security-scan
```

**실행 방식:**
- 인자 없이 실행 → `git diff --staged` 자동 실행 후 검사
- diff 텍스트 직접 붙여넣기 → `/git-security-scan [diff 내용]`

**지원 환경:** Claude Code · AWS Code · Kiro CLI (`.agents/skills/` 표준 경로 지원 환경 전체)

</details>

---

## ⚡ 빠른 시작 예시

### 기획서 작성
```
AI_GUIDE_PLANNING.md 첨부 후:
"카카오페이 같은 간편결제 서비스의 송금 기능 요구사항 정의서 작성해줘"
```

### 백엔드 API 개발
```
AI_GUIDE_BACKEND.md 첨부 후:
"Spring Boot로 주문 생성 API 만들어줘. 재고 부족 시 409 반환"
```

### 프론트엔드 컴포넌트
```
AI_GUIDE_FRONTEND.md 첨부 후:
"Next.js로 주문 목록 페이지 만들어줘. 로딩/에러/빈 상태 모두 처리해야 해"
```

### 아키텍처 설계
```
AI_GUIDE_ARCHITECTURE.md 첨부 후:
"DAU 10만 이커머스 서비스 아키텍처 설계해줘. 팀은 5명이야"
```

### 커밋 전 보안 검사
```bash
git add .
/git-security-scan   # Claude Code / AWS Code / Kiro
```
또는
```
git diff --staged 출력 복사 후
AI_GUIDE_GIT_SECURITY_SCAN.md 첨부해서 붙여넣기
```

---

## 🛠️ 요구사항

- **AI_GUIDE_*.md**: AI 모델 대화가 가능한 모든 환경 (Claude, ChatGPT, Gemini 등)
- **`.agents/skills/`**: Claude Code / AWS Code / Kiro CLI

---

## 📄 라이선스

MIT — 자유롭게 복사·수정·배포해서 쓰세요.
