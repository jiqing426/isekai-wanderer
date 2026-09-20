#!/usr/bin/env python3
"""CR-018 第二轮验证：T-010/T-006/T-005"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def get_test_token():
    """获取测试用户 token"""
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "cr018_test@test.com",
        "password": "***"
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "cr018_test@test.com",
        "password": "***",
        "nickname": "CR018测试"
    })
    if resp.status_code in [200, 201]:
        return resp.json()["access_token"]
    
    raise Exception(f"无法获取 token: {resp.text}")

def test_t010_total_fragments():
    """T-010: 验证签到后 total_fragments > 0"""
    print("\n" + "="*60)
    print("【T-010】签到后 total_fragments 验证")
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
    checked_in_today = sign_info_before.get("checked_in_today", False)
    
    print(f"  签到前 total_fragments: {total_fragments_before}")
    print(f"  今日已签到: {checked_in_today}")
    
    # 2. 执行签到（如果今日未签到）
    if not checked_in_today:
        print("\n[步骤 2] 执行签到...")
        resp = requests.post(f"{BASE_URL}/sign/checkin", headers=headers)
        print(f"  响应状态: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"  ❌ 签到失败: {resp.text[:200]}")
            return False
        
        checkin_data = resp.json()
        print(f"  签到成功: {json.dumps(checkin_data, ensure_ascii=False)}")
    else:
        print("\n[步骤 2] 今日已签到，跳过")
    
    # 3. 重新获取签到信息
    print("\n[步骤 3] 重新获取签到信息...")
    resp = requests.get(f"{BASE_URL}/sign/info", headers=headers)
    sign_info_after = resp.json()
    total_fragments_after = sign_info_after.get("total_fragments", 0)
    
    print(f"  签到后 total_fragments: {total_fragments_after}")
    
    # 4. 验证
    print("\n[步骤 4] 验证结果...")
    if total_fragments_after > 0:
        print(f"  ✅ total_fragments > 0: {total_fragments_after}")
        print(f"  ✅ BUG 已修复")
        return True
    else:
        print(f"  ❌ total_fragments 仍为 0")
        print(f"  ❌ BUG 未修复")
        return False

def test_t006_script_flow_length():
    """T-006: 验证剧本流程长度（不应两轮就结局）"""
    print("\n" + "="*60)
    print("【T-006】剧本流程长度验证")
    print("="*60)
    
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取剧本列表
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
    
    # 3. 进行多轮对话
    print("\n[步骤 3] 进行多轮对话...")
    max_rounds = 10
    ended_at_round = None
    
    for round_num in range(1, max_rounds + 1):
        print(f"\n  --- 第 {round_num} 轮 ---")
        
        # 获取对话
        resp = requests.get(f"{BASE_URL}/game/{session_id}/dialogue", headers=headers)
        if resp.status_code != 200:
            print(f"  ❌ 获取对话失败: {resp.status_code}")
            return False
        
        dialogue = resp.json()
        is_ended = dialogue.get("is_ended", False)
        choices = dialogue.get("choices", [])
        
        print(f"  对话内容: {dialogue.get('text', '')[:100]}...")
        print(f"  是否结束: {is_ended}")
        print(f"  可选选择: {len(choices)} 个")
        
        if is_ended:
            print(f"  ️ 剧本在第 {round_num} 轮结束")
            ended_at_round = round_num
            break
        
        # 做出选择
        if choices:
            choice_id = choices[0].get("id")
            resp = requests.post(f"{BASE_URL}/game/{session_id}/choice", headers=headers, json={
                "choice_id": choice_id
            })
            if resp.status_code != 200:
                print(f"  ❌ 选择失败: {resp.status_code}")
                return False
            print(f"  ✅ 已选择: {choice_id}")
        else:
            print(f"  ⚠️ 没有可选选择")
            break
    
    # 4. 验证
    print("\n[步骤 4] 验证结果...")
    if ended_at_round is None:
        print(f"  ✅ 剧本进行了 {max_rounds} 轮仍未结束")
        print(f"  ✅ 流程长度正常（> 2 轮）")
        return True
    elif ended_at_round >= 5:
        print(f"  ✅ 剧本在第 {ended_at_round} 轮结束")
        print(f"  ✅ 流程长度正常（≥ 5 轮）")
        return True
    else:
        print(f"  ❌ 剧本在第 {ended_at_round} 轮就结束了")
        print(f"  ❌ 流程过短（< 5 轮）")
        return False

def test_t005_free_chat_history():
    """T-005: 验证自由对话历史持久化"""
    print("\n" + "="*60)
    print("【T-005】自由对话历史持久化验证")
    print("="*60)
    
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取剧本列表
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
    
    # 3. 第一次自由对话
    print("\n[步骤 3] 第一次自由对话...")
    resp = requests.post(f"{BASE_URL}/game/{session_id}/free-chat", headers=headers, json={
        "message": "你好，我想了解你的故事"
    })
    
    if resp.status_code != 200:
        print(f"  ❌ 自由对话失败: {resp.status_code}")
        return False
    
    response_1 = resp.json()
    reply_1 = response_1.get("reply", "")
    print(f"  AI 回复 1: {reply_1[:100]}...")
    
    # 4. 第二次自由对话
    print("\n[步骤 4] 第二次自由对话...")
    resp = requests.post(f"{BASE_URL}/game/{session_id}/free-chat", headers=headers, json={
        "message": "能告诉我更多关于你的事吗？"
    })
    
    if resp.status_code != 200:
        print(f"   自由对话失败: {resp.status_code}")
        return False
    
    response_2 = resp.json()
    reply_2 = response_2.get("reply", "")
    print(f"  AI 回复 2: {reply_2[:100]}...")
    
    # 5. 获取自由对话历史
    print("\n[步骤 5] 获取自由对话历史...")
    resp = requests.get(f"{BASE_URL}/game/{session_id}/free-chat/history", headers=headers)
    
    if resp.status_code != 200:
        print(f"  ❌ 获取历史失败: {resp.status_code}")
        print(f"  响应: {resp.text[:200]}")
        return False
    
    history = resp.json()
    print(f"  历史记录: {json.dumps(history, ensure_ascii=False)[:500]}")
    
    # 6. 验证历史包含之前的对话
    print("\n[步骤 6] 验证历史持久化...")
    history_str = json.dumps(history, ensure_ascii=False)
    
    has_first_message = "你好，我想了解你的故事" in history_str
    has_second_message = "能告诉我更多关于你的事吗？" in history_str
    
    if has_first_message and has_second_message:
        print(f"  ✅ 历史记录包含两次对话")
        print(f"  ✅ 对话历史已持久化")
        return True
    else:
        print(f"  ❌ 历史记录不完整")
        print(f"  包含第一条消息: {has_first_message}")
        print(f"  包含第二条消息: {has_second_message}")
        return False

def main():
    print("\n" + "="*60)
    print("CR-018 第二轮验证测试")
    print("="*60)
    
    results = {}
    
    # 测试 T-010: total_fragments
    try:
        results["T-010 total_fragments"] = test_t010_total_fragments()
    except Exception as e:
        print(f"\n❌ T-010 测试异常: {e}")
        results["T-010 total_fragments"] = False
    
    # 测试 T-006: 剧本流程长度
    try:
        results["T-006 剧本流程长度"] = test_t006_script_flow_length()
    except Exception as e:
        print(f"\n❌ T-006 测试异常: {e}")
        results["T-006 剧本流程长度"] = False
    
    # 测试 T-005: 自由对话历史
    try:
        results["T-005 自由对话历史"] = test_t005_free_chat_history()
    except Exception as e:
        print(f"\n❌ T-005 测试异常: {e}")
        results["T-005 自由对话历史"] = False
    
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
    
    # 输出 JSON 结果
    print("\n" + "="*60)
    print("JSON 结果")
    print("="*60)
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
