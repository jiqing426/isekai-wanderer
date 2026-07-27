import requests, json

BASE_URL = "http://localhost:8000/api/v1"
login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "fragment-test@example.com", "password": "***"})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get goods to find the free one (碎片补给包, price 0)
goods_resp = requests.get(f"{BASE_URL}/fragment/shop/goods", headers=headers).json()
free_goods_id = None
for g in goods_resp["goods"]:
    if g["price"] == 0:
        free_goods_id = g["id"]
        print(f"Found free goods: {g['name']} (ID: {free_goods_id})")

if free_goods_id:
    # Exchange it
    print("\n=== POST /fragment/exchange (success case) ===")
    resp = requests.post(f"{BASE_URL}/fragment/exchange", headers=headers, json={"goods_id": free_goods_id, "quantity": 1})
    print(resp.status_code)
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

    # Check transactions
    print("\n=== GET /fragment/transactions (after exchange) ===")
    resp = requests.get(f"{BASE_URL}/fragment/transactions", headers=headers)
    print(resp.status_code)
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
else:
    print("No free goods found to test")
