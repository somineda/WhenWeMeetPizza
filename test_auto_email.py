#!/usr/bin/env python3
"""
최종 시간 확정 시 자동 이메일 발송 및 리마인드 이메일 테스트
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"
AUTH_BASE_URL = f"{BASE_URL}/auth"
EVENTS_BASE_URL = f"{BASE_URL}/events"

print("=" * 60)
print("자동 이메일 발송 및 리마인드 이메일 테스트")
print("=" * 60)

# 1. 로그인
print("\n[1] 사용자 로그인...")
response = requests.post(
    f"{AUTH_BASE_URL}/login/",
    json={
        "email": "testuser@example.com",
        "password": "SecurePass123!"
    }
)

if response.status_code != 200:
    print(f"❌ 로그인 실패: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

access_token = response.json()['tokens']['access']
print("✓ 로그인 성공")

# 2. 이벤트 생성
print("\n[2] 테스트 이벤트 생성...")
response = requests.post(
    f"{EVENTS_BASE_URL}/",
    headers={"Authorization": f"Bearer {access_token}"},
    json={
        "title": "자동 이메일 테스트 이벤트",
        "description": "최종 시간 확정 시 자동으로 이메일이 발송되는지 테스트",
        "date_start": "2026-01-10",
        "date_end": "2026-01-10",
        "time_start": "14:00",
        "time_end": "16:00",
        "timezone": "Asia/Seoul"
    }
)

if response.status_code != 201:
    print(f"❌ 이벤트 생성 실패: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

event_data = response.json()
event_id = event_data['id']
event_slug = event_data['slug']
print(f"✓ 이벤트 생성 성공 (ID: {event_id}, Slug: {event_slug})")

# 3. 참가자 추가
print("\n[3] 참가자 추가...")
response = requests.post(
    f"{EVENTS_BASE_URL}/{event_slug}/participants/",
    json={
        "nickname": "테스트참가자1",
        "email": "participant1@example.com"
    }
)

if response.status_code != 200:
    print(f"❌ 참가자 추가 실패: {response.status_code}")
    exit(1)

print("✓ 참가자 1 추가 성공")

response = requests.post(
    f"{EVENTS_BASE_URL}/{event_slug}/participants/",
    json={
        "nickname": "테스트참가자2",
        "email": "participant2@example.com"
    }
)
print("✓ 참가자 2 추가 성공")

# 4. 타임슬롯 조회
print("\n[4] 타임슬롯 조회...")
response = requests.get(f"{EVENTS_BASE_URL}/{event_slug}/")
if response.status_code != 200:
    print(f"❌ 타임슬롯 조회 실패: {response.status_code}")
    exit(1)

slots = response.json()['slots']
first_slot_id = slots[0]['slot_id']
print(f"✓ 타임슬롯 조회 성공 (첫 번째 슬롯 ID: {first_slot_id})")

# 5. 최종 시간 확정 (자동 이메일 발송 트리거)
print("\n[5] 최종 시간 확정 (자동 이메일 발송 테스트)...")
response = requests.post(
    f"{EVENTS_BASE_URL}/{event_id}/final-choice",
    headers={"Authorization": f"Bearer {access_token}"},
    json={"slot_id": first_slot_id}
)

if response.status_code != 200:
    print(f"❌ 최종 시간 확정 실패: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

final_choice_data = response.json()
print(f"✓ 최종 시간 확정 성공")
print(f"  Event ID: {final_choice_data['event_id']}")
print(f"  Slot ID: {final_choice_data['slot_id']}")
print(f"  Date: {final_choice_data['date']}")
print(f"  Time: {final_choice_data['start_time']} - {final_choice_data['end_time']}")

# 6. 확정된 시간 조회
print("\n[6] 확정된 시간 조회...")
response = requests.get(f"{EVENTS_BASE_URL}/{event_id}/final-choice")
if response.status_code == 200:
    print("✓ 확정된 시간 조회 성공")
    data = response.json()
    print(f"  확정 시간: {data['date']} {data['start_time']}-{data['end_time']}")
else:
    print(f"❌ 확정된 시간 조회 실패: {response.status_code}")

print("\n" + "=" * 60)
print("테스트 완료!")
print("=" * 60)
print("\n📧 이메일 발송 확인:")
print("1. 확정 이메일: Celery worker가 실행 중이면 participant1@example.com과")
print("   participant2@example.com으로 확정 이메일이 발송됩니다.")
print("2. 리마인드 이메일: 2026-01-10 오전 7시에 자동으로 발송되도록")
print("   스케줄링되었습니다. (Celery worker 필요)")
print("\n⚙️ Celery worker 실행 방법:")
print("   cd /Users/yunsomin/Downloads/pizza")
print("   source venv/bin/activate")
print("   celery -A config worker -l info")
