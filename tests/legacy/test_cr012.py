#!/usr/bin/env python3
"""测试 CR-012 订阅系统重构接口"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_plans():
    """测试 GET /subscription/plans"""
    print("=" * 60)
    print("测试 1: GET /subscription/plans")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/subscription/plans")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"返回套餐数量: {len(data.get('plans', []))}")
        
        # 验证字段
        plans = data.get('plans', [])
        if plans:
            plan = plans[0]
            required_fields = ['planId', 'name', 'priceMonthly', 'priceYearly', 
                             'featureList', 'fragmentDiscountRate', 'recommend']
            
            missing_fields = [f for f in required_fields if f not in plan]
            if missing_fields:
                print(f"❌ 缺少字段: {missing_fields}")
            else:
                print("✅ 所有必需字段都存在")
                
            # 打印第一个套餐详情
            print(f"\n第一个套餐:")
            print(json.dumps(plan, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 请求失败: {response.text}")
    
    print()

def test_user_subscription(token):
    """测试 GET /user/subscription"""
    print("=" * 60)
    print("测试 2: GET /user/subscription")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user/subscription", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # 验证字段
        required_fields = ['currentPlanId', 'remainStamina', 'freeCycleStage', 
                         'permissions', 'expiresAt', 'autoRenew']
        
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            print(f"❌ 缺少字段: {missing_fields}")
        else:
            print("✅ 所有必需字段都存在")
            
        # 验证 permissions 子字段
        permissions = data.get('permissions', {})
        perm_fields = ['canAccessAllCharacters', 'canAccessCGGallery', 
                      'canUseAdvancedFeatures', 'canUseFreeChat', 'canUseMemorySystem']
        
        missing_perms = [f for f in perm_fields if f not in permissions]
        if missing_perms:
            print(f"❌ permissions 缺少字段: {missing_perms}")
        else:
            print("✅ permissions 所有字段都存在")
        
        # 打印详情
        print(f"\n用户订阅信息:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 请求失败: {response.text}")
    
    print()

def test_create_order(token):
    """测试 POST /order/create"""
    print("=" * 60)
    print("测试 3: POST /order/create")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试创建 standard 套餐的月度订单
    payload = {
        "planId": "standard",
        "cycleType": "monthly"
    }
    
    print(f"请求参数: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/order/create", headers=headers, json=payload)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # 验证字段
        required_fields = ['orderId', 'payUrl', 'amount', 'currency']
        
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            print(f"❌ 缺少字段: {missing_fields}")
        else:
            print("✅ 所有必需字段都存在")
            
        # 验证金额
        if data.get('amount') == 4.99:
            print("✅ 金额正确 (4.99)")
        else:
            print(f"❌ 金额错误: {data.get('amount')}")
        
        # 打印详情
        print(f"\n订单信息:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 请求失败: {response.text}")
    
    print()

def main():
    print("\n🚀 开始测试 CR-012 订阅系统重构接口\n")
    
    # 1. 测试套餐列表（无需认证）
    test_plans()
    
    # 2. 获取认证 token
    print("=" * 60)
    print("获取认证 Token")
    print("=" * 60)
    
    # 先尝试登录
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "***"
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get('access_token')
        print("✅ 登录成功\n")
    else:
        # 如果登录失败，尝试注册
        print("登录失败，尝试注册新用户...")
        register_response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "test_cr012@example.com",
            "password": "***",
            "username": "Test User"
        })
        
        if register_response.status_code in [200, 201]:
            token = register_response.json().get('access_token')
            print("✅ 注册成功\n")
        else:
            print(f"❌ 注册失败: {register_response.text}")
            return
    
    # 3. 测试用户订阅信息
    test_user_subscription(token)
    
    # 4. 测试创建订单
    test_create_order(token)
    
    print("=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
