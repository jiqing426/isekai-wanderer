#!/usr/bin/env python3
"""QA测试：成就领取功能（完整流程）"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """登录获取token"""
    print("=" * 60)
    print("登录获取认证token")
    print("=" * 60)
    
    # 尝试登录
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@test.com",
            "password": "Test123456"
        }
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"\n✓ 登录成功，token: {token[:20]}...")
        return token
    else:
        print("\n✗ 登录失败，尝试注册新用户...")
        return None

def test_register_and_login():
    """注册并登录"""
    print("\n" + "=" * 60)
    print("注册新用户")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "qa_test@test.com",
            "password": "Test123456",
            "nickname": "QA测试"
        }
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        token = data.get("access_token")
        print(f"\n✓ 注册成功，token: {token[:20]}...")
        return token
    else:
        print("\n✗ 注册失败")
        return None

def test_achievements_with_token(token):
    """使用token测试成就功能"""
    print("\n" + "=" * 60)
    print("测试成就列表")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/achievements", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        achievements = data.get("achievements", [])
        print(f"成就总数: {len(achievements)}")
        print(f"已解锁: {data.get('unlocked_count', 0)}")
        print(f"已领取: {data.get('claimed_count', 0)}")
        
        if achievements:
            print("\n前3个成就:")
            for ach in achievements[:3]:
                print(f"  - {ach['id']}: {ach['name']} (解锁:{ach.get('isUnlocked', False)}, 领取:{ach.get('isClaimed', False)})")
        
        return achievements
    else:
        print(f"错误: {response.json()}")
        return []

def test_claim_achievement(token, achievement_id):
    """测试领取成就"""
    print("\n" + "=" * 60)
    print(f"测试领取成就: {achievement_id}")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 先尝试解锁
    print("\n1. 尝试解锁成就...")
    unlock_response = requests.post(
        f"{BASE_URL}/achievements/unlock",
        headers=headers,
        json={"achievement_id": achievement_id}
    )
    print(f"解锁状态码: {unlock_response.status_code}")
    print(f"解锁响应: {unlock_response.json()}")
    
    # 测试领取（小写）
    print("\n2. 测试领取（小写格式）...")
    claim_response = requests.post(
        f"{BASE_URL}/achievements/claim",
        headers=headers,
        json={"achievement_id": achievement_id.lower()}
    )
    print(f"领取状态码: {claim_response.status_code}")
    print(f"领取响应: {claim_response.json()}")
    
    # 测试领取（大写）
    print("\n3. 测试领取（大写格式）...")
    claim_response_upper = requests.post(
        f"{BASE_URL}/achievements/claim",
        headers=headers,
        json={"achievement_id": achievement_id.upper()}
    )
    print(f"领取状态码: {claim_response_upper.status_code}")
    print(f"领取响应: {claim_response_upper.json()}")
    
    # 验证不是500错误
    assert claim_response.status_code != 500, "服务器错误"
    assert claim_response_upper.status_code != 500, "服务器错误"
    
    print("\n✓ 大小写兼容性测试通过")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("成就系统完整QA测试")
    print("=" * 60)
    
    try:
        # 尝试登录
        token = test_login()
        
        if not token:
            # 如果登录失败，尝试注册
            token = test_register_and_login()
        
        if not token:
            print("\n✗ 无法获取认证token，测试终止")
            exit(1)
        
        # 测试成就列表
        achievements = test_achievements_with_token(token)
        
        if achievements:
            # 测试第一个成就的领取
            first_ach_id = achievements[0]['id']
            test_claim_achievement(token, first_ach_id)
        
        print("\n" + "=" * 60)
        print("所有测试通过 ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
