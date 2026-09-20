#!/usr/bin/env python3
"""Test gift functionality"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "cr009test2@example.com",
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

# Test gift
print("\n=== POST /game/{session_id}/gift ===")
resp = requests.post(f"{BASE_URL}/game/{session_id}/gift", headers=headers, json={
    "character_id": "22222222-2222-2222-2222-222222222222",
    "gift_id": "gift_001",
    "quantity": 1
})
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")

# Test gift history
print("\n=== GET /game/{session_id}/gift-history ===")
resp = requests.get(f"{BASE_URL}/game/{session_id}/gift-history", headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
