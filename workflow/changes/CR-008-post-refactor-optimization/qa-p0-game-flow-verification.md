# P0 验收验证报告：剧本游戏核心流程

**验证时间**: 2026-07-24 21:00 UTC  
**验证环境**: Backend localhost:8000  
**测试用户**: qa-test-new@isekai.dev  
**测试剧本**: 星月奇缘 (66666666-6666-6666-6666-666666666666)

---

## 验证结果汇总

| 步骤 | 功能 | 状态 | 说明 |
|------|------|------|------|
| 1 | 登录 | ✅ PASS | JWT token 正常获取 |
| 2 | 开始游戏 | ✅ PASS | Session 创建成功，返回初始节点 |
| 3 | 获取对话 | ✅ PASS | 返回节点类型、文本、选择分支 |
| 4 | 提交选择 | ❌ **FAIL** | AttributeError: 'MetaData' object has no attribute 'get' |
| 5 | 获取新对话 | ⏸️ BLOCKED | 因步骤 4 失败无法执行 |
| 6 | 检查结局 | ⏸️ BLOCKED | 因步骤 4 失败无法执行 |
| 7 | 获取进度 | ⏸️ BLOCKED | 因步骤 4 失败无法执行 |

**通过: 3/7 | 失败: 1/7 | 阻塞: 3/7**

---

## 详细测试记录

### 步骤 1: 登录 ✅

```
POST /api/v1/auth/login
Request: {"email":"qa-test-new@isekai.dev","password":"***"}
Response: HTTP 200
{
  "access_token": "***",
  "refresh_token": "***",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 步骤 2: 开始游戏 ✅

```
POST /api/v1/game/start
Request: {"script_id":"66666666-6666-6666-6666-666666666666"}
Response: HTTP 200
{
  "session_id": "1f7e3a2b-4c5d-6e7f-8a9b-0c1d2e3f4a5b",
  "node_id": "99999999-9999-9999-9999-999999999991",
  "message": "Game started"
}
```

**验证点**:
- ✅ Session ID 返回
- ✅ 初始节点 ID 返回
- ✅ 节点类型为 preset（有对话内容）

### 步骤 3: 获取对话 ✅

```
GET /api/v1/game/{session_id}/dialogue
Response: HTTP 200
{
  "node_id": "99999999-9999-9999-9999-999999999991",
  "type": "preset",
  "text": "你也是来看月相的吗？今晚的月亮正好是上弦月...",
  "choices": [
    {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "text": "虽然不是爱好者，但我对星空很好奇！能给我讲讲月相吗？",
      "affection_delta": 3
    },
    {
      "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "text": "我只是路过，对天文学没什么兴趣。",
      "affection_delta": -2
    }
  ]
}
```

**验证点**:
- ✅ 节点类型正确（preset）
- ✅ 对话文本存在
- ✅ 选择分支存在（2 个选项）
- ✅ 每个选择包含 id、text、affection_delta

### 步骤 4: 提交选择 ❌ **P0 失败**

```
POST /api/v1/game/{session_id}/choice
Request: {"choice_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}
Response: HTTP 500 (timeout after 10s)
```

**错误日志**:
```
File "/app/app/api/v1/game.py", line 286, in submit_choice
AttributeError: 'MetaData' object has no attribute 'get'
```

**根因分析**:
- 错误位置: `backend/app/api/v1/game.py:286`
- 错误类型: `AttributeError`
- 错误描述: 尝试在 `MetaData` 对象上调用 `.get()` 方法，但该方法不存在
- 影响: 选择提交接口完全不可用，阻塞整个游戏流程

**可能原因**:
1. `MetaData` 对象类型错误（应该是 dict 但实际是 MetaData 实例）
2. 代码逻辑错误（应该用属性访问而非 `.get()`）
3. 数据结构变更未同步更新代码

### 步骤 5-7: 阻塞 ⏸️

由于步骤 4 失败，后续步骤无法执行：
- 获取新对话（选择后）
- 检查结局状态
- 获取游戏进度

---

## 问题汇总

### P0 缺陷

**缺陷 ID**: BUG-GAME-CHOICE-001  
**严重程度**: P0（核心流程阻塞）  
**影响范围**: 剧本游戏选择分支功能完全不可用  
**复现步骤**:
1. 登录并创建游戏会话
2. 获取当前对话节点（有选择分支）
3. 提交任意选择
4. 接口返回 500 错误

**错误信息**:
```
AttributeError: 'MetaData' object has no attribute 'get'
File: backend/app/api/v1/game.py:286
Function: submit_choice
```

**建议修复**:
1. 检查 `game.py:286` 行的代码逻辑
2. 确认 `MetaData` 对象的正确访问方式
3. 添加单元测试覆盖选择提交流程

---

## 结论

**P0 验收失败** ❌

剧本游戏核心流程在"提交选择"步骤完全阻塞，无法继续推进游戏。需要 BE 立即修复 `game.py:286` 的 AttributeError 问题。

**阻塞项**:
- ❌ 选择分支功能
- ❌ 结局触发
- ❌ 游戏进度追踪

**下一步**:
1. BE 修复 `submit_choice` 函数的 AttributeError
2. 重新执行 P0 验收测试
3. 验证完整游戏流程（选择 → 推进 → 结局）
