# CR-018 发布计划

> 创建时间：2026-07-26 20:01
> 发布状态：✅ 已发布

---

## 发布信息

| 项 | 值 |
|---|---|
| 变更编号 | CR-018 |
| 变更名称 | 用户复测问题修复 |
| 发布时间 | 2026-07-26 20:01 GMT+8 |
| 发布方式 | Docker Compose 热更新（已在运行） |
| 发布确认 | PL 确认 P0/P1 全部通过 |

---

## 发布范围

### P0 任务（3/3 ✅）

| 任务 | 功能 | 修复文件 |
|------|------|----------|
| T-001 | 送礼接口 400 修复 | `backend/app/api/v1/gift.py` |
| T-002 | 自由对话 401 修复 | `frontend/src/api/chat.ts` |
| T-003 | 头像上传失败修复 | `frontend/src/api/user.ts` + `backend/app/api/v1/users.py` |

### P1 任务（8/8 ✅）

| 任务 | 功能 | 修复文件 |
|------|------|----------|
| T-004 | 好感度实时更新 | `backend/app/services/narrative/narrative_engine.py` |
| T-005 | 自由对话历史持久化 | `backend/app/services/narrative/free_chat_service.py` |
| T-006 | 剧本流程过短修复 | `backend/app/services/narrative/narrative_engine.py` |
| T-007 | 剧本进度记录修复 | `backend/app/services/narrative/script_service.py` |
| T-008 | UUID v4 数据迁移 | `backend/scripts/migrate_uuid_v4.sql` |
| T-009 | 完成剧本统计修正 | `backend/app/api/v1/users.py` |
| T-010 | 累计获得碎片修复 | `backend/app/api/v1/sign.py` |
| T-011 | 对话额度重置确认 | `backend/app/services/quota_service.py` |

### 二次复测修复（5/5 ✅）

| 任务 | 功能 | 修复文件 |
|------|------|----------|
| T-026 | 收支明细中文化 | `frontend/src/i18n/zh-CN.ts` + `backend/app/api/v1/fragment.py` |
| T-027 | 成就奖励跳转 | `frontend/src/views/FragmentMallView.vue` |
| T-028 | 帖子浏览量统计 | `backend/app/api/v1/community.py` |
| T-029 | 头像上传修复（P0 升级）| `frontend/src/api/user.ts` |
| T-030 | 会员账单中文映射 | `backend/app/api/v1/settings.py` + `frontend/src/views/SettingsView.vue` |

---

## 发布前检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| P0 任务全部通过 | ✅ | 3/3 QA 验证通过 |
| P1 任务全部通过 | ✅ | 8/8 QA 验证通过 |
| 二次复测任务通过 | ✅ | 5/5 QA 验证通过 |
| 后端健康检查 | ✅ | `curl http://localhost:8000/health` → 200 |
| 前端健康检查 | ✅ | Docker healthy |
| 数据库连接 | ✅ | PostgreSQL healthy |
| Redis 连接 | ✅ | Redis healthy |
| Docker Compose 全部运行 | ✅ | 4/4 containers healthy |

---

## 发布步骤

1. ✅ 确认所有服务运行正常（`docker compose ps`）
2. ✅ 确认后端健康检查通过（`/api/v1/health`）
3. ✅ 确认前端构建通过
4. ✅ 确认数据库迁移完成（UUID v4）
5. ✅ PL 确认 P0/P1 全部通过
6. ✅ 标记发布完成

---

## 回滚方案

如需回滚：
1. 从备份恢复数据库：`psql < /tmp/backup_before_uuid_migration.sql`
2. 回退代码到 CR-018 之前版本
3. `docker compose down && docker compose up -d`

---

## 发布后监控

- 后端日志：`docker compose logs -f backend`
- 前端日志：`docker compose logs -f frontend`
- 健康检查：`curl http://localhost:8000/health`
- 用户反馈：关注飞书群消息

---

## P2 待发布项（不阻塞本次发布）

| 任务 | 功能 | 状态 |
|------|------|------|
| T-012 | AI 叙事 loading 状态 | FE 已实现，QA 回归中 |
| T-013 | 性格 loyal 映射中文 | FE 已实现，QA 回归中 |
| T-015 | 语音试听功能 | FE 已实现，QA 回归中 |
| T-016 | 成就卡片 JSON 展示 | FE 已实现，QA 回归中 |
| T-017 | 碎片商城 Tab 样式 | FE 已实现，QA 回归中 |
| T-019 | 个人中心对话次数展示 | FE 已实现，QA 回归中 |
| T-020 | AI 记忆 Invalid Date | FE 已实现，QA 回归中 |
| T-021 | 角色羁绊英文翻译 | FE 已实现，QA 回归中 |
| T-024 | 剧本详情封面图优化 | FE 已实现，QA 回归中 |
| T-025 | 前端中文 i18n 补全 | FE 已实现，QA 回归中 |

P2 任务 QA 回归通过后将追加发布。
