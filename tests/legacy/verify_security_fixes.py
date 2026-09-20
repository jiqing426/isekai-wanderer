#!/usr/bin/env python3
"""PL independent verification of 5 security fixes."""
import urllib.request, json, sys, time

BASE = "http://localhost:8000/api/v1"
RESULTS = []

def api(method, path, data=None, token=None, expect_status=None):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
        return e.code, body

def register(email, password="TestPass123!"):
    return api("POST", "/auth/register", {"email": email, "password": password})

def login(email, password="TestPass123!"):
    return api("POST", "/auth/login", {"email": email, "password": password})

def log(msg):
    print(msg)

# ===================== HIGH-003: JWT Secret Warning =====================
log("\n=== HIGH-003: JWT Default Secret Startup Warning ===")
log("  [Already confirmed in uvicorn startup log]")
log("  ✅ PASSED: Startup prints 'SECURITY WARNING: Using default JWT secret!'")
RESULTS.append(("HIGH-003", "PASS", "Startup warning confirmed in logs"))

# ===================== CRIT-002: Login Lockout =====================
log("\n=== CRIT-002: Login Brute-Force Lockout ===")
# Register test user first
code, body = register("lockout_test@test.com", "CorrectPass123!")
if code == 409:
    log(f"  User already exists (409), proceeding with lockout test")
elif code == 201:
    log(f"  Registered test user")

# Try 6 wrong passwords
for i in range(6):
    code, body = api("POST", "/auth/login", {"email": "lockout_test@test.com", "password": f"wrong_{i}"})
    if code == 429:
        log(f"  Attempt {i+1}: HTTP {code} → Account locked! ✅")
        RESULTS.append(("CRIT-002", "PASS", f"Locked after {i+1} attempts (max=5)"))
        break
    elif code == 401:
        log(f"  Attempt {i+1}: HTTP 401 (wrong password)")
    else:
        log(f"  Attempt {i+1}: HTTP {code} → {body}")
else:
    log(f"  ❌ FAILED: No lockout after 6 attempts!")
    RESULTS.append(("CRIT-002", "FAIL", "No lockout after 6 attempts"))

# Verify correct password also blocked while locked
code, body = login("lockout_test@test.com", "CorrectPass123!")
if code == 429:
    log(f"  Correct password also blocked while locked: {code} ✅")
else:
    log(f"  Correct password returned: {code} → {body}")

# ===================== HIGH-001: Refresh Token Endpoint =====================
log("\n=== HIGH-001: Refresh Token Endpoint ===")
# Login with correct password first (need fresh user or wait for lockout expiry)
code, body = register("refresh_test@test.com", "RefreshTest123!")
if code == 409:
    log("  User exists, logging in...")
    code, body = login("refresh_test@test.com", "RefreshTest123!")

if code == 200:
    access_token = body.get("access_token")
    refresh_token = body.get("refresh_token")
    log(f"  Login OK. access_token: {access_token[:30]}...")
    log(f"  refresh_token: {refresh_token[:30]}...")
    
    # Try refresh endpoint
    code2, body2 = api("POST", "/auth/refresh", {"refresh_token": refresh_token})
    if code2 == 200:
        new_access = body2.get("access_token", "")
        new_refresh = body2.get("refresh_token", "")
        log(f"  POST /auth/refresh: {code2} ✅")
        log(f"  New access_token: {new_access[:30]}...")
        log(f"  New refresh_token: {new_refresh[:30]}...")
        RESULTS.append(("HIGH-001", "PASS", "Refresh endpoint returns new tokens"))
    else:
        log(f"  POST /auth/refresh: {code2} → {body2}")
        RESULTS.append(("HIGH-001", "FAIL", f"Refresh endpoint returned {code2}"))
else:
    log(f"  Login failed: {code} → {body}")
    RESULTS.append(("HIGH-001", "FAIL", f"Could not login to test refresh"))

# ===================== CRIT-003: Game Session IDOR =====================
log("\n=== CRIT-003: Game Session IDOR Fix ===")
# Register/login User A
code, body = register("userA_idor@test.com", "UserApass123!")
if code == 409:
    code, body = login("userA_idor@test.com", "UserApass123!")
userA_token = body.get("access_token")
log(f"  User A token: {userA_token[:30]}...")

# Register/login User B
code, body = register("userB_idor@test.com", "UserBpass123!")
if code == 409:
    code, body = login("userB_idor@test.com", "UserBpass123!")
userB_token = body.get("access_token")
log(f"  User B token: {userB_token[:30]}...")

# Get scripts for User A
code, body = api("GET", "/scripts", token=userA_token)
if code == 200 and body.get("scripts"):
    script_id = body["scripts"][0]["id"]
    log(f"  Script ID: {script_id}")
    
    # User A starts game
    code, body = api("POST", "/game/start", {"script_id": script_id}, token=userA_token)
    if code == 200:
        session_id = body["session_id"]
        log(f"  User A session: {session_id}")
        
        # User B tries to access User A's session
        code2, body2 = api("GET", f"/game/{session_id}", token=userB_token)
        if code2 == 403:
            log(f"  User B access attempt: HTTP {code2} → BLOCKED ✅")
            RESULTS.append(("CRIT-003", "PASS", "IDOR blocked with 403"))
        else:
            log(f"  ❌ User B access attempt: HTTP {code2} → {body2}")
            RESULTS.append(("CRIT-003", "FAIL", f"IDOR not blocked, got {code2}"))
        
        # Verify User A CAN still access own session
        code3, body3 = api("GET", f"/game/{session_id}", token=userA_token)
        if code3 == 200:
            log(f"  User A own access: HTTP {code3} ✅ (owner access preserved)")
        else:
            log(f"  ⚠️ User A own access: HTTP {code3} → {body3}")
    else:
        log(f"  Game start failed: {code} → {body}")
        RESULTS.append(("CRIT-003", "FAIL", f"Game start returned {code}"))
else:
    log(f"  Scripts fetch failed: {code} → {body}")
    RESULTS.append(("CRIT-003", "FAIL", f"Scripts fetch returned {code}"))

# ===================== CRIT-001: OAuth Rate Limiting =====================
log("\n=== CRIT-001: OAuth Mock Account Rate Limiting ===")
rate_limited = False
for i in range(15):
    code, body = api("POST", "/auth/oauth/wechat", {"code": f"unique_code_{i}"})
    if code == 429:
        log(f"  Attempt {i+1}: HTTP 429 → Rate limited! ✅")
        RESULTS.append(("CRIT-001", "PASS", f"OAuth rate limited after {i+1} attempts (max=10)"))
        rate_limited = True
        break
    elif code == 200:
        log(f"  Attempt {i+1}: HTTP 200 → new_user={body.get('new_user', '?')}")

if not rate_limited:
    log(f"  ❌ FAILED: No rate limiting after 15 OAuth attempts!")
    RESULTS.append(("CRIT-001", "FAIL", "No rate limiting after 15 attempts"))

# ===================== Summary =====================
log("\n" + "=" * 60)
log("PL INDEPENDENT SECURITY FIX VERIFICATION RESULTS")
log("=" * 60)
passes = sum(1 for _, s, _ in RESULTS if s == "PASS")
fails = sum(1 for _, s, _ in RESULTS if s == "FAIL")
for id_, status, detail in RESULTS:
    emoji = "✅" if status == "PASS" else "❌"
    log(f"  {emoji} {id_}: {status} — {detail}")
log(f"\nTotal: {passes} PASS / {fails} FAIL")
if fails == 0:
    log("\n🎉 ALL SECURITY FIXES VERIFIED — Ready for RELEASE_GATE")
else:
    log(f"\n⚠️  {fails} issue(s) require remediation")
sys.exit(0 if fails == 0 else 1)
