# CR-007 Bug 与 LLM 架构问题分析

**分析时间**: 2026-07-21T23:30:00Z  
**分析人**: PL  
**状态**: 待老大确认

---

## 一、Bug 分析（3 个）

### Bug 1: 自由对话 API 500 错误 🔴 最严重

**位置**: `backend/app/api/v1/chat.py` 第49行

**错误**: `TypeError: FreeChatService.send_message() missing 1 required positional argument: 'db'`

**根因分析**:
- `chat.py` 第13行: `from app.services.free_chat_service import free_chat_service`
- `free_chat_service.py` 第203行: `free_chat_service = FreeChatService()`
- 调用处传递了 `db=db, user_id=user_id, character_id=..., message=..., session_id=...`
- `send_message` 签名: `async def send_message(self, db, user_id, character_id, message, script_id=None, session_id=None)`

**可能原因**:
1. 循环导入导致 `free_chat_service` 导入的不是实例而是类
2. 或者 `db` 参数传递方式有问题（关键字参数 vs 位置参数）

**修复方案**:
- 检查导入链，确保 `free_chat_service` 是实例
- 或在调用处改为位置参数传递 `db`

**工时**: 0.5d

---

### Bug 2: 游戏选择接口参数名不一致 🟡

**位置**: `/api/v1/game/{session_id}/choice`

**分析结果**: 经代码检查，**前后端参数名一致**：
- 前端 `stores/game.ts` 第158行: `choice_id: choiceId`
- 后端 `game.py` 第28行: `choice_id: str`
- 后端第217行: `choice_id=UUID(request.choice_id)`

**结论**: 代码层面参数名一致。422 错误可能是：
1. 前端传了空 `choice_id`
2. 或 `choice_id` 格式不对（不是有效 UUID）
3. 或前端某个地方传了 `choice_index` 而非 `choice_id`

**修复方案**:
- 前端增加 `choice_id` 非空校验
- 后端返回更明确的错误信息

**工时**: 0.5d

---

### Bug 3: 好感度历史 API 返回空数组 🟢 可能正常

**位置**: `/api/v1/affection/history?character_id=xxx`

**分析结果**: 经代码检查，**写入逻辑正确**：
- `affection_service.py` 第117-128行: 每次 `update_affection()` 都会创建 `AffectionHistory` 记录
- 查询逻辑也正确：按 `user_id + character_id` 过滤

**结论**: 返回空数组是因为**还没有触发过好感动画**（没有做过影响好感度的选择）。这是正常行为。

**修复方案**: 无需修复，但建议：
- 添加测试数据种子脚本
- 或在文档中说明

**工时**: 0d（无需修复）

---

## 二、LLM 架构问题分析（4 个需求）

### 需求 1: LLM Provider 切为真实模型 🔴 最高优先级

**当前状态**:
- `.env` 已配置:
  ```
  LLM_PROVIDER=custom
  LLM_API_KEY=sk-6Nig_1ndlOU3eaIVK2dDHQ
  LLM_BASE_URL=https://www.thoushub.com/v1
  LLM_MODEL=deepseek-chat
  OPENAI_API_KEY=sk-6Nig_1ndlOU3eaIVK2dDHQ
  OPENAI_BASE_URL=https://www.thoushub.com/v1
  OPENAI_MODEL=deepseek-chat
  ```
- 但 `config.py` 只定义了:
  ```python
  llm_provider: str = "mock"  # 只支持 "openai" | "mock"
  llm_api_key: str = "test-key-placeholder"
  llm_model: str = "gpt-4o-mini"
  openai_api_key: str = ""
  openai_model: str = "gpt-4o-mini"
  ```
- **缺少**: `llm_base_url` 字段

**问题**:
1. `config.py` 没有 `llm_base_url` 字段，`.env` 中的 `LLM_BASE_URL` 不会被读取
2. `llm_provider` 默认 `"mock"`，`.env` 中 `LLM_PROVIDER=custom` 不被识别
3. `gateway.py` 判断逻辑: `if settings.llm_provider == "mock" or not settings.openai_api_key` → 用 mock

**修复方案**:
1. `config.py` 添加 `llm_base_url: str = ""`
2. `config.py` 修改 `llm_provider` 支持 `"thoushub"` | `"openai"` | `"mock"`
3. `gateway.py` 修改判断逻辑，优先使用 `llm_api_key` + `llm_base_url`

**工时**: 0.5d

---

### 需求 2: Gateway 层架构断层 🟡

**当前状态**:
- `ModelRouter` 已实现（`backend/app/llm/model_router.py`），定义了 13 个模型 + 场景映射
- `LLMGateway.provider` 属性直接创建 `OpenAIProvider` 或 `MockProvider`，完全没用到 `ModelRouter`

**问题**: `ModelRouter` 设计了场景→模型映射，但 `Gateway` 没用它

**修复方案**:
1. `LLMGateway` 初始化时创建 `ModelRouter` 实例
2. `provider` 属性改为接收 `scenario` 参数，根据场景选择模型
3. 或新增 `get_provider_for_scenario(scenario)` 方法

**工时**: 1d

---

### 需求 3: 新增 ThoushubProvider 🟡

**当前状态**:
- `OpenAIProvider` 使用 `AsyncOpenAI(api_key=..., model=...)`
- 不支持自定义 `base_url`

**问题**: Thoushub 代理使用 OpenAI 兼容 API，但需要自定义 `base_url`

**修复方案**:
- 修改 `OpenAIProvider` 支持 `base_url` 参数
- `AsyncOpenAI(api_key=..., base_url=..., model=...)`
- 不需要新建 Provider，只需扩展 `OpenAIProvider`

**工时**: 0.5d

---

### 需求 4: .env 配置真实 API Key 和 Base URL 🟢

**当前状态**: `.env` 已配置（见需求1）

**问题**: `config.py` 没有读取这些字段

**修复方案**: 同需求1

**工时**: 0d（已包含在需求1中）

---

## 三、优先级排序

| 优先级 | 任务 | 工时 | 依赖 |
|--------|------|------|------|
| **P0** | Bug 1: 修复自由对话 API 500 | 0.5d | 无 |
| **P0** | 需求 1+4: config.py 支持 llm_base_url + 真实模型 | 0.5d | 无 |
| **P0** | 需求 3: OpenAIProvider 支持 base_url | 0.5d | 需求1 |
| **P1** | 需求 2: Gateway 集成 ModelRouter | 1d | 需求1+3 |
| **P1** | Bug 2: 游戏选择接口参数校验 | 0.5d | 无 |
| **P2** | Bug 3: 好感度历史（无需修复） | 0d | - |

**总计**: 3d

---

## 四、执行计划

### Phase 1: 紧急修复（P0，1.5d）

1. **BE**: 修复 Bug 1（自由对话 API 500）
2. **BE**: 修改 config.py 支持 `llm_base_url`
3. **BE**: 修改 OpenAIProvider 支持 `base_url`
4. **BE**: 修改 gateway.py 使用真实模型

### Phase 2: 架构完善（P1，1.5d）

5. **BE**: Gateway 集成 ModelRouter
6. **BE**: 游戏选择接口参数校验

### Phase 3: 验证

7. **QA**: 验证所有 API 正常
8. **QA**: 验证 LLM 真实调用

---

## 五、与 v4.4 页面重写的关系

**这些 Bug/LLM 问题是后端问题，与前端页面重写并行**。

- FE 继续按原计划重写页面（DEV-FE-003 ~ DEV-FE-009）
- BE 先修复这些问题，再配合 FE 联调

---

## 六、任务清单

| 任务ID | 任务描述 | 角色 | 优先级 | 工时 |
|--------|----------|------|--------|------|
| DEV-BE-002 | 修复自由对话 API 500 错误 | BE | P0 | 0.5d |
| DEV-BE-003 | config.py 支持 llm_base_url + 真实模型配置 | BE | P0 | 0.5d |
| DEV-BE-004 | OpenAIProvider 支持 base_url 参数 | BE | P0 | 0.5d |
| DEV-BE-005 | Gateway 集成 ModelRouter | BE | P1 | 1d |
| DEV-BE-006 | 游戏选择接口参数校验增强 | BE | P1 | 0.5d |

---

**分析完成，等待老大确认后分配任务。**
