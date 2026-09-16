#!/usr/bin/env python3
"""
skills-md 자동 라우터 — Claude Code `UserPromptSubmit` 훅
출처: https://github.com/2001056/skills-md

동작
  1. 사용자 프롬프트에서 작업 신호를 감지해 "가장 작은 일치 규율" 하나를 고른다.
  2. 작업공간형 규율이면 `_workspace/.active-run` 티켓을 쓴다 (stop_gate.py 가 읽음).
  3. 골라진 스킬과 "끝내기 전 반드시 존재해야 할 증거 파일"을 컨텍스트로 주입한다.
  4. 신호가 없으면 아무것도 하지 않는다 (일반 대화는 건드리지 않음).

우회: 환경변수 SKILLS_MD_GATE=off
해제: 프롬프트에 "게이트 해제" 또는 "gate off" 포함 시 티켓 삭제
"""
import json
import os
import re
import sys
import time

TICKET = os.path.join("_workspace", ".active-run")

# 규율 정의 — 순서가 우선순위. 앞에 있을수록 먼저 매칭.
# evidence 는 작업공간 디렉토리 기준 상대경로. 여러 개면 모두 필요.
# sections 는 evidence 파일 안에 반드시 있어야 할 헤딩(투자 규율용).
DISCIPLINES = [
    {
        "name": "git-security-scan",
        "skill": "/git-security-scan",
        "prefix": None,  # 작업공간 없음 → 게이트 비대상
        "evidence": [],
        "signals": [r"/git-security-scan", r"커밋\s*전\s*보안", r"시크릿\s*(검사|스캔)", r"security[- ]scan"],
        "rules": "스테이징된 diff 를 CRITICAL/HIGH/MEDIUM/LOW 로 분류해 보고한다.",
    },
    {
        "name": "investigate",
        "skill": "(내장 규율) 조사 프로토콜",
        "prefix": "investigate-",
        "evidence": ["evidence.md"],
        "sections": ["## 재현", "## 가설", "## 원인"],
        "signals": [
            r"버그", r"에러", r"오류", r"안\s*돼", r"안\s*됨", r"왜\s*(이래|안|그래)", r"디버그", r"debug",
            r"원인", r"고장", r"깨졌", r"실패", r"crash", r"exception", r"traceback", r"500\b", r"404\b",
        ],
        "rules": (
            "1) 먼저 재현한다 — 재현 못 하면 '재현 불가'를 근거와 함께 기록.\n"
            "2) 경쟁 가설 3개 이상을 세우고, 가설마다 지지/반박 증거를 모은다.\n"
            "3) 인과 사슬을 끝까지 추적한다 (증상 → 직접 원인 → 근본 원인).\n"
            "4) 수정 뒤 재현 절차를 다시 돌려 사라졋는지 확인한 결과를 적는다.\n"
            "위 내용을 evidence.md 의 `## 재현` `## 가설` `## 원인` 섹션에 기록한다."
        ),
    },
    {
        "name": "dev-plan",
        "skill": "/dev-plan",
        "prefix": "plan-",
        "evidence": ["04_review.md"],
        "signals": [r"/dev-plan", r"기획", r"요구사항", r"\bPRD\b", r"유저\s*스토리", r"user\s*stor", r"화면\s*목록", r"\bIA\b"],
        "rules": "요구사항 → UX 플로우 → API 정책 → 검수 순으로 진행하고, 04_review.md 판정까지 낸다.",
    },
    {
        "name": "dev-architect",
        "skill": "/dev-architect",
        "prefix": "architect-",
        "evidence": ["03_review.md"],
        "signals": [r"/dev-architect", r"아키텍처", r"시스템\s*설계", r"\bADR\b", r"기술\s*선정", r"architecture"],
        "rules": "아키텍처 설계 → ADR → 검수 순으로 진행하고, 03_review.md 판정까지 낸다.",
    },
    {
        "name": "dev-frontend",
        "skill": "/dev-frontend",
        "prefix": "frontend-",
        "evidence": ["03_review.md"],
        "signals": [r"/dev-frontend", r"컴포넌트", r"프론트", r"화면\s*(구현|만들)", r"\bUI\b", r"\bReact\b", r"\bVue\b", r"Next\.?js", r"접근성", r"a11y"],
        "rules": "컴포넌트 구현 → 접근성(WCAG 2.1 AA) 검사 → 리뷰 순으로 진행하고, 03_review.md 판정까지 낸다. 렌더되는 산출물은 실제로 띄워 본 결과를 근거로 고친다.",
    },
    {
        "name": "dev-backend",
        "skill": "/dev-backend",
        "prefix": "backend-",
        "evidence": ["04_review.md"],
        "signals": [r"/dev-backend", r"\bAPI\b", r"엔드포인트", r"백엔드", r"서버\s*(구현|로직)", r"\bDB\b", r"데이터베이스", r"스키마", r"\bCRUD\b", r"Spring", r"NestJS", r"FastAPI"],
        "rules": "코드 구현 → 테스트 → 문서 → 리뷰 순으로 진행하고, 04_review.md 판정까지 낸다. 테스트는 실제로 실행한 결과를 근거로 남긴다.",
    },
]

MULTI_STEP = [r"그리고\s*(나서|난\s*뒤|다음)", r"다음에", r"순서대로", r"단계", r"1\)\s*.+2\)", r"먼저.+(그\s*다음|그리고)", r"\bthen\b"]


def read_stdin_json():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def detect(prompt):
    low = prompt.lower()
    for d in DISCIPLINES:
        for sig in d["signals"]:
            if re.search(sig, prompt, re.IGNORECASE) or re.search(sig, low):
                return d
    return None


def is_multi_step(prompt):
    return any(re.search(p, prompt, re.IGNORECASE) for p in MULTI_STEP)


def write_ticket(d, prompt, multi):
    os.makedirs("_workspace", exist_ok=True)
    ticket = {
        "discipline": d["name"],
        "skill": d["skill"],
        "prefix": d["prefix"],
        "evidence": d["evidence"],
        "sections": d.get("sections", []),
        "multi_step": multi,
        "started_at": int(time.time()),
        "prompt_head": prompt.strip().replace("\n", " ")[:120],
    }
    with open(TICKET, "w", encoding="utf-8") as f:
        json.dump(ticket, f, ensure_ascii=False, indent=2)


def main():
    if os.environ.get("SKILLS_MD_GATE", "").lower() == "off":
        return 0
    data = read_stdin_json()
    prompt = data.get("prompt") or ""
    if not prompt.strip():
        return 0

    # 수동 해제
    if re.search(r"게이트\s*해제|gate\s*off", prompt, re.IGNORECASE):
        if os.path.exists(TICKET):
            os.remove(TICKET)
            print("[skills-md router] 활성 티켓을 해제했습니다. 이번 턴은 게이트 없이 종료할 수 있습니다.")
        return 0

    d = detect(prompt)
    if d is None:
        return 0  # 일반 대화 — 개입하지 않음

    multi = is_multi_step(prompt)
    lines = []
    lines.append("[skills-md router] 감지된 규율: %s → %s" % (d["name"], d["skill"]))
    lines.append("규칙: " + d["rules"])

    if d["prefix"]:
        write_ticket(d, prompt, multi)
        ev = ", ".join(d["evidence"])
        lines.append(
            "완료 조건(stop-gate 가 검사): `_workspace/%s{YYYY-MM-DD}-{NNN}/` 안에 %s 가 실제로 존재하고 비어 있지 않아야 턴을 끝낼 수 있다."
            % (d["prefix"], ev)
        )
        if d.get("sections"):
            lines.append("evidence.md 필수 섹션: " + " / ".join(d["sections"]))
        lines.append("증거 없이 '완료'라고 쓰지 말 것. 막히면 사용자에게 '게이트 해제'를 요청하거나 SKILLS_MD_GATE=off 로 우회 가능.")
    else:
        lines.append("(작업공간 없는 단일 규율 — 종료 게이트 비대상)")

    if multi:
        lines.append(
            "다단계 작업 감지: 스토리를 순서대로 하나씩 끝내고, 각 스토리마다 '무엇을 확인했는지' 한 줄 증거를 남긴 뒤 다음으로 넘어간다."
        )

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
