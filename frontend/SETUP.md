# 프론트엔드 설치 및 실행 가이드

## 🚀 빠른 시작

### 1. Node.js 설치 확인

```bash
node --version
npm --version
```

Node.js가 설치되어 있지 않다면:

**macOS (Homebrew):**
```bash
brew install node
```

**또는 공식 사이트:**
https://nodejs.org/ (LTS 버전 권장)

---

### 2. 프로젝트 의존성 설치

```bash
cd frontend
npm install
```

**설치되는 주요 패키지:**
- Next.js 14 (React 프레임워크)
- TypeScript (타입 안정성)
- Tailwind CSS (스타일링)
- Axios (HTTP 클라이언트)
- Zustand (상태 관리)
- React Hook Form + Zod (폼 관리 및 검증)
- React Hot Toast (알림)
- date-fns (날짜 처리)

---

### 3. 환경 변수 확인

`.env.local` 파일이 이미 생성되어 있습니다:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

필요한 경우 백엔드 URL을 수정하세요.

---

### 4. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:3000 을 열어주세요!

---

## 📱 구현된 페이지

### ✅ 완료된 페이지

1. **홈페이지** (`/`)
   - 서비스 소개
   - 주요 기능 안내
   - 반응형 디자인

2. **로그인** (`/login`)
   - 이메일/비밀번호 로그인
   - 폼 검증 (Zod)
   - 에러 처리
   - 자동 인증 상태 관리

3. **회원가입** (`/register`)
   - 이메일, 닉네임, 비밀번호 입력
   - 비밀번호 확인 검증
   - 자동 로그인 및 리다이렉트

### ⏳ 다음 구현 예정

4. **이벤트 생성** (`/events/create`)
5. **이벤트 상세** (`/e/[slug]`)
6. **내 이벤트 목록** (`/events/my`)
7. **대시보드** (`/e/[slug]/dashboard`)

---

## 🧪 테스트 방법

### 1. 백엔드 서버 먼저 실행

```bash
# 별도 터미널에서
cd ..  # pizza 프로젝트 루트로 이동
source venv/bin/activate
python manage.py runserver
```

### 2. 프론트엔드 실행

```bash
# frontend 디렉토리에서
npm run dev
```

### 3. 회원가입 테스트

1. http://localhost:3000 접속
2. "회원가입" 버튼 클릭
3. 이메일, 닉네임, 비밀번호 입력
4. 회원가입 완료 후 자동 로그인

### 4. 로그인 테스트

1. http://localhost:3000/login 접속
2. 등록한 이메일/비밀번호 입력
3. 로그인 성공 시 "내 이벤트" 페이지로 리다이렉트

---

## 🎨 UI 컴포넌트 사용법

### Button 컴포넌트

```tsx
import Button from '@/components/ui/Button';

// Primary 버튼
<Button variant="primary">클릭</Button>

// 로딩 상태
<Button variant="primary" isLoading>처리 중...</Button>

// 크기 변경
<Button size="sm">작은 버튼</Button>
<Button size="lg">큰 버튼</Button>

// 비활성화
<Button disabled>비활성화</Button>
```

### Input 컴포넌트

```tsx
import Input from '@/components/ui/Input';

// 기본 입력
<Input label="이메일" type="email" />

// 에러 표시
<Input
  label="비밀번호"
  type="password"
  error="비밀번호를 입력해주세요"
/>

// 헬퍼 텍스트
<Input
  label="닉네임"
  helperText="2-20자 사이로 입력해주세요"
/>
```

### Card 컴포넌트

```tsx
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card';

<Card>
  <CardHeader>
    <h2>제목</h2>
  </CardHeader>
  <CardBody>
    <p>내용</p>
  </CardBody>
  <CardFooter>
    <Button>확인</Button>
  </CardFooter>
</Card>
```

---

## 🔧 개발 팁

### Hot Reload
파일을 저장하면 자동으로 브라우저가 새로고침됩니다.

### TypeScript 에러 확인
```bash
npm run build
```

### 코드 스타일 검사
```bash
npm run lint
```

### Tailwind CSS IntelliSense
VSCode 확장 프로그램 "Tailwind CSS IntelliSense"를 설치하면 클래스 자동완성을 사용할 수 있습니다.

---

## 📂 프로젝트 구조

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 루트 레이아웃
│   ├── page.tsx           # 홈페이지 ✅
│   ├── login/             # 로그인 ✅
│   │   └── page.tsx
│   ├── register/          # 회원가입 ✅
│   │   └── page.tsx
│   └── events/            # 이벤트 관련 (예정)
│       ├── create/
│       └── my/
├── components/            # React 컴포넌트
│   ├── ui/               # 공통 UI 컴포넌트 ✅
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Card.tsx
│   ├── layout/           # 레이아웃 컴포넌트 ✅
│   │   └── Header.tsx
│   └── event/            # 이벤트 관련 컴포넌트 (예정)
├── lib/                  # 유틸리티 & 설정
│   ├── api.ts           # API 클라이언트 ✅
│   ├── store.ts         # Zustand 상태 관리 ✅
│   └── utils.ts         # 유틸리티 함수 ✅
└── types/               # TypeScript 타입 정의 ✅
    └── index.ts
```

---

## 🐛 문제 해결

### Q: `npm install`이 실패합니다
**A:** Node.js 버전을 확인하세요. Node.js 18 이상을 권장합니다.

```bash
node --version  # v18.0.0 이상인지 확인
```

### Q: 백엔드 연결이 안 됩니다
**A:** 백엔드 서버가 실행 중인지 확인하세요.

```bash
# 백엔드 서버 실행 확인
curl http://127.0.0.1:8000/api/v1/auth/login/
```

### Q: CORS 에러가 발생합니다
**A:** 백엔드 설정에서 CORS가 허용되어 있는지 확인하세요.

`config/settings/development.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True  # 개발 환경에서만!
```

### Q: 페이지가 하얗게 나옵니다
**A:** 브라우저 콘솔(F12)에서 에러를 확인하세요.

---

## 📝 다음 단계

로그인/회원가입이 완료되었습니다! 다음으로 구현할 페이지:

1. **이벤트 생성 페이지** - 새로운 일정 만들기
2. **이벤트 상세 페이지** - 일정 정보 및 참가자 등록
3. **가능 시간 선택 페이지** - 타임슬롯 선택 UI
4. **대시보드 페이지** - 참가 현황 히트맵

---

생성일: 2026-01-08
