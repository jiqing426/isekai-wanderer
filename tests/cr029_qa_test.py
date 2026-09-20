#!/usr/bin/env python3
"""
CR-029 QA Test Script
验证节点分支功能：不同角色看到不同节点
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """登录获取 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@test.com",
        "password": "Test123456！"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"Login failed: {response.text}")

def create_session(token, script_id, character_id):
    """创建游戏会话"""
    response = requests.post(
        f"{BASE_URL}/game/start",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "script_id": script_id,
            "character_id": character_id
        }
    )
    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        
        # 检查会话状态，如果是已完成的会话，尝试获取对话确认
        dialogue_resp = requests.get(
            f"{BASE_URL}/game/{session_id}/dialogue",
            headers={"Authorization": f"Bearer {token}"}
        )
        if dialogue_resp.status_code == 200:
            dialogue_data = dialogue_resp.json()
            # 如果是ending类型，说明是旧会话，需要标记
            if dialogue_data.get("type") == "ending":
                return session_id, True  # 返回session_id和is_ended标志
        
        return session_id, False
    raise Exception(f"Create session failed: {response.text}")

def get_dialogue(token, session_id):
    """获取对话内容"""
    response = requests.get(
        f"{BASE_URL}/game/{session_id}/dialogue",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Get dialogue failed: {response.text}")

def submit_choice(token, session_id, choice_id):
    """提交选择"""
    response = requests.post(
        f"{BASE_URL}/game/{session_id}/choice",
        headers={"Authorization": f"Bearer {token}"},
        json={"choice_id": choice_id}
    )
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Submit choice failed: {response.text}")

def extract_node_info(dialogue):
    """从对话响应中提取节点信息"""
    current_node = dialogue.get("current_node", {})
    node_id = current_node.get("id")
    content = current_node.get("content", {})
    text = content.get("text", "")
    return node_id, text

def test_character_filtering():
    """测试角色过滤功能"""
    print("=" * 60)
    print("CR-029 QA Test: Character Node Filtering")
    print("=" * 60)
    
    # 登录
    print("\n[1] 登录...")
    token = login()
    print(f"✓ 登录成功")
    
    # 测试数据
    script_id = "de1c935a-3e82-4e29-aff9-c69c3a460418"  # 星月奇缘
    characters = [
        ("沈星澜", "900a9744-04ca-4c6b-a276-c79595218672"),
        ("白夜", "0dfedba2-1f5d-417d-a6a8-74f52d954a46"),
        ("暮雪", "dd7dacc0-fea8-434d-b63b-f4efbe4de615"),
    ]
    
    sessions = {}
    
    # 为每个角色创建会话
    print("\n[2] 创建游戏会话...")
    for name, char_id in characters:
        session_id, is_ended = create_session(token, script_id, char_id)
        sessions[name] = session_id
        status = "(ended)" if is_ended else "(active)"
        print(f"  ✓ {name}: {session_id} {status}")
    
    # 获取每个角色的初始对话（应该相同）
    print("\n[3] 获取初始对话...")
    initial_node_ids = {}
    initial_dialogues = {}
    for name, session_id in sessions.items():
        dialogue = get_dialogue(token, session_id)
        initial_dialogues[name] = dialogue
        node_id, text = extract_node_info(dialogue)
        initial_node_ids[name] = node_id
        print(f"\n  {name}:")
        print(f"    Node ID: {node_id}")
        print(f"    Text: {text[:80]}...")
    
    # 验证初始节点相同
    print("\n[4] 验证初始节点...")
    unique_initial_nodes = set(initial_node_ids.values())
    print(f"  唯一初始节点数: {len(unique_initial_nodes)}")
    print(f"  节点分布: {initial_node_ids}")
    
    if len(unique_initial_nodes) != 1:
        print("\n✗ 测试失败: 不同角色的初始节点不同")
        return False
    print("  ✓ 所有角色从同一初始节点开始")
    
    # 获取初始节点的选择项
    print("\n[5] 获取选择项...")
    first_dialogue = initial_dialogues[characters[0][0]]
    choices = first_dialogue.get("choices", [])
    
    # 如果初始节点没有足够的选择项，需要导航到有3个选择项的节点
    if len(choices) < 3:
        print(f"  初始节点只有 {len(choices)} 个选择项，需要导航到分支选择节点...")
        
        # 选择第一个选项继续
        if len(choices) > 0:
            choice_id = choices[0]["id"]
            print(f"  选择: {choices[0].get('text', 'N/A')}")
            
            for name, session_id in sessions.items():
                submit_choice(token, session_id, choice_id)
            
            # 重新获取对话
            print("\n[6] 获取分支选择节点的对话...")
            branch_dialogues = {}
            for name, session_id in sessions.items():
                dialogue = get_dialogue(token, session_id)
                branch_dialogues[name] = dialogue
                node_id, text = extract_node_info(dialogue)
                print(f"\n  {name}:")
                print(f"    Node ID: {node_id}")
                print(f"    Text: {text[:80]}...")
            
            # 获取分支选择节点的选择项
            first_branch_dialogue = branch_dialogues[characters[0][0]]
            choices = first_branch_dialogue.get("choices", [])
            print(f"\n  找到 {len(choices)} 个选择项")
            for i, choice in enumerate(choices):
                print(f"    {i+1}. {choice.get('text', 'N/A')}")
            
            # 为每个角色选择不同的选项
            print("\n[7] 为每个角色选择不同的选项...")
            branch_node_ids = {}
            for i, (name, session_id) in enumerate(sessions.items()):
                if i < len(choices):
                    choice_id = choices[i]["id"]
                    print(f"  {name} 选择: {choices[i].get('text', 'N/A')}")
                    
                    result = submit_choice(token, session_id, choice_id)
                    
                    # 获取选择后的对话
                    dialogue = get_dialogue(token, session_id)
                    node_id, text = extract_node_info(dialogue)
                    branch_node_ids[name] = node_id
                    print(f"    → Node ID: {node_id}")
                    print(f"    → Text: {text[:80]}...")
        else:
            print("\n✗ 测试失败: 没有可用的选择项")
            return False
    else:
        print(f"  ✓ 找到 {len(choices)} 个选择项")
        for i, choice in enumerate(choices):
            print(f"    {i+1}. {choice.get('text', 'N/A')}")
        
        # 为每个角色选择不同的选项
        print("\n[6] 为每个角色选择不同的选项...")
        branch_node_ids = {}
        for i, (name, session_id) in enumerate(sessions.items()):
            choice_id = choices[i]["id"]
            print(f"  {name} 选择: {choices[i].get('text', 'N/A')}")
            
            result = submit_choice(token, session_id, choice_id)
            
            # 获取选择后的对话
            dialogue = get_dialogue(token, session_id)
            node_id, text = extract_node_info(dialogue)
            branch_node_ids[name] = node_id
            print(f"    → Node ID: {node_id}")
            print(f"    → Text: {text[:80]}...")
    
    # 验证分支节点
    print("\n[8] 验证角色分支节点...")
    unique_branch_nodes = set(branch_node_ids.values())
    print(f"  唯一分支节点数: {len(unique_branch_nodes)}")
    print(f"  节点分布: {branch_node_ids}")
    
    # 验证分支节点存在（使用新的UUID v4格式）
    branch_nodes = [
        "17f71833-c529-4610-aebd-5a349bdf1e84",  # 沈星澜
        "76585918-46f8-48b9-a8b1-a2a13f6f0205",  # 白夜
        "fa1cd260-7f69-4b29-bd05-7a94aafd0eee",  # 暮雪
    ]
    
    found_branches = [nid for nid in branch_node_ids.values() if nid in branch_nodes]
    print(f"  找到分支节点: {len(found_branches)}/3")
    
    if len(unique_branch_nodes) == 3 and len(found_branches) == 3:
        print("\n✓ 测试通过: 不同角色进入不同的分支节点")
        return True
    else:
        print("\n✗ 测试失败: 未检测到角色特定的分支节点")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 60)
    print("CR-029 QA Test: Backward Compatibility")
    print("=" * 60)
    
    print("\n[1] 登录...")
    token = login()
    print(f"✓ 登录成功")
    
    print("\n[2] 创建不带 character_id 的会话...")
    script_id = "de1c935a-3e82-4e29-aff9-c69c3a460418"
    
    response = requests.post(
        f"{BASE_URL}/game/start",
        headers={"Authorization": f"Bearer {token}"},
        json={"script_id": script_id}
    )
    
    if response.status_code == 200:
        session_id = response.json()["session_id"]
        print(f"  ✓ 会话创建成功: {session_id}")
        
        print("\n[3] 获取对话...")
        dialogue = get_dialogue(token, session_id)
        node_id, text = extract_node_info(dialogue)
        print(f"  ✓ 对话获取成功: {node_id}")
        
        print("\n✓ 向后兼容性测试通过")
        return True
    else:
        print(f"  ✗ 会话创建失败: {response.text}")
        return False

if __name__ == "__main__":
    try:
        result1 = test_character_filtering()
        result2 = test_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"  角色过滤测试: {'✓ 通过' if result1 else '✗ 失败'}")
        print(f"  向后兼容测试: {'✓ 通过' if result2 else '✗ 失败'}")
        
        if result1 and result2:
            print("\n✓ 所有测试通过")
            exit(0)
        else:
            print("\n✗ 部分测试失败")
            exit(1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
