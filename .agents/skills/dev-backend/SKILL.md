---
name: dev-backend
description: 구현 대상(기능 설명 또는 API 명세)을 받아 백엔드 전문가 팀(코더·테스트 작성자·문서 작성자·코드 리뷰어)을 오케스트레이션해 완성된 백엔드 구현 세트를 생성한다. 트리거 — "/dev-backend".
argument-hint: "[구현할 기능 설명 또는 API 명세 파일 경로]"
---

# /dev-backend — 백엔드 단계 오케스트레이터

## 입력
$ARGUMENTS

## 동작

### Step 0 — 입력 검증

`$ARGUMENTS`가 비어 있으면 안내 후 종료:
> "구현할 기능을 설명하거나 API 명세 파일 경로를 입력해 주세요."

기존 `/dev-plan` 산출물이 있는 경우 `_workspace/plan-*/03_api_policy.md`를 자동으로 로드합니다.

### Step 1 — 작업 공간 생성

`_workspace/backend-{YYYY-MM-DD}-{NNN}/` 디렉토리 생성.

작업 시작 시 출력:
```
/dev-backend 백엔드 단계 시작
run_id: backend-{YYYY-MM-DD}-{NNN}
```

### Phase 1 — 코드 구현 (backend-coder)

`backend-coder` 에이전트를 호출합니다.

입력:
- 기능 설명 또는 API 명세: $ARGUMENTS
- 작업 공간: _workspace/backend-{run_id}/

에이전트가 `01_implementation/` 디렉토리에 구현 파일들을 작성합니다.

완료 후: `✅ Phase 1 완료 — 코드 구현`

### Phase 2 — 테스트 작성 (backend-test-writer)

`backend-test-writer` 에이전트를 호출합니다.

입력:
- 구현 코드: _workspace/backend-{run_id}/01_implementation/

에이전트가 `02_tests/` 디렉토리에 테스트 파일들을 작성합니다.

완료 후: `✅ Phase 2 완료 — 테스트 코드 작성`

### Phase 3 — 문서 작성 (backend-doc-writer)

`backend-doc-writer` 에이전트를 호출합니다.

입력:
- 구현 코드: _workspace/backend-{run_id}/01_implementation/

에이전트가 `03_docs/` 디렉토리에 문서를 작성합니다 (Swagger 어노테이션 + README).

완료 후: `✅ Phase 3 완료 — 문서 작성`

### Phase 4 — 코드 리뷰 (backend-reviewer)

`backend-reviewer` 에이전트를 호출합니다.

입력:
- 전체 작업 디렉토리: _workspace/backend-{run_id}/

에이전트가 `04_review.md`를 작성합니다.

### Step 5 — 최종 결과 전달

사용자에게 반환:

1. 코드 리뷰 종합 판정
2. 생성된 파일 목록:
   - `01_implementation/` — 구현 코드
   - `02_tests/` — 테스트 코드
   - `03_docs/` — Swagger + README
   - `04_review.md` — 코드 리뷰 보고서
3. CRITICAL / HIGH 이슈 즉시 표시

판정이 ✅이면:
> "백엔드 구현 완료. 다음 단계: `/git-security-scan` 또는 `/dev-frontend`"

❌이면:
> "리뷰 이슈 해결 후 재검수 필요. `04_review.md` 참고"

## 에이전트 호출 규칙
- 모든 에이전트: `model: opus` 사용
- Phase 1 완료 후 Phase 2·3 진행 (구현 코드 필요)
- Phase 4는 Phase 1~3 완료 후 실행

## 작업 규모별 선택적 실행

> 서브에이전트는 각각 독립 컨텍스트를 사용하므로 토큰 소모가 큽니다.
> 입력의 복잡도와 규모를 판단해 필요한 단계만 선택적으로 실행합니다.

| 작업 규모 | 권장 실행 범위 |
|---|---|
| 단순 CRUD / 엔드포인트 1~2개 | Phase 1만 실행 (코드 구현) |
| 중간 규모 (비즈니스 로직 포함) | Phase 1~2 실행 (코드 + 테스트) |
| 신규 도메인 / 복잡한 로직 | Phase 1~4 전체 실행 |

입력을 분석해 단순 작업이면 Phase 1만 실행하고 추가 단계 필요 여부를 사용자에게 확인합니다.
