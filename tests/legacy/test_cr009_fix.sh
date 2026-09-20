#!/bin/bash
# 测试需要修复的3个接口

# 先注册/登录获取 token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"***"}' | jq -r '.access_token')

if [ "$TOKEN" = "null" ]; then
  # 注册新用户
  TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"***"}' | jq -r '.access_token')
fi

echo "Token: ${TOKEN:0:50}..."

# 测试1: GET /affection
echo -e "\n=== 测试1: GET /affection ==="
curl -s -w "\nHTTP Status: %{http_code}\n" \
  http://localhost:8000/api/v1/affection \
  -H "Authorization: Bearer $TOKEN" | jq .

# 测试2: POST /game/{sessionId}/choice (需要先创建会话)
echo -e "\n=== 测试2: POST /game/start ==="
SESSION=$(curl -s -X POST http://localhost:8000/api/v1/game/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"script_id":"11111111-1111-1111-1111-111111111111"}')
echo "$SESSION" | jq .
SESSION_ID=$(echo "$SESSION" | jq -r '.session_id')

echo -e "\n=== 测试3: POST /game/{sessionId}/choice ==="
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -X POST "http://localhost:8000/api/v1/game/$SESSION_ID/choice" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"choice_id":"11111111-1111-1111-1111-111111111111"}' | jq .

# 测试4: POST /game/{sessionId}/free-chat
echo -e "\n=== 测试4: POST /game/{sessionId}/free-chat ==="
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -X POST "http://localhost:8000/api/v1/game/$SESSION_ID/free-chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"你好"}' | jq .
