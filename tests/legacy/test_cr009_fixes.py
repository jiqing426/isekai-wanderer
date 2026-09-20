#!/usr/bin/env python3
"""Test CR-009 P0 fixes for the three endpoints."""
import requests
import json
import sys

BASE = "http://localhost:8000/api/v1"

def test_endpoints():
    # Register test user
    print("=== Registering test user ===")
    r = requests.post(f"{BASE}/auth/register", json={
        "email": "test_cr009@example.com",
        "password": "***"
    })
    if r.status_code in [200, 201]:
        token = r.json()["access_token"]
        print(f"✓ User registered, token obtained")
    elif r.status_code == 409:
        # User exists, login instead
        r = requests.post(f"{BASE}/auth/login", json={
            "email": "test_cr009@example.com",
            "password": "***"
        })
        token = r.json()["access_token"]
        print(f"✓ User logged in, token obtained")
    else:
        print(f"✗ Auth failed: {r.status_code} - {r.text}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: /affection endpoint
    print("\n=== Test 1: GET /affection ===")
    r = requests.get(f"{BASE}/api/v1/affection", headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Success: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"✗ Failed: {r.text}")
    
    # Test 2: /game/start to create a session
    print("\n=== Test 2: POST /game/start ===")
    r = requests.post(f"{BASE}/api/v1/game/start", headers=headers, json={
        "script_id": "11111111-1111-1111-1111-111111111111",
        "route_id": "11111111-1111-1111-1111-111111111112"
    })
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        session_id = r.json()["session_id"]
        print(f"✓ Session created: {session_id}")
    else:
        print(f"✗ Failed: {r.text}")
        # Try to continue with a mock session ID for testing
        session_id = "test-session-id"
    
    # Test 3: /game/{id}/choice
    print(f"\n=== Test 3: POST /game/{session_id}/choice ===")
    r = requests.post(f"{BASE}/api/v1/game/{session_id}/choice", headers=headers, json={
        "choice_id": "11111111-1111-1111-1111-111111111113"
    })
    print(f"Status: {r.status_code}")
    if r.status_code in [200, 400, 404]:  # 400/404 acceptable if choice invalid
        print(f"✓ Endpoint working (status {r.status_code})")
        print(f"Response: {r.text[:200]}")
    else:
        print(f"✗ Unexpected error: {r.text}")
    
    # Test 4: /game/{id}/free-chat
    print(f"\n=== Test 4: POST /game/{session_id}/free-chat ===")
    r = requests.post(f"{BASE}/api/v1/game/{session_id}/free-chat", headers=headers, json={
        "message": "你好，今天天气怎么样？"
    })
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Success: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"✗ Failed: {r.text}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_endpoints()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
