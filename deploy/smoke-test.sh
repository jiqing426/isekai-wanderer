#!/bin/bash
# Delivery E2E Smoke Test for CR-001 Production Deployment
# Tests all 33 core API endpoints against the real backend

set -e
BE="http://localhost:8000"
PASS=0
FAIL=0
TOTAL=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

pass_test() {
    echo -e "  ${GREEN}✓${NC} [$1] $2"
    PASS=$((PASS + 1))
    TOTAL=$((TOTAL + 1))
}

fail_test() {
    echo -e "  ${RED}✗${NC} [$1] $2"
    FAIL=$((FAIL + 1))
    TOTAL=$((TOTAL + 1))
}

skip_test() {
    echo -e "  ${YELLOW}⊘${NC} [skip] $1"
    TOTAL=$((TOTAL + 1))
}

echo "============================================"
echo "  CR-001 Production Smoke Test"
echo "  Backend: $BE"
echo "  Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  Mock API: no (real FastAPI + PostgreSQL)"
echo "============================================"
echo ""

# --- 1. Health ---
echo "--- Health & Infrastructure ---"
HEALTH_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/health)
[ "$HEALTH_CODE" = "200" ] && pass_test "$HEALTH_CODE" "GET /health" || fail_test "$HEALTH_CODE" "GET /health"

MOD_HEALTH=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/moderation/health)
[ "$MOD_HEALTH" = "200" ] && pass_test "$MOD_HEALTH" "GET /moderation/health" || fail_test "$MOD_HEALTH" "GET /moderation/health"

# --- 2. Auth ---
echo ""
echo "--- Authentication ---"

EMAIL="smoketest-$(date +%s)@isekai-wanderer.com"
REG_CODE=$(curl -s -o /tmp/reg.json -w '%{http_code}' -X POST $BE/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"$EMAIL\",\"password\":\"SmokeTest123!\",\"display_name\":\"SmokeTest\"}")
([ "$REG_CODE" = "200" ] || [ "$REG_CODE" = "201" ]) && pass_test "$REG_CODE" "POST /auth/register" || fail_test "$REG_CODE" "POST /auth/register"

# Login
LOGIN_RESP=$(curl -s -X POST $BE/api/v1/auth/login \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"$EMAIL\",\"password\":\"SmokeTest123!\"}")
ACCESS_TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")
REFRESH_TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('refresh_token',''))" 2>/dev/null || echo "")
TOKEN=""
if [ -n "$ACCESS_TOKEN" ]; then
    pass_test "200" "POST /auth/login (access+refresh tokens obtained)"
    TOKEN="$ACCESS_TOKEN"
else
    fail_test "FAIL" "POST /auth/login"
fi

# Refresh token (body with refresh_token field)
if [ -n "$REFRESH_TOKEN" ]; then
    REFRESH_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/auth/refresh \
        -H 'Content-Type: application/json' \
        -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}")
    [ "$REFRESH_CODE" = "200" ] && pass_test "$REFRESH_CODE" "POST /auth/refresh" || fail_test "$REFRESH_CODE" "POST /auth/refresh"
else
    skip_test "POST /auth/refresh (no refresh_token)"
fi

# OAuth mock
OAUTH_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/auth/oauth/google \
    -H 'Content-Type: application/json' \
    -d '{"code":"mock-code-123"}')
[ "$OAUTH_CODE" = "200" ] && pass_test "$OAUTH_CODE" "POST /auth/oauth/google (mock)" || fail_test "$OAUTH_CODE" "POST /auth/oauth/google (mock)"

# --- 3. User ---
echo ""
echo "--- User Profile ---"
if [ -n "$TOKEN" ]; then
    PROF_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X GET $BE/api/v1/user/profile \
        -H "Authorization: Bearer $TOKEN")
    [ "$PROF_CODE" = "200" ] && pass_test "$PROF_CODE" "GET /user/profile" || fail_test "$PROF_CODE" "GET /user/profile"

    PUT_PROF=$(curl -s -o /dev/null -w '%{http_code}' -X PUT $BE/api/v1/user/profile \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"onboarding_completed":true}')
    [ "$PUT_PROF" = "200" ] && pass_test "$PUT_PROF" "PUT /user/profile" || fail_test "$PUT_PROF" "PUT /user/profile"
else
    skip_test "GET /user/profile (no token)"
    skip_test "PUT /user/profile (no token)"
fi

# --- 4. Scripts & Game ---
echo ""
echo "--- Scripts & Game ---"
SESSION_ID=""
if [ -n "$TOKEN" ]; then
    SCRIPTS_CODE=$(curl -s -o /tmp/scripts.json -w '%{http_code}' $BE/api/v1/scripts \
        -H "Authorization: Bearer $TOKEN")
    if [ "$SCRIPTS_CODE" = "200" ]; then
        pass_test "$SCRIPTS_CODE" "GET /scripts"
        # Handle both list and dict responses
        SCRIPT_ID=$(python3 -c "
import json
d = json.load(open('/tmp/scripts.json'))
if isinstance(d, list) and len(d) > 0:
    print(d[0]['id'])
elif isinstance(d, dict):
    items = d.get('items', d.get('scripts', d.get('data', [])))
    if items and len(items) > 0:
        print(items[0]['id'])
    else:
        # Try first key that has a list
        for k, v in d.items():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict) and 'id' in v[0]:
                print(v[0]['id'])
                break
        else:
            print('')
else:
    print('')
" 2>/dev/null || echo "")
        if [ -n "$SCRIPT_ID" ]; then
            echo "    Script ID: $SCRIPT_ID"
        fi
    else
        fail_test "$SCRIPTS_CODE" "GET /scripts"
    fi

    # Start game
    if [ -n "$SCRIPT_ID" ]; then
        START_RESP=$(curl -s -X POST $BE/api/v1/game/start \
            -H "Authorization: Bearer $TOKEN" \
            -H 'Content-Type: application/json' \
            -d "{\"script_id\":\"$SCRIPT_ID\"}")
        SESSION_ID=$(echo "$START_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id', d.get('id', '')))" 2>/dev/null || echo "")
        if [ -n "$SESSION_ID" ]; then
            pass_test "200" "POST /game/start (session=${SESSION_ID:0:8}...)"
        else
            fail_test "FAIL" "POST /game/start (response: $(echo $START_RESP | head -c 100))"
        fi

        # Get game state
        if [ -n "$SESSION_ID" ]; then
            STATE_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/game/$SESSION_ID \
                -H "Authorization: Bearer $TOKEN")
            [ "$STATE_CODE" = "200" ] && pass_test "$STATE_CODE" "GET /game/{session_id}" || fail_test "$STATE_CODE" "GET /game/{session_id}"
        fi
    else
        skip_test "POST /game/start (no script_id)"
        skip_test "GET /game/{session_id}"
    fi
else
    skip_test "GET /scripts (no token)"
    skip_test "POST /game/start"
    skip_test "GET /game/{session_id}"
fi

# --- 5. Affection ---
echo ""
echo "--- Affection ---"
if [ -n "$TOKEN" ]; then
    AFF_CODE=$(curl -s -o /tmp/aff.json -w '%{http_code}' $BE/api/v1/affection \
        -H "Authorization: Bearer $TOKEN")
    if [ "$AFF_CODE" = "200" ]; then
        pass_test "$AFF_CODE" "GET /affection"
        AFF_ID=$(python3 -c "
import json
d = json.load(open('/tmp/aff.json'))
if isinstance(d, list) and len(d) > 0:
    print(d[0]['id'])
else:
    print('')
" 2>/dev/null || echo "")
        if [ -n "$AFF_ID" ]; then
            AFF_D_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/affection/$AFF_ID \
                -H "Authorization: Bearer $TOKEN")
            [ "$AFF_D_CODE" = "200" ] && pass_test "$AFF_D_CODE" "GET /affection/{id}" || fail_test "$AFF_D_CODE" "GET /affection/{id}"
        else
            skip_test "GET /affection/{id} (empty list)"
        fi
    else
        fail_test "$AFF_CODE" "GET /affection"
    fi
else
    skip_test "GET /affection (no token)"
fi

# --- 6. Daily ---
echo ""
echo "--- Daily Check-in & Tasks ---"
if [ -n "$TOKEN" ]; then
    CHECKIN_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/daily/checkin \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{}')
    ([ "$CHECKIN_CODE" = "200" ] || [ "$CHECKIN_CODE" = "201" ]) && pass_test "$CHECKIN_CODE" "POST /daily/checkin" || fail_test "$CHECKIN_CODE" "POST /daily/checkin"

    STATS_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/daily/stats \
        -H "Authorization: Bearer $TOKEN")
    [ "$STATS_CODE" = "200" ] && pass_test "$STATS_CODE" "GET /daily/stats" || fail_test "$STATS_CODE" "GET /daily/stats"

    TASKS_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/daily/tasks \
        -H "Authorization: Bearer $TOKEN")
    [ "$TASKS_CODE" = "200" ] && pass_test "$TASKS_CODE" "GET /daily/tasks" || fail_test "$TASKS_CODE" "GET /daily/tasks"
else
    skip_test "POST /daily/checkin (no token)"
    skip_test "GET /daily/stats (no token)"
    skip_test "GET /daily/tasks (no token)"
fi

# --- 7. Memories ---
echo ""
echo "--- Memories ---"
if [ -n "$TOKEN" ] && [ -n "$SESSION_ID" ]; then
    MEM_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/memories \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d "{\"session_id\":\"$SESSION_ID\",\"character_id\":\"22222222-2222-2222-2222-222222222222\",\"content\":\"I love cats and dogs\",\"memory_type\":\"personal\"}")
    ([ "$MEM_CODE" = "201" ] || [ "$MEM_CODE" = "200" ]) && pass_test "$MEM_CODE" "POST /memories" || fail_test "$MEM_CODE" "POST /memories"

    MEM_LIST=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/memories \
        -H "Authorization: Bearer $TOKEN")
    [ "$MEM_LIST" = "200" ] && pass_test "$MEM_LIST" "GET /memories" || fail_test "$MEM_LIST" "GET /memories"

    MEM_RECALL=$(curl -s -o /dev/null -w '%{http_code}' "$BE/api/v1/memories/recall?query=cats" \
        -H "Authorization: Bearer $TOKEN")
    [ "$MEM_RECALL" = "200" ] && pass_test "$MEM_RECALL" "GET /memories/recall" || fail_test "$MEM_RECALL" "GET /memories/recall"
else
    skip_test "POST /memories (no session_id)"
    skip_test "GET /memories"
    skip_test "GET /memories/recall"
fi

# --- 8. Payment & Subscription ---
echo ""
echo "--- Payment & Subscription ---"
if [ -n "$TOKEN" ]; then
    PLANS_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/payment/plans \
        -H "Authorization: Bearer $TOKEN")
    [ "$PLANS_CODE" = "200" ] && pass_test "$PLANS_CODE" "GET /payment/plans" || fail_test "$PLANS_CODE" "GET /payment/plans"

    PURCHASE_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/payment/purchase \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"item_id":"shards_100","item_name":"100 Shards","price":0.99,"currency":"USD"}')
    ([ "$PURCHASE_CODE" = "200" ] || [ "$PURCHASE_CODE" = "201" ]) && pass_test "$PURCHASE_CODE" "POST /payment/purchase (mock)" || fail_test "$PURCHASE_CODE" "POST /payment/purchase (mock)"

    RECHARGE_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/payment/recharge \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"shards":50,"amount":0.49,"currency":"USD","provider":"mock"}')
    ([ "$RECHARGE_CODE" = "200" ] || [ "$RECHARGE_CODE" = "201" ]) && pass_test "$RECHARGE_CODE" "POST /payment/recharge" || fail_test "$RECHARGE_CODE" "POST /payment/recharge"

    HIST_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/payment/history \
        -H "Authorization: Bearer $TOKEN")
    [ "$HIST_CODE" = "200" ] && pass_test "$HIST_CODE" "GET /payment/history" || fail_test "$HIST_CODE" "GET /payment/history"

    SUB_STATUS=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/subscription/status \
        -H "Authorization: Bearer $TOKEN")
    [ "$SUB_STATUS" = "200" ] && pass_test "$SUB_STATUS" "GET /subscription/status" || fail_test "$SUB_STATUS" "GET /subscription/status"
else
    skip_test "GET /payment/plans (no token)"
    skip_test "POST /payment/purchase (no token)"
    skip_test "POST /payment/recharge (no token)"
    skip_test "GET /payment/history (no token)"
    skip_test "GET /subscription/status (no token)"
fi

# --- 9. Gallery & UGC ---
echo ""
echo "--- Gallery & UGC ---"
if [ -n "$TOKEN" ]; then
    CGS_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/gallery/cgs \
        -H "Authorization: Bearer $TOKEN")
    [ "$CGS_CODE" = "200" ] && pass_test "$CGS_CODE" "GET /gallery/cgs" || fail_test "$CGS_CODE" "GET /gallery/cgs"

    COLL_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/gallery/collections \
        -H "Authorization: Bearer $TOKEN")
    [ "$COLL_CODE" = "200" ] && pass_test "$COLL_CODE" "GET /gallery/collections" || fail_test "$COLL_CODE" "GET /gallery/collections"

    ACH_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/gallery/achievements \
        -H "Authorization: Bearer $TOKEN")
    [ "$ACH_CODE" = "200" ] && pass_test "$ACH_CODE" "GET /gallery/achievements" || fail_test "$ACH_CODE" "GET /gallery/achievements"

    ACH2_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/achievements \
        -H "Authorization: Bearer $TOKEN")
    [ "$ACH2_CODE" = "200" ] && pass_test "$ACH2_CODE" "GET /achievements" || fail_test "$ACH2_CODE" "GET /achievements"

    UGC_POST=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/ugc/posts \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"title":"Smoke Test Post","content":"Testing production deployment"}')
    ([ "$UGC_POST" = "200" ] || [ "$UGC_POST" = "201" ]) && pass_test "$UGC_POST" "POST /ugc/posts" || fail_test "$UGC_POST" "POST /ugc/posts"

    UGC_LIST=$(curl -s -o /dev/null -w '%{http_code}' $BE/api/v1/ugc/posts \
        -H "Authorization: Bearer $TOKEN")
    [ "$UGC_LIST" = "200" ] && pass_test "$UGC_LIST" "GET /ugc/posts" || fail_test "$UGC_LIST" "GET /ugc/posts"
else
    skip_test "GET /gallery/cgs (no token)"
    skip_test "GET /gallery/collections (no token)"
    skip_test "GET /gallery/achievements (no token)"
    skip_test "GET /achievements (no token)"
    skip_test "POST /ugc/posts (no token)"
    skip_test "GET /ugc/posts (no token)"
fi

# --- 10. Share & Moderation ---
echo ""
echo "--- Share & Moderation ---"
if [ -n "$TOKEN" ]; then
    SHARE_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/share/generate \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"share_type":"ending","title":"Test Ending","description":"Smoke test share"}')
    ([ "$SHARE_CODE" = "200" ] || [ "$SHARE_CODE" = "201" ]) && pass_test "$SHARE_CODE" "POST /share/generate" || fail_test "$SHARE_CODE" "POST /share/generate"
else
    skip_test "POST /share/generate (no token)"
fi

# Moderation check requires auth + correct schema: content (not text), content_type Literal
if [ -n "$TOKEN" ]; then
    MOD_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BE/api/v1/moderation/check \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"content":"Hello world, this is a test message","content_type":"post"}')
    [ "$MOD_CODE" = "200" ] && pass_test "$MOD_CODE" "POST /moderation/check" || fail_test "$MOD_CODE" "POST /moderation/check"
else
    skip_test "POST /moderation/check (no token)"
fi

# --- Summary ---
echo ""
echo "============================================"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
    echo "  ✅ ALL SMOKE TESTS PASSED"
    exit 0
else
    echo "  ❌ $FAIL SMOKE TESTS FAILED"
    exit 1
fi
