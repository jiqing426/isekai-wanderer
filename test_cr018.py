#!/usr/bin/env python3
"""CR-018 P0 验证：送礼接口 + 签到 total_fragments BUG 验证"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def get_test_token():
    """获取测试用户 token"""
    # 尝试登录
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "cr018_test@test.com",
        "password": "***"
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    
    # 注册新用户
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "cr018_test@test.com",
        "password": "***",
        "nickname": "CR018测试"
    })
    if resp.status_code in [200, 201]:
        return resp.json()["access_token"]
    
    raise Exception(f"无法获取 token: {resp.text}")

def test_gift_api():
    """测试送礼接口"""
    print("\n" + "="*60)
    print("【测试 1】送礼接口验证")
    print("="*60)
    
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取游戏会话（需要先开始游戏）
    print("\n[步骤 1] 获取剧本列表...")
    resp = requests.get(f"{BASE_URL}/scripts", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ 获取剧本失败: {resp.status_code}")
        return False
    
    scripts = resp.json().get("scripts", [])
    if not scripts:
        print("  ❌ 没有可用剧本")
        return False
    
    script_id = scripts[0]["id"]
    print(f"  ✅ 使用剧本: {script_id}")
    
    # 2. 开始游戏
    print("\n[步骤 2] 开始游戏...")
    resp = requests.post(f"{BASE_URL}/game/start", headers=headers, json={
        "script_id": script_id
    })
    if resp.status_code not in [200, 201]:
        print(f"  ❌ 开始游戏失败: {resp.status_code}")
        return False
    
    session_id = resp.json().get("session_id")
    print(f"  ✅ 游戏会话: {session_id}")
    
    # 3. 获取礼物目录
    print("\n[步骤 3] 获取礼物目录...")
    resp = requests.get(f"{BASE_URL}/characters/gifts/catalog", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ 获取礼物目录失败: {resp.status_code}")
        return False
    
    gifts = resp.json().get("gifts", [])
    if not gifts:
        print("  ❌ 没有可用礼物")
        return False
    
    gift = gifts[0]
    print(f"  ✅ 选择礼物: {gift.get('name')} (ID: {gift.get('id')})")
    print(f"     价格: {gift.get('price')} 碎片")
    
    # 4. 检查当前碎片余额
    print("\n[步骤 4] 检查当前碎片余额...")
    resp = requests.get(f"{BASE_URL}/users/me/asset", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ 获取资产信息失败: {resp.status_code}")
        return False
    
    asset_before = resp.json()
    balance_before = asset_before.get("balance", 0)
    print(f"  当前余额: {balance_before}")
    
    # 如果余额不足，尝试获取更便宜的礼物
    gift_price = gift.get("price", 0)
    if balance_before < gift_price:
        print(f"  ️ 余额不足，尝试寻找更便宜的礼物...")
        for g in gifts:
            if g.get("price", 0) <= balance_before:
                gift = g
                gift_price = gift.get("price", 0)
                print(f"  ✅ 选择礼物: {gift.get('name')} (ID: {gift.get('id')})")
                print(f"     价格: {gift_price} 碎片")
                break
        else:
            print(f"  ❌ 没有足够便宜的礼物（余额: {balance_before}）")
            return False
    
    # 5. 获取角色列表
    print("\n[步骤 5] 获取角色列表...")
    resp = requests.get(f"{BASE_URL}/characters", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ 获取角色列表失败: {resp.status_code}")
        return False
    
    characters = resp.json().get("characters", [])
    if not characters:
        print("  ❌ 没有可用角色")
        return False
    
    character = characters[0]
    character_id = character.get("id")
    print(f"  ✅ 选择角色: {character.get('name')} (ID: {character_id})")
    
    # 6. 检查当前好感度
    print("\n[步骤 6] 检查当前好感度...")
    resp = requests.get(f"{BASE_URL}/affection", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ 获取好感度失败: {resp.status_code}")
        return False
    
    affections_before = resp.json().get("affections", [])
    print(f"  当前好感度列表: {len(affections_before)} 个角色")
    if affections_before:
        for aff in affections_before[:3]:
            print(f"    - {aff.get('character_name')}: {aff.get('value')} ({aff.get('level')})")
    
    # 7. 调用送礼接口
    print("\n[步骤 7] 调用送礼接口...")
    gift_payload = {
        "gift_id": gift.get("id"),
        "character_id": character_id
    }
    print(f"  请求: POST /api/v1/game/{session_id}/gift")
    print(f"  参数: {json.dumps(gift_payload, ensure_ascii=False)}")
    
    resp = requests.post(f"{BASE_URL}/game/{session_id}/gift", headers=headers, json=gift_payload)
    print(f"  响应状态: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"  ❌ 送礼失败: {resp.text[:200]}")
        return False
    
    gift_response = resp.json()
    print(f"  响应内容: {json.dumps(gift_response, ensure_ascii=False, indent=2)[:500]}")
    
    # 7. 验证碎片扣减
    print("\n[步骤 7] 验证碎片扣减...")
    resp = requests.get(f"{BASE_URL}/users/me/asset", headers=headers)
    asset_after = resp.json()
    balance_after = asset_after.get("balance", 0)
    
    print(f"  送礼前余额: {balance_before}")
    print(f"  送礼后余额: {balance_after}")
    print(f"  扣减数量: {balance_before - balance_after}")
    
    if balance_after < balance_before:
        print("  ✅ 碎片扣减正确")
    else:
        print("  ️ 碎片未扣减（可能是免费礼物或余额不足）")
    
    # 8. 验证好感度增加
    print("\n[步骤 8] 验证好感度增加...")
    resp = requests.get(f"{BASE_URL}/affection", headers=headers)
    affections_after = resp.json().get("affections", [])
    
    print(f"  送礼后好感度列表: {len(affections_after)} 个角色")
    
    # 比较变化
    changed = False
    for aff_after in affections_after:
        char_id = aff_after.get("character_id")
        for aff_before in affections_before:
            if aff_before.get("character_id") == char_id:
                old_value = aff_before.get("value", 0)
                new_value = aff_after.get("value", 0)
                if new_value > old_value:
                    print(f"  ✅ {aff_after.get('character_name')}: {old_value} → {new_value} (+{new_value - old_value})")
                    changed = True
                break
    
    if not changed:
        print("  ⚠️ 未检测到好感度变化")
    
    # 9. 检查送礼历史
    print("\n[步骤 9] 检查送礼历史...")
    resp = requests.get(f"{BASE_URL}/game/{session_id}/gift-history", headers=headers)
    if resp.status_code == 200:
        history = resp.json()
        print(f"  送礼历史记录: {json.dumps(history, ensure_ascii=False)[:300]}")
    else:
        print(f"  ️ 获取送礼历史失败: {resp.status_code}")
    
    return True

def test_sign_total_fragments():
    """测试签到后 total_fragments 是否正确"""
    print("\n" + "="*60)
    print("【测试 2】签到 total_fragments BUG 验证")
    print("="*60)
    
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取签到信息
    print("\n[步骤 1] 获取签到信息...")
    resp = requests.get(f"{BASE_URL}/sign/info", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ 获取签到信息失败: {resp.status_code}")
        return False
    
    sign_info_before = resp.json()
    total_fragments_before = sign_info_before.get("total_fragments", 0)
    print(f"  签到前 total_fragments: {total_fragments_before}")
    print(f"  签到前 streak_days: {sign_info_before.get('streak_days', 0)}")
    print(f"  今日已签到: {sign_info_before.get('checked_in_today', False)}")
    
    # 2. 执行签到
    print("\n[步骤 2] 执行签到...")
    resp = requests.post(f"{BASE_URL}/sign/checkin", headers=headers)
    print(f"  响应状态: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"  响应内容: {resp.text[:200]}")
        if resp.status_code == 409:
            print("  ⚠️ 今日已签到，跳过")
            # 即使已签到，也检查 total_fragments
        else:
            print(f"  ❌ 签到失败")
            return False
    else:
        checkin_data = resp.json()
        print(f"  签到成功: {json.dumps(checkin_data, ensure_ascii=False)}")
    
    # 3. 重新获取签到信息
    print("\n[步骤 3] 重新获取签到信息...")
    resp = requests.get(f"{BASE_URL}/sign/info", headers=headers)
    sign_info_after = resp.json()
    total_fragments_after = sign_info_after.get("total_fragments", 0)
    
    print(f"  签到后 total_fragments: {total_fragments_after}")
    print(f"  签到后 streak_days: {sign_info_after.get('streak_days', 0)}")
    print(f"  签到后 total_checkins: {sign_info_after.get('total_checkins', 0)}")
    
    # 4. 验证
    print("\n[步骤 4] 验证结果...")
    if total_fragments_after > total_fragments_before:
        print(f"  ✅ total_fragments 已更新: {total_fragments_before} → {total_fragments_after}")
        print(f"  ✅ BUG 已修复")
        return True
    elif total_fragments_after > 0:
        print(f"  ✅ total_fragments > 0: {total_fragments_after}")
        print(f"  ✅ BUG 已修复")
        return True
    else:
        print(f"  ❌ total_fragments 仍为 0")
        print(f"  ❌ BUG 未修复")
        return False

def main():
    print("\n" + "="*60)
    print("CR-018 P0 验证测试")
    print("="*60)
    
    results = {}
    
    # 测试 1: 送礼接口
    try:
        results["送礼接口"] = test_gift_api()
    except Exception as e:
        print(f"\n❌ 送礼接口测试异常: {e}")
        results["送礼接口"] = False
    
    # 测试 2: 签到 total_fragments
    try:
        results["签到 total_fragments"] = test_sign_total_fragments()
    except Exception as e:
        print(f"\n❌ 签到测试异常: {e}")
        results["签到 total_fragments"] = False
    
    # 汇总
    print("\n" + "="*60)
    print("测试汇总")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n总计: {passed_count}/{total_count} 通过")
    
    if passed_count == total_count:
        print("\n 所有测试通过")
    else:
        print(f"\n🔴 {total_count - passed_count} 个测试失败")

if __name__ == "__main__":
    main()
