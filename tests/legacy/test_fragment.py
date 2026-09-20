#!/usr/bin/env python3
"""Test fragment mall endpoints."""

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "fragment-test@example.com",
    "password": "***"
})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("=== 1. GET /fragment/shop/goods ===")
resp = requests.get(f"{BASE_URL}/fragment/shop/goods", headers=headers)
print(resp.status_code)
import json
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

print("\n=== 2. POST /fragment/exchange (test with non-existent goods) ===")
resp = requests.post(f"{BASE_URL}/fragment/exchange", headers=headers, json={
    "goods_id": "00000000-0000-0000-0000-000000000001",
    "quantity": 1
})
print(resp.status_code)
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

print("\n=== 3. GET /fragment/transactions ===")
resp = requests.get(f"{BASE_URL}/fragment/transactions", headers=headers)
print(resp.status_code)
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
