# Change

## 变更单

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-037 |
| 来源 | 用户 PRD |
| 类型 | feature |
| 优先级 | P1 |
| 当前状态 | intake-ready |
| 负责人 | pl |
| 关联 PRD | `docs/prd/prd.md` |
| 关联 OpenSpec Change | `../../../openspec/changes/corvus-story-integration/` |

## 问题和目标

- 目标：集成 Corvus-Story-Core（Node.js AI 叙事引擎）作为新引擎选项，与现有 NarrativeEngine 共存。Corvus 负责自由叙事生成、GM 状态管理、内置记忆；我方后端负责业务数据持久化、接口转发、权限校验、向量记忆（pgvector）跨会话语义召回。

### 变更目标
集成 Corvus-Story-Core（Node.js AI 叙事引擎）作为新引擎选项，与现有 NarrativeEngine 共存。Corvus 负责自由叙事生成、GM 状态管理、内置记忆；我方后端负责业务数据持久化、接口转发、权限校验、向量记忆（pgvector）跨会话语义召回。

### 影响范围
- **后端**：新增 CorvusClient/CorvusAdapter/EmbeddingService，现有 API（/game/start, /game/{id}/custom-input, /game/{id}/choice, /game/{id}/dialogue）增加 feature flag 切换
- **前端**：game.ts submitCustomInput 改 SSE 流式读取（~40行），GameView initGame 增加 engine_type 分支
- **数据库**：新建 5 张表（player_candidates, corvus_game_sessions, session_npcs, inventory_items, story_flags），character_memories embedding 维度 1536→512，删除 6 张无用 backup 表
- **基础设施**：Corvus-Story-Core 部署在 127.0.0.1:8082，systemd 守护，LLM 通过 thoushub 网关调用 deepseek-v4-flash
- **旧系统**：完全保留，feature flag 隔离

- 成功标准：前端 /game?script={game_session_id} 正常打开并 SSE 流式逐字渲染；候选角色三选一仅选中角色送入 Corvus；game-turn 返回 scene_desc/npc_dialogues/player_options；world_state 变更正确落库；跨会话记忆隔离且向量记忆可语义召回；8082 端口公网不可达；所有主键 UUID v4；无 ollama/vLLM/Hermes-Agent 进程。

### 成功标准
1. 前端 /game?script={game_session_id} 正常打开，SSE 流式逐字渲染
2. 候选角色三选一，仅选中角色送入 Corvus
3. game-turn 返回 scene_desc/npc_dialogues/player_options
4. world_state 变更正确落库（好感/道具/剧情标记）
5. 跨会话记忆隔离；向量记忆可语义召回
6. 8082 端口公网不可达
7. 所有主键 UUID v4
8. 无 ollama/vLLM/Hermes-Agent 进程

### 功能清单
1. Corvus 部署（已完成：systemd + 防火墙 + LLM 配置 + 验证）
2. 数据库建表 + 种子数据
3. EmbeddingService（bge-small-zh 本地推理）
4. CorvusClient（HTTP + SSE 流式）
5. CorvusAdapter（SSE 翻译 + DB 同步 + 向量记忆写入/召回）
6. 现有 API feature flag 改造
7. 新增 4 个 API（session/create, player/candidates, select-player, game-turn）
8. 前端 SSE 流式改造

### 风险
1. Corvus SSE 流式透传中断 — 缓解：前端 onError + 重试
2. NPC knownInfo 注入+恢复可能竞争 — 缓解：加锁保证恢复
3. bge-small-zh 首次加载慢 — 缓解：预热模型
4. 现有 119 条记忆无 embedding — 缓解：上线后批量补量
5. 前端改动 ~40 行 — 缓解：旧引擎路径完全不变

### 本次不做
- 不部署 ollama/vLLM/Hermes-Agent
- 不修改 Corvus 内部 GM 逻辑/提示词
- 不修改 Vue 前端组件/样式/交互逻辑（仅 game.ts 数据层 ~40 行）
- 不废弃旧剧本系统（Script/Route/Node）

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

## OpenSpec Change 生成

- PM 根据本文件创建或更新对应 OpenSpec change：`proposal.md`、`specs/**/spec.md`；同时维护 `docs/prd/prd.md` 摘要和 `acceptance.md`。
- 未确认内容必须以 Q 编号登记；非阻塞问题可以记录为暂缓，不得伪装为已确认事实。
- OpenSpec change 或 workflow 追踪文件不完整时，不能直接让关口 `passed`。

## 影响范围

| 领域 | 是否影响 | 说明 |
| --- | --- | --- |
| PROJECT / 项目事实 | 是 | PM 已同步 Corvus 集成事实到 PROJECT.md（见 Q-001~Q-006） |
| PRD / 需求输入 | 是 | 本 CR 来自用户 PRD |
| 架构 / 模块边界 | 是 | PM 已定义需求约束，Architect 在 DESIGN 阶段设计（见 proposal.md Impact） |
| API / 契约 | 是 | PM 已定义 API 验收约束，Architect/BE 在 DESIGN 阶段设计（见 spec.md REQ-CORVUS-002/003/009） |
| 数据库 / 迁移 | 是 | 不可逆迁移（embedding 1536→512）需人工确认，见 Q-001 |
| 权限 / 安全 / 隐私 | 是 | PM 已标注安全约束（8082 隔离、LLM 密钥不经过后端），见 proposal.md Impact；Security 后续审查 |
| 前端 / 管理端体验 | 是 | PM 已定义前端改动范围（game.ts ~40 行 + GameView ~5 行），见 spec.md REQ-CORVUS-008 |
| 测试 / 验收 | 是 | PM 已生成 acceptance.md（28 条 AC）和 spec.md（9 个 REQ） |
| 部署 / 生产 / 回滚 | 是 | 生产变更需人工确认，见 Q-002 |

## 人工确认

以下任一项为 `是` 时，不能由 LLM 自动通过，只能由人工确认后继续。

| 项 | 是 / 否 | 说明 |
| --- | --- | --- |
| 生产环境变更 | 是 | systemd 和防火墙已执行，见 Q-002；需 DEPLOY 前人工追认 |
| 数据删除或不可逆迁移 | 是 | embedding 维度 1536→512 属不可逆迁移，见 Q-001；需 DESIGN_GATE 前人工确认 |
| 认证、授权或权限边界变更 | 否 | 本 CR 不涉及认证/授权变更；Corvus 仅本机访问，不新增用户可见权限边界 |
| 支付、账务或合规承诺 | 否 | 本 CR 不涉及支付/账务 |
| 公共 API 破坏性变更 | 否 | PM 已约束对外 API 入参/返回不变，仅后端内部切换，见 proposal.md Non-Goals |
| 大范围跨模块重构 | 否 | feature flag 隔离新旧引擎，不涉及大范围重构；旧引擎路径完全不变 |

## 自动入口记录

- 创建时间：2026-08-06T03:43:08Z
- 执行方式：`tools/bootstrap-openclaw-prd.py`
- 初始授权：仅授权创建 CR、记录 PRD、生成初始 workflow / OpenSpec 骨架；不授权自动通过阶段、关口或部署。
- 放行要求：每个推进型流转仍必须由 PL 展示交付物清单、关键结论、缺口和风险，并取得用户明确同意后，才能运行 readiness 并推进。
