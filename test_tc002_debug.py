#!/usr/bin/env python3
"""Debug TC-002: investigate choice endpoint and quota consumption."""
import requests, json, uuid

BASE = "http://localhost:8000/api/v1"
CR = f"{BASE}/cr016"

# Register
r = requests.post(f"{BASE}/auth/register", json={
    "email": f"tc002_{uuid.uuid4().hex[:6]}@test.com",
    "password": "***", "nickname": "TC002"
})
token = r.json().get("access_token")
h = {"Authorization": f"Bearer {token}"}
print(f"Token obtained: {token[:20]}...")

# Check initial quota
r = requests.get(f"{CR}/dialogue/quota/status", headers=h)
print(f"\n=== Initial Quota ===")
print(json.dumps(r.json(), indent=2))

# Get scripts
r = requests.get(f"{BASE}/scripts", headers=h)
scripts = r.json().get("scripts", [])
script_id = scripts[0]["id"]
print(f"\nUsing script: {script_id}")

# Start game
r = requests.post(f"{BASE}/game/start", headers=h, json={"script_id": script_id})
print(f"\n=== Start Game (HTTP {r.status_code}) ===")
game = r.json()
print(json.dumps(game, indent=2)[:500])
session_id = game.get("session_id") or game.get("id")

# Get dialogue
r = requests.get(f"{BASE}/game/{session_id}/dialogue", headers=h)
print(f"\n=== GET Dialogue (HTTP {r.status_code}) ===")
dialogue = r.json() if r.status_code == 200 else {}
print(json.dumps(dialogue, indent=2)[:2000])

# Look for choices in dialogue response
choices = dialogue.get("choices", dialogue.get("options", []))
print(f"\n=== Choices found: {len(choices)} ===")
if choices:
    for c in choices[:5]:
        print(f"  choice: {json.dumps(c)[:200]}")
    # Try with first valid choice
    choice_id = choices[0].get("id") or choices[0].get("choice_id")
    print(f"\nUsing choice_id: {choice_id}")
else:
    # Try UUID format
    choice_id = str(uuid.uuid4())
    print(f"\nNo choices found, using random UUID: {choice_id}")

# Submit choice
print(f"\n=== POST Choice ===")
r = requests.post(f"{BASE}/game/{session_id}/choice", headers=h, json={
    "choice_id": choice_id, "choice_text": "Test choice"
})
print(f"HTTP {r.status_code}")
print(json.dumps(r.json(), indent=2)[:1000])

# Check quota after
r = requests.get(f"{CR}/dialogue/quota/status", headers=h)
print(f"\n=== Quota After Choice ===")
print(json.dumps(r.json(), indent=2))
