#!/bin/sh
# ============================================================
# skills-md 훅 테스트 — 라우터 + 종료 게이트
# 사용법: sh tests/test_gates.sh   (레포 루트에서)
#
# 원칙: "막아야 할 때 막고, 통과해야 할 때 통과" 를 둘 다 검증한다.
#       한쪽만 초록이면 거짓 통과일 수 있으므로 대조군을 항상 같이 둔다.
# ============================================================

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS="$ROOT/.agents/hooks"
PY="${PY:-python3}"
TMP="$(mktemp -d)"
FAIL=0
PASS=0

ok()   { PASS=$((PASS+1)); printf "  ✅ %s\n" "$1"; }
bad()  { FAIL=$((FAIL+1)); printf "  ❌ %s\n" "$1"; }
check(){ if [ "$1" = "$2" ]; then ok "$3 (exit=$1)"; else bad "$3 (기대 $2, 실제 $1)"; fi; }

cd "$TMP"
unset SKILLS_MD_GATE

router() { printf '{"prompt": "%s"}' "$1" | "$PY" "$HOOKS/router.py"; }
stop()   { printf '{"stop_hook_active": %s}' "${1:-false}" | "$PY" "$HOOKS/stop_gate.py" 2>"$TMP/stderr"; echo $?; }

echo "▶ 1. 일반 대화는 라우터가 개입하지 않는다"
OUT=$(router "안녕 오늘 날씨 어때"); RC=$?
[ -z "$OUT" ] && [ ! -f _workspace/.active-run ] && ok "티켓 없음·출력 없음" || bad "일반 대화에 개입함: $OUT"

echo "▶ 2. 티켓 없으면 Stop 은 항상 통과 (대조군)"
check "$(stop false)" 0 "티켓 없음 → 통과"

echo "▶ 3. 백엔드 신호 → dev-backend 티켓 + 컨텍스트"
OUT=$(router "회원가입 API 엔드포인트 만들어줘")
echo "$OUT" | grep -q "dev-backend" && ok "컨텍스트에 dev-backend" || bad "dev-backend 미감지: $OUT"
[ -f _workspace/.active-run ] && ok "티켓 생성" || bad "티켓 없음"
grep -q '"prefix": "backend-"' _workspace/.active-run && ok "prefix=backend-" || bad "prefix 틀림"

echo "▶ 4. 증거 없이 끝내려 하면 차단 (막아야 할 때)"
check "$(stop false)" 2 "작업공간 없음 → 차단"
grep -q "끝낼 수 없습니다" "$TMP/stderr" && ok "차단 사유가 stderr 로 전달됨" || bad "사유 없음"

mkdir -p _workspace/backend-2026-09-16-001
check "$(stop false)" 2 "작업공간만 있고 04_review.md 없음 → 차단"

printf '# r\n' > _workspace/backend-2026-09-16-001/04_review.md
check "$(stop false)" 2 "껍데기 04_review.md (제목 한 줄) → 차단"

echo "▶ 5. 무한루프 가드: stop_hook_active=true 면 증거 없어도 통과"
check "$(stop true)" 0 "stop_hook_active=true → 통과"
[ -f _workspace/.active-run ] && ok "가드 통과 시 티켓은 유지" || bad "티켓이 지워짐"

echo "▶ 6. 증거를 실제로 채우면 통과하고 티켓이 정리된다 (통과해야 할 때)"
cat > _workspace/backend-2026-09-16-001/04_review.md <<'R'
# 백엔드 코드 리뷰 보고서
## 종합 판정
✅ 통과 — CRITICAL 0 / HIGH 0
## 상세
- 입력 검증 누락 없음
- 테스트 12개 실행, 전부 통과 (pytest 출력 첨부)
R
check "$(stop false)" 0 "증거 완비 → 통과"
[ ! -f _workspace/.active-run ] && ok "통과 후 티켓 삭제" || bad "티켓 남음"

echo "▶ 7. 조사 규율(dev-investigate): 4단계 산출물 계약"
OUT=$(router "로그인하면 500 에러 나는데 왜 이래")
echo "$OUT" | grep -q "dev-investigate" && ok "dev-investigate 감지" || bad "dev-investigate 미감지: $OUT"
W=_workspace/investigate-2026-09-16-001; mkdir -p "$W"
doc(){ printf '# %s\n\n%s\n' "$1" "$2" > "$3"; }
doc "재현" "절차: 로그인 클릭 → 500. 실제 출력: HTTP 500 {error:token}. 환경: main@abc123. 판정: 재현됨" "$W/01_reproduction.md"
doc "가설" "H1 토큰 만료 미처리(로직) / H2 세션 스토어 장애(외부) / H3 프록시 타임아웃(환경) — 각 지지·반박·확인법" "$W/02_hypotheses.md"
check "$(stop false)" 2 "01·02만 있고 03·04 없음 → 차단"
grep -q "03_root_cause.md" "$TMP/stderr" && grep -q "04_review.md" "$TMP/stderr" && ok "빠진 파일 둘을 정확히 지목" || bad "빠진 파일 미지목: $(cat "$TMP/stderr")"
doc "원인" "H2·H3 기각(로그 정상). H1 생존: 증상 500 → 만료 토큰 통과 → 갱신·만료검사 부재. 수정 후 01 절차 재실행: 200 OK, 재현 사라짐" "$W/03_root_cause.md"
check "$(stop false)" 2 "04_review.md 만 없음 → 차단"
doc "검수" "종합 판정 ✅ 원인 확정 — 재현·가설3·사슬 완결·재검증 통과" "$W/04_review.md"
check "$(stop false)" 0 "네 파일 모두 있음 → 통과"
[ ! -f _workspace/.active-run ] && ok "통과 후 티켓 삭제" || bad "티켓 남음"

echo "▶ 8. 우회 스위치"
router "결제 API 만들어줘" >/dev/null
check "$(SKILLS_MD_GATE=off "$PY" "$HOOKS/stop_gate.py" </dev/null; echo $?)" 0 "SKILLS_MD_GATE=off → 통과"
OUT=$(router "게이트 해제")
[ ! -f _workspace/.active-run ] && ok "'게이트 해제' 로 티켓 삭제" || bad "티켓 남음"

echo "▶ 9. 낡은 티켓은 자동 정리"
router "상품 목록 API" >/dev/null
check "$(SKILLS_MD_GATE_STALE=0 "$PY" "$HOOKS/stop_gate.py" </dev/null; echo $?)" 0 "STALE=0 → 낡은 티켓 삭제 후 통과"
[ ! -f _workspace/.active-run ] && ok "낡은 티켓 삭제됨" || bad "티켓 남음"

route(){ printf '{"prompt": %s}' "$(printf '%s' "$1" | "$PY" -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" | "$PY" "$HOOKS/router.py" | head -1; rm -f _workspace/.active-run; }
expect_route(){ OUT=$(route "$2"); echo "$OUT" | grep -q "감지된 규율: $1 " && ok "$3 → $1" || bad "$3 (기대 $1) 실제: ${OUT:-<출력 없음>}"; }

echo "▶ 10. 라우터: README 빠른 시작 예시 5개가 의도한 규율로 간다"
expect_route dev-plan          "카카오페이 같은 간편결제 서비스의 송금 기능 요구사항 정의서 작성해줘" "기획 예시"
expect_route dev-backend       "Spring Boot로 주문 생성 API 만들어줘. 재고 부족 시 409 반환" "백엔드 예시"
expect_route dev-frontend      "Next.js로 주문 목록 페이지 만들어줘. 로딩/에러/빈 상태 모두 처리해야 해" "프론트 예시 (에러 상태≠버그)"
expect_route dev-architect     "DAU 10만 이커머스 서비스 아키텍처 설계해줘. 팀은 5명이야" "아키텍처 예시"
expect_route git-security-scan "커밋 전 보안 검사 해줘" "보안 예시"

echo "▶ 11. 라우터 대조군: 진짜 버그 신고는 여전히 investigate"
expect_route dev-investigate "로그인 누르면 500 에러 나는데 왜 이래" "500 에러 신고"
expect_route dev-investigate "결제하면 오류 발생해" "오류 발생"
expect_route dev-investigate "빌드 실패하는데 원인 찾아줘" "빌드 실패"
expect_route dev-investigate "버그 있어 고쳐줘" "버그"

echo "▶ 12. 라우터 대조군: 요구사항 표현의 에러/실패는 버그로 안 본다"
expect_route dev-frontend "에러 메시지 표시 컴포넌트 만들어줘" "에러 메시지 UI"
expect_route dev-backend  "실패 시 재시도 로직을 결제 API에 넣어줘" "실패 시 재시도 (API+조사 '에')"
expect_route dev-backend  "DB에 인덱스 추가해줘" "DB+조사 '에'"

echo "▶ 13. 플러그인 모드면 스킬을 /skills-md: 네임스페이스로 표시"
OUT=$(printf '{"prompt":"회원 API 만들어줘"}' | CLAUDE_PLUGIN_ROOT=/tmp/x "$PY" "$HOOKS/router.py" | head -1); rm -f _workspace/.active-run
echo "$OUT" | grep -q "/skills-md:dev-backend" && ok "플러그인 모드 → /skills-md:dev-backend" || bad "네임스페이스 미표시: $OUT"
OUT=$(printf '{"prompt":"회원 API 만들어줘"}' | "$PY" "$HOOKS/router.py" | head -1); rm -f _workspace/.active-run
echo "$OUT" | grep -q "→ /dev-backend" && ok "복사 모드 → /dev-backend (대조군)" || bad "복사 모드 표시 틀림: $OUT"

echo ""
echo "────────────────────────────────"
echo "PASS: $PASS   FAIL: $FAIL"
rm -rf "$TMP"
[ "$FAIL" -eq 0 ] && { echo "✅ 전부 통과"; exit 0; } || { echo "❌ 실패 있음"; exit 1; }
