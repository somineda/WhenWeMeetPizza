# 카카오톡 공유 기능 구현 가이드

## 1. 카카오 개발자 설정

### 1단계: 앱 등록
1. [카카오 개발자 콘솔](https://developers.kakao.com/) 접속
2. 내 애플리케이션 → 애플리케이션 추가하기
3. 앱 이름, 사업자명 입력

### 2단계: JavaScript 키 발급
1. 앱 선택 → 요약 정보
2. **JavaScript 키** 복사

### 3단계: 플랫폼 등록
1. 앱 설정 → 플랫폼
2. Web 플랫폼 등록
3. 사이트 도메인 입력:
   - 개발: `http://localhost:3000`
   - 운영: `https://yourdomain.com`

---

## 2. 프론트엔드 구현 (React)

### 설치 및 초기화

```bash
# React 프로젝트에서
npm install react-kakao-sdk
```

### App.js - SDK 초기화

```javascript
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Kakao SDK 초기화
    if (window.Kakao && !window.Kakao.isInitialized()) {
      window.Kakao.init('YOUR_JAVASCRIPT_KEY'); // 발급받은 키로 교체
      console.log('Kakao SDK initialized:', window.Kakao.isInitialized());
    }
  }, []);

  return (
    <div className="App">
      {/* 앱 컴포넌트 */}
    </div>
  );
}

export default App;
```

### public/index.html - SDK 추가

```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <title>Pizza Meeting Scheduler</title>

    <!-- 카카오 SDK 추가 -->
    <script src="https://developers.kakao.com/sdk/js/kakao.js"></script>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

### KakaoShareButton.jsx - 공유 버튼 컴포넌트

```javascript
import React, { useState } from 'react';

const KakaoShareButton = ({ eventId }) => {
  const [loading, setLoading] = useState(false);

  const handleKakaoShare = async () => {
    if (!window.Kakao) {
      alert('카카오톡 공유 기능을 사용할 수 없습니다.');
      return;
    }

    try {
      setLoading(true);

      // 백엔드에서 공유 정보 가져오기
      const response = await fetch(`/api/v1/events/${eventId}/share-info`);
      const data = await response.json();

      // 카카오톡 공유하기 (템플릿 직접 사용)
      window.Kakao.Share.sendDefault(data.kakao_template);

    } catch (error) {
      console.error('카카오톡 공유 실패:', error);
      alert('공유에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleKakaoShare}
      disabled={loading}
      style={{
        backgroundColor: '#FEE500',
        color: '#000000',
        border: 'none',
        padding: '12px 24px',
        fontSize: '16px',
        borderRadius: '8px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}
    >
      <img
        src="https://developers.kakao.com/assets/img/about/logos/kakaolink/kakaolink_btn_medium.png"
        alt="카카오톡"
        style={{ width: '24px', height: '24px' }}
      />
      {loading ? '공유 중...' : '카카오톡으로 공유'}
    </button>
  );
};

export default KakaoShareButton;
```

### 사용 예시

```javascript
// EventDetailPage.jsx
import KakaoShareButton from './components/KakaoShareButton';

function EventDetailPage({ event }) {
  return (
    <div>
      <h1>{event.title}</h1>
      <p>{event.description}</p>

      {/* 카카오톡 공유 버튼 */}
      <KakaoShareButton eventId={event.id} />
    </div>
  );
}
```

---

## 3. API 응답 구조

### GET /api/v1/events/{event_id}/share-info

```json
{
  "event_id": 1,
  "event_title": "피자 파티 일정 조율",
  "share_url": "http://localhost:3000/e/abc123",

  "kakao_template": {
    "object_type": "feed",
    "content": {
      "title": "📅 피자 파티 일정 조율",
      "description": "맛있는 피자를 먹으며 즐거운 시간을 보내요!",
      "image_url": "",
      "link": {
        "web_url": "http://localhost:3000/e/abc123",
        "mobile_web_url": "http://localhost:3000/e/abc123"
      }
    },
    "buttons": [
      {
        "title": "일정 참여하기",
        "link": {
          "web_url": "http://localhost:3000/e/abc123",
          "mobile_web_url": "http://localhost:3000/e/abc123"
        }
      }
    ]
  }
}
```

---

## 4. 고급 기능

### 커스텀 이미지 추가

백엔드에서 이벤트에 이미지 필드를 추가하고:

```python
# apps/events/views.py - EventShareInfoView
kakao_template = {
    "object_type": "feed",
    "content": {
        "title": kakao_title,
        "description": kakao_description,
        "image_url": event.image_url if event.image_url else "https://yourdomain.com/default-image.png",
        # ...
    }
}
```

### 공유 성공 콜백

```javascript
window.Kakao.Share.sendDefault({
  ...data.kakao_template,
  callback: {
    success: function() {
      console.log('카카오톡 공유 성공');
      // 분석 이벤트 전송 등
    },
    fail: function(error) {
      console.error('카카오톡 공유 실패:', error);
    }
  }
});
```

### 여러 버튼 추가

```javascript
"buttons": [
  {
    "title": "일정 참여하기",
    "link": {
      "web_url": data.share_url,
      "mobile_web_url": data.share_url
    }
  },
  {
    "title": "자세히 보기",
    "link": {
      "web_url": `${data.share_url}/detail`,
      "mobile_web_url": `${data.share_url}/detail`
    }
  }
]
```

---

## 5. 테스트

### 개발 환경 테스트
1. 로컬 서버 실행: `http://localhost:3000`
2. 카카오 개발자 콘솔에서 플랫폼 등록 확인
3. 브라우저에서 공유 버튼 클릭
4. 카카오톡 앱이나 웹 카카오톡으로 테스트

### 문제 해결

**"SDK is not initialized" 에러**
- `window.Kakao.init()` 호출 확인
- JavaScript 키가 올바른지 확인

**"Invalid origin" 에러**
- 플랫폼 설정에서 도메인 확인
- 프로토콜(http/https) 일치 확인

**공유가 안 되는 경우**
- 브라우저 콘솔에서 에러 확인
- 카카오톡 로그인 상태 확인
- 모바일에서는 카카오톡 앱 설치 확인

---

## 6. 보안 주의사항

⚠️ **JavaScript 키는 공개되어도 안전합니다**
- 프론트엔드에서 사용하는 키이므로 노출되어도 괜찮음
- REST API 키는 절대 프론트엔드에 노출하지 마세요

⚠️ **Admin 키는 백엔드에서만 사용**
- 서버 환경변수에 저장
- 절대 프론트엔드 코드에 포함하지 마세요

---

## 참고 자료

- [카카오 개발자 문서 - JavaScript SDK](https://developers.kakao.com/docs/latest/ko/javascript/getting-started)
- [카카오톡 공유 가이드](https://developers.kakao.com/docs/latest/ko/message/js-link)
- [메시지 템플릿](https://developers.kakao.com/docs/latest/ko/message/message-template)
