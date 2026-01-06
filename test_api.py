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

# Test 5: Join Event as Anonymous User (without auth)
print("\n" + "=" * 50)
print("Testing Join Event (Anonymous)...")
print("=" * 50)
response = requests.post(
    f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
    json={
        "nickname": "여우리더",
        "email": "me@example.com"
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
        "nickname": "여우리더",
        "email": "another@example.com"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 7: Join Event as Logged-in User
logged_in_participant_id = None
if access_token:
    print("\n" + "=" * 50)
    print("Testing Join Event (Authenticated)...")
    print("=" * 50)
    response = requests.post(
        f"{EVENTS_BASE_URL}/{TEST_EVENT_SLUG}/participants/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "nickname": "로그인유저닉네임",
            "email": "loggeduser@example.com"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    if response.status_code == 200:
        logged_in_participant_id = response.json().get('participant_id')

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

# Test 12: Delete Participant (본인 삭제)
if access_token and logged_in_participant_id:
    print("\n" + "=" * 50)
    print("Testing Delete Participant (Self)...")
    print("=" * 50)
    response = requests.delete(
        f"http://127.0.0.1:8000/api/v1/participants/{logged_in_participant_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("Response: Successfully deleted (204 No Content)")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 13: Delete Participant without Authentication (should fail)
if anonymous_participant_id:
    print("\n" + "=" * 50)
    print("Testing Delete Participant without Auth (should fail)...")
    print("=" * 50)
    response = requests.delete(
        f"http://127.0.0.1:8000/api/v1/participants/{anonymous_participant_id}"
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")

# Test 14: Try to delete other's participant without permission (should fail)
if access_token and anonymous_participant_id:
    print("\n" + "=" * 50)
    print("Testing Delete Other's Participant without Permission (should fail)...")
    print("=" * 50)
    # 익명 참가자를 삭제하려고 시도 (권한 없음)
    response = requests.delete(
        f"http://127.0.0.1:8000/api/v1/participants/{anonymous_participant_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type') == 'application/json' else response.text}")
