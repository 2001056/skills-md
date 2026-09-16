#!/usr/bin/env python3
"""
skills-md 종료 게이트 — Claude Code `Stop` 훅
출처: https://github.com/2001056/skills-md

판정 규칙 (결정론적)
  - 티켓(_workspace/.active-run) 이 없으면 → 통과. 일반 대화는 절대 막지 않는다.
  - stop_hook_active 가 true 면 → 통과. (이미 한 번 막아서 이어가는 중 — 무한루프 방지)
  - SKILLS_MD_GATE=off 면 → 통과.
  - 티켓이 너무 오래됐으면(기본 6시간) → 낡은 티켓 삭제 후 통과.
  - 티켓이 가리키는 작업공간의 증거 파일이 없거나 비어 있으면 → 차단(exit 2).
    빠진 항목을 stderr 로 정확히 알려 모델이 이어서 채우게 한다.
  - 증거가 모두 있으면 → 티켓 삭제 후 통과.

exit 0 = 통과, exit 2 = 차단(stderr 가 모델에게 이유로 전달됨)
"""
import glob
import json
import os
import sys
import time

# 플러그인 모드: 훅은 설치 캐시가 아니라 사용자 프로젝트 디렉토리 기준으로 돌아야 한다.
_proj = os.environ.get("CLAUDE_PROJECT_DIR")
if _proj and os.path.isdir(_proj):
    os.chdir(_proj)

TICKET = os.path.join("_workspace", ".active-run")
STALE_SECONDS = int(os.environ.get("SKILLS_MD_GATE_STALE", str(6 * 3600)))
MIN_BYTES = 40  # "비어 있지 않음"의 하한. 제목 한 줄만 있는 껍데기 파일을 걸러낸다.


def read_stdin_json():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def load_ticket():
    try:
        with open(TICKET, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def latest_workspace(prefix):
    dirs = [d for d in glob.glob(os.path.join("_workspace", prefix + "*")) if os.path.isdir(d)]
    if not dirs:
        return None
    return max(dirs, key=os.path.getmtime)


def check_evidence(ws, ticket):
    """빠진 항목 목록을 돌려준다. 비어 있으면 통과."""
    missing = []
    for rel in ticket.get("evidence", []):
        p = os.path.join(ws, rel)
        if not os.path.isfile(p):
            missing.append("%s 없음" % p)
            continue
        if os.path.getsize(p) < MIN_BYTES:
            missing.append("%s 가 사실상 비어 있음 (%d bytes)" % (p, os.path.getsize(p)))
            continue
        sections = ticket.get("sections") or []
        if sections:
            try:
                text = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                text = ""
            for s in sections:
                if s not in text:
                    missing.append("%s 에 섹션 `%s` 없음" % (p, s))
    return missing


def main():
    if os.environ.get("SKILLS_MD_GATE", "").lower() == "off":
        return 0
    data = read_stdin_json()
    if data.get("stop_hook_active"):
        return 0  # 무한루프 가드

    ticket = load_ticket()
    if not ticket:
        return 0  # 활성 작업 없음 — 통과

    # 낡은 티켓 정리
    if time.time() - int(ticket.get("started_at", 0)) > STALE_SECONDS:
        try:
            os.remove(TICKET)
        except OSError:
            pass
        return 0

    prefix = ticket.get("prefix")
    if not prefix:
        try:
            os.remove(TICKET)
        except OSError:
            pass
        return 0

    ws = latest_workspace(prefix)
    if ws is None:
        missing = ["작업공간 `_workspace/%s{YYYY-MM-DD}-{NNN}/` 이 아직 만들어지지 않음" % prefix]
    else:
        missing = check_evidence(ws, ticket)

    if missing:
        sys.stderr.write(
            "[skills-md stop-gate] 아직 끝낼 수 없습니다 — 규율 `%s` 의 완료 증거가 부족합니다.\n" % ticket.get("discipline")
        )
        for m in missing:
            sys.stderr.write("  - %s\n" % m)
        sys.stderr.write(
            "증거를 실제로 만든 뒤 다시 마무리하세요. 정말 중단해야 하면 사용자에게 '게이트 해제'를 요청하거나 SKILLS_MD_GATE=off 로 우회할 수 있습니다.\n"
        )
        return 2

    # 통과 — 티켓 정리
    try:
        os.remove(TICKET)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
