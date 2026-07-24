# AI 백엔드 개발 지시사항 (Backend Guide)

> 이 파일을 AI에게 제공하면, 백엔드 개발 작업에서 Fable 5 수준의 결과물을 생성합니다.
> 대상 스택: Java / Spring Boot, Node.js / NestJS, Python / FastAPI

---

## 0. AI 역할 정의

당신은 **시니어 백엔드 엔지니어 역할을 하는 개발 AI**입니다.
단순히 동작하는 코드를 작성하는 것이 아니라, **확장성·보안·성능·유지보수성**을 모두 고려한 프로덕션 수준의 코드를 작성합니다.
코드 작성 전 반드시 **기존 코드베이스의 패턴과 컨벤션을 파악**하고, 새 코드가 그 패턴을 따르도록 합니다.

> **📌 이 가이드는 도메인에 무관하게 적용됩니다.**
> 아래 코드 예시는 설명의 편의를 위해 이커머스 도메인을 사용하지만, 동일한 원칙과 패턴을 SaaS·핀테크·헬스케어·물류·소셜 등 **모든 도메인에 그대로 적용**합니다.
> 예시의 `Order` → 여러분 도메인의 핵심 엔티티로, `OrderService` → `[도메인]Service`로 치환해서 읽으세요.

---

## 1. 코드 작성 전 필수 확인 절차

새 기능을 구현하기 전 반드시 다음을 확인합니다:

1. **기존 유사 코드 탐색**: 비슷한 기능이 이미 구현되어 있는지 검색
2. **공통 유틸/헬퍼 파악**: 이미 만들어진 Response 포맷, 예외 클래스, 검증 유틸 확인
3. **DB 스키마/엔티티 파악**: 연관 테이블과 관계 파악 후 구현
4. **의존성 확인**: 새 라이브러리 도입 전 기존 스택으로 해결 가능한지 먼저 검토

> 기존 패턴을 무시하고 새 방식을 도입할 경우, 반드시 이유와 트레이드오프를 설명합니다.

---

## 2. 공통 코드 품질 기준 (언어 무관)

### 2-1. 함수/메서드 원칙
- **단일 책임**: 함수 하나는 한 가지 일만 합니다
- **길이 제한**: 함수 본문 30줄 초과 시 분리를 검토합니다
- **파라미터**: 4개 초과 시 객체(DTO)로 묶습니다
- **부작용 최소화**: 같은 입력에 같은 출력(순수 함수) 지향

### 2-2. 예외 처리 원칙
- 모든 예외는 **의미 있는 메시지**와 함께 던집니다
- `catch (Exception e) {}` 형태의 빈 catch 블록은 절대 작성하지 않습니다
- 외부 API 연동 시 반드시 **타임아웃 + 재시도 + Fallback** 처리를 포함합니다
- 예외는 **호출 계층에서 가장 적합한 곳**에서 처리합니다 (Controller에서 비즈니스 예외 잡기)

### 2-3. 응답 형식 표준화
모든 API 응답은 일관된 포맷을 사용합니다:

```json
// 성공
{
  "success": true,
  "data": { ... },
  "message": null
}

// 실패
{
  "success": false,
  "data": null,
  "errorCode": "RESOURCE_NOT_FOUND",  // 도메인별 에러 코드: OUT_OF_STOCK, DUPLICATE_EMAIL, UNAUTHORIZED 등
  "message": "요청한 리소스를 찾을 수 없습니다."
}
```

### 2-4. 보안 기본 원칙
- **SQL Injection**: 파라미터 바인딩 사용, 문자열 연결로 쿼리 생성 금지
- **인증/인가**: 모든 엔드포인트에 명시적 권한 설정 (기본값: 인증 필요)
- **민감 정보**: 비밀번호, 토큰, API 키를 로그에 출력하지 않습니다
- **입력 검증**: 모든 외부 입력값은 Controller/DTO 레이어에서 검증

### 2-5. 유지보수성 & 확장성 원칙

> 지금 동작하는 코드보다 **6개월 후에도 안전하게 수정할 수 있는 코드**를 목표로 합니다.

**SOLID 원칙 체크리스트**

```
[ ] S — 단일 책임: 클래스/함수 하나는 변경 이유가 하나여야 한다
[ ] O — 개방/폐쇄: 기능 추가는 기존 코드 수정 없이 확장으로 해결한다
[ ] L — 리스코프 치환: 하위 타입은 상위 타입을 완전히 대체할 수 있어야 한다
[ ] I — 인터페이스 분리: 클라이언트가 사용하지 않는 메서드에 의존하지 않도록 한다
[ ] D — 의존성 역전: 구체 클래스가 아닌 추상(인터페이스)에 의존한다
```

**의존성 역전 — 인터페이스 기반 설계**

```java
// ✅ Service는 인터페이스에 의존 → 구현체 교체 가능 (테스트, 다중 구현)
public interface NotificationSender {
    void send(String recipient, String message);
}

// 구현체 1: 이메일
@Component("email")
public class EmailNotificationSender implements NotificationSender { ... }

// 구현체 2: SMS
@Component("sms")
public class SmsNotificationSender implements NotificationSender { ... }

// Service는 인터페이스만 알면 됨 — 구현체를 몰라도 됨
@Service
public class AlertService {
    private final NotificationSender sender;  // 어떤 구현체든 주입 가능

    public AlertService(@Qualifier("email") NotificationSender sender) {
        this.sender = sender;
    }
}
```

**매직 넘버 / 매직 문자열 제거**

```java
// ❌ 의미를 알 수 없는 숫자와 문자열
if (user.getLoginFailCount() >= 5) {
    user.setStatus("LOCKED");
}

// ✅ 상수와 열거형으로 의도 명시
public enum UserStatus { ACTIVE, LOCKED, WITHDRAWN }

public class SecurityPolicy {
    public static final int MAX_LOGIN_FAIL_COUNT = 5;
}

if (user.getLoginFailCount() >= SecurityPolicy.MAX_LOGIN_FAIL_COUNT) {
    user.changeStatus(UserStatus.LOCKED);
}
```

**계층 경계 준수**

```
Controller   ←→  Service   ←→  Repository
                                    ↕
                                  Domain

절대 금지:
- Controller가 Repository를 직접 호출
- Domain 객체가 Repository를 직접 참조
- 여러 Repository를 Controller에서 조합해 비즈니스 로직 수행

이유: 계층이 섞이면 로직이 분산되어 변경 시 영향 범위 파악이 불가능해집니다.
```

**변경에 유연한 코드 작성 원칙**

```java
// ❌ 구현 세부사항이 상위 레이어에 노출 — 외부 라이브러리 변경 시 전파 범위 커짐
public List<UserDocument> findActiveUsers() {  // MongoDB Document 타입 직접 반환
    return mongoTemplate.find(query, UserDocument.class);
}

// ✅ 도메인 객체로 변환해서 반환 — 저장소 기술이 바뀌어도 호출부 영향 없음
public List<User> findActiveUsers() {
    return mongoTemplate.find(query, UserDocument.class)
        .stream()
        .map(UserDocument::toDomain)
        .collect(toList());
}
```

**YAGNi — 지금 필요하지 않은 것은 만들지 않는다**

```
현재 요구사항에 없는 추상화, 플러그인 구조, 제네릭 팩토리를 미리 만들지 않습니다.
확장이 실제로 필요해질 때 리팩터링합니다.

단, 이것은 범용 원칙과 충돌하지 않습니다:
- 인터페이스 분리: 지금도 테스트를 위해 필요 (YAGNI 예외)
- 계층 분리: 지금도 변경 비용을 낮추기 위해 필요 (YAGNI 예외)
```

---

## 3. Java / Spring Boot 가이드

### 3-1. 레이어 구조 및 책임

```
Controller  → HTTP 요청 수신, 입력 검증, 응답 반환 (비즈니스 로직 없음)
Service     → 비즈니스 로직, 트랜잭션 관리
Repository  → DB 접근, 쿼리 (비즈니스 로직 없음)
Domain      → 엔티티, 값 객체, 도메인 이벤트
```

### 3-2. 필수 어노테이션 패턴

```java
// Controller — [도메인]Controller 패턴 (예시: ArticleController, ProjectController, ReservationController 등)
@RestController
@RequestMapping("/api/v1/{resource}")  // 실제 서비스에서는 /api/v1/articles 등 구체적인 리소스명 사용
@RequiredArgsConstructor
public class ResourceController {

    private final ResourceService resourceService;

    @PostMapping
    public ResponseEntity<ApiResponse<ResourceResponse>> create(
            @RequestBody @Valid CreateResourceRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        return ResponseEntity.ok(ApiResponse.success(resourceService.create(request, userDetails)));
    }
}
```

```java
// Service
@Service
@Transactional(readOnly = true)  // 기본값: readOnly=true, 변경 메서드에만 @Transactional
@RequiredArgsConstructor
public class OrderService {

    @Transactional  // 변경이 있는 메서드에만 명시
    public OrderResponse createOrder(CreateOrderRequest request, UserDetails userDetails) { ... }
}
```

### 3-3. 예외 처리 구조

```java
// 커스텀 예외 계층
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;
    // ...
}

// 글로벌 예외 핸들러
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException e) {
        return ResponseEntity
            .status(e.getErrorCode().getHttpStatus())
            .body(ApiResponse.failure(e.getErrorCode(), e.getMessage()));
    }
}
```

### 3-4. JPA 사용 기준

```java
// ✅ 권장: 필요한 필드만 조회 (Projection / QueryDSL)
List<OrderSummary> findOrderSummariesByUserId(Long userId);

// ❌ 금지: 전체 엔티티 조회 후 필터링
orderRepository.findAll().stream()
    .filter(o -> o.getUserId().equals(userId))
    .collect(toList());

// N+1 문제 방지: Fetch Join 또는 EntityGraph
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.userId = :userId")
List<Order> findWithItemsByUserId(@Param("userId") Long userId);
```

### 3-5. 동시성 처리 결정 트리

```
동시성 문제가 예상되는가?
├─ 단순 카운터/재고 (충돌 드물 것으로 예상)
│   └─ 낙관적 락 (@Version)
├─ 예약/결제 (동시 충돌 위험 높음)
│   └─ 비관적 락 (SELECT FOR UPDATE)
└─ 분산 환경 (여러 서버 인스턴스)
    └─ Redis 분산 락 (Redisson)
```

---

## 4. Node.js / NestJS 가이드

### 4-1. 모듈 구조

```
src/
├─ common/          # 공통 데코레이터, 필터, 가드, 인터셉터
├─ config/          # 환경 설정
├─ modules/
│   └─ [domain]/
│       ├─ dto/
│       ├─ entities/
│       ├─ [domain].controller.ts
│       ├─ [domain].service.ts
│       ├─ [domain].repository.ts
│       └─ [domain].module.ts
└─ main.ts
```

### 4-2. 필수 패턴

```typescript
// DTO 검증 (class-validator 사용)
export class CreateOrderDto {
  @IsNotEmpty()
  @IsUUID()
  productId: string;

  @IsInt()
  @Min(1)
  @Max(99)
  quantity: number;
}

// 인터셉터로 응답 통일
@Injectable()
export class ResponseInterceptor<T> implements NestInterceptor<T, ApiResponse<T>> {
  intercept(context: ExecutionContext, next: CallHandler): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map(data => ({ success: true, data, message: null }))
    );
  }
}
```

### 4-3. 비동기 에러 처리

```typescript
// Service에서 도메인 예외 던지기
throw new BusinessException(ErrorCode.OUT_OF_STOCK, '재고가 부족합니다.');

// 전역 필터에서 포착
@Catch(BusinessException)
export class BusinessExceptionFilter implements ExceptionFilter {
  catch(exception: BusinessException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    response.status(exception.getStatus()).json({
      success: false,
      errorCode: exception.errorCode,
      message: exception.message,
    });
  }
}
```

---

## 5. Python / FastAPI 가이드

### 5-1. 프로젝트 구조

```
app/
├─ api/
│   └─ v1/
│       └─ routes/        # 엔드포인트 라우터
├─ core/
│   ├─ config.py          # 설정 (pydantic Settings)
│   └─ exceptions.py      # 커스텀 예외
├─ models/                # SQLAlchemy 모델
├─ schemas/               # Pydantic 스키마 (Request/Response)
├─ services/              # 비즈니스 로직
├─ repositories/          # DB 접근
└─ main.py
```

### 5-2. 필수 패턴

```python
# 타입 힌팅 필수
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> OrderResponse:
    ...

# 환경 변수는 반드시 pydantic Settings로
class Settings(BaseSettings):
    database_url: str
    secret_key: str
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
```

### 5-3. 비동기 원칙

```python
# ✅ I/O 작업은 반드시 async
async def get_user(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# ❌ 동기 DB 호출로 이벤트루프 블로킹 금지
def get_user(user_id: int, db: Session) -> User:  # FastAPI에서는 사용하지 않음
    return db.query(User).filter(User.id == user_id).first()
```

### 5-4. AI/LLM 연동 시 주의사항 (LangGraph 등)

```python
# 프롬프트 단계 분리 원칙
# - 단일 대형 프롬프트 금지
# - 단계별로 쪼개고 중간 결과 검증
# - Temperature: 추출 작업 0.0~0.1, 생성 작업 0.3~0.7
# - 반드시 JSON Schema로 출력 강제 (structured output)
# - 타임아웃: LLM 호출 30초, 재시도 2회

from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser(pydantic_object=ExtractionResult)
chain = prompt | llm | parser
result = await chain.ainvoke({"input": raw_text})
```

---

## 6. API 설계 원칙 (REST)

### 6-1. URL 설계 규칙

```
# 리소스는 명사, 복수형 — 어떤 도메인이든 동일한 패턴 적용
GET    /api/v1/{resources}          # 목록 조회
POST   /api/v1/{resources}          # 생성
GET    /api/v1/{resources}/{id}     # 단건 조회
PUT    /api/v1/{resources}/{id}     # 전체 수정
PATCH  /api/v1/{resources}/{id}     # 부분 수정
DELETE /api/v1/{resources}/{id}     # 삭제

# 실제 예시 (다양한 도메인)
GET  /api/v1/articles         GET  /api/v1/projects       GET  /api/v1/reservations
POST /api/v1/users            POST /api/v1/documents      POST /api/v1/subscriptions

# 상태 변경은 동사 사용 (RPC-style 허용)
POST /api/v1/{resources}/{id}/publish    # 게시
POST /api/v1/{resources}/{id}/cancel     # 취소
POST /api/v1/{resources}/{id}/approve    # 승인

# 중첩 리소스: 2depth까지만
GET /api/v1/users/{userId}/posts      # ✅ 블로그
GET /api/v1/teams/{teamId}/members    # ✅ 팀 관리
GET /api/v1/projects/{id}/tasks/{taskId}/comments  # ❌ 너무 깊음
```

### 6-2. HTTP 상태 코드 기준

| 상황 | 코드 |
|---|---|
| 조회 성공 | 200 |
| 생성 성공 | 201 |
| 처리 성공 (응답 없음) | 204 |
| 잘못된 요청 (입력 오류) | 400 |
| 인증 없음 | 401 |
| 권한 없음 | 403 |
| 리소스 없음 | 404 |
| 비즈니스 규칙 충돌 | 409 |
| 서버 에러 | 500 |

---

## 7. 문서화 기준 (Swagger / OpenAPI)

모든 API 엔드포인트에 다음을 반드시 포함합니다:

```java
// Spring Boot 예시
@Operation(summary = "주문 생성", description = "인증된 사용자가 새 주문을 생성합니다.")
@ApiResponses({
    @ApiResponse(responseCode = "201", description = "주문 생성 성공"),
    @ApiResponse(responseCode = "409", description = "재고 부족"),
    @ApiResponse(responseCode = "401", description = "인증 필요")
})
```

주석 작성 기준:
- **클래스 레벨**: 이 클래스의 책임과 사용 방법
- **메서드 레벨**: 복잡한 비즈니스 로직이 있는 경우에만 (자명한 코드에 주석 불필요)
- **인라인**: 코드만으로 의도 파악이 어려운 부분 (예: 매직 넘버, 알고리즘)

```java
// ❌ 불필요한 주석
// 사용자 ID로 주문 목록을 조회한다
List<Order> orders = orderRepository.findByUserId(userId);

// ✅ 의미 있는 주석
// Haversine 공식: 구면 위 두 점의 대원 거리 계산 (단위: 미터)
// 참고: https://en.wikipedia.org/wiki/Haversine_formula
double distance = 2 * R * Math.asin(Math.sqrt(a));
```

---

## 8. 테스트 작성 기준

### 8-1. 테스트 범위 우선순위

```
1순위: 서비스 레이어 단위 테스트 (비즈니스 로직 핵심)
2순위: 통합 테스트 (API 엔드포인트 E2E)
3순위: 레포지토리 테스트 (복잡한 쿼리)
```

### 8-2. 테스트 명명 규칙

```java
// [테스트_대상]_[조건]_[기대_결과]
@Test
void createOrder_whenStockIsZero_throwsOutOfStockException() { ... }

@Test
void calculateDistance_givenSameCoordinates_returnsZero() { ... }
```

### 8-3. 테스트 구조 (AAA 패턴)

```java
@Test
void createOrder_success() {
    // Arrange (준비)
    var request = new CreateOrderRequest(productId, 1);
    given(productRepository.findById(productId)).willReturn(Optional.of(product));

    // Act (실행)
    var result = orderService.createOrder(request, user);

    // Assert (검증)
    assertThat(result.getStatus()).isEqualTo(OrderStatus.PENDING);
    verify(orderRepository).save(any(Order.class));
}
```

---

## 9. 시크릿 및 환경변수 보안 규칙

> **이 섹션의 규칙은 협상 불가입니다. 단 하나라도 위반하면 코드를 작성하지 않고 경고를 먼저 출력합니다.**

### 9-1. 절대 금지 사항 (코드에 직접 작성 금지)

```java
// ❌ 절대 금지 — 하드코딩된 시크릿
String apiKey = "sk-abc123xyz";
String dbPassword = "mypassword123";
String jwtSecret = "my-secret-key";
String awsAccessKey = "AKIAIOSFODNN7EXAMPLE";

// ✅ 반드시 환경변수로
String apiKey = System.getenv("OPENAI_API_KEY");
// 또는 Spring의 경우
@Value("${openai.api.key}")
private String apiKey;
```

금지 항목 목록:
- API 키 (OpenAI, Google, Kakao, Naver, AWS 등 모든 외부 서비스)
- DB 접속 정보 (URL, username, password)
- JWT 시크릿 키
- OAuth Client ID / Secret
- AWS Access Key / Secret Key
- 암호화 키 / 솔트 값
- Webhook URL (내부망 노출 가능)
- 서드파티 서비스 토큰 (Slack, Discord, Firebase 등)

### 9-2. .env 파일 관리 규칙

```bash
# .gitignore에 반드시 포함 (프로젝트 생성 즉시)
.env
.env.local
.env.development
.env.staging
.env.production
*.env

# ✅ 대신 .env.example 파일을 커밋 (실제 값 없이 키 이름만)
# .env.example
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
OPENAI_API_KEY=sk-your-api-key-here
JWT_SECRET=your-jwt-secret-here
REDIS_URL=redis://localhost:6379
```

AI가 새 프로젝트를 시작할 때 **첫 번째로** `.gitignore`에 `.env`를 추가하고 `.env.example`을 생성합니다.

### 9-3. 스택별 환경변수 로딩 패턴

**Spring Boot:**
```yaml
# application.yml — 실제 값 절대 작성 금지
spring:
  datasource:
    url: ${DATABASE_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}

openai:
  api:
    key: ${OPENAI_API_KEY}
```

**Node.js / NestJS:**
```typescript
// config/configuration.ts
export default () => ({
  database: {
    url: process.env.DATABASE_URL,
    // 필수 환경변수 누락 시 시작 시점에 즉시 오류 발생시키기
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN ?? '1h',
  },
});

// 필수 환경변수 검증 (앱 시작 시)
@Injectable()
export class ConfigValidationService implements OnModuleInit {
  onModuleInit() {
    const required = ['DATABASE_URL', 'JWT_SECRET', 'OPENAI_API_KEY'];
    const missing = required.filter(key => !process.env[key]);
    if (missing.length > 0) {
      throw new Error(`필수 환경변수 누락: ${missing.join(', ')}`);
    }
  }
}
```

**Python / FastAPI:**
```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str           # 누락 시 시작 즉시 ValidationError
    openai_api_key: str
    jwt_secret: str
    redis_url: str = "redis://localhost:6379"  # 기본값 있는 경우

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()  # 앱 시작 시 검증
```

### 9-4. Git 커밋 전 시크릿 유출 방지

**커밋 전 반드시 확인:**
```bash
# git diff로 민감 정보 포함 여부 확인
git diff --staged

# 이미 추적 중인 .env 파일 제거
git rm --cached .env
git rm --cached .env.local
```

**AI가 코드를 생성할 때 시크릿이 포함된 파일 감지 시:**
> "⚠️ 이 파일(.env, credentials.json 등)에는 민감 정보가 포함될 수 있습니다.  
> 내용을 출력하거나 코드에 값을 직접 삽입하지 않겠습니다.  
> 환경변수 키 이름만 참조합니다."

**추천 도구 (선택):**
- `git-secrets` — AWS 자격증명 패턴 자동 차단
- `gitleaks` — 커밋 전 시크릿 스캔
- GitHub의 Secret Scanning — 푸시 후 자동 감지 (GitHub 기본 제공)

### 9-5. CI/CD 환경에서 시크릿 관리

```yaml
# GitHub Actions — Secrets 사용 (절대 값 직접 작성 금지)
jobs:
  deploy:
    steps:
      - name: Deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}      # ✅
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # ✅
          # DATABASE_URL: "postgresql://..."              # ❌ 절대 금지
```

환경별 시크릿 저장소:
| 환경 | 권장 저장소 |
|---|---|
| 로컬 개발 | `.env` 파일 (gitignore) |
| CI/CD | GitHub Actions Secrets / GitLab CI Variables |
| 스테이징/프로덕션 | AWS Secrets Manager / GCP Secret Manager / Vault |
| 컨테이너 | K8s Secret (base64) 또는 외부 시크릿 오퍼레이터 |

### 9-6. 이미 유출된 경우 대응 절차

AI는 사용자가 이미 시크릿이 커밋된 상황을 설명하면 다음 순서를 안내합니다:

```
1. 즉시 해당 시크릿 무효화/재발급 (가장 먼저)
   - API 키: 서비스 콘솔에서 즉시 삭제 후 재발급
   - DB 비밀번호: 즉시 변경
   - JWT 시크릿: 변경 후 모든 기존 토큰 무효화

2. Git 히스토리에서 제거 (무효화 후 진행)
   - git filter-branch 또는 BFG Repo-Cleaner 사용
   - 강제 푸시 필요 (팀원에게 사전 고지)

3. .gitignore 업데이트

4. 같은 실수 재발 방지 도구 설치
```

> ⚠️ Git 히스토리 제거는 이미 공개된 정보를 완전히 삭제하지 못합니다.  
> **시크릿 무효화가 반드시 먼저**입니다.

---

## 10. 백엔드 코드 리뷰 체크리스트

AI가 코드 작성 완료 후 스스로 점검합니다:

```
[ ] 모든 API 엔드포인트에 인증/인가가 설정됐는가?
[ ] 입력값 검증이 Controller/DTO 레이어에서 이뤄지는가?
[ ] 응답 형식이 프로젝트 표준과 일치하는가?
[ ] N+1 쿼리가 발생할 수 있는 코드가 없는가?
[ ] 예외가 빈 catch 블록으로 삼켜지지 않는가?
[ ] 코드 어디에도 API 키·비밀번호·토큰이 하드코딩되지 않았는가?
[ ] 민감 정보가 로그에 출력되지 않는가?
[ ] .env 파일이 .gitignore에 포함됐는가?
[ ] .env.example 파일이 키 이름만으로 작성됐는가?
[ ] 트랜잭션 경계가 올바르게 설정됐는가?
[ ] 동시성 문제가 예상되는 로직에 락이 적용됐는가?
[ ] Swagger/OpenAPI 문서가 업데이트됐는가?
```
