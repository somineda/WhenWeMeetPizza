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
