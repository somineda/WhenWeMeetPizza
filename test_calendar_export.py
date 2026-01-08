#!/usr/bin/env python
"""
캘린더 내보내기 기능 테스트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.events.models import Event, TimeSlot, FinalChoice
from datetime import datetime, timedelta
from django.utils import timezone
import requests
import json

User = get_user_model()
BASE_URL = "http://127.0.0.1:8000"

print("\n📅 캘린더 내보내기 기능 테스트\n")

# 1. 테스트 데이터 생성
print("1️⃣ 테스트 데이터 생성 중...")

# 사용자 생성
user, _ = User.objects.get_or_create(
    email='test@example.com',
    defaults={'nickname': '테스트 주최자'}
)
if not user.check_password('testpass123456'):
    user.set_password('testpass123456')
    user.save()

# 로그인
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login/",
    json={"email": "test@example.com", "password": "testpass123456"}
)
access_token = login_response.json()['tokens']['access']
headers = {'Authorization': f'Bearer {access_token}'}

# 이벤트 생성 (API 사용 - 타임슬롯 자동 생성)
now = timezone.now()
event_data = {
    "title": "피자 파티",
    "description": "맛있는 피자를 먹으며 즐거운 시간을 보내요!",
    "date_start": (now + timedelta(days=1)).date().isoformat(),
    "date_end": (now + timedelta(days=1)).date().isoformat(),
    "time_start": "18:00",
    "time_end": "20:00",
    "timezone": "Asia/Seoul"
}

event_response = requests.post(
    f"{BASE_URL}/api/v1/events/",
    json=event_data,
    headers=headers
)
event_id = event_response.json()['id']
event = Event.objects.get(id=event_id)

print(f"   ✅ 이벤트 생성: {event.title} (ID: {event.id})")

# 타임슬롯 가져오기
slots = list(TimeSlot.objects.filter(event=event).order_by('start_datetime'))
print(f"   ✅ {len(slots)}개의 타임슬롯 생성")

# 2. 최종 시간 확정 전 테스트
print("\n2️⃣ 최종 시간 확정 전 - 캘린더 내보내기 조회")
print("="*70)

response = requests.get(f"{BASE_URL}/api/v1/events/{event.id}/calendar-export")
print(f"상태 코드: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\n📊 응답 데이터:")
    print(f"   이벤트: {data['event_title']}")
    print(f"   최종 시간 확정: {data['has_final_choice']}")
    print(f"   메시지: {data['message']}")
    print(f"   Google Calendar URL: {data['google_calendar_url']}")
    print(f"   .ics 다운로드 URL: {data['ics_download_url']}")
else:
    print(f"   ❌ 에러: {response.text}")

# 3. 최종 시간 확정
print("\n3️⃣ 최종 시간 확정 중...")

# 첫 번째 타임슬롯을 최종 시간으로 선택
final_slot = slots[0]
final_choice_data = {
    "slot_id": final_slot.id
}

final_response = requests.post(
    f"{BASE_URL}/api/v1/events/{event.id}/final-choice",
    json=final_choice_data,
    headers=headers
)

if final_response.status_code == 201:
    print(f"   ✅ 최종 시간 확정: {final_slot.start_datetime}")
else:
    print(f"   ❌ 확정 실패: {final_response.text}")

# 4. 최종 시간 확정 후 테스트
print("\n4️⃣ 최종 시간 확정 후 - 캘린더 내보내기 조회")
print("="*70)

response = requests.get(f"{BASE_URL}/api/v1/events/{event.id}/calendar-export")
print(f"상태 코드: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()
    print(f"📊 응답 데이터:")
    print(f"   이벤트: {data['event_title']}")
    print(f"   최종 시간 확정: {data['has_final_choice']}")
    print(f"   메시지: {data['message']}")

    if data['has_final_choice']:
        print(f"\n⏰ 확정된 시간:")
        print(f"   시작: {data['final_start_datetime_local']}")
        print(f"   종료: {data['final_end_datetime_local']}")

        print(f"\n🔗 캘린더 링크:")
        print(f"   Google Calendar: {data['google_calendar_url'][:100]}...")
        print(f"   .ics 다운로드: {data['ics_download_url']}")
else:
    print(f"   ❌ 에러: {response.text}")

# 5. .ics 파일 다운로드 테스트
print("\n5️⃣ .ics 파일 다운로드 테스트")
print("="*70)

ics_response = requests.get(f"{BASE_URL}/api/v1/events/{event.id}/calendar.ics")
print(f"상태 코드: {ics_response.status_code}")

if ics_response.status_code == 200:
    print(f"Content-Type: {ics_response.headers.get('Content-Type')}")
    print(f"Content-Disposition: {ics_response.headers.get('Content-Disposition')}")

    print(f"\n📄 .ics 파일 내용 (처음 500자):")
    print("="*70)
    print(ics_response.text[:500])
    print("="*70)
else:
    print(f"   ❌ 에러: {ics_response.text}")

# 6. 전체 JSON 응답 출력
print("\n6️⃣ 전체 응답 데이터 (JSON)")
print("="*70)
print(json.dumps(data, indent=2, ensure_ascii=False))
print("="*70)

# 정리
print("\n🧹 테스트 데이터 정리 중...")
event.delete()
user.delete()
print("✅ 정리 완료\n")

print("="*70)
print("✅ 캘린더 내보내기 테스트 완료!")
print("="*70)
print("\n📝 사용 방법:")
print("   1. GET /api/v1/events/{event_id}/calendar-export")
print("      → Google Calendar URL과 .ics 다운로드 URL 조회")
print("   2. GET /api/v1/events/{event_id}/calendar.ics")
print("      → .ics 파일 직접 다운로드")
print("\n💡 프론트엔드 구현:")
print("   - Google Calendar 버튼: google_calendar_url을 새 창에서 열기")
print("   - 캘린더 다운로드 버튼: ics_download_url로 파일 다운로드")
print("="*70)
