# PRD

## 当前输入

| 项 | 内容 |
| --- | --- |
| 来源 | 用户 PRD |
| 关联 CR | CR-037 |
| 标题 | Corvus-Story-Core 集成部署文档（补充修改版） |
| 记录时间 | 2026-08-06T03:43:08Z |

## 原始 PRD

```markdown
# Corvus-Story-Core 集成部署文档（补充修改版）

## 0 基础设施

### 0.1 模型方案
不部署 Ollama、不部署 vLLM；直接对接自有 OpenAI 兼容中转网关，使用模型 deepseek-v4-flash。

### 0.2 自有中转网关要求
1. 中转网关必须严格兼容 OpenAI /v1/chat/completions 协议
2. 中转网关地址示例：https://your-proxy-domain.com/v1（末尾必须带/v1）
3. 拥有中转网关的 API-Key（sk-xxxx 格式）
4. 网关支持模型名：deepseek-v4-flash，模型输出支持长文本角色扮演、结构化 JSON 输出
5. 服务器可以访问该中转网关网络，无防火墙拦截出站 https 请求

### 0.3 数据库
- PostgreSQL 业务数据库可用（复用现有 isekai 数据库）
- 已创建业务库，用于存储：候选玩家角色、游戏会话、会话 NPC、道具、剧情标记
- Corvus-Story-Core 负责会话内剧情记忆；玩家业务元数据全部存储我方业务数据库

### 0.4 防火墙 & 安全规则
1. 服务器防火墙禁止 8082 端口对公网开放
2. 8082 端口仅允许本地回环 127.0.0.1 访问
3. 验证：本机 curl 127.0.0.1:8082/api/health 可访问；外网访问 服务器IP:8082 必须拒绝

### 0.5 网络环境
- 服务器可以访问 github，能够 git clone 拉取 Corvus-Story-Core 代码
- 服务器出站可以访问中转网关域名
- 本项目不需要部署 Hermes-Agent、不需要部署向量数据库独立服务，记忆全部复用 Corvus-Story-Core 内置记忆模块

## 1 项目现状完整说明

1. Web 前端完全保持原样，访问路由 /game?script={game_session_id} 维持不变；Vue 前端组件、渲染逻辑、按钮、表单、样式、交互逻辑全部禁止改动。
2. URL 参数 script 等价业务字段 game_session_id，全部使用 UUID-v4 格式。
3. 业务模型：
   - 每个用户拥有最多 3 个候选玩家角色（角色池）
   - 用户打开页面，从 3 个角色选择其中 1 个角色进入剧本会话
   - 当前剧本会话，只加载选中的 1 个角色进入 AI 上下文；另外 2 个候选角色完全不送入 Corvus
   - 用户想要换角色，必须开启全新剧本会话，复用旧会话不允许
4. 叙事引擎：Corvus-Story-Core，部署路径 /root/code/Corvus-Story-Core；端口绑定 127.0.0.1:8082；彻底关闭自带 Web 调试 UI，只保留 FastAPI API 内核服务，开启框架内置游戏记忆模块，不依赖外部 Hermes-Agent。
5. 职责拆分：
   - Corvus-Story-Core：负责 GM 游戏主循环、剧情生成、会话内记忆管理、解析剧情输出结构化世界状态、NPC 记忆、事件摘要。LLM 请求转发给自有中转网关，模型 deepseek-v4-flash。
   - 我方业务后端：管理用户、角色池、会话元数据、数据库持久化、接口转发、权限校验；接收 Corvus 输出的 world_state，同步道具、好感、剧情标记到业务数据库。
   - 移除 Hermes-Agent，不再有独立记忆服务进程；长会话记忆能力全部由 Corvus-Story-Core 内部实现。
6. ID 强制规范：所有业务实体 ID 统一使用 UUID v4，禁止自增数字 ID。

## 2 Corvus-Story-Core 完整部署

### 2.1 拉取源代码
```bash
cd /root/code
git clone https://github.com/JustLateNightAI/Corvus-Story-Core.git
cd Corvus-Story-Core
```

### 2.2 创建 Python 虚拟环境并安装依赖
```bash
python3.10 -m venv venv  # 或 python3.11
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 编写 .env 配置文件
文件路径：/root/code/Corvus-Story-Core/.env
```env
# LLM大模型｜自有中转网关配置
LLM_BASE_URL=https://your-proxy-domain.com/v1
LLM_API_KEY=sk-你的中转APIKEY
LLM_MODEL=deepseek-v4-flash

# 服务网络绑定
SERVER_HOST=127.0.0.1
SERVER_PORT=8082

# UI开关：关闭全部自带网页前端
DISABLE_WEB_UI=true
SERVE_STATIC=false

# Session ID生成规则
GENERATE_UUID_SESSION=true

# 内置记忆模块开启（替代Hermes-Agent）
ENABLE_INTERNAL_MEMORY=true
MEMORY_AUTO_SUMMARY=true
MEMORY_MAX_TURNS=12

# 日志配置
LOG_LEVEL=info
```

### 2.4 systemd 守护进程配置
文件：/etc/systemd/system/corvus-story.service
```ini
[Unit]
Description=Corvus-Story-Core Narrative Backend Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/code/Corvus-Story-Core
ExecStart=/root/code/Corvus-Story-Core/venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8082
Restart=on-failure
RestartSec=5
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target
```

### 2.5 部署校验步骤
1. systemctl status corvus-story → active (running)
2. curl http://127.0.0.1:8082/api/health → 返回健康 json
3. 外网访问 服务器IP:8082 → 必须拒绝
4. journalctl -u corvus-story -f → 无 401/网络报错
5. 模拟 Corvus 内部链路 → 可成功调用中转网关返回 deepseek-v4-flash 结果

### 2.6 Corvus 业务约束
1. Corvus 仅作为叙事计算内核；会话剧情记忆由 Corvus 内部维护；用户业务数据全部存储我方业务数据库
2. 禁止修改 Corvus 内部 GM 逻辑、提示词体系；只封装外层调用层
3. Corvus 只接受我方业务后端内网调用；前端浏览器永远不能直接请求 8082
4. 本项目不安装 ollama/vLLM、不部署 Hermes-Agent，不启动额外记忆服务进程

## 3 数据库实体模型（全部 ID 为 UUID v4）

### 3.1 PlayerCandidate｜候选玩家角色池
```json
{
  "player_candidate_id": "uuid-v4",
  "user_id": "uuid-v4",
  "name": "string 角色名字",
  "personality": "string 角色性格描述",
  "backstory": "string 角色完整背景故事",
  "appearance": "string 外貌描述",
  "initial_inventory": ["item-id-uuid-v4"],
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 3.2 GameSession｜剧本会话
```json
{
  "game_session_id": "uuid-v4",
  "user_id": "uuid-v4",
  "selected_player_candidate_id": "uuid-v4 | null",
  "initial_location_id": "uuid-v4",
  "status": "enum [waiting_select_player, playing, finished]",
  "corvus_internal_session_id": "uuid-v4",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 3.3 NpcInSession｜本局会话内的 NPC 实例
```json
{
  "session_npc_id": "uuid-v4",
  "game_session_id": "uuid-v4",
  "npc_template_id": "uuid-v4",
  "affinity": 0,
  "present": true,
  "created_at": "timestamp"
}
```

### 3.4 InventoryItem｜剧本会话道具
```json
{
  "item_id": "uuid-v4",
  "game_session_id": "uuid-v4",
  "name": "string",
  "desc": "string",
  "created_at": "timestamp"
}
```

### 3.5 StoryFlag｜剧情标记
```json
{
  "flag_id": "uuid-v4",
  "game_session_id": "uuid-v4",
  "flag_key": "string",
  "flag_value": "any",
  "created_at": "timestamp"
}
```

## 4 后端接口完整设计

最高优先级约束：前端页面完全不动，对外接口入参、返回 JSON 字段名保持现有协议，不做破坏性变更；所有改造全部放在后端内部逻辑层。

### 4.1 创建剧本会话
POST /api/game/session/create
入参：{"user_id": "uuid-v4"}
返回：{"code": 0, "data": {"game_session_id": "uuid-v4"}}

### 4.2 获取候选玩家角色
GET /api/game/player/candidates?user_id=xxx
返回：{"code": 0, "data": [...]}

### 4.3 用户选定角色
POST /api/game/session/select-player
入参：{"game_session_id": "uuid-v4", "player_candidate_id": "uuid-v4"}

后端内部执行步骤：
1. 查询 GameSession，校验 status=waiting_select_player
2. 更新 GameSession：selected_player_candidate_id + status=playing
3. 读取候选玩家角色完整数据
4. 过滤：另外两个候选角色不送入 Corvus
5. 内网调用 Corvus http://127.0.0.1:8082/api/game/create_session
6. 存储 corvus_internal_session_id
7. 接收 Corvus 返回的初始世界场景数据，适配为前端预期 JSON 格式返回

### 4.4 游戏回合接口
POST /api/game/game-turn
入参：{"game_session_id": "uuid-v4", "player_input": "玩家输入的动作文本"}

后端内部执行流程：
1. 查询 GameSession，校验 status=playing
2. 读取选中玩家角色、corvus_internal_session_id、在场 NPC、location、story_flags、inventory
3. 内网 POST 请求 Corvus 127.0.0.1:8082/api/game/turn
4. 接收 Corvus 返回：scene_desc、npc_dialogues、player_options、world_state
5. 解析 world_state，同步好感、道具、剧情标记到业务数据库
6. 将 Corvus 输出映射转换为前端原有协议 JSON 返回

## 5 记忆系统整体规则（无 Hermes-Agent）
1. 会话隔离：依靠 corvus_internal_session_id，每条 GameSession 对应 Corvus 内部独立 session
2. Corvus 内置记忆开启，自动做：对话滚动窗口、关键事件摘要、NPC 关系、剧情事实记录
3. 我方业务数据库存储世界状态快照（道具、好感、剧情 flag）；Corvus 存储会话剧情对话与事件记忆
4. 后续如需扩展更强 RAG 长期记忆，再额外增加向量库，当前版本不引入

## 6 强制业务规则
1. 用户最多 3 个候选玩家角色；开局三选一；只加载选中角色进入 AI 上下文
2. 换角色必须创建全新 game_session_id；禁止旧会话直接替换 player_candidate_id
3. 全部业务主键 UUID-v4，禁止自增数字 ID
4. 前端 Vue 所有代码禁止修改；页面路由 /game?script= 格式保留
5. Corvus 服务仅本机 127.0.0.1 访问，8082 端口对公网屏蔽
6. 业务数据持久化全部存储我方业务数据库
7. 不安装、不使用 ollama、vLLM、Hermes-Agent

## 7 Agent 开发权限范围

✅允许修改：
1. Linux 脚本、systemd 服务单元配置、corvus .env 配置
2. 业务数据库建表语句、DAO 层、实体模型
3. 后端 Service 业务逻辑层
4. 后端接口内部实现代码
5. Corvus HTTP 调用封装代码
6. ID 生成逻辑，全部 UUID-v4

❌绝对禁止修改：
1. Vue 前端全部源代码、组件、样式、交互逻辑
2. 对外 API 的入参字段名、返回 JSON 字段结构（保持对现有前端兼容）
3. 页面路由格式 /game?script=
4. 用户可见任何 UI 表现
5. 不引入 ollama/vLLM/Hermes-Agent

## 8 开发完成后完整测试校验清单
- [ ] Corvus 服务 systemd active (running)；curl 127.0.0.1:8082/api/health 返回正常；公网访问 8082 拒绝
- [ ] Corvus 日志无 401、无网络超时；可正常调用中转网关返回 deepseek-v4-flash 结果
- [ ] http://47.107.174.176:8081/game?script={game_session_id} 页面正常打开
- [ ] 获取候选角色接口返回最多 3 个角色数据
- [ ] select-player 选定角色；GameSession 状态更新为 playing；仅该角色送入 Corvus
- [ ] game-turn 接口正常调用，返回 scene_desc、npc_dialogues、player_options，页面渲染正常
- [ ] world_state 变化后，好感、道具、剧情标记正确落库
- [ ] 不同 game_session 对应不同 corvus_internal_session_id，记忆隔离
- [ ] 更换角色生成全新 game_session_id，旧会话记忆不影响新会话
- [ ] 数据库所有业务表主键 UUID v4，无自增 ID
- [ ] 服务器没有 ollama、vLLM、Hermes-Agent 进程
```

## 结构化摘要

| 项 | 内容 |
| --- | --- |
| 关联 CR | CR-037 |
| 变更类型 | Feature — 新增 AI 自由叙事能力（Corvus-Story-Core 集成） |
| 优先级 | P1 |
| 目标用户 | 乙女玩家（核心）、冒险者（核心） |

### 目标

集成 Corvus-Story-Core（Node.js AI 叙事引擎）作为新引擎选项，与现有 NarrativeEngine 共存。Corvus 负责 GM 游戏主循环、剧情生成、会话内记忆；我方后端负责业务数据持久化、接口转发、权限校验、向量记忆（pgvector）跨会话语义召回。

### 范围

- Corvus 部署在 127.0.0.1:8082，systemd 守护，LLM 走 thoushub 网关调用 deepseek-v4-flash
- 新旧引擎共存，feature flag（engine_type 字段）切换
- 前端 API 签名不变，后端内部切换 Corvus 路径
- SSE 流式透传（不在后端组装等待）
- 向量记忆：本地 bge-small-zh + pgvector，写入（对话结束→向量化）+ 召回（回合开始→NPC knownInfo 注入）
- 所有 UUID v4
- 新增 5 张表 + embedding 维度 1536→512 + 删除 6 张无用 backup 表

### 非目标

- 不部署 ollama / vLLM / Hermes-Agent
- 不修改 Corvus 内部 GM 逻辑 / 提示词
- 不修改 Vue 前端组件 / 样式 / 交互逻辑（仅 game.ts 数据层 ~40 行）
- 不废弃旧剧本系统（Script / Route / Node）
- 不新增基础设施费用
- 不引入独立向量数据库服务

### 验收标准

详见 `workflow/changes/CR-037/acceptance.md`，共 28 条 AC（P0: 20 条, P1: 8 条）。

### 待澄清问题

详见 `openspec/changes/corvus-story-integration/proposal.md` Open Questions 章节。Q-001（不可逆 DB 迁移）阻塞 MVP，需 PL 在 DESIGN_GATE 前取得人工确认。Q-002~Q-006 已关闭（非阻塞）。

### World.json 最小字段定义（GAP-003 Backfill）

Corvus-Story-Core 的 `WorldInfo` 接口（`server/types/index.ts`）定义了以下字段，后端创建游戏时 `world` 对象必须覆盖所有字段：

| 字段 | 类型 | 说明 | 草案值 |
| --- | --- | --- | --- |
| setting | string | 世界设定关键词，用于 GM 系统提示词 `# WORLD > Setting:` | `modern-fantasy` |
| tone | string | 叙事基调，用于 GM 系统提示词 `# WORLD > Tone:` | `mysterious` |
| rules | string | 世界规则文本，用于 GM 系统提示词 `# WORLD > Rules:` | 见下方草案内容 |
| customInstructions | string | 额外叙事指令，用于 GM 系统提示词 `# WORLD > Additional instructions:` | 见下方草案内容 |
| currencyName | string | 货币名称，用于玩家初始金币显示 | `星尘` |
| era | string | 时代背景，用于 GM 系统提示词 `# WORLD > Era:` | `modern` |
| narratorEnabled | boolean | 是否允许 [Narrator] 旁白块 | `true` |

> **注意**：Corvus `WorldInfo` 没有 `worldName` / `settingDescription` 字段。世界名称通过 `GameConfig.name`（创建游戏时的 `name` 字段）承载；详细设定描述拆分到 `setting`（关键词）+ `rules`（规则文本）+ `customInstructions`（叙事指令）三个字段中。

#### World 内容草案（异世界漫游）

```json
{
  "setting": "modern-fantasy — 当代都市与魔法共存的世界。科技与超自然力量交织，人类与异界来客共存于现代都市。",
  "tone": "mysterious — 充满悬念和探索感，叙事基调偏向神秘、未知和惊奇，但不含恐怖元素。",
  "rules": "1. 异世界来客（穿越者）拥有不同于原住民的能力体系，但能力需逐步觉醒。\n2. 都市中存在隐藏的魔法空间，普通人无法感知。\n3. NPC 好感度影响剧情走向和可触发事件。\n4. 玩家选择具有不可逆性，每个决策影响后续剧情分支。\n5. 道具和剧情标记（story_flags）跨回合持久化。\n6. 玩家最多携带 10 件道具。\n7. 战斗采用回合制叙事，不使用骰子或数值伤害表。",
  "customInstructions": "叙事风格参考视觉小说和轻小说。每回合输出：1段场景描写（2-4句）+ 1-3条 NPC 对话 + 2-4个玩家选项。避免过长描写，保持节奏明快。NPC 对话需体现性格差异。选项需有实际意义（影响好感/剧情/道具）。",
  "currencyName": "星尘",
  "era": "modern — 现代都市背景，存在隐藏魔法世界",
  "narratorEnabled": true
}
```

#### 后端 world 传入逻辑要求

- `CorvusAdapter.create_session()` 调用 `CorvusClient.create_game()` 时，**必须传入完整的 `world_setting` 字典**，覆盖所有 `WorldInfo` 字段。
- 当前代码（`corvus_adapter.py` line ~117）调用 `create_game()` 时未传 `world_setting` 参数，导致使用默认值（`setting="modern-fantasy"`, `tone="mysterious"`, `rules=[]`, `customInstructions=""`, `currencyName="星尘"`, `era="modern"`），`rules` 和 `customInstructions` 为空。
- 修复要求：`CorvusAdapter.create_session()` 从配置或常量中读取完整 world 内容，传入 `CorvusClient.create_game(world_setting=<上述草案>)`。
- 此修复属于 BE 职责范围，PM 在此仅定义内容需求和字段规范。
