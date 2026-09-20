#!/usr/bin/env python3
"""测试 CR-009 P0 任务接口"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 登录获取 token
print("正在登录...")
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "cr009test@example.com",
    "password": "***"
})

if resp.status_code != 200:
    print(f"登录失败: {resp.text}")
    exit(1)

token = resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}
print(f"✓ 登录成功，token: {token[:30]}...")

print("\n" + "=" * 60)
print("CR-009 P0 任务接口测试")
print("=" * 60)

# 1. 剧本详情数据补全
print("\n【1】剧本详情数据补全")
print("-" * 60)

# 1.1 GET /scripts/{id} - 角色数据
print("\n1.1 GET /scripts/11111111-1111-1111-1111-111111111111")
resp = requests.get(f"{BASE_URL}/scripts/11111111-1111-1111-1111-111111111111")
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✓ 角色数量: {len(data.get('characters', []))}")
    if data.get('characters'):
        char = data['characters'][0]
        print(f"  角色信息: {char.get('name')}, 年龄: {char.get('age')}, 身高: {char.get('height')}")
else:
    print(f"✗ 错误: {resp.text}")

# 1.2 GET /scripts/{id}/routes - 路线探索数据
print("\n1.2 GET /scripts/11111111-1111-1111-1111-111111111111/routes")
resp = requests.get(f"{BASE_URL}/scripts/11111111-1111-1111-1111-111111111111/routes", headers=headers)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✓ 路线数量: {len(data.get('routes', []))}")
else:
    print(f"✗ 错误: {resp.text}")

# 1.3 GET /scripts/{id}/endings - 结局收集数据
print("\n1.3 GET /scripts/11111111-1111-1111-1111-111111111111/endings")
resp = requests.get(f"{BASE_URL}/scripts/11111111-1111-1111-1111-111111111111/endings", headers=headers)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✓ 结局数量: {len(data.get('endings', []))}")
else:
    print(f"✗ 错误: {resp.text}")

# 2. 游戏内容页面后端
print("\n【2】游戏内容页面后端")
print("-" * 60)

# 先创建一个游戏会话
print("\n创建游戏会话...")
resp = requests.post(f"{BASE_URL}/game/start", headers=headers, json={
    "script_id": "11111111-1111-1111-1111-111111111111"
})
if resp.status_code == 200:
    session_id = resp.json().get("session_id")
    print(f"✓ 会话ID: {session_id}")
else:
    print(f"✗ 创建会话失败: {resp.text}")
    session_id = None

if session_id:
    # 2.1 GET /game/{sessionId}/progress - 进度条数据
    print(f"\n2.1 GET /game/{session_id}/progress")
    resp = requests.get(f"{BASE_URL}/game/{session_id}/progress", headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ 进度: {data.get('completion_rate', 0)}%")
        print(f"  已探索节点: {data.get('explored_nodes', 0)}")
    else:
        print(f"✗ 错误: {resp.text}")

    # 2.2 GET /game/{sessionId}/history - 历史对话
    print(f"\n2.2 GET /game/{session_id}/history")
    resp = requests.get(f"{BASE_URL}/game/{session_id}/history", headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ 历史记录数量: {len(data.get('history', []))}")
    else:
        print(f"✗ 错误: {resp.text}")

    # 2.3 POST /game/{sessionId}/gift - 送礼功能
    print(f"\n2.3 POST /game/{session_id}/gift")
    resp = requests.post(f"{BASE_URL}/game/{session_id}/gift", headers=headers, json={
        "character_id": "22222222-2222-2222-2222-222222222222",
        "gift_id": "gift_001",
        "quantity": 1
    })
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ 送礼结果: {data.get('status')}")
    else:
        print(f"✗ 错误: {resp.text}")

    # 2.4 GET /game/{sessionId}/gift-history - 送礼历史
    print(f"\n2.4 GET /game/{session_id}/gift-history")
    resp = requests.get(f"{BASE_URL}/game/{session_id}/gift-history", headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ 送礼历史数量: {len(data.get('gifts', []))}")
    else:
        print(f"✗ 错误: {resp.text}")

# 3. 个人中心后端
print("\n【3】个人中心后端")
print("-" * 60)

# 3.1 GET /users/me/game-stats - 游戏统计
print("\n3.1 GET /users/me/game-stats")
resp = requests.get(f"{BASE_URL}/users/me/game-stats", headers=headers)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✓ 总游戏时长: {data.get('total_play_time_minutes', 0)} 分钟")
    print(f"  总选择次数: {data.get('total_choices', 0)}")
else:
    print(f"✗ 错误: {resp.text}")

# 3.2 GET /users/me/latest-session - 快速继续
print("\n3.2 GET /users/me/latest-session")
resp = requests.get(f"{BASE_URL}/users/me/latest-session", headers=headers)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    if data:
        print(f"✓ 最新会话: {data.get('script_name')}")
        print(f"  进度: {data.get('progress', 0)}%")
    else:
        print("✓ 无最新会话")
else:
    print(f"✗ 错误: {resp.text}")

# 3.3 POST /daily/checkin - 签到
print("\n3.3 POST /daily/checkin")
resp = requests.post(f"{BASE_URL}/daily/checkin", headers=headers)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✓ 签到结果: {data.get('status')}")
    print(f"  获得碎片: {data.get('fragments_earned', 0)}")
else:
    print(f"✗ 错误: {resp.text}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
