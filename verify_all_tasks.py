#!/usr/bin/env python3
"""验证所有任务完成状态"""
import requests

BASE = "http://localhost:8000/api/v1"

# 获取认证token
print("=== 认证 ===")
login = requests.post(f"{BASE}/auth/login", json={"email":"test@example.com","password":"***"})
if login.status_code != 200:
    print(f"登录失败: {login.status_code}")
    exit(1)
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✓ 认证成功\n")

# 任务1: 点赞接口测试
print("=== 任务1: 点赞接口 ===")
posts = requests.get(f"{BASE}/community/posts", headers=headers).json()
if posts.get("posts"):
    post_id = posts["posts"][0]["id"]
    like = requests.post(f"{BASE}/community/posts/{post_id}/like", headers=headers)
    print(f"POST /community/posts/{post_id}/like")
    print(f"状态码: {like.status_code}")
    print(f"响应: {like.json()}")
    if like.status_code in [200, 201, 400]:  # 400表示已点赞
        print("✓ 点赞接口正常\n")
    else:
        print("✗ 点赞接口异常\n")
else:
    print("✗ 无法获取帖子列表\n")

# 任务2: CR-013 剧本详情API
print("=== 任务2: CR-013 剧本详情API ===")
script = requests.get(f"{BASE}/scripts/11111111-1111-1111-1111-111111111111/detail", headers=headers)
print(f"GET /scripts/11111111-1111-1111-1111-111111111111/detail")
print(f"状态码: {script.status_code}")
if script.status_code == 200:
    data = script.json()
    print(f"标题: {data.get('title')}")
    print(f"章节数: {len(data.get('chapters', []))}")
    print(f"总节点数: {data.get('totalNodes')}")
    print("✓ CR-013 API正常\n")
else:
    print(f"✗ CR-013 API异常: {script.text}\n")

# 任务2: CR-014 成就系统API
print("=== 任务2: CR-014 成就系统API ===")
achievements = requests.get(f"{BASE}/achievements", headers=headers)
print(f"GET /achievements")
print(f"状态码: {achievements.status_code}")
if achievements.status_code == 200:
    data = achievements.json()
    print(f"成就总数: {data.get('total')}")
    print(f"已解锁数: {data.get('unlockedCount')}")
    print("✓ CR-014 API正常\n")
else:
    print(f"✗ CR-014 API异常: {achievements.text}\n")

# 任务2: CR-015 角色设定API
print("=== 任务2: CR-015 角色设定API ===")
character = requests.get(f"{BASE}/characters/char-001/detail", headers=headers)
print(f"GET /characters/char-001/detail")
print(f"状态码: {character.status_code}")
if character.status_code == 200:
    data = character.json()
    print(f"角色名: {data.get('name')}")
    print(f"英文名: {data.get('nameEn')}")
    print(f"性格标签: {data.get('personality', {}).get('tags')}")
    print("✓ CR-015 API正常\n")
else:
    print(f"✗ CR-015 API异常: {character.text}\n")

print("=" * 50)
print("所有任务验证完成")
