#!/usr/bin/env python3
"""Executable fixtures for workflow and gate readiness tools."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[2]
TEST_ARTIFACT = "backend/tests/test_example.py"
TEST_ARTIFACT_DEV2 = "backend/tests/test_example_two.py"
TEST_RED_COMMAND = f"python {TEST_ARTIFACT}"
TEST_GREEN_COMMAND = f"python {TEST_ARTIFACT}"
TEST_GREEN_COMMAND_DEV2 = f"python {TEST_ARTIFACT_DEV2}"
ROLE_TO_TEMPLATE_DIR = {
    "hr": "hr",
    "ceo": "ceo",
    "pl": "pl",
    "pm": "pm",
    "sa": "architect",
    "qa": "qa",
    "security": "security",
    "op": "ops",
    "be": "backend",
    "fe": "frontend",
    "admin": "admin",
    "ai": "ai-engineer",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def normalize_prompt_text(text: str) -> str:
    return text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"


def strip_front_matter(text: str) -> str:
    lines = normalize_prompt_text(text).splitlines()
    if not lines or lines[0].strip() != "---":
        return "\n".join(lines).strip() + "\n"
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).strip() + "\n"
    return "\n".join(lines).strip() + "\n"


def runtime_prompt_text(root: Path, workspace_name: str) -> tuple[str, str]:
    template_dir = ROLE_TO_TEMPLATE_DIR[workspace_name]
    role_dir = root / "skills" / template_dir
    soul_text = normalize_prompt_text((role_dir / "AGENTS.md").read_text(encoding="utf-8"))
    skill_text = strip_front_matter((role_dir / "SKILL.md").read_text(encoding="utf-8"))
    agents_text = soul_text.rstrip() + "\n\n---\n\n" + skill_text.rstrip() + "\n"
    return agents_text, soul_text


def write_runtime_workspace(root: Path, workspace: Path, workspace_name: str) -> None:
    agents_text, soul_text = runtime_prompt_text(root, workspace_name)
    write(workspace / "PROJECT_WORKSPACE.md", "project_root: pending\nsource: test\nupdated_at: 2026-06-08T00:00:00Z\n")
    write(workspace / "AGENTS.md", agents_text)
    write(workspace / "SOUL.md", soul_text)
    write(workspace / ".openclaw-agent" / "AGENTS.md", agents_text)
    write(workspace / ".openclaw-agent" / "SOUL.md", soul_text)


class ReadinessToolTests(unittest.TestCase):
    def run_tool(self, project_root: Path, *args: str, expected: int) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, *args],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, expected, output)
        return result

    def copy_template(self) -> Path:
        temp_root = Path(tempfile.mkdtemp(prefix="readiness-fixture-"))
        project_root = temp_root / "project"
        shutil.copytree(TEMPLATE_ROOT, project_root)
        self.addCleanup(shutil.rmtree, temp_root, ignore_errors=True)
        return project_root

    def test_bootstrap_preserves_existing_role_agents_prompts(self) -> None:
        root = self.copy_template()
        pm_agents = root / "skills" / "pm" / "AGENTS.md"
        before = pm_agents.read_text(encoding="utf-8")
        self.assertIn("## 执行方法", before)

        result = self.run_tool(
            root,
            "tools/bootstrap-openclaw-prd.py",
            "--project-root",
            str(root),
            "--prd-text",
            "示例需求：实现一个可验证的业务功能，包含用户动作、系统结果和验收标准。",
            expected=0,
        )

        after = pm_agents.read_text(encoding="utf-8")
        self.assertEqual(after, before)
        self.assertIn("Ensured role AGENTS.md", result.stdout)

    def set_state(self, root: Path, stage: str, gate: str, owner: str = "pl", task: str = "DEV-001") -> None:
        write(
            root / "workflow" / "state.md",
            f"""# Workflow State

- 需求名称：Example Capability
- 当前阶段：{stage}
- 当前状态：in_progress
- 当前负责人：{owner}
- 当前关口：{gate}
- 当前变更：workflow/changes/CR-001/
- 当前 OpenSpec Change：openspec/changes/CR-001-example-change/
- 当前任务：{task}
""",
        )

    def make_ready_project(self) -> Path:
        root = self.copy_template()
        change_dir = root / "openspec" / "changes" / "CR-001-example-change"
        cr_dir = root / "workflow" / "changes" / "CR-001"

        self.set_state(root, "DEVELOPMENT", "DESIGN_GATE", owner="backend")
        write(
            cr_dir / "change.md",
            """# Change

## 问题和目标

- 现状：Example capability is absent.
- 目标：Deliver example capability.
- 成功标准：AC-001 is verified.
- 本次不做：Production deployment.
""",
        )
        write(
            change_dir / "proposal.md",
            """# Proposal: Example Change

## Why

- Users need the example capability.

## What Changes

- Add a minimal backend example behavior.

## Non-Goals

- No production rollout in this change.

## Success Criteria

- AC-001 is verified by an automated test.

## Impact

| Area | Impact | Notes |
| --- | --- | --- |
| API | No breaking change | Internal example only |

## Open Questions

| ID | Question | Blocks MVP | User Answer | Resolution | Status | Shown to User |
| --- | --- | --- | --- | --- | --- | --- |
| Q-001 | Is a public API required for the MVP? | 否 | User confirmed no public API for MVP. | Deferred as non-blocking. | Open | Shown in chat before REQ_GATE. |
""",
        )
        write(
            change_dir / "specs" / "capability" / "spec.md",
            """# Capability Spec

## ADDED Requirements

### Requirement: Example Requirement

The system SHALL expose the example behavior.

#### Scenario: Example Scenario

- GIVEN a valid example request
- WHEN the backend handles it
- THEN the example response is returned

## Open Questions

| ID | Question | Blocks MVP | User Answer | Resolution | Status | Shown to User |
| --- | --- | --- | --- | --- | --- | --- |
| Q-002 | Is the example response format final? | 否 | User accepted the current MVP format. | Non-blocking follow-up can refine it later. | Open | Shown in chat before REQ_GATE. |
""",
        )
        write(
            change_dir / "design.md",
            """# Design

## Overview

- Implement the example behavior inside the backend module.

## Technical Approach

- Add one backend source file and one automated test artifact.

## Technology Decisions

| Decision | Selected | Status | Evidence |
| --- | --- | --- | --- |
| New framework / database / infrastructure | None | Not Required | This fixture uses the existing template boundary only. |

## Document Sync

| Target Doc | Status | Summary / Evidence |
| --- | --- | --- |
| `docs/architecture/architecture.md` | Not Required | The example behavior does not change long-term module boundaries. |
| `docs/api/api.md` | Not Required | No public API contract changes in this fixture. |
| `docs/database/database.md` | Not Required | No data model or migration changes. |
| `docs/security/security.md` | Not Required | No auth, permission, or sensitive data changes. |
| `docs/decisions/decisions.md` | Not Required | No irreversible architecture decision introduced. |
| `docs/runtime/runtime-contract.md` | Synced | Runtime delivery contract is recorded for this fixture. |

## Risks and Rollback

- Revert DEV-001 if verification fails.
""",
        )
        write(
            change_dir / "tasks.md",
            f"""# Tasks

## Implementation Tasks

| Task ID | Phase | Owner Agent | Requirement / AC | Excluded AC | Allowed Write Scope | Test Case Artifact | Verification | Rollback / Revert Plan | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | DEVELOPMENT | backend | AC-001 | 无 | backend/src/example.py | workflow/changes/CR-001/test-plan.md#DEV-001 | {TEST_GREEN_COMMAND} | Revert backend/src/example.py | Ready |
""",
        )
        write(
            cr_dir / "acceptance.md",
            f"""# Acceptance

| 验收编号 | 需求编号 | 优先级 | 来源规格 | 验收标准 | 设计落点 | OpenSpec Task | 实现证据 | 测试用例 / 验证命令 | 状态 | 覆盖状态 | 未覆盖原因 | PL 处理 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AC-001 | REQ-001 | P1 | `../../../openspec/changes/CR-001-example-change/specs/capability/spec.md` | Example response is returned | backend/src/example.py | DEV-001 | backend/src/example.py | {TEST_GREEN_COMMAND} | Ready | not_covered | Awaiting implementation | Pending PL review | Awaiting QA |
""",
        )
        write(
            cr_dir / "test-plan.md",
            f"""# Test Plan

## Test-First Scope

- Cover AC-001 with an automated backend test.

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 类型 | 覆盖验收项 | 状态 |
| --- | --- | --- | --- | --- |
| DEV-001 | {TEST_ARTIFACT} | automated | AC-001 | Ready |

## Red Failure Records

| 任务编号 | 覆盖验收项 | 测试用例产物 | 命令 / 步骤 | 失败摘要 | 记录时间 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_RED_COMMAND} | Expected failure before implementation | 2026-06-08T00:00:00Z | Recorded |

## Green Pass Records

| 任务编号 | 覆盖验收项 | 测试用例产物 | 命令 / 步骤 | 通过摘要 | 记录时间 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_GREEN_COMMAND} | Passed after implementation | 2026-06-08T00:10:00Z | Recorded |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 必需通过 | 记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DEVELOPMENT | Green pass | {TEST_GREEN_COMMAND} | AC-001 | qa | yes | workflow/changes/CR-001/test-report.md | Ready |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | {TEST_GREEN_COMMAND} | http://localhost:3000 | http://localhost:8080 | /api/v1/health | no | AC-001 | workflow/changes/CR-001/test-report.md | Ready |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | {TEST_GREEN_COMMAND} | fixture browser | open page and verify example action | http://localhost:3000 | http://localhost:8080 | /api/v1/example | no | AC-001 | workflow/changes/CR-001/test-report.md | Ready |

## Cannot Automate

| 任务编号 | 项 | 原因 | 人工验证负责人 | 验证记录 |
| --- | --- | --- | --- | --- |
""",
        )
        write(
            root / "docs" / "runtime" / "runtime-contract.md",
            f"""# Runtime Contract

| Key | Value | Owner | Evidence / Source | Status |
| --- | --- | --- | --- | --- |
| frontend_origin | http://localhost:3000 | architect / frontend | fixture .env and compose | Defined |
| backend_origin | http://localhost:8080 | architect / backend | fixture backend listen config | Defined |
| frontend_port | 3000 | frontend / ops | fixture compose | Defined |
| backend_port | 8080 | backend / ops | fixture compose | Defined |
| api_base_path | /api/v1 | architect / backend / frontend | docs/api/api.md | Defined |
| frontend_to_backend_url | http://localhost:3000/api/v1/health | frontend / backend | browser proxy smoke | Defined |
| vite_proxy_target | http://localhost:8080 | frontend | fixture vite proxy target | Defined |
| health_endpoint | /api/v1/health | backend / qa | fixture smoke | Defined |
| delivery_e2e_command | {TEST_GREEN_COMMAND} | qa / ops | fixture command | Defined |
| browser_e2e_command | {TEST_GREEN_COMMAND} | qa / frontend | fixture browser command | Defined |
| browser_e2e_user_actions | open page and verify example action | qa / frontend | fixture browser actions | Defined |
| api_contract_doc | docs/api/api.md | architect / backend / frontend | fixture API contract | Defined |
| database_contract_doc | docs/database/database.md | architect / backend | fixture database contract | Defined |
| persistence_contract | Not Required: fixture has no database writes | architect / backend | fixture storage decision | Defined |
| mock_policy | no mock API for Delivery E2E / Release evidence | qa / pl | QA policy | Defined |
""",
        )
        write(
            cr_dir / "review.md",
            f"""# Review

## Gate Approvals

| Gate | Owner | Reviewers | Readiness Command | Conclusion | Next Stage | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| INIT | ceo | pl | manual | passed | TRIAGE | Approved |
| REQ_GATE | pl | pl | python tools/check-gate-readiness.py --gate requirement --change CR-001-example-change --change-id CR-001 | passed | DESIGN | Approved |
| DESIGN_GATE | pl | architect | python tools/check-gate-readiness.py --gate design --change CR-001-example-change --change-id CR-001 | passed | DEVELOPMENT | Approved |
| RELEASE_GATE | pl | qa / security / ops | python tools/check-gate-readiness.py --gate release --change CR-001-example-change --change-id CR-001 | draft | DEPLOY | Pending |

## 阶段结论

| 阶段 | 负责人 | 输入 | 输出 | 结论 |
| --- | --- | --- | --- | --- |
| INIT | ceo | change.md | Go decision | passed |
| TRIAGE | pl | INIT | Owner and risk routing | submitted |
| REQUIREMENT | pm | TRIAGE | proposal/specs/acceptance | submitted |
| DESIGN | architect | REQ_GATE | design/tasks/test-plan | submitted |

## Stage Pause Confirmations

| Stage | Action | Next Stage | Deliverables | Summary Shown | User Confirmation | Recorded At | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REQ_GATE | approve | DESIGN | requirement gate review | Requirement readiness and open question summary shown to user. | User confirmed entering DESIGN. | 2026-06-08T00:05:00Z | Recorded before state transition. |

## Development Task Handoffs

| Completed Task | Completion Status | Pause Report | User Continue | Next Task | Recorded At | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## 开发覆盖声明

| 任务编号 | 已实现 AC | 已测试 AC | 未实现 AC | 未测试 AC | 已运行命令 | CI/CD 证据 | 失败命令 | 需要人工验收 | 已知风险 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001 | AC-001 | 无 | 无 | {TEST_GREEN_COMMAND} | 本地 CI 等价：{TEST_GREEN_COMMAND} | 无 | 无 | 无 |

## QA 覆盖复核

| 验收编号 | 开发声明 | QA 复核 | 结论 | 退回对象 |
| --- | --- | --- | --- | --- |
| AC-001 | DEV-001 declares AC-001 covered. | QA reviewed Green evidence. | passed | 无 |

## 人工验收范围

- 已覆盖：AC-001。
- 明确未覆盖：无。
- 已批准暂缓：无。
- 不属于本 CR：无。
- 需要人工只验证：无。
""",
        )
        write(
            cr_dir / "test-report.md",
            f"""# Test Report

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-001 |
| 测试负责人 | qa |
| 测试结论 | Passed |
| 测试时间 | 2026-06-08T00:15:00Z |

## CI/CD 执行结果

| 类型 | 命令 / Pipeline | 覆盖验收项 | 触发来源 | 结果 | 证据链接 / 日志 | 负责人 |
| --- | --- | --- | --- | --- | --- | --- |
| CI | {TEST_GREEN_COMMAND} | AC-001 | QA 复核 | passed | workflow/changes/CR-001/logs/agent-runs/20260608-backend-DEV-001.md | qa |

## Delivery E2E / Runtime Smoke Results

| 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 结果 | 证据链接 / 日志 | 负责人 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {TEST_GREEN_COMMAND} | http://localhost:3000 | http://localhost:8080 | /api/v1/health | no | AC-001 | passed | workflow/changes/CR-001/logs/agent-runs/20260608-backend-DEV-001.md | qa |

## Browser Interaction E2E Results

| 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 结果 | 证据链接 / 日志 | 负责人 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {TEST_GREEN_COMMAND} | fixture browser | open page and verify example action | http://localhost:3000 | http://localhost:8080 | /api/v1/example | no | AC-001 | passed | workflow/changes/CR-001/logs/agent-runs/20260608-backend-DEV-001.md | qa |
""",
        )
        write(
            cr_dir / "security-review.md",
            """# Security Review

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-001 |
| 审查负责人 | security |
| 审查结论 | Passed |
| 审查时间 | 2026-06-08T00:20:00Z |
""",
        )
        write(
            cr_dir / "deploy-plan.md",
            f"""# Deploy Plan

## 发布步骤

| 步骤 | 命令 / 操作 | 预期结果 | 负责人 |
| --- | --- | --- | --- |
| 1 | Deploy to staging | Service health check passes | ops |

## 回滚方案

- Revert DEV-001 and redeploy the previous version.

## 监控方案

- Watch service health and error rates after deployment.

## 发布前检查

| 项 | 状态 | 说明 |
| --- | --- | --- |
| CI/CD 结果已通过或有批准豁免 | passed | {TEST_GREEN_COMMAND} passed |
| Delivery E2E / Runtime Smoke 已通过 | passed | {TEST_GREEN_COMMAND} passed with Mock API=no |
| Browser Interaction E2E 已通过 | passed | {TEST_GREEN_COMMAND} passed with real browser action and Mock API=no |
| 测试结论已通过或阻塞项有负责人 | passed | Test report passed |
| 安全审查已通过或阻塞项有负责人 | passed | Security review passed |
| 回滚路径可执行 | passed | Revert DEV-001 and redeploy |
""",
        )
        write(cr_dir / "logs" / "agent-runs" / "20260608-backend-DEV-001.md", "# Agent Run\n\nRecorded.\n")
        write(root / "backend" / "src" / "example.py", "# placeholder\n")
        write(
            root / TEST_ARTIFACT,
            "from pathlib import Path\n\nassert Path('backend/src/example.py').exists()\n",
        )
        return root

    def add_second_dev_task(
        self,
        root: Path,
        *,
        dev1_status: str = "Completed",
        pause_report: str | None = "Reported",
        user_continue: str | None = "Confirmed",
    ) -> None:
        change_dir = root / "openspec" / "changes" / "CR-001-example-change"
        cr_dir = root / "workflow" / "changes" / "CR-001"

        tasks_path = change_dir / "tasks.md"
        tasks = tasks_path.read_text(encoding="utf-8")
        tasks_path.write_text(
            tasks.replace(
                f"| DEV-001 | DEVELOPMENT | backend | AC-001 | 无 | backend/src/example.py | workflow/changes/CR-001/test-plan.md#DEV-001 | {TEST_GREEN_COMMAND} | Revert backend/src/example.py | Ready |",
                f"| DEV-001 | DEVELOPMENT | backend | AC-001 | 无 | backend/src/example.py | workflow/changes/CR-001/test-plan.md#DEV-001 | {TEST_GREEN_COMMAND} | Revert backend/src/example.py | {dev1_status} |\n"
                f"| DEV-002 | DEVELOPMENT | backend | AC-001 | 无 | backend/src/example_two.py | workflow/changes/CR-001/test-plan.md#DEV-002 | {TEST_GREEN_COMMAND_DEV2} | Revert backend/src/example_two.py | Ready |",
            ),
            encoding="utf-8",
            newline="\n",
        )

        test_plan_path = cr_dir / "test-plan.md"
        test_plan = test_plan_path.read_text(encoding="utf-8")
        test_plan = test_plan.replace(
            f"| DEV-001 | {TEST_ARTIFACT} | automated | AC-001 | Ready |",
            f"| DEV-001 | {TEST_ARTIFACT} | automated | AC-001 | Ready |\n"
            f"| DEV-002 | {TEST_ARTIFACT_DEV2} | automated | AC-001 | Ready |",
        )
        test_plan = test_plan.replace(
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_RED_COMMAND} | Expected failure before implementation | 2026-06-08T00:00:00Z | Recorded |",
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_RED_COMMAND} | Expected failure before implementation | 2026-06-08T00:00:00Z | Recorded |\n"
            f"| DEV-002 | AC-001 | {TEST_ARTIFACT_DEV2} | {TEST_RED_COMMAND} | Expected failure before implementation | 2026-06-08T00:20:00Z | Recorded |",
        )
        test_plan_path.write_text(test_plan, encoding="utf-8", newline="\n")

        acceptance_path = cr_dir / "acceptance.md"
        acceptance_text = acceptance_path.read_text(encoding="utf-8")
        acceptance_path.write_text(
            acceptance_text.replace(" | DEV-001 | backend/src/example.py |", " | DEV-001, DEV-002 | backend/src/example.py |"),
            encoding="utf-8",
            newline="\n",
        )

        if pause_report is None and user_continue is None:
            return

        review_path = cr_dir / "review.md"
        review = review_path.read_text(encoding="utf-8")
        marker = (
            "| Completed Task | Completion Status | Pause Report | User Continue | Next Task | Recorded At | Notes |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
        )
        row = (
            f"| DEV-001 | {dev1_status} | {pause_report or ''} | {user_continue or ''} | "
            "DEV-002 | 2026-06-08T00:30:00Z | User-visible handoff recorded. |\n"
        )
        review_path.write_text(review.replace(marker, marker + row), encoding="utf-8", newline="\n")

    def mark_acceptance_verified(self, root: Path) -> None:
        acceptance = root / "workflow" / "changes" / "CR-001" / "acceptance.md"
        acceptance.write_text(
            acceptance.read_text(encoding="utf-8").replace(
                "| Ready | not_covered | Awaiting implementation | Pending PL review | Awaiting QA |",
                "| Verified | covered | 无 | PL accepted coverage | QA passed |",
            ),
            encoding="utf-8",
            newline="\n",
        )

    def test_template_example_fails_closed(self) -> None:
        self.run_tool(
            TEMPLATE_ROOT,
            "tools/check-transition-readiness.py",
            "--change-id",
            "CR-001",
            "--from-stage",
            "INTAKE",
            "--to-stage",
            "REQUIREMENT",
            "--action",
            "submit",
            expected=1,
        )
        self.run_tool(
            TEMPLATE_ROOT,
            "tools/check-gate-readiness.py",
            "--gate",
            "requirement",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.run_tool(
            TEMPLATE_ROOT,
            "tools/check-workflow-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            "--target-file",
            "backend/src/example.py",
            expected=1,
        )
        self.run_tool(
            TEMPLATE_ROOT,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.run_tool(
            TEMPLATE_ROOT,
            "tools/check-dev-task-handoff-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--next-task-id",
            "DEV-001",
            expected=1,
        )

    def test_happy_path_passes_all_readiness_checks(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "REQ_GATE", "REQ_GATE")
        self.run_tool(
            root,
            "tools/check-transition-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--from-stage",
            "REQ_GATE",
            "--to-stage",
            "DEVELOPMENT",
            "--action",
            "approve",
            expected=1,
        )
        self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "requirement",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=0,
        )
        self.run_tool(
            root,
            "tools/check-transition-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--from-stage",
            "REQ_GATE",
            "--to-stage",
            "DESIGN",
            "--action",
            "approve",
            expected=0,
        )
        self.set_state(root, "DESIGN_GATE", "DESIGN_GATE")
        self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "design",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=0,
        )
        acceptance = root / "workflow" / "changes" / "CR-001" / "acceptance.md"
        acceptance.write_text(
            acceptance.read_text(encoding="utf-8").replace(
                "| Ready | not_covered | Awaiting implementation | Pending PL review | Awaiting QA |",
                "| Verified | covered | 无 | PL accepted coverage | QA passed |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.set_state(root, "RELEASE_GATE", "RELEASE_GATE")
        self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "release",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=0,
        )
        self.set_state(root, "DEVELOPMENT", "DESIGN_GATE", owner="backend")
        self.run_tool(
            root,
            "tools/check-dev-task-handoff-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--next-task-id",
            "DEV-001",
            expected=0,
        )
        self.run_tool(
            root,
            "tools/check-workflow-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            "--target-file",
            "backend/src/example.py",
            expected=0,
        )
        self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=0,
        )

    def test_release_allows_blocked_acceptance_with_deferred_approval_note(self) -> None:
        root = self.make_ready_project()
        acceptance = root / "workflow" / "changes" / "CR-001" / "acceptance.md"
        acceptance.write_text(
            acceptance.read_text(encoding="utf-8").replace(
                "| Ready | not_covered | Awaiting implementation | Pending PL review | Awaiting QA |",
                "| Blocked | deferred_with_approval | Browser UI validation moved to CR-002 | PL approved defer | PL approval recorded before release |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        review_path = root / "workflow" / "changes" / "CR-001" / "review.md"
        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                "| AC-001 | DEV-001 declares AC-001 covered. | QA reviewed Green evidence. | passed | 无 |",
                "| AC-001 | DEV-001 declares AC-001 deferred with approval. | QA confirmed defer record. | blocked | pl |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.set_state(root, "RELEASE_GATE", "RELEASE_GATE")
        self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "release",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=0,
        )

    def test_design_accepts_manual_confirmation_text_as_decision_evidence(self) -> None:
        root = self.make_ready_project()
        design = root / "openspec" / "changes" / "CR-001-example-change" / "design.md"
        design.write_text(
            design.read_text(encoding="utf-8").replace(
                "| New framework / database / infrastructure | None | Not Required | This fixture uses the existing template boundary only. |",
                "| New framework / database / infrastructure | Python stdlib | Accepted | PL 确认: this fixture deliberately uses plain manual confirmation text. |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.set_state(root, "DESIGN_GATE", "DESIGN_GATE")
        self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "design",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=0,
        )

    def test_design_gate_rejects_missing_runtime_contract(self) -> None:
        root = self.make_ready_project()
        (root / "docs" / "runtime" / "runtime-contract.md").unlink()
        self.set_state(root, "DESIGN_GATE", "DESIGN_GATE")

        result = self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "design",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.assertIn("runtime-contract.md", result.stdout)

    def test_release_gate_rejects_mock_delivery_smoke(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        test_report = root / "workflow" / "changes" / "CR-001" / "test-report.md"
        test_report.write_text(
            test_report.read_text(encoding="utf-8").replace(
                "| python backend/tests/test_example.py | http://localhost:3000 | http://localhost:8080 | /api/v1/health | no | AC-001 | passed | workflow/changes/CR-001/logs/agent-runs/20260608-backend-DEV-001.md | qa |",
                "| python backend/tests/test_example.py --mock | http://localhost:3000 | http://localhost:8080 | /api/v1/health | yes | AC-001 | passed | workflow/changes/CR-001/logs/agent-runs/20260608-backend-DEV-001.md | qa |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.set_state(root, "RELEASE_GATE", "RELEASE_GATE")

        result = self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "release",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.assertIn("Mock API", result.stdout)
        self.assertIn("mock", result.stdout.lower())

    def test_release_gate_rejects_missing_browser_e2e_results(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        test_report = root / "workflow" / "changes" / "CR-001" / "test-report.md"
        text = test_report.read_text(encoding="utf-8")
        start = text.index("\n## Browser Interaction E2E Results\n")
        test_report.write_text(text[:start], encoding="utf-8", newline="\n")
        self.set_state(root, "RELEASE_GATE", "RELEASE_GATE")

        result = self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "release",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.assertIn("Browser Interaction E2E Results", result.stdout)

    def test_transition_rejects_missing_stage_pause_confirmation(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "REQ_GATE", "REQ_GATE")
        review_path = root / "workflow" / "changes" / "CR-001" / "review.md"
        review = review_path.read_text(encoding="utf-8")
        start = review.index("\n## Stage Pause Confirmations\n")
        end = review.index("\n## Development Task Handoffs\n")
        review_path.write_text(review[:start] + review[end:], encoding="utf-8", newline="\n")

        result = self.run_tool(
            root,
            "tools/check-transition-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--from-stage",
            "REQ_GATE",
            "--to-stage",
            "DESIGN",
            "--action",
            "approve",
            expected=1,
        )
        self.assertIn("阶段暂停确认", result.stdout)

    def test_transition_rejects_prd_autopilot_as_user_confirmation(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "REQ_GATE", "REQ_GATE")
        review_path = root / "workflow" / "changes" / "CR-001" / "review.md"
        review = review_path.read_text(encoding="utf-8")
        review_path.write_text(
            review.replace("User confirmed entering DESIGN.", "PRD 自动入口授权"),
            encoding="utf-8",
            newline="\n",
        )

        result = self.run_tool(
            root,
            "tools/check-transition-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--from-stage",
            "REQ_GATE",
            "--to-stage",
            "DESIGN",
            "--action",
            "approve",
            expected=1,
        )
        self.assertIn("不能使用 PRD 自动入口授权", result.stdout)

    def test_design_gate_rejects_missing_document_sync(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "DESIGN_GATE", "DESIGN_GATE")
        design_path = root / "openspec" / "changes" / "CR-001-example-change" / "design.md"
        design = design_path.read_text(encoding="utf-8")
        start = design.index("\n## Document Sync\n")
        end = design.index("\n## Risks and Rollback\n")
        design_path.write_text(design[:start] + design[end:], encoding="utf-8", newline="\n")

        result = self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "design",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.assertIn("文档同步表", result.stdout)

    def test_design_gate_rejects_unconfirmed_technology_decision(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "DESIGN_GATE", "DESIGN_GATE")
        design_path = root / "openspec" / "changes" / "CR-001-example-change" / "design.md"
        design = design_path.read_text(encoding="utf-8")
        design_path.write_text(
            design.replace(
                "| New framework / database / infrastructure | None | Not Required | This fixture uses the existing template boundary only. |",
                "| Primary database | PostgreSQL | Proposed | Architect recommends it. |",
            ),
            encoding="utf-8",
            newline="\n",
        )

        result = self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "design",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.assertIn("不得通过 DESIGN_GATE", result.stdout)

    def test_design_gate_rejects_accepted_technology_without_accepted_adr(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "DESIGN_GATE", "DESIGN_GATE")
        design_path = root / "openspec" / "changes" / "CR-001-example-change" / "design.md"
        design = design_path.read_text(encoding="utf-8")
        design_path.write_text(
            design.replace(
                "| New framework / database / infrastructure | None | Not Required | This fixture uses the existing template boundary only. |",
                "| Primary database | PostgreSQL | Accepted | `docs/decisions/0001-use-postgresql.md` |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        write(
            root / "docs" / "decisions" / "0001-use-postgresql.md",
            """# ADR-0001: Use PostgreSQL

状态：Proposed

## 背景

- Candidate only.
""",
        )

        result = self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "design",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.assertIn("不是 Accepted", result.stdout)

    def test_task_completion_executes_green_command_success(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=0,
        )
        self.assertIn("任务完成检查：通过", result.stdout)

    def test_task_completion_allows_acceptance_referencing_test_artifact(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        acceptance_path = root / "workflow" / "changes" / "CR-001" / "acceptance.md"
        acceptance_path.write_text(
            acceptance_path.read_text(encoding="utf-8").replace(TEST_GREEN_COMMAND, TEST_ARTIFACT),
            encoding="utf-8",
            newline="\n",
        )
        self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=0,
        )

    def test_task_completion_rejects_acceptance_not_aligned_with_green_evidence(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        acceptance_path = root / "workflow" / "changes" / "CR-001" / "acceptance.md"
        acceptance_path.write_text(
            acceptance_path.read_text(encoding="utf-8").replace(
                TEST_GREEN_COMMAND,
                "python backend/tests/test_other.py",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.assertIn("必须引用 Green 命令或当前测试用例产物", result.stdout)

    def test_task_completion_rejects_green_command_failure(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        write(root / TEST_ARTIFACT, "raise SystemExit(7)\n")
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.assertIn("Green 命令真实执行失败", result.stdout)
        self.assertIn("exit code = 7", result.stdout)

    def test_task_completion_rejects_green_placeholder_command(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        test_plan_path = root / "workflow" / "changes" / "CR-001" / "test-plan.md"
        green_row = (
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_GREEN_COMMAND} | "
            "Passed after implementation | 2026-06-08T00:10:00Z | Recorded |"
        )
        test_plan_path.write_text(
            test_plan_path.read_text(encoding="utf-8").replace(
                green_row,
                f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | 测试通过 | Passed after implementation | 2026-06-08T00:10:00Z | Recorded |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.assertIn("Green 记录命令不是有效真实命令", result.stdout)

    def test_task_completion_rejects_backfilled_red_record(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        test_plan_path = root / "workflow" / "changes" / "CR-001" / "test-plan.md"
        red_row = (
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_RED_COMMAND} | "
            "Expected failure before implementation | 2026-06-08T00:00:00Z | Recorded |"
        )
        test_plan_path.write_text(
            test_plan_path.read_text(encoding="utf-8").replace(
                red_row,
                f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_RED_COMMAND} | 事后补做 Red，业务代码已实现后运行 | 2026-06-08T00:00:00Z | Recorded |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.assertIn("不能作为合规 TDD Red", result.stdout)

    def test_task_completion_rejects_missing_test_artifact_file(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        (root / TEST_ARTIFACT).unlink()
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.assertIn("测试用例产物不存在", result.stdout)

    def test_task_completion_rejects_green_command_not_referencing_artifact(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        other_artifact = "backend/tests/test_other.py"
        other_command = f"python {other_artifact}"
        write(root / other_artifact, "print('unrelated test passed')\n")
        test_plan_path = root / "workflow" / "changes" / "CR-001" / "test-plan.md"
        green_row = (
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_GREEN_COMMAND} | "
            "Passed after implementation | 2026-06-08T00:10:00Z | Recorded |"
        )
        test_plan_path.write_text(
            test_plan_path.read_text(encoding="utf-8").replace(
                green_row,
                f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {other_command} | Passed after implementation | 2026-06-08T00:10:00Z | Recorded |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.assertIn("Green 命令必须引用测试用例产物", result.stdout)

    def test_task_completion_rejects_red_green_without_shared_artifact(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        other_artifact = "backend/tests/test_other.py"
        other_command = f"python {other_artifact}"
        write(root / other_artifact, "print('other test passed')\n")
        test_plan_path = root / "workflow" / "changes" / "CR-001" / "test-plan.md"
        test_plan = test_plan_path.read_text(encoding="utf-8")
        test_plan = test_plan.replace(
            f"| DEV-001 | {TEST_ARTIFACT} | automated | AC-001 | Ready |",
            f"| DEV-001 | {TEST_ARTIFACT}, {other_artifact} | automated | AC-001 | Ready |",
        )
        test_plan = test_plan.replace(
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_GREEN_COMMAND} | Passed after implementation | 2026-06-08T00:10:00Z | Recorded |",
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT}, {other_artifact} | {other_command} | Passed after implementation | 2026-06-08T00:10:00Z | Recorded |",
        )
        test_plan_path.write_text(test_plan, encoding="utf-8", newline="\n")
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.assertIn("Red/Green 命令必须覆盖同一测试用例产物", result.stdout)

    def test_task_completion_rejects_missing_red_green_fields(self) -> None:
        root = self.make_ready_project()
        self.mark_acceptance_verified(root)
        test_plan_path = root / "workflow" / "changes" / "CR-001" / "test-plan.md"
        test_plan = test_plan_path.read_text(encoding="utf-8")
        test_plan = test_plan.replace(
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_RED_COMMAND} | Expected failure before implementation | 2026-06-08T00:00:00Z | Recorded |",
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | 待填写 |  |  | Pending |",
        )
        test_plan = test_plan.replace(
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_GREEN_COMMAND} | Passed after implementation | 2026-06-08T00:10:00Z | Recorded |",
            f"| DEV-001 | AC-001 | {TEST_ARTIFACT} | {TEST_GREEN_COMMAND} |  |  | Recorded |",
        )
        test_plan_path.write_text(test_plan, encoding="utf-8", newline="\n")
        result = self.run_tool(
            root,
            "tools/check-task-completion-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            expected=1,
        )
        self.assertIn("Red 记录命令必须填写真实命令", result.stdout)
        self.assertIn("Red 记录必须填写记录时间", result.stdout)
        self.assertIn("Green 记录必须填写通过摘要", result.stdout)

    def test_requirement_gate_tracks_pending_confirmations(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "REQ_GATE", "REQ_GATE")
        change_dir = root / "openspec" / "changes" / "CR-001-example-change"

        proposal_path = change_dir / "proposal.md"
        proposal = proposal_path.read_text(encoding="utf-8")
        proposal_path.write_text(
            proposal.replace(
                "| API | No breaking change | Internal example only |",
                "| API | 待确认 | Need product decision |",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "requirement",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.assertIn("存在未关联待澄清问题的待确认", result.stdout)

        write(
            proposal_path,
            """# 提案：Example Change

## 为什么做

- Users need the example capability.

## 变更内容

- Add a minimal backend example behavior.

## 不做范围

- No production rollout in this change.

## 成功标准

- AC-001 is verified by an automated test.

## 影响范围

| 领域 | 影响 | 备注 |
| --- | --- | --- |
| API | 待确认，见 Q-001 | Public API can be decided later |

## 待澄清问题

| 编号 | 问题 | 是否阻塞 MVP | 用户回答 | 处理结论 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Q-001 | 是否需要公开 API？ | 否 | 待确认 | 暂缓，不阻塞 MVP | Open |
""",
        )
        result = self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "requirement",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=1,
        )
        self.assertIn("必须记录已向用户展示", result.stdout)

        write(
            proposal_path,
            """# 提案：Example Change

## 为什么做

- Users need the example capability.

## 变更内容

- Add a minimal backend example behavior.

## 不做范围

- No production rollout in this change.

## 成功标准

- AC-001 is verified by an automated test.

## 影响范围

| 领域 | 影响 | 备注 |
| --- | --- | --- |
| API | 待确认，见 Q-001 | Public API can be decided later |

## 待澄清问题

| 编号 | 问题 | 是否阻塞 MVP | 用户回答 | 处理结论 | 状态 | 展示状态 |
| --- | --- | --- | --- | --- | --- | --- |
| Q-001 | 是否需要公开 API？ | 否 | 用户确认 MVP 暂不需要公开 API | 暂缓，不阻塞 MVP | Open | 已在聊天里向用户展示并确认暂缓 |
""",
        )
        self.run_tool(
            root,
            "tools/check-gate-readiness.py",
            "--gate",
            "requirement",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            expected=0,
        )

    def test_code_readiness_rejects_inactive_change(self) -> None:
        root = self.make_ready_project()
        state = root / "workflow" / "state.md"
        state.write_text(
            state.read_text(encoding="utf-8").replace(
                "当前 OpenSpec Change：openspec/changes/CR-001-example-change/",
                "当前 OpenSpec Change：openspec/changes/CR-999-other-change/",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_tool(
            root,
            "tools/check-workflow-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-001",
            "--target-file",
            "backend/src/example.py",
            expected=1,
        )
        self.assertIn("当前 OpenSpec Change 必须是 openspec/changes/CR-001-example-change", result.stdout)

    def test_dev_task_handoff_rejects_missing_pause_report(self) -> None:
        root = self.make_ready_project()
        self.add_second_dev_task(root, pause_report="Pending", user_continue="Confirmed")
        result = self.run_tool(
            root,
            "tools/check-dev-task-handoff-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--next-task-id",
            "DEV-002",
            expected=1,
        )
        self.assertIn("必须先停下汇报", result.stdout)

    def test_dev_task_handoff_rejects_missing_user_continue(self) -> None:
        root = self.make_ready_project()
        self.add_second_dev_task(root, pause_report="Reported", user_continue="Pending")
        result = self.run_tool(
            root,
            "tools/check-dev-task-handoff-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--next-task-id",
            "DEV-002",
            expected=1,
        )
        self.assertIn("必须记录用户明确继续确认", result.stdout)

        result = self.run_tool(
            root,
            "tools/check-workflow-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-002",
            "--target-file",
            "backend/src/example_two.py",
            expected=1,
        )
        self.assertIn("开发任务暂停/继续检查未通过", result.stdout)

    def test_dev_task_handoff_allows_confirmed_continue(self) -> None:
        root = self.make_ready_project()
        self.add_second_dev_task(root, pause_report="Reported", user_continue="Confirmed")
        self.run_tool(
            root,
            "tools/check-dev-task-handoff-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--next-task-id",
            "DEV-002",
            expected=0,
        )
        self.run_tool(
            root,
            "tools/check-workflow-readiness.py",
            "--change-id",
            "CR-001",
            "--change",
            "CR-001-example-change",
            "--task-id",
            "DEV-002",
            "--target-file",
            "backend/src/example_two.py",
            expected=0,
        )

    def test_workflow_next_requirement_gate_suggests_readiness_command(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "REQ_GATE", "REQ_GATE")
        result = self.run_tool(root, "tools/workflow-next.py", expected=0)
        self.assertIn("需求关口", result.stdout)
        self.assertIn("check-gate-readiness.py", result.stdout)
        self.assertIn("--gate requirement", result.stdout)

    def test_workflow_next_design_gate_suggests_readiness_command(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "DESIGN_GATE", "DESIGN_GATE")
        result = self.run_tool(root, "tools/workflow-next.py", expected=0)
        self.assertIn("设计关口", result.stdout)
        self.assertIn("check-gate-readiness.py", result.stdout)
        self.assertIn("--gate design", result.stdout)

    def test_workflow_next_development_suggests_code_and_completion_checks(self) -> None:
        root = self.make_ready_project()
        self.set_state(root, "DEVELOPMENT", "DESIGN_GATE", owner="backend", task="DEV-001")
        result = self.run_tool(root, "tools/workflow-next.py", expected=0)
        self.assertIn("DEVELOPMENT", result.stdout)
        self.assertIn("DEV-001", result.stdout)
        self.assertIn("check-workflow-readiness.py", result.stdout)
        self.assertIn("check-task-completion-readiness.py", result.stdout)

    def test_workflow_next_before_dev002_suggests_handoff_check(self) -> None:
        root = self.make_ready_project()
        self.add_second_dev_task(root, pause_report="Reported", user_continue="Confirmed")
        self.set_state(root, "DEVELOPMENT", "DESIGN_GATE", owner="backend", task="DEV-002")
        result = self.run_tool(root, "tools/workflow-next.py", expected=0)
        self.assertIn("DEV-002", result.stdout)
        self.assertIn("DEV handoff", result.stdout)
        self.assertIn("check-dev-task-handoff-readiness.py", result.stdout)
        self.assertIn("--next-task-id DEV-002", result.stdout)

    def test_workflow_status_reports_missing_state_file_clearly(self) -> None:
        root = self.make_ready_project()
        (root / "workflow" / "state.md").unlink()
        result = self.run_tool(root, "tools/workflow-status.py", expected=1)
        self.assertIn("缺少必要文件: workflow/state.md", result.stdout)

    def test_cluster_readiness_requires_required_agents_cover_startup_order(self) -> None:
        root = self.copy_template()
        cluster_config = root / "workflow" / "cluster.config.yaml"
        text = cluster_config.read_text(encoding="utf-8")
        start = text.index("  required_agents:\n")
        end = text.index("\n\n  agents:\n")
        reduced_required = (
            "  required_agents:\n"
            "    - hr\n"
            "    - ceo\n"
            "    - pl\n"
            "    - pm\n"
            "    - architect\n"
            "    - qa\n"
        )
        cluster_config.write_text(text[:start] + reduced_required + text[end:], encoding="utf-8", newline="\n")

        result = self.run_tool(
            root,
            "tools/check-cluster-readiness.py",
            "--project-root",
            str(root),
            expected=1,
        )
        self.assertIn("required_agents must include every startup_order role", result.stdout)

    def test_cluster_readiness_requires_connectivity_targets_exclude_owner(self) -> None:
        root = self.copy_template()
        cluster_config = root / "workflow" / "cluster.config.yaml"
        text = cluster_config.read_text(encoding="utf-8")
        text = text.replace("  connectivity_test_targets:\n", "  connectivity_test_targets:\n    - hr\n", 1)
        cluster_config.write_text(text, encoding="utf-8", newline="\n")

        result = self.run_tool(
            root,
            "tools/check-cluster-readiness.py",
            "--project-root",
            str(root),
            expected=1,
        )
        self.assertIn("connectivity_test_targets must not include owner_agent", result.stdout)

    def test_cluster_readiness_uses_mapped_agent_workspace_names_by_default(self) -> None:
        root = self.copy_template()
        cluster_root = Path(tempfile.mkdtemp(prefix="openclaw-cluster-fixture-"))
        self.addCleanup(shutil.rmtree, cluster_root, ignore_errors=True)

        for workspace_name in ("hr", "ceo", "pl", "pm", "sa", "qa", "security", "op", "be", "fe", "admin", "ai"):
            write_runtime_workspace(root, cluster_root / "agents" / workspace_name, workspace_name)
        write(cluster_root / "runtime" / "openclaw-agent-plan.md", "# Plan\n")
        write(cluster_root / "runtime" / "openclaw-process-status.md", "# Process\n")

        result = self.run_tool(
            root,
            "tools/check-cluster-readiness.py",
            "--project-root",
            str(root),
            "--cluster-root",
            str(cluster_root),
            expected=0,
        )
        self.assertIn("Cluster readiness: OK", result.stdout)

    def test_cluster_readiness_requires_role_agents_template(self) -> None:
        root = self.copy_template()
        (root / "skills" / "pm" / "AGENTS.md").unlink()

        result = self.run_tool(
            root,
            "tools/check-cluster-readiness.py",
            "--project-root",
            str(root),
            expected=1,
        )
        self.assertIn("Missing skills/pm/AGENTS.md", result.stdout)

    def test_cluster_readiness_rejects_stale_inherent_agent_prompts(self) -> None:
        root = self.copy_template()
        cluster_root = Path(tempfile.mkdtemp(prefix="openclaw-cluster-fixture-"))
        self.addCleanup(shutil.rmtree, cluster_root, ignore_errors=True)

        for workspace_name in ("hr", "ceo", "pl", "pm", "sa", "qa", "security", "op", "be", "fe", "admin", "ai"):
            write_runtime_workspace(root, cluster_root / "agents" / workspace_name, workspace_name)
        write(cluster_root / "agents" / "ceo" / "AGENTS.md", "# stale ceo prompt\n")
        write(cluster_root / "agents" / "hr" / ".openclaw-agent" / "SOUL.md", "# stale hr soul\n")
        write(cluster_root / "runtime" / "openclaw-agent-plan.md", "# Plan\n")
        write(cluster_root / "runtime" / "openclaw-process-status.md", "# Process\n")

        result = self.run_tool(
            root,
            "tools/check-cluster-readiness.py",
            "--project-root",
            str(root),
            "--cluster-root",
            str(cluster_root),
            expected=1,
        )
        self.assertIn("role ceo is stale", result.stdout)
        self.assertIn("role hr is stale", result.stdout)


if __name__ == "__main__":
    unittest.main()
