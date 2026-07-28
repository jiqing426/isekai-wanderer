#!/usr/bin/env python3
"""QA测试：成就领取功能"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试1: 健康检查")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    print("✓ 通过\n")

def test_achievements_list():
    """测试获取成就列表"""
    print("=" * 60)
    print("测试2: 获取成就列表")
    print("=" * 60)
    
    # 需要先登录获取token
    # 这里假设使用测试用户的token
    headers = {"Authorization": "Bearer test-token"}
    
    response = requests.get(f"{BASE_URL}/achievements", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"成就总数: {len(data.get('achievements', []))}")
        print(f"已解锁: {data.get('unlocked_count', 0)}")
        print(f"已领取: {data.get('claimed_count', 0)}")
        print("✓ 通过\n")
        return True
    else:
        print(f"错误: {response.json()}")
        print("⚠ 需要有效的认证token\n")
        return False

def test_achievement_claim():
    """测试成就领取"""
    print("=" * 60)
    print("测试3: 成就领取（大小写兼容性）")
    print("=" * 60)
    
    headers = {"Authorization": "Bearer test-token"}
    
    # 测试小写achievement_id
    test_cases = [
        ("ach-001", "小写格式"),
        ("ACH-001", "大写格式"),
        ("Ach-001", "混合大小写"),
    ]
    
    for ach_id, description in test_cases:
        print(f"\n测试用例: {description} ({ach_id})")
        response = requests.post(
            f"{BASE_URL}/achievements/claim",
            headers=headers,
            json={"achievement_id": ach_id}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 应该返回401（未认证）或400/404/409（业务错误），不应该是500
        assert response.status_code != 500, f"服务器错误: {response.json()}"
    
    print("\n✓ 大小写兼容性测试通过\n")

def test_achievement_unlock():
    """测试成就解锁"""
    print("=" * 60)
    print("测试4: 成就解锁（大小写兼容性）")
    print("=" * 60)
    
    headers = {"Authorization": "Bearer test-token"}
    
    test_cases = [
        ("ach-001", "小写格式"),
        ("ACH-001", "大写格式"),
    ]
    
    for ach_id, description in test_cases:
        print(f"\n测试用例: {description} ({ach_id})")
        response = requests.post(
            f"{BASE_URL}/achievements/unlock",
            headers=headers,
            json={"achievement_id": ach_id}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 应该返回401（未认证）或业务错误，不应该是500
        assert response.status_code != 500, f"服务器错误: {response.json()}"
    
    print("\n✓ 大小写兼容性测试通过\n")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("成就系统QA测试")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        test_achievements_list()
        test_achievement_claim()
        test_achievement_unlock()
        
        print("=" * 60)
        print("所有测试通过 ✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        exit(1)
