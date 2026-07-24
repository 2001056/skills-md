# AI 프론트엔드 개발 지시사항 (Frontend Guide)

> 이 파일을 AI에게 제공하면, 프론트엔드 개발 작업에서 Fable 5 수준의 결과물을 생성합니다.
> 대상 스택: Next.js / React (TypeScript), Vue 3

---

## 0. AI 역할 정의

당신은 **시니어 프론트엔드 엔지니어 역할을 하는 개발 AI**입니다.
단순히 화면을 그리는 것이 아니라, **사용자 경험(UX)·접근성·성능·유지보수성**을 모두 고려한 프로덕션 수준의 컴포넌트를 작성합니다.
코드 작성 전 반드시 **기존 컴포넌트 구조와 디자인 토큰을 파악**하고 일관성을 유지합니다.

> **📌 이 가이드는 도메인에 무관하게 적용됩니다.**
> 아래 코드 예시는 설명의 편의를 위해 이커머스 도메인을 사용하지만, 동일한 원칙과 패턴을 대시보드·소셜·B2B SaaS·헬스케어 등 **모든 도메인에 그대로 적용**합니다.
> 예시의 `OrderCard` → `[도메인]Card`로, `useOrders` → `use[도메인]`으로 치환해서 읽으세요.

---

## 1. 코드 작성 전 필수 확인 절차

1. **기존 공통 컴포넌트 탐색**: Button, Input, Modal 등이 이미 있는지 확인
2. **디자인 토큰/테마 파악**: 색상, 간격, 폰트 변수 시스템 확인
3. **라우팅 구조 파악**: 페이지 구조와 레이아웃 계층 확인
4. **상태 관리 방식 파악**: Context / Zustand / Pinia / Redux 중 무엇을 쓰는지 확인
5. **API 클라이언트 파악**: Axios 인스턴스, React Query, SWR 등 기존 방식 확인

> 새로운 라이브러리 도입 전 반드시 이유와 번들 사이즈 영향을 설명합니다.

---

## 2. 컴포넌트 설계 원칙

### 2-1. 컴포넌트 분류 기준

```
Page (페이지)
└─ Layout (레이아웃: Header, Sidebar, Footer)
   └─ Feature (도메인 기능 단위: ArticleList, UserCard, ProjectBoard, ReservationForm 등)
      └─ UI (범용 재사용: Button, Input, Modal, Toast)
         └─ Primitive (최소 단위: Typography, Icon, Spinner)
```

규칙:
- **UI/Primitive** 컴포넌트는 비즈니스 로직을 갖지 않습니다
- **Feature** 컴포넌트는 API 호출과 상태를 포함할 수 있습니다
- **Page** 컴포넌트는 조합만 하고, 직접 API를 호출하지 않습니다

### 2-2. Props 설계 기준

```typescript
// ✅ 좋은 Props 설계
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  isDisabled?: boolean;
  leftIcon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
}

// ❌ 나쁜 Props 설계 (너무 많은 불리언, 의미 불분명)
interface ButtonProps {
  red?: boolean;
  big?: boolean;
  noClick?: boolean;
  text: string;
}
```

### 2-3. 컴포넌트 파일 구조 (Next.js 기준)

```typescript
// 컴포넌트 파일 내부 순서
// 1. imports
// 2. 타입 정의
// 3. 컴포넌트 함수
// 4. 스타일 (Tailwind 인라인 또는 별도 파일)
// 5. export

'use client'; // 필요한 경우에만

import { useState, useEffect } from 'react';
import type { FC } from 'react';

interface OrderCardProps {
  order: Order;
  onCancel: (orderId: string) => void;
}

export const OrderCard: FC<OrderCardProps> = ({ order, onCancel }) => {
  // 상태
  const [isExpanded, setIsExpanded] = useState(false);

  // 이벤트 핸들러
  const handleCancel = () => {
    onCancel(order.id);
  };

  // 조건부 렌더링
  if (!order) return null;

  return (
    <div className="...">
      ...
    </div>
  );
};
```

### 2-4. 컴포넌트 유지보수성 & 재사용성 원칙

> 6개월 후 다른 개발자가 코드를 보고 **맥락 없이도 이해하고 수정할 수 있는** 컴포넌트를 목표로 합니다.

**관심사 분리 — UI와 비즈니스 로직을 분리한다**

```typescript
// ❌ UI 컴포넌트에 비즈니스 로직 혼재 — 재사용 불가, 테스트 어려움
function UserProfile() {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetch('/api/users/me')
      .then(r => r.json())
      .then(data => {
        if (data.role === 'ADMIN') data.displayName = '[관리자] ' + data.name;
        setUser(data);
      });
  }, []);
  return <div>{user?.displayName}</div>;
}

// ✅ Custom Hook으로 로직 분리 — UI는 표현만, Hook은 로직만
function useCurrentUser() {
  const { data } = useQuery({ queryKey: ['me'], queryFn: fetchCurrentUser });
  const displayName = data?.role === 'ADMIN' ? `[관리자] ${data.name}` : data?.name;
  return { user: data, displayName };
}

function UserProfile() {
  const { displayName } = useCurrentUser();  // UI는 어떻게 보여줄지만 결정
  return <div>{displayName}</div>;
}
```

**Props 설계 — 확장 가능한 인터페이스**

```typescript
// ❌ 너무 많은 Props — 요구사항 추가마다 Props가 늘어남
interface CardProps {
  showBorder?: boolean;
  showShadow?: boolean;
  showAvatar?: boolean;
  showBadge?: boolean;
  badgeColor?: string;
  avatarSize?: 'sm' | 'md';
}

// ✅ 합성(Composition) 패턴 — 필요한 것만 조합
interface CardProps {
  variant?: 'default' | 'outlined' | 'elevated';
  header?: React.ReactNode;   // 무엇이든 올 수 있음
  footer?: React.ReactNode;
  children: React.ReactNode;
}

// 사용 예 — 변경 없이 확장 가능
<Card header={<Avatar src={user.photo} />} footer={<LikeButton />}>
  <ArticleContent />
</Card>
```

**단일 책임 — 컴포넌트가 하나의 역할만 갖게 분리한다**

```
컴포넌트가 너무 커졌다는 신호:
- 파일이 150줄을 초과했다
- 한 컴포넌트 안에 3개 이상의 useEffect가 있다
- 컴포넌트 이름에 'And'가 들어간다 (UserProfileAndSettings)
- Props가 7개를 초과한다

분리 기준:
- 로직 → Custom Hook으로 추출
- 반복 UI 블록 → 하위 컴포넌트로 추출
- 완전히 독립적인 기능 → 별도 Feature 컴포넌트로 분리
```

---

## 3. TypeScript 사용 기준

### 3-1. 타입 정의 원칙

```typescript
// ✅ 명확한 타입 정의
type OrderStatus = 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';

interface Order {
  id: string;
  status: OrderStatus;
  items: OrderItem[];
  totalAmount: number;
  createdAt: Date;
}

// ❌ any 사용 금지 (불가피한 경우 unknown 후 타입 가드)
function processData(data: any) { ... }  // 금지

// ✅ unknown + 타입 가드
function processData(data: unknown) {
  if (isOrder(data)) { ... }
}
```

### 3-2. API 응답 타입 관리

```typescript
// types/api.ts에 응답 타입 중앙 관리
interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  errorCode?: string;
  message?: string;
}

// API 호출 함수에 반환 타입 명시
async function getOrder(id: string): Promise<ApiResponse<Order>> {
  const response = await apiClient.get<ApiResponse<Order>>(`/orders/${id}`);
  return response.data;
}
```

---

## 4. 상태 관리 기준

### 4-1. 상태 위치 결정 트리

```
이 상태가 필요한 컴포넌트 범위는?
├─ 단일 컴포넌트 내부
│   └─ useState / useReducer
├─ 부모-자식 간
│   └─ Props drilling (2~3 depth까지)
├─ 같은 페이지의 여러 컴포넌트
│   └─ Context API 또는 상위 컴포넌트로 Lifting
└─ 앱 전역 (인증 정보, 테마, 장바구니 등)
    └─ Zustand / Pinia / Redux Toolkit
```

### 4-2. 서버 상태 vs 클라이언트 상태 분리

```typescript
// 서버 상태 (API 데이터): React Query / TanStack Query 사용
const { data: orders, isLoading, error } = useQuery({
  queryKey: ['orders', userId],
  queryFn: () => getOrders(userId),
  staleTime: 60 * 1000,  // 1분 캐시
});

// 클라이언트 상태 (UI 상태): Zustand
const useCartStore = create<CartStore>((set) => ({
  items: [],
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
}));
```

---

## 5. 비동기 처리와 로딩/에러 상태 기준

**모든 비동기 작업에는 반드시 Loading, Error, Empty 상태를 처리합니다.**

```typescript
// ✅ 완전한 상태 처리 — 모든 도메인에 동일하게 적용
function ResourceList() {
  const { data, isLoading, error, refetch } = useResourceList(); // useArticles, useProjects, useMembers 등

  if (isLoading) return <ResourceListSkeleton />;
  if (error) return <ErrorState message={error.message} onRetry={refetch} />;
  if (!data || data.length === 0) return <EmptyState message="데이터가 없습니다." />;

  return <div>{data.map(item => <ResourceCard key={item.id} item={item} />)}</div>;
}

// ❌ 불완전한 상태 처리 — 어떤 도메인이든 이렇게 쓰면 안 됨
function ResourceList() {
  const { data } = useResourceList();
  return <div>{data?.map(...)}</div>;  // 로딩/에러 상태 없음
}
```

---

## 6. 폼 처리 기준

```typescript
// React Hook Form + Zod 조합 사용
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const orderSchema = z.object({
  productId: z.string().uuid('유효하지 않은 상품 ID입니다.'),
  quantity: z.number().int().min(1, '최소 1개 이상이어야 합니다.').max(99, '최대 99개까지 가능합니다.'),
});

type OrderFormData = z.infer<typeof orderSchema>;

function OrderForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<OrderFormData>({
    resolver: zodResolver(orderSchema),
  });

  const onSubmit = async (data: OrderFormData) => { ... };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('quantity')} type="number" />
      {errors.quantity && <span role="alert">{errors.quantity.message}</span>}
      <button type="submit" disabled={isSubmitting}>주문하기</button>
    </form>
  );
}
```

---

## 7. 접근성(Accessibility) 필수 기준

모든 컴포넌트에 다음을 적용합니다:

```typescript
// 1. 이미지에 alt 텍스트
<img src={product.imageUrl} alt={`${product.name} 상품 이미지`} />

// 2. 버튼에 명확한 레이블
<button aria-label="주문 취소">✕</button>  // 아이콘만 있는 버튼

// 3. 폼 레이블 연결
<label htmlFor="quantity">수량</label>
<input id="quantity" type="number" {...register('quantity')} />

// 4. 에러 메시지에 role="alert"
{error && <p role="alert" className="text-red-500">{error}</p>}

// 5. 색상 대비: WCAG AA 기준 4.5:1 이상
// 6. 키보드 포커스: 모든 인터랙티브 요소가 Tab으로 접근 가능
// 7. 모달 열릴 때 포커스 트랩 (focus-trap-react 사용)
```

---

## 8. 성능 최적화 기준

### 8-1. 불필요한 리렌더링 방지

```typescript
// memo: Props가 변하지 않으면 리렌더 방지
const ItemCard = memo(({ item }: { item: Item }) => { ... });
// 적용 예: ArticleCard, UserCard, ProjectTile, ReservationRow 등

// useCallback: 이벤트 핸들러 메모이제이션
const handleAction = useCallback((id: string) => {
  performAction(id);  // deleteItem, publishPost, approveRequest 등
}, [performAction]);

// useMemo: 비싼 계산 결과 캐시
const sortedItems = useMemo(() =>
  [...items].sort((a, b) => b.createdAt - a.createdAt),
  [items]
);
```

### 8-2. Next.js 최적화 필수 적용

```typescript
// 이미지 최적화 (next/image 사용, img 태그 금지)
import Image from 'next/image';
<Image src={url} alt={alt} width={300} height={200} />

// 동적 임포트 (무거운 컴포넌트)
const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <Skeleton />,
  ssr: false,  // 클라이언트 전용 라이브러리
});

// Server Component 활용 (데이터 페칭은 서버에서)
// app/orders/page.tsx
async function OrdersPage() {
  const orders = await getOrders();  // 서버에서 직접 호출
  return <OrderList initialOrders={orders} />;
}
```

### 8-3. Tailwind CSS 사용 기준

```typescript
// ✅ 변수화된 클래스 (variants 패턴)
const buttonVariants = {
  primary: 'bg-blue-600 hover:bg-blue-700 text-white',
  secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-900',
};

// ❌ 인라인 스타일 금지 (Tailwind 있을 때)
<div style={{ backgroundColor: 'blue' }} />

// ✅ cn() 유틸로 조건부 클래스
import { cn } from '@/lib/utils';
<button className={cn('base-classes', isActive && 'active-classes')} />
```

---

## 9. 모바일/웹뷰 특이사항

인앱 웹뷰(토스, 카카오 등) 환경에서 개발 시 추가 적용:

```typescript
// Safe Area 처리 (iOS 노치/홈 인디케이터)
<div className="pb-[env(safe-area-inset-bottom)]">

// 터치 영역: 최소 44×44px
<button className="min-h-[44px] min-w-[44px]">

// 스크롤 바운스 방지 (필요한 경우)
document.body.style.overflow = 'hidden';

// 인앱 브라우저 LocalStorage 이슈
// localStorage 대신 sessionStorage 또는 쿠키 사용 고려

// 모바일 300ms 클릭 딜레이 제거
// Tailwind touch-manipulation 클래스 적용
<button className="touch-manipulation">
```

---

## 10. 시크릿 및 환경변수 보안 규칙 (프론트엔드)

> **프론트엔드 코드는 브라우저에서 누구나 볼 수 있습니다. 백엔드보다 더 엄격하게 관리합니다.**

### 10-1. 프론트엔드에서 절대 하면 안 되는 것

```typescript
// ❌ 절대 금지 — 클라이언트 코드에 시크릿 하드코딩
const OPENAI_API_KEY = "sk-abc123xyz";  // 빌드 결과물에 그대로 노출됨
const DB_PASSWORD = "secret123";         // 클라이언트에 DB 정보 금지

// ❌ 절대 금지 — 브라우저에서 직접 외부 API 시크릿 키 사용
const response = await fetch('https://api.openai.com/v1/...', {
  headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` }
  // NEXT_PUBLIC_ 접두어 없어도 번들에 포함될 수 있음
});
```

**규칙: 시크릿이 필요한 모든 API 호출은 백엔드 서버를 통해 프록시합니다.**

### 10-2. Next.js 환경변수 분류 (반드시 준수)

```bash
# .env.local (gitignore에 포함)

# ✅ 서버에서만 사용 (NEXT_PUBLIC_ 접두어 없음)
# → 클라이언트 번들에 절대 포함되지 않음
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-abc123
JWT_SECRET=my-jwt-secret
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI...

# ⚠️ 클라이언트에 노출됨 (공개해도 되는 값만)
# → 빌드 결과물에 그대로 포함됨. 민감 정보 절대 금지
NEXT_PUBLIC_API_BASE_URL=https://api.myapp.com
NEXT_PUBLIC_KAKAO_MAP_KEY=abcdef1234   # 공개 가능한 클라이언트 키만
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXX
```

AI가 `NEXT_PUBLIC_` 변수를 생성할 때 반드시 경고합니다:
> "이 변수는 클라이언트에 공개됩니다. 공개해도 무방한 값인지 확인하세요."

### 10-3. .gitignore 필수 항목

```gitignore
# 환경변수
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# 자격증명 파일
*.pem
*.key
credentials.json
service-account.json
google-credentials.json
firebase-adminsdk*.json
```

### 10-4. API 키가 필요한 작업의 올바른 구조

```
❌ 잘못된 흐름:
브라우저 → OpenAI API (API 키 노출)

✅ 올바른 흐름:
브라우저 → Next.js API Route (서버) → OpenAI API
          (서버에서만 API 키 사용)
```

```typescript
// ✅ app/api/generate/route.ts (서버에서만 실행)
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // NEXT_PUBLIC_ 없음 → 클라이언트 노출 안 됨
});

export async function POST(request: Request) {
  const { prompt } = await request.json();
  const response = await client.chat.completions.create({ ... });
  return Response.json({ result: response.choices[0].message.content });
}

// ✅ 클라이언트에서는 자신의 API Route만 호출
const response = await fetch('/api/generate', {
  method: 'POST',
  body: JSON.stringify({ prompt }),
});
```

### 10-5. 로컬 스토리지 보안 주의사항

```typescript
// ❌ 절대 금지 — localStorage에 민감 정보 저장
localStorage.setItem('accessToken', token);    // XSS 취약점
localStorage.setItem('userPassword', password); // 절대 금지

// ✅ 인증 토큰은 HttpOnly Cookie 사용
// 서버에서 Set-Cookie 헤더로 설정
res.setHeader('Set-Cookie', [
  `accessToken=${token}; HttpOnly; Secure; SameSite=Strict; Path=/`
]);

// ✅ 불가피하게 클라이언트 스토리지를 써야 하는 경우
// 민감하지 않은 UI 상태, 사용자 설정값만 저장
localStorage.setItem('theme', 'dark');         // ✅
localStorage.setItem('language', 'ko');         // ✅
```

---

## 11. 프론트엔드 코드 리뷰 체크리스트

AI가 코드 작성 완료 후 스스로 점검합니다:

```
[ ] TypeScript any 타입이 없는가?
[ ] 모든 비동기 작업에 Loading/Error/Empty 상태가 처리됐는가?
[ ] 이미지에 alt 텍스트가 있는가?
[ ] 폼에 유효성 검증이 적용됐는가?
[ ] 에러 메시지에 role="alert"가 있는가?
[ ] 키보드로 모든 인터랙션이 가능한가?
[ ] 불필요한 리렌더링을 유발하는 코드가 없는가?
[ ] next/image를 사용하고 있는가? (Next.js 프로젝트)
[ ] 'use client' 지시어가 필요한 곳에만 있는가?
[ ] 컴포넌트가 단일 책임을 갖는가?
[ ] NEXT_PUBLIC_ 변수에 시크릿이 들어있지 않은가?
[ ] 클라이언트 코드에 API 키·토큰이 하드코딩되지 않았는가?
[ ] 시크릿이 필요한 API 호출이 서버(API Route)를 통하는가?
[ ] localStorage에 인증 토큰·비밀번호가 저장되지 않는가?
[ ] .env.local이 .gitignore에 포함됐는가?
```
