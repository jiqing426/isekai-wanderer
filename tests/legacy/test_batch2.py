#!/usr/bin/env python3
"""Test batch 2 endpoints (11-19) for CR-008."""

import requests

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

# Test all 9 endpoints
endpoints = [
    ("GET", "/users/me/stats", "11. GET /users/me/stats"),
    ("GET", "/users/me/asset", "12. GET /users/me/asset"),
    ("GET", "/sign/info", "13. GET /sign/info"),
    ("GET", "/users/me/latest-save", "14. GET /users/me/latest-save"),
    ("GET", "/users/me/memory/summary", "15. GET /users/me/memory/summary"),
    ("GET", "/users/me/characters/bond", "16. GET /users/me/characters/bond"),
    ("GET", "/users/me/endings", "17. GET /users/me/endings"),
    ("GET", "/users/me/endings/recent", "18. GET /users/me/endings/recent"),
    ("GET", "/users/me/memory/full", "19. GET /users/me/memory/full (should be 403 for free tier)"),
]

for method, path, label in endpoints:
    print(f"=== {label} ===")
    resp = requests.request(method, f"{BASE_URL}{path}", headers=headers)
    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(resp.text)
    print()
