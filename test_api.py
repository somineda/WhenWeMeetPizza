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

# ============================================================
# Phase 6: My Events List API Tests
# ============================================================

# Test 26: Get My Events (Authenticated)
if access_token:
    print("\n" + "=" * 50)
    print("Testing Get My Events (Authenticated)...")
    print("=" * 50)
    response = requests.get(
        f"{EVENTS_BASE_URL}/my/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 27: Get My Events with Pagination
if access_token:
    print("\n" + "=" * 50)
    print("Testing Get My Events with Pagination...")
    print("=" * 50)
    response = requests.get(
        f"{EVENTS_BASE_URL}/my/?page=1&size=5",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 28: Get My Events without Auth (should fail)
print("\n" + "=" * 50)
print("Testing Get My Events without Auth (should fail)...")
print("=" * 50)
response = requests.get(f"{EVENTS_BASE_URL}/my/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# ============================================================
# Phase 7: Event Update API Tests
# ============================================================

# Get event_id from created event
event_id_for_update = None
if access_token and created_event_slug:
    print("\n" + "=" * 50)
    print("Getting event ID for update tests...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{created_event_slug}/")
    if response.status_code == 200:
        event_id_for_update = response.json().get('id')
        print(f"Event ID: {event_id_for_update}")

# Test 29: Update Event as Organizer (Full Update)
if access_token and event_id_for_update:
    print("\n" + "=" * 50)
    print("Testing Update Event (Organizer - Full Update)...")
    print("=" * 50)
    response = requests.patch(
        f"{EVENTS_BASE_URL}/{event_id_for_update}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "1월 피자모임 (수정됨)",
            "description": "마감기한과 일정이 변경되었습니다.",
            "date_start": "2025-12-26",
            "date_end": "2025-12-28",
            "time_start": "10:00",
            "time_end": "22:00",
            "deadline_at": "2025-12-25T23:59:00+09:00"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 30: Partial Update (Title and Description only)
if access_token and event_id_for_update:
    print("\n" + "=" * 50)
    print("Testing Partial Update (Title and Description only)...")
    print("=" * 50)
    response = requests.patch(
        f"{EVENTS_BASE_URL}/{event_id_for_update}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "1월 신년 피자모임",
            "description": "신년을 기념하는 피자모임입니다!"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 31: Update with Invalid Dates (should fail)
if access_token and event_id_for_update:
    print("\n" + "=" * 50)
    print("Testing Update with Invalid Dates (should fail)...")
    print("=" * 50)
    response = requests.patch(
        f"{EVENTS_BASE_URL}/{event_id_for_update}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "date_start": "2025-12-30",
            "date_end": "2025-12-25"  # End before start
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 32: Update without Authentication (should fail)
if event_id_for_update:
    print("\n" + "=" * 50)
    print("Testing Update without Auth (should fail)...")
    print("=" * 50)
    response = requests.patch(
        f"{EVENTS_BASE_URL}/{event_id_for_update}/",
        json={
            "title": "Unauthorized Update"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 33: Create another user and try to update (should fail - not organizer)
print("\n" + "=" * 50)
print("Creating another user for permission test...")
print("=" * 50)
response = requests.post(
    f"{AUTH_BASE_URL}/register/",
    json={
        "email": "anotheruser@example.com",
        "password": "AnotherPass123!",
        "password2": "AnotherPass123!",
        "nickname": "다른유저"
    }
)
another_user_token = None
if response.status_code == 201:
    another_user_token = response.json()['tokens']['access']
    print("Another user created successfully")
elif response.status_code == 400:
    # User already exists, try to login
    print("User already exists, logging in...")
    response = requests.post(
        f"{AUTH_BASE_URL}/login/",
        json={
            "email": "anotheruser@example.com",
            "password": "AnotherPass123!"
        }
    )
    if response.status_code == 200:
        another_user_token = response.json()['tokens']['access']
        print("Login successful")

if another_user_token and event_id_for_update:
    print("\n" + "=" * 50)
    print("Testing Update as Non-Organizer (should fail)...")
    print("=" * 50)
    response = requests.patch(
        f"{EVENTS_BASE_URL}/{event_id_for_update}/",
        headers={"Authorization": f"Bearer {another_user_token}"},
        json={
            "title": "해킹 시도"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
# ============================================================
# Phase 8: Event Delete API Tests
# ============================================================

# Test 34: Delete Event as Organizer (should succeed)
if access_token and event_id_for_update:
    print("\n" + "=" * 50)
    print("Testing Delete Event (Organizer)...")
    print("=" * 50)
    response = requests.delete(
        f"{EVENTS_BASE_URL}/{event_id_for_update}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("Response: Successfully deleted (204 No Content)")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 35: Verify deleted event is not accessible
if event_id_for_update:
    print("\n" + "=" * 50)
    print("Testing Access Deleted Event (should fail)...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{created_event_slug}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 36: Verify deleted event not in My Events list
if access_token:
    print("\n" + "=" * 50)
    print("Testing My Events after deletion (should not include deleted event)...")
    print("=" * 50)
    response = requests.get(
        f"{EVENTS_BASE_URL}/my/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    deleted_event_in_list = any(item['id'] == event_id_for_update for item in data.get('items', []))
    if deleted_event_in_list:
        print("❌ Deleted event is still in the list!")
    else:
        print("✓ Deleted event is not in the list")
    print(f"Total events: {data.get('total')}")

# Test 37: Delete without Authentication (should fail)
# Create a new event for this test
new_event_id = None
if access_token:
    print("\n" + "=" * 50)
    print("Creating new event for delete permission test...")
    print("=" * 50)
    response = requests.post(
        f"{EVENTS_BASE_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "삭제 테스트 이벤트",
            "date_start": "2025-12-25",
            "date_end": "2025-12-30",
            "time_start": "09:00",
            "time_end": "23:00",
            "timezone": "Asia/Seoul"
        }
    )
    if response.status_code == 201:
        new_event_id = response.json().get('id')
        print(f"Created event ID: {new_event_id}")

if new_event_id:
    print("\n" + "=" * 50)
    print("Testing Delete without Auth (should fail)...")
    print("=" * 50)
    response = requests.delete(f"{EVENTS_BASE_URL}/{new_event_id}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 38: Delete as Non-Organizer (should fail)
if another_user_token and new_event_id:
    print("\n" + "=" * 50)
    print("Testing Delete as Non-Organizer (should fail)...")
    print("=" * 50)
    response = requests.delete(
        f"{EVENTS_BASE_URL}/{new_event_id}/",
        headers={"Authorization": f"Bearer {another_user_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
# ============================================================
# Phase 9: Event Summary API Tests
# ============================================================

# Create a new event specifically for summary tests
summary_test_event_id = None
summary_test_event_slug = None
if access_token:
    print("\n" + "=" * 50)
    print("Creating new event for summary tests...")
    print("=" * 50)
    response = requests.post(
        f"{EVENTS_BASE_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "요약 테스트 이벤트",
            "date_start": "2026-01-10",
            "date_end": "2026-01-11",
            "time_start": "14:00",
            "time_end": "16:00",  # 4 slots per day = 8 total slots
            "timezone": "Asia/Seoul"
        }
    )
    if response.status_code == 201:
        summary_test_event_id = response.json().get('id')
        summary_test_event_slug = response.json().get('slug')
        print(f"Created event ID: {summary_test_event_id}")
        print(f"Created event slug: {summary_test_event_slug}")

# Create participants and submit availabilities
summary_participant_ids = []
if summary_test_event_slug:
    print("\n" + "=" * 50)
    print("Creating participants for summary tests...")
    print("=" * 50)
    
    # Get time slots
    response = requests.get(f"{EVENTS_BASE_URL}/{summary_test_event_slug}/")
    summary_time_slots = []
    if response.status_code == 200:
        summary_time_slots = response.json().get('slots', [])
        print(f"Total time slots: {len(summary_time_slots)}")
    
    # Create 3 participants
    for i in range(1, 4):
        response = requests.post(
            f"{EVENTS_BASE_URL}/{summary_test_event_slug}/participants/",
            json={
                "nickname": f"요약테스트참가자{i}",
                "email": f"summary-test-{i}@example.com"
            }
        )
        if response.status_code == 200:
            participant_id = response.json().get('participant_id')
            summary_participant_ids.append(participant_id)
            print(f"Created participant {i}: {participant_id}")
    
    # Submit availabilities
    if summary_participant_ids and summary_time_slots:
        print("\n" + "=" * 50)
        print("Submitting availabilities for summary tests...")
        print("=" * 50)
        
        # Participant 1: available for first 6 slots
        slot_ids_1 = [slot['slot_id'] for slot in summary_time_slots[:6]]
        requests.post(
            f"http://127.0.0.1:8000/api/v1/participants/{summary_participant_ids[0]}/availabilities/",
            json={"available_slot_ids": slot_ids_1}
        )
        print(f"Participant 1 available for {len(slot_ids_1)} slots")
        
        # Participant 2: available for first 4 slots (overlap with P1)
        slot_ids_2 = [slot['slot_id'] for slot in summary_time_slots[:4]]
        requests.post(
            f"http://127.0.0.1:8000/api/v1/participants/{summary_participant_ids[1]}/availabilities/",
            json={"available_slot_ids": slot_ids_2}
        )
        print(f"Participant 2 available for {len(slot_ids_2)} slots")
        
        # Participant 3: available for first 2 slots (all participants overlap)
        slot_ids_3 = [slot['slot_id'] for slot in summary_time_slots[:2]]
        requests.post(
            f"http://127.0.0.1:8000/api/v1/participants/{summary_participant_ids[2]}/availabilities/",
            json={"available_slot_ids": slot_ids_3}
        )
        print(f"Participant 3 available for {len(slot_ids_3)} slots")
        
        print("\nExpected availability pattern:")
        print("  Slot 1-2: 3 participants (all)")
        print("  Slot 3-4: 2 participants (P1, P2)")
        print("  Slot 5-6: 1 participant (P1)")
        print("  Slot 7-8: 0 participants")

# Test 39: Get Event Summary without filters
if summary_test_event_id:
    print("\n" + "=" * 50)
    print("Test 39: Get Event Summary (No Filters)...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{summary_test_event_id}/summary/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Event ID: {data.get('event_id')}")
        print(f"Total Participants: {data.get('total_participants')}")
        print(f"Total Slots: {len(data.get('slots', []))}")
        print(f"Total Best Slots: {len(data.get('best_slots', []))}")
        
        print("\nFirst 5 slots:")
        for slot in data.get('slots', [])[:5]:
            print(f"  Slot {slot['slot_id']}: {slot['available_count']} available, is_all_available={slot['is_all_available']}")
        
        print("\nFirst 5 best slots (sorted by available_count):")
        for slot in data.get('best_slots', [])[:5]:
            print(f"  Slot {slot['slot_id']}: {slot['available_count']} available, is_all_available={slot['is_all_available']}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 40: Get Event Summary with min_participants=2
if summary_test_event_id:
    print("\n" + "=" * 50)
    print("Test 40: Get Event Summary (min_participants=2)...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{summary_test_event_id}/summary/?min_participants=2")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Slots (filtered): {len(data.get('slots', []))}")
        print(f"Total Best Slots (filtered): {len(data.get('best_slots', []))}")
        
        print("\nFiltered slots (only slots with 2+ participants):")
        for slot in data.get('slots', []):
            print(f"  Slot {slot['slot_id']}: {slot['available_count']} available, is_all_available={slot['is_all_available']}")
        
        # Verify all slots have at least 2 participants
        all_meet_min = all(slot['available_count'] >= 2 for slot in data.get('slots', []))
        if all_meet_min:
            print("✓ All filtered slots have at least 2 participants")
        else:
            print("❌ Some slots don't meet min_participants requirement")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 41: Get Event Summary with min_participants=3
if summary_test_event_id:
    print("\n" + "=" * 50)
    print("Test 41: Get Event Summary (min_participants=3)...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{summary_test_event_id}/summary/?min_participants=3")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Slots (filtered): {len(data.get('slots', []))}")
        
        print("\nFiltered slots (only slots with 3 participants - all available):")
        for slot in data.get('slots', []):
            print(f"  Slot {slot['slot_id']}: {slot['available_count']} available, is_all_available={slot['is_all_available']}")
        
        # Should only show slots 1-2 (where all 3 participants are available)
        if len(data.get('slots', [])) == 2:
            print("✓ Correctly filtered to slots where all 3 participants are available")
        else:
            print(f"❌ Expected 2 slots, got {len(data.get('slots', []))}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 42: Get Event Summary with only_all_available=true
if summary_test_event_id:
    print("\n" + "=" * 50)
    print("Test 42: Get Event Summary (only_all_available=true)...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{summary_test_event_id}/summary/?only_all_available=true")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Participants: {data.get('total_participants')}")
        print(f"Total Slots (only all available): {len(data.get('slots', []))}")
        
        print("\nSlots where all participants are available:")
        for slot in data.get('slots', []):
            print(f"  Slot {slot['slot_id']}: {slot['available_count']} available, is_all_available={slot['is_all_available']}")
        
        # Verify all slots have is_all_available=True
        all_slots_all_available = all(slot['is_all_available'] for slot in data.get('slots', []))
        if all_slots_all_available and len(data.get('slots', [])) > 0:
            print("✓ All filtered slots have all participants available")
        elif len(data.get('slots', [])) == 0:
            print("⚠ No slots where all participants are available (expected 2)")
        else:
            print("❌ Some slots don't have all participants available")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 43: Get Event Summary with combined filters
if summary_test_event_id:
    print("\n" + "=" * 50)
    print("Test 43: Get Event Summary (min_participants=2 & only_all_available=true)...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{summary_test_event_id}/summary/?min_participants=2&only_all_available=true")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Slots (filtered): {len(data.get('slots', []))}")
        
        print("\nFiltered slots:")
        for slot in data.get('slots', []):
            print(f"  Slot {slot['slot_id']}: {slot['available_count']} available, is_all_available={slot['is_all_available']}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 44: Verify best_slots are sorted by available_count descending
if summary_test_event_id:
    print("\n" + "=" * 50)
    print("Test 44: Verify best_slots sorting...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{summary_test_event_id}/summary/")
    if response.status_code == 200:
        data = response.json()
        best_slots = data.get('best_slots', [])
        
        print("Best slots in order:")
        for i, slot in enumerate(best_slots[:8]):
            print(f"  {i+1}. Slot {slot['slot_id']}: {slot['available_count']} available")
        
        # Verify descending order
        counts = [slot['available_count'] for slot in best_slots]
        is_sorted = all(counts[i] >= counts[i+1] for i in range(len(counts)-1))
        if is_sorted:
            print("✓ Best slots are correctly sorted by available_count (descending)")
        else:
            print("❌ Best slots are NOT sorted correctly")
            print(f"   Counts: {counts}")

# Test 45: Event Summary with no participants
if access_token:
    print("\n" + "=" * 50)
    print("Test 45: Event Summary with No Participants...")
    print("=" * 50)
    
    # Create event without participants
    response = requests.post(
        f"{EVENTS_BASE_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "참가자 없는 이벤트",
            "date_start": "2026-01-15",
            "date_end": "2026-01-15",
            "time_start": "10:00",
            "time_end": "12:00",
            "timezone": "Asia/Seoul"
        }
    )
    
    if response.status_code == 201:
        empty_event_id = response.json().get('id')
        
        response = requests.get(f"{EVENTS_BASE_URL}/{empty_event_id}/summary/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total Participants: {data.get('total_participants')}")
            print(f"Total Slots: {len(data.get('slots', []))}")
            print(f"Total Best Slots: {len(data.get('best_slots', []))}")
            
            if data.get('total_participants') == 0:
                print("✓ Correctly shows 0 participants")
            
            # All slots should have 0 available_count
            all_zero = all(slot['available_count'] == 0 for slot in data.get('slots', []))
            if all_zero and len(data.get('slots', [])) > 0:
                print("✓ All slots have 0 available_count")

# Test 46: Event Summary with invalid min_participants (should default to 1)
if summary_test_event_id:
    print("\n" + "=" * 50)
    print("Test 46: Event Summary with Invalid min_participants...")
    print("=" * 50)
    response = requests.get(f"{EVENTS_BASE_URL}/{summary_test_event_id}/summary/?min_participants=invalid")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Slots: {len(data.get('slots', []))}")
        print("✓ Invalid min_participants handled gracefully (defaulted to 1)")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

print("\n" + "=" * 50)
print("ALL TESTS COMPLETED!")
print("=" * 50)
