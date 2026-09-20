#!/usr/bin/env python3
"""Bootstrap an OpenClaw project workflow from a raw PRD.

This tool is intentionally conservative: it prepares workflow structure,
records the PRD as the current change input, and generates role AGENTS.md files.
It does not approve gates, write business implementation, deploy, or touch
production data.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROLE_NAMES = (
    "pl",
    "ceo",
    "pm",
    "architect",
    "backend",
    "frontend",
    "admin",
    "ai-engineer",
    "qa",
    "security",
    "ops",
    "hr",
)

DIRECTORY_SKELETON = (
    "workflow",
    "workflow/changes",
    "openspec/changes",
    "tools",
    "skills",
    "docs/prd",
    "docs/status",
    "docs/testing",
    "docs/security",
    "docs/toolchain",
    "docs/runtime",
)


def read_text(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def now_text():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text, flags=re.UNICODE)
    text = text.strip("-")
    return text[:48] or "prd-change"


def is_placeholder_change(change_dir):
    change_file = change_dir / "change.md"
    if not change_file.exists():
        return False
    text = read_text(change_file)
    return (
        "| 当前状态 | draft |" in text
        and "- 目标：" in text
        and "## 原始 PRD" not in text
        and "## 自动入口记录" not in text
    )


def next_change_id(changes_dir):
    placeholder = changes_dir / "CR-001"
    if is_placeholder_change(placeholder):
        return "CR-001"
    max_number = 0
    if changes_dir.exists():
        for path in changes_dir.iterdir():
            match = re.match(r"CR-(\d+)$", path.name)
            if match:
                max_number = max(max_number, int(match.group(1)))
    return "CR-%03d" % (max_number + 1)


def title_from_prd(prd_text):
    for line in prd_text.splitlines():
        line = line.strip().lstrip("#").strip()
        if line:
            return line[:80]
    return "PRD 需求"


def ensure_skeleton(project_root):
    for relative in DIRECTORY_SKELETON:
        (project_root / relative).mkdir(parents=True, exist_ok=True)


def copy_file_if_exists(source, destination):
    if source.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(destination))
        return True
    return False


def generate_agents(project_root):
    skills_dir = project_root / "skills"
    ensured = []
    if not skills_dir.is_dir():
        return ensured
    for role_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        agents_file = role_dir / "AGENTS.md"
        if agents_file.exists():
            ensured.append(str(agents_file.relative_to(project_root)))
            continue
        role_file = role_dir / "ROLE.md"
        if not role_file.exists():
            continue
        write_text(agents_file, read_text(role_file).rstrip() + "\n")
        ensured.append(str(agents_file.relative_to(project_root)))
    return ensured


def render_change(change_id, title, change_name, prd_text, created_at):
    return """# Change

## 变更单

| 项 | 内容 |
| --- | --- |
| CR 编号 | {change_id} |
| 来源 | 用户 PRD |
| 类型 | feature |
| 优先级 | P1 |
| 当前状态 | intake-ready |
| 负责人 | pl |
| 关联 PRD | `docs/prd/prd.md` |
| 关联 OpenSpec Change | `../../../openspec/changes/{change_name}/` |

## 问题和目标

- 现状：来自用户 PRD，待 PM 在 REQUIREMENT 阶段结构化。
- 目标：{title}
- 成功标准：PRD 中 P0/P1 验收项被拆成可测试 acceptance，并通过后续设计、开发、QA 与发布关口。
- 本次不做：PRD 未明确授权的生产部署、真实支付、真实 AI/付费资源调用、不可逆数据操作。

## 原始 PRD

```markdown
{prd_text}
```

## OpenSpec Change 生成

- PM 根据本文件创建或更新对应 OpenSpec change：`proposal.md`、`specs/**/spec.md`；同时维护 `docs/prd/prd.md` 摘要和 `acceptance.md`。
- 未确认内容必须以 Q 编号登记；非阻塞问题可以记录为暂缓，不得伪装为已确认事实。
- OpenSpec change 或 workflow 追踪文件不完整时，不能直接让关口 `passed`。

## 影响范围

| 领域 | 是否影响 | 说明 |
| --- | --- | --- |
| PROJECT / 项目事实 | 待确认 | PM/PL 从 PRD 识别 |
| PRD / 需求输入 | 是 | 本 CR 来自用户 PRD |
| 架构 / 模块边界 | 待确认 | Architect 在 DESIGN 阶段判断 |
| API / 契约 | 待确认 | Architect/BE 在 DESIGN 阶段判断 |
| 数据库 / 迁移 | 待确认 | 发现不可逆迁移时必须人工确认 |
| 权限 / 安全 / 隐私 | 待确认 | Security 在后续阶段审查 |
| 前端 / 管理端体验 | 待确认 | FE/Admin 按任务单执行 |
| 测试 / 验收 | 是 | QA/PM 生成 acceptance 和 test-plan |
| 部署 / 生产 / 回滚 | 待确认 | Ops 在发布阶段处理 |

## 人工确认

以下任一项为 `是` 时，不能由 LLM 自动通过，只能由人工确认后继续。

| 项 | 是 / 否 | 说明 |
| --- | --- | --- |
| 生产环境变更 | 待确认 | PRD 自动入口默认不授权 |
| 数据删除或不可逆迁移 | 待确认 | PRD 自动入口默认不授权 |
| 认证、授权或权限边界变更 | 待确认 | 需安全评审，必要时人工确认 |
| 支付、账务或合规承诺 | 待确认 | PRD 自动入口默认不授权 |
| 公共 API 破坏性变更 | 待确认 | 需人工确认兼容策略 |
| 大范围跨模块重构 | 待确认 | 需 PL/Architect 判断 |

## 自动入口记录

- 创建时间：{created_at}
- 执行方式：`tools/bootstrap-openclaw-prd.py`
- 初始授权：仅授权创建 CR、记录 PRD、生成初始 workflow / OpenSpec 骨架；不授权自动通过阶段、关口或部署。
- 放行要求：每个推进型流转仍必须由 PL 展示交付物清单、关键结论、缺口和风险，并取得用户明确同意后，才能运行 readiness 并推进。
""".format(
        change_id=change_id,
        title=title,
        change_name=change_name,
        prd_text=prd_text.strip(),
        created_at=created_at,
    )


def render_prd_doc(change_id, title, prd_text, created_at):
    return """# PRD

## 当前输入

| 项 | 内容 |
| --- | --- |
| 来源 | 用户 PRD |
| 关联 CR | {change_id} |
| 标题 | {title} |
| 记录时间 | {created_at} |

## 原始 PRD

```markdown
{prd_text}
```

## 结构化摘要

待 PM 在 REQUIREMENT 阶段拆解目标、范围、非目标、P0/P1 验收标准和 Q 编号待澄清问题。
""".format(change_id=change_id, title=title, prd_text=prd_text.strip(), created_at=created_at)


def render_state(change_id, title, change_name, created_at):
    return """# Workflow State

- 需求名称：{title}
- 当前阶段：INTAKE
- 当前状态：intake-ready
- 当前负责人：pl
- 当前关口：无
- 当前变更：workflow/changes/{change_id}
- 当前 OpenSpec Change：openspec/changes/{change_name}
- 当前任务：无
- 执行模式：prd-autopilot
- 最近更新时间：{created_at}
- 当前结论：PRD 已进入自动入口
- 阻塞问题：无
- 下一步动作：PL 展示 INTAKE 交付物、关键结论、缺口和风险，取得用户明确同意后，运行阶段流转检查并进入 INIT 阶段
- 退回对象：无
- 退回原因：无

## 当前交付物

| 所属阶段 | 交付物 | 状态 | 负责人 | 说明 |
| --- | --- | --- | --- | --- |
| INTAKE | `workflow/changes/{change_id}/change.md` | ready | pl | PRD 自动入口已生成 |
| INIT | `workflow/changes/{change_id}/review.md` | pending | ceo | 立项结论 |
| TRIAGE | `workflow/changes/{change_id}/review.md` | pending | pl | 分流调度、风险识别和主责确认 |
| REQUIREMENT | `docs/prd/prd.md` | ready | pm | 原始 PRD 已记录，待结构化 |
| REQUIREMENT | `openspec/changes/{change_name}/proposal.md` | pending | pm | OpenSpec 变更动机、范围和成功标准 |
| REQUIREMENT | `openspec/changes/{change_name}/specs/**/spec.md` | pending | pm | OpenSpec Requirement / Scenario 规格差异 |
| REQUIREMENT | `workflow/changes/{change_id}/acceptance.md` | pending | pm / qa | 验收追踪 |
| DESIGN | `openspec/changes/{change_name}/design.md` | pending | architect | OpenSpec 技术设计 |
| DESIGN | `openspec/changes/{change_name}/tasks.md` | pending | architect / pl | OpenSpec 开发任务单 |
| DESIGN | `workflow/changes/{change_id}/test-plan.md` | pending | qa / 实现 Agent | 测试先行计划 |
| QA | `workflow/changes/{change_id}/test-report.md` | pending | qa | 测试结论 |
| SECURITY | `workflow/changes/{change_id}/security-review.md` | pending | security | 安全结论 |
| RELEASE_GATE | `workflow/changes/{change_id}/deploy-plan.md` | pending | ops | 发布步骤、回滚方案和监控方案 |
| DEPLOY | `workflow/changes/{change_id}/deploy-record.md` | pending | ops | 实际部署执行记录 |

## 流转日志

| 时间 | 从 | 到 | 动作 | 负责人 | 结论 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| {created_at} | - | INTAKE | prd_bootstrap | pl | intake-ready | 用户 PRD 自动进入流程 |

## Agent 执行日志

| 时间 | Agent | 阶段 | 任务 | 结果 | 日志文件 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| {created_at} | pl | INTAKE | PRD 自动入口 | ready | `workflow/changes/{change_id}/logs/agent-runs/` | 已创建 CR 与初始状态 |
""".format(change_id=change_id, title=title, change_name=change_name, created_at=created_at)


def ensure_review(project_root, change_id, change_name, created_at):
    review_path = project_root / "workflow" / "changes" / change_id / "review.md"
    if review_path.exists():
        text = read_text(review_path)
        placeholder_review = (
            "| 当前状态 | draft |" in text
            and "| INTAKE | pl | 原始目标 | `change.md` | draft |" in text
            and "用户明确同意推进" not in text
        )
        if not placeholder_review:
            return
    write_text(
        review_path,
        """# Review

本文记录当前 CR 的阶段结论、风险、联调、发布和归档状态。

## 当前状态

| 项 | 内容 |
| --- | --- |
| CR 编号 | {change_id} |
| 当前阶段 | INTAKE |
| 当前状态 | intake-ready |
| 当前负责人 | pl |
| 下一步 | 触发 INIT、TRIAGE、REQUIREMENT |

## 关口审批

| 关口 | 主责 | 评审人 | Readiness 命令 | 结论 | 下一阶段 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| INIT | ceo | pl | manual | draft | TRIAGE | 待 INIT 立项判断 |
| REQ_GATE | pl | pl | `python tools/check-gate-readiness.py --gate requirement --change {change_name} --change-id {change_id}` | draft | DESIGN | 待 PL 审查 PM 交付 |
| DESIGN_GATE | pl | architect | `python tools/check-gate-readiness.py --gate design --change {change_name} --change-id {change_id}` | draft | DEVELOPMENT | 待 Architect 交付 |
| RELEASE_GATE | pl | qa / security / ops | `python tools/check-gate-readiness.py --gate release --change {change_name} --change-id {change_id}` | draft | DEPLOY | 待 QA/Security/Ops 交付 |

## 阶段结论

| 阶段 | 负责人 | 输入 | 输出 | 结论 |
| --- | --- | --- | --- | --- |
| INTAKE | pl | 用户 PRD | `change.md` | ready |
| INIT | ceo | `change.md` | 立项结论 | pending |
| TRIAGE | pl | 立项结论 | 分流调度、风险和主责确认 | pending |
| REQUIREMENT | pm | 立项结论 | OpenSpec `proposal.md`、`specs/**/spec.md`、`acceptance.md` | pending |
| DESIGN | architect | 需求关口结论 | OpenSpec `design.md`、`tasks.md`、`test-plan.md` | pending |
| DEVELOPMENT | pl | 设计关口结论 | OpenSpec task、代码变更和 Agent Run Log | pending |
| INTEGRATION | pl | 开发记录 | 联调结论 | pending |
| QA | qa | `test-plan.md` | `test-report.md` | pending |
| SECURITY | security | 测试报告 | `security-review.md` | pending |
| RELEASE_GATE | pl | 测试、安全和发布计划 | `review.md`、`deploy-plan.md` | pending |
| DEPLOY | ops | 发布关口结论 | `deploy-record.md` | pending |

## 阶段暂停确认

| 阶段 | 动作 | 下一阶段 | 交付物 | 展示摘要 | 用户确认 | 记录时间 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| INTAKE | accept | INIT | `change.md`, `docs/prd/prd.md` | 待 PL 向用户展示 PRD 记录、范围、缺口和风险 | 待确认 | {created_at} | PRD 自动入口不替代用户明确同意推进 |

## Development Task Handoffs

| Completed Task | Completion Status | Pause Report | User Continue | Next Task | Recorded At | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## 开发覆盖声明

| 任务编号 | 已实现 AC | 已测试 AC | 未实现 AC | 未测试 AC | 已运行命令 | 失败命令 | 需要人工验收 | 已知风险 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 |

## Contract Gaps Discovered During Development

开发、联调或 QA 阶段发现上游需求、设计、API、runtime、数据、权限或测试计划漏项时，必须先登记本表。缺口未关闭时不得推进发布关口；影响设计产物时必须退回并重新运行 DESIGN_GATE readiness。

| Gap ID | Discovered Stage | Symptom | Missing Upstream Contract | Earliest Broken Stage | Return To | Required Backfill | Verification Required | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GAP-001 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | Pending |

## QA 覆盖复核

| 验收编号 | 开发声明 | QA 复核 | 结论 | 退回对象 |
| --- | --- | --- | --- | --- |
| AC-001 | 待填写 | 待填写 | Pending | 待填写 |

## 人工验收范围

- 已覆盖：待填写。
- 明确未覆盖：待填写。
- 已批准暂缓：待填写。
- 不属于本 CR：待填写。
- 需要人工只验证：待填写。

## 联调记录

| 场景 | 关联验收项 | 参与模块 | 依赖任务 | 验证方式 | 结果 | 问题 |
| --- | --- | --- | --- | --- | --- | --- |

## 风险

| 编号 | 风险 | 等级 | 负责人 | 状态 | 缓解措施 |
| --- | --- | --- | --- | --- | --- |
| R-001 | PRD 中可能存在未确认范围或高风险操作 | Medium | pl | Open | PM 以 Q 编号登记，PL 在关口阻塞 |

## 反馈和归档

- 本轮完成内容：待填写
- 未完成内容：待填写
- 新需求入口：待填写
- 长期事实已同步：否
- 是否归档：否
""".format(change_id=change_id, change_name=change_name, created_at=created_at),
    )


def ensure_placeholder(path, title):
    if path.exists():
        return
    write_text(path, "# {0}\n\n待对应角色在流程阶段补齐。\n".format(title))


def ensure_runtime_contract(path):
    if path.exists():
        return
    write_text(
        path,
        """# Runtime Contract

本文记录交付拓扑契约。DESIGN 阶段必须填写，Frontend、Backend、QA、Ops 只能按本文件约定配置端口、API base、代理、健康检查、浏览器交互 E2E 和交付级 E2E。Delivery E2E / Release 证据禁止使用 mock API。

| Key | Value | Owner | Evidence / Source | Status |
| --- | --- | --- | --- | --- |
| frontend_origin | 待填写 | architect / frontend | `.env.example`, `vite.config.*`, `docker-compose.yml` | Pending |
| backend_origin | 待填写 | architect / backend | `.env.example`, backend listen config, `docker-compose.yml` | Pending |
| public_frontend_origin | 待填写 | architect / frontend / ops | 公网 IP、域名或外网入口；无公网时写 `Not Required: <原因>` | Pending |
| public_backend_origin | 待填写 | architect / backend / ops | 公网 API 入口、域名或外网访问地址；无公网时写 `Not Required: <原因>` | Pending |
| frontend_port | 待填写 | frontend / ops | `vite.config.*`, `docker-compose.yml` | Pending |
| backend_port | 待填写 | backend / ops | backend listen config, `docker-compose.yml` | Pending |
| exposed_ports | 待填写 | ops / backend / frontend | 容器、服务器、防火墙或代理暴露的端口清单 | Pending |
| api_base_path | `/api/v1` | architect / backend / frontend | `docs/api/api.md` | Pending |
| frontend_to_backend_url | 待填写 | frontend / backend | browser request path through frontend origin, e.g. `<frontend_origin>/api/v1/health` | Pending |
| vite_proxy_target | 待填写 | frontend | `vite.config.*` proxy target, or `Not Required` with reason | Pending |
| proxy_mode | 待填写 | architect / frontend / ops | 直连、前端代理、Nginx、Gateway 或 `Not Required` | Pending |
| cors_allowed_origins | 待填写 | architect / backend / ops | CORS origin 来源、环境变量或配置文件；禁止只硬编码 localhost | Pending |
| health_endpoint | `/api/v1/health` | backend / qa | backend route and delivery smoke command | Pending |
| delivery_e2e_command | 待填写 | qa / ops | command that starts real services and opens frontend entry | Pending |
| browser_e2e_command | 待填写 | qa / frontend | command/tool that opens a real browser and performs user actions | Pending |
| browser_e2e_user_actions | 待填写 | qa / frontend | click/fill/drag/filter/navigation actions covered by browser E2E | Pending |
| api_contract_doc | `docs/api/api.md` | architect / backend / frontend | API base, routes, auth, errors and frontend access rules | Pending |
| database_contract_doc | `docs/database/database.md` | architect / backend | database/storage source, migrations, retention or no-database reason | Pending |
| persistence_contract | 待填写 | architect / backend | database, file, memory-only, external service, or `Not Required` with reason | Pending |
| mock_policy | no mock API for Delivery E2E / Release evidence | qa / pl | mock tests are component/functional only, not release evidence | Pending |

## 规则

- 前端、后端、Vite proxy、`.env.example`、`docker-compose.yml` 必须和本表一致。
- Delivery E2E 必须从真实前端入口访问真实后端；不得用 mock API、fixture server 或组件级替身作为 release 证据。
- Browser Interaction E2E 必须打开真实浏览器并执行用户动作；只用 fetch/curl/API smoke 不能替代前端验收项的浏览器交互证据。
- API、数据库/存储、mock 策略和 runtime 配置必须互相引用：`docs/api/api.md` 说明 API 与数据库/Mock/Runtime 的关系，`docs/database/database.md` 说明数据来源与 API/Mock/Runtime 的关系。
- 目标环境存在公网、域名、IP 直连或跨域访问时，`public_*`、`cors_allowed_origins`、`proxy_mode`、`exposed_ports` 不能为空。
- 如果当前 CR 没有前端或后端，必须把对应项写成 `Not Required: <原因>`，并由 PL 在 `review.md` 记录批准。
""",
    )


def ensure_acceptance(path, change_id, change_name):
    if path.exists():
        return
    write_text(
        path,
        """# Acceptance

验收覆盖矩阵。每个 P0/P1 验收项必须能从 OpenSpec Requirement / Scenario 追到 OpenSpec task、实现证据、测试证据和覆盖结论。

| 验收编号 | 需求编号 | 优先级 | 来源规格 | 验收标准 | 设计落点 | OpenSpec Task | 实现证据 | 测试用例 / 验证命令 | 状态 | 覆盖状态 | 未覆盖原因 | PL 处理 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AC-001 | REQ-001 | P1 | `../../../openspec/changes/{change_name}/specs/capability/spec.md` | 待填写 | 待填写 | DEV-001 | 待填写 | 待填写 | Pending | not_covered | 尚未进入设计/开发 | 待 PL 审查 | 待填写 |

## 状态规则

- `覆盖状态` 只允许使用 `covered`、`not_covered`、`manual_pending`、`deferred_with_approval`、`out_of_scope_with_reason`。
- P0/P1 验收项不得缺少 `覆盖状态`、`未覆盖原因` 或 `PL 处理`。
- 发布关口前，P0/P1 不能是 `not_covered`。
- 前端可见的数据展示、列表、详情、刷新和状态查询必须作为独立可测试 AC 或明确设计落点记录，不能只写创建/更新/删除。
""".format(change_id=change_id, change_name=change_name),
    )


def ensure_test_plan(path):
    if path.exists():
        return
    write_text(
        path,
        """# Test Plan

## 测试先行范围

- 待填写。

## 测试用例产物

| 任务编号 | 测试用例产物 | 类型 | 覆盖验收项 | 状态 |
| --- | --- | --- | --- | --- |
| DEV-001 | 待填写 | automated/manual | AC-001 | Pending |

## Red 失败记录

| 任务编号 | 覆盖验收项 | 测试用例产物 | 命令 / 步骤 | 失败摘要 | 记录时间 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001 | 待填写 | 待填写 | 待填写 | 待填写 | Pending |

## Green 通过记录

| 任务编号 | 覆盖验收项 | 测试用例产物 | 命令 / 步骤 | 通过摘要 | 记录时间 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001 | 待填写 | 待填写 | 待填写 | 待填写 | Pending |

## CI/CD 证据计划

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 必需通过 | 记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DEVELOPMENT | Green 通过后 | 待填写 | AC-001 | qa / dev | 是 | `workflow/changes/<CR-ID>/test-report.md` | Pending |
| RELEASE_GATE | 发布关口前 | 待填写 | AC-001 | qa / ops | 是 | `workflow/changes/<CR-ID>/deploy-plan.md` | Pending |

## 环境测试矩阵

| 环境编号 | 环境名称 | 入口 / Origin | 适用范围 | 必测风险 | 状态 |
| --- | --- | --- | --- | --- | --- |
| ENV-L1 | DEV_LOCAL | 待填写 | 本地开发验证 | 页面加载、本机 API、基础交互 | Pending |
| ENV-L2 | DEPLOY_PRIVATE | 待填写 | 内网或测试机验证 | 部署监听、代理、服务可达性 | Pending |
| ENV-L3 | DEPLOY_PUBLIC | 待填写 | 公网 IP / 域名 / 外网入口验证 | CORS、反向代理、端口暴露、外网可访问性 | Pending |

## Delivery E2E / Runtime Smoke Plan

交付级 E2E 必须打开真实前端入口，经前端代理或运行时配置访问真实后端。mock API 可以用于组件或功能测试，但不能作为本表证据。本表证明运行通路，不替代浏览器交互验收。

| 任务编号 | 环境编号 | 证据等级 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | ENV-L1 | L1 | 待填写 | 待填写 | 待填写 | `/api/v1/health` | no | AC-001 | `workflow/changes/<CR-ID>/test-report.md` | Pending |

## Browser Interaction E2E Plan

浏览器交互 E2E 必须使用真实浏览器打开真实前端入口，执行点击、填写、拖拽、筛选、导航等用户动作，并经真实 API / Proxy 访问真实后端。只用 fetch/curl/API smoke 不得覆盖前端交互验收项。

| 任务编号 | 环境编号 | 证据等级 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | ENV-L1 | L1 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | `/api/v1/<resource>` | no | AC-001 | `workflow/changes/<CR-ID>/test-report.md` | Pending |

## TDD 流程偏差

| 任务编号 | 偏差类型 | 已写业务代码 | 缺失证据 | 补救验证 | 用户确认 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | Pending |

## 无法自动化

| 任务编号 | 项 | 原因 | 人工验证负责人 | 验证记录 |
| --- | --- | --- | --- | --- |
| DEV-001 | 待填写 | 待填写 | 待填写 | 待填写 |
""",
    )


def ensure_test_report(path):
    if path.exists():
        return
    write_text(
        path,
        """# Test Report

| 项 | 内容 |
| --- | --- |
| CR 编号 | 待填写 |
| 测试负责人 | qa |
| 测试结论 | Pending |
| 测试时间 | 待填写 |

## 测试结果汇总

| 测试类型 | 工具 | 套件数 | 用例数 | 结果 |
| --- | --- | --- | --- | --- |
| 后端单元 / 集成 | 待填写 | 待填写 | 待填写 | Pending |
| 前端组件 / 页面 | 待填写 | 待填写 | 待填写 | Pending |
| API / 契约 | 待填写 | 待填写 | 待填写 | Pending |
| Delivery E2E / Runtime Smoke | 待填写 | 待填写 | 待填写 | Pending |
| Browser Interaction E2E | 待填写 | 待填写 | 待填写 | Pending |

## CI/CD 执行结果

| 类型 | 命令 / Pipeline | 覆盖验收项 | 触发来源 | 结果 | 证据链接 / 日志 | 负责人 |
| --- | --- | --- | --- | --- | --- | --- |
| CI | 待填写 | AC-001 | Green / Release readiness | Pending | 待填写 | qa |

## Delivery E2E / Runtime Smoke Results

| 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 结果 | 证据链接 / 日志 | 负责人 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 待填写 | 待填写 | 待填写 | `/api/v1/health` | no | AC-001 | Pending | 待填写 | qa |

## Browser Interaction E2E Results

只用 API/fetch/curl/Runtime Smoke 的结果不能替代本节。存在前端行为或用户验收项时，本节必须记录真实浏览器、真实前端入口、用户动作和 no-mock 后端访问证据。

| 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 结果 | 证据链接 / 日志 | 负责人 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | `/api/v1/<resource>` | no | AC-001 | Pending | 待填写 | qa |

## 验收结果

| 验收编号 | 验收项 | 优先级 | 验证方式 | 结果 | 备注 |
| --- | --- | --- | --- | --- | --- |
| AC-001 | 待填写 | P1 | 待填写 | Pending | 待填写 |

## 缺陷

| 编号 | 问题 | 影响 | 责任 Agent | 状态 |
| --- | --- | --- | --- | --- |
| 待填写 | 待填写 | 待填写 | 待填写 | Open |
""",
    )


def ensure_deploy_plan(path):
    if path.exists():
        return
    write_text(
        path,
        """# Deploy Plan

本文记录发布关口前必须评审的发布计划。实际部署执行结果写入 `deploy-record.md`。

| 项 | 内容 |
| --- | --- |
| CR 编号 | 待填写 |
| 目标环境 | 待填写 |
| 目标证据等级 | L3 |
| 发布负责人 | ops |
| 计划状态 | Pending |
| 人工确认要求 | 待填写 |

## 发布步骤

| 步骤 | 命令 / 操作 | 预期结果 | 负责人 |
| --- | --- | --- | --- |
| 1 | 待填写 | 待填写 | ops |

## 回滚方案

- 待填写。

## 监控方案

- 待填写。

## 发布前检查

| 项 | 状态 | 说明 |
| --- | --- | --- |
| CI/CD 结果已通过或有批准豁免 | Pending | 待填写 |
| Delivery E2E / Runtime Smoke 已通过 | Pending | 必须从真实前端入口访问真实后端，Mock API=no |
| Browser Interaction E2E 已通过 | Pending | 必须真实浏览器执行用户动作；API/fetch/curl 不能替代，Mock API=no |
| 目标环境测试矩阵已覆盖 | Pending | 至少说明 ENV-L1 / ENV-L2 / ENV-L3 哪些已验证，交付目标默认要求覆盖目标环境对应项 |
| 公网 / 外网访问验证已完成或声明不适用 | Pending | 存在公网入口、域名、IP 或跨域访问时，必须验证 CORS、代理和端口暴露 |
| 测试结论已通过或阻塞项有负责人 | Pending | 待填写 |
| 安全审查已通过或阻塞项有负责人 | Pending | 待填写 |
| 回滚路径可执行 | Pending | 待填写 |
""",
    )


def ensure_deploy_record(path):
    if path.exists():
        return
    write_text(
        path,
        """# Deploy Record

| 项 | 内容 |
| --- | --- |
| CR 编号 | 待填写 |
| 版本 / Commit | 待填写 |
| 环境 | 待填写 |
| 部署负责人 | ops |
| 部署结论 | Pending |
| 部署时间 | 待填写 |

## CD 执行证据

| 制品 / 版本 | 环境 | Pipeline / 命令 | 结果 | 日志 / 监控链接 |
| --- | --- | --- | --- | --- |
| 待填写 | 待填写 | 待填写 | Pending | 待填写 |

## 部署后 Runtime Smoke

| 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 结果 | 证据链接 / 日志 |
| --- | --- | --- | --- | --- | --- | --- |
| 待填写 | 待填写 | 待填写 | `/api/v1/health` | no | Pending | 待填写 |
""",
    )


def ensure_tasks(path, change_id):
    if path.exists():
        return
    write_text(
        path,
        """# Tasks

## 实现任务

| 任务编号 | 阶段 | 负责人 Agent | 关联验收项 | Consumers | 不覆盖验收项 | 允许写入范围 | 测试用例产物 | 验证方式 | 回滚 / 撤销方案 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | DEVELOPMENT | 待填写 | AC-001 | 待填写 | 无 | 待填写 | `workflow/changes/{change_id}/test-plan.md` | 待填写 | 待填写 | Pending |

## 任务规则

- 每个任务必须关联至少一个 AC 编号。
- 每个涉及 API、页面、管理端或用户动作的任务必须填写 `Consumers`，明确哪个页面、组件、菜单、按钮、调用方或脚本会消费这项能力。
- 不覆盖的 AC 必须显式写入 `不覆盖验收项`；无不覆盖项时写 `无`。
- 声明任务完成前，必须在 `workflow/changes/<CR-ID>/review.md` 写开发覆盖声明。
""".format(change_id=change_id),
    )


def render_design_placeholder():
    return """# Design

## Overview

- 待 Architect 在 DESIGN 阶段补齐。

## Technical Approach

- 待 Architect 在 DESIGN 阶段补齐；不得自行采纳技术选型。

## Technology Decisions

| Decision | Selected | Status | Evidence |
| --- | --- | --- | --- |
| 语言 / 框架 | 待确认 | Proposed | 待用户/PL/Architect 确认 |
| 数据库 / 存储 | 待确认 | Proposed | 待用户/PL/Architect 确认 |
| 缓存 / 队列 | 待确认 | Proposed | 待用户/PL/Architect 确认 |
| 云服务 / 部署方式 | 待确认 | Proposed | 待用户/PL/Architect 确认 |
| 模型供应商 / AI 工具 | 待确认 | Proposed | 待用户/PL/Architect 确认 |

## Document Sync

| Target Doc | Status | Summary / Evidence |
| --- | --- | --- |
| `docs/architecture/architecture.md` | Pending | 待确认设计后同步模块边界和核心流程。 |
| `docs/api/api.md` | Pending | 待确认是否有 API 契约变化。 |
| `docs/database/database.md` | Pending | 待确认是否有数据模型或迁移变化。 |
| `docs/security/security.md` | Pending | 待确认权限、敏感数据和审计影响。 |
| `docs/decisions/decisions.md` | Pending | 待确认是否产生重要取舍或不可逆决策。 |
| `docs/runtime/runtime-contract.md` | Pending | 待确认前端入口、后端地址、API base、代理、健康检查、交付级 E2E、浏览器交互 E2E、API/数据库契约和 mock policy。 |
"""


def bootstrap_project(project_root, prd_text, change_id, change_name):
    created_at = now_text()
    title = title_from_prd(prd_text)
    if not change_id:
        change_id = next_change_id(project_root / "workflow" / "changes")
    if not change_name:
        change_name = "%s-%s" % (change_id, slugify(title))

    ensure_skeleton(project_root)
    change_dir = project_root / "workflow" / "changes" / change_id
    change_dir.mkdir(parents=True, exist_ok=True)
    (change_dir / "logs" / "agent-runs").mkdir(parents=True, exist_ok=True)
    openspec_dir = project_root / "openspec" / "changes" / change_name
    (openspec_dir / "specs" / "capability").mkdir(parents=True, exist_ok=True)

    write_text(change_dir / "change.md", render_change(change_id, title, change_name, prd_text, created_at))
    write_text(project_root / "docs" / "prd" / "prd.md", render_prd_doc(change_id, title, prd_text, created_at))
    write_text(project_root / "workflow" / "state.md", render_state(change_id, title, change_name, created_at))
    ensure_review(project_root, change_id, change_name, created_at)
    ensure_runtime_contract(project_root / "docs" / "runtime" / "runtime-contract.md")

    ensure_acceptance(change_dir / "acceptance.md", change_id, change_name)
    ensure_test_plan(change_dir / "test-plan.md")
    ensure_test_report(change_dir / "test-report.md")
    ensure_placeholder(change_dir / "security-review.md", "Security Review")
    ensure_deploy_plan(change_dir / "deploy-plan.md")
    ensure_deploy_record(change_dir / "deploy-record.md")
    ensure_placeholder(openspec_dir / "proposal.md", "Proposal")
    if not (openspec_dir / "design.md").exists():
        write_text(openspec_dir / "design.md", render_design_placeholder())
    ensure_tasks(openspec_dir / "tasks.md", change_id)
    ensure_placeholder(openspec_dir / "specs" / "capability" / "spec.md", "Capability Spec")

    generated_agents = generate_agents(project_root)
    return change_id, change_name, generated_agents


def parse_args():
    parser = argparse.ArgumentParser(description="Bootstrap OpenClaw workflow from a PRD text or file.")
    parser.add_argument("--project-root", default=".", help="Project/kanban workspace root.")
    parser.add_argument("--prd-file", help="Path to PRD markdown/text file.")
    parser.add_argument("--prd-text", help="Raw PRD text. Prefer --prd-file for long input.")
    parser.add_argument("--change-id", default="", help="CR id. Defaults to next CR-###.")
    parser.add_argument("--change", default="", help="OpenSpec change directory name. Defaults to CR slug.")
    parser.add_argument("--workspace-root", default=os.environ.get("OPENCLAW_WORKSPACE_ROOT", ""), help="Deprecated. Role workspaces must not mirror project files.")
    parser.add_argument("--roles", default=",".join(ROLE_NAMES), help="Deprecated. Role workspaces must not mirror project files.")
    parser.add_argument("--no-sync-workspaces", action="store_true", help="Deprecated no-op. Project files are never mirrored into role workspaces.")
    return parser.parse_args()


def main():
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    if args.prd_file:
        prd_text = read_text(Path(args.prd_file).resolve())
    else:
        prd_text = args.prd_text or sys.stdin.read()
    if not prd_text.strip():
        print("PRD text is empty. Pass --prd-file, --prd-text, or stdin.", file=sys.stderr)
        return 2

    change_id, change_name, agents = bootstrap_project(project_root, prd_text, args.change_id, args.change)

    print("OpenClaw PRD bootstrap complete.")
    print("CR: %s" % change_id)
    print("OpenSpec change: %s" % change_name)
    print("Ensured role AGENTS.md: %d" % len(agents))
    print("Workspace sync: disabled; role workspaces are runtime shells and must not mirror project files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
