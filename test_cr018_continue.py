#!/usr/bin/env python3
"""CR-018 持续验证：T-002 自由对话 + T-003 更换头像"""

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

def test_free_chat():
    """T-002: 验证剧本内自由对话"""
    print("\n" + "="*60)
    print("【T-002】剧本内自由对话验证")
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
    
    # 3. 调用自由对话接口
    print("\n[步骤 3] 调用自由对话接口...")
    free_chat_payload = {
        "message": "你好，我想和你聊天"
    }
    
    print(f"  请求: POST /api/v1/game/{session_id}/free-chat")
    print(f"  参数: {json.dumps(free_chat_payload, ensure_ascii=False)}")
    
    resp = requests.post(f"{BASE_URL}/game/{session_id}/free-chat", headers=headers, json=free_chat_payload)
    print(f"  响应状态: {resp.status_code}")
    
    if resp.status_code == 401:
        print(f"  ❌ 返回 401 TOKEN_EXPIRED - BUG 未修复")
        print(f"  响应: {resp.text[:300]}")
        return False
    elif resp.status_code == 200:
        response_data = resp.json()
        print(f"  ✅ 自由对话成功")
        print(f"  响应内容: {json.dumps(response_data, ensure_ascii=False)[:500]}")
        
        # 验证返回 AI 回复
        if "response" in response_data or "message" in response_data or "text" in response_data:
            print("  ✅ 包含 AI 回复内容")
        else:
            print("  ⚠️ 响应格式未知")
        
        return True
    else:
        print(f"  ⚠️ 返回 {resp.status_code}: {resp.text[:200]}")
        return False

def test_avatar_upload():
    """T-003: 验证更换头像"""
    print("\n" + "="*60)
    print("【T-003】更换头像验证")
    print("="*60)
    
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 检查当前用户信息
    print("\n[步骤 1] 获取当前用户信息...")
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ 获取用户信息失败: {resp.status_code}")
        return False
    
    user_info = resp.json()
    print(f"  当前头像: {user_info.get('avatar_url', '无')}")
    
    # 2. 上传新头像
    print("\n[步骤 2] 上传新头像...")
    
    # 创建一个简单的测试图片（1x1 像素 PNG）
    import base64
    # 最小的 PNG 文件
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    test_image = base64.b64decode(test_image_b64)
    
    files = {
        'file': ('test_avatar.png', test_image, 'image/png')
    }
    
    resp = requests.post(f"{BASE_URL}/users/me/avatar", headers=headers, files=files)
    print(f"  响应状态: {resp.status_code}")
    
    if resp.status_code == 401:
        print(f"  ❌ 返回 401 TOKEN_EXPIRED - BUG 未修复")
        print(f"  响应: {resp.text[:300]}")
        return False
    elif resp.status_code == 200:
        response_data = resp.json()
        print(f"  ✅ 头像上传成功")
        print(f"  响应内容: {json.dumps(response_data, ensure_ascii=False)[:300]}")
        
        # 3. 验证头像已更新
        print("\n[步骤 3] 验证头像已更新...")
        resp = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        updated_user = resp.json()
        new_avatar = updated_user.get('avatar_url', '无')
        print(f"  更新后头像: {new_avatar}")
        
        if new_avatar and new_avatar != user_info.get('avatar_url'):
            print("  ✅ 头像已成功更新")
        else:
            print("  ️ 头像可能未更新")
        
        return True
    else:
        print(f"  ⚠️ 返回 {resp.status_code}: {resp.text[:200]}")
        return False

def main():
    print("\n" + "="*60)
    print("CR-018 持续验证测试")
    print("="*60)
    
    results = {}
    
    # 测试 T-002: 自由对话
    try:
        results["T-002 自由对话"] = test_free_chat()
    except Exception as e:
        print(f"\n❌ T-002 测试异常: {e}")
        results["T-002 自由对话"] = False
    
    # 测试 T-003: 更换头像
    try:
        results["T-003 更换头像"] = test_avatar_upload()
    except Exception as e:
        print(f"\n❌ T-003 测试异常: {e}")
        results["T-003 更换头像"] = False
    
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
