# Pizza Scheduler Frontend

React + Next.js 기반의 일정 조율 플랫폼 프론트엔드입니다.

## 🚀 시작하기

### 1. Node.js 설치

먼저 Node.js를 설치해주세요.

**macOS (Homebrew):**
```bash
brew install node
```

**또는 공식 사이트에서 다운로드:**
https://nodejs.org/ (LTS 버전 권장)

### 2. 의존성 설치

```bash
cd frontend
npm install
```

### 3. 환경 변수 설정

`.env.local` 파일이 이미 생성되어 있습니다:

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

### 4. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:3000 을 열어주세요.

## 📁 프로젝트 구조

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 루트 레이아웃
│   ├── page.tsx           # 홈페이지
│   ├── globals.css        # 전역 스타일
│   ├── login/             # 로그인 페이지
│   ├── register/          # 회원가입 페이지
│   ├── events/            # 이벤트 관련 페이지
│   └── e/[slug]/          # 이벤트 상세 페이지
├── components/            # React 컴포넌트
│   ├── ui/               # 기본 UI 컴포넌트
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Card.tsx
│   ├── layout/           # 레이아웃 컴포넌트
│   │   └── Header.tsx
│   ├── event/            # 이벤트 관련 컴포넌트
│   └── participant/      # 참가자 관련 컴포넌트
├── lib/                  # 유틸리티 & 설정
│   ├── api.ts           # API 클라이언트
│   ├── store.ts         # Zustand 상태 관리
│   └── utils.ts         # 유틸리티 함수
├── types/               # TypeScript 타입 정의
│   └── index.ts
└── public/              # 정적 파일
```

## 🛠 기술 스택

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Form Handling:** React Hook Form + Zod
- **Date Handling:** date-fns
- **Notifications:** React Hot Toast
- **Icons:** Lucide React
- **QR Code:** qrcode.react

## 📦 주요 라이브러리

```json
{
  "next": "14.2.0",
  "react": "^18.3.0",
  "axios": "^1.6.7",
  "zustand": "^4.5.0",
  "react-hook-form": "^7.50.0",
  "zod": "^3.22.4",
  "date-fns": "^3.3.1",
  "react-hot-toast": "^2.4.1",
  "tailwindcss": "^3.4.1"
}
```

## 🎨 UI 컴포넌트

### Button
```tsx
import Button from '@/components/ui/Button';

<Button variant="primary" size="md">클릭</Button>
<Button variant="outline" isLoading>처리 중</Button>
```

**Variants:** `primary` | `secondary` | `outline` | `ghost` | `danger`
**Sizes:** `sm` | `md` | `lg`

### Input
```tsx
import Input from '@/components/ui/Input';

<Input
  label="이메일"
  type="email"
  error="올바른 이메일을 입력해주세요"
/>
```

### Card
```tsx
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card';

<Card>
  <CardHeader>제목</CardHeader>
  <CardBody>내용</CardBody>
  <CardFooter>푸터</CardFooter>
</Card>
```

## 🔌 API 사용법

### 인증
```tsx
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

const { setAuth } = useAuthStore();

// 로그인
const response = await authApi.login(email, password);
setAuth(response.user, response.tokens.access, response.tokens.refresh);
```

### 이벤트
```tsx
import { eventApi } from '@/lib/api';

// 이벤트 생성
const event = await eventApi.create({
  title: '피자 파티',
  description: '맛있는 피자!',
  date_start: '2026-01-15',
  date_end: '2026-01-16',
  time_start: '14:00',
  time_end: '16:00',
  timezone: 'Asia/Seoul'
});

// 이벤트 조회
const event = await eventApi.getBySlug('4e7073ef');

// 대시보드 조회
const dashboard = await eventApi.getDashboard(eventId);
```

## 📄 구현 현황

### ✅ 모든 페이지 완성! 🎉

1. ✅ 홈페이지 (`/`)
2. ✅ 로그인 페이지 (`/login`)
3. ✅ 회원가입 페이지 (`/register`)
4. ✅ 이벤트 생성 페이지 (`/events/create`)
5. ✅ 내 이벤트 목록 페이지 (`/events/my`)
6. ✅ 이벤트 상세 페이지 (`/e/[slug]`)
   - 이벤트 정보 표시
   - 공유 링크/QR 코드
   - 참가자 등록
   - 가능 시간 선택
7. ✅ 대시보드 페이지 (`/e/[slug]/dashboard`)
   - 통계 카드 (참가자, 제출률, 인기 시간)
   - 참가자 현황 테이블
   - 히트맵 차트 (시간대별 가능 인원)
   - 최종 시간 선택 (생성자 전용)
   - 확정 이메일 발송

## 🐛 개발 팁

- **Hot Reload:** 파일을 저장하면 자동으로 브라우저가 새로고침됩니다
- **TypeScript:** 타입 에러가 있으면 빌드가 실패합니다
- **Tailwind CSS:** 클래스 자동완성을 위해 Tailwind CSS IntelliSense VSCode 확장 설치 권장

## 📞 백엔드 연결

Django 백엔드 서버가 `http://127.0.0.1:8000`에서 실행 중이어야 합니다.

```bash
# 백엔드 서버 실행 (별도 터미널)
cd ..
source venv/bin/activate
python manage.py runserver
```

## 🚀 빌드 & 배포

### 프로덕션 빌드
```bash
npm run build
npm run start
```

### 정적 내보내기
```bash
npm run build
# out/ 폴더에 정적 파일 생성
```

---

생성일: 2026-01-08
버전: 0.1.0
