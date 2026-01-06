#!/usr/bin/env python3
import requests
import json

AUTH_BASE_URL = "http://127.0.0.1:8000/api/v1/auth"
EVENTS_BASE_URL = "http://127.0.0.1:8000/api/v1/events"

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
# Phase 3: Event Participation Tests
# ============================================================

# Note: You need to create an event first via admin panel or Django shell
# For testing, we'll use a sample slug. Replace with actual event slug.
TEST_EVENT_SLUG = "test-event-12345678"

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
