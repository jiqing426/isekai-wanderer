#!/usr/bin/env python3
"""Suggest the next read-only workflow action."""

import argparse
import sys
from pathlib import Path

from workflow_common import (
    command_base,
    current_task_id,
    find_task,
    gate_conclusions,
    green_row,
    handoff_summary,
    is_filled,
    major_gaps,
    next_dev_task,
    red_green_summary,
    red_row,
    rel_path,
    row_value,
    status_in,
    task_id,
    task_status,
    test_artifact_row,
    READY_STATUSES,
    IN_PROGRESS_STATUSES,
    COMPLETED_STATUSES,
    load_context,
)
from typing import Dict, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="基于当前 workflow 证据提示下一步 readiness 入口。")
    parser.add_argument("--project-root", default="", help="项目根目录，默认从 tools/ 推断。")
    parser.add_argument("--change-id", default="", help="覆盖 workflow CR 编号，例如 CR-001。")
    parser.add_argument("--change", default="", help="覆盖 OpenSpec change 目录名。")
    parser.add_argument("--task-id", default="", help="覆盖当前任务；默认读取 workflow/state.md。")
    return parser.parse_args()


def command(ctx_base: str, script: str, extra: str = "") -> str:
    suffix = f" {extra}" if extra else ""
    return f"python tools/{script} {ctx_base}{suffix}"


def first_scope_target(task_row: Optional[Dict[str, str]]) -> str:
    scope = row_value(task_row, "Allowed Write Scope", "允许写入范围") or ""
    for raw in scope.replace("\n", ",").split(","):
        item = raw.replace("`", "").strip()
        if item and item not in {".", "*", "**/*"}:
            return item
    return "<PATH>"


def print_missing(ctx) -> None:
    if not ctx.missing_files:
        return
    print("\n需要补齐或确认的文件")
    for path in ctx.missing_files:
        print(f"- 缺少必要文件: {path}")


def suggest_gate(ctx, gate_name: str, gate_arg: str, label: str) -> None:
    base = command_base(ctx.change_id, ctx.change)
    conclusions = gate_conclusions(ctx.review)
    print(f"下一步建议: 运行{label}检查")
    print(f"- 当前阶段: {ctx.stage or '未知'}")
    print(f"- 当前关口结论 {gate_name}: {conclusions.get(gate_name) or '缺失'}")
    if gate_name == "REQ_GATE":
        print(f"- 前置 INIT 结论: {conclusions.get('INIT') or '缺失'}")
    if gate_name == "DESIGN_GATE":
        print(f"- 前置 REQ_GATE 结论: {conclusions.get('REQ_GATE') or '缺失'}")
    if gate_name == "RELEASE_GATE":
        print(f"- 前置 DESIGN_GATE 结论: {conclusions.get('DESIGN_GATE') or '缺失'}")
    print("\n应执行")
    print(f"- {command(base, 'check-gate-readiness.py', f'--gate {gate_arg}')}")
    print_missing(ctx)


def suggest_development(ctx, task_override: str) -> None:
    base = command_base(ctx.change_id, ctx.change)
    task = current_task_id(ctx, task_override)
    task_row = find_task(ctx.tasks, task)
    print("下一步建议: DEVELOPMENT 任务准入与完成检查")
    print(f"- 当前任务: {task or '未设置'}")
    if task_row is None:
        print(f"- OpenSpec tasks.md 中未找到当前任务 {task or '<TASK-ID>'}。")
        print_missing(ctx)
        return

    print(f"- 任务状态: {task_status(task_row) or '未知'}")
    if not status_in(task_status(task_row), READY_STATUSES | IN_PROGRESS_STATUSES | COMPLETED_STATUSES):
        print(f"- 任务状态缺口: 当前状态不适合开始或声明完成。")

    handoff_state, handoff_gaps, previous = handoff_summary(ctx.review, ctx.tasks, task)
    if previous:
        print("\n准备开始当前 DEV 任务前")
        print(f"- {task} 是 {previous} 之后的 DEV 任务，需要 DEV handoff 检查。")
        print(f"- {command(base, 'check-dev-task-handoff-readiness.py', f'--next-task-id {task}')}")
        if handoff_state == "ready":
            print("- 当前记录看起来已补齐；仍以 readiness 命令结果为准。")
        else:
            for gap in handoff_gaps:
                print(f"- 缺口: {gap}")

    artifact = test_artifact_row(ctx.test_plan, task)
    rg = red_green_summary(ctx.test_plan, task)
    red = red_row(ctx.test_plan, task)
    green = green_row(ctx.test_plan, task)
    target = first_scope_target(task_row)

    print("\n代码准入")
    print(f"- {command(base, 'check-workflow-readiness.py', f'--task-id {task} --target-file {target}')}")
    if artifact is None:
        print(f"- 缺口: {task} 缺少测试用例产物记录。")
    elif not is_filled(row_value(artifact, "Test Case Artifact", "测试用例产物")):
        print(f"- 缺口: {task} 测试用例产物为空。")
    if rg["red_state"] != "ready":
        print("- Red/Green 缺口: Red 失败记录未补齐，补齐前不要写业务代码。")
        for gap in rg["red_gaps"]:
            print(f"- Red 缺口: {gap}")
    else:
        print(f"- Red 已记录: {row_value(red, 'Status', '状态') or '未知'}")

    print("\n任务完成")
    print(f"- {command(base, 'check-task-completion-readiness.py', f'--task-id {task}')}")
    if rg["green_state"] != "ready":
        print("- Red/Green 缺口: Green 通过记录未补齐，补齐前不要声明任务完成。")
        for gap in rg["green_gaps"]:
            print(f"- Green 缺口: {gap}")
    else:
        print(f"- Green 已记录: {row_value(green, 'Status', '状态') or '未知'}")

    next_task = next_dev_task(ctx.tasks, task)
    if next_task is not None and status_in(task_status(task_row), COMPLETED_STATUSES):
        next_id = task_id(next_task)
        print("\n准备进入下一个 DEV 任务")
        print(f"- 开始 {next_id} 前运行 DEV handoff 检查。")
        print(f"- {command(base, 'check-dev-task-handoff-readiness.py', f'--next-task-id {next_id}')}")

    gaps = major_gaps(ctx, task_override)
    if gaps:
        print("\n主要缺口")
        for gap in gaps:
            print(f"- {gap}")
    else:
        print_missing(ctx)


def suggest_general(ctx) -> None:
    base = command_base(ctx.change_id, ctx.change) if ctx.change_id else ""
    print("下一步建议: 先查看状态并补齐当前阶段证据")
    print(f"- 当前阶段: {ctx.stage or '未知'}")
    if base:
        print(f"- python tools/workflow-status.py {base}")
    print_missing(ctx)


def print_next(project_root: Path, change_id: str, change: str, task_override: str) -> int:
    ctx = load_context(project_root, change_id, change)
    print("工作流下一步入口")
    if ctx.errors:
        print("- 无法判断下一步，先修复必要状态信息。")
        for error in ctx.errors:
            print(f"- {error}")
        print_missing(ctx)
        return 1

    if ctx.stage == "REQ_GATE":
        suggest_gate(ctx, "REQ_GATE", "requirement", "需求关口")
    elif ctx.stage == "DESIGN_GATE":
        suggest_gate(ctx, "DESIGN_GATE", "design", "设计关口")
    elif ctx.stage == "RELEASE_GATE":
        suggest_gate(ctx, "RELEASE_GATE", "release", "发布关口")
    elif ctx.stage == "DEVELOPMENT":
        suggest_development(ctx, task_override)
    else:
        suggest_general(ctx)
    return 0


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    return print_next(project_root, args.change_id, args.change, args.task_id)


if __name__ == "__main__":
    sys.exit(main())
