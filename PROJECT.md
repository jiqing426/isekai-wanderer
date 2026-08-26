# PROJECT

本文记录项目级事实。新项目初始化后通常由 `skills/pm/SKILL.md` 从 `docs/prd/prd.md` 同步已确认的目标、范围、用户和依赖；PRD 未覆盖的信息标记为"待确认"。

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 异世界漫游（Isekai Wanderer） |
| 项目代号 | isekai-wanderer |
| 项目阶段 | MVP 开发（CR-001） |
| 负责人 | 待确认 |
| 主要用户 | 乙女玩家（核心）、冒险者（核心） |
| 代码仓库 | 待确认 |
| 生产入口 | 待确认（部署平台见 Q-005） |

## 范围

### 包含

- S001 叙事一致性引擎（REQ-001）
- S002 结构化剧本系统（2 个剧本：乙女恋爱 3 路线 + 奇幻冒险 2 路线，REQ-002）
- S003 跨会话角色记忆（REQ-003）
- S004 好感度系统基础版（REQ-004）
- S006 基础视觉呈现（REQ-005）
- S007 用户账户系统（仅邮箱，REQ-006）
- S016 每日签到 Streak（REQ-007）
- S017 每日任务系统（REQ-008）
- S018 Corvus-Story-Core AI 自由叙事引擎集成（CR-037, REQ-CORVUS-001~009）— 新旧引擎共存 + SSE 流式 + pgvector 向量记忆

### 不包含

- 真实支付/订阅（S025/S024）
- OAuth 第三方登录
- UGC、社交分享、国际化、SEO
- Push 通知、邮件召回
- 自由对话模式（旧引擎路径）
- 管理后台
- 第 3 个剧本
- CG 画廊系统
- ollama / vLLM / Hermes-Agent 部署（CR-037 明确不做）

## 模块清单

| 模块 | 路径 | 职责 | 技术栈 | 负责人 |
| --- | --- | --- | --- | --- |
| 后端 | `backend/` | API、叙事引擎、记忆系统、Corvus 集成 | Python 3.12 + FastAPI + SQLAlchemy + Alembic + pgvector + sentence-transformers (bge-small-zh) | 待确认 |
| 前端 | `frontend/` | PWA 网页端用户应用 | Vue 3 + TS + Vite + Pinia + Naive UI | 待确认 |
| AI | `backend/app/llm/` | LLM 集成、角色记忆、对话生成 | LLM Gateway (thoushub → deepseek-v4-flash) + bge-small-zh-v1.5 (本地 embedding) | 待确认 |
| 部署 | `deploy/` | 部署和运行时配置 | Docker + Nginx + systemd (Corvus 服务) | 待确认 |

## 外部依赖

| 依赖 | 用途 | 环境 | 负责人 | 失败影响 |
| --- | --- | --- | --- | --- |
| LLM API | AI 叙事生成（Corvus 引擎走 thoushub 网关 + deepseek-v4-flash） | 生产 | Architect + AI Engineer | 核心体验不可用 |
| 向量数据库 | 角色记忆存储（PostgreSQL + pgvector, bge-small-zh 512 维） | 生产 | Architect | 跨会话记忆不可用 |
| Corvus-Story-Core | AI 自由叙事引擎（127.0.0.1:8082, systemd 守护） | 生产 | Admin / Ops | Corvus 引擎不可用，降级旧引擎 |
| 邮件服务 | 注册验证/密码重置 | 待确认 | 待确认 | 新用户注册流程阻塞 |
| 美术资源 | 立绘/背景/BGM | 待确认（PRE-03） | PL | 视觉体验降级 |

## 数据分级

| 数据类别 | 示例 | 敏感级别 | 存储位置 | 访问限制 |
| --- | --- | --- | --- | --- |
| 用户凭证 | 邮箱、密码哈希 | 高 | 待确认 | 仅后端服务访问 |
| 用户行为 | 对话记录、选择历史、好感度 | 中 | 待确认 | 用户本人 + 后端服务 |
| 角色记忆 | 向量嵌入、记忆文本 | 中 | 待确认 | 后端服务 + 向量数据库 |
| 剧本内容 | 节点、路线、预设对话 | 低 | 待确认 | 公开读取 |

## 维护规则

- 项目范围、模块职责、外部依赖或数据分级变化时必须更新本文。
- 具体 API 写入 `docs/api/api.md`，具体表结构写入 `docs/database/database.md`，不要在本文重复维护。
- 不确定内容标注为"待确认"，不得写成既定事实。
