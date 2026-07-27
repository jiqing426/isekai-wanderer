#!/usr/bin/env python3
"""检查 OpenSpec 驱动的 workflow 关口是否可以记录为 passed。"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


NOT_FILLED = "待填写"
NOT_CONFIRMED = "待确认"
CLARIFICATION_ID_PATTERN = re.compile(r"\bQ-\d+\b")
BLANK_VALUES = {"", "Pending", "pending", "draft", "TBD", "TODO", "-", "none"}
SECTION_ALIASES = {
    "Gate Approvals": ("Gate Approvals", "关口审批", "关口结论"),
    "QA Coverage Review": ("QA Coverage Review", "QA 覆盖复核"),
    "Manual Acceptance Scope": ("Manual Acceptance Scope", "人工验收范围"),
    "Open Questions": ("Open Questions", "待澄清问题", "开放问题"),
    "Why": ("Why", "为什么做", "背景和动机"),
    "What Changes": ("What Changes", "变更内容", "做什么"),
    "Non-Goals": ("Non-Goals", "不做范围", "本次不做"),
    "Success Criteria": ("Success Criteria", "成功标准"),
    "Impact": ("Impact", "影响范围"),
    "Overview": ("Overview", "设计概览", "概览"),
    "Technical Approach": ("Technical Approach", "技术方案"),
    "Technology Decisions": ("Technology Decisions", "技术选型", "技术决策", "选型决策"),
    "Document Sync": ("Document Sync", "Documentation Sync", "Docs Sync", "文档同步", "长期事实同步"),
    "Implementation Tasks": ("Implementation Tasks", "实现任务"),
    "Test-First Scope": ("Test-First Scope", "测试先行范围"),
    "Test Case Artifacts": ("Test Case Artifacts", "测试用例产物"),
    "Red Failure Records": ("Red Failure Records", "Red 失败记录", "实现前失败记录"),
    "Green Pass Records": ("Green Pass Records", "Green 通过记录", "实现后通过记录"),
    "Cannot Automate": ("Cannot Automate", "无法自动化"),
    "CI/CD Evidence Plan": ("CI/CD Evidence Plan", "CI/CD 证据计划", "CI/CD 证据矩阵"),
    "CI/CD Execution Results": ("CI/CD Execution Results", "CI/CD 执行结果", "CI/CD 结果"),
    "Delivery E2E / Runtime Smoke Plan": (
        "Delivery E2E / Runtime Smoke Plan",
        "Delivery E2E Plan",
        "Runtime Smoke Plan",
        "交付级 E2E / 运行冒烟计划",
        "运行时冒烟计划",
    ),
    "Delivery E2E / Runtime Smoke Results": (
        "Delivery E2E / Runtime Smoke Results",
        "Delivery E2E Results",
        "Runtime Smoke Results",
        "交付级 E2E / 运行冒烟结果",
        "运行时冒烟结果",
    ),
    "Browser Interaction E2E Plan": (
        "Browser Interaction E2E Plan",
        "Browser E2E Plan",
        "浏览器交互 E2E 计划",
        "浏览器 E2E 计划",
    ),
    "Browser Interaction E2E Results": (
        "Browser Interaction E2E Results",
        "Browser E2E Results",
        "浏览器交互 E2E 结果",
        "浏览器 E2E 结果",
    ),
}
COVERAGE_ALLOWED_STATUSES = {
    "covered",
    "not_covered",
    "manual_pending",
    "deferred_with_approval",
    "out_of_scope_with_reason",
}
COVERAGE_RELEASE_STATUSES = {
    "covered",
    "deferred_with_approval",
    "out_of_scope_with_reason",
}
DESIGN_DOC_TARGETS = (
    "docs/architecture/architecture.md",
    "docs/api/api.md",
    "docs/database/database.md",
    "docs/security/security.md",
    "docs/decisions/decisions.md",
    "docs/runtime/runtime-contract.md",
)
DOC_SYNCED_STATUSES = {"synced", "updated", "complete", "completed", "已同步", "已更新", "完成"}
DOC_NOT_REQUIRED_STATUSES = {"not required", "n/a", "na", "no change", "无需同步", "不适用", "无变更"}
TECH_DECISION_ACCEPTED_STATUSES = {"accepted", "adopted", "approved", "已采纳", "已接受", "已确认", "采用"}
TECH_DECISION_PENDING_STATUSES = {"proposed", "pending", "open", "待确认", "待定", "候选"}
RUNTIME_REQUIRED_KEYS = {
    "frontend_origin",
    "backend_origin",
    "frontend_port",
    "backend_port",
    "api_base_path",
    "frontend_to_backend_url",
    "vite_proxy_target",
    "health_endpoint",
    "delivery_e2e_command",
    "browser_e2e_command",
    "browser_e2e_user_actions",
    "api_contract_doc",
    "database_contract_doc",
    "persistence_contract",
    "mock_policy",
}
RUNTIME_READY_STATUSES = {
    "defined",
    "ready",
    "approved",
    "accepted",
    "verified",
    "passed",
    "已定义",
    "已确认",
    "已通过",
}
CI_CD_PLAN_STATUSES = {"ready", "approved", "recorded", "planned", "passed", "已计划", "已确认", "已记录"}
CI_CD_PASS_STATUSES = {"passed", "success", "green", "approved", "已通过", "成功"}
CI_CD_SKIP_STATUSES = {"skipped_with_reason", "skipped", "not required", "无需", "不适用"}
DELIVERY_PLAN_STATUSES = {"ready", "approved", "recorded", "planned", "已计划", "已确认", "已记录"}
DELIVERY_PASS_STATUSES = {"passed", "success", "green", "已通过", "成功"}
MOCK_DISABLED_VALUES = {
    "no",
    "false",
    "disabled",
    "none",
    "real",
    "real backend",
    "否",
    "不使用",
    "禁止",
    "关闭",
    "真实后端",
}


def read_text(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def is_filled(value: Optional[str]) -> bool:
    if value is None:
        return False
    text = value.replace("`", "").strip()
    if text in BLANK_VALUES:
        return False
    return NOT_FILLED not in text and NOT_CONFIRMED not in text


def split_markdown_row(line: str) -> List[str]:
    text = line.strip()
    if not text.startswith("|"):
        return []
    return [cell.strip() for cell in text.strip("|").split("|")]


def section_content(content: str, section: str) -> str:
    for section_name in SECTION_ALIASES.get(section, (section,)):
        pattern = re.compile(
            rf"(?ms)^##\s+{re.escape(section_name)}\s*\n(.+?)(?=^##\s+|\Z)"
        )
        match = pattern.search(content)
        if match:
            return match.group(1)
    return ""


def section_spans(content: str, section: str) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    for section_name in SECTION_ALIASES.get(section, (section,)):
        pattern = re.compile(
            rf"(?ms)^##\s+{re.escape(section_name)}\s*\n.+?(?=^##\s+|\Z)"
        )
        spans.extend((match.start(), match.end()) for match in pattern.finditer(content))
    return spans


def position_in_spans(position: int, spans: List[Tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in spans)


def section_has_filled_bullet(content: str, section: str) -> bool:
    for line in section_content(content, section).splitlines():
        match = re.match(r"^\s*-\s*(.+)$", line)
        if match and is_filled(match.group(1)):
            return True
    return False


def bullet_value(content: str, label: str) -> Optional[str]:
    pattern = re.compile(rf"(?m)^-[ \t]*{re.escape(label)}[：:][ \t]*(.*)$")
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def state_value(content: str, label: str) -> Optional[str]:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*(.+?)\s*$", content)
    return match.group(1).strip() if match else None


def normalize_state_ref(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip().replace("\\", "/").lstrip("./").rstrip("/")


def state_ref_matches(value: Optional[str], expected: str) -> bool:
    return normalize_state_ref(value) == normalize_state_ref(expected)


def normalized_status(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip().lower()


def section_rows(content: str, section: str) -> List[Dict[str, str]]:
    text = section_content(content, section)
    rows: List[Dict[str, str]] = []
    headers: Optional[List[str]] = None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cols = split_markdown_row(line)
        if not cols or all(re.fullmatch(r"-+", col) for col in cols):
            continue
        if headers is None:
            headers = cols
            continue
        rows.append({headers[i]: cols[i] for i in range(min(len(headers), len(cols)))})
    return rows


def top_table_rows(content: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    headers: Optional[List[str]] = None
    for line in content.splitlines():
        if re.match(r"^##\s+", line):
            break
        if not line.strip().startswith("|"):
            continue
        cols = split_markdown_row(line)
        if not cols or all(re.fullmatch(r"-+", col) for col in cols):
            continue
        if headers is None:
            headers = cols
            continue
        rows.append({headers[i]: cols[i] for i in range(min(len(headers), len(cols)))})
    return rows


def row_value(row: Optional[Dict[str, str]], *keys: str) -> Optional[str]:
    if row is None:
        return None
    for key in keys:
        if key in row:
            return row[key]
    return None


def cell_refs(value: Optional[str]) -> List[str]:
    if not value:
        return []
    text = value.replace("\\", "/")
    refs = re.findall(r"`([^`]+)`", text)
    refs.extend(re.findall(r"\[[^\]]+\]\(([^)]+)\)", text))
    if not refs:
        refs = re.split(r"[,;\n]", text)
    return [ref.strip() for ref in refs if is_filled(ref.strip())]


def cell_codes(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return re.findall(r"\b[A-Z][A-Z0-9_]*-[A-Z0-9_.-]+\b", value)


def cell_acceptance_ids(value: Optional[str]) -> List[str]:
    return [code for code in cell_codes(value) if code.startswith("AC-")]


def contract_key(value: Optional[str]) -> str:
    text = normalized_cell(value)
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", text, flags=re.UNICODE)
    return text.strip("_")


def mock_is_disabled(value: Optional[str]) -> bool:
    text = normalized_cell(value)
    if text in MOCK_DISABLED_VALUES:
        return True
    return "no mock" in text or "without mock" in text or "禁用 mock" in text or "不使用 mock" in text


def row_skip_with_reason(row: Dict[str, str]) -> bool:
    status = normalized_cell(row_value(row, "状态", "Status", "结果", "Result"))
    if status not in CI_CD_SKIP_STATUSES:
        return False
    text = " ".join(value for value in row.values() if value)
    lowered = normalized_cell(text)
    return (
        "not required:" in lowered
        or "not required：" in lowered
        or "无需" in lowered
        or "不适用" in lowered
        or "无前端" in lowered
        or "no frontend" in lowered
        or "backend-only" in lowered
    )


def row_item_text(row: Dict[str, str]) -> str:
    return row_value(row, "项", "Item") or ""


def resolve_project_ref(project_root: Path, base_dir: Path, ref: str) -> Optional[Path]:
    cleaned = ref.replace("`", "").strip().split("#", 1)[0]
    if not cleaned or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", cleaned):
        return None
    path = Path(cleaned)
    if path.is_absolute():
        return path.resolve()
    normalized = cleaned.replace("\\", "/").lstrip("./")
    root_prefixes = (
        "openspec/",
        "workflow/",
        "docs/",
        "backend/",
        "frontend/",
        "admin/",
        "tests/",
        "tools/",
        "PROJECT.md",
    )
    if normalized.startswith(root_prefixes):
        return (project_root / normalized).resolve()
    return (base_dir / cleaned).resolve()


def looks_like_project_ref(ref: str) -> bool:
    cleaned = ref.replace("`", "").strip().split("#", 1)[0]
    return (
        "/" in cleaned
        or "\\" in cleaned
        or cleaned.startswith(".")
        or bool(re.search(r"\.(md|txt|ya?ml|json|py|ts|tsx|js|jsx)$", cleaned, re.IGNORECASE))
    )


def path_is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def rel_path(project_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def add_if_blank(failures: List[str], value: Optional[str], message: str) -> None:
    if not is_filled(value):
        failures.append(message)


def normalized_cell(value: Optional[str]) -> str:
    return (value or "").replace("`", "").strip().lower()


def priority_value(row: Dict[str, str]) -> str:
    return normalized_cell(row_value(row, "优先级", "Priority")).upper()


def coverage_status(row: Dict[str, str]) -> str:
    return normalized_cell(row_value(row, "覆盖状态", "Coverage Status"))


def check_acceptance_coverage_fields(
    row: Dict[str, str],
    index: int,
    failures: List[str],
    require_release_ready: bool = False,
) -> None:
    acceptance_id = row_value(row, "验收编号", "Acceptance ID") or f"第 {index} 行"
    add_if_blank(failures, row_value(row, "需求编号", "Requirement ID"), f"acceptance.md 第 {index} 行必须填写需求编号")
    priority = priority_value(row)
    if priority not in {"P0", "P1", "P2", "P3"}:
        failures.append(f"acceptance.md 第 {index} 行优先级必须是 P0/P1/P2/P3，当前是：{row_value(row, '优先级', 'Priority')}")

    status = coverage_status(row)
    if status not in COVERAGE_ALLOWED_STATUSES:
        failures.append(f"验收项 {acceptance_id} 覆盖状态必须是 {', '.join(sorted(COVERAGE_ALLOWED_STATUSES))} 之一，当前是：{status or '缺失'}")
        return

    reason = row_value(row, "未覆盖原因", "Uncovered Reason")
    pl_decision = row_value(row, "PL 处理", "PL Decision")
    if priority in {"P0", "P1"}:
        add_if_blank(failures, reason, f"验收项 {acceptance_id} 是 {priority}，必须填写未覆盖原因；已覆盖时写 无")
        add_if_blank(failures, pl_decision, f"验收项 {acceptance_id} 是 {priority}，必须填写 PL 处理")

    if status in {"not_covered", "manual_pending", "deferred_with_approval", "out_of_scope_with_reason"}:
        add_if_blank(failures, reason, f"验收项 {acceptance_id} 覆盖状态为 {status} 时必须填写未覆盖原因")
        add_if_blank(failures, pl_decision, f"验收项 {acceptance_id} 覆盖状态为 {status} 时必须填写 PL 处理")

    if require_release_ready and priority in {"P0", "P1"} and status not in COVERAGE_RELEASE_STATUSES:
        failures.append(
            f"发布关口前，P0/P1 验收项 {acceptance_id} 覆盖状态只能是 covered、deferred_with_approval 或 out_of_scope_with_reason，当前是：{status}"
        )


def qa_review_conclusion_passed(value: Optional[str]) -> bool:
    return normalized_cell(value) in {"passed", "pass", "covered", "accepted", "通过", "已通过", "覆盖成立"}


def check_qa_coverage_review(
    review: Optional[str],
    acceptance_rows: List[Dict[str, str]],
    failures: List[str],
) -> None:
    if review is None:
        failures.append("缺少 review.md，无法检查 QA 覆盖复核")
        return
    rows = section_rows(review, "QA Coverage Review")
    if not rows:
        failures.append("review.md 缺少 QA 覆盖复核表")
        return
    for acceptance in acceptance_rows:
        acceptance_id = row_value(acceptance, "验收编号", "Acceptance ID")
        if not is_filled(acceptance_id):
            continue
        qa_row = next((row for row in rows if row_value(row, "验收编号", "Acceptance ID") == acceptance_id), None)
        if qa_row is None:
            failures.append(f"QA 覆盖复核缺少验收项 {acceptance_id}")
            continue
        add_if_blank(failures, row_value(qa_row, "开发声明", "Development Statement"), f"QA 覆盖复核 {acceptance_id} 必须填写开发声明")
        add_if_blank(failures, row_value(qa_row, "QA 复核", "QA Review"), f"QA 覆盖复核 {acceptance_id} 必须填写 QA 复核")
        conclusion = row_value(qa_row, "结论", "Conclusion")
        add_if_blank(failures, conclusion, f"QA 覆盖复核 {acceptance_id} 必须填写结论")
        status = coverage_status(acceptance)
        if status == "covered" and not qa_review_conclusion_passed(conclusion):
            failures.append(f"验收项 {acceptance_id} 标为 covered 时，QA 覆盖复核结论必须通过，当前是：{conclusion}")
        if status != "covered":
            add_if_blank(failures, row_value(qa_row, "退回对象", "Return To"), f"验收项 {acceptance_id} 非 covered 时，QA 覆盖复核必须填写退回对象或处理对象")


def check_manual_acceptance_scope(review: Optional[str], failures: List[str]) -> None:
    if review is None:
        return
    content = section_content(review, "Manual Acceptance Scope")
    if not content.strip():
        failures.append("review.md 缺少人工验收范围")
        return
    required_labels = ("已覆盖", "明确未覆盖", "已批准暂缓", "不属于本 CR", "需要人工只验证")
    for label in required_labels:
        value = bullet_value(content, label)
        if not is_filled(value):
            failures.append(f"人工验收范围必须填写：{label}")


def check_runtime_contract(project_root: Path, failures: List[str], release_mode: bool = False) -> None:
    path = project_root / "docs" / "runtime" / "runtime-contract.md"
    content = read_text(path)
    if content is None:
        failures.append("缺少 docs/runtime/runtime-contract.md，无法确认前端、后端、API base、代理和交付 E2E 运行拓扑")
        return

    rows = top_table_rows(content)
    if not rows:
        failures.append("docs/runtime/runtime-contract.md 必须包含运行时契约表")
        return

    by_key: Dict[str, Dict[str, str]] = {}
    for row in rows:
        key = contract_key(row_value(row, "Key", "键", "项", "Item"))
        if key:
            by_key[key] = row

    for key in sorted(RUNTIME_REQUIRED_KEYS):
        row = by_key.get(key)
        if row is None:
            failures.append(f"runtime contract 缺少 {key}")
            continue
        value = row_value(row, "Value", "值", "内容")
        status = row_value(row, "Status", "状态")
        evidence = row_value(row, "Evidence / Source", "Evidence", "来源", "依据", "说明")
        add_if_blank(failures, value, f"runtime contract {key} 必须填写值")
        add_if_blank(failures, status, f"runtime contract {key} 必须填写状态")
        add_if_blank(failures, evidence, f"runtime contract {key} 必须填写来源或依据")
        if is_filled(status) and normalized_cell(status) not in RUNTIME_READY_STATUSES:
            failures.append(f"runtime contract {key} 状态必须是 Defined/Ready/Accepted/Verified/Passed，当前是：{status}")

    mock_row = by_key.get("mock_policy")
    if mock_row is not None and not mock_is_disabled(row_value(mock_row, "Value", "值", "内容")):
        failures.append("runtime contract mock_policy 必须明确 Delivery E2E / Release 证据禁止 mock API")

    command_row = by_key.get("delivery_e2e_command")
    command_value = row_value(command_row, "Value", "值", "内容") if command_row else ""
    if is_filled(command_value) and "mock" in normalized_cell(command_value):
        failures.append("runtime contract delivery_e2e_command 不能使用 mock 命令作为交付级 E2E")

    if release_mode:
        for key, row in by_key.items():
            status = normalized_cell(row_value(row, "Status", "状态"))
            if status not in RUNTIME_READY_STATUSES:
                failures.append(f"发布关口前 runtime contract {key} 状态必须已确认或已验证，当前是：{row_value(row, 'Status', '状态')}")


def check_ci_cd_evidence_plan(test_plan: Optional[str], acceptance_ids: Set[str], failures: List[str]) -> None:
    if test_plan is None:
        return
    rows = section_rows(test_plan, "CI/CD Evidence Plan")
    if not rows:
        failures.append("test-plan.md 必须包含 CI/CD 证据计划，定义自动检查或本地 CI 等价命令")
        return
    for index, row in enumerate(rows, start=1):
        for keys, label in (
            (("阶段", "Stage"), "阶段"),
            (("触发时机", "Trigger"), "触发时机"),
            (("命令 / Pipeline", "Command / Pipeline"), "命令 / Pipeline"),
            (("覆盖验收项", "Acceptance IDs"), "覆盖验收项"),
            (("负责人", "Owner"), "负责人"),
            (("记录位置", "Record Location"), "记录位置"),
            (("状态", "Status"), "状态"),
        ):
            add_if_blank(failures, row_value(row, *keys), f"CI/CD 证据计划第 {index} 行必须填写 {label}")
        covered_acs = cell_acceptance_ids(row_value(row, "覆盖验收项", "Acceptance IDs"))
        if acceptance_ids and not covered_acs:
            failures.append(f"CI/CD 证据计划第 {index} 行必须覆盖至少一个验收编号")
        for acceptance_id in covered_acs:
            if acceptance_id not in acceptance_ids:
                failures.append(f"CI/CD 证据计划第 {index} 行覆盖了不存在的验收编号 {acceptance_id}")
        status = normalized_cell(row_value(row, "状态", "Status"))
        if status not in CI_CD_PLAN_STATUSES and status not in CI_CD_SKIP_STATUSES:
            failures.append(f"CI/CD 证据计划第 {index} 行状态必须是 Ready/Approved/Recorded/Planned 或 skipped_with_reason，当前是：{row_value(row, '状态', 'Status')}")


def check_ci_cd_execution_results(test_report: Optional[str], acceptance_ids: Set[str], failures: List[str]) -> None:
    if test_report is None:
        return
    rows = section_rows(test_report, "CI/CD Execution Results")
    if not rows:
        failures.append("test-report.md 必须包含 CI/CD 执行结果")
        return
    has_passed = False
    for index, row in enumerate(rows, start=1):
        for keys, label in (
            (("类型", "Type"), "类型"),
            (("命令 / Pipeline", "Command / Pipeline"), "命令 / Pipeline"),
            (("覆盖验收项", "Acceptance IDs"), "覆盖验收项"),
            (("触发来源", "Trigger Source"), "触发来源"),
            (("结果", "Result"), "结果"),
            (("证据链接 / 日志", "Evidence / Log"), "证据链接 / 日志"),
            (("负责人", "Owner"), "负责人"),
        ):
            add_if_blank(failures, row_value(row, *keys), f"CI/CD 执行结果第 {index} 行必须填写 {label}")
        covered_acs = cell_acceptance_ids(row_value(row, "覆盖验收项", "Acceptance IDs"))
        if acceptance_ids and not covered_acs:
            failures.append(f"CI/CD 执行结果第 {index} 行必须覆盖至少一个验收编号")
        for acceptance_id in covered_acs:
            if acceptance_id not in acceptance_ids:
                failures.append(f"CI/CD 执行结果第 {index} 行覆盖了不存在的验收编号 {acceptance_id}")
        result = normalized_cell(row_value(row, "结果", "Result"))
        if result in CI_CD_PASS_STATUSES:
            has_passed = True
        elif result not in CI_CD_SKIP_STATUSES:
            failures.append(f"CI/CD 执行结果第 {index} 行结果必须是 passed/success/green 或 skipped_with_reason，当前是：{row_value(row, '结果', 'Result')}")
    if not has_passed:
        failures.append("发布关口前必须至少有一条通过的 CI/CD 执行结果，或将相关 AC 标为已批准暂缓/不属于范围")


def check_delivery_smoke_plan(test_plan: Optional[str], acceptance_ids: Set[str], failures: List[str]) -> None:
    if test_plan is None:
        return
    rows = section_rows(test_plan, "Delivery E2E / Runtime Smoke Plan")
    if not rows:
        failures.append("test-plan.md 必须包含 Delivery E2E / Runtime Smoke Plan，验证真实前端入口经过代理访问真实后端")
        return
    for index, row in enumerate(rows, start=1):
        for keys, label in (
            (("任务编号", "Task ID"), "任务编号"),
            (("命令 / 步骤", "Command / Steps"), "命令 / 步骤"),
            (("前端入口", "Frontend URL"), "前端入口"),
            (("后端地址", "Backend URL"), "后端地址"),
            (("API / Proxy Path", "API 路径", "代理路径"), "API / Proxy Path"),
            (("Mock API", "是否 Mock API", "Mock"), "Mock API"),
            (("覆盖验收项", "Acceptance IDs"), "覆盖验收项"),
            (("证据记录位置", "Evidence Target"), "证据记录位置"),
            (("状态", "Status"), "状态"),
        ):
            add_if_blank(failures, row_value(row, *keys), f"Delivery E2E 计划第 {index} 行必须填写 {label}")
        command = row_value(row, "命令 / 步骤", "Command / Steps") or ""
        if "mock" in normalized_cell(command):
            failures.append(f"Delivery E2E 计划第 {index} 行命令不得使用 mock API")
        if not mock_is_disabled(row_value(row, "Mock API", "是否 Mock API", "Mock")):
            failures.append(f"Delivery E2E 计划第 {index} 行 Mock API 必须为 no/否；mock 测试不能作为交付证据")
        covered_acs = cell_acceptance_ids(row_value(row, "覆盖验收项", "Acceptance IDs"))
        if acceptance_ids and not covered_acs:
            failures.append(f"Delivery E2E 计划第 {index} 行必须覆盖至少一个验收编号")
        for acceptance_id in covered_acs:
            if acceptance_id not in acceptance_ids:
                failures.append(f"Delivery E2E 计划第 {index} 行覆盖了不存在的验收编号 {acceptance_id}")
        status = normalized_cell(row_value(row, "状态", "Status"))
        if status not in DELIVERY_PLAN_STATUSES:
            failures.append(f"Delivery E2E 计划第 {index} 行状态必须是 Ready/Approved/Recorded/Planned，当前是：{row_value(row, '状态', 'Status')}")


def check_delivery_smoke_results(test_report: Optional[str], acceptance_ids: Set[str], failures: List[str]) -> None:
    if test_report is None:
        return
    rows = section_rows(test_report, "Delivery E2E / Runtime Smoke Results")
    if not rows:
        failures.append("test-report.md 必须包含 Delivery E2E / Runtime Smoke Results")
        return
    has_passed = False
    for index, row in enumerate(rows, start=1):
        for keys, label in (
            (("命令 / 步骤", "Command / Steps"), "命令 / 步骤"),
            (("前端入口", "Frontend URL"), "前端入口"),
            (("后端地址", "Backend URL"), "后端地址"),
            (("API / Proxy Path", "API 路径", "代理路径"), "API / Proxy Path"),
            (("Mock API", "是否 Mock API", "Mock"), "Mock API"),
            (("覆盖验收项", "Acceptance IDs"), "覆盖验收项"),
            (("结果", "Result"), "结果"),
            (("证据链接 / 日志", "Evidence / Log"), "证据链接 / 日志"),
            (("负责人", "Owner"), "负责人"),
        ):
            add_if_blank(failures, row_value(row, *keys), f"Delivery E2E 结果第 {index} 行必须填写 {label}")
        command = row_value(row, "命令 / 步骤", "Command / Steps") or ""
        if "mock" in normalized_cell(command):
            failures.append(f"Delivery E2E 结果第 {index} 行命令使用了 mock API，不能作为发布证据")
        if not mock_is_disabled(row_value(row, "Mock API", "是否 Mock API", "Mock")):
            failures.append(f"Delivery E2E 结果第 {index} 行 Mock API 必须为 no/否；mock 结果不能作为发布证据")
        covered_acs = cell_acceptance_ids(row_value(row, "覆盖验收项", "Acceptance IDs"))
        if acceptance_ids and not covered_acs:
            failures.append(f"Delivery E2E 结果第 {index} 行必须覆盖至少一个验收编号")
        for acceptance_id in covered_acs:
            if acceptance_id not in acceptance_ids:
                failures.append(f"Delivery E2E 结果第 {index} 行覆盖了不存在的验收编号 {acceptance_id}")
        result = normalized_cell(row_value(row, "结果", "Result"))
        if result in DELIVERY_PASS_STATUSES:
            has_passed = True
        else:
            failures.append(f"Delivery E2E 结果第 {index} 行结果必须是 passed/success/green，当前是：{row_value(row, '结果', 'Result')}")
    if not has_passed:
        failures.append("发布关口前必须至少有一条通过的 Delivery E2E / Runtime Smoke 结果")


def check_browser_e2e_plan(test_plan: Optional[str], acceptance_ids: Set[str], failures: List[str]) -> None:
    if test_plan is None:
        return
    rows = section_rows(test_plan, "Browser Interaction E2E Plan")
    if not rows:
        failures.append("test-plan.md 必须包含 Browser Interaction E2E Plan；存在前端验收项时必须计划真实浏览器用户动作")
        return
    for index, row in enumerate(rows, start=1):
        if row_skip_with_reason(row):
            continue
        for keys, label in (
            (("任务编号", "Task ID"), "任务编号"),
            (("命令 / 步骤", "Command / Steps"), "命令 / 步骤"),
            (("Browser / Tool", "浏览器 / 工具", "浏览器"), "Browser / Tool"),
            (("用户动作", "User Actions", "Actions"), "用户动作"),
            (("前端入口", "Frontend URL"), "前端入口"),
            (("后端地址", "Backend URL"), "后端地址"),
            (("API / Proxy Path", "API 路径", "代理路径"), "API / Proxy Path"),
            (("Mock API", "是否 Mock API", "Mock"), "Mock API"),
            (("覆盖验收项", "Acceptance IDs"), "覆盖验收项"),
            (("证据记录位置", "Evidence Target"), "证据记录位置"),
            (("状态", "Status"), "状态"),
        ):
            add_if_blank(failures, row_value(row, *keys), f"Browser Interaction E2E 计划第 {index} 行必须填写 {label}")
        command = row_value(row, "命令 / 步骤", "Command / Steps") or ""
        if "mock" in normalized_cell(command):
            failures.append(f"Browser Interaction E2E 计划第 {index} 行命令不得使用 mock API")
        if not mock_is_disabled(row_value(row, "Mock API", "是否 Mock API", "Mock")):
            failures.append(f"Browser Interaction E2E 计划第 {index} 行 Mock API 必须为 no/否；mock 测试不能作为发布证据")
        covered_acs = cell_acceptance_ids(row_value(row, "覆盖验收项", "Acceptance IDs"))
        if acceptance_ids and not covered_acs:
            failures.append(f"Browser Interaction E2E 计划第 {index} 行必须覆盖至少一个验收编号")
        for acceptance_id in covered_acs:
            if acceptance_id not in acceptance_ids:
                failures.append(f"Browser Interaction E2E 计划第 {index} 行覆盖了不存在的验收编号 {acceptance_id}")
        status = normalized_cell(row_value(row, "状态", "Status"))
        if status not in DELIVERY_PLAN_STATUSES:
            failures.append(f"Browser Interaction E2E 计划第 {index} 行状态必须是 Ready/Approved/Recorded/Planned，当前是：{row_value(row, '状态', 'Status')}")


def check_browser_e2e_results(test_report: Optional[str], acceptance_ids: Set[str], failures: List[str]) -> None:
    if test_report is None:
        return
    rows = section_rows(test_report, "Browser Interaction E2E Results")
    if not rows:
        failures.append("test-report.md 必须包含 Browser Interaction E2E Results")
        return
    has_passed = False
    has_skip = False
    for index, row in enumerate(rows, start=1):
        if row_skip_with_reason(row):
            has_skip = True
            continue
        for keys, label in (
            (("命令 / 步骤", "Command / Steps"), "命令 / 步骤"),
            (("Browser / Tool", "浏览器 / 工具", "浏览器"), "Browser / Tool"),
            (("用户动作", "User Actions", "Actions"), "用户动作"),
            (("前端入口", "Frontend URL"), "前端入口"),
            (("后端地址", "Backend URL"), "后端地址"),
            (("API / Proxy Path", "API 路径", "代理路径"), "API / Proxy Path"),
            (("Mock API", "是否 Mock API", "Mock"), "Mock API"),
            (("覆盖验收项", "Acceptance IDs"), "覆盖验收项"),
            (("结果", "Result"), "结果"),
            (("证据链接 / 日志", "Evidence / Log"), "证据链接 / 日志"),
            (("负责人", "Owner"), "负责人"),
        ):
            add_if_blank(failures, row_value(row, *keys), f"Browser Interaction E2E 结果第 {index} 行必须填写 {label}")
        command = row_value(row, "命令 / 步骤", "Command / Steps") or ""
        if "mock" in normalized_cell(command):
            failures.append(f"Browser Interaction E2E 结果第 {index} 行命令使用了 mock API，不能作为发布证据")
        if not mock_is_disabled(row_value(row, "Mock API", "是否 Mock API", "Mock")):
            failures.append(f"Browser Interaction E2E 结果第 {index} 行 Mock API 必须为 no/否；mock 结果不能作为发布证据")
        covered_acs = cell_acceptance_ids(row_value(row, "覆盖验收项", "Acceptance IDs"))
        if acceptance_ids and not covered_acs:
            failures.append(f"Browser Interaction E2E 结果第 {index} 行必须覆盖至少一个验收编号")
        for acceptance_id in covered_acs:
            if acceptance_id not in acceptance_ids:
                failures.append(f"Browser Interaction E2E 结果第 {index} 行覆盖了不存在的验收编号 {acceptance_id}")
        result = normalized_cell(row_value(row, "结果", "Result"))
        if result in DELIVERY_PASS_STATUSES:
            has_passed = True
        else:
            failures.append(f"Browser Interaction E2E 结果第 {index} 行结果必须是 passed/success/green，当前是：{row_value(row, '结果', 'Result')}")
    if not has_passed and not has_skip:
        failures.append("发布关口前必须至少有一条通过的 Browser Interaction E2E 结果，或记录 Not Required: <原因> 并由 PL 批准")


def check_design_document_sync(
    project_root: Path,
    change_dir: Path,
    design: str,
    failures: List[str],
) -> None:
    rows = section_rows(design, "Document Sync")
    if not rows:
        failures.append("OpenSpec design.md 必须包含文档同步表，记录设计结论是否已拆分到对应 docs")
        return

    seen_targets: Set[str] = set()
    for index, row in enumerate(rows, start=1):
        target_cell = row_value(row, "Target Doc", "目标文档", "Document", "Doc", "文档")
        status_cell = row_value(row, "Status", "状态")
        notes = row_value(row, "Summary / Evidence", "同步说明", "说明", "Evidence", "Notes", "备注", "原因")

        add_if_blank(failures, target_cell, f"design.md 文档同步表第 {index} 行必须填写目标文档")
        add_if_blank(failures, status_cell, f"design.md 文档同步表第 {index} 行必须填写同步状态")
        add_if_blank(failures, notes, f"design.md 文档同步表第 {index} 行必须填写同步说明或无需同步原因")

        status = normalized_cell(status_cell)
        allowed_statuses = DOC_SYNCED_STATUSES | DOC_NOT_REQUIRED_STATUSES
        if status and status not in allowed_statuses:
            failures.append(
                f"design.md 文档同步表第 {index} 行状态必须是 Synced/已同步 或 Not Required/无需同步，当前是：{status_cell}"
            )

        for ref in cell_refs(target_cell):
            target_path = resolve_project_ref(project_root, change_dir, ref)
            if target_path is None:
                failures.append(f"design.md 文档同步表第 {index} 行目标文档必须是仓库内路径：{ref}")
                continue
            if not target_path.exists():
                failures.append(f"design.md 文档同步表第 {index} 行目标文档不存在：{rel_path(project_root, target_path)}")
                continue
            if not path_is_under(target_path, project_root / "docs"):
                failures.append(f"design.md 文档同步表第 {index} 行目标文档必须位于 docs/ 下：{rel_path(project_root, target_path)}")
                continue
            seen_targets.add(rel_path(project_root, target_path))

    for target in DESIGN_DOC_TARGETS:
        if target not in seen_targets:
            failures.append(f"design.md 文档同步表必须覆盖 {target}，状态为 Synced/已同步 或 Not Required/无需同步")


def check_api_database_mock_contract(project_root: Path, failures: List[str]) -> None:
    api_path = project_root / "docs" / "api" / "api.md"
    database_path = project_root / "docs" / "database" / "database.md"
    api = read_text(api_path)
    database = read_text(database_path)

    if api is None:
        failures.append("缺少 docs/api/api.md，无法检查 API / 数据 / Mock / Runtime 关系")
        return
    if database is None:
        failures.append("缺少 docs/database/database.md，无法检查数据库 / API / Mock / Runtime 关系")
        return

    api_normalized = api.replace("\\", "/").lower()
    database_normalized = database.replace("\\", "/").lower()
    if "docs/runtime/runtime-contract.md" not in api_normalized and "../runtime/runtime-contract.md" not in api_normalized:
        failures.append("docs/api/api.md 必须引用 docs/runtime/runtime-contract.md，说明 API base、proxy 或运行时来源")
    if "docs/database/database.md" not in api_normalized and "../database/database.md" not in api_normalized:
        failures.append("docs/api/api.md 必须引用 docs/database/database.md，说明 API 与数据来源关系")
    if "mock" not in api_normalized:
        failures.append("docs/api/api.md 必须说明 mock API 不能作为 Delivery E2E / Release 证据")
    if "docs/api/api.md" not in database_normalized and "../api/api.md" not in database_normalized:
        failures.append("docs/database/database.md 必须引用 docs/api/api.md，说明数据只能通过 API 边界访问")
    if "docs/runtime/runtime-contract.md" not in database_normalized and "../runtime/runtime-contract.md" not in database_normalized:
        failures.append("docs/database/database.md 必须引用 docs/runtime/runtime-contract.md，说明持久化和运行配置关系")
    if "mock" not in database_normalized:
        failures.append("docs/database/database.md 必须说明 mock/fixture/seed data 不能作为发布真实数据来源")


def check_technology_decisions(
    project_root: Path,
    change_dir: Path,
    design: str,
    failures: List[str],
) -> None:
    rows = section_rows(design, "Technology Decisions")
    if not rows:
        failures.append("OpenSpec design.md 必须包含 Technology Decisions / 技术选型表；没有新增选型时也要记录 Not Required")
        return

    for index, row in enumerate(rows, start=1):
        item = row_value(row, "Decision", "Item", "选型项", "技术项", "决策")
        selected = row_value(row, "Selected", "Choice", "选择", "方案")
        status_cell = row_value(row, "Status", "状态")
        evidence = row_value(row, "Evidence", "ADR / Confirmation", "确认依据", "依据", "记录")

        add_if_blank(failures, item, f"技术选型表第 {index} 行必须填写选型项")
        add_if_blank(failures, selected, f"技术选型表第 {index} 行必须填写候选或选择")
        add_if_blank(failures, status_cell, f"技术选型表第 {index} 行必须填写状态")
        add_if_blank(failures, evidence, f"技术选型表第 {index} 行必须填写 ADR 或人工确认依据")

        status = normalized_cell(status_cell)
        if status in TECH_DECISION_PENDING_STATUSES:
            failures.append(f"技术选型表第 {index} 行仍是 {status_cell}，不得通过 DESIGN_GATE；必须先获得用户/PL/Architect 明确接受")
            continue
        if status not in TECH_DECISION_ACCEPTED_STATUSES and status not in DOC_NOT_REQUIRED_STATUSES:
            failures.append(f"技术选型表第 {index} 行状态必须是 Accepted/已确认、Proposed/待确认 或 Not Required/无需选型，当前是：{status_cell}")
            continue
        if status in DOC_NOT_REQUIRED_STATUSES:
            continue

        evidence_text = evidence or ""
        if not re.search(r"\bADR-\d+\b|docs/decisions/|人工确认|用户确认|PL 确认|Architect 确认|已确认|Confirmed by user|Confirmed by PL", evidence_text, re.IGNORECASE):
            failures.append(f"技术选型表第 {index} 行已采纳选型必须引用 ADR 或明确的人工确认记录（用户/PL/Architect）")
        for ref in cell_refs(evidence_text):
            if not looks_like_project_ref(ref):
                continue
            evidence_path = resolve_project_ref(project_root, change_dir, ref)
            if evidence_path is None:
                continue
            if not evidence_path.exists():
                failures.append(f"技术选型表第 {index} 行引用的确认依据不存在：{rel_path(project_root, evidence_path)}")
                continue
            if "docs/decisions/" in rel_path(project_root, evidence_path):
                evidence_content = read_text(evidence_path) or ""
                if not re.search(r"(?im)^状态[：:]\s*Accepted\b|^Status[：:]\s*Accepted\b|^状态[：:]\s*已采纳\b", evidence_content):
                    failures.append(f"技术选型表第 {index} 行引用的 ADR 不是 Accepted/已采纳：{rel_path(project_root, evidence_path)}")
                # ADR 必须包含人工确认（用户/PL），Agent 不得自行 Accepted
                if not re.search(r"人工确认|用户确认|PL 确认|Architect 确认|confirmed by user|confirmed by PL|approved by user|approved by PL|人工审批|用户审批", evidence_content, re.IGNORECASE):
                    failures.append(f"技术选型表第 {index} 行引用的 ADR 必须包含人工确认记录，当前 ADR 仅由 Agent 自行决策，未经人工审批：{rel_path(project_root, evidence_path)}")


def find_openspec_change_dir(project_root: Path, change_id: str, change: Optional[str]) -> Optional[Path]:
    changes_dir = project_root / "openspec" / "changes"
    if change:
        candidate = changes_dir / change
        return candidate if candidate.is_dir() else None
    if not changes_dir.exists():
        return None
    exact = changes_dir / change_id
    if exact.is_dir():
        return exact
    matches = sorted(
        path for path in changes_dir.iterdir()
        if path.is_dir() and path.name.startswith(f"{change_id}-")
    )
    return matches[0] if matches else None


def markdown_files(path: Path) -> List[Path]:
    if not path.exists():
        return []
    return sorted(p for p in path.rglob("*.md") if p.is_file())


def has_heading(content: str, pattern: str) -> bool:
    return re.search(pattern, content, flags=re.MULTILINE) is not None


def check_open_questions(content: str, source_name: str, failures: List[str]) -> None:
    for row in section_rows(content, "Open Questions"):
        status = row_value(row, "Status", "状态") or ""
        question_id = row_value(row, "ID", "Id", "编号") or ""
        blocks = row_value(row, "Blocks MVP", "是否阻塞 MVP", "阻塞 MVP") or ""
        answer = row_value(row, "User Answer", "用户回答") or ""
        resolution = row_value(row, "Resolution", "处理结论") or ""
        shown = row_value(
            row,
            "Shown to User",
            "Displayed to User",
            "User Visible",
            "用户可见",
            "用户展示",
            "展示状态",
            "确认记录",
            "交互记录",
        ) or ""
        question = row_value(row, "Question", "问题") or ""

        if not is_filled(question):
            failures.append(f"{source_name} 的待澄清问题必须填写问题内容")
            continue
        if not CLARIFICATION_ID_PATTERN.search(" ".join([question_id, *row.values()])):
            failures.append(f"{source_name} 的待澄清问题必须包含 Q-001 这类编号")
        if not is_filled(shown):
            failures.append(f"{source_name} 的待澄清问题必须记录已向用户展示或确认的交互证据")

        status_open = status.strip().lower() in {"", "open", "pending", "待确认"}
        clearly_non_blocking = blocks.strip().lower() in {
            "否",
            "no",
            "false",
            "non-blocking",
            "非阻塞",
            "不阻塞",
            "暂缓",
        }
        handled = is_filled(answer) or is_filled(resolution)
        if status_open and not handled:
            if clearly_non_blocking:
                failures.append(
                    f"{source_name} 存在非阻塞但仍 Open 的待澄清问题，必须记录用户回答或暂缓结论"
                )
            else:
                failures.append(
                    f"{source_name} 存在阻塞 MVP 的待澄清问题，必须先回答、暂缓或标记为非阻塞"
                )
        if not status_open and not handled:
            failures.append(
                f"{source_name} 已关闭的待澄清问题必须记录用户回答或处理结论"
            )


def clarification_ids(content: str) -> Set[str]:
    ids: Set[str] = set()
    for row in section_rows(content, "Open Questions"):
        for value in row.values():
            ids.update(CLARIFICATION_ID_PATTERN.findall(value))
    return ids


def check_untracked_pending_confirmations(
    content: str,
    source_name: str,
    known_clarification_ids: Set[str],
    failures: List[str],
) -> None:
    open_question_spans = section_spans(content, "Open Questions")
    for match in re.finditer(r"(?m)^.*待确认.*$", content):
        if position_in_spans(match.start(), open_question_spans):
            continue
        line = match.group(0).strip()
        if not line:
            continue
        referenced_ids = set(CLARIFICATION_ID_PATTERN.findall(line))
        if not referenced_ids:
            failures.append(f"{source_name} 存在未关联待澄清问题的待确认：{line[:120]}")
            continue
        unknown_ids = sorted(referenced_ids - known_clarification_ids)
        if unknown_ids:
            ids = ", ".join(unknown_ids)
            failures.append(f"{source_name} 引用了不存在的待澄清问题编号：{ids}")


def gate_conclusion(review: Optional[str], gate: str) -> Optional[str]:
    if review is None:
        return None
    for row in section_rows(review, "Gate Approvals"):
        if row_value(row, "Gate", "关口") == gate:
            return row_value(row, "Conclusion", "结论")
    return None


def stage_conclusion(review: Optional[str], stage: str) -> Optional[str]:
    if review is None:
        return None
    for row in section_rows(review, "阶段结论"):
        if row_value(row, "阶段", "Stage") == stage:
            return row_value(row, "结论", "Conclusion")
    return None


def check_gate_state(
    project_root: Path,
    change_id: str,
    change_dir: Path,
    gate: str,
    failures: List[str],
) -> None:
    state = read_text(project_root / "workflow" / "state.md")
    if state is None:
        failures.append("缺少 workflow/state.md")
        return

    expected_stage_by_gate = {
        "requirement": "REQ_GATE",
        "design": "DESIGN_GATE",
        "release": "RELEASE_GATE",
    }
    expected_stage = expected_stage_by_gate[gate]
    actual_stage = state_value(state, "当前阶段")
    actual_gate = state_value(state, "当前关口")
    if actual_stage != expected_stage:
        failures.append(f"workflow/state.md 当前阶段必须是 {expected_stage}，当前是：{actual_stage}")
    if actual_gate != expected_stage:
        failures.append(f"workflow/state.md 当前关口必须是 {expected_stage}，当前是：{actual_gate}")

    expected_evidence = f"workflow/changes/{change_id}"
    active_evidence = state_value(state, "当前变更")
    if not state_ref_matches(active_evidence, expected_evidence):
        failures.append(f"当前 workflow 变更必须是 {expected_evidence}，当前是：{active_evidence}")

    expected_openspec_change = f"openspec/changes/{change_dir.name}"
    active_openspec_change = state_value(state, "当前 OpenSpec Change")
    if not state_ref_matches(active_openspec_change, expected_openspec_change):
        failures.append(f"当前 OpenSpec Change 必须是 {expected_openspec_change}，当前是：{active_openspec_change}")


def check_requirement_preconditions(project_root: Path, change_id: str, failures: List[str]) -> None:
    review = read_text(project_root / "workflow" / "changes" / change_id / "review.md")
    if review is None:
        failures.append(f"缺少 workflow/changes/{change_id}/review.md")
        return

    init_conclusion = gate_conclusion(review, "INIT")
    if init_conclusion != "passed":
        failures.append(f"进入需求关口前，INIT 结论必须是 passed，当前是：{init_conclusion}")

    triage_conclusion = stage_conclusion(review, "TRIAGE")
    if normalized_status(triage_conclusion) not in {"ready", "submitted", "passed"}:
        failures.append(
            f"进入需求关口前，TRIAGE 阶段结论必须是 ready、submitted 或 passed，当前是：{triage_conclusion}"
        )


def check_requirement_files(
    project_root: Path,
    change_id: str,
    change_dir: Path,
    failures: List[str],
) -> Optional[str]:
    change_path = project_root / "workflow" / "changes" / change_id / "change.md"
    acceptance_path = project_root / "workflow" / "changes" / change_id / "acceptance.md"
    change = read_text(change_path)
    acceptance = read_text(acceptance_path)
    pending_confirmation_sources: List[Tuple[str, str]] = []
    known_clarification_ids: Set[str] = set()

    if change is None:
        failures.append(f"缺少 workflow/changes/{change_id}/change.md")
    else:
        pending_confirmation_sources.append((f"workflow/changes/{change_id}/change.md", change))
        add_if_blank(failures, bullet_value(change, "目标"), "change.md 必须填写目标")
        add_if_blank(failures, bullet_value(change, "成功标准"), "change.md 必须填写成功标准")

    proposal_path = change_dir / "proposal.md"
    proposal = read_text(proposal_path)
    if proposal is None:
        failures.append(f"缺少 {proposal_path.relative_to(project_root)}")
    else:
        pending_confirmation_sources.append((str(proposal_path.relative_to(project_root)), proposal))
        known_clarification_ids.update(clarification_ids(proposal))
        for section in ("Why", "What Changes", "Non-Goals", "Success Criteria", "Impact"):
            if not section_content(proposal, section).strip():
                failures.append(f"proposal.md 必须包含 {section} / 中文等价章节")
        if not section_has_filled_bullet(proposal, "Why"):
            failures.append("proposal.md 必须填写为什么做")
        if not section_has_filled_bullet(proposal, "What Changes"):
            failures.append("proposal.md 必须填写变更内容")
        if not section_has_filled_bullet(proposal, "Success Criteria"):
            failures.append("proposal.md 必须填写成功标准")
        check_open_questions(proposal, "proposal.md", failures)

    spec_dir = change_dir / "specs"
    specs = markdown_files(spec_dir)
    if not specs:
        failures.append(f"缺少 {spec_dir.relative_to(project_root)}/**/*.md")
    else:
        for spec_path in specs:
            spec = read_text(spec_path) or ""
            pending_confirmation_sources.append((str(spec_path.relative_to(project_root)), spec))
            known_clarification_ids.update(clarification_ids(spec))
            if not has_heading(spec, r"^###\s+Requirement:"):
                failures.append(f"{spec_path.relative_to(project_root)} 必须至少包含一个 '### Requirement:' 标题")
            if not has_heading(spec, r"^####\s+Scenario:"):
                failures.append(f"{spec_path.relative_to(project_root)} 必须至少包含一个 '#### Scenario:' 标题")
            check_open_questions(spec, str(spec_path.relative_to(project_root)), failures)

    if acceptance is None:
        failures.append(f"缺少 workflow/changes/{change_id}/acceptance.md")
        return None
    pending_confirmation_sources.append((f"workflow/changes/{change_id}/acceptance.md", acceptance))

    rows = top_table_rows(acceptance)
    if not rows:
        failures.append("acceptance.md 必须至少包含一行验收追踪")
    acceptance_ids: Set[str] = set()
    for index, row in enumerate(rows, start=1):
        acceptance_id = row_value(row, "验收编号")
        add_if_blank(failures, acceptance_id, f"acceptance.md 第 {index} 行必须填写验收编号")
        check_acceptance_coverage_fields(row, index, failures)
        if is_filled(acceptance_id):
            if acceptance_id in acceptance_ids:
                failures.append(f"acceptance.md 第 {index} 行重复使用验收编号 {acceptance_id}")
            acceptance_ids.add(acceptance_id)
        source_spec = row_value(row, "来源规格")
        add_if_blank(failures, source_spec, f"acceptance.md 第 {index} 行必须填写来源规格")
        spec_refs = cell_refs(source_spec)
        if source_spec is not None and not spec_refs:
            failures.append(f"acceptance.md 第 {index} 行来源规格必须引用具体 spec 文件")
        for ref in spec_refs:
            spec_path = resolve_project_ref(project_root, acceptance_path.parent, ref)
            if spec_path is None:
                failures.append(f"acceptance.md 第 {index} 行来源规格必须是仓库内路径：{ref}")
                continue
            if not spec_path.exists():
                failures.append(f"acceptance.md 第 {index} 行来源规格不存在：{rel_path(project_root, spec_path)}")
                continue
            if not path_is_under(spec_path, change_dir / "specs"):
                failures.append(
                    f"acceptance.md 第 {index} 行来源规格必须位于 {rel_path(project_root, change_dir / 'specs')} 下：{rel_path(project_root, spec_path)}"
                )
        add_if_blank(failures, row_value(row, "验收标准"), f"acceptance.md 第 {index} 行必须填写验收标准")

    for source_name, content in pending_confirmation_sources:
        check_untracked_pending_confirmations(
            content,
            source_name,
            known_clarification_ids,
            failures,
        )

    return acceptance


def check_design_files(
    project_root: Path,
    change_id: str,
    change_dir: Path,
    acceptance: Optional[str],
    failures: List[str],
    release_mode: bool = False,
) -> None:
    review = read_text(project_root / "workflow" / "changes" / change_id / "review.md")
    conclusion = gate_conclusion(review, "REQ_GATE")
    if conclusion != "passed":
        failures.append(f"进入设计关口前，REQ_GATE 结论必须是 passed，当前是：{conclusion}")

    design = read_text(change_dir / "design.md")
    if design is None:
        failures.append(f"缺少 {(change_dir / 'design.md').relative_to(project_root)}")
    else:
        if not section_has_filled_bullet(design, "Overview"):
            failures.append("OpenSpec design.md 必须填写设计概览")
        if not section_has_filled_bullet(design, "Technical Approach"):
            failures.append("OpenSpec design.md 必须填写技术方案")
        check_technology_decisions(project_root, change_dir, design, failures)
        check_design_document_sync(project_root, change_dir, design, failures)
    check_runtime_contract(project_root, failures, release_mode=release_mode)
    check_api_database_mock_contract(project_root, failures)

    tasks = read_text(change_dir / "tasks.md")
    acceptance_rows = top_table_rows(acceptance) if acceptance is not None else []
    acceptance_ids = {
        value
        for value in (row_value(row, "验收编号") for row in acceptance_rows)
        if is_filled(value)
    }
    task_ids: Set[str] = set()
    if tasks is None:
        failures.append(f"缺少 {(change_dir / 'tasks.md').relative_to(project_root)}")
    else:
        rows = section_rows(tasks, "Implementation Tasks")
        if not rows:
            failures.append("OpenSpec tasks.md 必须包含实现任务表")
        for index, row in enumerate(rows, start=1):
            task_id = row_value(row, "Task ID", "任务编号")
            add_if_blank(failures, task_id, f"OpenSpec tasks 第 {index} 行必须填写任务编号")
            if is_filled(task_id):
                if task_id in task_ids:
                    failures.append(f"OpenSpec tasks 第 {index} 行重复使用任务编号 {task_id}")
                task_ids.add(task_id)
            add_if_blank(failures, row_value(row, "Owner Agent", "负责人 Agent"), f"OpenSpec tasks 第 {index} 行必须填写负责人 Agent")
            requirement_ref = row_value(row, "Requirement / AC", "关联验收项")
            add_if_blank(failures, requirement_ref, f"OpenSpec tasks 第 {index} 行必须填写 Requirement 或 AC 关联")
            excluded_ref = row_value(row, "Excluded AC", "不覆盖验收项")
            if excluded_ref is None or not is_filled(excluded_ref):
                failures.append(f"OpenSpec tasks 第 {index} 行必须填写不覆盖验收项；无不覆盖项时写 无")
            referenced_acs = cell_acceptance_ids(requirement_ref)
            if acceptance_ids and not referenced_acs:
                failures.append(f"OpenSpec tasks 第 {index} 行必须至少关联一个验收编号")
            for acceptance_id in referenced_acs:
                if acceptance_id not in acceptance_ids:
                    failures.append(f"OpenSpec tasks 第 {index} 行引用了不存在的验收编号 {acceptance_id}")
            add_if_blank(failures, row_value(row, "Allowed Write Scope", "允许写入范围"), f"OpenSpec tasks 第 {index} 行必须填写允许写入范围")
            add_if_blank(failures, row_value(row, "Test Case Artifact", "测试用例产物"), f"OpenSpec tasks 第 {index} 行必须填写测试用例产物")
            add_if_blank(failures, row_value(row, "Verification", "验证方式"), f"OpenSpec tasks 第 {index} 行必须填写验证方式")
            add_if_blank(failures, row_value(row, "Rollback / Revert Plan", "回滚 / 撤销方案"), f"OpenSpec tasks 第 {index} 行必须填写回滚或撤销方案")
            status = row_value(row, "Status", "状态")
            allowed_task_statuses = {"Ready", "Approved"}
            if release_mode:
                allowed_task_statuses.update({"Implemented", "Done", "Delivered", "Completed"})
            if status not in allowed_task_statuses:
                allowed = ", ".join(sorted(allowed_task_statuses))
                failures.append(f"OpenSpec tasks 第 {index} 行状态必须是 {allowed} 之一，当前是：{status}")

    test_plan = read_text(project_root / "workflow" / "changes" / change_id / "test-plan.md")
    if test_plan is None:
        failures.append(f"缺少 workflow/changes/{change_id}/test-plan.md")
    else:
        if not section_has_filled_bullet(test_plan, "Test-First Scope"):
            failures.append("test-plan.md 必须填写测试先行范围")
        rows = section_rows(test_plan, "Test Case Artifacts")
        if not rows:
            failures.append("test-plan.md 必须至少包含一行测试用例产物")
        for index, row in enumerate(rows, start=1):
            task_id = row_value(row, "任务编号", "Task ID")
            add_if_blank(failures, task_id, f"测试用例产物第 {index} 行必须填写任务编号")
            if is_filled(task_id) and task_ids and task_id not in task_ids:
                failures.append(f"测试用例产物第 {index} 行引用了不存在的任务编号 {task_id}")
            add_if_blank(failures, row_value(row, "测试用例产物", "Test Case Artifact"), f"测试用例产物第 {index} 行必须填写产物")
            coverage = row_value(row, "覆盖验收项", "Acceptance IDs")
            add_if_blank(failures, coverage, f"测试用例产物第 {index} 行必须填写覆盖验收项")
            covered_acs = cell_acceptance_ids(coverage)
            if acceptance_ids and not covered_acs:
                failures.append(f"测试用例产物第 {index} 行必须覆盖至少一个验收编号")
            for acceptance_id in covered_acs:
                if acceptance_id not in acceptance_ids:
                    failures.append(f"测试用例产物第 {index} 行覆盖了不存在的验收编号 {acceptance_id}")
            status = row_value(row, "状态", "Status")
            if status not in {"Ready", "Approved", "Recorded"}:
                failures.append(f"设计关口前，测试用例产物第 {index} 行状态必须是 Ready、Approved 或 Recorded，当前是：{status}")
        red_rows = section_rows(test_plan, "Red Failure Records")
        if not red_rows:
            failures.append("test-plan.md 必须包含 Red 失败记录表；记录内容可以到 DEVELOPMENT 写代码前再补")
        for index, row in enumerate(red_rows, start=1):
            task_id = row_value(row, "任务编号", "Task ID")
            if is_filled(task_id) and task_ids and task_id not in task_ids:
                failures.append(f"Red 记录第 {index} 行引用了不存在的任务编号 {task_id}")
        check_ci_cd_evidence_plan(test_plan, acceptance_ids, failures)
        check_delivery_smoke_plan(test_plan, acceptance_ids, failures)
        check_browser_e2e_plan(test_plan, acceptance_ids, failures)

    if acceptance is not None:
        for index, row in enumerate(top_table_rows(acceptance), start=1):
            add_if_blank(failures, row_value(row, "设计落点"), f"设计关口前，acceptance.md 第 {index} 行必须填写设计落点")
            task_ref = row_value(row, "OpenSpec Task", "开发任务", "绑定任务")
            add_if_blank(failures, task_ref, f"设计关口前，acceptance.md 第 {index} 行必须填写 OpenSpec task")
            referenced_tasks = [code for code in cell_codes(task_ref) if not code.startswith("AC-")]
            if task_ids and not referenced_tasks:
                failures.append(f"acceptance.md 第 {index} 行必须至少引用一个 OpenSpec task 编号")
            for task_id in referenced_tasks:
                if task_id not in task_ids:
                    failures.append(f"acceptance.md 第 {index} 行引用了不存在的 OpenSpec task 编号 {task_id}")
            add_if_blank(failures, row_value(row, "测试用例 / 验证命令", "测试证据"), f"设计关口前，acceptance.md 第 {index} 行必须填写测试用例或验证引用")
            status = row_value(row, "状态")
            allowed_statuses = {"Designed", "Ready", "Approved"}
            if release_mode:
                allowed_statuses.update({"Verified", "Blocked"})
            if status not in allowed_statuses:
                allowed = ", ".join(sorted(allowed_statuses))
                failures.append(f"acceptance.md 第 {index} 行状态必须是 {allowed} 之一，当前是：{status}")


def check_release_files(project_root: Path, change_id: str, failures: List[str]) -> None:
    review = read_text(project_root / "workflow" / "changes" / change_id / "review.md")
    conclusion = gate_conclusion(review, "DESIGN_GATE")
    if conclusion != "passed":
        failures.append(f"进入发布关口前，DESIGN_GATE 结论必须是 passed，当前是：{conclusion}")

    acceptance = read_text(project_root / "workflow" / "changes" / change_id / "acceptance.md")
    acceptance_rows: List[Dict[str, str]] = []
    if acceptance is None:
        failures.append(f"缺少 workflow/changes/{change_id}/acceptance.md")
    else:
        acceptance_rows = top_table_rows(acceptance)
        for index, row in enumerate(acceptance_rows, start=1):
            check_acceptance_coverage_fields(row, index, failures, require_release_ready=True)
            status = row_value(row, "状态")
            notes = row_value(row, "备注")
            if status == "Blocked" and is_filled(notes):
                continue
            if status != "Verified":
                failures.append(f"发布关口前，acceptance.md 第 {index} 行必须是 Verified，或是带备注的 Blocked；当前是：{status}")
            elif not is_filled(row_value(row, "测试用例 / 验证命令", "测试证据")):
                failures.append(f"发布关口前，acceptance.md 第 {index} 行必须填写测试用例或验证命令")

    check_qa_coverage_review(review, acceptance_rows, failures)
    check_manual_acceptance_scope(review, failures)

    test_report_text: Optional[str] = None
    for filename, label in (
        ("test-report.md", "测试结论"),
        ("security-review.md", "审查结论"),
    ):
        content = read_text(project_root / "workflow" / "changes" / change_id / filename)
        if content is None:
            failures.append(f"缺少 workflow/changes/{change_id}/{filename}")
            continue
        if filename == "test-report.md":
            test_report_text = content
        row = next((r for r in top_table_rows(content) if row_value(r, "项") == label), None)
        add_if_blank(failures, row_value(row, "内容"), f"{filename} 必须填写 {label}")
    acceptance_id_set = {
        value
        for value in (row_value(row, "验收编号", "Acceptance ID") for row in acceptance_rows)
        if is_filled(value)
    }
    check_ci_cd_execution_results(test_report_text, acceptance_id_set, failures)
    check_delivery_smoke_results(test_report_text, acceptance_id_set, failures)
    check_browser_e2e_results(test_report_text, acceptance_id_set, failures)

    deploy_plan = read_text(project_root / "workflow" / "changes" / change_id / "deploy-plan.md")
    if deploy_plan is None:
        failures.append(f"缺少 workflow/changes/{change_id}/deploy-plan.md")
    else:
        if not section_rows(deploy_plan, "发布步骤") and not section_rows(deploy_plan, "部署步骤"):
            failures.append("deploy-plan.md 必须包含发布步骤或部署步骤")
        if not section_has_filled_bullet(deploy_plan, "回滚方案"):
            failures.append("deploy-plan.md 必须填写回滚方案")
        if not section_has_filled_bullet(deploy_plan, "监控方案"):
            failures.append("deploy-plan.md 必须填写监控方案")
        precheck_rows = section_rows(deploy_plan, "发布前检查")
        ci_cd_row = next(
            (
                row for row in precheck_rows
                if "ci" in normalized_cell(row_value(row, "项", "Item"))
                or "cd" in normalized_cell(row_value(row, "项", "Item"))
                or "自动" in (row_value(row, "项", "Item") or "")
            ),
            None,
        )
        if ci_cd_row is None:
            failures.append("deploy-plan.md 发布前检查必须包含 CI/CD 结果项")
        else:
            status = normalized_cell(row_value(ci_cd_row, "状态", "Status"))
            if status not in CI_CD_PASS_STATUSES and status not in CI_CD_SKIP_STATUSES:
                failures.append(f"deploy-plan.md 发布前检查的 CI/CD 状态必须是 passed/approved 或 skipped_with_reason，当前是：{row_value(ci_cd_row, '状态', 'Status')}")
            add_if_blank(failures, row_value(ci_cd_row, "说明", "Notes"), "deploy-plan.md 发布前检查的 CI/CD 结果必须填写说明")
        delivery_row = next(
            (
                row for row in precheck_rows
                if (
                    "delivery" in normalized_cell(row_item_text(row))
                    or "runtime" in normalized_cell(row_item_text(row))
                    or "交付" in row_item_text(row)
                    or "运行" in row_item_text(row)
                )
                and "browser" not in normalized_cell(row_item_text(row))
                and "浏览器" not in row_item_text(row)
                and "交互" not in row_item_text(row)
            ),
            None,
        )
        if delivery_row is None:
            failures.append("deploy-plan.md 发布前检查必须包含 Delivery E2E / Runtime Smoke 结果项")
        else:
            status = normalized_cell(row_value(delivery_row, "状态", "Status"))
            if status not in DELIVERY_PASS_STATUSES:
                failures.append(f"deploy-plan.md 发布前检查的 Delivery E2E / Runtime Smoke 状态必须是 passed/success/green，当前是：{row_value(delivery_row, '状态', 'Status')}")
            add_if_blank(failures, row_value(delivery_row, "说明", "Notes"), "deploy-plan.md 发布前检查的 Delivery E2E / Runtime Smoke 必须填写说明")
        browser_row = next(
            (
                row for row in precheck_rows
                if (
                    "browser" in normalized_cell(row_item_text(row))
                    or "浏览器" in row_item_text(row)
                    or "交互" in row_item_text(row)
                )
                and (
                    "e2e" in normalized_cell(row_item_text(row))
                    or "interaction" in normalized_cell(row_item_text(row))
                    or "交互" in row_item_text(row)
                )
            ),
            None,
        )
        if browser_row is None:
            failures.append("deploy-plan.md 发布前检查必须包含 Browser Interaction E2E 结果项")
        else:
            status = normalized_cell(row_value(browser_row, "状态", "Status"))
            if status not in DELIVERY_PASS_STATUSES and not row_skip_with_reason(browser_row):
                failures.append(f"deploy-plan.md 发布前检查的 Browser Interaction E2E 状态必须是 passed/success/green 或 skipped_with_reason，当前是：{row_value(browser_row, '状态', 'Status')}")
            add_if_blank(failures, row_value(browser_row, "说明", "Notes"), "deploy-plan.md 发布前检查的 Browser Interaction E2E 必须填写说明")

    logs_dir = project_root / "workflow" / "changes" / change_id / "logs" / "agent-runs"
    if not logs_dir.exists() or not any(logs_dir.glob("*.md")):
        failures.append(f"workflow/changes/{change_id}/logs/agent-runs/ 必须至少包含一份 Agent Run Log")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="关口结论写入 passed 前的 readiness 检查。")
    parser.add_argument("--project-root", default="", help="项目根目录，默认从 tools/ 推断。")
    parser.add_argument("--change-id", required=True, help="workflow CR 编号，例如 CR-001。")
    parser.add_argument("--change", default="", help="OpenSpec change 目录名；未传时按 CR 前缀查找。")
    parser.add_argument("--gate", required=True, choices=["requirement", "design", "release"], help="要检查的关口。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    failures: List[str] = []

    change_dir = find_openspec_change_dir(project_root, args.change_id, args.change or None)
    if change_dir is None:
        change_ref = args.change or f"{args.change_id}-<change-name>"
        failures.append(f"缺少 openspec/changes/{change_ref}/")
        acceptance = None
    else:
        check_gate_state(project_root, args.change_id, change_dir, args.gate, failures)
        if args.gate == "requirement":
            check_requirement_preconditions(project_root, args.change_id, failures)
        acceptance = check_requirement_files(project_root, args.change_id, change_dir, failures)
        if args.gate == "design":
            check_design_files(project_root, args.change_id, change_dir, acceptance, failures)
        if args.gate == "release":
            check_design_files(project_root, args.change_id, change_dir, acceptance, failures, release_mode=True)
            check_release_files(project_root, args.change_id, failures)

    if failures:
        print("关口检查：未通过")
        print(f"关口：{args.gate}")
        for failure in failures:
            print(f"- {failure}")
        print(
            "Agent 不得把关口标记为 passed，也不得推进 workflow/state.md。"
            "请生成缺失草案、请求确认，或记录 returned。"
        )
        return 1

    print("关口检查：通过")
    print(f"关口 {args.gate} 在捕获人工确认后可以记录为 passed。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
