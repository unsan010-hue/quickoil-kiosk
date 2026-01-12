# QuickOil 오일 선택 페이지 (OilSelectPage)

## 목표

Tailwind UI pricing 컴포넌트 스타일을 기반으로 한 엔진오일 등급 선택 페이지.
**업셀(Upsell) 극대화**가 핵심 - 고객이 자연스럽게 상위 등급을 선택하도록 유도.

---

## 기술 스택

```
React 18 + TypeScript
Tailwind CSS (Tailwind UI 스타일)
```

---

## 레이아웃 참고

Tailwind UI pricing 섹션 구조를 따름:
- 5개 카드 가로 배열 (lg:grid-cols-5)
- `data-featured` 속성으로 추천 카드 강조
- `group/tier` 패턴으로 카드별 조건부 스타일링
- 체크 아이콘 리스트로 무료 서비스 표시

---

## 제품 데이터

```typescript
interface OilProduct {
  id: string;
  name: string;
  brand: 'kixx' | 'total' | 'ristar';
  description: string;
}

interface OilTier {
  id: string;
  name: string;
  price: number;
  oilType: string;
  tagline: string;
  badge?: {
    text: string;
    type: 'recommended' | 'popular' | 'premium';
  };
  products: OilProduct[];
  freeServices: string[];
}

const oilTiers: OilTier[] = [
  {
    id: 'economy',
    name: '이코노미',
    price: 50000,
    oilType: '합성유',
    tagline: '경제적인 선택, 일반 주행에 적합',
    products: [
      { id: 'dx5', name: 'Kixx DX5', brand: 'kixx', description: 'GS칼텍스 합성유' },
      { id: 'gx5', name: 'Kixx GX5', brand: 'kixx', description: 'GS칼텍스 합성유' },
    ],
    freeServices: ['washer'],
  },
  {
    id: 'standard',
    name: '스탠다드',
    price: 70000,
    oilType: '고급 합성유',
    tagline: '균형 잡힌 성능과 보호',
    products: [
      { id: 'gx7', name: 'Kixx GX7', brand: 'kixx', description: 'GS칼텍스 고급 합성유' },
      { id: 'quartz9000', name: '토탈쿼츠 9000', brand: 'total', description: '프랑스 토탈 프리미엄' },
    ],
    freeServices: ['washer', 'tire'],
  },
  {
    id: 'premium',
    name: '프리미엄',
    price: 90000,
    oilType: 'PAO 합성유',
    tagline: '고급 합성유, 향상된 엔진 보호와 연비',
    badge: { text: '추천', type: 'recommended' },
    products: [
      { id: 'pao', name: 'Kixx PAO', brand: 'kixx', description: 'PAO 기반 최고급 합성유' },
    ],
    freeServices: ['washer', 'tire', 'aircon'],
  },
  {
    id: 'hyperformance',
    name: '하이퍼포먼스',
    price: 120000,
    oilType: '에스터 합성유',
    tagline: '최고급 전합성유, 고출력 엔진에 최적화',
    badge: { text: '인기', type: 'popular' },
    products: [
      { id: 'supernormal', name: '리스타 슈퍼노멀', brand: 'ristar', description: '에스터 기반 고성능' },
    ],
    freeServices: ['washer', 'tire', 'aircon', 'interior'],
  },
  {
    id: 'racing',
    name: '레이싱',
    price: 150000,
    oilType: '최고급 에스터',
    tagline: '극한 성능, 스포츠카 및 튜닝카 전용',
    badge: { text: '최고급', type: 'premium' },
    products: [
      { id: 'metallocene', name: '리스타 메탈로센', brand: 'ristar', description: '메탈로센 최고급' },
    ],
    freeServices: ['washer', 'tire', 'aircon', 'interior', 'engine'],
  },
];

const freeServices = [
  { id: 'washer', name: '워셔액 보충' },
  { id: 'tire', name: '타이어 공기압 체크' },
  { id: 'aircon', name: '에어컨 필터 점검' },
  { id: 'interior', name: '실내 간단 청소' },
  { id: 'engine', name: '엔진룸 클리닝' },
];
```

---

## UI 구조

### 전체 레이아웃

```
┌─────────────────────────────────────────────────────────────────┐
│  Header: 진행 단계 표시 (1.차종선택 → 2.엔진오일 → 3.추가서비스 → 4.견적서)  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  차량 정보 요약: 브랜드 기아 | 차종 K5 | 연료 휘발유              │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│                    엔진오일 선택                                 │
│            차량에 맞는 엔진오일을 선택해주세요                     │
│                                                                 │
│  ┌─────┐ ┌─────┐ ┌─────────┐ ┌─────┐ ┌─────┐                   │
│  │이코 │ │스탠 │ │ 프리미엄 │ │하이퍼│ │레이싱│  ← 5개 카드       │
│  │노미 │ │다드 │ │  ⭐추천  │ │포먼스│ │     │                   │
│  │     │ │     │ │(강조됨) │ │     │ │     │                   │
│  └─────┘ └─────┘ └─────────┘ └─────┘ └─────┘                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Footer: 선택한 오일 요약 + [다음 단계 →] 버튼                    │
└─────────────────────────────────────────────────────────────────┘
```

### 카드 구조 (Tailwind UI pricing 스타일)

```html
<!-- 추천 카드 (data-featured) -->
<div 
  data-featured="true" 
  class="group/tier rounded-3xl p-8 ring-1 ring-gray-200 
         data-[featured]:ring-2 data-[featured]:ring-orange-500"
>
  <!-- 헤더: 등급명 + 뱃지 -->
  <div class="flex items-center justify-between gap-x-4">
    <h3 class="text-lg font-semibold">프리미엄</h3>
    <span class="rounded-full bg-orange-500 px-2.5 py-1 text-xs font-semibold text-white">
      추천
    </span>
  </div>
  
  <!-- 설명 -->
  <p class="mt-4 text-sm text-gray-600">고급 합성유, 향상된 엔진 보호와 연비</p>
  
  <!-- 제품명 + ⓘ 버튼 (제품 2개 이상일 때) -->
  <div class="mt-4 flex items-center justify-between">
    <div>
      <p class="font-medium">Kixx PAO</p>
      <p class="text-sm text-gray-500">PAO 합성유</p>
    </div>
    <!-- 제품 2개 이상일 때만 표시 -->
    <button class="text-gray-400 hover:text-gray-600">ⓘ</button>
  </div>
  
  <!-- 가격 -->
  <p class="mt-6 flex items-baseline gap-x-1">
    <span class="text-4xl font-semibold tracking-tight text-orange-500">90,000</span>
    <span class="text-sm font-semibold text-gray-600">원</span>
  </p>
  
  <!-- 선택 버튼 -->
  <button class="mt-6 block w-full rounded-md bg-orange-500 px-3 py-2 
                 text-center text-sm font-semibold text-white 
                 hover:bg-orange-400">
    선택하기
  </button>
  
  <!-- 무료 서비스 체크리스트 -->
  <ul class="mt-8 space-y-3 text-sm text-gray-600">
    <li class="flex gap-x-3">
      <svg class="h-6 w-5 text-green-500">✓</svg>
      워셔액 보충
    </li>
    <li class="flex gap-x-3">
      <svg class="h-6 w-5 text-green-500">✓</svg>
      타이어 공기압 체크
    </li>
    <li class="flex gap-x-3">
      <svg class="h-6 w-5 text-green-500">✓</svg>
      에어컨 필터 점검
    </li>
  </ul>
</div>
```

---

## 스타일 가이드

### 컬러

```css
/* 메인 액센트 - 오렌지 (Tailwind orange) */
--accent: theme('colors.orange.500');        /* #f97316 */
--accent-light: theme('colors.orange.50');   /* #fff7ed */
--accent-dark: theme('colors.orange.600');   /* #ea580c */

/* 체크 아이콘 - 그린 */
--check: theme('colors.green.500');          /* #22c55e */

/* 뱃지 컬러 */
--badge-recommended: theme('colors.orange.500');  /* 추천 */
--badge-popular: theme('colors.red.500');         /* 인기 */  
--badge-premium: theme('colors.gray.900');        /* 최고급 */
```

### 카드 상태

```css
/* 기본 카드 */
.card-default {
  @apply rounded-3xl p-6 ring-1 ring-gray-200 bg-white;
}

/* 추천 카드 (data-featured) */
.card-featured {
  @apply ring-2 ring-orange-500;
}

/* 선택된 카드 */
.card-selected {
  @apply ring-2 ring-orange-500 bg-orange-50;
}

/* 호버 */
.card-hover {
  @apply hover:ring-orange-300 transition-all;
}
```

### 뱃지 스타일

```html
<!-- 추천 (오렌지) -->
<span class="rounded-full bg-orange-500 px-2.5 py-1 text-xs font-semibold text-white">
  추천
</span>

<!-- 인기 (레드) -->
<span class="rounded-full bg-red-500 px-2.5 py-1 text-xs font-semibold text-white">
  🔥 인기
</span>

<!-- 최고급 (블랙) -->
<span class="rounded-full bg-gray-900 px-2.5 py-1 text-xs font-semibold text-white">
  💎 최고급
</span>
```

---

## 컴포넌트 분리

```
src/
├── components/
│   └── oil/
│       ├── OilSelectPage.tsx       # 페이지 전체
│       ├── OilCard.tsx             # 개별 카드
│       ├── OilCardList.tsx         # 카드 5개 그리드
│       ├── ServiceChecklist.tsx    # 무료 서비스 체크 목록
│       ├── ProductInfoModal.tsx    # ⓘ 클릭 시 제품 선택 모달
│       └── SelectionSummary.tsx    # 하단 선택 요약 바
```

---

## OilCard 컴포넌트 Props

```typescript
interface OilCardProps {
  tier: OilTier;
  isSelected: boolean;
  onSelect: (tierId: string) => void;
  onProductInfo: (tierId: string) => void;  // ⓘ 버튼 클릭
}
```

---

## 업셀 포인트 (중요!)

### 1. 추천 카드 강조
- `프리미엄` 카드에 `data-featured="true"` 적용
- 오렌지 테두리 + 뱃지로 시선 집중
- 카드 순서 중앙에 배치

### 2. 무료 서비스 시각적 차이
- 체크(✓) 개수가 등급별로 확연히 다르게 보여야 함
- 이코노미: 1개 → 레이싱: 5개
- 그린 체크 아이콘으로 "혜택" 느낌

### 3. 가격 강조
- 가격은 오렌지 컬러로 강조
- "원" 단위는 작게

### 4. 카드 높이 통일
- 모든 카드 높이 동일 (가장 긴 카드 기준)
- 서비스 적은 카드는 여백으로 채움

---

## 반응형 (iPad 가로모드 기준)

```css
/* 기본: 5개 가로 배열 */
.grid-cols-5

/* 카드 최소 너비 확보 */
min-width: 200px per card

/* iPad 가로 1180px 기준 */
카드 너비: 약 220px each
간격: 16px (gap-4)
외곽 패딩: 48px
```

---

## 인터랙션

### 카드 선택
1. 카드 클릭 → 해당 카드 `selected` 상태
2. 하단 요약 바에 선택 정보 표시
3. "다음 단계" 버튼 활성화

### ⓘ 버튼 (제품 2개 이상인 경우)
1. 버튼 클릭 → 모달 열림
2. 같은 등급 내 다른 제품 선택 가능
3. "동일 가격입니다" 안내 문구

### 선택 버튼 상태
```html
<!-- 미선택 -->
<button class="bg-white text-orange-500 ring-1 ring-orange-200 hover:ring-orange-300">
  선택하기
</button>

<!-- 선택됨 -->
<button class="bg-orange-500 text-white">
  ✓ 선택됨
</button>
```

---

## 하단 요약 바

```html
<div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
  <div class="max-w-7xl mx-auto flex items-center justify-between">
    <!-- 선택 정보 -->
    <div class="flex items-center gap-2">
      <span class="text-green-500">✓</span>
      <span class="font-medium">프리미엄</span>
      <span class="text-gray-500">·</span>
      <span>Kixx PAO</span>
      <span class="text-orange-500 font-semibold ml-4">90,000원</span>
    </div>
    
    <!-- 다음 버튼 -->
    <button class="bg-orange-500 text-white px-8 py-3 rounded-full font-semibold">
      다음 단계 →
    </button>
  </div>
</div>
```

---

## 체크 아이콘 SVG

```html
<svg 
  viewBox="0 0 20 20" 
  fill="currentColor" 
  class="h-6 w-5 flex-none text-green-500"
>
  <path 
    fill-rule="evenodd" 
    d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z" 
    clip-rule="evenodd" 
  />
</svg>
```

---

## 구현 순서

1. **OilCard.tsx** - 단일 카드 컴포넌트 (Tailwind UI 스타일)
2. **ServiceChecklist.tsx** - 체크 목록 컴포넌트
3. **OilCardList.tsx** - 5개 카드 그리드
4. **SelectionSummary.tsx** - 하단 요약 바
5. **ProductInfoModal.tsx** - 제품 선택 모달
6. **OilSelectPage.tsx** - 페이지 조합

---

## 주의사항

- Tailwind UI pricing 컴포넌트 패턴 따르기 (`group/tier`, `data-featured`)
- 다크모드 불필요 (iPad 키오스크 전용)
- 모바일 반응형 불필요 (iPad 가로모드 고정)
- 애니메이션은 간결하게 (터치 피드백 정도)