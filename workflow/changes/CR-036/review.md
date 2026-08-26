# CR-036 Review

## 开发覆盖声明

### T-036-BE-001: 自由对话角色过滤 (P1)

**修改文件**: `backend/app/api/v1/game.py`
**修改内容**: `get_free_chat_history` 使用 `game_session.character_id` 而非固定 `is_main`

**修改前**:
```python
char_stmt = select(Character).where(
    Character.script_id == game_session.script_id,
    Character.is_main == True
).limit(1)
```

**修改后**:
```python
character_id = str(game_session.character_id) if game_session.character_id else None
if not character_id:
    # fallback: 获取该剧本的主角色
    ...
```

**状态**: ✅ done

---

### T-036-BE-002: 剧本游戏 AI 对话基于框架 (P1)

**方案**: 新增异步 AI 生成接口，preset 节点先返回预设文本，前端异步调用补充

**修改文件**: `backend/app/api/v1/game.py`

**新增接口**: `GET /game/{session_id}/ai-dialogue`
- 获取当前节点，仅对 preset/fixed_scene 节点生成
- 调用 `_generate_validated_dialogue`（PromptBuilder 6层 prompt）
- 30 秒超时
- 失败返回空文本（前端忽略）

**保持不变**: `_handle_preset_node` 不调用 AI（CR-035 修复保留）

**状态**: ✅ done

---

## 开发覆盖声明: FE 修复

### 任务信息

| 字段 | 值 |
|------|-----|
| 任务编号 | T-036-FE-001 |
| 任务名称 | FE: 社区帖子详情头像显示 |
| 负责人 | fe (isekai-wanderer-fe) |
| 关联 AC | AC-036-001 |
| 实际工时 | 0.2h |
| 完成时间 | 2026-08-05T17:05:00+08:00 |

### 已实现 AC

| AC | 描述 | 实现状态 | 测试状态 | 证据 |
|----|------|----------|----------|------|
| AC-036-001 | 社区帖子详情显示头像 | ✅ 已修复 | ✅ 构建通过 | `CommunityView.vue` 添加 img + fallback |

### 已测试 AC

| 测试项 | 结果 |
|--------|------|
| `npm run build` | ✅ PASSED (exit code 0) |
| TypeScript 类型检查 | ✅ PASSED |

### 未实现 AC

无

### 未测试 AC

| AC | 原因 |
|----|------|
| AC-036-001 | 需要真实浏览器环境验证 |

### 已运行命令

| 命令 | 结果 |
|------|------|
| `npm run build` | ✅ PASSED |

### 失败命令

无

### 需要人工验收

- 有头像的作者显示头像图片
- 无头像的作者显示名称首字母
- 头像加载失败时 fallback 到首字母

### 已知风险

无

---

## 代码变更清单 (FE)

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `frontend/src/views/CommunityView.vue` | Modified | 帖子详情头像显示 img + fallback 到首字母 |

---

## 变更详情 (FE)

### `frontend/src/views/CommunityView.vue`

**模板修改**:
```html
<!-- 修改前 -->
<div class="detail-avatar">{{ selectedPost.author.name.charAt(0) }}</div>

<!-- 修改后 -->
<div class="detail-avatar">
  <img v-if="selectedPost.author?.avatar && !avatarFailed" 
       :src="selectedPost.author.avatar" 
       :alt="selectedPost.author.name" 
       class="detail-avatar-img" 
       @error="avatarFailed = true" />
  <span v-else>{{ selectedPost.author.name.charAt(0) }}</span>
</div>
```

**脚本修改**:
```typescript
const avatarFailed = ref(false);
```

**样式修改**:
```css
.detail-avatar {
  /* ... 原有样式 ... */
  overflow: hidden;  /* 新增 */
}
.detail-avatar-img {  /* 新增 */
  width: 100%; height: 100%; object-fit: cover; border-radius: 50%;
}
```
