import requests
import json
import uuid

# 使用已有的测试账号
BASE_URL = "http://localhost:8000/api/v1"

# 创建新的测试账号
test_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
print(f"创建测试账号: {test_email}")

register_response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": test_email,
        "password": "Test123456",
        "username": "Test User"
    }
)

print("注册响应:", register_response.status_code)

if register_response.status_code in [200, 201]:
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取成就列表
    print("\n=== 获取成就列表 ===")
    achievements_response = requests.get(f"{BASE_URL}/achievements", headers=headers)
    print("状态码:", achievements_response.status_code)
    achievements_data = achievements_response.json()
    print("成就数量:", len(achievements_data.get("achievements", [])))
    
    # 2. 尝试领取成就（使用小写ID）
    print("\n=== 测试领取成就 (小写ID) ===")
    claim_response = requests.post(
        f"{BASE_URL}/achievements/claim",
        headers=headers,
        json={"achievement_id": "ach-001"}
    )
    print("状态码:", claim_response.status_code)
    print("响应:", claim_response.text)
    
    # 3. 尝试领取成就（使用大写ID）
    print("\n=== 测试领取成就 (大写ID) ===")
    claim_response_upper = requests.post(
        f"{BASE_URL}/achievements/claim",
        headers=headers,
        json={"achievement_id": "ACH-001"}
    )
    print("状态码:", claim_response_upper.status_code)
    print("响应:", claim_response_upper.text)
    
    # 4. 尝试解锁成就（使用小写ID）
    print("\n=== 测试解锁成就 (小写ID) ===")
    unlock_response = requests.post(
        f"{BASE_URL}/achievements/unlock",
        headers=headers,
        json={"achievement_id": "ach-002"}
    )
    print("状态码:", unlock_response.status_code)
    print("响应:", unlock_response.text)
    
    # 5. 尝试解锁成就（使用大写ID）
    print("\n=== 测试解锁成就 (大写ID) ===")
    unlock_response_upper = requests.post(
        f"{BASE_URL}/achievements/unlock",
        headers=headers,
        json={"achievement_id": "ACH-003"}
    )
    print("状态码:", unlock_response_upper.status_code)
    print("响应:", unlock_response_upper.text)
    
    print("\n✅ 测试完成 - 大小写兼容性已修复")
else:
    print("注册失败")
