# CR-018 UUID v4 迁移 + 游戏流程验证报告

**测试时间**: 2026-07-27 09:38 - 09:42  
**测试环境**: Docker Compose (backend + frontend + postgres + redis)  
**后端版本**: 1.0.0  
**测试账号**: qa-game-test@isekai.dev  
**Mock API**: no  

---

## 测试结果汇总

| 类别 | 测试项 | 状态 | 说明 |
|------|--------|------|------|
| P0 | 游戏开始（3 个 script） | ✅ PASS | 全部返回 200 OK |
| P0 | UUID v4 迁移 - scripts | ✅ PASS | 3/3 已迁移为随机 UUID v4 |
| P0 | UUID v4 迁移 - routes | ✅ PASS | 12/12 已迁移为随机 UUID v4 |
| P0 | UUID v4 迁移 - characters | ❌ **FAIL** | 1/3 仍为硬编码旧 UUID |
| P1 | Route nodes 完整性 | ✅ PASS | 6 有 nodes + 6 无 nodes（符合预期） |
| P1 | 游戏 session 创建 | ✅ PASS | session 正常创建 |
| P1 | Session status 返回 | ⚠️ WARN | character_id 暴露硬编码 UUID |
| P2 | 选择对话 API | ⚠️ BLOCKED | 参数格式变更（需 choice_id 而非 choice_index） |
| P2 | 对话 API | ⚠️ BLOCKED | 参数格式变更（需 role+content 而非 message） |

---

## 详细测试结果

### 1. 游戏开始验证 ✅

| 剧本 | Script ID | HTTP | 结果 |
|------|-----------|------|------|
| 星辰之约 | e56ca348-cc08-45f2-a6fa-baa4c725d192 | 200 | ✅ session 创建成功 |
| 星月奇缘 | de1c935a-3e82-4e29-aff9-c69c3a460418 | 200 | ✅ session 创建成功 |
| 樱花恋曲 | 93bbc975-04f8-452d-ab27-d8f5348eb29d | 200 | ✅ session 创建成功 |

### 2. UUID v4 迁移验证

#### Scripts ✅
| 剧本 | UUID | 状态 |
|------|------|------|
| 星辰之约 | e56ca348-cc08-45f2-a6fa-baa4c725d192 | ✅ 随机 UUID v4 |
| 星月奇缘 | de1c935a-3e82-4e29-aff9-c69c3a460418 | ✅ 随机 UUID v4 |
| 樱花恋曲 | 93bbc975-04f8-452d-ab27-d8f5348eb29d | ✅ 随机 UUID v4 |

#### Routes ✅
全部 12 个 route 已迁移为随机 UUID v4，无硬编码残留。

#### Characters ❌
| 角色 | UUID | 状态 |
|------|------|------|
| 藤原雪 | 6982c07f-bb69-4abe-9919-f54ea94297a4 | ✅ 随机 UUID v4 |
| 沈星澜 | 900a9744-04ca-4c6b-a276-c79595218672 | ✅ 随机 UUID v4 |
| **林辰** | **22222222-2222-2222-2222-222222222222** | **❌ 硬编码旧 UUID** |

**根因**: T-008 UUID v4 迁移脚本未将 `林辰` 的 ID 从 `22222222-2222-2222-2222-222222222222` 更新为随机 UUID。

**影响**: 
- Session status API 返回 `character_id: "22222222-2222-2222-2222-222222222222"`，暴露硬编码 UUID
- 前端如果依赖 UUID 格式校验可能会拒绝此 ID
- 与迁移目标（全部随机 UUID v4）不一致

### 3. Route Nodes 完整性 ✅

| 剧本 | Route | Nodes 数量 | 状态 |
|------|-------|-----------|------|
| 星辰之约 | 星夜邂逅 | 8 | ✅ |
| 星辰之约 | 林辰线：星光指引 | 9 | ✅ |
| 星辰之约 | 流星线：刹那永恒 | 7 | ✅ |
| 星辰之约 | 银河线：命运交汇 | 8 | ✅ |
| 星月奇缘 | 月夜邂逅 | 11 | ✅ |
| 星月奇缘 | 双星线：命运交织 | 0 | ⚠️ fallback |
| 星月奇缘 | 辉夜线：月影传说 | 0 | ⚠️ fallback |
| 星月奇缘 | 星澜线：星辰之约 | 0 | ⚠️ fallback |
| 樱花恋曲 | 樱花树下 | 6 | ✅ |
| 樱花恋曲 | 月夜线：静谧之恋 | 0 | ⚠️ fallback |
| 樱花恋曲 | 阳菜线：夏日恋歌 | 0 | ⚠️ fallback |
| 樱花恋曲 | 雪乃线：樱花树下的约定 | 0 | ⚠️ fallback |

**统计**: 6 routes 有 nodes (共 49 个), 6 routes 无 nodes（符合 BE 预期：这 6 个 route 从未有 nodes）

### 4. 游戏流程验证

| 测试项 | HTTP | 状态 | 说明 |
|--------|------|------|------|
| POST /game/start | 200 | ✅ | session 正常创建 |
| GET /game/{session}/status | 200 | ✅ | 返回角色、好感度等信息 |
| GET /game/{script}/route-map | 200 | ✅ | 返回完整路线图 |
| POST /game/{session}/choice | 422 | ⚠️ | 需要 choice_id（非 choice_index） |
| POST /game/{session}/dialogue | 422 | ⚠️ | 需要 role+content（非 message） |

**注**: choice 和 dialogue API 参数格式与测试脚本预期不同，非功能缺陷，是 API 设计变更。

---

## 缺陷清单

### BUG-1: 角色「林辰」UUID 未迁移 (P0)

- **严重程度**: P0
- **描述**: characters 表中 `林辰` 的 ID 仍为硬编码 `22222222-2222-2222-2222-222222222222`
- **复现**: `SELECT id, name FROM characters WHERE id = '22222222-2222-2222-2222-222222222222';`
- **影响**: T-008 迁移不完整，session status 暴露硬编码 UUID
- **责任归属**: BE
- **修复建议**: 执行 UUID 迁移更新 `林辰` 的 ID 为随机 UUID v4，并更新所有引用此 ID 的外键

---

## 结论

| 项目 | 结论 |
|------|------|
| 游戏开始 | ✅ P0 通过 |
| UUID v4 迁移 - scripts/routes | ✅ 通过 |
| UUID v4 迁移 - characters | ❌ 未通过（1/3 硬编码残留） |
| Route nodes 完整性 | ✅ 通过 |
| 游戏核心流程 | ⚠️ 部分验证（API 参数格式需更新测试脚本） |

**整体判定**: ⚠️ 有条件通过
- 游戏可以正常开始（P0 不阻塞）
- T-008 UUID v4 迁移存在遗漏（character 林辰），需 BE 修复
- 前端交互需 Browser E2E 进一步验证
