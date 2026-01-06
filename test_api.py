#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1/auth"

# Test 1: Register
print("=" * 50)
print("Testing Registration...")
print("=" * 50)
response = requests.post(
    f"{BASE_URL}/register/",
    json={
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "password2": "SecurePass123!",
        "first_name": "Test",
        "last_name": "User"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 201:
    access_token = response.json()['tokens']['access']

    # Test 2: Get Profile
    print("\n" + "=" * 50)
    print("Testing Get Profile...")
    print("=" * 50)
    response = requests.get(
        f"{BASE_URL}/profile/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Update Profile
    print("\n" + "=" * 50)
    print("Testing Update Profile...")
    print("=" * 50)
    response = requests.patch(
        f"{BASE_URL}/profile/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"first_name": "Updated"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 4: Login
print("\n" + "=" * 50)
print("Testing Login...")
print("=" * 50)
response = requests.post(
    f"{BASE_URL}/login/",
    json={
        "email": "testuser@example.com",
        "password": "SecurePass123!"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
