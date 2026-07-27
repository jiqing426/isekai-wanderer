#!/usr/bin/env python3
"""Shared read-only helpers for workflow status tools."""

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Dict, List, Optional, Set, Tuple


BLANK_VALUES = {"", "Pending", "pending", "draft", "TBD", "TODO", "-", "none", "无"}
COMPLETED_STATUSES = {"Implemented", "Done", "Completed", "Delivered", "已完成"}
READY_STATUSES = {"Ready", "Approved"}
IN_PROGRESS_STATUSES = {"In Progress", "Doing", "Started", "in_progress"}
RED_STATUSES = {"Failed", "Red", "Recorded"}
GREEN_STATUSES = {"Passed", "Green", "Recorded", "通过", "已记录"}
ACCEPTANCE_DONE_STATUSES = {"Implemented", "Verified"}
HANDOFF_PAUSE_STATUSES = {"Reported", "Paused", "Recorded", "已汇报", "已暂停", "已记录"}
HANDOFF_CONTINUE_STATUSES = {"Confirmed", "Continue", "Approved", "用户已确认继续", "已确认继续", "继续"}

SECTION_ALIASES = {
    "Gate Approvals": ("Gate Approvals", "关口审批", "关口结论"),
    "Implementation Tasks": ("Implementation Tasks", "实现任务"),
    "Test Case Artifacts": ("Test Case Artifacts", "测试用例产物"),
    "Red Failure Records": ("Red Failure Records", "Red 失败记录", "实现前失败记录"),
    "Green Pass Records": ("Green Pass Records", "Green 通过记录", "实现后通过记录"),
    "Development Task Handoffs": (
        "Development Task Handoffs",
        "开发任务暂停确认",
        "开发任务暂停/继续确认",
        "开发任务交接",
    ),
}

STATE_LABELS = {
    "stage": ("当前阶段", "Current Stage"),
    "status": ("当前状态", "Current Status"),
    "owner": ("当前负责人", "Current Owner"),
    "gate": ("当前关口", "Current Gate"),
    "change_ref": ("当前变更", "Current Change"),
    "openspec_ref": ("当前 OpenSpec Change", "Current OpenSpec Change"),
    "task": ("当前任务", "Current Task"),
    "next_action": ("下一步动作", "Next Action"),
}


@dataclass
class WorkflowContext:
    project_root: Path
    change_id: str = ""
    change: str = ""
    change_dir: Optional[Path] = None
    state_path: Optional[Path] = None
    review_path: Optional[Path] = None
    tasks_path: Optional[Path] = None
    test_plan_path: Optional[Path] = None
    acceptance_path: Optional[Path] = None
    state: Optional[str] = None
    review: Optional[str] = None
    tasks: Optional[str] = None
    test_plan: Optional[str] = None
    acceptance: Optional[str] = None
    stage: Optional[str] = None
    gate: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    current_task: Optional[str] = None
    state_change_ref: Optional[str] = None
    state_openspec_ref: Optional[str] = None
    missing_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def read_text(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def rel_path(project_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def clean_cell(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip()


def is_filled(value: Optional[str]) -> bool:
    text = clean_cell(value)
    if text in BLANK_VALUES:
        return False
    return "待填写" not in text and "待确认" not in text and bool(text)


def normalize_status(value: Optional[str]) -> str:
    return clean_cell(value).casefold()


def status_in(value: Optional[str], allowed: Set[str]) -> bool:
    normalized = normalize_status(value)
    return bool(normalized) and normalized in {item.casefold() for item in allowed}


def state_value(content: Optional[str], key: str) -> Optional[str]:
    if content is None:
        return None
    for label in STATE_LABELS[key]:
        match = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*(.+?)\s*$", content)
        if match:
            return match.group(1).strip()
    return None


def normalize_ref(value: Optional[str]) -> str:
    return clean_cell(value).replace("\\", "/").lstrip("./").rstrip("/")


def ref_matches(value: Optional[str], expected: str) -> bool:
    return normalize_ref(value) == normalize_ref(expected)


def extract_change_id(value: Optional[str]) -> str:
    text = normalize_ref(value)
    if "<" in text or ">" in text:
        return ""
    match = re.search(r"(?:^|/)workflow/changes/([^/\s]+)", text)
    if match:
        return match.group(1)
    match = re.search(r"\bCR-\d+\b", text)
    return match.group(0) if match else ""


def extract_change_name(value: Optional[str]) -> str:
    text = normalize_ref(value)
    if "<" in text or ">" in text:
        return ""
    match = re.search(r"(?:^|/)openspec/changes/([^/\s]+)", text)
    return match.group(1) if match else ""


def find_openspec_change_dir(project_root: Path, change_id: str, change: Optional[str]) -> Optional[Path]:
    changes_dir = project_root / "openspec" / "changes"
    if change:
        candidate = changes_dir / change
        return candidate if candidate.is_dir() else None
    if not changes_dir.exists() or not change_id:
        return None
    exact = changes_dir / change_id
    if exact.is_dir():
        return exact
    matches = sorted(
        path for path in changes_dir.iterdir()
        if path.is_dir() and path.name.startswith(f"{change_id}-")
    )
    return matches[0] if matches else None


def split_markdown_row(line: str) -> List[str]:
    text = line.strip()
    if not text.startswith("|"):
        return []
    return [cell.strip() for cell in text.strip("|").split("|")]


def section_content(content: Optional[str], section: str) -> str:
    if content is None:
        return ""
    for section_name in SECTION_ALIASES.get(section, (section,)):
        pattern = re.compile(rf"(?ms)^##\s+{re.escape(section_name)}\s*\n(.+?)(?=^##\s+|\Z)")
        match = pattern.search(content)
        if match:
            return match.group(1)
    return ""


def table_rows_from_text(text: str) -> List[Dict[str, str]]:
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


def section_rows(content: Optional[str], section: str) -> List[Dict[str, str]]:
    return table_rows_from_text(section_content(content, section))


def top_table_rows(content: Optional[str]) -> List[Dict[str, str]]:
    if content is None:
        return []
    lines: List[str] = []
    for line in content.splitlines():
        if re.match(r"^##\s+", line):
            break
        lines.append(line)
    return table_rows_from_text("\n".join(lines))


def row_value(row: Optional[Dict[str, str]], *keys: str) -> Optional[str]:
    if row is None:
        return None
    for key in keys:
        if key in row:
            return row[key]
    return None


def row_by_value(rows: List[Dict[str, str]], value: str, *keys: str) -> Optional[Dict[str, str]]:
    for row in rows:
        if row_value(row, *keys) == value:
            return row
    return None


def task_id(row: Dict[str, str]) -> str:
    return row_value(row, "Task ID", "任务编号") or ""


def task_status(row: Optional[Dict[str, str]]) -> Optional[str]:
    return row_value(row, "Status", "状态")


def gate_conclusions(review: Optional[str]) -> Dict[str, Optional[str]]:
    conclusions: Dict[str, Optional[str]] = {}
    for gate in ("INIT", "REQ_GATE", "DESIGN_GATE", "RELEASE_GATE"):
        row = row_by_value(section_rows(review, "Gate Approvals"), gate, "Gate", "关口")
        conclusions[gate] = row_value(row, "Conclusion", "结论")
    return conclusions


def implementation_tasks(tasks: Optional[str]) -> List[Dict[str, str]]:
    return section_rows(tasks, "Implementation Tasks")


def dev_tasks(tasks: Optional[str]) -> List[Dict[str, str]]:
    return [row for row in implementation_tasks(tasks) if task_id(row).startswith("DEV-")]


def find_task(tasks: Optional[str], task: Optional[str]) -> Optional[Dict[str, str]]:
    if not task:
        return None
    return row_by_value(implementation_tasks(tasks), task, "Task ID", "任务编号")


def previous_dev_task(tasks: Optional[str], current_task: Optional[str]) -> Optional[Dict[str, str]]:
    dev_rows = dev_tasks(tasks)
    for index, row in enumerate(dev_rows):
        if task_id(row) == current_task and index > 0:
            return dev_rows[index - 1]
    return None


def next_dev_task(tasks: Optional[str], current_task: Optional[str]) -> Optional[Dict[str, str]]:
    dev_rows = dev_tasks(tasks)
    for index, row in enumerate(dev_rows):
        if task_id(row) == current_task and index + 1 < len(dev_rows):
            return dev_rows[index + 1]
    return None


def first_ready_dev_task(tasks: Optional[str]) -> Optional[Dict[str, str]]:
    for row in dev_tasks(tasks):
        if status_in(task_status(row), READY_STATUSES | IN_PROGRESS_STATUSES):
            return row
    return None


def task_progress(tasks: Optional[str]) -> Dict[str, int]:
    progress = {"total": 0, "completed": 0, "ready": 0, "in_progress": 0, "other": 0}
    for row in dev_tasks(tasks):
        progress["total"] += 1
        status = task_status(row)
        if status_in(status, COMPLETED_STATUSES):
            progress["completed"] += 1
        elif status_in(status, READY_STATUSES):
            progress["ready"] += 1
        elif status_in(status, IN_PROGRESS_STATUSES):
            progress["in_progress"] += 1
        else:
            progress["other"] += 1
    return progress


def test_artifact_row(test_plan: Optional[str], task: Optional[str]) -> Optional[Dict[str, str]]:
    if not task:
        return None
    return row_by_value(section_rows(test_plan, "Test Case Artifacts"), task, "任务编号", "Task ID")


def red_row(test_plan: Optional[str], task: Optional[str]) -> Optional[Dict[str, str]]:
    if not task:
        return None
    return row_by_value(section_rows(test_plan, "Red Failure Records"), task, "任务编号", "Task ID")


def green_row(test_plan: Optional[str], task: Optional[str]) -> Optional[Dict[str, str]]:
    if not task:
        return None
    return row_by_value(section_rows(test_plan, "Green Pass Records"), task, "任务编号", "Task ID")


def record_state(row: Optional[Dict[str, str]], status_set: Set[str], summary_keys: Tuple[str, ...]) -> Tuple[str, List[str]]:
    if row is None:
        return "missing", ["缺少记录"]
    gaps: List[str] = []
    status = row_value(row, "Status", "状态")
    if not status_in(status, status_set):
        gaps.append(f"状态不是有效值: {status or '空'}")
    if not is_filled(row_value(row, "Test Case Artifact", "测试用例产物")):
        gaps.append("缺少测试用例产物")
    if not is_filled(row_value(row, "Command / Steps", "命令 / 步骤")):
        gaps.append("缺少命令 / 步骤")
    if not is_filled(row_value(row, *summary_keys)):
        gaps.append("缺少摘要")
    if not is_filled(row_value(row, "Recorded At", "记录时间")):
        gaps.append("缺少记录时间")
    return ("ready" if not gaps else "incomplete"), gaps


def red_green_summary(test_plan: Optional[str], task: Optional[str]) -> Dict[str, object]:
    red_state, red_gaps = record_state(red_row(test_plan, task), RED_STATUSES, ("Failure Summary", "失败摘要"))
    green_state, green_gaps = record_state(green_row(test_plan, task), GREEN_STATUSES, ("Pass Summary", "通过摘要"))
    return {
        "red_state": red_state,
        "red_gaps": red_gaps,
        "green_state": green_state,
        "green_gaps": green_gaps,
    }


def acceptance_ids(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [code for code in re.findall(r"\bAC-[A-Z0-9_.-]+\b", value)]


def acceptance_rows_for_task(acceptance: Optional[str], task: Optional[str]) -> List[Dict[str, str]]:
    if not task:
        return []
    rows = []
    for row in top_table_rows(acceptance):
        task_ref = row_value(row, "OpenSpec Task", "开发任务") or ""
        if task in task_ref:
            rows.append(row)
    return rows


def acceptance_summary(acceptance: Optional[str], task: Optional[str]) -> Tuple[str, List[str]]:
    rows = acceptance_rows_for_task(acceptance, task)
    if not rows:
        return "missing", ["acceptance.md 缺少当前任务的验收追踪行"]
    gaps: List[str] = []
    for row in rows:
        acceptance_id = row_value(row, "验收编号", "Acceptance ID") or "未知验收项"
        status = row_value(row, "状态", "Status")
        if status not in ACCEPTANCE_DONE_STATUSES:
            gaps.append(f"{acceptance_id} 状态不是 Implemented/Verified: {status or '空'}")
        if not is_filled(row_value(row, "测试用例 / 验证命令", "Test Case / Verification Command")):
            gaps.append(f"{acceptance_id} 缺少测试用例 / 验证命令")
    return ("ready" if not gaps else "incomplete"), gaps


def find_handoff_row(review: Optional[str], completed_task: str, next_task: str) -> Optional[Dict[str, str]]:
    for row in section_rows(review, "Development Task Handoffs"):
        completed = row_value(row, "Completed Task", "完成任务", "已完成任务")
        next_value = row_value(row, "Next Task", "下一任务", "下一个任务")
        if completed == completed_task and next_value == next_task:
            return row
    return None


def handoff_summary(review: Optional[str], tasks: Optional[str], current_task: Optional[str]) -> Tuple[str, List[str], Optional[str]]:
    previous = previous_dev_task(tasks, current_task)
    if previous is None:
        return "not_required", [], None
    previous_id = task_id(previous)
    gaps: List[str] = []
    if not status_in(task_status(previous), COMPLETED_STATUSES):
        gaps.append(f"上一个 DEV 任务 {previous_id} 尚未完成，当前状态: {task_status(previous) or '空'}")
    row = find_handoff_row(review, previous_id, current_task or "")
    if row is None:
        gaps.append(f"缺少 {previous_id} -> {current_task} 的暂停/继续记录")
        return "missing", gaps, previous_id
    if not status_in(row_value(row, "Pause Report", "暂停汇报", "暂停记录"), HANDOFF_PAUSE_STATUSES):
        gaps.append(f"{previous_id} 完成后缺少有效暂停汇报")
    if not status_in(row_value(row, "User Continue", "用户继续", "继续确认", "用户继续确认"), HANDOFF_CONTINUE_STATUSES):
        gaps.append(f"开始 {current_task} 前缺少用户继续确认")
    if not is_filled(row_value(row, "Recorded At", "记录时间")):
        gaps.append(f"{previous_id} -> {current_task} 缺少记录时间")
    return ("ready" if not gaps else "incomplete"), gaps, previous_id


def command_base(change_id: str, change: str) -> str:
    return f"--change-id {change_id} --change {change}" if change else f"--change-id {change_id}"


def load_context(project_root: Path, change_id_override: str = "", change_override: str = "") -> WorkflowContext:
    root = project_root.resolve()
    ctx = WorkflowContext(project_root=root, state_path=root / "workflow" / "state.md")
    ctx.state = read_text(ctx.state_path)
    if ctx.state is None:
        ctx.missing_files.append("workflow/state.md")
        ctx.errors.append("缺少必要文件: workflow/state.md")
        return ctx

    ctx.stage = state_value(ctx.state, "stage")
    ctx.status = state_value(ctx.state, "status")
    ctx.owner = state_value(ctx.state, "owner")
    ctx.gate = state_value(ctx.state, "gate")
    ctx.current_task = state_value(ctx.state, "task")
    if ctx.current_task and ctx.current_task in {"无", "none", "None", "-"}:
        ctx.current_task = ""
    ctx.state_change_ref = state_value(ctx.state, "change_ref")
    ctx.state_openspec_ref = state_value(ctx.state, "openspec_ref")

    ctx.change_id = change_id_override or extract_change_id(ctx.state_change_ref)
    ctx.change = change_override or extract_change_name(ctx.state_openspec_ref)
    if not ctx.change_id:
        ctx.errors.append("无法从 workflow/state.md 识别当前 CR；请传 --change-id")
    if not ctx.change:
        found = find_openspec_change_dir(root, ctx.change_id, None)
        if found is not None:
            ctx.change_dir = found
            ctx.change = found.name
        else:
            ctx.errors.append("无法从 workflow/state.md 识别当前 OpenSpec change；请传 --change")
    else:
        ctx.change_dir = find_openspec_change_dir(root, ctx.change_id, ctx.change)

    if ctx.change_id:
        ctx.review_path = root / "workflow" / "changes" / ctx.change_id / "review.md"
        ctx.test_plan_path = root / "workflow" / "changes" / ctx.change_id / "test-plan.md"
        ctx.acceptance_path = root / "workflow" / "changes" / ctx.change_id / "acceptance.md"
        ctx.review = read_text(ctx.review_path)
        ctx.test_plan = read_text(ctx.test_plan_path)
        ctx.acceptance = read_text(ctx.acceptance_path)
        for path, text in (
            (ctx.review_path, ctx.review),
            (ctx.test_plan_path, ctx.test_plan),
            (ctx.acceptance_path, ctx.acceptance),
        ):
            if text is None:
                ctx.missing_files.append(rel_path(root, path))

    if ctx.change_dir is None and ctx.change:
        ctx.errors.append(f"缺少必要目录: openspec/changes/{ctx.change}/")
    if ctx.change_dir is not None:
        ctx.tasks_path = ctx.change_dir / "tasks.md"
        ctx.tasks = read_text(ctx.tasks_path)
        if ctx.tasks is None:
            ctx.missing_files.append(rel_path(root, ctx.tasks_path))

    if (
        not change_id_override
        and ctx.change_id
        and ctx.state_change_ref
        and not ref_matches(ctx.state_change_ref, f"workflow/changes/{ctx.change_id}")
    ):
        ctx.errors.append(f"workflow/state.md 当前变更不是 workflow/changes/{ctx.change_id}: {ctx.state_change_ref}")
    if (
        not change_override
        and ctx.change
        and ctx.state_openspec_ref
        and not ref_matches(ctx.state_openspec_ref, f"openspec/changes/{ctx.change}")
    ):
        ctx.errors.append(f"workflow/state.md 当前 OpenSpec Change 不是 openspec/changes/{ctx.change}: {ctx.state_openspec_ref}")

    return ctx


def current_task_id(ctx: WorkflowContext, override: str = "") -> str:
    if override:
        return override
    if ctx.current_task:
        return ctx.current_task
    row = first_ready_dev_task(ctx.tasks)
    return task_id(row) if row is not None else ""


def major_gaps(ctx: WorkflowContext, task_override: str = "") -> List[str]:
    gaps: List[str] = []
    gaps.extend(ctx.errors)
    for path in ctx.missing_files:
        gaps.append(f"缺少必要文件: {path}")

    conclusions = gate_conclusions(ctx.review)
    stage = ctx.stage or ""
    task = current_task_id(ctx, task_override)
    current = find_task(ctx.tasks, task)

    if stage == "REQ_GATE" and conclusions.get("INIT") != "passed":
        gaps.append(f"REQ_GATE 前 INIT 结论需要 passed，当前: {conclusions.get('INIT') or '缺失'}")
    if stage in {"DESIGN_GATE", "DEVELOPMENT", "RELEASE_GATE"} and conclusions.get("REQ_GATE") != "passed":
        gaps.append(f"REQ_GATE 结论需要 passed，当前: {conclusions.get('REQ_GATE') or '缺失'}")
    if stage in {"DEVELOPMENT", "RELEASE_GATE"} and conclusions.get("DESIGN_GATE") != "passed":
        gaps.append(f"DESIGN_GATE 结论需要 passed，当前: {conclusions.get('DESIGN_GATE') or '缺失'}")

    if stage == "DEVELOPMENT":
        if not task:
            gaps.append("workflow/state.md 缺少当前 DEV 任务")
        elif current is None:
            gaps.append(f"OpenSpec tasks.md 缺少当前任务 {task}")
        else:
            if not status_in(task_status(current), READY_STATUSES | IN_PROGRESS_STATUSES | COMPLETED_STATUSES):
                gaps.append(f"当前任务 {task} 状态不可执行或不可完成: {task_status(current) or '空'}")
            artifact = test_artifact_row(ctx.test_plan, task)
            if artifact is None:
                gaps.append(f"{task} 缺少测试用例产物记录")
            elif not is_filled(row_value(artifact, "Test Case Artifact", "测试用例产物")):
                gaps.append(f"{task} 测试用例产物为空")
            rg = red_green_summary(ctx.test_plan, task)
            if rg["red_state"] != "ready":
                gaps.extend(f"{task} Red: {gap}" for gap in rg["red_gaps"])
            if rg["green_state"] != "ready":
                gaps.extend(f"{task} Green: {gap}" for gap in rg["green_gaps"])
            acceptance_state, acceptance_gaps = acceptance_summary(ctx.acceptance, task)
            if acceptance_state != "ready":
                gaps.extend(acceptance_gaps)
            handoff_state, handoff_gaps, _ = handoff_summary(ctx.review, ctx.tasks, task)
            if handoff_state not in {"ready", "not_required"}:
                gaps.extend(handoff_gaps)

    return gaps
