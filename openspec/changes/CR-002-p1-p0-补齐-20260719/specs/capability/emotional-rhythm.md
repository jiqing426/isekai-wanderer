# S-CR2-003 情绪节奏（CR-002 补充）

**MAS（最小可用标准）**：情绪标签驱动打字速度+BGM 音量联动。

## REQ-CR2-003: 情绪节奏

### Requirement: 情绪标签驱动交互

**ID**: REQ-CR2-003-R01
**优先级**: P1

剧本关键节点有情绪标签时，对话打字速度跟随调整，BGM 音量跟随调整。

#### Scenario: 紧张情绪加速打字

- **Given** 当前对话节点情绪标签为 tense
- **When** AI 输出对话文本
- **Then** 打字速度提升至 2x，BGM 音量提升至 1.2x

#### Scenario: 温馨情绪减速打字

- **Given** 当前对话节点情绪标签为 warm
- **When** AI 输出对话文本
- **Then** 打字速度降低至 0.7x，BGM 音量降低至 0.8x

### R/C/U/D 完整性

| 动作 | 是否包含 | 说明 |
| --- | --- | --- |
| Create | 否 | — |
| Read | 是 | 读取情绪标签 |
| Update | 是 | 动态调整速度和音量 |
| Delete | 否 | — |

### 下游约束

- 依赖：SSE 流式对话（已存在）、AudioPlayer（已存在）
- FE：TypewriterSpeed + BGMVolume 联动
