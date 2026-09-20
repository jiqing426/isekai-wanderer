#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "cr009test3@example.com",
    "password": "***"
})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Start a game session
resp = requests.post(f"{BASE_URL}/game/start", headers=headers, json={
    "script_id": "11111111-1111-1111-1111-111111111111"
})
session_id = resp.json()["session_id"]
print(f"Session ID: {session_id}")

# Test 1: GET /game/{sessionId}/progress
print("\n=== Test 1: GET /game/{sessionId}/progress ===")
resp = requests.get(f"{BASE_URL}/game/{session_id}/progress", headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")

# Test 2: GET /game/{sessionId}/history
print("\n=== Test 2: GET /game/{sessionId}/history ===")
resp = requests.get(f"{BASE_URL}/game/{session_id}/history", headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")

# Test 3: GET /gift/catalog
print("\n=== Test 3: GET /gift/catalog ===")
resp = requests.get(f"{BASE_URL}/gift/catalog", headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")

# Test 4: POST /daily/checkin
print("\n=== Test 4: POST /daily/checkin ===")
resp = requests.post(f"{BASE_URL}/daily/checkin", headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")

