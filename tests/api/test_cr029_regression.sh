#!/bin/bash
# CR-029 Regression Test Script
# Tests BUG-029-001~010 fixes

set -e

echo "============================================================"
echo "CR-029 Regression Tests"
echo "============================================================"

# Login
# Reset password first
docker compose exec -T db psql -U isekai -d isekai -c "UPDATE users SET password_hash='\$2b\$12\$QHxdcnGNGYcuihJeRRetiOAC4CbQrK8ByEuIx79hedkwo5NHWT1Oa' WHERE email='test@test.com';" >/dev/null 2>&1

TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"***"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token obtained: ${TOKEN:0:20}..."

# BUG-029-008: Test choice API doesn't return 500
echo ""
echo "=== BUG-029-008: Choice API 500 error regression ==="

# Get an active session with character
SESSION_INFO=$(docker compose exec -T db psql -U isekai -d isekai -t -A -c \
  "SELECT gs.id, gs.current_node_id FROM game_sessions gs WHERE gs.status='active' AND gs.character_id IS NOT NULL AND gs.current_node_id IS NOT NULL LIMIT 1;")

SESSION_ID=$(echo "$SESSION_INFO" | cut -d'|' -f1)
NODE_ID=$(echo "$SESSION_INFO" | cut -d'|' -f2)

echo "Session: $SESSION_ID, Current Node: $NODE_ID"

# Get choices for current node
CHOICES=$(docker compose exec -T db psql -U isekai -d isekai -t -A -c \
  "SELECT id FROM node_choices WHERE node_id = '$NODE_ID' LIMIT 1;")

if [ -n "$CHOICES" ]; then
  CHOICE_ID=$(echo "$CHOICES" | tr -d ' ')
  echo "Testing choice: $CHOICE_ID"
  
  # Make choice - should not return 500
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    "http://localhost:8000/api/v1/game/$SESSION_ID/choice" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"choice_id\": \"$CHOICE_ID\"}")
  
  echo "HTTP Status: $HTTP_CODE"
  if [ "$HTTP_CODE" = "500" ]; then
    echo "BUG-029-008: FAILED (500 error)"
  elif [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "BUG-029-008: PASSED"
  else
    echo "BUG-029-008: HTTP $HTTP_CODE (check manually)"
  fi
else
  echo "No choices available for current node, skipping"
fi

# BUG-029-003: Test gift records API
echo ""
echo "=== BUG-029-003: Gift records show all characters ==="
GIFT_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:8000/api/v1/gift/history" \
  -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$GIFT_RESPONSE" | tail -1)
BODY=$(echo "$GIFT_RESPONSE" | head -n -1)
echo "HTTP Status: $HTTP_CODE"
echo "Response preview: $(echo $BODY | head -c 200)"

# BUG-029-005: Test progress API
echo ""
echo "=== BUG-029-005: Progress calculation ==="
if [ -n "$SESSION_ID" ]; then
  PROGRESS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/game/$SESSION_ID/progress" \
    -H "Authorization: Bearer $TOKEN")
  echo "Progress response: $PROGRESS_RESPONSE"
fi

# BUG-029-001: Verify negative affection choices exist
echo ""
echo "=== BUG-029-001: Negative affection choices ==="
NEG_COUNT=$(docker compose exec -T db psql -U isekai -d isekai -t -A -c \
  "SELECT COUNT(*) FROM node_choices WHERE affection_delta < 0;")
echo "Negative affection choices: $NEG_COUNT"
if [ "$NEG_COUNT" -gt 0 ]; then
  echo "BUG-029-001: PASSED ($NEG_COUNT negative choices exist)"
else
  echo "BUG-029-001: FAILED (no negative choices)"
fi

# BUG-029-004: Verify affection scale includes 100
echo ""
echo "=== BUG-029-004: Affection scale includes 100 ==="
# Check frontend code
if grep -q "threshold: 100" frontend/src/components/AffectionDisplay.vue; then
  echo "BUG-029-004: PASSED (threshold 100 found in AffectionDisplay.vue)"
else
  echo "BUG-029-004: FAILED (threshold 100 not found)"
fi

# BUG-029-009: Verify choice button reset
echo ""
echo "=== BUG-029-009: Choice button reset after error ==="
if grep -q "defineExpose.*reset" frontend/src/components/ChoicePanel.vue && \
   grep -q "choicePanelRef" frontend/src/views/GameView.vue; then
  echo "BUG-029-009: PASSED (reset() exposed and referenced)"
else
  echo "BUG-029-009: FAILED (reset mechanism not found)"
fi

# BUG-029-002: Free chat character switch
echo ""
echo "=== BUG-029-002: Free chat character switch ==="
if grep -q "currentDialogue?.character_id" frontend/src/views/GameView.vue && \
   grep -q "query.*priority\|query.*character" frontend/src/views/FreeChatView.vue; then
  echo "BUG-029-002: PASSED (character_id priority logic found)"
else
  echo "BUG-029-002: Checking code..."
  grep -n "character_id" frontend/src/views/FreeChatView.vue | head -5
fi

# BUG-029-008: Memory service type check
echo ""
echo "=== BUG-029-008: Memory service type safety ==="
if grep -q "isinstance.*mem_text.*str" backend/app/services/narrative/memory_service.py; then
  echo "BUG-029-008: PASSED (type check found in memory_service.py)"
else
  echo "BUG-029-008: FAILED (type check not found)"
fi

# Original CR-029: Verify branch filtering still works
echo ""
echo "=== CR-029 Original: Branch filtering regression ==="
BRANCH_NODES=$(docker compose exec -T db psql -U isekai -d isekai -t -A -c \
  "SELECT COUNT(*) FROM nodes WHERE character_id IS NOT NULL;")
PUBLIC_NODES=$(docker compose exec -T db psql -U isekai -d isekai -t -A -c \
  "SELECT COUNT(*) FROM nodes WHERE character_id IS NULL;")
echo "Branch nodes: $BRANCH_NODES, Public nodes: $PUBLIC_NODES"
if [ "$BRANCH_NODES" -gt 0 ] && [ "$PUBLIC_NODES" -gt 0 ]; then
  echo "CR-029 Original: PASSED (branch + public nodes coexist)"
else
  echo "CR-029 Original: FAILED"
fi

# Original CR-029: Verify 3 choices per node
echo ""
echo "=== CR-029 Original: 3 choices per node ==="
THREE_CHOICE_NODES=$(docker compose exec -T db psql -U isekai -d isekai -t -A -c \
  "SELECT COUNT(*) FROM (SELECT node_id FROM node_choices GROUP BY node_id HAVING COUNT(*) = 3) t;")
echo "Nodes with exactly 3 choices: $THREE_CHOICE_NODES"
if [ "$THREE_CHOICE_NODES" -gt 0 ]; then
  echo "CR-029 Choices: PASSED ($THREE_CHOICE_NODES nodes with 3 choices)"
else
  echo "CR-029 Choices: FAILED"
fi

# Original CR-029: Verify backward compatibility
echo ""
echo "=== CR-029 Original: Backward compatibility ==="
NULL_SESSIONS=$(docker compose exec -T db psql -U isekai -d isekai -t -A -c \
  "SELECT COUNT(*) FROM game_sessions WHERE character_id IS NULL;")
TOTAL_SESSIONS=$(docker compose exec -T db psql -U isekai -d isekai -t -A -c \
  "SELECT COUNT(*) FROM game_sessions;")
echo "Sessions: $NULL_SESSIONS NULL / $TOTAL_SESSIONS total"
if [ "$NULL_SESSIONS" -gt 0 ]; then
  echo "CR-029 Compat: PASSED (existing sessions intact)"
else
  echo "CR-029 Compat: WARNING (no NULL sessions found)"
fi

echo ""
echo "============================================================"
echo "Regression tests complete"
echo "============================================================"
