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

# 플러그인 모드: 훅은 설치 캐시가 아니라 사용자 프로젝트 디렉토리 기준으로 돌아야 한다.
_proj = os.environ.get("CLAUDE_PROJECT_DIR")
if _proj and os.path.isdir(_proj):
    os.chdir(_proj)

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
        "name": "dev-investigate",
        "skill": "/dev-investigate",
        "prefix": "investigate-",
        "evidence": ["01_reproduction.md", "02_hypotheses.md", "03_root_cause.md", "04_review.md"],
        "signals": [
            # 버그 '신고 어법'만 잡는다 — "에러 상태 UI", "실패 시 재시도" 같은 요구사항 표현은 제외
            r"버그",
            r"(에러|오류)\s*(가\s*|는\s*|이\s*)?(나|남|났|뜨|떠|뜸|발생|생겨|생기|터져|터짐)",
            r"실패\s*(해|함|했|하는데|하네|한다|중)",
            r"안\s*돼", r"안\s*됨", r"왜\s*(이래|안|그래)", r"디버그", r"debug",
            r"원인", r"고장", r"깨졌", r"crash", r"exception", r"traceback", r"500\b", r"404\b",
        ],
        "rules": (
            "재현(01_reproduction.md) → 경쟁 가설 3개+(02_hypotheses.md) → 인과 사슬·수정·재검증(03_root_cause.md) → 검수(04_review.md) 순으로 진행한다. "
            "재현 없이, 가설 하나로 '고쳤다'고 끝내지 않는다. 재현 불가도 결론의 한 종류이며 증거가 필요하다."
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


_LB = r"(?<![A-Za-z0-9])"   # 앞이 영문·숫자가 아니면 경계
_LA = r"(?![A-Za-z0-9])"    # 뒤가 영문·숫자가 아니면 경계


def _kr_boundary(sig):
    """한국어 조사는 영단어에 바로 붙는다("API에", "DB로", "UI가").
    파이썬 re 에서 한글도 \\w 라서 \\bAPI\\b 는 "API에"를 못 잡는다.
    신호 앞뒤의 \\b 를 '영문·숫자 아님' 경계로 바꿔 조사 결합을 통과시킨다."""
    if sig.startswith(r"\b"):
        sig = _LB + sig[2:]
    if sig.endswith(r"\b"):
        sig = sig[:-2] + _LA
    return sig


def display_skill(d):
    """플러그인으로 설치된 경우(CLAUDE_PLUGIN_ROOT 존재) 스킬은 /skills-md: 네임스페이스로 호출된다."""
    s = d["skill"]
    if s.startswith("/") and os.environ.get("CLAUDE_PLUGIN_ROOT"):
        return "/skills-md:" + s[1:]
    return s


def read_stdin_json():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def detect(prompt):
    low = prompt.lower()
    for d in DISCIPLINES:
        for sig in d["signals"]:
            sig = _kr_boundary(sig)
            if re.search(sig, prompt, re.IGNORECASE) or re.search(sig, low):
                return d
    return None


def is_multi_step(prompt):
    return any(re.search(_kr_boundary(p), prompt, re.IGNORECASE) for p in MULTI_STEP)


def write_ticket(d, prompt, multi):
    os.makedirs("_workspace", exist_ok=True)
    ticket = {
        "discipline": d["name"],
        "skill": display_skill(d),
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
    lines.append("[skills-md router] 감지된 규율: %s → %s" % (d["name"], display_skill(d)))
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
