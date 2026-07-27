# CR-018 Review

## 通信台账

| 时间 | from | to | 目的 | 状态 | 说明 |
|------|------|-----|------|------|------|
| 2026-07-26T19:50:00+08:00 | qa | pl | P2 浏览器回归测试报告 | received | 6/10 通过，4/10 失败（测试框架问题） |

---

## P2 浏览器回归测试报告审查

**报告来源**: QA Agent (2026-07-26 19:50)
**报告位置**: `workflow/changes/CR-018/test-report-p2-regression.md`

### 测试结果

| 类别 | 数量 | 任务 |
|------|------|------|
| ✅ 通过 | 6 | T-016, T-017, T-019, T-020, T-025, T-024(前次报告) |
| ❌ 失败 | 4 | T-012, T-013, T-015, T-021 |

> **注**: 报告摘要说 6/10 通过，但详细列表中 T-024 也标记为 ❌ FAIL（5/10 失败）。根据前次 test-report.md，T-024 已通过浏览器测试。此处以详细列表为准，但 T-024 的实际状态需确认。

### 失败根因分析

**核心问题**: Playwright Token 持久化失败（测试框架问题，非功能缺陷）

所有失败项的共同原因：
1. `beforeEach` 中通过 `page.evaluate()` 设置的 token 在后续 `page.goto()` 时丢失
2. 前端路由守卫检测到未登录，重定向到 `/login` 页面
3. 导致 `.script-card`、`.char-card` 等选择器超时

**证据**: 错误日志中的页面快照显示登录页面（包含邮箱/密码输入框）

### PL 判定

| 项目 | 判定 | 理由 |
|------|------|------|
| 功能缺陷 | ❌ 否 | 失败原因是测试框架 token 注入方式不当，非代码逻辑错误 |
| 阻塞发布 | ❌ 否 | QA 建议 P2 不阻塞发布 |
| 需要修复 | ✅ 是 | 测试框架需要修复以提供有效回归证据 |
| 需要重测 | ✅ 是 | 修复后需重新验证 T-012/T-013/T-015/T-021 |

### 修复方案（QA 建议）

使用 `page.addInitScript()` 替代 `page.evaluate()`：

```typescript
await page.addInitScript((token) => {
  localStorage.setItem('isekai_access_token', token);
}, testToken);
```

### RELEASE_GATE 影响

**当前状态**: 不阻塞，但 RELEASE_GATE 需要完整 Browser Interaction E2E 结果

- RELEASE_GATE 要求 Browser Interaction E2E Results 且 `Mock API=no`
- 当前 4 项失败是测试框架问题，不是功能问题
- 修复测试框架后可重新生成有效证据
- **建议**: 先修复测试框架，重跑失败项，再进入 RELEASE_GATE

### 下一步

1. 通知 FE 修复 Playwright 测试框架的 token 持久化问题
2. 修复后重新运行 T-012/T-013/T-015/T-021
3. 确认全部通过后进入 RELEASE_GATE
