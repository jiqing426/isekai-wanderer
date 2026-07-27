#!/usr/bin/env python3
"""PL 独立全量验证脚本 — 发布前检查"""
import urllib.request, json, sys

BASE = 'http://localhost:8000/api/v1'

def api(method, path, data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f'{BASE}{path}', data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except:
            return e.code, str(e.reason)

results = []

# Auth flow
s, d = api('POST', '/auth/register', {'email':'release@test.com','password':'Test123456','display_name':'Release'})
results.append(('Register', s, s in [200,201]))

s, d = api('POST', '/auth/login', {'email':'release@test.com','password':'Test123456'})
token = d.get('access_token','') if isinstance(d, dict) else ''
results.append(('Login', s, s==200 and bool(token)))

s, d = api('GET', '/user/profile', token=token)
results.append(('Profile', s, s==200))

s, d = api('POST', '/auth/oauth/google', {'code':'mock_code'}, token=token)
results.append(('OAuth Google', s, s in [200,201]))

# Game flow
s, d = api('GET', '/scripts', token=token)
scripts = d if isinstance(d, list) else d.get('scripts', d.get('items', []))
results.append(('Scripts list', s, s==200 and len(scripts) > 0))

s, d = api('POST', '/game/start', {'script_id':'66666666-6666-6666-6666-666666666666'}, token=token)
sid = d.get('session_id','') if isinstance(d, dict) else ''
results.append(('Game start', s, s==200 and bool(sid)))

if sid:
    s, d = api('GET', f'/game/{sid}', token=token)
    results.append(('Game state', s, s==200))

    s, d = api('GET', f'/game/{sid}/dialogue', token=token)
    results.append(('Get dialogue', s, s==200))

    choices = d.get('choices', []) if isinstance(d, dict) else []
    if choices:
        cid = choices[0].get('choice_id', choices[0].get('id', ''))
        s, d = api('POST', f'/game/{sid}/choice', {'choice_id': cid}, token=token)
        results.append(('Submit choice', s, s==200))

# Affection
s, d = api('GET', '/affection', token=token)
results.append(('Affection list', s, s==200))

# Daily
s, d = api('POST', '/daily/checkin', token=token)
results.append(('Daily checkin', s, s in [200,201]))

s, d = api('GET', '/daily/status', token=token)
results.append(('Daily status', s, s==200))

# Subscription
s, d = api('GET', '/subscription/plans', token=token)
results.append(('Sub plans', s, s==200))

s, d = api('POST', '/subscription/subscribe', {'plan_id':'premium','payment_method':'mock'}, token=token)
results.append(('Subscribe', s, s in [200,201]))

# Shop
s, d = api('GET', '/shop/plans', token=token)
results.append(('Shop plans', s, s==200))

# Gallery
s, d = api('GET', '/gallery/cgs', token=token)
results.append(('Gallery CGs', s, s==200))

s, d = api('GET', '/gallery/achievements', token=token)
results.append(('Achievements', s, s==200))

# Community
s, d = api('GET', '/community/posts', token=token)
results.append(('Community posts', s, s==200))

# Share
s, d = api('POST', '/share/generate', {'session_id': sid or '66666666-6666-6666-6666-666666666666', 'title':'Test Share'}, token=token)
results.append(('Share generate', s, s in [200,201]))

# Moderation
s, d = api('GET', '/moderation/health')
results.append(('Mod health', s, s==200))

s, d = api('POST', '/moderation/check', {'content':'hello','content_type':'post'}, token=token)
results.append(('Mod check', s, s==200))

# OpenAPI
req = urllib.request.Request('http://localhost:8000/openapi.json')
resp = urllib.request.urlopen(req)
spec = json.loads(resp.read())
results.append(('OpenAPI paths', len(spec['paths']), True))

passed = sum(1 for r in results if r[2])
total = len(results)
print(f'\n{"="*50}')
print(f'BE API 验证: {passed}/{total} passed')
print(f'{"="*50}')
for name, status, ok in results:
    print(f'  {"✅" if ok else "❌"} {name}: {status}')

if passed < total:
    sys.exit(1)
