#!/usr/bin/env python3
"""
成就系统完整QA测试
测试流程：注册 -> 解锁成就 -> 领取成就 -> 验证碎片奖励
"""

import requests
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def test_full_achievement_flow():
    print("=" * 60)
    print("成就系统完整QA测试")
    print("=" * 60)
    
    # 1. 创建测试账号
    test_email = f"qa_full_{uuid.uuid4().hex[:8]}@test.com"
    print(f"\n1. 创建测试账号: {test_email}")
    
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": test_email,
            "password": "Test123456",
            "username": "QA Test"
        }
    )
    
    assert register_response.status_code in [200, 201], f"注册失败: {register_response.text}"
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✓ 注册成功")
    
    # 2. 获取初始碎片余额
    print("\n2. 获取初始碎片余额")
    asset_response = requests.get(f"{BASE_URL}/users/me/asset", headers=headers)
    assert asset_response.status_code == 200, f"获取资产失败: {asset_response.text}"
    initial_balance = asset_response.json()["balance"]
    print(f"   初始碎片: {initial_balance}")
    
    # 3. 获取成就列表
    print("\n3. 获取成就列表")
    achievements_response = requests.get(f"{BASE_URL}/achievements", headers=headers)
    assert achievements_response.status_code == 200, f"获取成就列表失败: {achievements_response.text}"
    achievements = achievements_response.json()["achievements"]
    print(f"   ✓ 成就数量: {len(achievements)}")
    
    # 4. 解锁第一个成就（小写ID）
    first_achievement = achievements[0]["id"]
    print(f"\n4. 解锁成就: {first_achievement}")
    
    unlock_response = requests.post(
        f"{BASE_URL}/achievements/unlock",
        headers=headers,
        json={"achievement_id": first_achievement.lower()}
    )
    assert unlock_response.status_code == 200, f"解锁失败: {unlock_response.text}"
    print(f"   ✓ 解锁成功")
    
    # 5. 尝试重复解锁（应该失败）
    print("\n5. 尝试重复解锁（应该返回409）")
    duplicate_unlock = requests.post(
        f"{BASE_URL}/achievements/unlock",
        headers=headers,
        json={"achievement_id": first_achievement}
    )
    assert duplicate_unlock.status_code == 409, f"重复解锁应该返回409，实际: {duplicate_unlock.status_code}"
    print(f"   ✓ 正确拒绝重复解锁")
    
    # 6. 领取成就奖励
    print("\n6. 领取成就奖励")
    claim_response = requests.post(
        f"{BASE_URL}/achievements/claim",
        headers=headers,
        json={"achievement_id": first_achievement}
    )
    assert claim_response.status_code == 200, f"领取失败: {claim_response.text}"
    reward_amount = claim_response.json()["reward"]["amount"]
    print(f"   ✓ 领取成功，奖励: {reward_amount} 碎片")
    
    # 7. 尝试重复领取（应该失败）
    print("\n7. 尝试重复领取（应该返回409）")
    duplicate_claim = requests.post(
        f"{BASE_URL}/achievements/claim",
        headers=headers,
        json={"achievement_id": first_achievement}
    )
    assert duplicate_claim.status_code == 409, f"重复领取应该返回409，实际: {duplicate_claim.status_code}"
    print(f"   ✓ 正确拒绝重复领取")
    
    # 8. 验证碎片余额增加
    print("\n8. 验证碎片余额")
    final_asset_response = requests.get(f"{BASE_URL}/users/me/asset", headers=headers)
    final_balance = final_asset_response.json()["balance"]
    expected_balance = initial_balance + reward_amount
    assert final_balance == expected_balance, f"碎片余额不正确: 期望 {expected_balance}, 实际 {final_balance}"
    print(f"   ✓ 碎片余额: {final_balance} (增加了 {reward_amount})")
    
    # 9. 测试大小写兼容性
    print("\n9. 测试大小写兼容性")
    second_achievement = achievements[1]["id"]
    
    # 解锁（大写ID）
    unlock_upper = requests.post(
        f"{BASE_URL}/achievements/unlock",
        headers=headers,
        json={"achievement_id": second_achievement.upper()}
    )
    assert unlock_upper.status_code == 200, f"大写ID解锁失败: {unlock_upper.text}"
    print(f"   ✓ 大写ID解锁成功")
    
    # 领取（混合大小写）
    mixed_case_id = second_achievement[:3] + second_achievement[3:].lower()
    claim_mixed = requests.post(
        f"{BASE_URL}/achievements/claim",
        headers=headers,
        json={"achievement_id": mixed_case_id}
    )
    assert claim_mixed.status_code == 200, f"混合大小写领取失败: {claim_mixed.text}"
    print(f"   ✓ 混合大小写领取成功")
    
    # 10. 验证成就状态
    print("\n10. 验证成就状态")
    final_achievements = requests.get(f"{BASE_URL}/achievements", headers=headers)
    final_achievements_data = final_achievements.json()["achievements"]
    
    unlocked_count = sum(1 for a in final_achievements_data if a.get("unlocked", False))
    
    assert unlocked_count >= 2, f"解锁数量不正确: {unlocked_count}"
    print(f"   ✓ 已解锁: {unlocked_count}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print("\n测试总结:")
    print(f"  - 账号: {test_email}")
    print(f"  - 初始碎片: {initial_balance}")
    print(f"  - 最终碎片: {final_balance}")
    print(f"  - 获得碎片: {final_balance - initial_balance}")
    print(f"  - 解锁成就: {unlocked_count}")
    print(f"  - 领取成就: {claimed_count}")

if __name__ == "__main__":
    try:
        test_full_achievement_flow()
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
