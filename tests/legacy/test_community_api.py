#!/usr/bin/env python3
"""Test community API endpoints"""
import requests

BASE = "http://localhost:8000/api/v1"

# Get token
print("=== 获取认证Token ===")
resp = requests.post(f"{BASE}/auth/login", json={"email":"test@example.com","password":"***"})
if resp.status_code != 200:
    print(f"登录失败: {resp.status_code}")
    exit(1)
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✓ Token获取成功\n")

# Test 1: Like post
print("=== 1. 测试点赞接口 POST /community/posts/{id}/like ===")
post_id = "366a8ec2-b65f-4b4a-9b28-5c253e02d5ea"
resp = requests.post(f"{BASE}/community/posts/{post_id}/like", headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
if resp.status_code in [200, 201, 400]:  # 400 = already liked
    print("✓ 点赞接口正常\n")
else:
    print("✗ 点赞接口异常\n")

# Test 2: Unlike post
print("=== 2. 测试取消点赞接口 DELETE /community/posts/{id}/like ===")
resp = requests.delete(f"{BASE}/community/posts/{post_id}/like", headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
if resp.status_code == 200:
    print("✓ 取消点赞接口正常\n")
else:
    print("✗ 取消点赞接口异常\n")

# Test 3: Get comments
print("=== 3. 测试获取评论接口 GET /community/posts/{id}/comments ===")
resp = requests.get(f"{BASE}/community/posts/{post_id}/comments", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"评论数量: {len(data.get('comments', []))}")
    print("✓ 获取评论接口正常\n")
else:
    print("✗ 获取评论接口异常\n")

# Test 4: Create comment
print("=== 4. 测试创建评论接口 POST /community/posts/{id}/comments ===")
resp = requests.post(f"{BASE}/community/posts/{post_id}/comments", headers=headers, json={"content":"测试评论"})
print(f"Status: {resp.status_code}")
if resp.status_code == 201:
    print(f"评论ID: {resp.json().get('id')}")
    print("✓ 创建评论接口正常\n")
else:
    print("✗ 创建评论接口异常\n")

# Test 5: Delete comment
print("=== 5. 测试删除评论接口 DELETE /community/posts/comments/{id} ===")
# First create a comment to delete
resp = requests.post(f"{BASE}/community/posts/{post_id}/comments", headers=headers, json={"content":"待删除评论"})
if resp.status_code == 201:
    comment_id = resp.json()["id"]
    resp = requests.delete(f"{BASE}/community/posts/comments/{comment_id}", headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 204:
        print("✓ 删除评论接口正常\n")
    else:
        print("✗ 删除评论接口异常\n")
else:
    print("✗ 无法创建测试评论\n")

print("=" * 50)
print("所有接口测试完成")
