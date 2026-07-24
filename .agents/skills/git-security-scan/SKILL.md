---
name: git-security-scan
description: git add로 스테이징된 변경사항을 커밋 전에 보안 취약점 검사. 시크릿 하드코딩·민감 파일·SQL 인젝션·디버그 모드 노출 등을 CRITICAL/HIGH/MEDIUM/LOW 4단계로 분류해 보고. 트리거 — "/git-security-scan".
argument-hint: "[git diff --staged 출력 붙여넣기, 또는 생략 시 자동 실행]"
---

# /git-security-scan — 커밋 전 보안 검사

## 입력
$ARGUMENTS

## 동작

### Step 1 — diff 수집

`$ARGUMENTS`가 비어 있으면 `git diff --staged`를 직접 실행해 diff를 가져온다.
diff 결과가 비어 있으면 다음을 출력하고 종료:
> "스테이징된 변경사항이 없습니다. `git add` 후 다시 실행하세요."

`$ARGUMENTS`에 diff 텍스트가 붙여넣어진 경우 그것을 그대로 분석 대상으로 사용한다.

### Step 2 — 보안 검사 수행

**검사 대상: `+`로 시작하는 라인(새로 추가된 코드)만. `-` 라인(삭제 코드)은 검사하지 않는다.**

아래 4단계 기준 순서로 전체 diff를 검사한다.

---

#### 🔴 CRITICAL — 즉시 커밋 차단

**C-1. 시크릿 / 자격증명 하드코딩**

다음 API 키 패턴이 추가 라인에 존재하는지 검사:
```
sk-[A-Za-z0-9]{20,}                       → OpenAI API Key
AKIA[A-Z0-9]{16}                           → AWS Access Key ID
ghp_[A-Za-z0-9]{36}                       → GitHub Personal Access Token
ghs_[A-Za-z0-9]{36}                       → GitHub App Secret
AIza[A-Za-z0-9_-]{35}                     → Google API Key
ya29\.[A-Za-z0-9_-]+                       → Google OAuth Token
xoxb-[A-Za-z0-9-]+                         → Slack Bot Token
xoxp-[A-Za-z0-9-]+                         → Slack User Token
SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43} → SendGrid API Key
key-[A-Za-z0-9]{32}                        → Mailgun API Key
AC[a-z0-9]{32}                             → Twilio Account SID
SK[a-z0-9]{32}                             → Twilio Auth Token
-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----
```

비밀번호 변수 직접 할당 패턴:
```
(password|passwd|pwd|secret|api_key|apikey|api-key|token|auth_token|access_token|secret_key|private_key)\s*[=:]\s*["'][^${}()\s]{4,}["']
```

False Positive 예외 (보고하지 않음):
- 값이 `${...}`, `process.env.`, `os.environ`, `@Value`, `secrets.` 형태
- 값이 `your-`, `<your-`, `placeholder`, `change-me`, `xxx`, `example` 등 플레이스홀더
- `*.test.*`, `*.spec.*`, `__tests__/` 파일 내 더미 값
- `*.example`, `*.sample`, `*.template` 파일
- README, 문서 파일 내 코드 블록
- 삭제된 라인(`-`로 시작)

발견 시 보고 형식:
```
🔴 CRITICAL — 하드코딩된 시크릿 감지
  파일: src/config/database.js (line 12)
  내용: password = "db_p****"  (마스킹 처리)
  조치: 환경변수로 교체 → process.env.DB_PASSWORD
        .env.example에 키 이름만 추가
        이미 커밋된 적 있다면 → 아래 유출 대응 절차 참고
```

**C-2. 민감 파일 자체 스테이징**

`diff --git a/` 라인에 다음 파일이 포함되어 있으면 CRITICAL:
```
.env / .env.local / .env.development / .env.staging / .env.production / .env.test
*.pem / *.key (*.lock 제외, 정확히 .key 확장자) / *.p12 / *.pfx / *.jks / *.keystore
id_rsa / id_ed25519 / id_ecdsa
credentials.json / service-account*.json / firebase-adminsdk*.json
google-credentials.json / gcloud-key*.json
*.secret / secrets.yaml / secrets.yml / vault-token
.netrc / .aws/credentials / .ssh/id_*
```

발견 시 보고 형식:
```
🔴 CRITICAL — 민감 파일 스테이징 감지
  파일: .env
  조치:
    1. git reset HEAD .env          (스테이징 취소)
    2. .gitignore에 .env 추가 확인
    3. 이미 커밋된 기록이 있다면 → git rm --cached .env 후 커밋
    4. 파일 내 시크릿이 실제 값이라면 즉시 무효화/재발급
```

**C-3. 클라우드 자격증명 직접 작성**
```
aws_access_key_id: AKIA...  /  aws_secret_access_key: ...
"type": "service_account"   (GCP service account JSON 구조)
client_secret: ...          /  subscription_key: ...  (Azure)
```

---

#### 🟠 HIGH — 커밋 전 해결 권장

**H-1. 내부 인프라 정보 노출**
- RFC 1918 내부 IP: `10.x.x.x` / `172.16-31.x.x` / `192.168.x.x`
- 내부 호스트명: `(internal|private|prod)-*.local|corp|lan`
- DB URI 자격증명 포함: `mongodb://user:pass@` / `postgresql://user:pass@`
- 예외: 주석 처리 라인, README 예시

**H-2. 디버그 모드 활성화 (프로덕션 파일)**
```
DEBUG = True  /  app.debug = True  /  app.run(debug=True)
spring.jpa.show-sql: true  /  spring.h2.console.enabled: true
NODE_ENV = 'development'  (프로덕션 설정 파일에서)
```

**H-3. 민감 정보 로그 출력**
```
console.log(password, token, secret, apiKey, user.password)
log.info("password: {}", password)  /  System.out.println(apiKey)
print(password)  /  logging.info(f"token: {access_token}")
```

**H-4. 위험한 보안 설정**
```
cors({ origin: '*' })           (CORS 전체 허용, 프로덕션)
rejectUnauthorized: false       (SSL 검증 비활성화)
verify=False                    (Python requests SSL 비활성화)
privileged: true                (Kubernetes)
allowPrivilegeEscalation: true
```

---

#### 🟡 MEDIUM — 다음 작업 시 해결

**M-1. 보안 관련 TODO/FIXME 주석**
```
// TODO: 인증 추가 예정
// FIXME: 임시로 권한 체크 제거함
// HACK: 빠른 배포를 위해 검증 스킵
```

**M-2. 취약한 암호화 / 해시 알고리즘**
```
md5(password)  /  sha1(password)
DES / 3DES / RC4 / AES ECB 모드
Math.random()  /  random.random()  (보안 목적 사용 시)
```

**M-3. SQL 인젝션 위험 패턴**
```
`SELECT * FROM users WHERE id = ${userId}`
"SELECT ... WHERE name = '" + name + "'"
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**M-4. NEXT_PUBLIC_ 변수에 민감 정보**
```
NEXT_PUBLIC_API_SECRET=sk-abc123
NEXT_PUBLIC_DB_PASSWORD=secret123
```
`NEXT_PUBLIC_` 변수 값에 `secret`, `password`, `key`, `token`, `private`, `credential` 포함 여부 확인

---

#### 🔵 LOW / INFO — 참고

**L-1. .gitignore 미설정 가능성**
스테이징 목록에 `*.log`, `*.tmp`, `node_modules/`, `__pycache__/`, `.DS_Store`, `target/`, `build/`, `dist/` 포함 시

**L-2. 대용량 이진 파일**
`*.jar`, `*.war`, `*.zip`, `*.tar.gz` 등 빌드 아티팩트

**L-3. 주석 처리된 인증/인가 코드**
```
// if (!isAuthenticated) return res.status(401).json(...)
// @PreAuthorize("hasRole('ADMIN')")
```

---

### Step 3 — 결과 보고

반드시 다음 형식으로 출력한다:

```
🔍 보안 검사 결과
──────────────────────────────────────
🔴 CRITICAL : X건  (즉시 커밋 중단)
🟠 HIGH     : X건  (이번 커밋에서 해결 권장)
🟡 MEDIUM   : X건  (다음 작업 시 해결)
🔵 LOW/INFO : X건  (참고)
──────────────────────────────────────
[각 항목 파일명·라인·조치 상세]
```

CRITICAL 또는 HIGH가 1건이라도 있으면:
> ⛔ 커밋을 중단하세요. 위 항목을 해결한 뒤 다시 `/git-security-scan`을 실행하세요.

모두 MEDIUM 이하이면:
> ✅ 커밋 진행 가능합니다. MEDIUM 이하 항목은 후속 작업으로 처리하세요.

---

## 시크릿 이미 유출된 경우 대응 절차

CRITICAL 항목이 이미 커밋/푸시된 경우에만 안내:

```
1. 🚨 해당 시크릿 즉시 무효화 (가장 먼저)
2. Git 히스토리 제거
   java -jar bfg.jar --replace-text secrets.txt my-repo.git
3. 강제 푸시 (팀원 사전 고지 필수)
   git push origin --force --all
4. GitHub Secret Scanning 알림 확인
```
> ⚠️ 히스토리 제거 전에 반드시 시크릿 무효화부터 진행.

## 재발 방지 도구 (이슈 발견 시에만 안내)

```bash
# gitleaks pre-commit hook
brew install gitleaks   # macOS
scoop install gitleaks  # Windows
# .git/hooks/pre-commit에 추가:
gitleaks protect --staged --redact -v || exit 1
```
GitHub → Settings → Security → Secret scanning → Push protection 활성화 (무료)
