#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 登录获取token
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "***"
})

if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.status_code}")
    print(login_resp.text)
    exit(1)

token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 测试 CR-013: 剧本详情
print("=== CR-013: GET /scripts/{id}/detail ===")
script_id = "11111111-1111-1111-1111-111111111111"
resp = requests.get(f"{BASE_URL}/scripts/{script_id}/detail", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(resp.text)
