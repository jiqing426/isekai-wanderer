#!/usr/bin/env python3
import urllib.request
import json

BASE = "http://localhost:8000/api/v1"
PASSWORD = "Test" + "1234" + "!"


def req(method, path, data=None, auth_token=""):
    url = BASE + "/" + path
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = "Bearer " + auth_token
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        bt = e.read() if e.fp else b"{}"
        try:
            return json.loads(bt), e.code
        except Exception:
            return {"raw": bt.decode(errors="replace")}, e.code


# Register + Login
d, code = req("POST", "auth/register", {"email": "phase3check@test.com", "password": PASSWORD})
print("Register: code=%d" % code)
d, code = req("POST", "auth/login", {"email": "phase3check@test.com", "password": PASSWORD})
token = d.get("access_token", "")
print("Login: code=%d token_len=%d" % (code, len(token)))

print()
print("--- Fix 1: PUT /user/profile ---")
d, code = req("PUT", "user/profile", {"onboarding_completed": True, "preferred_genre": "romance", "locale": "zh"}, token)
print("  code=%d resp=%s" % (code, json.dumps(d, ensure_ascii=False)[:150]))

print()
print("--- Fix 2: character_name ---")
cid = "22222222-2222-2222-2222-222222222222"
d, code = req("GET", "affection/" + cid, token)
cn = d.get("character_name", "MISSING")
lv = d.get("level", "?")
val = d.get("affection_value", d.get("value", 0))
print("  code=%d character_name=%s level=%s value=%s" % (code, cn, lv, val))
if val < 20:
    exp = "acquaintance"
elif val < 40:
    exp = "ambiguous"
elif val < 60:
    exp = "trust"
elif val < 80:
    exp = "bond"
else:
    exp = "love"
match = "YES" if lv == exp else "NO"
print("  5-level match: %s (expected=%s)" % (match, exp))

print()
print("--- Affection list ---")
d, code = req("GET", "affection", token)
affs = d.get("affections", [])
if affs:
    a = affs[0]
    print("  fields: %s" % list(a.keys()))
    print("  character_name=%s value=%s level=%s" % (a.get("character_name", "MISSING"), a.get("value", "MISSING"), a.get("level", "MISSING")))
else:
    print("  code=%d empty" % code)

print()
print("--- New routes ---")
r2 = urllib.request.Request("http://localhost:8000/openapi.json")
resp2 = urllib.request.urlopen(r2)
spec = json.loads(resp2.read())
paths = sorted(spec.get("paths", {}).keys())
found = False
keywords = ["payment", "subscribe", "oauth", "ugc", "community", "post", "share", "gallery", "achievement"]
for p in paths:
    if any(k in p for k in keywords):
        methods = list(spec["paths"][p].keys())
        print("  %s: %s" % (p, methods))
        found = True
if not found:
    print("  (none yet)")
