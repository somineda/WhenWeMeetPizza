#!/usr/bin/env python3
"""
참가자 가능 시간 조회 API 테스트
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"
AUTH_BASE_URL = f"{BASE_URL}/auth"
EVENTS_BASE_URL = f"{BASE_URL}/events"
PARTICIPANTS_BASE_URL = f"{BASE_URL}/participants"

print("=" * 60)
print("참가자 가능 시간 조회 API 테스트")
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
    exit(1)

access_token = response.json()['tokens']['access']
print("✓ 로그인 성공")

# 2. 이벤트 생성
print("\n[2] 테스트 이벤트 생성...")
response = requests.post(
    f"{EVENTS_BASE_URL}/",
    headers={"Authorization": f"Bearer {access_token}"},
    json={
        "title": "가능 시간 조회 테스트",
        "date_start": "2026-01-15",
        "date_end": "2026-01-15",
        "time_start": "10:00",
        "time_end": "12:00",
        "timezone": "Asia/Seoul"
    }
)

if response.status_code != 201:
    print(f"❌ 이벤트 생성 실패: {response.status_code}")
    exit(1)

event_data = response.json()
event_id = event_data['id']
event_slug = event_data['slug']
print(f"✓ 이벤트 생성 성공 (ID: {event_id})")

# 3. 참가자 추가
print("\n[3] 참가자 추가...")
response = requests.post(
    f"{EVENTS_BASE_URL}/{event_slug}/participants/",
    json={
        "nickname": "조회테스트참가자",
        "email": "retrieve-test@example.com"
    }
)

if response.status_code != 200:
    print(f"❌ 참가자 추가 실패: {response.status_code}")
    exit(1)

participant_id = response.json()['participant_id']
print(f"✓ 참가자 추가 성공 (ID: {participant_id})")

# 4. 타임슬롯 조회
print("\n[4] 타임슬롯 조회...")
response = requests.get(f"{EVENTS_BASE_URL}/{event_slug}/")
if response.status_code != 200:
    print(f"❌ 타임슬롯 조회 실패: {response.status_code}")
    exit(1)

slots = response.json()['slots']
all_slot_ids = [slot['slot_id'] for slot in slots]
print(f"✓ 타임슬롯 조회 성공 (총 {len(all_slot_ids)}개)")

# 5. 가능 시간 저장 (슬롯 1, 3, 5 선택)
print("\n[5] 가능 시간 저장 (슬롯 1, 3, 5)...")
selected_slot_ids = [all_slot_ids[0], all_slot_ids[2], all_slot_ids[4]] if len(all_slot_ids) >= 5 else all_slot_ids[:3]
response = requests.post(
    f"{PARTICIPANTS_BASE_URL}/{participant_id}/availabilities/",
    json={"available_slot_ids": selected_slot_ids}
)

if response.status_code != 200:
    print(f"❌ 가능 시간 저장 실패: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

print(f"✓ 가능 시간 저장 성공")
print(f"  저장된 슬롯 ID: {selected_slot_ids}")

# 6. 가능 시간 조회 (핵심 테스트!)
print("\n[6] 가능 시간 조회...")
response = requests.get(f"{PARTICIPANTS_BASE_URL}/{participant_id}/availabilities/")

if response.status_code != 200:
    print(f"❌ 가능 시간 조회 실패: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

availability_data = response.json()
print("✓ 가능 시간 조회 성공")
print(f"  참가자 ID: {availability_data['participant_id']}")
print(f"  참가자 닉네임: {availability_data['participant_nickname']}")
print(f"  이벤트 ID: {availability_data['event_id']}")
print(f"  가능한 슬롯 ID: {availability_data['available_slot_ids']}")
print(f"  총 가능 시간대: {availability_data['total_available']}개")

# 7. 검증: 저장한 슬롯과 조회한 슬롯이 일치하는지 확인
print("\n[7] 데이터 일치성 검증...")
retrieved_slot_ids = set(availability_data['available_slot_ids'])
expected_slot_ids = set(selected_slot_ids)

if retrieved_slot_ids == expected_slot_ids:
    print("✅ 저장된 데이터와 조회된 데이터가 일치합니다!")
else:
    print("❌ 데이터 불일치!")
    print(f"  예상: {expected_slot_ids}")
    print(f"  실제: {retrieved_slot_ids}")

# 8. 가능 시간 업데이트 (슬롯 2, 4만 선택)
print("\n[8] 가능 시간 업데이트 (슬롯 2, 4)...")
updated_slot_ids = [all_slot_ids[1], all_slot_ids[3]] if len(all_slot_ids) >= 4 else all_slot_ids[:2]
response = requests.post(
    f"{PARTICIPANTS_BASE_URL}/{participant_id}/availabilities/",
    json={"available_slot_ids": updated_slot_ids}
)

if response.status_code != 200:
    print(f"❌ 가능 시간 업데이트 실패: {response.status_code}")
    exit(1)

print(f"✓ 가능 시간 업데이트 성공")
print(f"  업데이트된 슬롯 ID: {updated_slot_ids}")

# 9. 업데이트 후 다시 조회
print("\n[9] 업데이트 후 재조회...")
response = requests.get(f"{PARTICIPANTS_BASE_URL}/{participant_id}/availabilities/")

if response.status_code != 200:
    print(f"❌ 재조회 실패: {response.status_code}")
    exit(1)

availability_data = response.json()
print("✓ 재조회 성공")
print(f"  가능한 슬롯 ID: {availability_data['available_slot_ids']}")
print(f"  총 가능 시간대: {availability_data['total_available']}개")

# 10. 검증: 업데이트된 데이터 확인
print("\n[10] 업데이트 데이터 일치성 검증...")
retrieved_slot_ids = set(availability_data['available_slot_ids'])
expected_slot_ids = set(updated_slot_ids)

if retrieved_slot_ids == expected_slot_ids:
    print("✅ 업데이트된 데이터가 정확히 조회됩니다!")
else:
    print("❌ 업데이트 후 데이터 불일치!")
    print(f"  예상: {expected_slot_ids}")
    print(f"  실제: {retrieved_slot_ids}")

# 11. 빈 슬롯 저장 후 조회
print("\n[11] 모든 가능 시간 삭제 (빈 배열 저장)...")
response = requests.post(
    f"{PARTICIPANTS_BASE_URL}/{participant_id}/availabilities/",
    json={"available_slot_ids": []}
)

if response.status_code != 200:
    print(f"❌ 빈 배열 저장 실패: {response.status_code}")
    exit(1)

print("✓ 빈 배열 저장 성공")

response = requests.get(f"{PARTICIPANTS_BASE_URL}/{participant_id}/availabilities/")
availability_data = response.json()
print(f"  조회 결과: {availability_data['available_slot_ids']}")
print(f"  총 가능 시간대: {availability_data['total_available']}개")

if len(availability_data['available_slot_ids']) == 0:
    print("✅ 빈 배열이 정확히 저장/조회됩니다!")
else:
    print("❌ 빈 배열 처리 실패!")

# 12. 존재하지 않는 참가자 조회
print("\n[12] 존재하지 않는 참가자 조회 (404 예상)...")
response = requests.get(f"{PARTICIPANTS_BASE_URL}/999999/availabilities/")
print(f"Status: {response.status_code}")

if response.status_code == 404:
    print("✅ 존재하지 않는 참가자에 대해 404 반환")
else:
    print(f"⚠ 예상과 다른 상태 코드: {response.status_code}")

print("\n" + "=" * 60)
print("모든 테스트 완료!")
print("=" * 60)
