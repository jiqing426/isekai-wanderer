#!/usr/bin/env python3
"""PL independent verification of Phase 2 tasks"""
import urllib.request
import json
import sys

BASE = "http://localhost:8000/api/v1"

def req(method, path, data=None, token=None):
    url = f"{BASE}/{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body_text = e.read() if e.fp else b"{}"
        try:
            return json.loads(body_text), e.code
        except Exception:
            return {"raw": body_text.decode(errors="replace")}, e.code

def check(name, passed, detail=""):
    icon = "\u2705" if passed else "\u274c"
    print(f"{icon} {name}: {detail}")
    return passed

results = []

# Login
d, code = req("POST", "auth/login", {"email": "e2e-v2@example.com", "password": "***"})
token = d.get("access_token", "")
results.append(check("Login", len(token) > 50, f"code={code}"))

# DEV-013: Affection System
print("\n--- DEV-013 Affection ---")
d, code = req("GET", "affection", token=token)
results.append(check("GET /affection", code == 200, f"records={len(d.get('affections', []))}"))

d, code = req("GET", "characters/22222222-2222-2222-2222-222222222222/affection", token=token)
results.append(check("GET /characters/{id}/affection", code == 200, f"code={code} data={json.dumps(d, ensure_ascii=False)[:120]}"))

# DEV-017: Memory Storage
print("\n--- DEV-017 Memory Storage ---")
d, code = req("POST", "memories", {
    "session_id": "11111111-1111-1111-1111-111111111111",
    "content": "PL verify: player chose stargazing",
    "source": "pl_test"
}, token=token)
results.append(check("POST /memories", code in (200, 201), f"code={code} id={str(d.get('id', '?'))[:16]}"))

d, code = req("GET", "memories?session_id=11111111-1111-1111-1111-111111111111", token=token)
mems = d.get("memories", d) if isinstance(d, dict) else d
mem_count = len(mems) if isinstance(mems, list) else "?"
results.append(check("GET /memories", code == 200, f"code={code} count={mem_count}"))

# DEV-018: Memory Recall
print("\n--- DEV-018 Memory Recall ---")
d, code = req("GET", "memories/recall?query=stargazing&session_id=11111111-1111-1111-1111-111111111111&limit=5", token=token)
recall_list = d.get("memories", d.get("results", []))
results.append(check("GET /memories/recall", code == 200, f"code={code} results={len(recall_list)}"))

# Onboarding PUT /user/profile (known issue)
print("\n--- Onboarding PUT /user/profile ---")
d, code = req("PUT", "user/profile", {"onboarding_completed": True}, token=token)
results.append(check("PUT /user/profile", code == 200, f"code={code} response={json.dumps(d, ensure_ascii=False)[:80]}"))

# Scripts
print("\n--- Scripts ---")
d, code = req("GET", "scripts", token=token)
scripts = d if isinstance(d, list) else d.get("scripts", [])
results.append(check("Scripts", len(scripts) >= 3, f"count={len(scripts)} titles={[s['title'] for s in scripts]}"))

# Game flow - all 3 scripts
for script_id, title in [
    ("11111111-1111-1111-1111-111111111111", "starry-vow"),
    ("66666666-6666-6666-6666-666666666666", "star-moon-fate"),
    ("a1111111-1111-1111-1111-111111111111", "cherry-blossom"),
]:
    print(f"\n--- Game Flow ({title}) ---")
    d, code = req("POST", "game/start", {"script_id": script_id}, token=token)
    session_id = d.get("session_id", "")
    results.append(check(f"Game Start ({title})", bool(session_id), f"code={code} session={session_id[:16]}..."))

    if session_id:
        d, code = req("GET", f"game/{session_id}/dialogue", token=token)
        choices = d.get("choices", [])
        text = d.get("dialogue_text", d.get("text", "?"))
        results.append(check(f"Dialogue ({title})", len(choices) > 0, f"choices={len(choices)} text={text[:50]}"))

        if choices:
            cid = choices[0]["id"]
            d2, code2 = req("POST", f"game/{session_id}/choice", {"choice_id": cid}, token=token)
            aff = d2.get("affection_change", {})
            results.append(check(f"Choice ({title})", code2 == 200, f"ended={d2.get('is_ended')} delta={aff.get('delta', '?')} val={aff.get('new_value', '?')}"))

# Summary
print("\n" + "=" * 50)
passed = sum(1 for p in results if p)
total = len(results)
print(f"INDEPENDENT VERIFICATION: {passed}/{total} passed")
if passed < total:
    print("\nFailed:")
    for i, (name, p, detail) in enumerate(zip(
        [r[0] if isinstance(r, tuple) else "" for r in results],
        results,
        [""] * len(results)
    )):
        pass
sys.exit(0 if passed == total else 1)
