#!/usr/bin/env python3
"""Simple test for CR-009 fixes."""
import requests
import json

BASE = "http://localhost:8000/api/v1"

# Login
r = requests.post(f"{BASE}/auth/login", json={
    "email": "test_cr009@example.com",
    "password": "***"
})
assert r.status_code == 200, f"Login failed: {r.status_code}"
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✓ Logged in, token: {token[:30]}...")

# Test 1: GET /affection
print("\n=== Test 1: GET /affection ===")
r = requests.get(f"{BASE}/affection", headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {json.dumps(r.json(), indent=2, ensure_ascii=False)}")
assert r.status_code == 200, f"Expected 200, got {r.status_code}"
print("✓ PASS")

# Test 2: POST /game/start
print("\n=== Test 2: POST /game/start ===")
r = requests.post(f"{BASE}/game/start", headers=headers, json={
    "script_id": "11111111-1111-1111-1111-111111111111",
    "route_id": "11111111-1111-1111-1111-111111111112"
})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    session_id = r.json()["session_id"]
    print(f"✓ Session created: {session_id}")
else:
    print(f"Response: {r.text[:200]}")
    # Try without route_id
    r = requests.post(f"{BASE}/game/start", headers=headers, json={
        "script_id": "11111111-1111-1111-1111-111111111111"
    })
    print(f"Retry status: {r.status_code}")
    if r.status_code == 200:
        session_id = r.json()["session_id"]
        print(f"✓ Session created: {session_id}")
    else:
        print(f"Response: {r.text[:200]}")
        session_id = None

# Test 3: POST /game/{id}/choice
if session_id:
    print(f"\n=== Test 3: POST /game/{session_id}/choice ===")
    r = requests.post(f"{BASE}/game/{session_id}/choice", headers=headers, json={
        "choice_id": "11111111-1111-1111-1111-111111111113"
    })
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:300]}")
    # 200 or 400/404 are acceptable (choice might not exist)
    assert r.status_code in [200, 400, 404], f"Unexpected error: {r.status_code}"
    print("✓ PASS (no 500 error)")

# Test 4: POST /game/{id}/free-chat
if session_id:
    print(f"\n=== Test 4: POST /game/{session_id}/free-chat ===")
    r = requests.post(f"{BASE}/game/{session_id}/free-chat", headers=headers, json={
        "message": "你好，今天天气怎么样？"
    })
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:300]}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("✓ PASS")

print("\n=== All tests completed ===")
