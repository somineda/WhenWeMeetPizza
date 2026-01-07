#!/usr/bin/env python3
import requests
import json

AUTH_BASE_URL = "http://127.0.0.1:8000/api/v1/auth"
EVENTS_BASE_URL = "http://127.0.0.1:8000/api/v1/events"

print("=" * 50)
print("EVENT CREATION API TESTS")
print("=" * 50)

# Test 1: Register with Nickname
print("=" * 50)
print("Testing Registration with Nickname...")
print("=" * 50)
response = requests.post(
    f"{AUTH_BASE_URL}/register/",
    json={
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "password2": "SecurePass123!",
        "nickname": "테스트유저"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

access_token = None
if response.status_code == 201:
    access_token = response.json()['tokens']['access']

    # Test 2: Get Profile
    print("\n" + "=" * 50)
    print("Testing Get Profile...")
    print("=" * 50)
    response = requests.get(
        f"{AUTH_BASE_URL}/profile/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # Test 3: Update Profile
    print("\n" + "=" * 50)
    print("Testing Update Profile...")
    print("=" * 50)
    response = requests.patch(
        f"{AUTH_BASE_URL}/profile/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"nickname": "업데이트된닉네임"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 4: Login
print("\n" + "=" * 50)
print("Testing Login...")
print("=" * 50)
response = requests.post(
    f"{AUTH_BASE_URL}/login/",
    json={
        "email": "testuser@example.com",
        "password": "SecurePass123!"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if response.status_code == 200:
    access_token = response.json()['tokens']['access']

# ============================================================
# Event Creation Tests
# ============================================================

# Test Event-1: Create Event (Authenticated)
if access_token:
    print("\n" + "=" * 50)
    print("Testing Create Event (Authenticated)...")
    print("=" * 50)
    response = requests.post(
        f"{EVENTS_BASE_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "12월 피자모임",
            "description": "12월 피자모임은 언제 하나요?",
            "date_start": "2025-12-25",
            "date_end": "2025-12-30",
            "time_start": "09:00",
            "time_end": "23:00",
            "timezone": "Asia/Seoul",
            "deadline_at": "2025-12-30T23:59:00+09:00"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    created_event_slug = None
    if response.status_code == 201:
        created_event_slug = response.json().get('slug')
        print(f"✓ Event created with slug: {created_event_slug}")

# Test Event-2: Create Event without auth (should fail)
print("\n" + "=" * 50)
print("Testing Create Event without Auth (should fail)...")
print("=" * 50)
response = requests.post(
    f"{EVENTS_BASE_URL}/",
    json={
        "title": "Unauthorized Event",
        "date_start": "2025-12-25",
        "date_end": "2025-12-30",
        "time_start": "09:00",
        "time_end": "23:00",
        "timezone": "Asia/Seoul",
        "deadline_at": "2025-12-30T23:59:00+09:00"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test Event-3: Create Event with invalid dates (end before start)
if access_token:
    print("\n" + "=" * 50)
    print("Testing Create Event with invalid dates (should fail)...")
    print("=" * 50)
    response = requests.post(
        f"{EVENTS_BASE_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "Invalid Date Event",
            "date_start": "2025-12-30",
            "date_end": "2025-12-25",  # End before start
            "time_start": "09:00",
            "time_end": "23:00",
            "timezone": "Asia/Seoul",
            "deadline_at": "2025-12-30T23:59:00+09:00"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# ============================================================
# Phase 3: Event Participation Tests
# ============================================================

# Use the created event slug from Event Creation test
TEST_EVENT_SLUG = created_event_slug if created_event_slug else "test-event-12345678"
print(f"\nUsing event slug for participation tests: {TEST_EVENT_SLUG}")

# Test 5: Join Event as Anonymous User without email (should fail)
print("\n" + "=" * 50)
print("Testing Join Event (Anonymous without email - should fail)...")
print("=" * 50)
response = requests.post(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
    json={
        "nickname": "여우리더"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 5-2: Join Event as Anonymous User with email
print("\n" + "=" * 50)
print("Testing Join Event (Anonymous with email)...")
print("=" * 50)
ANONYMOUS_EMAIL = "anonymous@example.com"
response = requests.post(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
    json={
        "nickname": "익명여우리더",
        "email": ANONYMOUS_EMAIL
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
anonymous_participant_id = None
if response.status_code == 200:
    anonymous_participant_id = response.json().get('participant_id')

# Test 6: Join Event with Duplicate Nickname (should fail)
print("\n" + "=" * 50)
print("Testing Join Event with Duplicate Nickname...")
print("=" * 50)
response = requests.post(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
    json={
        "nickname": "익명여우리더",  # Same as Test 5-2
        "email": "another@example.com"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 7: Join Event as Logged-in User with same email (auto-link test)
logged_in_participant_id = None
if access_token:
    print("\n" + "=" * 50)
    print("Testing Join Event (Authenticated with same email - auto-link)...")
    print("=" * 50)
    response = requests.post(
        f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "nickname": "로그인후연결된닉네임",
            "email": ANONYMOUS_EMAIL  # Same email as anonymous participant
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    if response.status_code == 200:
        logged_in_participant_id = response.json().get('participant_id')
        # Check if it's the same participant_id as anonymous one (auto-linked)
        if logged_in_participant_id == anonymous_participant_id:
            print("✓ Successfully auto-linked to existing anonymous participant!")

# Test 7-2: Join Event as Logged-in User with different email
if access_token:
    print("\n" + "=" * 50)
    print("Testing Join Event (Authenticated with different email)...")
    print("=" * 50)
    response = requests.post(
        f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "nickname": "새로운참가자",
            "email": "newuser@example.com"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 8: Join Event with Empty Nickname (should fail)
print("\n" + "=" * 50)
print("Testing Join Event with Empty Nickname...")
print("=" * 50)
response = requests.post(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
    json={
        "nickname": "",
        "email": "empty@example.com"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 9: Get Participant List (Authenticated, requires login)
if access_token:
    print("\n" + "=" * 50)
    print("Testing Get Participant List (Authenticated)...")
    print("=" * 50)
    # Assuming event_id is 1 (the test event we created)
    TEST_EVENT_ID = 1
    response = requests.get(
        f"{EVENTS_BASE_URL}/{TEST_EVENT_ID}/participants",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # Test 10: Get Participant List with Pagination
    print("\n" + "=" * 50)
    print("Testing Get Participant List with Pagination...")
    print("=" * 50)
    response = requests.get(
        f"{EVENTS_BASE_URL}/{TEST_EVENT_ID}/participants?page=1&size=10",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 11: Get Participant List without Authentication (should fail)
print("\n" + "=" * 50)
print("Testing Get Participant List without Auth (should fail)...")
print("=" * 50)
TEST_EVENT_ID = 1
response = requests.get(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_ID}/participants"
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 12: Delete Participant (Auto-linked participant - should succeed)
if access_token and logged_in_participant_id:
    print("\n" + "=" * 50)
    print("Testing Delete Auto-linked Participant (Self)...")
    print("=" * 50)
    print(f"Attempting to delete participant_id: {logged_in_participant_id}")
    response = requests.delete(
        f"http://127.0.0.1:8000/api/v1/participants/{logged_in_participant_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("Response: Successfully deleted (204 No Content)")
        print("✓ Auto-linked participant can be deleted by the user!")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 13: Create another anonymous participant for deletion tests
print("\n" + "=" * 50)
print("Creating another anonymous participant for deletion tests...")
print("=" * 50)
response = requests.post(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
    json={
        "nickname": "또다른익명참가자",
        "email": "another-anonymous@example.com"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
another_anonymous_id = None
if response.status_code == 200:
    another_anonymous_id = response.json().get('participant_id')

# Test 14: Delete Participant without Authentication (should fail)
if another_anonymous_id:
    print("\n" + "=" * 50)
    print("Testing Delete Participant without Auth (should fail)...")
    print("=" * 50)
    response = requests.delete(
        f"http://127.0.0.1:8000/api/v1/participants/{another_anonymous_id}"
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 15: Try to delete other's participant without permission (should fail)
if access_token and another_anonymous_id:
    print("\n" + "=" * 50)
    print("Testing Delete Other's Participant without Permission (should fail)...")
    print("=" * 50)
    # 다른 익명 참가자를 삭제하려고 시도 (권한 없음 - user가 None이므로)
    response = requests.delete(
        f"http://127.0.0.1:8000/api/v1/participants/{another_anonymous_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# ============================================================
# Phase 4: Event Detail API Tests
# ============================================================

# Test 16: Get Event Detail (without authentication)
print("\n" + "=" * 50)
print("Testing Get Event Detail (No Auth)...")
print("=" * 50)
response = requests.get(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/"
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 17: Get Event Detail with Authentication
if access_token:
    print("\n" + "=" * 50)
    print("Testing Get Event Detail (With Auth)...")
    print("=" * 50)
    response = requests.get(
        f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 18: Get Non-existent Event Detail (should fail with 404)
print("\n" + "=" * 50)
print("Testing Get Non-existent Event Detail (should fail)...")
print("=" * 50)
response = requests.get(
    f"{EVENTS_BASE_URL}/nonexistent-event-slug/"
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# ============================================================
# Phase 5: Submit Availability API Tests
# ============================================================

# Test 19: Get time slots from event detail
print("\n" + "=" * 50)
print("Getting time slots from event detail...")
print("=" * 50)
response = requests.get(f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/")
time_slots = []
test_participant_id = None

if response.status_code == 200:
    event_data = response.json()
    time_slots = event_data.get('slots', [])
    print(f"Total time slots: {len(time_slots)}")
    if time_slots:
        print(f"First slot: {time_slots[0]}")
        print(f"Last slot: {time_slots[-1]}")

# Test 20: Create a new participant for availability tests
print("\n" + "=" * 50)
print("Creating a participant for availability tests...")
print("=" * 50)
response = requests.post(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
    json={
        "nickname": "가능시간제출테스트참가자",
        "email": "availability-test@example.com"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
if response.status_code == 200:
    test_participant_id = response.json().get('participant_id')
    print(f"Created participant_id: {test_participant_id}")

# Test 21: Submit availability for participant (select first 5 slots)
if test_participant_id and time_slots:
    print("\n" + "=" * 50)
    print("Testing Submit Availability (first 5 slots)...")
    print("=" * 50)
    available_slot_ids = [slot['slot_id'] for slot in time_slots[:5]]
    print(f"Submitting slots: {available_slot_ids}")

    response = requests.post(
        f"http://127.0.0.1:8000/api/v1/participants/{test_participant_id}/availabilities/",
        json={
            "available_slot_ids": available_slot_ids
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 22: Update availability (change to different slots)
if test_participant_id and time_slots and len(time_slots) >= 10:
    print("\n" + "=" * 50)
    print("Testing Update Availability (different slots)...")
    print("=" * 50)
    available_slot_ids = [slot['slot_id'] for slot in time_slots[5:10]]
    print(f"Updating to slots: {available_slot_ids}")

    response = requests.post(
        f"http://127.0.0.1:8000/api/v1/participants/{test_participant_id}/availabilities/",
        json={
            "available_slot_ids": available_slot_ids
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 23: Submit empty availability (clear all)
if test_participant_id:
    print("\n" + "=" * 50)
    print("Testing Submit Empty Availability (clear all)...")
    print("=" * 50)

    response = requests.post(
        f"http://127.0.0.1:8000/api/v1/participants/{test_participant_id}/availabilities/",
        json={
            "available_slot_ids": []
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 24: Submit availability with invalid slot IDs (should fail)
if test_participant_id:
    print("\n" + "=" * 50)
    print("Testing Submit Availability with Invalid Slot IDs (should fail)...")
    print("=" * 50)

    response = requests.post(
        f"http://127.0.0.1:8000/api/v1/participants/{test_participant_id}/availabilities/",
        json={
            "available_slot_ids": [99999, 88888]  # Invalid slot IDs
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 25: Verify event detail shows updated available_count
if test_participant_id and time_slots:
    print("\n" + "=" * 50)
    print("Submitting availability for multiple participants...")
    print("=" * 50)

    # Create another participant
    response = requests.post(
        f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
        json={
            "nickname": "두번째참가자",
            "email": "second-participant@example.com"
        }
    )
    second_participant_id = None
    if response.status_code == 200:
        second_participant_id = response.json().get('participant_id')
        print(f"Created second participant_id: {second_participant_id}")

        # Submit availability for both participants (same slots)
        same_slots = [slot['slot_id'] for slot in time_slots[:3]]

        # First participant
        requests.post(
            f"http://127.0.0.1:8000/api/v1/participants/{test_participant_id}/availabilities/",
            json={"available_slot_ids": same_slots}
        )

        # Second participant
        requests.post(
            f"http://127.0.0.1:8000/api/v1/participants/{second_participant_id}/availabilities/",
            json={"available_slot_ids": same_slots}
        )

        print(f"Both participants submitted availability for slots: {same_slots}")

        # Check event detail
        print("\n" + "=" * 50)
        print("Verifying Event Detail shows correct available_count...")
        print("=" * 50)
        response = requests.get(f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/")
        if response.status_code == 200:
            event_data = response.json()
            print(f"Total participants: {event_data.get('participants_count')}")
            print(f"First 5 slots with available_count:")
            for slot in event_data.get('slots', [])[:5]:
                print(f"  Slot {slot['slot_id']} ({slot['date']} {slot['start_time']}-{slot['end_time']}): {slot['available_count']}/{slot['total_participants']} available")
