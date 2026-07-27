#!/usr/bin/env python3
"""Debug delivery E2E failure."""
import requests, json, uuid

FRONTEND = "http://localhost:8081"
BASE = f"{FRONTEND}/api/v1"

# Register fresh user
email = f"cr016_debug_{uuid.uuid4().hex[:6]}@test.com"
r = requests.post(f"{BASE}/auth/register", json={
    "email": email,
    "password": "Test123456!",
    "nickname": "Debug"
})
print(f"Register: {r.status_code}")
if r.status_code not in (200, 201):
    print(r.text[:300])
    exit(1)

data = r.json()
token = data["access_token"]
h = {"Authorization": f"Bearer {token}"}
print(f"User: {email}")

# Create subscription
print("\n=== Create Subscription ===")
r = requests.post(f"{BASE}/cr016/subscription/create", headers=h, json={"tier": "basic", "cycle": "monthly"})
print(f"HTTP {r.status_code}")
print(json.dumps(r.json(), indent=2))

# Check quota
print("\n=== Quota Status ===")
r = requests.get(f"{BASE}/cr016/dialogue/quota/status", headers=h)
print(f"HTTP {r.status_code}")
print(f"Response: {r.text[:500]}")
if r.status_code == 200:
    d = r.json()
    print(json.dumps(d, indent=2))
