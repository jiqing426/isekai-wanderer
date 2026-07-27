#!/usr/bin/env python3
"""检查开始下一个 DEV-* 任务前是否已暂停汇报并获得用户继续确认。"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


NOT_FILLED = "待填写"
NOT_CONFIRMED = "待确认"
BLANK_VALUES = {"", "Pending", "pending", "draft", "TBD", "TODO", "-", "none"}
SECTION_ALIASES = {
    "Implementation Tasks": ("Implementation Tasks", "实现任务"),
    "Development Task Handoffs": (
        "Development Task Handoffs",
        "开发任务暂停确认",
        "开发任务暂停/继续确认",
        "开发任务交接",
    ),
}
DEFAULT_PAUSE_CONFIG = {
    "enabled": True,
    "applies_to_stage": "DEVELOPMENT",
    "applies_to_task_id_pattern": r"^DEV-.+",
    "evidence_file": "workflow/changes/<CR-ID>/review.md",
    "evidence_section": "Development Task Handoffs",
    "completed_task_statuses": ["Implemented", "Done", "Completed", "Delivered", "已完成"],
    "pause_report_statuses": ["Reported", "Paused", "Recorded", "已汇报", "已暂停", "已记录"],
    "user_continue_statuses": ["Confirmed", "Continue", "Approved", "用户已确认继续", "已确认继续", "继续"],
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


def normalize_status(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip().casefold()


def status_allowed(value: Optional[str], allowed: List[str]) -> bool:
    normalized = normalize_status(value)
    return bool(normalized) and normalized in {normalize_status(item) for item in allowed}


def parse_scalar(value: str) -> str | bool:
    text = value.strip()
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    return text


def parse_development_pause_config(path: Path) -> Dict[str, object]:
    content = read_text(path)
    if content is None:
        raise FileNotFoundError(path)

    config: Dict[str, object] = {
        key: list(value) if isinstance(value, list) else value
        for key, value in DEFAULT_PAUSE_CONFIG.items()
    }
    found = False
    in_section = False
    current_list_key: Optional[str] = None
    list_keys = {"completed_task_statuses", "pause_report_statuses", "user_continue_statuses"}

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))

        if indent == 2 and stripped == "development_task_pause:":
            found = True
            in_section = True
            current_list_key = None
            continue
        if not in_section:
            continue
        if indent <= 2:
            break

        if indent == 4 and ":" in stripped:
            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            current_list_key = None
            if key in list_keys and not raw_value:
                config[key] = []
                current_list_key = key
            elif key in DEFAULT_PAUSE_CONFIG and raw_value:
                config[key] = parse_scalar(raw_value)
            continue

        if indent == 6 and current_list_key and stripped.startswith("- "):
            value = parse_scalar(stripped[2:])
            if isinstance(value, str):
                current = config.setdefault(current_list_key, [])
                if isinstance(current, list):
                    current.append(value)

    if not found:
        raise ValueError("workflow/execution.config.yaml 缺少 development_task_pause 配置")
    return config


def state_value(content: str, label: str) -> Optional[str]:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*(.+?)\s*$", content)
    return match.group(1).strip() if match else None


def normalize_ref(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip().replace("\\", "/").lstrip("./").rstrip("/")


def ref_matches(value: Optional[str], expected: str) -> bool:
    return normalize_ref(value) == normalize_ref(expected)


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


def task_id(row: Dict[str, str]) -> Optional[str]:
    return row_value(row, "Task ID", "任务编号")


def find_handoff_row(rows: List[Dict[str, str]], completed_task: str, next_task: str) -> Optional[Dict[str, str]]:
    for row in rows:
        completed = row_value(row, "Completed Task", "完成任务", "已完成任务")
        next_value = row_value(row, "Next Task", "下一任务", "下一个任务")
        if completed == completed_task and next_value == next_task:
            return row
    return None


def configured_list(config: Dict[str, object], key: str) -> List[str]:
    value = config.get(key)
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="下一个 DEV-* 任务启动前的暂停/继续准入检查。")
    parser.add_argument("--project-root", default="", help="项目根目录，默认从 tools/ 推断。")
    parser.add_argument("--change-id", required=True, help="workflow CR 编号，例如 CR-001。")
    parser.add_argument("--change", default="", help="OpenSpec change 目录名；未传时按 CR 前缀查找。")
    parser.add_argument("--next-task-id", required=True, help="准备开始的下一个 OpenSpec DEV-* 任务编号。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    failures: List[str] = []

    try:
        config = parse_development_pause_config(project_root / "workflow" / "execution.config.yaml")
    except (FileNotFoundError, ValueError) as error:
        config = DEFAULT_PAUSE_CONFIG
        failures.append(str(error))

    if config.get("enabled") is False:
        print("开发任务暂停/继续检查：已禁用")
        return 0

    required_stage = str(config.get("applies_to_stage") or "DEVELOPMENT")
    task_pattern = str(config.get("applies_to_task_id_pattern") or r"^DEV-.+")

    state = read_text(project_root / "workflow" / "state.md")
    active_openspec_change: Optional[str] = None
    if state is None:
        failures.append("缺少 workflow/state.md")
    else:
        stage = state_value(state, "当前阶段")
        if stage != required_stage:
            failures.append(f"当前阶段必须是 {required_stage} 才能开始 DEV-* 任务，当前是：{stage}")
        expected_evidence = f"workflow/changes/{args.change_id}"
        active_evidence = state_value(state, "当前变更")
        if not ref_matches(active_evidence, expected_evidence):
            failures.append(f"当前变更必须是 {expected_evidence}，当前是：{active_evidence}")
        active_openspec_change = state_value(state, "当前 OpenSpec Change")

    try:
        dev_re = re.compile(task_pattern)
    except re.error as error:
        dev_re = re.compile(r"^DEV-.+")
        failures.append(f"development_task_pause.applies_to_task_id_pattern 不是有效正则：{error}")

    if not dev_re.fullmatch(args.next_task_id):
        if failures:
            print("开发任务暂停/继续检查：未通过")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("开发任务暂停/继续检查：通过")
        print(f"任务 {args.next_task_id} 不匹配 DEV-* 规则，不需要暂停/继续校验。")
        return 0

    change_dir = find_openspec_change_dir(project_root, args.change_id, args.change or None)
    previous_task_id: Optional[str] = None
    previous_task: Optional[Dict[str, str]] = None
    if change_dir is None:
        change_ref = args.change or f"{args.change_id}-<change-name>"
        failures.append(f"缺少 openspec/changes/{change_ref}/")
    else:
        expected_openspec = f"openspec/changes/{change_dir.name}"
        if state is not None and not ref_matches(active_openspec_change, expected_openspec):
            failures.append(f"当前 OpenSpec Change 必须是 {expected_openspec}，当前是：{active_openspec_change}")

        tasks = read_text(change_dir / "tasks.md")
        if tasks is None:
            failures.append(f"缺少 {(change_dir / 'tasks.md').relative_to(project_root)}")
        else:
            task_rows = section_rows(tasks, "Implementation Tasks")
            dev_tasks = [
                row for row in task_rows
                if (task_id(row) or "") and dev_re.fullmatch(task_id(row) or "")
            ]
            next_index = next(
                (index for index, row in enumerate(dev_tasks) if task_id(row) == args.next_task_id),
                None,
            )
            if next_index is None:
                failures.append(f"任务 {args.next_task_id} 不存在于 DEV-* 实现任务顺序中")
            elif next_index > 0:
                previous_task = dev_tasks[next_index - 1]
                previous_task_id = task_id(previous_task)
                completed_statuses = configured_list(config, "completed_task_statuses")
                previous_status = row_value(previous_task, "Status", "状态")
                if not status_allowed(previous_status, completed_statuses):
                    failures.append(
                        f"上一个 DEV-* 任务 {previous_task_id} 必须先完成，当前状态是：{previous_status}"
                    )

    if previous_task_id is None:
        if failures:
            print("开发任务暂停/继续检查：未通过")
            for failure in failures:
                print(f"- {failure}")
            print("不得开始下一个 DEV-* 任务；请补齐任务顺序或 workflow 记录。")
            return 1
        print("开发任务暂停/继续检查：通过")
        print(f"任务 {args.next_task_id} 是当前 change 的第一个 DEV-* 任务，不需要上一个任务的暂停/继续证据。")
        return 0

    evidence_file = str(config.get("evidence_file") or "workflow/changes/<CR-ID>/review.md")
    evidence_file = evidence_file.replace("<CR-ID>", args.change_id)
    review = read_text(project_root / evidence_file)
    if review is None:
        failures.append(f"缺少 {evidence_file}")
    else:
        section = str(config.get("evidence_section") or "Development Task Handoffs")
        handoff_rows = section_rows(review, section)
        handoff = find_handoff_row(handoff_rows, previous_task_id, args.next_task_id)
        if handoff is None:
            failures.append(
                f"缺少 {evidence_file} 中 {previous_task_id} -> {args.next_task_id} 的暂停/继续记录"
            )
        else:
            completed_statuses = configured_list(config, "completed_task_statuses")
            pause_statuses = configured_list(config, "pause_report_statuses")
            continue_statuses = configured_list(config, "user_continue_statuses")
            completion_status = row_value(handoff, "Completion Status", "完成状态")
            pause_report = row_value(handoff, "Pause Report", "暂停汇报", "暂停记录")
            user_continue = row_value(handoff, "User Continue", "用户继续", "继续确认", "用户继续确认")
            recorded_at = row_value(handoff, "Recorded At", "记录时间")

            if completion_status is not None and not status_allowed(completion_status, completed_statuses):
                failures.append(
                    f"{previous_task_id} -> {args.next_task_id} 的完成状态必须是已完成状态，当前是：{completion_status}"
                )
            if not status_allowed(pause_report, pause_statuses):
                failures.append(
                    f"{previous_task_id} 完成后必须先停下汇报，暂停汇报状态当前是：{pause_report}"
                )
            if not status_allowed(user_continue, continue_statuses):
                failures.append(
                    f"开始 {args.next_task_id} 前必须记录用户明确继续确认，当前是：{user_continue}"
                )
            if not is_filled(recorded_at):
                failures.append(f"{previous_task_id} -> {args.next_task_id} 必须填写记录时间")

    if failures:
        print("开发任务暂停/继续检查：未通过")
        for failure in failures:
            print(f"- {failure}")
        print("不得开始下一个 DEV-* 任务；请先汇报上一个任务结果，并等待用户明确说继续。")
        return 1

    print("开发任务暂停/继续检查：通过")
    print(f"允许在用户继续确认后开始 {args.next_task_id}。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
