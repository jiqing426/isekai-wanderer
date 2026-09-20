import requests
import json

BASE = "http://localhost:8000/api/v1"
TOKEN_RESP = requests.post(f"{BASE}/auth/login", json={"email":"test@example.com","password":"***"})
TOKEN = TOKEN_RESP.json()["access_token"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

print("=== CR-013: 剧本详情API ===")
r = requests.get(f"{BASE}/scripts/11111111-1111-1111-1111-111111111111/detail", headers=HEADERS)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Title: {data.get('title')}")
    print(f"Chapters: {len(data.get('chapters', []))}")
    print(f"Total nodes: {data.get('totalNodes')}")
    print(f"Unlocked: {data.get('unlockedNodes')}")
else:
    print(f"Error: {r.text}")

print("\n=== CR-014: 成就系统API ===")
r = requests.get(f"{BASE}/achievements", headers=HEADERS)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Total: {data.get('total')}")
    print(f"Unlocked: {data.get('unlockedCount')}")
    print(f"First achievement: {data.get('achievements', [{}])[0].get('name')}")
else:
    print(f"Error: {r.text}")

print("\n=== CR-015: 角色设定API ===")
r = requests.get(f"{BASE}/characters/char-001/detail", headers=HEADERS)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Name: {data.get('name')}")
    print(f"NameEn: {data.get('nameEn')}")
    print(f"Personality: {data.get('personality', {}).get('tags')}")
else:
    print(f"Error: {r.text}")

print("\n=== CR-015: AI对话校验 ===")
r = requests.post(f"{BASE}/ai/validate-dialogue", headers=HEADERS, json={
    "characterId": "char-001",
    "dialogue": "你好，我是玩家"
})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Valid: {data.get('valid')}")
    print(f"Score: {data.get('score')}")
else:
    print(f"Error: {r.text}")
