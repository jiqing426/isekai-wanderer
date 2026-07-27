#!/usr/bin/env python3
"""Test BUG-002 fix: POST /fragment/exchange with invalid UUID"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "bug002-test@example.com",
    "password": "***"
})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("=== Test BUG-002 Fix: Invalid UUID ===")
resp = requests.post(f"{BASE_URL}/fragment/exchange", headers=headers, json={
    "goods_id": "invalid-uuid",
    "quantity": 1
})
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")

if resp.status_code == 400:
    print("\n✅ BUG-002 修复成功：无效 UUID 返回 400")
else:
    print(f"\n❌ BUG-002 修复失败：期望 400，实际 {resp.status_code}")
