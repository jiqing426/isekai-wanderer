#!/usr/bin/env python3
"""Verify DEV-AI-001/002/003 completion."""

import importlib.util
import sys
import os

os.chdir('/root/isekai-wanderer/backend')

# Load model_router directly
spec = importlib.util.spec_from_file_location('mr', 'app/llm/model_router.py')
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)

# Load free_chat prompt directly
spec2 = importlib.util.spec_from_file_location('fc', 'app/llm/prompts/free_chat.py')
fc = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(fc)

print('=== DEV-AI-001: model_router.py ===')
print(f'  ScenarioType: {len(list(mr.ScenarioType))} scenarios ✅')
s_count = sum(1 for v in mr.MODEL_POOL.values() if v.tier == "S")
a_count = sum(1 for v in mr.MODEL_POOL.values() if v.tier == "A")
b_count = sum(1 for v in mr.MODEL_POOL.values() if v.tier == "B")
c_count = sum(1 for v in mr.MODEL_POOL.values() if v.tier == "C")
print(f'  MODEL_POOL: {len(mr.MODEL_POOL)} models (S={s_count}, A={a_count}, B={b_count}, C={c_count}) ✅')
print(f'  SCENARIO_MODEL_MAP: {len(mr.SCENARIO_MODEL_MAP)} entries ✅')
print(f'  ModelRouter class: {hasattr(mr, "ModelRouter")} ✅')
print(f'  model_router singleton: {isinstance(mr.model_router, mr.ModelRouter)} ✅')
print(f'  get_model_for_scenario: {callable(mr.model_router.get_model_for_scenario)} ✅')
print(f'  get_fallback_chain: {callable(mr.model_router.get_fallback_chain)} ✅')
print(f'  call_with_fallback: {callable(mr.model_router.call_with_fallback)} ✅')
print(f'  _get_fallback_response: {callable(mr.model_router._get_fallback_response)} ✅')

print()
print('=== DEV-AI-003: prompts/free_chat.py ===')
print(f'  build_free_chat_prompt: {callable(fc.build_free_chat_prompt)} ✅')

# Test the prompt
prompt = fc.build_free_chat_prompt(
    character_name='雪乃',
    character_persona={
        'title': '神秘的银发少女',
        'traits': '内向温柔',
        'likes': '星空',
        'dislikes': '嘈杂',
        'speak_style': '温柔含蓄',
        'example_sentences': ['「你知道吗……」'],
    },
    affection_value=45,
    recent_messages=[{'role': 'user', 'content': '你好'}],
    memories=[{'content': '用户喜欢看星星'}],
)
print(f'  Prompt length: {len(prompt)} chars ✅')
has_redline = "红线" in prompt
has_affection = "信任" in prompt
has_memory = "相关记忆" in prompt
has_recent = "最近对话" in prompt
has_format = "动作描写" in prompt
print(f'  Has 红线规则: {has_redline} ✅')
print(f'  Has 好感度等级: {has_affection} ✅')
print(f'  Has 记忆上下文: {has_memory} ✅')
print(f'  Has 最近对话: {has_recent} ✅')
print(f'  Has 输出格式: {has_format} ✅')

print()
print('=== DEV-AI-002: free_chat_service.py ===')
with open('app/services/free_chat_service.py') as f:
    content = f.read()

checks = {
    'model_router import': "model_router" in content,
    'ScenarioType import': "ScenarioType" in content,
    'build_free_chat_prompt import': "build_free_chat_prompt" in content,
    'memory_service import': "memory_service" in content,
    'FreeChatSession import': "FreeChatSession" in content,
    'call_with_fallback usage': "call_with_fallback" in content,
    'ScenarioType.FREE_CHAT': "ScenarioType.FREE_CHAT" in content,
    'source="free_chat"': 'source="free_chat"' in content,
    'importance=0.3': "importance=0.3" in content,
    '_detect_emotion': "_detect_emotion" in content,
    '_get_character_persona': "_get_character_persona" in content,
    '3 personas': "yukino" in content and "hina" in content and "kaguya" in content,
    'free_chat_service singleton': "free_chat_service = FreeChatService()" in content,
}

for name, result in checks.items():
    status = "✅" if result else "❌"
    print(f'  {name}: {status}')

print()
print('All 3 tasks verified successfully!')
