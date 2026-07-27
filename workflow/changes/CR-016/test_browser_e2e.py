#!/usr/bin/env python3
"""
CR-016 Browser E2E Test
验证前端页面集成 CR-016 API
"""
import requests
import json

# 测试前端页面是否可访问
FRONTEND_URL = "http://localhost:8081"

def test_frontend_pages():
    """测试关键前端页面"""
    pages = [
        ("/", "首页"),
        ("/subscription", "订阅页面"),
    ]
    
    results = []
    for path, name in pages:
        try:
            resp = requests.get(f"{FRONTEND_URL}{path}", timeout=5)
            status = "PASS" if resp.status_code == 200 else "FAIL"
            results.append({
                "page": name,
                "path": path,
                "status": status,
                "http_code": resp.status_code
            })
            print(f"{status} {name} ({path}): HTTP {resp.status_code}")
        except Exception as e:
            results.append({
                "page": name,
                "path": path,
                "status": "FAIL",
                "error": str(e)
            })
            print(f"FAIL {name} ({path}): {e}")
    
    return results

def test_api_integration():
    """测试前端调用的 API 路径"""
    # 注册测试用户
    auth_resp = requests.post("http://localhost:8000/api/v1/auth/register", json={
        "email": "browser_e2e@test.com",
        "password": "***",
        "nickname": "BrowserE2E"
    })
    
    if auth_resp.status_code not in [200, 201]:
        # 尝试登录
        auth_resp = requests.post("http://localhost:8000/api/v1/auth/login", json={
            "email": "browser_e2e@test.com",
            "password": "***"
        })
    
    if auth_resp.status_code not in [200, 201]:
        print(f"FAIL 无法创建测试用户: {auth_resp.status_code}")
        return []
    
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试前端调用的 API 路径（旧路径）
    api_tests = [
        ("GET", "/api/v1/subscription/status", "订阅状态（旧路径）"),
        ("GET", "/api/v1/dialogue/quota/status", "对话额度（旧路径）"),
        ("GET", "/api/v1/cr016/subscription/status", "订阅状态（新路径）"),
        ("GET", "/api/v1/cr016/dialogue/quota/status", "对话额度（新路径）"),
    ]
    
    results = []
    for method, path, name in api_tests:
        try:
            if method == "GET":
                resp = requests.get(f"http://localhost:8000{path}", headers=headers)
            else:
                resp = requests.post(f"http://localhost:8000{path}", headers=headers)
            
            status = "PASS" if resp.status_code == 200 else "FAIL"
            results.append({
                "api": name,
                "path": path,
                "status": status,
                "http_code": resp.status_code,
                "response": resp.json() if resp.status_code == 200 else None
            })
            print(f"{status} {name} ({path}): HTTP {resp.status_code}")
        except Exception as e:
            results.append({
                "api": name,
                "path": path,
                "status": "FAIL",
                "error": str(e)
            })
            print(f"FAIL {name} ({path}): {e}")
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("CR-016 Browser E2E Test")
    print("=" * 60)
    
    print("\n[1] 测试前端页面访问")
    print("-" * 60)
    page_results = test_frontend_pages()
    
    print("\n[2] 测试 API 集成")
    print("-" * 60)
    api_results = test_api_integration()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_results = page_results + api_results
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = sum(1 for r in all_results if r["status"] == "FAIL")
    
    print(f"总计: {len(all_results)} | 通过: {passed} | 失败: {failed}")
    
    if failed > 0:
        print("\n失败项:")
        for r in all_results:
            if r["status"] == "FAIL":
                name = r.get('page') or r.get('api')
                error = r.get('error') or f"HTTP {r.get('http_code')}"
                print(f"  - {name}: {error}")
    
    # 输出 JSON 结果
    with open("/root/isekai-wanderer/workflow/changes/CR-016/browser-e2e-results.json", "w") as f:
        json.dump({
            "pages": page_results,
            "apis": api_results,
            "summary": {"passed": passed, "failed": failed, "total": len(all_results)}
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细结果已保存到: workflow/changes/CR-016/browser-e2e-results.json")
