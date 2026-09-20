#!/usr/bin/env python3
"""Check which Phase 3 APIs BE has already implemented"""
import urllib.request
import json

# Check OpenAPI spec
r = urllib.request.Request("http://localhost:8000/openapi.json")
resp = urllib.request.urlopen(r)
spec = json.loads(resp.read())
paths = sorted(spec.get("paths", {}).keys())

print("=== All registered API routes ===")
for p in paths:
    methods = list(spec["paths"][p].keys())
    print(f"  {p}: {methods}")

# Check specific endpoints FE needs
print("\n=== FE-required endpoints check ===")
fe_needed = [
    ("GET", "/api/v1/subscription/status", "W11 订阅页"),
    ("POST", "/api/v1/payment/recharge", "碎片充值"),
    ("POST", "/api/v1/payment/purchase", "剧本购买"),
    ("GET", "/api/v1/gallery/cgs", "W08 画廊"),
    ("GET", "/api/v1/achievements", "成就墙"),
    ("PUT", "/api/v1/user/preferences", "偏好设置"),
    ("GET", "/api/v1/user/preferences", "偏好读取"),
]

missing = []
for method, path, desc in fe_needed:
    found = path in spec.get("paths", {})
    if found:
        methods = list(spec["paths"][path].keys())
        has_method = method.lower() in [m.lower() for m in methods]
        status = "OK" if has_method else f"MISSING {method} (has {methods})"
    else:
        status = "NOT FOUND"
        missing.append((method, path, desc))
    icon = "Y" if status == "OK" else "X"
    print(f"  [{icon}] {method} {path} ({desc}): {status}")

if missing:
    print(f"\n=== {len(missing)} endpoints MISSING ===")
    for m, p, d in missing:
        print(f"  {m} {p} ({d})")
else:
    print("\n=== All FE-required endpoints exist ===")
