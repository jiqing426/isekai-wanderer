import requests
import uuid

BASE_URL = "http://localhost:8000/api/v1"

# 创建测试账号
test_email = f"check_{uuid.uuid4().hex[:8]}@test.com"
register_response = requests.post(
    f"{BASE_URL}/auth/register",
    json={"email": test_email, "password": "Test123456", "username": "Check"}
)
token = register_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 获取成就列表
response = requests.get(f"{BASE_URL}/achievements", headers=headers)
achievements = response.json()["achievements"]

print("成就字段结构:")
if achievements:
    print(f"第一个成就: {achievements[0]}")
    print(f"\n所有字段: {list(achievements[0].keys())}")
