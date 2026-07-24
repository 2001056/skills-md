---
name: dev-architect
description: 시스템 설명과 요구사항을 받아 아키텍처 전문가 팀(시스템 아키텍트·ADR 작성자·아키텍처 리뷰어)을 오케스트레이션해 완성된 아키텍처 설계 세트를 생성한다. 트리거 — "/dev-architect".
argument-hint: "[설계할 시스템 설명 또는 요구사항]"
---

# /dev-architect — 아키텍처 단계 오케스트레이터

## 입력
$ARGUMENTS

## 동작

### Step 0 — 입력 검증

`$ARGUMENTS`가 비어 있으면 안내 후 종료:
> "설계할 시스템을 설명해 주세요. 예: `/dev-architect DAU 5만 B2B SaaS, 팀 4명, AWS 환경`"

### Step 1 — 작업 공간 생성

`_workspace/architect-{YYYY-MM-DD}-{NNN}/` 디렉토리 생성.

작업 시작 시 출력:
```
/dev-architect 아키텍처 단계 시작
run_id: architect-{YYYY-MM-DD}-{NNN}
```

### Phase 1 — 아키텍처 설계 (architect-designer)

`architect-designer` 에이전트를 호출합니다.

입력:
- 시스템 설명: $ARGUMENTS
- 출력 경로: `_workspace/architect-{run_id}/01_architecture.md`

에이전트가 전체 아키텍처 설계 문서를 `01_architecture.md`에 작성합니다.

완료 후: `✅ Phase 1 완료 — 아키텍처 설계`

### Phase 2 — ADR 작성 (architect-adr-writer)

`architect-adr-writer` 에이전트를 호출합니다.

입력:
- 아키텍처 설계: `_workspace/architect-{run_id}/01_architecture.md`
- 출력 경로: `_workspace/architect-{run_id}/02_adr/`

에이전트가 주요 기술 결정마다 ADR 파일을 `02_adr/` 디렉토리에 작성합니다.

완료 후: `✅ Phase 2 완료 — ADR 작성`

### Phase 3 — 아키텍처 검수 (architect-reviewer)

`architect-reviewer` 에이전트를 호출합니다.

입력:
- 아키텍처 설계: `_workspace/architect-{run_id}/01_architecture.md`
- ADR 목록: `_workspace/architect-{run_id}/02_adr/`
- 출력 경로: `_workspace/architect-{run_id}/03_review.md`

에이전트가 아키텍처 리뷰 보고서를 `03_review.md`에 작성합니다.

### Step 4 — 최종 결과 전달

사용자에게 반환:

1. 리뷰 종합 판정
2. 생성된 파일 목록:
   - `01_architecture.md` — 전체 아키텍처 설계
   - `02_adr/` — 기술 결정 ADR 모음
   - `03_review.md` — 아키텍처 리뷰 보고서
3. CRITICAL / HIGH 이슈 즉시 표시

판정이 ✅이면:
> "아키텍처 설계 완료. 다음 단계: `/dev-backend` 또는 `/dev-frontend`"

❌이면:
> "아키텍처 이슈 해결 후 재검수 필요. `03_review.md` 참고"

## 에이전트 호출 규칙
- 모든 에이전트: `model: opus` 사용
- Phase 1 → 2 → 3 순차 실행

## 작업 규모별 선택적 실행

> 서브에이전트는 각각 독립 컨텍스트를 사용하므로 토큰 소모가 큽니다.
> 입력의 복잡도와 규모를 판단해 필요한 단계만 선택적으로 실행합니다.

| 작업 규모 | 권장 실행 범위 |
|---|---|
| 기능 단위 기술 결정 (DB 선택, 캐싱 전략 등) | Phase 2만 실행 (ADR 작성) |
| 서비스 일부 리아키텍처 | Phase 1~2 실행 (설계 + ADR) |
| 신규 서비스 / 전체 아키텍처 | Phase 1~3 전체 실행 |

입력을 분석해 단순 기술 결정이면 Phase 2(ADR)만 실행하고 추가 단계 필요 여부를 사용자에게 확인합니다.
