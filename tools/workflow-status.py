#!/usr/bin/env python3
"""Print a read-only workflow status summary."""

import argparse
import sys
from pathlib import Path

from workflow_common import (
    command_base,
    current_task_id,
    dev_tasks,
    find_task,
    gate_conclusions,
    green_row,
    major_gaps,
    red_green_summary,
    red_row,
    rel_path,
    row_value,
    task_id,
    task_progress,
    task_status,
    test_artifact_row,
    load_context,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="输出当前 workflow 状态、关口结论和主要缺口。")
    parser.add_argument("--project-root", default="", help="项目根目录，默认从 tools/ 推断。")
    parser.add_argument("--change-id", default="", help="覆盖 workflow CR 编号，例如 CR-001。")
    parser.add_argument("--change", default="", help="覆盖 OpenSpec change 目录名。")
    parser.add_argument("--task-id", default="", help="覆盖当前任务；默认读取 workflow/state.md。")
    return parser.parse_args()


def state_label(value: object) -> str:
    if value == "ready":
        return "已记录"
    if value == "incomplete":
        return "不完整"
    if value == "missing":
        return "缺失"
    return str(value)


def print_status(project_root: Path, change_id: str, change: str, task_override: str) -> int:
    ctx = load_context(project_root, change_id, change)
    task = current_task_id(ctx, task_override)
    task_row = find_task(ctx.tasks, task)
    conclusions = gate_conclusions(ctx.review)
    progress = task_progress(ctx.tasks)

    print("工作流状态")
    print(f"- 当前阶段: {ctx.stage or '未知'}")
    print(f"- 当前关口: {ctx.gate or '未知'}")
    print(f"- 当前状态: {ctx.status or '未知'}")
    print(f"- 当前负责人: {ctx.owner or '未知'}")
    print(f"- 当前 CR: {ctx.change_id or '未知'}")
    print(f"- OpenSpec change: {ctx.change or '未知'}")
    print(f"- 当前任务: {task or '未设置'}")

    print("\n已读取证据")
    for path in (ctx.state_path, ctx.review_path, ctx.tasks_path, ctx.test_plan_path, ctx.acceptance_path):
        if path is None:
            continue
        status = "存在" if path.exists() else "缺失"
        print(f"- {rel_path(ctx.project_root, path)}: {status}")

    print("\n关口结论")
    for gate in ("INIT", "REQ_GATE", "DESIGN_GATE", "RELEASE_GATE"):
        print(f"- {gate}: {conclusions.get(gate) or '缺失'}")

    print("\nDEV 任务进度")
    print(
        "- 总数: {total}; 已完成: {completed}; Ready/Approved: {ready}; 进行中: {in_progress}; 其他: {other}".format(
            **progress
        )
    )
    for row in dev_tasks(ctx.tasks):
        marker = " <- 当前" if task_id(row) == task else ""
        print(f"- {task_id(row)}: {task_status(row) or '未知'}{marker}")

    print("\n当前任务证据")
    if not task:
        print("- 未设置当前任务，无法汇总 Red/Green。")
    elif task_row is None:
        print(f"- OpenSpec tasks.md 中未找到 {task}。")
    else:
        print(f"- 任务状态: {task_status(task_row) or '未知'}")
        print(f"- Owner Agent: {row_value(task_row, 'Owner Agent', '负责人 Agent', '负责人') or '缺失'}")
        print(f"- Allowed Write Scope: {row_value(task_row, 'Allowed Write Scope', '允许写入范围') or '缺失'}")
        artifact = test_artifact_row(ctx.test_plan, task)
        print(f"- 测试用例产物: {row_value(artifact, 'Test Case Artifact', '测试用例产物') or '缺失'}")
        rg = red_green_summary(ctx.test_plan, task)
        red = red_row(ctx.test_plan, task)
        green = green_row(ctx.test_plan, task)
        print(f"- Red 状态: {state_label(rg['red_state'])}; 记录状态: {row_value(red, 'Status', '状态') or '缺失'}")
        print(f"- Green 状态: {state_label(rg['green_state'])}; 记录状态: {row_value(green, 'Status', '状态') or '缺失'}")

    print("\n主要缺口")
    gaps = major_gaps(ctx, task_override)
    if not gaps:
        print("- 暂未发现主要缺口；仍以 readiness 命令结果为准。")
    else:
        for gap in gaps:
            print(f"- {gap}")

    if ctx.change_id:
        base = command_base(ctx.change_id, ctx.change)
        print("\n常用下一步入口")
        print(f"- python tools/workflow-next.py {base}")

    return 1 if ctx.errors else 0


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    return print_status(project_root, args.change_id, args.change, args.task_id)


if __name__ == "__main__":
    sys.exit(main())
