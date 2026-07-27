#!/usr/bin/env python3
"""检查当前 CR 是否允许从一个 workflow 阶段流转到下一个阶段。"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


NOT_FILLED = "待填写"
NOT_CONFIRMED = "待确认"
BLANK_VALUES = {"", "Pending", "pending", "draft", "TBD", "TODO", "-", "none"}
SECTION_ALIASES = {
    "Gate Approvals": ("Gate Approvals", "关口审批", "关口结论"),
    "阶段结论": ("阶段结论", "Stage Conclusions"),
    "Stage Pause Confirmations": ("Stage Pause Confirmations", "阶段暂停确认", "用户推进确认"),
}
NON_ADVANCING_ACTIONS = {"reject", "block", "stop", "rollback"}


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


def state_value(content: str, label: str) -> Optional[str]:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*(.+?)\s*$", content)
    return match.group(1).strip() if match else None


def normalize_ref(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip().replace("\\", "/").lstrip("./").rstrip("/")


def ref_matches(value: Optional[str], expected: str) -> bool:
    return normalize_ref(value) == normalize_ref(expected)


def normalized_status(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip().lower()


def parse_workflow_config(path: Path) -> Tuple[Set[str], Dict[str, Dict[str, str]]]:
    content = read_text(path)
    if content is None:
        raise FileNotFoundError(path)

    terminal_stages: Set[str] = set()
    stages: Dict[str, Dict[str, str]] = {}
    in_terminal = False
    in_stages = False
    in_next = False
    current_stage: Optional[str] = None

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))

        if indent == 2 and stripped == "terminal_stages:":
            in_terminal = True
            continue
        if in_terminal:
            if indent == 4 and stripped.startswith("- "):
                terminal_stages.add(stripped[2:].strip())
                continue
            if indent <= 2:
                in_terminal = False

        if indent == 2 and stripped == "stages:":
            in_stages = True
            current_stage = None
            continue
        if not in_stages:
            continue
        if indent <= 2 and stripped != "stages:":
            in_stages = False
            current_stage = None
            in_next = False
            continue
        if indent == 4 and stripped.endswith(":"):
            current_stage = stripped[:-1]
            stages.setdefault(current_stage, {})
            in_next = False
            continue
        if current_stage and indent == 6 and stripped == "next:":
            in_next = True
            continue
        if current_stage and indent == 6 and stripped.endswith(":"):
            in_next = False
            continue
        if current_stage and in_next and indent == 8 and ":" in stripped:
            action, target = stripped.split(":", 1)
            stages[current_stage][action.strip()] = target.strip()

    return terminal_stages, stages


def find_row_by_value(rows: List[Dict[str, str]], value: str, *keys: str) -> Optional[Dict[str, str]]:
    for row in rows:
        if row_value(row, *keys) == value:
            return row
    return None


def gate_conclusion(review: Optional[str], gate: str) -> Optional[str]:
    if review is None:
        return None
    row = find_row_by_value(section_rows(review, "Gate Approvals"), gate, "Gate", "关口")
    return row_value(row, "Conclusion", "结论")


def stage_conclusion(review: Optional[str], stage: str) -> Optional[str]:
    if review is None:
        return None
    row = find_row_by_value(section_rows(review, "阶段结论"), stage, "阶段", "Stage")
    return row_value(row, "结论", "Conclusion")


def is_advancing_action(action: str) -> bool:
    normalized = normalized_status(action)
    return normalized not in NON_ADVANCING_ACTIONS and not normalized.startswith("return")


def confirmation_rejected(value: Optional[str]) -> bool:
    text = normalized_status(value)
    return text in {"not confirmed", "unconfirmed", "rejected", "denied", "no", "未确认", "未同意", "拒绝"}


def stage_pause_confirmation_row(
    review: Optional[str],
    from_stage: str,
    action: str,
    to_stage: str,
) -> Optional[Dict[str, str]]:
    if review is None:
        return None
    for row in section_rows(review, "Stage Pause Confirmations"):
        stage = row_value(row, "Stage", "阶段")
        row_action = row_value(row, "Action", "动作")
        next_stage = row_value(row, "Next Stage", "下一阶段")
        if stage == from_stage and row_action == action and next_stage == to_stage:
            return row
    return None


def require_stage_pause_confirmation(
    review: Optional[str],
    from_stage: str,
    action: str,
    to_stage: str,
    failures: List[str],
) -> None:
    if not is_advancing_action(action):
        return
    if review is None:
        return

    rows = section_rows(review, "Stage Pause Confirmations")
    if not rows:
        failures.append("缺少 Stage Pause Confirmations / 阶段暂停确认表；推进阶段前必须记录已向用户展示并获得确认")
        return

    row = stage_pause_confirmation_row(review, from_stage, action, to_stage)
    if row is None:
        failures.append(f"缺少阶段暂停确认记录：{from_stage} --{action}-> {to_stage}")
        return

    deliverables = row_value(row, "Deliverables", "交付物")
    summary = row_value(row, "Summary Shown", "展示摘要", "展示内容", "关键摘要")
    confirmation = row_value(row, "User Confirmation", "用户确认", "确认依据")
    recorded_at = row_value(row, "Recorded At", "记录时间")

    if not is_filled(deliverables):
        failures.append(f"{from_stage} 阶段暂停确认必须填写已完成交付物")
    if not is_filled(summary):
        failures.append(f"{from_stage} 阶段暂停确认必须填写已向用户展示的摘要")
    if not is_filled(confirmation) or confirmation_rejected(confirmation):
        failures.append(f"{from_stage} 阶段暂停确认必须记录用户明确同意推进")
    if "PRD 自动入口授权" in (confirmation or ""):
        failures.append(f"{from_stage} 阶段暂停确认不能使用 PRD 自动入口授权替代用户明确同意推进")
    if not is_filled(recorded_at):
        failures.append(f"{from_stage} 阶段暂停确认必须填写记录时间")


def require_review_conclusion(
    review: Optional[str],
    from_stage: str,
    action: str,
    failures: List[str],
) -> None:
    if review is None:
        failures.append("缺少 workflow/changes/<CR-ID>/review.md，无法确认阶段或关口结论")
        return

    if action == "approve" and from_stage in {"INIT", "REQ_GATE", "DESIGN_GATE", "RELEASE_GATE"}:
        conclusion = gate_conclusion(review, from_stage)
        if conclusion != "passed":
            failures.append(f"{from_stage} 关口结论必须是 passed，当前是：{conclusion}")
        return

    if action == "submit":
        conclusion = stage_conclusion(review, from_stage)
        if normalized_status(conclusion) not in {"ready", "submitted", "passed", "delivered"}:
            failures.append(
                f"{from_stage} 阶段结论必须是 ready、submitted、passed 或 delivered，当前是：{conclusion}"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查 workflow 阶段流转是否符合 workflow.config.yaml。")
    parser.add_argument("--project-root", default="", help="项目根目录，默认从 tools/ 推断。")
    parser.add_argument("--change-id", required=True, help="workflow CR 编号，例如 CR-001。")
    parser.add_argument("--change", default="", help="OpenSpec change 目录名；提供时会校验当前激活的 OpenSpec change。")
    parser.add_argument("--from-stage", default="", help="来源阶段；默认读取 workflow/state.md 的当前阶段。")
    parser.add_argument("--to-stage", required=True, help="目标阶段，例如 DESIGN。")
    parser.add_argument("--action", required=True, help="流转动作，例如 submit、approve、return_requirement。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    failures: List[str] = []

    try:
        terminal_stages, stages = parse_workflow_config(project_root / "workflow" / "workflow.config.yaml")
    except FileNotFoundError:
        failures.append("缺少 workflow/workflow.config.yaml")
        terminal_stages, stages = set(), {}

    state = read_text(project_root / "workflow" / "state.md")
    current_stage: Optional[str] = None
    if state is None:
        failures.append("缺少 workflow/state.md")
    else:
        current_stage = state_value(state, "当前阶段")
        from_stage = args.from_stage or current_stage or ""
        if current_stage != from_stage:
            failures.append(f"workflow/state.md 当前阶段必须是 {from_stage}，当前是：{current_stage}")

        expected_evidence = f"workflow/changes/{args.change_id}"
        active_evidence = state_value(state, "当前变更")
        if not ref_matches(active_evidence, expected_evidence):
            failures.append(f"当前变更必须是 {expected_evidence}，当前是：{active_evidence}")

        if args.change:
            expected_openspec = f"openspec/changes/{args.change}"
            active_openspec = state_value(state, "当前 OpenSpec Change")
            if not ref_matches(active_openspec, expected_openspec):
                failures.append(f"当前 OpenSpec Change 必须是 {expected_openspec}，当前是：{active_openspec}")

    from_stage = args.from_stage or current_stage or ""
    if from_stage not in stages:
        if from_stage not in terminal_stages:
            failures.append(f"workflow.config.yaml 中不存在来源阶段：{from_stage}")
    else:
        next_map = stages[from_stage]
        expected_target = next_map.get(args.action)
        if expected_target is None:
            allowed = ", ".join(f"{action}->{target}" for action, target in sorted(next_map.items()))
            failures.append(f"{from_stage} 不支持动作 {args.action}；允许的流转是：{allowed}")
        elif expected_target != args.to_stage:
            failures.append(
                f"{from_stage} 通过动作 {args.action} 只能流转到 {expected_target}，不能流转到 {args.to_stage}"
            )

    review = read_text(project_root / "workflow" / "changes" / args.change_id / "review.md")
    require_review_conclusion(review, from_stage, args.action, failures)
    require_stage_pause_confirmation(review, from_stage, args.action, args.to_stage, failures)

    if failures:
        print("阶段流转检查：未通过")
        for failure in failures:
            print(f"- {failure}")
        print("不得推进 workflow/state.md；请补齐阶段暂停确认、对应阶段/关口结论，或按 workflow.config.yaml 选择合法流转。")
        return 1

    print("阶段流转检查：通过")
    print(f"允许通过动作 {args.action} 从 {from_stage} 流转到 {args.to_stage}。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
