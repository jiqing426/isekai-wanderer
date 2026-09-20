#!/usr/bin/env python3
import requests, json

BASE = "http://localhost:8000/api/v1"

# Login with existing test account
r = requests.post(f"{BASE}/auth/login", json={"email":"fragment-test@example.com","password":"***"})
if r.status_code != 200:
    print(f"Login failed: {r.status_code}")
    print(r.json())
    exit(1)

token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}

print("=== GET /users/me/devices ===")
r = requests.get(f"{BASE}/users/me/devices", headers=h)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

print("\n=== GET /users/me/member-info ===")
r = requests.get(f"{BASE}/users/me/member-info", headers=h)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
