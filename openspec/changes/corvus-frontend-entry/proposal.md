# OpenSpec Change: corvus-frontend-entry

## Motivation

CR-037 完成了 Corvus-Story-Core 后端集成，但前端入口未接入。前端 `startGame()` 只调用 legacy `POST /game/start`，`engine_type` 永远为 `undefined`，Corvus SSE 分支代码成为 dead code。用户实际仍玩 legacy 内置游戏。

## Scope

### In Scope

- 前端 `game.ts` startGame 改造：支持 Corvus 会话创建流程
- 前端 Corvus 会话创建：调用 `POST /game/session/create` + `POST /game/session/select-player`
- 前端 SSE 流式分支激活：`submitChoice` / `submitCustomInput` 的 Corvus 分支可用
- 前端角色候选管理 UI：查看/创建/选择 player_candidates
- 前端剧本选择区分 legacy/corvus
- 后端 `GET /scripts` 补充 `engine_type` 字段（如需要）
- localStorage 会话恢复区分 legacy/corvus

### Out of Scope

- 后端 Corvus 核心逻辑（CR-037 已完成）
- Corvus-Story-Core 服务本身部署和配置
- 新剧本内容制作

## Success Criteria

1. 用户可以在前端选择 Corvus 剧本并开始游戏
2. 游戏过程中对话通过 SSE 流式渲染
3. 用户可以自由输入文字推进剧情
4. `engine_type` 正确设置为 `'corvus'` 并持久化
5. Legacy 剧本不受影响
6. Browser E2E 可验证 Corvus 全链路
