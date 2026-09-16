# skills-md — AI 개발 가이드 & 스킬 모음

> 하위 AI 모델(Sonnet, Haiku 등)에서 Fable 5 수준의 결과물을 끌어내기 위한
> 프롬프트 가이드 파일과 에이전트 스킬 모음입니다.

---

## 디렉토리 구조

```
AI_GUIDE_*.md          도메인별 개발 가이드 (AI에게 첨부하거나 @include)
.agents/agents/        전문화된 서브에이전트 정의 파일
.agents/skills/        에이전트를 오케스트레이션하는 스킬 진입점
hooks/                 git pre-commit 보안 스캔 훅 + Claude Code 훅 설치 스크립트
.agents/hooks/         Claude Code 훅 (자동 라우터 · 종료 게이트)
tests/                 훅 테스트 (차단·통과 양방향)
```

---

## 사용 가능한 스킬

| 스킬 | 설명 | 서브에이전트 구성 |
|---|---|---|
| `/dev-plan` | 기획 단계 오케스트레이터 | 요구사항 분석 → UX 설계 → API 설계 → 검수 |
| `/dev-backend` | 백엔드 단계 오케스트레이터 | 코드 구현 → 테스트 → 문서 → 리뷰 |
| `/dev-frontend` | 프론트엔드 단계 오케스트레이터 | 컴포넌트 구현 → 접근성 검사 → 리뷰 |
| `/dev-architect` | 아키텍처 단계 오케스트레이터 | 아키텍처 설계 → ADR 작성 → 검수 |
| `/git-security-scan` | 커밋 전 보안 검사 | 단일 에이전트 |

---

## 파일 추가 / 수정 컨벤션

### 새 AI_GUIDE_*.md 추가 시

1. 파일명: `AI_GUIDE_[도메인명].md` (대문자 스네이크케이스)
2. **Section 0**에 AI 역할 정의 필수 (시니어 [역할] 역할을 하는 AI)
3. Section 0 하단에 도메인 무관 범용 안내 문구 포함:
   ```
   > 📌 이 가이드는 도메인에 무관하게 적용됩니다.
   ```
4. 코드 예시는 특정 도메인에 종속되지 않도록 — 불가피한 경우 여러 도메인 예시 병기
5. 마지막 섹션에 AI 자체 점검용 체크리스트 포함
6. `README.md`의 가이드 상세 `<details>` 섹션 업데이트

### 새 에이전트 추가 시 (`.agents/agents/`)

1. 파일명: `{stage}-{role}.md` (예: `backend-coder.md`, `plan-reviewer.md`)
2. frontmatter 필수:
   ```yaml
   ---
   name: agent-name
   description: 이 에이전트를 언제/어떻게 쓰는지 한 줄 설명
   ---
   ```
3. 에이전트 정의는 자기완결적으로 — 외부 파일 없이도 역할 수행 가능
4. 출력 형식을 명확히 정의 (어떤 파일을 어디에 씀)
5. 품질 체크리스트 포함

### 새 스킬 추가 시 (`.agents/skills/`)

1. 디렉토리 구조: `.agents/skills/{skill-name}/SKILL.md`
2. frontmatter 필수:
   ```yaml
   ---
   name: skill-name
   description: 트리거 조건 포함한 설명. 트리거 — "/skill-name".
   argument-hint: "[인자 힌트]"
   ---
   ```
3. `$ARGUMENTS` 변수로 사용자 입력 처리
4. 빈 입력 처리 및 안내 메시지 포함
5. 작업 공간: `_workspace/{skill}-{YYYY-MM-DD}-{NNN}/` 패턴 사용
6. README.md 업데이트

---

### 새 규율(라우팅 대상) 추가 시 (`.agents/hooks/router.py`)

1. `DISCIPLINES` 리스트에 항목 추가 — 순서가 우선순위 (앞에 있을수록 먼저 매칭)
2. `prefix` 는 해당 스킬의 `_workspace/{prefix}...` 와 정확히 일치시킬 것
3. `evidence` 는 스킬이 **마지막에 실제로 쓰는 파일명**만 — 없는 파일을 요구하면 영구 차단됨
4. 작업공간이 없는 스킬은 `prefix: None` (게이트 비대상)
5. `tests/test_gates.sh` 에 차단 케이스와 통과 케이스를 **둘 다** 추가하고 통과시킬 것

### 훅 수정 시 원칙

- 티켓 없는 일반 대화를 막는 변경은 금지 (`stop_gate.py` 의 "티켓 없으면 통과"는 불변)
- `stop_hook_active` 무한루프 가드는 제거 금지
- python 3.9 호환 문법 유지 (`match`, `X | Y` 타입 금지)

## 작업 시 유의사항

- 예시 코드는 이커머스/결제 도메인에 종속되지 않도록 유지
- 에이전트 파일 수정 시 해당 에이전트를 사용하는 SKILL.md도 함께 확인
- `hooks/pre-commit` 수정 시 실제 bash 문법 테스트 필요 (Windows Git Bash 기준)
- README.md의 파일 구성 트리는 실제 구조와 항상 일치하도록 유지
