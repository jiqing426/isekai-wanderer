#!/usr/bin/env python3
"""Standalone test for ModelRouter — matches spec § 3.2 exactly.

Run: python run_model_router_test.py
"""

import sys
import os
import asyncio
import importlib.util

# Load model_router.py directly (bypasses __init__.py heavy imports)
spec = importlib.util.spec_from_file_location(
    "model_router",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "llm", "model_router.py"),
)
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)

ScenarioType = mr.ScenarioType
ModelConfig = mr.ModelConfig
MODEL_POOL = mr.MODEL_POOL
SCENARIO_MODEL_MAP = mr.SCENARIO_MODEL_MAP
ModelRouter = mr.ModelRouter
model_router = mr.model_router

passed = 0
failed = 0


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name} — {detail}")
        failed += 1


# ═══════════════════════════════════════════════════════════
print("\n═══ ScenarioType (11 scenarios) ═══")
# ═══════════════════════════════════════════════════════════

scenarios = list(ScenarioType)
test("Count = 11", len(scenarios) == 11, f"got {len(scenarios)}")

expected = [
    ("NARRATIVE", "narrative"),
    ("CONVERGENCE", "convergence"),
    ("CHOICE_GENERATION", "choice_gen"),
    ("ENDING", "ending"),
    ("FREE_CHAT", "free_chat"),
    ("FREE_CHAT_ADVANCED", "free_chat_adv"),
    ("MEMORY_EXTRACTION", "memory_ext"),
    ("EMOTION_INFERENCE", "emotion_inf"),
    ("CONTENT_MODERATION", "content_mod"),
    ("DIALOGUE_QUALITY", "dialogue_qual"),
    ("USER_PERSONA_UPDATE", "persona_upd"),
]
for attr, val in expected:
    test(f"{attr} = '{val}'", getattr(ScenarioType, attr).value == val)


# ═══════════════════════════════════════════════════════════
print("\n═══ MODEL_POOL ═══")
# ═══════════════════════════════════════════════════════════

# Note: spec header says "14" but actual list is 4+4+4+1=13
test("Pool size = 13 (S4+A4+B4+C1)", len(MODEL_POOL) == 13, f"got {len(MODEL_POOL)}")

tiers = {}
for n, c in MODEL_POOL.items():
    tiers.setdefault(c.tier, []).append(n)

test("S tier = 4", len(tiers.get("S", [])) == 4, f"got {len(tiers.get('S', []))}")
test("A tier = 4", len(tiers.get("A", [])) == 4, f"got {len(tiers.get('A', []))}")
test("B tier = 4", len(tiers.get("B", [])) == 4, f"got {len(tiers.get('B', []))}")
test("C tier = 1", len(tiers.get("C", [])) == 1, f"got {len(tiers.get('C', []))}")

# Verify each model by name
s_names = ["qwen3.7-max", "deepseek-v4-pro", "kimi-k2.7-code", "glm-5.2"]
a_names = ["qwen3.7-plus", "deepseek-v4-flash", "kimi-k2.6", "glm-5.1"]
b_names = ["qwen3.6-plus", "deepseek-v3.2", "kimi-k2.5", "glm-5"]
c_names = ["qwen3.6-flash"]

for n in s_names:
    test(f"S: {n}", n in MODEL_POOL and MODEL_POOL[n].tier == "S")
for n in a_names:
    test(f"A: {n}", n in MODEL_POOL and MODEL_POOL[n].tier == "A")
for n in b_names:
    test(f"B: {n}", n in MODEL_POOL and MODEL_POOL[n].tier == "B")
for n in c_names:
    test(f"C: {n}", n in MODEL_POOL and MODEL_POOL[n].tier == "C")

# C tier has empty fallback
test("C-tier empty fallback_chain", MODEL_POOL["qwen3.6-flash"].fallback_chain == [])

# All fallback references valid
all_ok = True
bad = ""
for n, c in MODEL_POOL.items():
    for fb in c.fallback_chain:
        if fb not in MODEL_POOL:
            all_ok = False
            bad = f"{n} → {fb}"
test("All fallback refs valid", all_ok, bad)

# Verify exact fallback chains per spec
test("qwen3.7-max chain", MODEL_POOL["qwen3.7-max"].fallback_chain == ["deepseek-v4-pro", "kimi-k2.6", "qwen3.6-plus"])
test("deepseek-v4-pro chain", MODEL_POOL["deepseek-v4-pro"].fallback_chain == ["qwen3.7-max", "kimi-k2.6", "qwen3.6-plus"])
test("qwen3.7-plus chain", MODEL_POOL["qwen3.7-plus"].fallback_chain == ["kimi-k2.6", "glm-5.1", "deepseek-v3.2"])
test("deepseek-v4-flash chain", MODEL_POOL["deepseek-v4-flash"].fallback_chain == ["kimi-k2.5", "glm-5", "qwen3.6-plus"])
test("qwen3.6-plus chain", MODEL_POOL["qwen3.6-plus"].fallback_chain == ["deepseek-v3.2", "glm-5", "kimi-k2.5"])


# ═══════════════════════════════════════════════════════════
print("\n═══ SCENARIO_MODEL_MAP ═══")
# ═══════════════════════════════════════════════════════════

test("All 11 scenarios mapped", all(s in SCENARIO_MODEL_MAP for s in ScenarioType))
test("All mapped models exist", all(m in MODEL_POOL for m in SCENARIO_MODEL_MAP.values()))

expected_map = {
    ScenarioType.NARRATIVE: "qwen3.7-max",
    ScenarioType.CONVERGENCE: "qwen3.7-max",
    ScenarioType.CHOICE_GENERATION: "qwen3.7-plus",
    ScenarioType.ENDING: "qwen3.7-max",
    ScenarioType.FREE_CHAT: "deepseek-v4-flash",
    ScenarioType.FREE_CHAT_ADVANCED: "qwen3.7-plus",
    ScenarioType.MEMORY_EXTRACTION: "qwen3.6-flash",
    ScenarioType.EMOTION_INFERENCE: "qwen3.6-flash",
    ScenarioType.CONTENT_MODERATION: "qwen3.6-flash",
    ScenarioType.DIALOGUE_QUALITY: "qwen3.7-plus",
    ScenarioType.USER_PERSONA_UPDATE: "qwen3.6-plus",
}
for s, m in expected_map.items():
    test(f"{s.value} → {m}", SCENARIO_MODEL_MAP[s] == m)


# ═══════════════════════════════════════════════════════════
print("\n═══ ModelRouter methods ═══")
# ═══════════════════════════════════════════════════════════

test("Singleton exists", isinstance(model_router, ModelRouter))
test("get_model_for_scenario()", callable(getattr(model_router, "get_model_for_scenario", None)))
test("get_fallback_chain()", callable(getattr(model_router, "get_fallback_chain", None)))
test("call_with_fallback()", callable(getattr(model_router, "call_with_fallback", None)))
test("_get_fallback_response()", callable(getattr(model_router, "_get_fallback_response", None)))

# get_model_for_scenario
m = model_router.get_model_for_scenario(ScenarioType.NARRATIVE)
test("NARRATIVE → qwen3.7-max", m.name == "qwen3.7-max" and m.tier == "S")
m = model_router.get_model_for_scenario(ScenarioType.FREE_CHAT)
test("FREE_CHAT → deepseek-v4-flash", m.name == "deepseek-v4-flash" and m.tier == "A")
m = model_router.get_model_for_scenario(ScenarioType.MEMORY_EXTRACTION)
test("MEMORY_EXT → qwen3.6-flash", m.name == "qwen3.6-flash" and m.tier == "C")

# get_fallback_chain
chain = model_router.get_fallback_chain(ScenarioType.NARRATIVE)
test("NARRATIVE chain len=4", len(chain) == 4, f"got {len(chain)}")
test("Chain: qwen3.7-max,deepseek-v4-pro,kimi-k2.6,qwen3.6-plus",
     [c.name for c in chain] == ["qwen3.7-max", "deepseek-v4-pro", "kimi-k2.6", "qwen3.6-plus"])
test("Chain tiers: S,S,A,B",
     [c.tier for c in chain] == ["S", "S", "A", "B"])

# _get_fallback_response
r = model_router._get_fallback_response(ScenarioType.NARRATIVE)
test("NARRATIVE fallback text", r["text"] == "故事还在继续，请稍等片刻……")
r = model_router._get_fallback_response(ScenarioType.FREE_CHAT)
test("FREE_CHAT fallback text", "微微侧头" in r["text"])
r = model_router._get_fallback_response(ScenarioType.ENDING)
test("ENDING fallback (default)", r["text"] == "请稍后再试。")


# ═══════════════════════════════════════════════════════════
print("\n═══ call_with_fallback (async) ═══")
# ═══════════════════════════════════════════════════════════

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def test_success():
    """First model succeeds → return immediately"""
    calls = []

    async def mock_ok(model, msgs, **kw):
        calls.append(model.name)
        return {"text": "OK", "model": model.name, "tier": model.tier}

    model_router._call_model = mock_ok
    resp = await model_router.call_with_fallback(
        ScenarioType.NARRATIVE, [{"role": "user", "content": "hi"}]
    )
    test("Success: model=qwen3.7-max", resp["model"] == "qwen3.7-max")
    test("Success: only 1 call", len(calls) == 1, f"got {len(calls)}")


async def test_degradation():
    """First model fails, second succeeds"""
    n = [0]

    async def mock_partial(model, msgs, **kw):
        n[0] += 1
        if n[0] == 1:
            raise Exception("fail")
        return {"text": "recovered", "model": model.name}

    model_router._call_model = mock_partial
    resp = await model_router.call_with_fallback(
        ScenarioType.NARRATIVE, [{"role": "user", "content": "hi"}]
    )
    test("Degradation: 2 calls", n[0] == 2, f"got {n[0]}")
    test("Degradation: recovered", resp["text"] == "recovered")
    test("Degradation: 2nd model", resp["model"] == "deepseek-v4-pro")


async def test_all_fail():
    """All models fail → preset fallback"""
    async def mock_fail(model, msgs, **kw):
        raise Exception("all fail")

    model_router._call_model = mock_fail
    resp = await model_router.call_with_fallback(
        ScenarioType.NARRATIVE, [{"role": "user", "content": "hi"}]
    )
    test("All fail: returns preset", "text" in resp and resp["text"] == "故事还在继续，请稍等片刻……")


async def test_c_tier_scenario():
    """C-tier scenario (MEMORY_EXTRACTION) → qwen3.6-flash, chain len=1"""
    calls = []

    async def mock_ok(model, msgs, **kw):
        calls.append(model.name)
        return {"text": "mem", "model": model.name}

    model_router._call_model = mock_ok
    chain = model_router.get_fallback_chain(ScenarioType.MEMORY_EXTRACTION)
    test("MEMORY_EXT chain len=1 (C-tier, no fallback)", len(chain) == 1, f"got {len(chain)}")

    resp = await model_router.call_with_fallback(
        ScenarioType.MEMORY_EXTRACTION, [{"role": "user", "content": "hi"}]
    )
    test("MEMORY_EXT: model=qwen3.6-flash", resp["model"] == "qwen3.6-flash")


async def test_all_fail_c_tier():
    """C-tier fails → preset fallback"""
    async def mock_fail(model, msgs, **kw):
        raise Exception("fail")

    model_router._call_model = mock_fail
    resp = await model_router.call_with_fallback(
        ScenarioType.MEMORY_EXTRACTION, [{"role": "user", "content": "hi"}]
    )
    test("C-tier all fail: preset fallback", resp["text"] == "请稍后再试。")


# Run async tests
loop.run_until_complete(test_success())
loop.run_until_complete(test_degradation())
loop.run_until_complete(test_all_fail())
loop.run_until_complete(test_c_tier_scenario())
loop.run_until_complete(test_all_fail_c_tier())
loop.close()


# ═══════════════════════════════════════════════════════════
print(f"\n{'═' * 50}")
print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
print(f"{'═' * 50}")

if failed > 0:
    sys.exit(1)
else:
    print("🎉 All tests passed!")
    sys.exit(0)
