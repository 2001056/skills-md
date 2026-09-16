# 🤖 skills-md

> **하위 AI 모델에서도 Fable 5 수준의 결과물을 끌어내는 프롬프트 가이드 & 스킬 모음**

Claude Fable 5 한도를 다 쓴 뒤 하위 모델(Sonnet, Haiku 등)을 사용할 때,  
이 레포의 파일을 대화에 첨부하거나 프로젝트에 복사해두면 동일한 품질의 결과물을 얻을 수 있습니다.

---

## 📦 파일 구성

```
skills-md/
├── .gitignore                        # .omc/ · _workspace/ 커밋 제외
├── CLAUDE.md                         # 이 레포용 Claude 컨텍스트 파일
├── CLAUDE.template.md                # 내 프로젝트에 복사해서 쓰는 템플릿
│
├── .claude-plugin/
│   ├── plugin.json                   # Claude Code 플러그인 매니페스트
│   └── marketplace.json              # 이 레포를 마켓플레이스로 등록하는 카탈로그
│
├── AI_GUIDE_PLANNING.md              # 서비스 기획 / 요구사항 정의
├── AI_GUIDE_BACKEND.md               # 백엔드 개발 (Spring Boot / NestJS / FastAPI)
├── AI_GUIDE_FRONTEND.md              # 프론트엔드 개발 (Next.js / React / Vue 3)
├── AI_GUIDE_ARCHITECTURE.md          # 시스템 아키텍처 설계
├── AI_GUIDE_GIT_SECURITY_SCAN.md     # 커밋 전 보안 검사 (첨부용)
│
├── hooks/
│   ├── pre-commit                    # git commit 시 자동 보안 검사 훅
│   ├── install.sh                    # 훅 설치 스크립트 (Linux / macOS / Git Bash)
│   ├── install.ps1                   # 훅 설치 스크립트 (Windows PowerShell)
│   └── install-claude-hooks.sh       # Claude Code 훅(라우터+게이트) 설치
│
├── tests/
│   └── test_gates.sh                 # 훅 테스트 (차단·통과 양방향 검증)
│
└── .agents/
    ├── skills/                       # 오케스트레이터 진입점 (명령어)
    │   ├── dev-plan/SKILL.md         # /dev-plan — 기획 단계
    │   ├── dev-backend/SKILL.md      # /dev-backend — 백엔드 단계
    │   ├── dev-frontend/SKILL.md     # /dev-frontend — 프론트엔드 단계
    │   ├── dev-architect/SKILL.md    # /dev-architect — 아키텍처 단계
    │   └── git-security-scan/SKILL.md  # /git-security-scan — 보안 검사
    │
    ├── hooks/                        # Claude Code 훅 — 자동 라우터 + 종료 게이트
    │   ├── router.py                 # UserPromptSubmit: 작업 신호 감지 → 스킬·증거 요건 주입
    │   ├── stop_gate.py              # Stop: 완료 증거 없이 턴 종료 차단
    │   ├── claude-settings.hooks.json  # settings.json 에 병합할 훅 설정 (수동 설치용)
    │   └── hooks.json                # 플러그인 설치 시 자동 적용되는 훅 설정
    │
    └── agents/                       # 전문화된 서브에이전트
        ├── plan-requirements-analyst.md   # 요구사항 분석 + RDS 작성
        ├── plan-ux-designer.md            # IA + UserFlow + 화면 목록
        ├── plan-api-designer.md           # API 정책 정의서
        ├── plan-reviewer.md               # 기획 완성도 검수
        ├── backend-coder.md               # 프로덕션 코드 구현
        ├── backend-test-writer.md         # 테스트 코드 (AAA 패턴)
        ├── backend-doc-writer.md          # Swagger + README 문서
        ├── backend-reviewer.md            # 백엔드 코드 리뷰
        ├── frontend-coder.md              # 컴포넌트 구현
        ├── frontend-a11y-reviewer.md      # 접근성 검수 (WCAG 2.1 AA)
        ├── frontend-reviewer.md           # 프론트엔드 코드 리뷰
        ├── architect-designer.md          # 시스템 아키텍처 설계
        ├── architect-adr-writer.md        # ADR 문서 작성
        └── architect-reviewer.md          # 아키텍처 설계 검수
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

### 방법 4 — 플러그인으로 설치 (Claude Code, 권장) ⭐

파일 복사 없이 두 줄로 끝납니다. 스킬 5종 + 서브에이전트 + 자동 라우터·종료 게이트 훅이 한 번에 붙습니다.

```
/plugin marketplace add 2001056/skills-md
/plugin install skills-md@skills-md
```

설치 후 스킬은 플러그인 네임스페이스로 호출합니다:

| 복사 방식 | 플러그인 방식 |
|---|---|
| `/dev-plan` | `/skills-md:dev-plan` |
| `/dev-backend` | `/skills-md:dev-backend` |
| `/dev-frontend` | `/skills-md:dev-frontend` |
| `/dev-architect` | `/skills-md:dev-architect` |
| `/git-security-scan` | `/skills-md:git-security-scan` |

훅(`router.py` · `stop_gate.py`)은 플러그인이 알아서 등록하므로 `install-claude-hooks.sh` 를 따로 돌릴 필요가 없습니다. 작업공간 `_workspace/` 는 여전히 **내 프로젝트 안**에 생깁니다.

```
/plugin marketplace update skills-md   # 새 버전 받기
/plugin uninstall skills-md@skills-md  # 제거
```

> 방법 2·3(복사)과 방법 4(플러그인)를 동시에 쓰면 스킬이 두 벌로 보입니다. 하나만 고르세요.

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
<summary><strong>🪝 hooks/pre-commit — git commit 시 자동 보안 검사</strong></summary>

<br>

`git commit` 실행 순간 자동으로 스테이징된 변경사항을 스캔합니다.  
CRITICAL / HIGH 항목이 발견되면 **커밋 자체를 차단**합니다. AI 없이도 동작하는 순수 쉘 스크립트입니다.

**자동 탐지 항목:**

| 심각도 | 탐지 항목 |
|---|---|
| 🔴 CRITICAL | OpenAI/AWS/GitHub/Google/Slack/SendGrid API 키, Private Key, 비밀번호 변수 직접 할당, `.env`/`*.pem`/`*.key` 등 민감 파일 스테이징 |
| 🟠 HIGH | 디버그 모드 활성화, SSL 검증 비활성화, DB URI 자격증명 포함 |

**설치 방법:**

```bash
# Linux / macOS / Git Bash
sh hooks/install.sh

# Windows PowerShell
PowerShell -ExecutionPolicy Bypass -File hooks/install.ps1
```

**설치 후 동작:**
```
$ git commit -m "feat: add payment API"

✅ git-security-scan: 이상 없음 — 커밋 진행    ← 문제 없을 때

⛔ git-security-scan: 보안 문제 감지 — 커밋이 차단됩니다    ← 문제 발견 시
────────────────────────────────────────────
🔴 CRITICAL : 1건
🟠 HIGH     : 0건
────────────────────────────────────────────
🔴 CRITICAL: OpenAI API Key 하드코딩 감지
```

**gitleaks 연동 (선택):**  
`gitleaks`가 설치되어 있으면 기본 패턴 스캔 이후 추가로 실행됩니다.
```bash
brew install gitleaks   # macOS
scoop install gitleaks  # Windows
```

**훅 제거:**
```bash
rm .git/hooks/pre-commit
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

## 🪝 Claude Code 훅 — 자동 라우터 + 종료 게이트

`.md` 가이드는 모델이 **따르지 않으면 그만**입니다. 이 훅 두 개는 그 빈틈을 메웁니다.

| 훅 | 이벤트 | 하는 일 |
|---|---|---|
| `router.py` | `UserPromptSubmit` | 프롬프트의 작업 신호(API·컴포넌트·기획·아키텍처·버그…)를 감지해 **맞는 스킬과 "끝내기 전 있어야 할 증거 파일"**을 컨텍스트로 주입. 신호가 없으면 개입하지 않음 |
| `stop_gate.py` | `Stop` | 라우터가 남긴 티켓(`_workspace/.active-run`)이 있는데 증거 파일이 없거나 비어 있으면 **턴 종료를 차단**하고 빠진 항목을 알려줌 |

**완료 증거 계약** (스킬이 이미 쓰는 `_workspace/` 산출물을 그대로 사용):

| 규율 | 작업공간 | 필요한 증거 |
|---|---|---|
| `/dev-plan` | `_workspace/plan-*/` | `04_review.md` |
| `/dev-backend` | `_workspace/backend-*/` | `04_review.md` |
| `/dev-frontend` | `_workspace/frontend-*/` | `03_review.md` |
| `/dev-architect` | `_workspace/architect-*/` | `03_review.md` |
| 조사(버그·에러) | `_workspace/investigate-*/` | `evidence.md` 에 `## 재현` `## 가설` `## 원인` 섹션 |
| `/git-security-scan` | 없음 | 게이트 비대상 |

**설치 (프로젝트 루트에서):**
```sh
sh hooks/install-claude-hooks.sh     # .claude/settings.json 에 훅 병합 (멱등)
sh tests/test_gates.sh               # 차단·통과 양방향 검증
```

**안전장치:**
- 티켓이 없으면(일반 대화) 절대 막지 않습니다.
- `stop_hook_active` 로 무한루프를 막습니다 (한 번 막은 뒤 이어가는 턴은 통과).
- 낡은 티켓(기본 6시간)은 자동 정리됩니다.
- 우회: `SKILLS_MD_GATE=off` · 해제: 프롬프트에 `게이트 해제`

> 이 훅은 모델의 **천장을 올리지 않습니다.** 증거 없이 "완료"라고 말하는 걸 막아, 모델이 자기 천장까지 확실히 가게 하는 장치입니다.

---

## ⚡ 빠른 시작 예시

플러그인으로 설치했다면(방법 4) **명령어 없이 프롬프트만 치면 됩니다.** 라우터가 작업 신호를 읽어 맞는 스킬과 완료 증거 조건을 자동으로 붙입니다. 아래 예시 문장은 전부 라우팅 회귀 테스트(`tests/test_gates.sh` 10~12번)로 검증돼 있습니다.

| 방식 | 하는 법 |
|---|---|
| 🔌 플러그인 (권장) | 프롬프트만 입력 → 라우터 자동 적용. 직접 부르려면 `/skills-md:dev-*` |
| 📎 파일 첨부 (모든 AI) | 해당 `AI_GUIDE_*.md` 를 첨부하고 같은 프롬프트 |
| 📂 복사 방식 | `.agents/` 복사 후 `/dev-*` (Claude Code · AWS Code · Kiro) |

### 기획서 작성
```
"카카오페이 같은 간편결제 서비스의 송금 기능 요구사항 정의서 작성해줘"
```
🔌 라우터 → `dev-plan` · 완료 조건 `_workspace/plan-*/04_review.md` · 📎 `AI_GUIDE_PLANNING.md`

### 백엔드 API 개발
```
"Spring Boot로 주문 생성 API 만들어줘. 재고 부족 시 409 반환"
```
🔌 라우터 → `dev-backend` · 완료 조건 `_workspace/backend-*/04_review.md` · 📎 `AI_GUIDE_BACKEND.md`

### 프론트엔드 컴포넌트
```
"Next.js로 주문 목록 페이지 만들어줘. 로딩/에러/빈 상태 모두 처리해야 해"
```
🔌 라우터 → `dev-frontend` · 완료 조건 `_workspace/frontend-*/03_review.md` · 📎 `AI_GUIDE_FRONTEND.md`

> "에러 상태 처리"는 요구사항 표현이라 버그 조사로 가지 않습니다. 라우터는 "에러 나요 / 오류 발생해" 같은 **신고 어법**만 조사 규율로 보냅니다.

### 아키텍처 설계
```
"DAU 10만 이커머스 서비스 아키텍처 설계해줘. 팀은 5명이야"
```
🔌 라우터 → `dev-architect` · 완료 조건 `_workspace/architect-*/03_review.md` · 📎 `AI_GUIDE_ARCHITECTURE.md`

### 버그 조사 (플러그인 전용 규율)
```
"로그인 누르면 500 에러 나는데 왜 이래"
```
🔌 라우터 → 조사 프로토콜 · 완료 조건 `_workspace/investigate-*/evidence.md` 에 `## 재현` `## 가설` `## 원인` 섹션. 재현 없이, 가설 하나로 "고쳤다"고 끝낼 수 없습니다.

### 커밋 전 보안 검사
```bash
git add .
/skills-md:git-security-scan   # 플러그인
/git-security-scan             # 복사 방식 (Claude Code / AWS Code / Kiro)
```
또는 `git diff --staged` 출력을 복사해 `AI_GUIDE_GIT_SECURITY_SCAN.md` 와 함께 붙여넣기.

---

## 🛠️ 요구사항

- **AI_GUIDE_*.md**: AI 모델 대화가 가능한 모든 환경 (Claude, ChatGPT, Gemini 등)
- **`.agents/skills/`**: Claude Code / AWS Code / Kiro CLI
- **`.agents/hooks/`**: Claude Code + python3 (3.9 이상)

---

## 📄 라이선스

MIT — 자유롭게 복사·수정·배포해서 쓰세요.
