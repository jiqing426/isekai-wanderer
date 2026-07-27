#!/usr/bin/env python3
"""CR-016 双表适配验证 — 验证旧 API 向后兼容 + BUG-005 修复"""

import requests
import json
import uuid
import sys

BASE = "http://localhost:8000/api/v1"
CR = f"{BASE}/cr016"

def register_user():
    """注册新用户"""
    email = f"cr016_verify_{uuid.uuid4().hex[:8]}@test.com"
    r = requests.post(f"{BASE}/auth/register", json={
        "email": email,
        "password": "***",
        "nickname": "CR016Verify"
    })
    if r.status_code not in (200, 201):
        # 尝试登录
        r = requests.post(f"{BASE}/auth/login", json={
            "email": email,
            "password": "***"
        })
    data = r.json()
    return data.get("access_token"), email

def h(token):
    return {"Authorization": f"Bearer {token}"}

def main():
    print("=" * 70)
    print("CR-016 双表适配验证")
    print("=" * 70)
    
    # ========================================
    # 1. 验证旧 API 向后兼容
    # ========================================
    print("\n[1] 验证旧 API 向后兼容")
    print("-" * 70)
    
    token, email = register_user()
    print(f"测试用户: {email}")
    
    # 1.1 旧 API: /subscription/status
    print("\n1.1 GET /subscription/status (旧 API)")
    r = requests.get(f"{BASE}/subscription/status", headers=h(token))
    print(f"  HTTP {r.status_code}")
    if r.status_code == 200:
        d = r.json()
        print(f"  响应: {json.dumps(d, indent=2)[:300]}")
        # 检查是否返回合理格式
        if "tier" in d or "currentPlanId" in d or "plan_id" in d:
            print("  ✅ 旧 API 可访问，返回格式正常")
        else:
            print("  ⚠️ 旧 API 返回格式异常")
    else:
        print(f"  ❌ 旧 API 失败: {r.text[:200]}")
    
    # 1.2 新 API: /cr016/subscription/status
    print("\n1.2 GET /cr016/subscription/status (新 API)")
    r = requests.get(f"{CR}/subscription/status", headers=h(token))
    print(f"  HTTP {r.status_code}")
    if r.status_code == 200:
        d = r.json()
        print(f"  响应: {json.dumps(d, indent=2)[:300]}")
        if d.get("tier") == "free":
            print("  ✅ 新 API 正常，tier=free")
        else:
            print(f"  ⚠️ 新 API tier={d.get('tier')}")
    else:
        print(f"  ❌ 新 API 失败: {r.text[:200]}")
    
    # 1.3 旧 API: /subscription/cancel (无订阅时应返回错误)
    print("\n1.3 POST /subscription/cancel (旧 API, 无订阅)")
    r = requests.post(f"{BASE}/subscription/cancel", headers=h(token))
    print(f"  HTTP {r.status_code}")
    if r.status_code in (400, 404, 409):
        print(f"  ✅ 旧 API 正确拒绝: {r.json().get('error_code', r.json().get('message', ''))[:100]}")
    elif r.status_code == 200:
        print(f"  ⚠️ 旧 API 意外成功: {r.json()}")
    else:
        print(f"  ❌ 旧 API 异常: {r.text[:200]}")
    
    # ========================================
    # 2. 验证 BUG-005 修复（quota 随订阅更新）
    # ========================================
    print("\n[2] 验证 BUG-005 修复")
    print("-" * 70)
    
    # 2.1 创建订阅前检查 quota
    print("\n2.1 创建订阅前 quota status")
    r = requests.get(f"{CR}/dialogue/quota/status", headers=h(token))
    if r.status_code == 200:
        before = r.json()
        print(f"  base_quota={before.get('base_quota')}, remaining={before.get('remaining')}, is_exempt={before.get('is_exempt')}")
    else:
        print(f"  ❌ 获取 quota 失败: {r.status_code}")
        return
    
    # 2.2 创建 Basic 订阅
    print("\n2.2 创建 Basic 订阅")
    r = requests.post(f"{CR}/subscription/create", headers=h(token), json={
        "tier": "basic",
        "cycle": "monthly"
    })
    if r.status_code != 200:
        print(f"  ❌ 创建订阅失败: {r.status_code} {r.text[:200]}")
        return
    sub = r.json()
    print(f"  ✅ 订阅创建成功: tier={sub.get('tier')}, status={sub.get('status')}")
    
    # 2.3 创建订阅后检查 quota
    print("\n2.3 创建订阅后 quota status")
    r = requests.get(f"{CR}/dialogue/quota/status", headers=h(token))
    if r.status_code == 200:
        after = r.json()
        print(f"  base_quota={after.get('base_quota')}, remaining={after.get('remaining')}, is_exempt={after.get('is_exempt')}")
        
        # BUG-005 验证：订阅后 quota 应反映订阅档位
        if after.get('is_exempt') == True and after.get('remaining') == -1:
            print("  ✅ BUG-005 已修复：订阅用户 quota 正确更新 (is_exempt=true, remaining=-1)")
        elif after.get('is_exempt') == True and after.get('remaining') == 10:
            print("  ❌ BUG-005 未修复：订阅用户 quota 未更新 (is_exempt=true 但 remaining=10)")
        elif after.get('is_exempt') == False:
            print("  ❌ BUG-005 未修复：订阅用户未被识别为 exempt")
        else:
            print(f"  ⚠️ 需要人工检查: {after}")
    else:
        print(f"  ❌ 获取 quota 失败: {r.status_code}")
    
    # 2.4 验证 subscription status 也正确
    print("\n2.4 验证 subscription status")
    r = requests.get(f"{CR}/subscription/status", headers=h(token))
    if r.status_code == 200:
        status = r.json()
        print(f"  tier={status.get('tier')}, is_exempt_from_quota={status.get('is_exempt_from_quota')}")
        if status.get('tier') == 'basic' and status.get('is_exempt_from_quota') == True:
            print("  ✅ subscription status 正确")
        else:
            print(f"  ⚠️ subscription status 异常: {status}")
    
    # 2.5 取消订阅
    print("\n2.5 取消订阅")
    r = requests.post(f"{CR}/subscription/cancel", headers=h(token))
    if r.status_code == 200:
        print(f"  ✅ 取消成功: {r.json().get('status')}")
    else:
        print(f"  ❌ 取消失败: {r.status_code} {r.text[:200]}")
    
    # ========================================
    # 3. 检查前端 API 路径 (BUG-006)
    # ========================================
    print("\n[3] 检查前端 API 路径 (BUG-006)")
    print("-" * 70)
    
    try:
        with open("/root/isekai-wanderer/frontend/src/api/subscription.ts", "r") as f:
            content = f.read()
        
        # 检查是否使用新路径
        uses_new = "/cr016/" in content
        uses_old_status = "'/subscription/status'" in content or '"/subscription/status"' in content
        uses_old_quota = "'/dialogue/quota'" in content or '"/dialogue/quota"' in content
        
        print(f"  使用新路径 /cr016/: {uses_new}")
        print(f"  使用旧路径 /subscription/status: {uses_old_status}")
        print(f"  使用旧路径 /dialogue/quota: {uses_old_quota}")
        
        if uses_new and not uses_old_status and not uses_old_quota:
            print("  ✅ BUG-006 已修复：前端使用新路径")
        elif uses_old_status or uses_old_quota:
            print("  ❌ BUG-006 未修复：前端仍使用旧路径")
        else:
            print("  ⚠️ 需要人工检查前端代码")
    except Exception as e:
        print(f"  ❌ 读取前端代码失败: {e}")
    
    print("\n" + "=" * 70)
    print("验证完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
