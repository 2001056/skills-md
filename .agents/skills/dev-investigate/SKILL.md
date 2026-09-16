---
name: dev-investigate
description: 버그·에러·"왜 안 되지" 같은 문제 신고를 받아 조사 전문가 팀(재현 담당·분석가·검수자)을 오케스트레이션해, 재현 → 경쟁 가설 → 인과 사슬 추적 → 수정 재검증을 증거 파일로 남기는 조사 보고 세트를 생성한다. 트리거 — "/dev-investigate". 라우터가 "에러 나요 / 오류 발생 / 왜 안 돼" 같은 신고 어법을 감지하면 자동 적용.
argument-hint: "[증상 설명, 에러 메시지, 재현 단서, 또는 로그 파일 경로]"
---

# /dev-investigate — 조사 단계 오케스트레이터

> 이 스킬의 존재 이유는 하나다. **재현 없이, 가설 하나로 "고쳤다"고 끝내는 것을 막는다.**
> 증상을 보고 떠오른 첫 원인을 바로 고치면, 자주 다른 곳을 고친 채 증상만 가라앉는다.

## 입력
$ARGUMENTS

## 동작

### Step 0 — 입력 검증

`$ARGUMENTS`가 비어 있으면 안내 후 종료:
> "무엇이 어떻게 안 되는지 알려주세요. 에러 메시지, 재현 단서, 로그 경로가 있으면 함께 주세요."

### Step 1 — 작업 공간 생성

`_workspace/investigate-{YYYY-MM-DD}-{NNN}/` 디렉토리 생성.

작업 시작 시 출력:
```
/dev-investigate 조사 단계 시작
run_id: investigate-{YYYY-MM-DD}-{NNN}
```

### Phase 1 — 재현 (investigate-reproducer)

`investigate-reproducer` 에이전트를 호출합니다.

입력:
- 증상 설명: $ARGUMENTS
- 작업 공간: _workspace/investigate-{run_id}/

에이전트가 `01_reproduction.md`를 작성합니다 — 최소 재현 절차, **직접 실행해 얻은** 관찰값, 환경, 재현 판정(재현됨 / 간헐 / 재현 불가).

**재현 불가면** 그 사실과 시도한 것을 그대로 기록합니다. 재현이 안 됐다고 Phase 2를 건너뛰지 않습니다 — 가설에 "왜 재현이 안 되는가"를 포함시킵니다.

완료 후: `✅ Phase 1 완료 — 재현 {재현됨|간헐|불가}`

### Phase 2 — 경쟁 가설 (investigate-analyst, 가설 모드)

`investigate-analyst` 에이전트를 호출합니다.

입력:
- 재현 기록: _workspace/investigate-{run_id}/01_reproduction.md

에이전트가 `02_hypotheses.md`를 작성합니다 — **서로 다른 원인을 가리키는 가설 3개 이상**, 가설마다 지지 증거·반박 증거·확인 방법(무엇을 보면 확정되고 무엇을 보면 기각되는가).

완료 후: `✅ Phase 2 완료 — 가설 {N}개`

### Phase 3 — 원인 추적 · 수정 · 재검증 (investigate-analyst, 추적 모드)

`investigate-analyst` 에이전트를 호출합니다.

입력:
- 재현 기록: 01_reproduction.md
- 가설 목록: 02_hypotheses.md

에이전트가 가설을 증거로 소거하며 `03_root_cause.md`를 작성합니다 — 인과 사슬(증상 → 직접 원인 → 근본 원인), 기각된 가설과 그 근거, 수정 내용, **Phase 1 재현 절차를 다시 돌린 결과**.

완료 후: `✅ Phase 3 완료 — 근본 원인 확정, 재검증 {통과|실패}`

### Phase 4 — 검수 (investigate-reviewer)

`investigate-reviewer` 에이전트를 호출합니다.

입력:
- 전체 작업 디렉토리: _workspace/investigate-{run_id}/

에이전트가 `04_review.md`를 작성합니다.

### Step 5 — 최종 결과 전달

사용자에게 반환:

1. 검수 종합 판정
2. 한 줄 결론 — "{증상}의 근본 원인은 {원인}이며, {수정}으로 재현이 사라졌다" (재현 불가·미해결이면 그 사실을 그대로)
3. 생성된 파일 목록:
   - `01_reproduction.md` — 재현 절차·관찰·환경·판정
   - `02_hypotheses.md` — 경쟁 가설과 확인 방법
   - `03_root_cause.md` — 인과 사슬·소거 근거·수정·재검증
   - `04_review.md` — 조사 검수 보고서
4. CRITICAL / HIGH 이슈 즉시 표시

판정이 ✅이면:
> "조사 완료. 수정이 코드에 반영됐으면 `/git-security-scan` 후 커밋하세요."

❌이면:
> "검수 이슈 해결 후 재검수 필요. `04_review.md` 참고"

## 에이전트 호출 규칙
- 모든 에이전트: `model: opus` 사용
- Phase 순서 고정. Phase 2는 1 없이, Phase 3은 2 없이 실행하지 않는다
- 재현 불가여도 4단계를 모두 남긴다 — "재현 불가"는 결론의 한 종류이고, 결론에는 증거가 필요하다

## 작업 규모별 실행

> 다른 스킬과 달리 **단계를 줄이지 않습니다.** 조사에서 "명백해 보여서 건너뛴 가설"이 오진의 주된 원인입니다.

| 상황 | 실행 |
|---|---|
| 명백한 오타·설정 실수로 보임 | 그래도 1→2→3→4. 가설은 짧게 써도 되지만 재검증은 반드시 |
| 재현 불가 | 1(불가 + 시도 목록) → 2("왜 재현 안 되나" 포함) → 3(가능한 범위) → 4 |
| 이미 원인을 안다고 확신 | 그 확신을 가설 1로 놓고 나머지 2개를 강제로 세운다. 확신은 자주 뒤집힌다 |

## 종료 게이트 계약

플러그인 훅 `stop_gate.py`는 `_workspace/investigate-*/` 안에 `01_reproduction.md` `02_hypotheses.md` `03_root_cause.md` `04_review.md` **네 파일이 모두 존재하고 비어 있지 않아야** 턴을 끝내게 합니다. 파일 하나만 남기고 "고쳤다"고 마무리하면 게이트가 빠진 파일을 지목하며 막습니다.
