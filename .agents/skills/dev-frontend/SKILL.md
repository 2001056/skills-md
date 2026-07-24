---
name: dev-frontend
description: 구현 대상(기능 설명 또는 화면 설계)을 받아 프론트엔드 전문가 팀(컴포넌트 개발자·접근성 검수자·코드 리뷰어)을 오케스트레이션해 완성된 프론트엔드 구현 세트를 생성한다. 트리거 — "/dev-frontend".
argument-hint: "[구현할 화면 또는 기능 설명]"
---

# /dev-frontend — 프론트엔드 단계 오케스트레이터

## 입력
$ARGUMENTS

## 동작

### Step 0 — 입력 검증

`$ARGUMENTS`가 비어 있으면 안내 후 종료:
> "구현할 화면이나 기능을 설명해 주세요."

기존 `/dev-plan` 산출물이 있는 경우 `_workspace/plan-*/02_ux_flow.md`를 자동으로 로드합니다.

### Step 1 — 작업 공간 생성

`_workspace/frontend-{YYYY-MM-DD}-{NNN}/` 디렉토리 생성.

작업 시작 시 출력:
```
/dev-frontend 프론트엔드 단계 시작
run_id: frontend-{YYYY-MM-DD}-{NNN}
```

### Phase 1 — 컴포넌트 구현 (frontend-coder)

`frontend-coder` 에이전트를 호출합니다.

입력:
- 기능/화면 설명: $ARGUMENTS
- 출력 경로: `_workspace/frontend-{run_id}/01_components/`

에이전트가 컴포넌트 파일들을 `01_components/` 디렉토리에 작성합니다.

완료 후: `✅ Phase 1 완료 — 컴포넌트 구현`

### Phase 2 — 접근성 검수 (frontend-a11y-reviewer)

`frontend-a11y-reviewer` 에이전트를 호출합니다.

입력:
- 구현 코드: `_workspace/frontend-{run_id}/01_components/`
- 출력 경로: `_workspace/frontend-{run_id}/02_a11y_report.md`

에이전트가 접근성 검수 보고서를 작성합니다.

완료 후: `✅ Phase 2 완료 — 접근성 검수`

### Phase 3 — 코드 리뷰 (frontend-reviewer)

`frontend-reviewer` 에이전트를 호출합니다.

입력:
- 구현 코드: `_workspace/frontend-{run_id}/01_components/`
- 접근성 보고서: `_workspace/frontend-{run_id}/02_a11y_report.md`
- 출력 경로: `_workspace/frontend-{run_id}/03_review.md`

에이전트가 코드 리뷰 보고서를 작성합니다.

### Step 4 — 최종 결과 전달

사용자에게 반환:

1. 코드 리뷰 종합 판정
2. 생성된 파일 목록:
   - `01_components/` — 구현된 컴포넌트
   - `02_a11y_report.md` — 접근성 검수 보고서
   - `03_review.md` — 코드 리뷰 보고서
3. CRITICAL / HIGH 이슈 즉시 표시

판정이 ✅이면:
> "프론트엔드 구현 완료. 다음 단계: `/git-security-scan`"

❌이면:
> "리뷰 이슈 해결 후 재검수 필요. `03_review.md` 참고"

## 에이전트 호출 규칙
- 모든 에이전트: `model: opus` 사용
- Phase 1 완료 후 Phase 2, Phase 2 완료 후 Phase 3 순차 실행

## 작업 규모별 선택적 실행

> 서브에이전트는 각각 독립 컨텍스트를 사용하므로 토큰 소모가 큽니다.
> 입력의 복잡도와 규모를 판단해 필요한 단계만 선택적으로 실행합니다.

| 작업 규모 | 권장 실행 범위 |
|---|---|
| 단순 컴포넌트 (표시 전용) | Phase 1만 실행 (구현) |
| 인터랙션 있는 컴포넌트 | Phase 1~2 실행 (구현 + 접근성) |
| 주요 페이지 / 복잡한 폼 | Phase 1~3 전체 실행 |

입력을 분석해 단순 작업이면 Phase 1만 실행하고 추가 단계 필요 여부를 사용자에게 확인합니다.
