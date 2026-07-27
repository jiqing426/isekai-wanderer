#!/usr/bin/env python3
"""CR-017 解锁动效系统 API 测试"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
CR017_BASE = f"{BASE_URL}/cr017"

# 测试用户凭证
def get_test_token():
    """获取测试用户token"""
    # 尝试登录 CR-017 测试用户
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "cr017_test@test.com",
        "password": "***"
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    
    # 如果不存在，注册新用户
    import time
    new_email = f'cr017_test_{int(time.time())}@test.com'
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": new_email,
        "password": "***",
        "nickname": "CR017测试"
    })
    if resp.status_code in [200, 201]:
        return resp.json()["access_token"]
    
    raise Exception(f"无法获取测试用户token: {resp.text}")

def test_tc001_record_cg_unlock():
    """TC-001: 记录 CG 解锁"""
    print("\n[TC-001] 记录 CG 解锁")
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "unlock_type": "cg",
        "content_id": "cg_test_001",
        "rarity": "SR",
        "title": "测试CG",
        "description": "测试用CG解锁"
    }
    
    resp = requests.post(f"{CR017_BASE}/unlock/record", json=payload, headers=headers)
    print(f"  响应状态: {resp.status_code}")
    print(f"  响应内容: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
    
    assert resp.status_code == 200, f"期望200，实际{resp.status_code}"
    data = resp.json()
    assert "id" in data, "应返回解锁记录ID"
    assert data["unlock_type"] == "cg", "unlock_type应为cg"
    assert data["rarity"] == "SR", "rarity应为SR"
    print("  ✓ TC-001 通过")

def test_tc002_record_achievement_unlock():
    """TC-002: 记录成就解锁"""
    print("\n[TC-002] 记录成就解锁")
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "unlock_type": "achievement",
        "content_id": "achievement_test_001",
        "rarity": "R",
        "title": "测试成就",
        "description": "测试用成就解锁"
    }
    
    resp = requests.post(f"{CR017_BASE}/unlock/record", json=payload, headers=headers)
    print(f"  响应状态: {resp.status_code}")
    print(f"  响应内容: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
    
    assert resp.status_code == 200, f"期望200，实际{resp.status_code}"
    data = resp.json()
    assert "id" in data, "应返回解锁记录ID"
    assert data["unlock_type"] == "achievement", "unlock_type应为achievement"
    print("  ✓ TC-002 通过")

def test_tc003_query_unlock_list():
    """TC-003: 查询解锁列表"""
    print("\n[TC-003] 查询解锁列表")
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 先记录2个解锁
    for i in range(2):
        payload = {
            "unlock_type": "cg",
            "content_id": f"cg_list_test_{i}",
            "rarity": "R",
            "title": f"列表测试CG {i}",
            "description": f"测试用CG {i}"
        }
        requests.post(f"{CR017_BASE}/unlock/record", json=payload, headers=headers)
    
    # 查询列表
    resp = requests.get(f"{CR017_BASE}/unlock/list", headers=headers)
    print(f"  响应状态: {resp.status_code}")
    data = resp.json()
    print(f"  返回记录数: {len(data.get('records', []))}")
    
    assert resp.status_code == 200, f"期望200，实际{resp.status_code}"
    assert "records" in data, "应返回records字段"
    assert len(data["records"]) >= 2, f"应至少有2条记录，实际{len(data['records'])}"
    print("  ✓ TC-003 通过")

def test_tc004_get_pending_unlocks():
    """TC-004: 获取未查看解锁"""
    print("\n[TC-004] 获取未查看解锁")
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 记录一个新解锁
    payload = {
        "unlock_type": "cg",
        "content_id": f"cg_pending_test_{int(time.time())}",
        "rarity": "SR",
        "title": "待查看测试CG",
        "description": "测试未查看状态"
    }
    requests.post(f"{CR017_BASE}/unlock/record", json=payload, headers=headers)
    
    # 获取未查看解锁
    resp = requests.get(f"{CR017_BASE}/unlock/pending", headers=headers)
    print(f"  响应状态: {resp.status_code}")
    data = resp.json()
    print(f"  未查看记录数: {len(data.get('pending_unlocks', []))}")
    
    assert resp.status_code == 200, f"期望200，实际{resp.status_code}"
    assert "records" in data, "应返回records字段"
    assert data["total"] >= 1, f"应至少有1条未查看记录，实际{data['total']}"
    print("  ✓ TC-004 通过")

def test_tc005_mark_viewed():
    """TC-005: 标记已查看"""
    print("\n[TC-005] 标记已查看")
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 先记录一个解锁
    payload = {
        "unlock_type": "cg",
        "content_id": f"cg_viewed_test_{int(time.time())}",
        "rarity": "R",
        "title": "标记查看测试CG",
        "description": "测试标记查看"
    }
    record_resp = requests.post(f"{CR017_BASE}/unlock/record", json=payload, headers=headers)
    record_id = record_resp.json().get("id")
    
    # 标记为已查看
    mark_payload = {"record_id": record_id}
    resp = requests.post(f"{CR017_BASE}/unlock/mark-viewed", json=mark_payload, headers=headers)
    print(f"  响应状态: {resp.status_code}")
    print(f"  响应内容: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
    
    assert resp.status_code == 200, f"期望200，实际{resp.status_code}"
    data = resp.json()
    assert data.get("success") == True, "success应为True"
    assert data.get("viewed") == True, "viewed应为True"
    print("  ✓ TC-005 通过")

def test_tc006_batch_record():
    """TC-006: 批量记录解锁"""
    print("\n[TC-006] 批量记录解锁")
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    batch_payload = {
        "unlocks": [
            {
                "unlock_type": "cg",
                "content_id": f"cg_batch_{int(time.time())}_1",
                "rarity": "R",
                "title": "批量测试CG 1",
                "description": "批量测试1"
            },
            {
                "unlock_type": "achievement",
                "content_id": f"ach_batch_{int(time.time())}_2",
                "rarity": "SR",
                "title": "批量测试成就 2",
                "description": "批量测试2"
            },
            {
                "unlock_type": "cg",
                "content_id": f"cg_batch_{int(time.time())}_3",
                "rarity": "SSR",
                "title": "批量测试CG 3",
                "description": "批量测试3"
            }
        ]
    }
    
    resp = requests.post(f"{CR017_BASE}/unlock/batch", json=batch_payload, headers=headers)
    print(f"  响应状态: {resp.status_code}")
    data = resp.json()
    print(f"  成功创建记录数: {len(data.get('created_ids', []))}")
    
    assert resp.status_code == 200, f"期望200，实际{resp.status_code}"
    assert data.get("success") == True, "success应为True"
    assert data.get("recorded_count") == 3, f"应创建3条记录，实际{data.get('recorded_count')}"
    assert len(data.get("records", [])) == 3, f"应返回3条records，实际{len(data.get('records', []))}"
    print("  ✓ TC-006 通过")

def test_tc007_rarity_validation():
    """TC-007: 稀有度验证"""
    print("\n[TC-007] 稀有度验证")
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    rarities = ["R", "SR", "SSR"]
    for rarity in rarities:
        payload = {
            "unlock_type": "cg",
            "content_id": f"cg_rarity_{rarity}_{int(time.time())}",
            "rarity": rarity,
            "title": f"稀有度测试 {rarity}",
            "description": f"测试{rarity}稀有度"
        }
        resp = requests.post(f"{CR017_BASE}/unlock/record", json=payload, headers=headers)
        print(f"  {rarity} 响应状态: {resp.status_code}")
        
        assert resp.status_code == 200, f"{rarity}期望200，实际{resp.status_code}"
        data = resp.json()
        assert data.get("rarity") == rarity, f"{rarity}rarity应为{rarity}，实际{data.get('rarity')}"
    
    print("  ✓ TC-007 通过")

def main():
    print("=" * 60)
    print("CR-017 解锁动效系统 API 测试")
    print("=" * 60)
    
    try:
        test_tc001_record_cg_unlock()
        test_tc002_record_achievement_unlock()
        test_tc003_query_unlock_list()
        test_tc004_get_pending_unlocks()
        test_tc005_mark_viewed()
        test_tc006_batch_record()
        test_tc007_rarity_validation()
        
        print("\n" + "=" * 60)
        print("测试结果: 7/7 通过 ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
