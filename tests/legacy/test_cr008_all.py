#!/usr/bin/env python3
"""Test all 18 CR-008 endpoints against API contract."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Get token
token_resp = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "cr008-test@isekai.dev",
    "password": "***",
    "display_name": "CR008 Test"
})
TOKEN = token_resp.json().get("access_token")
print(f"Token: {TOKEN[:20]}...")

headers = {"Authorization": f"Bearer {TOKEN}"}

def test_endpoint(name, method, path, expected_fields=None, auth=True):
    """Test a single endpoint."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Endpoint: {method} {path}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{path}", headers=headers if auth else {})
        elif method == "POST":
            resp = requests.post(f"{BASE_URL}{path}", headers=headers if auth else {}, json={})
        elif method == "PATCH":
            resp = requests.patch(f"{BASE_URL}{path}", headers=headers if auth else {}, json={})
        elif method == "DELETE":
            resp = requests.delete(f"{BASE_URL}{path}", headers=headers if auth else {})
        
        print(f"Status: {resp.status_code}")
        
        if resp.status_code in [200, 201, 204]:
            try:
                data = resp.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'array/null'}")
                
                if expected_fields:
                    missing = [f for f in expected_fields if f not in data]
                    if missing:
                        print(f"❌ Missing fields: {missing}")
                    else:
                        print(f"✅ All expected fields present")
                
                # Print sample data
                print(f"Sample: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                return True
            except:
                print(f"Response: {resp.text[:200]}")
                return True
        else:
            print(f"❌ Error: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

# Test all 18 endpoints
results = []

# P0 - 修复/新增（4 个）
results.append(("GET /ugc/posts", test_endpoint(
    "1. GET /api/v1/ugc/posts",
    "GET", "/ugc/posts",
    ["posts", "page", "page_size", "total"],
    auth=False
)))

results.append(("GET /characters", test_endpoint(
    "2. GET /api/v1/characters",
    "GET", "/characters",
    ["characters", "total"],
    auth=False
)))

results.append(("GET /gallery/collections", test_endpoint(
    "3. GET /api/v1/gallery/collections",
    "GET", "/gallery/collections",
    ["collections"],
    auth=True
)))

# P0 - 用户相关（5 个）
results.append(("GET /users/me", test_endpoint(
    "5. GET /api/v1/users/me",
    "GET", "/users/me",
    ["id", "email", "display_name", "avatar_url", "email_verified", 
     "subscription_tier", "preferred_genre", "locale", "onboarding_completed", "created_at"],
    auth=True
)))

results.append(("PATCH /users/me", test_endpoint(
    "6. PATCH /api/v1/users/me",
    "PATCH", "/users/me",
    ["id", "email", "display_name"],
    auth=True
)))

results.append(("POST /users/me/change-password", test_endpoint(
    "7. POST /api/v1/users/me/change-password",
    "POST", "/users/me/change-password",
    ["status", "message"],
    auth=True
)))

results.append(("GET /users/me/subscription", test_endpoint(
    "9. GET /api/v1/users/me/subscription",
    "GET", "/users/me/subscription",
    ["tier", "status", "trial_started_at", "trial_ends_at", "renew_at"],
    auth=True
)))

# P0 - 个人中心相关（9 个）
results.append(("GET /users/me/stats", test_endpoint(
    "10. GET /api/v1/users/me/stats",
    "GET", "/users/me/stats",
    ["scripts_completed", "total_play_time_minutes", "endings_unlocked", "cgs_collected", "total_dialogues"],
    auth=True
)))

results.append(("GET /users/me/asset", test_endpoint(
    "11. GET /api/v1/users/me/asset",
    "GET", "/users/me/asset",
    ["balance", "total_earned", "total_spent"],
    auth=True
)))

results.append(("GET /sign/info", test_endpoint(
    "12. GET /api/v1/sign/info",
    "GET", "/sign/info",
    ["checked_in_today", "streak_days", "total_checkins", "this_week", "next_milestone"],
    auth=True
)))

results.append(("GET /users/me/latest-save", test_endpoint(
    "13. GET /api/v1/users/me/latest-save",
    "GET", "/users/me/latest-save",
    ["id", "session_id", "script_id", "script_name", "character_name", "character_avatar", 
     "current_node_id", "label", "choice_count", "created_at", "updated_at"],
    auth=True
)))

results.append(("GET /users/me/memory/summary", test_endpoint(
    "14. GET /api/v1/users/me/memory/summary",
    "GET", "/users/me/memory/summary",
    ["total_memories", "recent", "is_full_available"],
    auth=True
)))

results.append(("GET /users/me/characters/bond", test_endpoint(
    "15. GET /api/v1/users/me/characters/bond",
    "GET", "/users/me/characters/bond",
    ["characters", "total"],
    auth=True
)))

results.append(("GET /users/me/endings", test_endpoint(
    "16. GET /api/v1/users/me/endings",
    "GET", "/users/me/endings",
    ["endings", "total_scripts", "total_endings_unlocked"],
    auth=True
)))

results.append(("GET /users/me/endings/recent", test_endpoint(
    "17. GET /api/v1/users/me/endings/recent",
    "GET", "/users/me/endings/recent",
    ["recent_endings", "total"],
    auth=True
)))

results.append(("GET /users/me/memory/full", test_endpoint(
    "18. GET /api/v1/users/me/memory/full",
    "GET", "/users/me/memory/full",
    ["memories", "total"],
    auth=True
)))

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
passed = sum(1 for _, r in results if r)
total = len(results)
print(f"Passed: {passed}/{total}")

for name, result in results:
    status = "✅" if result else "❌"
    print(f"{status} {name}")
