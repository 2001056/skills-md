#!/bin/sh
# ============================================================
# skills-md Claude Code 훅 설치 (자동 라우터 + 종료 게이트)
# 사용법: sh hooks/install-claude-hooks.sh   (프로젝트 루트에서)
#
# 하는 일
#   - 프로젝트의 .claude/settings.json 에 UserPromptSubmit / Stop 훅을 병합한다.
#   - 기존 settings 의 다른 항목은 건드리지 않는다 (멱등).
#   - python3 이 없고 python 만 있으면 명령어를 python 으로 바꿔 넣는다.
#
# 우회: 환경변수 SKILLS_MD_GATE=off
# 제거: .claude/settings.json 에서 hooks.UserPromptSubmit / hooks.Stop 항목 삭제
# ============================================================

set -e
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

if [ ! -f ".agents/hooks/router.py" ] || [ ! -f ".agents/hooks/stop_gate.py" ]; then
  echo "❌ .agents/hooks/router.py 또는 stop_gate.py 가 없습니다. .agents 폴더를 먼저 복사하세요."
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
  echo "❌ python3 (또는 python) 이 필요합니다."; exit 1
fi

mkdir -p .claude
[ -f .claude/settings.json ] || echo '{}' > .claude/settings.json

echo "🔧 Claude Code 훅 병합 중... (.claude/settings.json, 인터프리터: $PY)"

"$PY" - "$PY" <<'PYEOF'
import json, sys
py = sys.argv[1]
path = ".claude/settings.json"
try:
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
except Exception:
    settings = {}
hooks = settings.setdefault("hooks", {})

def entry(cmd):
    return {"hooks": [{"type": "command", "command": cmd}]}

def merge(event, cmd):
    lst = hooks.setdefault(event, [])
    for e in lst:
        for h in e.get("hooks", []):
            if h.get("command") == cmd:
                return False
    lst.append(entry(cmd))
    return True

a = merge("UserPromptSubmit", "%s .agents/hooks/router.py" % py)
b = merge("Stop", "%s .agents/hooks/stop_gate.py" % py)
with open(path, "w", encoding="utf-8") as f:
    json.dump(settings, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("  UserPromptSubmit 라우터:", "추가됨" if a else "이미 있음")
print("  Stop 종료 게이트     :", "추가됨" if b else "이미 있음")
PYEOF

echo ""
echo "✅ 설치 완료. Claude Code 를 다시 열면 적용됩니다."
echo "   우회: SKILLS_MD_GATE=off    해제: 프롬프트에 '게이트 해제'"
echo "   확인: sh tests/test_gates.sh"
