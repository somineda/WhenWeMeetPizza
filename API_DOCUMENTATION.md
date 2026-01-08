# Pizza Scheduler API 문서

## 📋 목차
1. [인증 API](#1-인증-api)
2. [이벤트 API](#2-이벤트-api)
3. [참가자 API](#3-참가자-api)
4. [시간 추천 API](#4-시간-추천-api)
5. [이벤트 공유 API](#5-이벤트-공유-api)
6. [대시보드 API](#6-대시보드-api)
7. [캘린더 내보내기 API](#7-캘린더-내보내기-api)

---

## 1. 인증 API

### 1.1 회원가입
```
POST /api/v1/auth/register/
```

**요청 Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "nickname": "홍길동"
}
```

**응답 (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "홍길동",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**권한:** 인증 불필요 (AllowAny)

---

### 1.2 로그인
```
POST /api/v1/auth/login/
```

**요청 Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**응답 (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "홍길동",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**권한:** 인증 불필요 (AllowAny)

---

### 1.3 내 프로필 조회
```
GET /api/v1/auth/me/
```

**응답 (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "홍길동"
}
```

**권한:** 인증 필요 (Bearer Token)

**헤더:**
```
Authorization: Bearer {access_token}
```

---

## 2. 이벤트 API

### 2.1 이벤트 생성
```
POST /api/v1/events/
```

**요청 Body:**
```json
{
  "title": "피자 파티 일정 조율",
  "description": "맛있는 피자를 먹으며 즐거운 시간을 보내요!",
  "date_start": "2026-01-15",
  "date_end": "2026-01-16",
  "time_start": "14:00",
  "time_end": "16:00",
  "timezone": "Asia/Seoul"
}
```

**응답 (201 Created):**
```json
{
  "id": 1,
  "title": "피자 파티 일정 조율",
  "slug": "4e7073ef",
  "description": "맛있는 피자를 먹으며 즐거운 시간을 보내요!",
  "date_start": "2026-01-15",
  "date_end": "2026-01-16",
  "time_start": "14:00",
  "time_end": "16:00",
  "timezone": "Asia/Seoul",
  "created_by": 1,
  "created_at": "2026-01-08T10:30:00+09:00",
  "time_slots": [
    {
      "id": 101,
      "start_datetime": "2026-01-15T14:00:00+09:00",
      "end_datetime": "2026-01-15T14:30:00+09:00"
    },
    // ... 30분 단위로 자동 생성된 타임슬롯들
  ]
}
```

**기능:**
- 타임슬롯이 30분 단위로 자동 생성됨
- 고유한 slug 자동 생성

**권한:** 인증 필요 (Bearer Token)

---

### 2.2 이벤트 상세 조회
```
GET /api/v1/events/{slug}/
```

**응답 (200 OK):**
```json
{
  "id": 1,
  "title": "피자 파티 일정 조율",
  "slug": "4e7073ef",
  "description": "맛있는 피자를 먹으며 즐거운 시간을 보내요!",
  "date_start": "2026-01-15",
  "date_end": "2026-01-16",
  "time_start": "14:00",
  "time_end": "16:00",
  "timezone": "Asia/Seoul",
  "created_by": {
    "id": 1,
    "nickname": "홍길동"
  },
  "time_slots": [
    {
      "id": 101,
      "start_datetime": "2026-01-15T14:00:00+09:00",
      "end_datetime": "2026-01-15T14:30:00+09:00"
    }
  ],
  "participants_count": 5,
  "final_choice": {
    "id": 1,
    "slot": {
      "id": 103,
      "start_datetime": "2026-01-15T15:00:00+09:00",
      "end_datetime": "2026-01-15T15:30:00+09:00"
    },
    "chosen_by": {
      "id": 1,
      "nickname": "홍길동"
    },
    "created_at": "2026-01-08T11:00:00+09:00"
  }
}
```

**권한:** 인증 불필요 (AllowAny)

---

### 2.3 내가 만든 이벤트 목록 조회
```
GET /api/v1/events/my/
```

**Query Parameters:**
- `page` (optional): 페이지 번호 (기본값: 1)
- `page_size` (optional): 페이지당 항목 수 (기본값: 10)

**응답 (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/events/my/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "피자 파티 일정 조율",
      "slug": "4e7073ef",
      "date_start": "2026-01-15",
      "date_end": "2026-01-16",
      "participants_count": 5,
      "created_at": "2026-01-08T10:30:00+09:00"
    }
  ]
}
```

**권한:** 인증 필요 (Bearer Token)

---

### 2.4 이벤트 수정
```
PUT /api/v1/events/{id}/
PATCH /api/v1/events/{id}/
```

**요청 Body (PATCH 예시):**
```json
{
  "title": "피자 파티 일정 조율 (수정됨)",
  "description": "새로운 설명"
}
```

**응답 (200 OK):**
```json
{
  "id": 1,
  "title": "피자 파티 일정 조율 (수정됨)",
  "description": "새로운 설명",
  // ... 기타 필드
}
```

**권한:** 이벤트 생성자만 가능

---

### 2.5 이벤트 요약 조회
```
GET /api/v1/events/{id}/summary/
```

**응답 (200 OK):**
```json
{
  "event_id": 1,
  "event_title": "피자 파티 일정 조율",
  "total_participants": 5,
  "submitted_participants": 3,
  "pending_participants": 2,
  "submission_rate": 60.0,
  "time_slots": [
    {
      "slot_id": 101,
      "start_datetime": "2026-01-15T14:00:00+09:00",
      "end_datetime": "2026-01-15T14:30:00+09:00",
      "available_count": 3,
      "availability_rate": 60.0
    }
  ]
}
```

**권한:** 인증 필요 (Bearer Token)

---

### 2.6 최종 시간 선택
```
POST /api/v1/events/{id}/final-choice
```

**요청 Body:**
```json
{
  "slot_id": 103
}
```

**응답 (201 Created):**
```json
{
  "event_id": 1,
  "date": "2026-01-15",
  "start_time": "15:00",
  "end_time": "15:30",
  "chosen_by": 1,
  "created_at": "2026-01-08T11:00:00+09:00",
  "slot_id": 103
}
```

**권한:** 이벤트 생성자만 가능

---

### 2.7 최종 시간 확정 이메일 발송
```
POST /api/v1/events/{id}/final-choice/send-email
```

**요청 Body:** 없음

**응답 (200 OK):**
```json
{
  "success": true,
  "message": "5명의 참가자에게 확정 알림 이메일을 발송했습니다",
  "sent_count": 5,
  "failed_count": 0
}
```

**기능:**
- 모든 참가자에게 최종 확정 시간 이메일 발송
- Celery를 통한 비동기 처리 (5초 후 발송)

**권한:** 이벤트 생성자만 가능

---

## 3. 참가자 API

### 3.1 참가자 등록 (익명/회원)
```
POST /api/v1/events/{slug}/participants/
```

**요청 Body (익명 참가자):**
```json
{
  "nickname": "철수",
  "email": "chulsoo@example.com"
}
```

**요청 Body (회원 참가자 - JWT 토큰 필요):**
```json
{
  "nickname": "홍길동"
}
```

**응답 (201 Created):**
```json
{
  "id": 10,
  "nickname": "철수",
  "email": "chulsoo@example.com",
  "is_registered": false,
  "created_at": "2026-01-08T12:00:00+09:00"
}
```

**권한:** 인증 불필요 (익명 가능)

---

### 3.2 참가자 목록 조회
```
GET /api/v1/events/{event_id}/participants
```

**응답 (200 OK):**
```json
{
  "event_id": 1,
  "participants": [
    {
      "id": 10,
      "nickname": "철수",
      "email": "chulsoo@example.com",
      "is_registered": false,
      "created_at": "2026-01-08T12:00:00+09:00"
    },
    {
      "id": 11,
      "nickname": "홍길동",
      "email": "user@example.com",
      "is_registered": true,
      "created_at": "2026-01-08T12:05:00+09:00"
    }
  ]
}
```

**권한:** 인증 불필요 (AllowAny)

---

### 3.3 참가자 가능 시간 제출
```
POST /api/v1/participants/{participant_id}/availability/
```

**요청 Body:**
```json
{
  "availabilities": [
    {
      "time_slot_id": 101,
      "is_available": true
    },
    {
      "time_slot_id": 102,
      "is_available": true
    },
    {
      "time_slot_id": 103,
      "is_available": false
    }
  ]
}
```

**응답 (201 Created):**
```json
{
  "participant_id": 10,
  "submitted_count": 2,
  "message": "가능 시간을 성공적으로 제출했습니다"
}
```

**권한:** 인증 불필요 (AllowAny)

---

## 4. 시간 추천 API

### 4.1 최적 시간 추천
```
GET /api/v1/events/{event_id}/recommend-time
```

**Query Parameters:**
- `limit` (optional): 추천할 시간대 개수 (기본값: 5)
- `min_participants` (optional): 최소 참가자 수 필터

**응답 (200 OK):**
```json
{
  "event_id": 1,
  "event_title": "피자 파티 일정 조율",
  "total_participants": 5,
  "total_time_slots": 8,
  "recommended_slots": [
    {
      "slot_id": 101,
      "start_datetime": "2026-01-15T14:00:00+09:00",
      "end_datetime": "2026-01-15T14:30:00+09:00",
      "start_datetime_local": "2026-01-15T14:00:00+09:00",
      "end_datetime_local": "2026-01-15T14:30:00+09:00",
      "available_count": 4,
      "total_participants": 5,
      "available_percentage": 80.0,
      "available_participants": ["철수", "영희", "민수", "지영"]
    }
  ],
  "message": "가장 많은 사람이 가능한 시간대 5개를 추천합니다"
}
```

**알고리즘:**
- 각 타임슬롯별 가능 인원 집계
- 가능 인원이 많은 순으로 정렬 (Timsort, O(N log N))
- 상위 N개 반환

**권한:** 인증 불필요 (AllowAny)

---

## 5. 이벤트 공유 API

### 5.1 QR 코드 생성
```
GET /api/v1/events/{event_id}/qr-code
```

**Query Parameters:**
- `size` (optional): QR 코드 크기 (기본값: 10)

**응답 (200 OK):**
- Content-Type: `image/png`
- PNG 이미지 파일

**권한:** 인증 불필요 (AllowAny)

---

### 5.2 공유 정보 조회
```
GET /api/v1/events/{event_id}/share-info
```

**응답 (200 OK):**
```json
{
  "event_id": 1,
  "event_title": "피자 파티 일정 조율",
  "event_slug": "4e7073ef",
  "share_url": "http://localhost:3000/e/4e7073ef",
  "qr_code_url": "http://localhost:8000/api/v1/events/1/qr-code",
  "kakao_title": "📅 피자 파티 일정 조율",
  "kakao_description": "맛있는 피자를 먹으며 즐거운 시간을 보내요!",
  "kakao_image_url": null,
  "kakao_template": {
    "object_type": "feed",
    "content": {
      "title": "📅 피자 파티 일정 조율",
      "description": "맛있는 피자를 먹으며 즐거운 시간을 보내요!",
      "image_url": null,
      "link": {
        "web_url": "http://localhost:3000/e/4e7073ef",
        "mobile_web_url": "http://localhost:3000/e/4e7073ef"
      }
    },
    "buttons": [
      {
        "title": "일정 참여하기",
        "link": {
          "web_url": "http://localhost:3000/e/4e7073ef",
          "mobile_web_url": "http://localhost:3000/e/4e7073ef"
        }
      }
    ]
  },
  "email_subject": "[일정 조율 초대] 피자 파티 일정 조율",
  "email_body": "안녕하세요!\n\n'피자 파티 일정 조율' 일정 조율에 초대합니다..."
}
```

**권한:** 인증 불필요 (AllowAny)

---

### 5.3 초대 이메일 발송
```
POST /api/v1/events/{event_id}/invite
```

**요청 Body:**
```json
{
  "emails": [
    "friend1@example.com",
    "friend2@example.com",
    "friend3@example.com"
  ],
  "message": "함께 피자 먹어요! 😊"
}
```

**응답 (200 OK):**
```json
{
  "success": true,
  "message": "3명에게 초대 메일을 발송했습니다",
  "sent_count": 3,
  "total_count": 3,
  "failed_emails": []
}
```

**권한:** 이벤트 생성자만 가능

---

## 6. 대시보드 API

### 6.1 참가 현황 대시보드
```
GET /api/v1/events/{event_id}/dashboard
```

**Query Parameters (익명 참가자용):**
- `participant_id`: 참가자 ID
- `email`: 참가자 이메일

**응답 (200 OK):**
```json
{
  "event_id": 1,
  "event_title": "피자 파티 일정 조율",
  "stats": {
    "total_participants": 5,
    "submitted_participants": 3,
    "pending_participants": 2,
    "submission_rate": 60.0,
    "total_time_slots": 8,
    "most_popular_slot": {
      "slot_id": 101,
      "start_datetime_local": "2026-01-15T14:00:00+09:00",
      "available_count": 4,
      "availability_rate": 80.0
    }
  },
  "participants": [
    {
      "participant_id": 10,
      "nickname": "철수",
      "email": "chulsoo@example.com",
      "is_registered": false,
      "has_submitted": true,
      "submitted_slots_count": 6,
      "joined_at": "2026-01-08T12:00:00+09:00"
    },
    {
      "participant_id": 11,
      "nickname": "영희",
      "email": "younghee@example.com",
      "is_registered": false,
      "has_submitted": false,
      "submitted_slots_count": 0,
      "joined_at": "2026-01-08T12:05:00+09:00"
    }
  ],
  "heatmap": [
    {
      "slot_id": 101,
      "start_datetime": "2026-01-15T14:00:00+09:00",
      "end_datetime": "2026-01-15T14:30:00+09:00",
      "start_datetime_local": "2026-01-15T14:00:00+09:00",
      "end_datetime_local": "2026-01-15T14:30:00+09:00",
      "available_count": 4,
      "available_participants": [
        {
          "participant_id": 10,
          "nickname": "철수"
        },
        {
          "participant_id": 12,
          "nickname": "민수"
        }
      ],
      "availability_rate": 80.0
    }
  ]
}
```

**권한:**
- 이벤트 생성자: JWT 토큰으로 인증
- 회원 참가자: JWT 토큰으로 인증
- 익명 참가자: `participant_id`와 `email` query parameter로 인증

**예시:**
```bash
# 회원/생성자
GET /api/v1/events/1/dashboard
Authorization: Bearer {token}

# 익명 참가자
GET /api/v1/events/1/dashboard?participant_id=10&email=chulsoo@example.com
```

---

## 7. 캘린더 내보내기 API

### 7.1 캘린더 내보내기 정보 조회
```
GET /api/v1/events/{event_id}/calendar-export
```

**응답 (200 OK - 최종 시간 확정된 경우):**
```json
{
  "event_id": 1,
  "event_title": "피자 파티",
  "has_final_choice": true,
  "final_start_datetime": "2026-01-15T15:00:00+09:00",
  "final_end_datetime": "2026-01-15T15:30:00+09:00",
  "final_start_datetime_local": "2026-01-15T15:00:00+09:00",
  "final_end_datetime_local": "2026-01-15T15:30:00+09:00",
  "google_calendar_url": "https://calendar.google.com/calendar/render?action=TEMPLATE&text=%ED%94%BC%EC%9E%90%20%ED%8C%8C%ED%8B%B0&dates=20260115T060000Z/20260115T063000Z&details=...",
  "ics_download_url": "http://localhost:8000/api/v1/events/1/calendar.ics",
  "message": "피자 파티 일정이 확정되었습니다. 캘린더에 추가하세요!"
}
```

**응답 (200 OK - 최종 시간 미확정):**
```json
{
  "event_id": 1,
  "event_title": "피자 파티",
  "has_final_choice": false,
  "final_start_datetime": null,
  "final_end_datetime": null,
  "final_start_datetime_local": null,
  "final_end_datetime_local": null,
  "google_calendar_url": null,
  "ics_download_url": "http://localhost:8000/api/v1/events/1/calendar.ics",
  "message": "아직 최종 시간이 확정되지 않았습니다."
}
```

**권한:** 인증 불필요 (AllowAny)

---

### 7.2 .ics 파일 다운로드
```
GET /api/v1/events/{event_id}/calendar.ics
```

**응답 (200 OK):**
- Content-Type: `text/calendar; charset=utf-8`
- Content-Disposition: `attachment; filename="{slug}.ics"`

**응답 Body (iCalendar 형식):**
```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Pizza Scheduler//Event Calendar//KO
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:event-1-finalchoice-1@pizzascheduler
DTSTAMP:20260108T071255Z
DTSTART:20260115T060000Z
DTEND:20260115T063000Z
SUMMARY:피자 파티
DESCRIPTION:맛있는 피자를 먹으며 즐거운 시간을 보내요!
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR
```

**응답 (400 Bad Request - 최종 시간 미확정):**
```json
{
  "detail": "아직 최종 시간이 확정되지 않았습니다."
}
```

**지원 캘린더:**
- Google Calendar
- Apple Calendar (macOS, iOS)
- Microsoft Outlook
- 기타 iCalendar 표준을 지원하는 모든 캘린더 앱

**권한:** 인증 불필요 (AllowAny)

---

## 📊 API 요약

### 인증 필요 API (Bearer Token)
- `POST /api/v1/events/` - 이벤트 생성
- `GET /api/v1/events/my/` - 내 이벤트 목록
- `PUT/PATCH /api/v1/events/{id}/` - 이벤트 수정
- `GET /api/v1/events/{id}/summary/` - 이벤트 요약
- `POST /api/v1/events/{id}/final-choice` - 최종 시간 선택
- `POST /api/v1/events/{id}/final-choice/send-email` - 확정 이메일 발송
- `POST /api/v1/events/{event_id}/invite` - 초대 이메일 발송
- `GET /api/v1/auth/me/` - 내 프로필 조회

### 이벤트 생성자 전용 API
- 이벤트 수정
- 최종 시간 선택
- 확정 이메일 발송
- 초대 이메일 발송

### 참가자 접근 가능 API
- `GET /api/v1/events/{event_id}/dashboard` - 대시보드 (생성자 + 모든 참가자)

### 인증 불필요 API (Public)
- `POST /api/v1/auth/register/` - 회원가입
- `POST /api/v1/auth/login/` - 로그인
- `GET /api/v1/events/{slug}/` - 이벤트 상세
- `POST /api/v1/events/{slug}/participants/` - 참가자 등록
- `GET /api/v1/events/{event_id}/participants` - 참가자 목록
- `POST /api/v1/participants/{id}/availability/` - 가능 시간 제출
- `GET /api/v1/events/{event_id}/recommend-time` - 시간 추천
- `GET /api/v1/events/{event_id}/qr-code` - QR 코드
- `GET /api/v1/events/{event_id}/share-info` - 공유 정보
- `GET /api/v1/events/{event_id}/calendar-export` - 캘린더 정보
- `GET /api/v1/events/{event_id}/calendar.ics` - .ics 다운로드

---

## 🔐 인증 방식

### JWT Bearer Token
```bash
# 헤더에 포함
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 익명 참가자 인증 (대시보드 접근)
```bash
# Query Parameter로 인증
GET /api/v1/events/1/dashboard?participant_id=10&email=user@example.com
```

---

## 🌐 Base URL

**개발 환경:**
```
http://127.0.0.1:8000
```

**프로덕션 환경:**
```
https://api.pizzascheduler.com
```

---

## 📝 에러 응답 형식

### 400 Bad Request
```json
{
  "field_name": [
    "필수 항목입니다"
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "잘못된 이메일 또는 비밀번호입니다"
}
```

### 403 Forbidden
```json
{
  "detail": "이벤트 생성자만 대시보드를 조회할 수 있습니다"
}
```

### 404 Not Found
```json
{
  "detail": "찾을 수 없습니다."
}
```

---

## 🎯 주요 기능별 API 플로우

### 1. 이벤트 생성 → 참가자 모집 → 시간 확정
```
1. POST /api/v1/auth/register/ (회원가입)
2. POST /api/v1/auth/login/ (로그인)
3. POST /api/v1/events/ (이벤트 생성)
4. GET /api/v1/events/{event_id}/share-info (공유 정보 조회)
5. POST /api/v1/events/{slug}/participants/ (참가자 등록 - 익명/회원)
6. POST /api/v1/participants/{id}/availability/ (가능 시간 제출)
7. GET /api/v1/events/{event_id}/dashboard (참가 현황 확인)
8. GET /api/v1/events/{event_id}/recommend-time (최적 시간 추천)
9. POST /api/v1/events/{id}/final-choice (최종 시간 선택)
10. POST /api/v1/events/{id}/final-choice/send-email (확정 알림 발송)
11. GET /api/v1/events/{event_id}/calendar-export (캘린더 추가)
```

### 2. 익명 참가자 플로우
```
1. GET /api/v1/events/{slug}/ (이벤트 조회)
2. POST /api/v1/events/{slug}/participants/ (참가 등록)
3. POST /api/v1/participants/{id}/availability/ (가능 시간 제출)
4. GET /api/v1/events/{event_id}/dashboard?participant_id=X&email=Y (현황 확인)
5. GET /api/v1/events/{event_id}/calendar-export (확정 시간 캘린더 추가)
```

### 3. 회원 참가자 플로우
```
1. POST /api/v1/auth/login/ (로그인)
2. GET /api/v1/events/{slug}/ (이벤트 조회)
3. POST /api/v1/events/{slug}/participants/ (참가 등록 - JWT 토큰 포함)
4. POST /api/v1/participants/{id}/availability/ (가능 시간 제출)
5. GET /api/v1/events/{event_id}/dashboard (현황 확인 - JWT 토큰으로 인증)
6. GET /api/v1/events/{event_id}/calendar-export (확정 시간 캘린더 추가)
```

---

## 💡 Swagger 문서

개발 서버에서 실시간 API 문서 및 테스트:

```
http://127.0.0.1:8000/api/schema/swagger-ui/
```

---

생성일: 2026-01-08
버전: 1.0.0
