#!/usr/bin/env python3
"""Test settings endpoints (8 total)."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login and get token
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "batch2-test@isekai.dev",
    "password": "***"
})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("Token obtained: " + token[:30] + "...")
print()

# Test all 8 endpoints
endpoints = [
    ("GET", "/users/me/play-setting", "1. GET /users/me/play-setting"),
    ("PATCH", "/users/me/play-setting", "2. PATCH /users/me/play-setting", {"typing_speed": "fast", "auto_play": True}),
    ("GET", "/users/me/notify-setting", "3. GET /users/me/notify-setting"),
    ("PATCH", "/users/me/notify-setting", "4. PATCH /users/me/notify-setting", {"update_notify": False, "checkin_push": False}),
    ("GET", "/users/me/devices", "5. GET /users/me/devices"),
    ("POST", "/users/me/devices/test-device-id/logout", "6. POST /users/me/devices/{id}/logout"),
    ("GET", "/users/me/member-info", "7. GET /users/me/member-info"),
    ("PATCH", "/users/me", "8. PATCH /users/me (signature)", {"signature": "在异世界寻找意义"}),
]

for item in endpoints:
    method = item[0]
    path = item[1]
    label = item[2]
    body = item[3] if len(item) > 3 else None
    
    print(f"=== {label} ===")
    if method == "GET":
        resp = requests.request(method, f"{BASE_URL}{path}", headers=headers)
    else:
        resp = requests.request(method, f"{BASE_URL}{path}", headers=headers, json=body)
    
    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(resp.text)
    print()
