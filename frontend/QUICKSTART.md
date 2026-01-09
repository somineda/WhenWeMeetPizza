# 🚀 빠른 시작 가이드

## 1단계: Node.js 설치

```bash
# macOS (Homebrew)
brew install node

# 설치 확인
node --version  # v18 이상
npm --version   # v9 이상
```

## 2단계: 의존성 설치

```bash
cd frontend
npm install
```

## 3단계: 백엔드 서버 실행 (별도 터미널)

```bash
# 프로젝트 루트로 이동
cd /Users/yunsomin/Downloads/pizza

# 가상환경 활성화
source venv/bin/activate

# Django 서버 실행
python manage.py runserver
```

백엔드가 http://127.0.0.1:8000 에서 실행됩니다.

## 4단계: 프론트엔드 실행

```bash
# frontend 디렉토리에서
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

## 5단계: 테스트하기

### 회원가입
1. http://localhost:3000 접속
2. 우측 상단 "회원가입" 클릭
3. 이메일, 닉네임, 비밀번호 입력
4. 회원가입 완료!

### 이벤트 만들기
1. 로그인 후 "이벤트 만들기" 버튼 클릭
2. 제목: "피자 파티"
3. 날짜: 내일 ~ 모레
4. 시간: 14:00 ~ 16:00
5. "이벤트 만들기" 클릭
6. 생성된 이벤트 페이지로 이동!

### 공유하기
1. 이벤트 페이지에서 공유 URL 복사
2. 친구들에게 공유
3. 친구들이 가능한 시간 선택
4. 대시보드에서 결과 확인

---

## 🎯 완성된 기능

### ✅ 홈페이지 (/)
- 서비스 소개
- 주요 기능 안내
- 로그인/회원가입 버튼

### ✅ 로그인 (/login)
- 이메일/비밀번호 로그인
- 폼 검증
- 자동 인증 상태 관리
- 로그인 후 "내 이벤트"로 이동

### ✅ 회원가입 (/register)
- 이메일, 닉네임, 비밀번호 입력
- 비밀번호 확인 검증
- 회원가입 후 자동 로그인
- 이벤트 생성 페이지로 이동

### ✅ 이벤트 생성 (/events/create)
- 제목, 설명 입력
- 날짜 범위 선택 (date picker)
- 시간 범위 선택 (time picker)
- 타임존 선택
- 날짜/시간 유효성 검증
- 타임슬롯 자동 생성 안내

### ✅ 내 이벤트 목록 (/events/my)
- 내가 만든 이벤트 목록
- 이벤트 카드 UI
- 참가자 수 표시
- 최종 확정 상태 표시
- 이벤트 상세 보기 링크
- 대시보드 링크

---

## 🎨 UI 컴포넌트

### Button
```tsx
<Button variant="primary">확인</Button>
<Button variant="outline">취소</Button>
<Button isLoading>처리 중...</Button>
```

### Input
```tsx
<Input
  label="이메일"
  type="email"
  error="에러 메시지"
/>
```

### Textarea
```tsx
<Textarea
  label="설명"
  rows={3}
  placeholder="입력하세요"
/>
```

### Select
```tsx
<Select
  label="선택"
  options={[
    { value: '1', label: '옵션 1' },
    { value: '2', label: '옵션 2' },
  ]}
/>
```

### Card
```tsx
<Card>
  <CardHeader>제목</CardHeader>
  <CardBody>내용</CardBody>
</Card>
```

---

## 🔧 개발 명령어

```bash
# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm run start

# 린트 검사
npm run lint
```

---

## 📁 파일 구조

```
frontend/
├── app/
│   ├── page.tsx                    # 홈 ✅
│   ├── login/page.tsx              # 로그인 ✅
│   ├── register/page.tsx           # 회원가입 ✅
│   └── events/
│       ├── create/page.tsx         # 이벤트 생성 ✅
│       └── my/page.tsx             # 내 이벤트 ✅
├── components/
│   ├── ui/
│   │   ├── Button.tsx              # 버튼 ✅
│   │   ├── Input.tsx               # 입력 ✅
│   │   ├── Textarea.tsx            # 텍스트영역 ✅
│   │   ├── Select.tsx              # 선택 ✅
│   │   └── Card.tsx                # 카드 ✅
│   └── layout/
│       └── Header.tsx              # 헤더 ✅
├── lib/
│   ├── api.ts                      # API 클라이언트 ✅
│   ├── store.ts                    # 상태 관리 ✅
│   └── utils.ts                    # 유틸 함수 ✅
└── types/
    └── index.ts                    # 타입 정의 ✅
```

---

## 🐛 문제 해결

### Q: npm install 실패
```bash
# Node.js 버전 확인
node --version  # v18 이상 필요

# npm 캐시 클리어
npm cache clean --force
npm install
```

### Q: 백엔드 연결 안 됨
```bash
# 백엔드 서버 실행 확인
curl http://127.0.0.1:8000/api/v1/auth/login/
```

### Q: CORS 에러
백엔드 설정 확인:
```python
# config/settings/development.py
CORS_ALLOW_ALL_ORIGINS = True
```

### Q: 화면이 안 나옴
```bash
# 브라우저 콘솔(F12)에서 에러 확인
# 터미널에서 에러 로그 확인
```

---

## 📝 다음 구현 예정

1. **이벤트 상세 페이지** (`/e/[slug]`)
   - 이벤트 정보 표시
   - 참가자 등록 폼
   - 공유 링크/QR 코드

2. **가능 시간 선택 페이지**
   - 타임슬롯 그리드 UI
   - 다중 선택 기능
   - 제출 확인

3. **대시보드 페이지** (`/e/[slug]/dashboard`)
   - 참가자 제출 현황
   - 히트맵 시각화
   - 최적 시간 추천
   - 최종 시간 선택

---

생성일: 2026-01-08
