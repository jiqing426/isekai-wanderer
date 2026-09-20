#!/usr/bin/env python3
"""Test script for CR-008 new personal-center endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get auth token for demo user."""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "demo@isekai.dev",
        "password": "***"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_endpoint(method, path, token=None, expected_status=200):
    """Test a single endpoint."""
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json={})
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json={})
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        status_ok = response.status_code == expected_status
        status_icon = "✓" if status_ok else "✗"
        print(f"{status_icon} {method} {path} -> {response.status_code}")
        
        if status_ok:
            try:
                data = response.json()
                print(f"  Response keys: {list(data.keys())}")
            except:
                print(f"  Response: {response.text[:100]}")
        else:
            print(f"  Expected {expected_status}, got {response.status_code}")
            print(f"  Error: {response.text[:200]}")
        
        return status_ok
    except Exception as e:
        print(f"✗ {method} {path} -> ERROR: {e}")
        return False

def main():
    print("Testing CR-008 New Personal-Center Endpoints\n")
    print("=" * 60)
    
    # Get auth token
    print("\n1. Getting auth token...")
    token = get_auth_token()
    if not token:
        print("✗ Failed to get auth token")
        return
    print("✓ Auth token obtained\n")
    
    print("=" * 60)
    print("\n2. Testing new endpoints...\n")
    
    endpoints = [
        ("GET", "/users/me/stats", True),
        ("GET", "/users/me/asset", True),
        ("GET", "/users/me/latest-save", True),
        ("GET", "/users/me/memory/summary", True),
        ("GET", "/users/me/characters/bond", True),
        ("GET", "/users/me/endings", True),
        ("GET", "/users/me/endings/recent", True),
        ("GET", "/users/me/memory/full", True),
    ]
    
    results = []
    for method, path, needs_auth in endpoints:
        result = test_endpoint(method, path, token if needs_auth else None)
        results.append((path, result))
    
    print("\n" + "=" * 60)
    print("\n3. Summary\n")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All endpoints working correctly!")
    else:
        print("\n✗ Some endpoints failed:")
        for path, result in results:
            if not result:
                print(f"  - {path}")

if __name__ == "__main__":
    main()
