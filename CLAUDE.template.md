# [프로젝트명] — AI 개발 가이드

> 이 CLAUDE.md는 skills-md 레포를 기반으로 생성된 템플릿입니다.
> 프로젝트에 맞게 수정해서 사용하세요.
> 출처: https://github.com/2001056/skills-md

---

## 프로젝트 개요

<!-- 프로젝트 목적을 2-3줄로 작성 -->
[프로젝트 설명]

**기술 스택:**
- Backend: [Spring Boot / NestJS / FastAPI]
- Frontend: [Next.js / React / Vue 3]
- DB: [PostgreSQL / MySQL / MongoDB]
- 배포: [AWS / GCP / Vercel / Railway]

---

## AI 개발 가이드 로드

<!-- 사용하는 가이드만 남기고 나머지는 삭제하세요 -->

@AI_GUIDE_PLANNING.md
@AI_GUIDE_BACKEND.md
@AI_GUIDE_FRONTEND.md
@AI_GUIDE_ARCHITECTURE.md

---

## 사용 가능한 스킬 (`.agents/` 설치 후)

| 스킬 | 용도 |
|---|---|
| `/dev-plan [기능 설명]` | 기획서 + UserFlow + API 정책 자동 생성 |
| `/dev-backend [구현 대상]` | 코드 + 테스트 + 문서 + 리뷰 자동 생성 |
| `/dev-frontend [구현 대상]` | 컴포넌트 + 접근성 + 리뷰 자동 생성 |
| `/dev-architect [시스템 설명]` | 아키텍처 설계 + ADR 자동 생성 |
| `/git-security-scan` | 커밋 전 보안 취약점 검사 |

---

## 프로젝트 컨벤션

### 코드 스타일
<!-- 팀에서 합의한 컨벤션을 작성 -->
- 들여쓰기: [탭 / 스페이스 N칸]
- 명명 규칙: [camelCase / snake_case / PascalCase]
- 최대 줄 길이: [80 / 100 / 120자]

### 브랜치 전략
```
main        → 프로덕션 배포
develop     → 통합 브랜치
feat/*      → 기능 개발
fix/*       → 버그 수정
hotfix/*    → 긴급 수정
```

### 커밋 메시지 형식
```
feat: 새 기능 추가
fix: 버그 수정
refactor: 코드 리팩터링
docs: 문서 수정
test: 테스트 추가/수정
chore: 빌드·설정 변경
```

### API 응답 형식
```json
// 성공
{ "success": true, "data": { ... }, "message": null }
// 실패
{ "success": false, "data": null, "errorCode": "ERROR_CODE", "message": "설명" }
```

---

## 디렉토리 구조

<!-- 실제 프로젝트 구조로 교체 -->
```
src/
├── [백엔드 구조]
└── [프론트엔드 구조]
```

---

## 환경 변수

<!-- 실제 환경 변수 키 이름만 작성 (값 절대 금지) -->
필수 환경 변수:
- `DATABASE_URL`
- `JWT_SECRET`
- [추가 키들]

참고: `.env.example` 파일 확인

---

## 보안 규칙

- 환경 변수 값을 코드에 직접 작성하지 않음
- `.env` 파일 커밋 금지 (`.gitignore` 확인)
- 커밋 전 `/git-security-scan` 또는 `hooks/pre-commit` 훅 실행

---

## 작업 흐름

```
새 기능 개발 시:
1. /dev-plan "[기능 설명]"    → 기획 산출물 생성
2. /dev-architect "[설명]"    → 아키텍처 결정 (필요시)
3. /dev-backend "[API 명세]"  → 백엔드 구현
4. /dev-frontend "[화면 설명]" → 프론트엔드 구현
5. git add . && /git-security-scan → 보안 검사
6. git commit
```
