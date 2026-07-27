#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "fragment-test@example.com",
    "password": "***"
})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test devices endpoint
print("=== Testing GET /users/me/devices ===")
resp = requests.get(f"{BASE_URL}/users/me/devices", headers=headers)
print(f"Status: {resp.status_code}")
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

# Test member-info endpoint
print("\n=== Testing GET /users/me/member-info ===")
resp = requests.get(f"{BASE_URL}/users/me/member-info", headers=headers)
print(f"Status: {resp.status_code}")
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
