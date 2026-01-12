# QuickOil iPad 메뉴판 UI/UX 가이드라인

## 1. 디자인 원칙

### 핵심 콘셉트
- **Apple 스타일 미니멀리즘**: 불필요한 요소 배제, 여백 활용
- **고연령 친화적**: 40-60대 고객이 주 사용자, 직관적이고 큰 터치 영역
- **신뢰감 있는 프리미엄**: 자동차 서비스업의 전문성 표현

### 디자인 키워드
```
Simple / Clean / Premium / Trustworthy / Accessible
```

---

## 2. 레이아웃

### 디바이스 환경
- **기기**: iPad (10세대 기준, 10.9인치)
- **해상도**: 1640 x 1180 px (가로 모드)
- **방향**: 가로(Landscape) 모드 고정
- **Safe Area**: 좌우 44px, 상하 24px 여백 확보

### 그리드 시스템
```
- 12컬럼 그리드
- 컬럼 간격(Gutter): 24px
- 외곽 마진: 48px
- 콘텐츠 최대 너비: 1544px
```

### 페이지 구조
```
┌─────────────────────────────────────────────────┐
│  Header (60px) - 로고, 현재 단계, 홈 버튼        │
├─────────────────────────────────────────────────┤
│                                                 │
│  Main Content Area                              │
│  (메뉴 선택 / 견적서 / 전화번호 입력 등)          │
│                                                 │
├─────────────────────────────────────────────────┤
│  Footer (80px) - 진행 버튼, 가격 합계            │
└─────────────────────────────────────────────────┘
```

---

## 3. 컬러 시스템

### Primary Colors
```css
--primary-black: #1D1D1F;      /* 메인 텍스트, 강조 버튼 */
--primary-white: #FFFFFF;      /* 배경 */
--primary-gray: #F5F5F7;       /* 섹션 배경, 카드 배경 */
```

### Accent Colors
```css
--accent-blue: #0071E3;        /* CTA 버튼, 링크, 선택 상태 */
--accent-blue-hover: #0077ED;  /* 버튼 호버 */
--accent-green: #34C759;       /* 성공, 완료 상태 */
--accent-orange: #FF9500;      /* 프리미엄/추천 뱃지 */
```

### Text Colors
```css
--text-primary: #1D1D1F;       /* 제목, 가격 */
--text-secondary: #6E6E73;     /* 설명, 부가 정보 */
--text-tertiary: #AEAEB2;      /* 플레이스홀더, 비활성 */
--text-inverse: #FFFFFF;       /* 어두운 배경 위 텍스트 */
```

### Status Colors
```css
--status-error: #FF3B30;       /* 에러, 경고 */
--status-success: #34C759;     /* 성공 */
--status-warning: #FF9500;     /* 주의 */
```

### 브랜드별 컬러 (오일 카테고리 구분용)
```css
--brand-mobil: #FF0000;        /* Mobil 1 - 레드 */
--brand-castrol: #00A650;      /* Castrol - 그린 */
--brand-zic: #003DA5;          /* SK ZIC - 블루 */
--brand-shell: #FBCE07;        /* Shell - 옐로우 */
--brand-total: #E4002B;        /* Total - 레드 */
```

---

## 4. 타이포그래피

### 폰트 패밀리
```css
--font-primary: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
--font-numeric: 'SF Pro Display', 'Pretendard', sans-serif;  /* 가격 표시용 */
```

### 폰트 스케일 (고연령 친화적 - 기본보다 1.2배 큰 사이즈)
```css
/* Display - 메인 페이지 제목 */
--text-display: 48px / 1.2 / Bold (600);

/* Heading 1 - 섹션 제목 */
--text-h1: 36px / 1.3 / Semibold (600);

/* Heading 2 - 카드 제목, 상품명 */
--text-h2: 28px / 1.3 / Semibold (600);

/* Heading 3 - 서브 타이틀 */
--text-h3: 24px / 1.4 / Medium (500);

/* Body Large - 가격, 중요 정보 */
--text-body-lg: 22px / 1.5 / Regular (400);

/* Body - 일반 텍스트 */
--text-body: 20px / 1.5 / Regular (400);

/* Caption - 부가 설명 */
--text-caption: 17px / 1.4 / Regular (400);
```

### 가격 표시 규칙
- 숫자는 SF Pro Display 또는 고정폭 숫자 사용
- 천 단위 콤마 필수: `85,000원`
- 할인가 표시: ~~기존가~~ → **할인가**
- 가격 정렬: 우측 정렬

---

## 5. 컴포넌트 스펙

### 버튼

#### Primary Button (CTA)
```css
height: 64px;
padding: 0 48px;
border-radius: 16px;
background: var(--accent-blue);
color: white;
font-size: 22px;
font-weight: 600;
min-width: 200px;

/* Active/Pressed */
transform: scale(0.98);
background: var(--accent-blue-hover);
```

#### Secondary Button
```css
height: 64px;
padding: 0 48px;
border-radius: 16px;
background: var(--primary-gray);
color: var(--text-primary);
font-size: 22px;
font-weight: 500;
```

#### Ghost Button (텍스트 버튼)
```css
height: 48px;
padding: 0 24px;
background: transparent;
color: var(--accent-blue);
font-size: 20px;
font-weight: 500;
```

### 카드 (오일 상품 카드)

```css
/* 기본 카드 */
width: 100%;
padding: 24px;
border-radius: 20px;
background: white;
box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

/* 선택된 상태 */
border: 3px solid var(--accent-blue);
box-shadow: 0 4px 20px rgba(0, 113, 227, 0.15);
```

#### 카드 내부 구조
```
┌──────────────────────────────────────┐
│  [브랜드 로고]     [추천 뱃지]        │
│                                      │
│  상품명 (H2)                         │
│  상품 설명 (Caption, Secondary)       │
│                                      │
│  ₩85,000              [선택 버튼]    │
└──────────────────────────────────────┘
```

### 입력 필드 (전화번호)

```css
/* 전화번호 입력 - 대형 숫자 키패드 스타일 */
height: 80px;
font-size: 36px;
text-align: center;
letter-spacing: 8px;
border: 2px solid var(--primary-gray);
border-radius: 16px;

/* Focus 상태 */
border-color: var(--accent-blue);
box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
```

### 숫자 키패드

```css
/* 키패드 버튼 */
width: 100px;
height: 100px;
border-radius: 50%;
font-size: 32px;
font-weight: 500;

/* 배치: 3x4 그리드 + 하단 삭제/확인 */
gap: 16px;
```

### 모달/다이얼로그

```css
max-width: 560px;
padding: 40px;
border-radius: 24px;
background: white;
box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);

/* Backdrop */
background: rgba(0, 0, 0, 0.4);
backdrop-filter: blur(8px);
```

---

## 6. 터치 & 인터랙션

### 터치 타겟 (고연령 친화)
```
- 최소 터치 영역: 48 x 48px (권장: 64 x 64px)
- 버튼 간 최소 간격: 16px
- 중요 버튼(CTA): 64px 높이 이상
```

### 터치 피드백
```css
/* 탭 시 시각적 피드백 */
transition: transform 0.1s ease, opacity 0.1s ease;

/* Active 상태 */
transform: scale(0.97);
opacity: 0.9;
```

### 스크롤
- 메뉴 목록: 세로 스크롤 (스크롤바 항상 표시)
- 스크롤 영역 명확히 표시 (상하 그라데이션 힌트)
- 스크롤 속도: 부드럽게 (`scroll-behavior: smooth`)

### 자동 복귀 타이머
```
- 30초 무활동 시 홈 화면으로 자동 복귀
- 마지막 10초: 화면 하단에 카운트다운 토스트 표시
- 터치 시 타이머 리셋
```

---

## 7. 페이지별 UI 스펙

### 7.1 홈 화면 (HomePage)
```
┌─────────────────────────────────────────────────┐
│                                                 │
│            [QuickOil 로고]                      │
│                                                 │
│         "엔진오일 교환 견적 받기"                │
│                                                 │
│         ┌─────────────────────┐                │
│         │                     │                │
│         │    시작하기 버튼     │                │
│         │    (큰 CTA 버튼)    │                │
│         │                     │                │
│         └─────────────────────┘                │
│                                                 │
│         관리자 로그인 (작은 텍스트 링크)          │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 7.2 메뉴 선택 (MenuPage)
```
┌─────────────────────────────────────────────────┐
│  [←]  오일 선택                    [홈]         │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Mobil   │ │ Castrol │ │ ZIC     │  ← 탭     │
│  └─────────┘ └─────────┘ └─────────┘           │
│                                                 │
│  ┌───────────────────────────────────────┐     │
│  │  [로고]              [추천]           │     │
│  │  Mobil 1 0W-40                        │     │
│  │  최고급 풀 합성유                      │     │
│  │  ₩95,000                    [선택]   │     │
│  └───────────────────────────────────────┘     │
│                                                 │
│  ┌───────────────────────────────────────┐     │
│  │  Mobil Super 3000 5W-30               │     │
│  │  합성유                               │     │
│  │  ₩75,000                    [선택]   │     │
│  └───────────────────────────────────────┘     │
│                                                 │
├─────────────────────────────────────────────────┤
│  선택: Mobil 1 0W-40         [견적서 보기 →]   │
└─────────────────────────────────────────────────┘
```

### 7.3 견적서 확인 (QuotePage)
```
┌─────────────────────────────────────────────────┐
│  [←]  견적서 확인                  [홈]         │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────────────────────────────────┐     │
│  │  견적 내역                            │     │
│  │  ─────────────────────────────────    │     │
│  │  Mobil 1 0W-40 (4L)      ₩95,000     │     │
│  │  공임비                   ₩20,000     │     │
│  │  ─────────────────────────────────    │     │
│  │  합계                    ₩115,000     │     │
│  └───────────────────────────────────────┘     │
│                                                 │
│  * 차종에 따라 오일량이 달라질 수 있습니다        │
│                                                 │
├─────────────────────────────────────────────────┤
│  [다시 선택]              [카카오톡으로 받기 →]  │
└─────────────────────────────────────────────────┘
```

### 7.4 전화번호 입력 (PhonePage)
```
┌─────────────────────────────────────────────────┐
│  [←]  전화번호 입력                [홈]         │
├─────────────────────────────────────────────────┤
│                                                 │
│       카카오톡으로 견적서를 보내드립니다          │
│                                                 │
│       ┌─────────────────────────┐              │
│       │    010-1234-5678       │  ← 입력필드   │
│       └─────────────────────────┘              │
│                                                 │
│           ┌─────┬─────┬─────┐                  │
│           │  1  │  2  │  3  │                  │
│           ├─────┼─────┼─────┤                  │
│           │  4  │  5  │  6  │   ← 숫자키패드   │
│           ├─────┼─────┼─────┤                  │
│           │  7  │  8  │  9  │                  │
│           ├─────┼─────┼─────┤                  │
│           │ CLR │  0  │  ⌫  │                  │
│           └─────┴─────┴─────┘                  │
│                                                 │
├─────────────────────────────────────────────────┤
│                           [견적서 발송하기 →]    │
└─────────────────────────────────────────────────┘
```

### 7.5 완료 화면 (CompletePage)
```
┌─────────────────────────────────────────────────┐
│                                                 │
│               ✓ (체크 아이콘)                   │
│                                                 │
│          견적서를 발송했습니다!                  │
│                                                 │
│          010-****-5678 으로                     │
│          카카오톡을 확인해주세요                 │
│                                                 │
│          ┌─────────────────────┐               │
│          │     처음으로        │               │
│          └─────────────────────┘               │
│                                                 │
│          10초 후 자동으로 처음 화면으로 이동      │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 8. 애니메이션 & 트랜지션

### 기본 트랜지션
```css
/* 기본 전환 */
transition-duration: 200ms;
transition-timing-function: ease-out;

/* 페이지 전환 */
transition-duration: 300ms;
transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
```

### 페이지 전환
```css
/* 진입 */
animation: slideInRight 300ms ease-out;

/* 퇴장 */
animation: slideOutLeft 300ms ease-out;

@keyframes slideInRight {
  from { transform: translateX(100px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
```

### 카드 선택 애니메이션
```css
/* 선택 시 */
animation: selectPop 200ms ease-out;

@keyframes selectPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}
```

### 완료 체크 애니메이션
```css
/* 체크마크 그리기 */
animation: drawCheck 500ms ease-out;
stroke-dasharray: 100;
stroke-dashoffset: 100;

@keyframes drawCheck {
  to { stroke-dashoffset: 0; }
}
```

---

## 9. 반응형 고려사항

### iPad 모델별 대응
```css
/* iPad 10세대 (기본) */
@media (min-width: 1180px) { }

/* iPad Pro 11" */
@media (min-width: 1194px) { }

/* iPad Pro 12.9" */
@media (min-width: 1366px) {
  /* 더 넓은 여백, 더 큰 카드 */
}

/* iPad Mini */
@media (max-width: 1133px) {
  /* 약간 축소된 폰트 사이즈 */
}
```

### 가로/세로 강제 고정
```javascript
// PWA manifest
"orientation": "landscape"

// CSS fallback
@media (orientation: portrait) {
  .rotate-message {
    display: flex;
    /* "가로로 회전해주세요" 메시지 표시 */
  }
}
```

---

## 10. 접근성 (Accessibility)

### 필수 적용 사항
```
- 색상 대비: WCAG AA 기준 (4.5:1 이상)
- 터치 타겟: 최소 48px (권장 64px)
- 포커스 표시: 명확한 아웃라인
- 애니메이션: reduced-motion 미디어쿼리 대응
```

### 색상 대비 체크
```css
/* 최소 대비 */
--text-primary on white: 12.6:1 ✓
--text-secondary on white: 4.6:1 ✓
--accent-blue on white: 4.5:1 ✓
white on --accent-blue: 4.5:1 ✓
```

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 11. 다크모드 (선택사항)

현재 버전에서는 라이트모드만 지원. 추후 확장 시:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --primary-black: #F5F5F7;
    --primary-white: #1D1D1F;
    --primary-gray: #2C2C2E;
    /* ... */
  }
}
```

---

## 12. 체크리스트

### 개발 전 확인
- [ ] Pretendard 폰트 적용
- [ ] 컬러 변수 정의 (CSS Variables)
- [ ] 기본 컴포넌트 스타일 세팅
- [ ] Tailwind config 커스터마이징

### 컴포넌트별 확인
- [ ] 버튼 터치 피드백 동작
- [ ] 카드 선택 상태 스타일
- [ ] 입력 필드 포커스 스타일
- [ ] 모달 백드롭 블러

### 최종 QA
- [ ] 실제 iPad에서 터치 테스트
- [ ] 폰트 크기 가독성 (40-60대 테스트)
- [ ] 자동 복귀 타이머 동작
- [ ] 가로모드 고정 확인