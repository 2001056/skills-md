---
name: dev-plan
description: 기능 아이디어나 개발 요청을 받아 기획 전문가 팀(요구사항 분석가·UX 설계자·API 설계자·기획 리뷰어)을 오케스트레이션해 완성된 기획 산출물 세트를 생성한다. 트리거 — "/dev-plan".
argument-hint: "[구현하고 싶은 기능 설명 또는 기획 요청]"
---

# /dev-plan — 기획 단계 오케스트레이터

## 입력
$ARGUMENTS

## 동작

### Step 0 — 입력 검증

`$ARGUMENTS`가 비어 있으면 안내 후 종료:
> "기획할 기능을 설명해 주세요. 예: `/dev-plan 사용자 초대 기능 구현`"

### Step 1 — 작업 공간 생성

`_workspace/plan-{YYYY-MM-DD}-{NNN}/` 디렉토리를 생성합니다.
Glob으로 기존 시퀀스를 확인하고 NNN을 결정합니다 (당일 없으면 001, 있으면 마지막+1).

작업 시작 시 출력:
```
/dev-plan 기획 단계 시작
run_id: plan-{YYYY-MM-DD}-{NNN}
입력: {$ARGUMENTS 요약}
```

### Phase 1 — 요구사항 분석 (plan-requirements-analyst)

`plan-requirements-analyst` 에이전트를 Agent 도구로 호출합니다.

입력:
- 기능 설명: $ARGUMENTS
- 출력 경로: `_workspace/plan-{run_id}/01_requirements.md`

에이전트가 요구사항 정의서(RDS)를 `01_requirements.md`에 작성합니다.

완료 후 한 줄 상태 출력:
`✅ Phase 1 완료 — 요구사항 정의서 작성`

### Phase 2 — UX 설계 (plan-ux-designer)

`plan-ux-designer` 에이전트를 호출합니다.

입력:
- 요구사항 정의서: `_workspace/plan-{run_id}/01_requirements.md`
- 출력 경로: `_workspace/plan-{run_id}/02_ux_flow.md`

에이전트가 IA + UserFlow(Mermaid) + 화면 목록을 `02_ux_flow.md`에 작성합니다.

완료 후: `✅ Phase 2 완료 — IA / UserFlow 설계`

### Phase 3 — API 설계 (plan-api-designer)

`plan-api-designer` 에이전트를 호출합니다.

입력:
- 요구사항 정의서: `_workspace/plan-{run_id}/01_requirements.md`
- UserFlow: `_workspace/plan-{run_id}/02_ux_flow.md`
- 출력 경로: `_workspace/plan-{run_id}/03_api_policy.md`

에이전트가 API 정책 정의서를 `03_api_policy.md`에 작성합니다.

완료 후: `✅ Phase 3 완료 — API 정책 정의서 작성`

### Phase 4 — 기획 검수 (plan-reviewer)

`plan-reviewer` 에이전트를 호출합니다.

입력:
- 전체 산출물: `_workspace/plan-{run_id}/` 디렉토리
- 출력 경로: `_workspace/plan-{run_id}/04_review.md`

에이전트가 기획 검수 보고서를 `04_review.md`에 작성합니다.

### Step 5 — 최종 결과 전달

사용자에게 다음을 반환합니다:

1. 검수 결과 종합 판정 (개발 착수 가능 여부)
2. 생성된 산출물 목록:
   - `01_requirements.md` — 요구사항 정의서 (RDS)
   - `02_ux_flow.md` — IA / UserFlow / 화면 목록
   - `03_api_policy.md` — API 정책 정의서
   - `04_review.md` — 기획 검수 보고서
3. CRITICAL / HIGH 이슈가 있는 경우 즉시 표시

검수 판정이 ✅이면:
> "기획 완료. 다음 단계: `/dev-architect` 또는 `/dev-backend [03_api_policy.md 경로]`"

❌이면:
> "기획 이슈 해결 후 재검수 필요. `04_review.md` 의 CRITICAL/HIGH 항목을 확인하세요."

## 에이전트 호출 규칙

- 모든 에이전트: `model: opus` 사용
- Phase 1 → 2 → 3 → 4 순차 실행 (각 단계 결과가 다음 단계의 입력)

## 작업 규모별 선택적 실행

> 서브에이전트는 각각 독립 컨텍스트를 사용하므로 토큰 소모가 큽니다.
> 입력의 복잡도와 규모를 판단해 필요한 단계만 선택적으로 실행합니다.

| 작업 규모 | 권장 실행 범위 |
|---|---|
| 간단한 기능 (화면 1개, API 1~2개) | Phase 1만 실행 (요구사항 정의서) |
| 중간 규모 (화면 3개 이하, API 5개 이하) | Phase 1~3 실행 (UX 설계까지) |
| 복잡한 기능 / 신규 서비스 | Phase 1~4 전체 실행 |

입력을 분석해 단순 기능이면 Phase 1만 실행하고 결과를 먼저 보여준 뒤, 추가 단계가 필요한지 사용자에게 확인합니다.
