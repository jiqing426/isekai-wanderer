#!/bin/bash
# Test all 9 personal-center endpoints

TOKEN=*** -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"batch2-test@isekai.dev","password":"***"}' | jq -r '.access_token')

echo "=== 11. GET /users/me/stats ==="
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me/stats | jq .

echo -e "\n=== 12. GET /users/me/asset ==="
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me/asset | jq .

echo -e "\n=== 13. GET /sign/info ==="
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/sign/info | jq .

echo -e "\n=== 14. GET /users/me/latest-save ==="
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me/latest-save | jq .

echo -e "\n=== 15. GET /users/me/memory/summary ==="
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me/memory/summary | jq .

echo -e "\n=== 16. GET /users/me/characters/bond ==="
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me/characters/bond | jq .

echo -e "\n=== 17. GET /users/me/endings ==="
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me/endings | jq .

echo -e "\n=== 18. GET /users/me/endings/recent ==="
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me/endings/recent | jq .

echo -e "\n=== 19. GET /users/me/memory/full (should be 403 for free tier) ==="
curl -s -w "\nHTTP Status: %{http_code}\n" -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me/memory/full
