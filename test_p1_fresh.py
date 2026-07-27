#!/usr/bin/env python3
import requests, json

BASE = "http://localhost:8000/api/v1"

# Test with a fresh user (no fragment records)
r = requests.post(f"{BASE}/auth/register", json={"email":"p1test3@example.com","password":"***"})
if r.status_code not in [200, 201]:
    print(f"Register failed: {r.status_code} - {r.json()}")
    exit(1)

token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}

print("=== Testing with fresh user (no data) ===")

print("\n--- GET /users/me/devices ---")
r = requests.get(f"{BASE}/users/me/devices", headers=h)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

print("\n--- GET /users/me/member-info ---")
r = requests.get(f"{BASE}/users/me/member-info", headers=h)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
