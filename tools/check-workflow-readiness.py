#!/usr/bin/env python3
"""检查某个 OpenSpec 任务是否允许修改业务代码。"""

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


NOT_FILLED = "待填写"
NOT_CONFIRMED = "待确认"
SECTION_ALIASES = {
    "Gate Approvals": ("Gate Approvals", "关口审批", "关口结论"),
    "Implementation Tasks": ("Implementation Tasks", "实现任务"),
    "Test Case Artifacts": ("Test Case Artifacts", "测试用例产物"),
    "Red Failure Records": ("Red Failure Records", "Red 失败记录", "实现前失败记录"),
    "Cannot Automate": ("Cannot Automate", "无法自动化"),
}


def read_text(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def is_filled(value: Optional[str]) -> bool:
    if value is None:
        return False
    text = value.replace("`", "").strip()
    return bool(text) and text not in {"Pending", "pending", "draft", "-"} and NOT_FILLED not in text and NOT_CONFIRMED not in text


def state_value(content: str, label: str) -> Optional[str]:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*(.+?)\s*$", content)
    return match.group(1).strip() if match else None


def normalize_state_ref(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip().replace("\\", "/").lstrip("./").rstrip("/")


def state_ref_matches(value: Optional[str], expected: str) -> bool:
    return normalize_state_ref(value) == normalize_state_ref(expected)


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


def row_value(row: Optional[Dict[str, str]], *keys: str) -> Optional[str]:
    if row is None:
        return None
    for key in keys:
        if key in row:
            return row[key]
    return None


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


def table_row(rows: List[Dict[str, str]], key: str, value: str, *alternate_keys: str) -> Optional[Dict[str, str]]:
    for row in rows:
        if row_value(row, key, *alternate_keys) == value:
            return row
    return None


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


def cell_codes(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return re.findall(r"\b[A-Z][A-Z0-9_]*-[A-Z0-9_.-]+\b", value)


def cell_acceptance_ids(value: Optional[str]) -> List[str]:
    return [code for code in cell_codes(value) if code.startswith("AC-")]


def gate_conclusion(review: Optional[str], gate: str) -> Optional[str]:
    if review is None:
        return None
    row = table_row(section_rows(review, "Gate Approvals"), "Gate", gate, "关口")
    return row_value(row, "Conclusion", "结论")


def check_dev_task_handoff(
    project_root: Path,
    change_id: str,
    change: str,
    task_id: str,
    failures: List[str],
) -> None:
    script = project_root / "tools" / "check-dev-task-handoff-readiness.py"
    if not script.exists():
        failures.append("缺少 tools/check-dev-task-handoff-readiness.py")
        return

    command = [
        sys.executable,
        str(script),
        "--project-root",
        str(project_root),
        "--change-id",
        change_id,
        "--next-task-id",
        task_id,
    ]
    if change:
        command.extend(["--change", change])

    result = subprocess.run(
        command,
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return

    output = result.stdout + result.stderr
    details = [
        line[2:].strip()
        for line in output.splitlines()
        if line.startswith("- ")
    ]
    if details:
        failures.append("开发任务暂停/继续检查未通过：" + "；".join(details))
    else:
        failures.append("开发任务暂停/继续检查未通过")


def normalize_relative_path(root: Path, path: str) -> str:
    raw = path.replace("\\", "/")
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            relative = candidate.resolve().relative_to(root.resolve())
            return relative.as_posix()
        except ValueError:
            return candidate.resolve().as_posix()
    return raw.lstrip("./")


def scope_covers_target(scope_text: Optional[str], target: str) -> bool:
    if not scope_text or NOT_FILLED in scope_text or NOT_CONFIRMED in scope_text:
        return False
    target_normalized = target.replace("\\", "/").lstrip("./")
    scope_items = [
        item.replace("`", "").strip().replace("\\", "/").lstrip("./")
        for item in re.split(r"[,;\n]", scope_text)
        if item.strip()
    ]
    for scope in scope_items:
        if scope in {".", "*", "**/*"}:
            return True
        if "*" in scope and fnmatch.fnmatch(target_normalized, scope):
            return True
        scope_clean = scope.rstrip("/")
        if target_normalized == scope_clean or target_normalized.startswith(scope_clean + "/"):
            return True
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="业务代码修改前的 workflow 准入检查。")
    parser.add_argument("--project-root", default="", help="项目根目录，默认从 tools/ 推断。")
    parser.add_argument("--change-id", required=True, help="workflow CR 编号，例如 CR-001。")
    parser.add_argument("--change", default="", help="OpenSpec change 目录名；未传时按 CR 前缀查找。")
    parser.add_argument("--task-id", required=True, help="要检查的 OpenSpec 任务编号。")
    parser.add_argument(
        "--target-file",
        required=True,
        action="append",
        help="计划写入的目标文件；多个文件可重复传入。",
    )
    parser.add_argument("--priority", default="", choices=["", "P0", "P1", "P2", "P3"], help="任务优先级。")
    parser.add_argument("--high-risk", action="store_true", help="按高风险任务处理。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    failures: List[str] = []
    linked_acceptance_ids: List[str] = []

    state = read_text(project_root / "workflow" / "state.md")
    active_openspec_change: Optional[str] = None
    if state is None:
        failures.append("缺少 workflow/state.md")
    else:
        stage = state_value(state, "当前阶段")
        if stage != "DEVELOPMENT":
            failures.append(f"当前阶段必须是 DEVELOPMENT，当前是：{stage}")
        active_evidence = state_value(state, "当前变更")
        expected_evidence = f"workflow/changes/{args.change_id}"
        if not state_ref_matches(active_evidence, expected_evidence):
            failures.append(
                f"当前 workflow 变更必须是 {expected_evidence}，当前是：{active_evidence}"
            )
        active_openspec_change = state_value(state, "当前 OpenSpec Change")

    review_path = project_root / "workflow" / "changes" / args.change_id / "review.md"
    review = read_text(review_path)
    if review is None:
        failures.append(f"缺少 workflow/changes/{args.change_id}/review.md")
    else:
        requirement_gate = gate_conclusion(review, "REQ_GATE")
        design_gate = gate_conclusion(review, "DESIGN_GATE")
        if requirement_gate != "passed":
            failures.append(f"REQ_GATE 结论必须是 passed，当前是：{requirement_gate}")
        if design_gate != "passed":
            failures.append(f"DESIGN_GATE 结论必须是 passed，当前是：{design_gate}")

    change_dir = find_openspec_change_dir(project_root, args.change_id, args.change or None)
    task: Optional[Dict[str, str]] = None
    if change_dir is None:
        change_ref = args.change or f"{args.change_id}-<change-name>"
        failures.append(f"缺少 openspec/changes/{change_ref}/")
    else:
        expected_openspec_change = f"openspec/changes/{change_dir.name}"
        if state is not None and not state_ref_matches(active_openspec_change, expected_openspec_change):
            failures.append(
                f"当前 OpenSpec Change 必须是 {expected_openspec_change}，当前是：{active_openspec_change}"
            )
        tasks = read_text(change_dir / "tasks.md")
        if tasks is None:
            failures.append(f"缺少 {(change_dir / 'tasks.md').relative_to(project_root)}")
        else:
            task = table_row(section_rows(tasks, "Implementation Tasks"), "Task ID", args.task_id, "任务编号")
            if task is None:
                failures.append(f"任务 {args.task_id} 不存在于 {(change_dir / 'tasks.md').relative_to(project_root)}")
            else:
                status = row_value(task, "Status", "状态")
                scope = row_value(task, "Allowed Write Scope", "允许写入范围")
                requirement_ref = row_value(task, "Requirement / AC", "关联验收项")
                if status not in {"Ready", "Approved"}:
                    failures.append(f"任务 {args.task_id} 状态必须是 Ready 或 Approved，当前是：{status}")
                if not is_filled(requirement_ref):
                    failures.append(f"任务 {args.task_id} 必须绑定至少一个验收项 AC-*")
                linked_acceptance_ids = cell_acceptance_ids(requirement_ref)
                if not linked_acceptance_ids:
                    failures.append(f"任务 {args.task_id} 的关联验收项必须包含 AC-* 编号，当前是：{requirement_ref}")
                excluded_ref = row_value(task, "Excluded AC", "不覆盖验收项")
                if excluded_ref is None or not is_filled(excluded_ref):
                    failures.append(f"任务 {args.task_id} 必须显式填写不覆盖验收项；无不覆盖项时写 无")
                for target in args.target_file:
                    relative_target = normalize_relative_path(project_root, target)
                    if not scope_covers_target(scope, relative_target):
                        failures.append(
                            f"任务 {args.task_id} 的允许写入范围未覆盖目标文件：{relative_target}"
                        )

    acceptance = read_text(project_root / "workflow" / "changes" / args.change_id / "acceptance.md")
    if acceptance is None:
        failures.append(f"缺少 workflow/changes/{args.change_id}/acceptance.md")
    elif linked_acceptance_ids:
        rows = top_table_rows(acceptance)
        for acceptance_id in linked_acceptance_ids:
            row = next(
                (item for item in rows if row_value(item, "验收编号", "Acceptance ID") == acceptance_id),
                None,
            )
            if row is None:
                failures.append(f"任务 {args.task_id} 绑定的验收项 {acceptance_id} 不存在于 acceptance.md")
                continue
            task_ref = row_value(row, "OpenSpec Task", "开发任务", "绑定任务")
            if args.task_id not in cell_codes(task_ref):
                failures.append(f"验收项 {acceptance_id} 必须在 acceptance.md 中反向关联任务 {args.task_id}")

    test_plan_path = project_root / "workflow" / "changes" / args.change_id / "test-plan.md"
    test_plan = read_text(test_plan_path)
    if test_plan is None:
        failures.append(f"缺少 workflow/changes/{args.change_id}/test-plan.md")
    else:
        artifact_row = table_row(section_rows(test_plan, "Test Case Artifacts"), "任务编号", args.task_id)
        if artifact_row is None:
            artifact_row = table_row(section_rows(test_plan, "Test Case Artifacts"), "Task ID", args.task_id)
        if artifact_row is None:
            failures.append(f"任务 {args.task_id} 在 test-plan.md 中缺少测试用例产物")
        else:
            artifact = row_value(artifact_row, "Test Case Artifact", "测试用例产物")
            coverage = row_value(artifact_row, "Acceptance IDs", "覆盖验收项")
            artifact_status = row_value(artifact_row, "Status", "状态")
            if not is_filled(artifact):
                failures.append(f"任务 {args.task_id} 写业务代码前必须填写测试用例产物")
            if not is_filled(coverage):
                failures.append(f"任务 {args.task_id} 写业务代码前必须填写测试用例产物覆盖的 AC")
            covered_acceptance_ids = set(cell_acceptance_ids(coverage))
            for acceptance_id in linked_acceptance_ids:
                if acceptance_id not in covered_acceptance_ids:
                    failures.append(f"任务 {args.task_id} 测试用例产物未覆盖绑定验收项 {acceptance_id}")
            if artifact_status not in {"Ready", "Approved", "Recorded"}:
                failures.append(
                    f"任务 {args.task_id} 测试用例产物状态必须是 Ready、Approved 或 Recorded，当前是：{artifact_status}"
                )
            artifact_type = (row_value(artifact_row, "Type", "类型") or "").lower()
            manual_only = ("manual" in artifact_type and "automated" not in artifact_type) or "cannot" in artifact_type
            if manual_only:
                manual_row = table_row(section_rows(test_plan, "Cannot Automate"), "任务编号", args.task_id)
                if manual_row is None:
                    manual_row = table_row(section_rows(test_plan, "Cannot Automate"), "Task ID", args.task_id)
                if manual_row is None:
                    failures.append(f"任务 {args.task_id} 使用人工测试时必须填写无法自动化记录")
                else:
                    if not is_filled(row_value(manual_row, "Reason", "原因")):
                        failures.append(f"任务 {args.task_id} 必须填写无法自动化原因")
                    if not is_filled(row_value(manual_row, "Manual Verification Owner", "人工验证负责人")):
                        failures.append(f"任务 {args.task_id} 必须填写人工验证负责人")

        red_row = table_row(section_rows(test_plan, "Red Failure Records"), "任务编号", args.task_id)
        if red_row is None:
            red_row = table_row(section_rows(test_plan, "Red Failure Records"), "Task ID", args.task_id)
        if red_row is None:
            failures.append(f"任务 {args.task_id} 在 test-plan.md 中缺少 Red 失败记录")
        else:
            if not is_filled(row_value(red_row, "Test Case Artifact", "测试用例产物")):
                failures.append(f"任务 {args.task_id} Red 记录必须填写测试用例产物")
            if not is_filled(row_value(red_row, "Command / Steps", "命令 / 步骤")):
                failures.append(f"任务 {args.task_id} Red 记录必须填写命令或步骤")
            if not is_filled(row_value(red_row, "Failure Summary", "失败摘要")):
                failures.append(f"任务 {args.task_id} Red 记录必须填写失败摘要")
            red_status = row_value(red_row, "Status", "状态")
            if red_status not in {"Failed", "Red", "Recorded"}:
                failures.append(f"任务 {args.task_id} Red 状态必须是 Failed、Red 或 Recorded，当前是：{red_status}")

    if task is not None:
        task_text = " ".join(task.values())
        risk_markers = [
            "P0",
            "P1",
            "API",
            "database",
            "permission",
            "security",
            "deploy",
            "production",
            "payment",
            "cross-module",
            "高风险",
            "数据库",
            "权限",
            "安全",
            "部署",
            "生产",
            "支付",
            "跨模块",
        ]
        risk_from_task = any(marker.lower() in task_text.lower() for marker in risk_markers)
        if (args.high_risk or args.priority in {"P0", "P1"} or risk_from_task) and test_plan is None:
            failures.append(f"P0/P1 或高风险任务必须有 workflow/changes/{args.change_id}/test-plan.md")

    check_dev_task_handoff(project_root, args.change_id, args.change, args.task_id, failures)

    if failures:
        print("代码准入检查：未通过")
        for failure in failures:
            print(f"- {failure}")
        print("写业务代码前，Agent 必须请求人工确认或补齐 workflow 记录。")
        return 1

    print("代码准入检查：通过")
    print(f"任务 {args.task_id} 可以在已批准的 OpenSpec 写入范围内修改代码。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
