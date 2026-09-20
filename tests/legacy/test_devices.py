#!/usr/bin/env python3
"""Test device logout endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "batch2-test@isekai.dev",
    "password": "***"
})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("Token: " + token[:30] + "...")

# Get devices
print("\n=== GET /users/me/devices ===")
resp = requests.get(f"{BASE_URL}/users/me/devices", headers=headers)
data = resp.json()
print(json.dumps(data, indent=2, ensure_ascii=False))

devices = data["devices"]
current_id = None
other_id = None
for d in devices:
    if d["is_current"]:
        current_id = d["id"]
    else:
        other_id = d["id"]

# Test 1: Try to logout current device (should fail with 400)
if current_id:
    print(f"\n=== POST /users/me/devices/{current_id}/logout (should fail 400) ===")
    resp = requests.post(f"{BASE_URL}/users/me/devices/{current_id}/logout", headers=headers)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

# Test 2: Logout non-current device (should succeed)
if other_id:
    print(f"\n=== POST /users/me/devices/{other_id}/logout (should succeed) ===")
    resp = requests.post(f"{BASE_URL}/users/me/devices/{other_id}/logout", headers=headers)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

# Test 3: Logout non-existent device (should fail with 404)
print(f"\n=== POST /users/me/devices/non-existent-id/logout (should fail 404) ===")
resp = requests.post(f"{BASE_URL}/users/me/devices/00000000-0000-0000-0000-000000000000/logout", headers=headers)
print(f"Status: {resp.status_code}")
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

# Verify device list after logout
print("\n=== GET /users/me/devices (after logout) ===")
resp = requests.get(f"{BASE_URL}/users/me/devices", headers=headers)
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
