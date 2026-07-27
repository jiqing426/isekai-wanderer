# Communication Ledger

跨角色通信必须以 `sessions_send` 作为可靠消息底座，本文简称 MSG。每次发送必须调用 `sessions_send(agentId="...", message="...", timeoutSeconds=...)`，等待 ack 或超时；在 MSG 必达可审计的前提下，尽可能同步到飞书群聊，保证人类可见和群内协同。任何失败都要记录，不能只写一句 `@role` 就视为通知成功。

| Message ID | From | To | Purpose | MSG Channel | MSG Status | Feishu Channel | Feishu Status | Ack Status | Attempts | Created At | Last Error | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 状态说明

- `queued`：待发送。
- `sent_msg`：已通过 `sessions_send(agentId="...", message="...", timeoutSeconds=...)` 发送，等待 ack 或超时。
- `acked_msg`：MSG 已确认，满足可靠投递底线。
- `msg_failed`：MSG 发送失败、超时或未 ack；当前阶段必需角色应阻塞。
- `sent_feishu`：已同步到飞书群聊，等待 ack 或可见性确认。
- `acked_feishu`：飞书群聊已确认。
- `feishu_failed`：飞书发送失败、超时或未 ack；必须记录，但不能替代 MSG 结果。
- `failed_all`：MSG 和飞书都失败。
- `deferred_non_blocking`：非当前阶段必需角色，可暂缓。
- `blocked`：当前阶段必需角色不可达，阻塞流程。
