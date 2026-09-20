#!/usr/bin/env python3
"""检查 OpenSpec 任务是否具备声明完成的证据。"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


NOT_FILLED = "待填写"
NOT_CONFIRMED = "待确认"
BLANK_VALUES = {"", "Pending", "pending", "draft", "TBD", "TODO", "-", "none"}
PLACEHOLDER_COMMANDS = {
    "ai verified",
    "ai判断",
    "green",
    "manual",
    "n/a",
    "na",
    "pass",
    "passed",
    "pending",
    "recorded",
    "run test",
    "run tests",
    "tbd",
    "todo",
    "不适用",
    "人工确认",
    "已通过",
    "待填写",
    "待确认",
    "手工确认",
    "测试通过",
}
PLACEHOLDER_COMMAND_MARKERS = (
    "<command>",
    "<cmd>",
    "<fill",
    "example command",
    "placeholder",
    "replace me",
    "your command",
    "待填写",
    "待确认",
)
BACKFILLED_RED_MARKERS = (
    "backfill",
    "backfilled",
    "post-implementation",
    "retrospective",
    "retroactive",
    "after implementation",
    "事后",
    "后补",
    "补做",
    "补记",
    "倒填",
    "回填",
    "已实现后",
    "实现后补",
)
FORBIDDEN_COMMAND_PREFIXES = {"echo", "exit", "false", "pause", "printf", "sleep", "true", "write-output"}
REAL_COMMAND_PREFIXES = {
    "bash",
    "bun",
    "cargo",
    "cmd",
    "composer",
    "deno",
    "dotnet",
    "go",
    "gradle",
    "java",
    "jest",
    "make",
    "mvn",
    "node",
    "npm",
    "npx",
    "pnpm",
    "poetry",
    "powershell",
    "pwsh",
    "py",
    "php",
    "pytest",
    "python",
    "python3",
    "ruff",
    "sh",
    "tox",
    "uv",
    "vitest",
    "yarn",
}
DEFAULT_REAL_TEST_CONFIG = {
    "enabled": True,
    "test_case_artifact_must_exist": True,
    "commands_must_reference_test_artifact": True,
    "red_green_must_share_test_artifact": True,
    "acceptance_must_reference_green_evidence": True,
    "green_command_must_execute": True,
    "green_expected_exit_code": 0,
    "red_record_requires_real_command": True,
    "red_command_rerun": False,
    "red_expected_exit_code": "non_zero",
    "timeout_seconds": 120,
    "reject_placeholder_commands": True,
}
SECTION_ALIASES = {
    "Gate Approvals": ("Gate Approvals", "关口审批", "关口结论"),
    "Implementation Tasks": ("Implementation Tasks", "实现任务"),
    "Development Coverage Statements": ("Development Coverage Statements", "开发覆盖声明"),
    "Test Case Artifacts": ("Test Case Artifacts", "测试用例产物"),
    "Red Failure Records": ("Red Failure Records", "Red 失败记录", "实现前失败记录"),
    "Green Pass Records": ("Green Pass Records", "Green 通过记录", "实现后通过记录"),
    "Cannot Automate": ("Cannot Automate", "无法自动化"),
}
COVERAGE_ALLOWED_STATUSES = {
    "covered",
    "not_covered",
    "manual_pending",
    "deferred_with_approval",
    "out_of_scope_with_reason",
}
COVERAGE_COMPLETION_STATUSES = {
    "covered",
    "manual_pending",
    "deferred_with_approval",
    "out_of_scope_with_reason",
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


def has_backfilled_red_marker(value: Optional[str]) -> bool:
    text = (value or "").lower()
    return any(marker in text for marker in BACKFILLED_RED_MARKERS)


def parse_scalar(value: str) -> "str | bool | int":
    text = value.strip()
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    return text


def parse_real_test_config(path: Path, failures: List[str]) -> Dict[str, "str | bool | int"]:
    content = read_text(path)
    config: Dict[str, "str | bool | int"] = dict(DEFAULT_REAL_TEST_CONFIG)
    if content is None:
        failures.append("缺少 workflow/execution.config.yaml，无法读取真实测试验证配置")
        return config

    found = False
    in_section = False
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))

        if indent == 4 and stripped == "real_test_verification:":
            found = True
            in_section = True
            continue
        if not in_section:
            continue
        if indent <= 4:
            break
        if indent == 6 and ":" in stripped:
            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            if key in DEFAULT_REAL_TEST_CONFIG and raw_value:
                config[key] = parse_scalar(raw_value)

    if not found:
        failures.append("workflow/execution.config.yaml 缺少 task_completion_readiness.real_test_verification 配置")
    return config


def clean_command(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip()


def clean_artifact(value: str) -> str:
    text = value.replace("`", "").strip().strip("\"'")
    if text.startswith("<") and text.endswith(">"):
        text = text[1:-1].strip()
    return text


def split_test_artifacts(value: Optional[str]) -> List[str]:
    if value is None:
        return []
    text = value.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    link_targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    raw_items = link_targets if link_targets else re.split(r"[,;\n、]", text)
    artifacts: List[str] = []
    for raw_item in raw_items:
        artifact = clean_artifact(raw_item)
        if not is_filled(artifact):
            continue
        artifacts.append(artifact)
    return artifacts


def strip_path_fragment(path: str) -> str:
    return path.split("#", 1)[0]


def normalize_artifact_ref(path: str) -> str:
    return strip_path_fragment(clean_artifact(path)).replace("\\", "/").lstrip("./").rstrip("/")


def artifact_path(project_root: Path, artifact: str) -> Path:
    candidate = Path(strip_path_fragment(clean_artifact(artifact)))
    if candidate.is_absolute():
        return candidate
    return project_root / candidate


def validate_test_artifacts(
    project_root: Path,
    task_id: str,
    artifacts: List[str],
    require_exists: bool,
    failures: List[str],
) -> List[str]:
    normalized: List[str] = []
    for artifact in artifacts:
        artifact_ref = normalize_artifact_ref(artifact)
        normalized.append(artifact_ref)
        if not require_exists:
            continue
        if re.match(r"^[a-z]+://", artifact_ref, flags=re.IGNORECASE):
            failures.append(f"任务 {task_id} 自动化测试用例产物必须是本地文件或目录，当前是：{artifact}")
            continue
        if not artifact_path(project_root, artifact).exists():
            failures.append(f"任务 {task_id} 测试用例产物不存在：{artifact_ref}")
    return normalized


def command_path_tokens(command: str) -> List[str]:
    tokens = re.findall(r"""[^\s"'|&;]+""", command)
    paths: List[str] = []
    for token in tokens:
        cleaned = clean_artifact(token).rstrip(".,)")
        if not cleaned or cleaned.startswith("-"):
            continue
        normalized = normalize_artifact_ref(cleaned)
        if not normalized:
            continue
        if "/" in normalized or normalized.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".spec", ".test")):
            paths.append(normalized)
    return paths


def command_covers_artifact(command: str, artifact: str) -> bool:
    artifact_ref = normalize_artifact_ref(artifact)
    if not artifact_ref:
        return False
    command_ref = clean_command(command).replace("\\", "/").casefold()
    artifact_lower = artifact_ref.casefold()
    if artifact_lower in command_ref:
        return True
    for token in command_path_tokens(command):
        token_lower = token.casefold().rstrip("/")
        if token_lower and artifact_lower.startswith(token_lower + "/"):
            return True
    return False


def command_artifact_coverage(command: str, artifacts: List[str]) -> Set[str]:
    return {
        artifact
        for artifact in artifacts
        if command_covers_artifact(command, artifact)
    }


def validate_command_covers_artifacts(
    task_id: str,
    label: str,
    command: str,
    artifacts: List[str],
    failures: List[str],
) -> Set[str]:
    covered = command_artifact_coverage(command, artifacts)
    missing = [artifact for artifact in artifacts if artifact not in covered]
    if missing:
        failures.append(
            f"任务 {task_id} {label} 命令必须引用测试用例产物，未覆盖：{', '.join(missing)}"
        )
    return covered


def acceptance_references_green_evidence(
    acceptance_command: Optional[str],
    green_command: str,
    artifacts: List[str],
) -> bool:
    if not is_filled(acceptance_command):
        return False
    acceptance_text = clean_command(acceptance_command).replace("\\", "/").casefold()
    green_text = clean_command(green_command).replace("\\", "/").casefold()
    if green_text and green_text in acceptance_text:
        return True
    return bool(command_artifact_coverage(acceptance_text, artifacts))


def command_segments(command: str) -> List[str]:
    return [
        segment.strip()
        for segment in re.split(r"\s*(?:&&|\|\||;)\s*", command)
        if segment.strip()
    ]


def first_token(segment: str) -> str:
    match = re.match(r"""^\s*(['"]?)([^\s'"]+)\1""", segment)
    return match.group(2).strip() if match else ""


def looks_like_real_command(command: str) -> Tuple[bool, str]:
    text = clean_command(command)
    normalized = re.sub(r"\s+", " ", text).strip().casefold()
    if not normalized:
        return False, "命令为空"
    if "\n" in text or "\r" in text:
        return False, "命令不能是多行占位步骤"
    if normalized in PLACEHOLDER_COMMANDS:
        return False, "命令是占位文本"
    if any(marker in normalized for marker in PLACEHOLDER_COMMAND_MARKERS):
        return False, "命令包含占位标记"

    valid_segment_seen = False
    for segment in command_segments(text):
        token = first_token(segment)
        normalized_token = Path(token).name.casefold()
        normalized_token = re.sub(r"\.exe$", "", normalized_token)
        if normalized_token in {"cd", "pushd", "popd"}:
            continue
        if normalized_token in FORBIDDEN_COMMAND_PREFIXES:
            return False, f"命令不能只用 {token} 冒充测试"
        if normalized_token in REAL_COMMAND_PREFIXES:
            valid_segment_seen = True
            continue
        token_text = token.replace("\\", "/").casefold()
        if token_text.startswith(("./", "../", "scripts/")):
            valid_segment_seen = True
            continue
        if token_text.endswith((".bat", ".cmd", ".ps1", ".py", ".sh")):
            valid_segment_seen = True
            continue

    if not valid_segment_seen:
        return False, "命令不是可识别的本地测试命令"
    return True, ""


def add_command_failure(
    failures: List[str],
    command: Optional[str],
    message_prefix: str,
    reject_placeholder_commands: bool,
) -> str:
    cleaned = clean_command(command)
    if not is_filled(cleaned):
        failures.append(f"{message_prefix}必须填写真实命令")
        return cleaned
    if reject_placeholder_commands:
        ok, reason = looks_like_real_command(cleaned)
        if not ok:
            failures.append(f"{message_prefix}不是有效真实命令：{reason}；当前是：{cleaned}")
    return cleaned


def command_output_excerpt(stdout: Optional[str], stderr: Optional[str], limit: int = 800) -> str:
    output = "\n".join(part for part in (stdout, stderr) if part)
    output = output.strip()
    if not output:
        return "无输出"
    if len(output) > limit:
        return output[:limit] + "...(已截断)"
    return output


def run_recorded_command(
    command: str,
    project_root: Path,
    timeout_seconds: int,
) -> "subprocess.CompletedProcess[str] | subprocess.TimeoutExpired":
    import tempfile, os, signal, tty, pty
    stdout_fd, stdout_path = tempfile.mkstemp(prefix="readiness_stdout_")
    stderr_fd, stderr_path = tempfile.mkstemp(prefix="readiness_stderr_")
    os.close(stdout_fd)
    os.close(stderr_fd)
    master_fd, slave_fd = pty.openpty()
    stdout_file = open(stdout_path, "w")
    stderr_file = open(stderr_path, "w")
    proc = subprocess.Popen(
        command,
        cwd=str(project_root),
        shell=True,
        stdout=slave_fd,
        stderr=slave_fd,
        stdin=slave_fd,
        close_fds=True,
        preexec_fn=os.setsid,
    )
    os.close(slave_fd)
    import select
    output_buf = []
    start_time = __import__("time").time()
    timed_out = False
    while True:
        elapsed = __import__("time").time() - start_time
        if elapsed > timeout_seconds:
            timed_out = True
            break
        rlist, _, _ = select.select([master_fd], [], [], 1.0)
        if rlist:
            try:
                data = os.read(master_fd, 4096)
                if not data:
                    break
                text = data.decode("utf-8", errors="replace")
                output_buf.append(text)
                stdout_file.write(text)
                stdout_file.flush()
            except OSError:
                break
        result_code = proc.poll()
        if result_code is not None:
            # Drain remaining output
            while True:
                rlist, _, _ = select.select([master_fd], [], [], 0.5)
                if not rlist:
                    break
                try:
                    data = os.read(master_fd, 4096)
                    if not data:
                        break
                    text = data.decode("utf-8", errors="replace")
                    output_buf.append(text)
                    stdout_file.write(text)
                    stdout_file.flush()
                except OSError:
                    break
            break
    if timed_out:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
        except Exception:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass
    try:
        os.close(master_fd)
    except OSError:
        pass
    stdout_file.close()
    stderr_file.close()
    output_text = "".join(output_buf)
    try:
        os.unlink(stdout_path)
        os.unlink(stderr_path)
    except OSError:
        pass
    if timed_out:
        raise subprocess.TimeoutExpired(command, timeout_seconds, output=output_text, stderr="")
    return subprocess.CompletedProcess(
        args=command,
        returncode=proc.returncode if proc.returncode is not None else -1,
        stdout=output_text,
        stderr="",
    )


def bool_config(config: Dict[str, "str | bool | int"], key: str, default: bool) -> bool:
    value = config.get(key, default)
    return value if isinstance(value, bool) else default


def int_config(config: Dict[str, "str | bool | int"], key: str, default: int) -> int:
    value = config.get(key, default)
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def command_exit_matches(expected: "str | bool | Optional[int]", returncode: int) -> bool:
    if isinstance(expected, int) and not isinstance(expected, bool):
        return returncode == expected
    if isinstance(expected, str) and expected.casefold() == "non_zero":
        return returncode != 0
    return returncode == 0


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


def normalized_cell(value: Optional[str]) -> str:
    return (value or "").replace("`", "").strip().lower()


def none_like(value: Optional[str]) -> bool:
    return normalized_cell(value) in {"无", "none", "n/a", "na", "-", "not applicable", "不适用"}


def table_row(rows: List[Dict[str, str]], value: str, *keys: str) -> Optional[Dict[str, str]]:
    for row in rows:
        if row_value(row, *keys) == value:
            return row
    return None


def add_if_blank(failures: List[str], value: Optional[str], message: str) -> None:
    if not is_filled(value):
        failures.append(message)


def state_value(content: str, label: str) -> Optional[str]:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*(.+?)\s*$", content)
    return match.group(1).strip() if match else None


def normalize_ref(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.replace("`", "").strip().replace("\\", "/").lstrip("./").rstrip("/")


def ref_matches(value: Optional[str], expected: str) -> bool:
    return normalize_ref(value) == normalize_ref(expected)


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


def gate_conclusion(review: Optional[str], gate: str) -> Optional[str]:
    if review is None:
        return None
    row = table_row(section_rows(review, "Gate Approvals"), gate, "Gate", "关口")
    return row_value(row, "Conclusion", "结论")


def cell_codes(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return re.findall(r"\b[A-Z][A-Z0-9_]*-[A-Z0-9_.-]+\b", value)


def cell_acceptance_ids(value: Optional[str]) -> List[str]:
    return [code for code in cell_codes(value) if code.startswith("AC-")]


def acceptance_row_by_id(rows: List[Dict[str, str]], acceptance_id: str) -> Optional[Dict[str, str]]:
    for row in rows:
        if row_value(row, "验收编号", "Acceptance ID") == acceptance_id:
            return row
    return None


def row_acceptance_set(row: Optional[Dict[str, str]], *keys: str) -> Set[str]:
    return set(cell_acceptance_ids(row_value(row, *keys)))


def coverage_status(row: Optional[Dict[str, str]]) -> str:
    return normalized_cell(row_value(row, "覆盖状态", "Coverage Status"))


def check_development_coverage_statement(
    review: Optional[str],
    task_id: str,
    acceptance_ids: List[str],
    acceptance_rows: List[Dict[str, str]],
    failures: List[str],
) -> None:
    if review is None:
        return
    rows = section_rows(review, "Development Coverage Statements")
    if not rows:
        failures.append("review.md 缺少开发覆盖声明表")
        return
    row = table_row(rows, task_id, "任务编号", "Task ID")
    if row is None:
        failures.append(f"任务 {task_id} 必须在 review.md 的开发覆盖声明表中记录覆盖声明")
        return

    required_fields = (
        ("已实现 AC", "Implemented AC"),
        ("已测试 AC", "Tested AC"),
        ("未实现 AC", "Unimplemented AC"),
        ("未测试 AC", "Untested AC"),
        ("已运行命令", "Commands Run"),
        ("需要人工验收", "Manual Validation Required"),
        ("已知风险", "Known Risk"),
    )
    for keys in required_fields:
        if not is_filled(row_value(row, *keys)):
            failures.append(f"任务 {task_id} 开发覆盖声明必须填写 {keys[0]}")

    implemented = row_acceptance_set(row, "已实现 AC", "Implemented AC")
    tested = row_acceptance_set(row, "已测试 AC", "Tested AC")
    unimplemented = row_acceptance_set(row, "未实现 AC", "Unimplemented AC")
    untested = row_acceptance_set(row, "未测试 AC", "Untested AC")
    manual_required = row_acceptance_set(row, "需要人工验收", "Manual Validation Required")

    for acceptance_id in acceptance_ids:
        row_for_acceptance = acceptance_row_by_id(acceptance_rows, acceptance_id)
        status = coverage_status(row_for_acceptance)
        if status not in COVERAGE_ALLOWED_STATUSES:
            failures.append(f"验收项 {acceptance_id} 覆盖状态非法或为空：{status or '缺失'}")
            continue
        if status not in COVERAGE_COMPLETION_STATUSES:
            failures.append(f"任务 {task_id} 不能声明完成：验收项 {acceptance_id} 覆盖状态仍是 {status}")

        if acceptance_id not in implemented and acceptance_id not in unimplemented:
            failures.append(f"任务 {task_id} 覆盖声明必须说明 {acceptance_id} 已实现或未实现")
        if acceptance_id not in tested and acceptance_id not in untested and acceptance_id not in manual_required:
            failures.append(f"任务 {task_id} 覆盖声明必须说明 {acceptance_id} 已测试、未测试或需要人工验收")

        if acceptance_id in unimplemented and status not in {"deferred_with_approval", "out_of_scope_with_reason"}:
            failures.append(
                f"任务 {task_id} 声明 {acceptance_id} 未实现时，acceptance.md 覆盖状态必须是 deferred_with_approval 或 out_of_scope_with_reason"
            )
        if acceptance_id in untested and status not in {"manual_pending", "deferred_with_approval", "out_of_scope_with_reason"}:
            failures.append(
                f"任务 {task_id} 声明 {acceptance_id} 未测试时，acceptance.md 覆盖状态必须是 manual_pending、deferred_with_approval 或 out_of_scope_with_reason"
            )
        if status == "covered" and (acceptance_id not in implemented or acceptance_id not in tested):
            failures.append(f"验收项 {acceptance_id} 标为 covered 时，开发覆盖声明必须同时列入已实现 AC 和已测试 AC")


def check_agent_run_log(project_root: Path, change_id: str, task_id: str, failures: List[str]) -> None:
    logs_dir = project_root / "workflow" / "changes" / change_id / "logs" / "agent-runs"
    if not logs_dir.exists():
        failures.append(f"缺少 Agent Run Log 目录：workflow/changes/{change_id}/logs/agent-runs/")
        return
    for log_path in logs_dir.glob("*.md"):
        if task_id in log_path.name:
            return
        content = read_text(log_path) or ""
        if task_id in content:
            return
    failures.append(f"任务 {task_id} 必须有对应 Agent Run Log")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查任务是否可以声明完成。")
    parser.add_argument("--project-root", default="", help="项目根目录，默认从 tools/ 推断。")
    parser.add_argument("--change-id", required=True, help="workflow CR 编号，例如 CR-001。")
    parser.add_argument("--change", default="", help="OpenSpec change 目录名；未传时按 CR 前缀查找。")
    parser.add_argument("--task-id", required=True, help="OpenSpec 任务编号，例如 DEV-001。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    failures: List[str] = []
    real_test_config = parse_real_test_config(project_root / "workflow" / "execution.config.yaml", failures)
    reject_placeholder_commands = bool_config(real_test_config, "reject_placeholder_commands", True)
    red_record_requires_real_command = bool_config(real_test_config, "red_record_requires_real_command", True)
    timeout_seconds = int_config(real_test_config, "timeout_seconds", 120)
    green_command = ""
    green_command_ready = False
    red_command = ""
    red_command_ready = False
    test_artifacts: List[str] = []
    red_covered_artifacts: Set[str] = set()
    green_covered_artifacts: Set[str] = set()

    state = read_text(project_root / "workflow" / "state.md")
    active_openspec_change: Optional[str] = None
    if state is None:
        failures.append("缺少 workflow/state.md")
    else:
        stage = state_value(state, "当前阶段")
        if stage != "DEVELOPMENT":
            failures.append(f"当前阶段必须是 DEVELOPMENT 才能声明开发任务完成，当前是：{stage}")
        expected_evidence = f"workflow/changes/{args.change_id}"
        active_evidence = state_value(state, "当前变更")
        if not ref_matches(active_evidence, expected_evidence):
            failures.append(f"当前变更必须是 {expected_evidence}，当前是：{active_evidence}")
        active_openspec_change = state_value(state, "当前 OpenSpec Change")

    review = read_text(project_root / "workflow" / "changes" / args.change_id / "review.md")
    if review is None:
        failures.append(f"缺少 workflow/changes/{args.change_id}/review.md")
    else:
        for gate in ("REQ_GATE", "DESIGN_GATE"):
            conclusion = gate_conclusion(review, gate)
            if conclusion != "passed":
                failures.append(f"{gate} 结论必须是 passed，当前是：{conclusion}")

    change_dir = find_openspec_change_dir(project_root, args.change_id, args.change or None)
    task: Optional[Dict[str, str]] = None
    linked_acceptance_ids: List[str] = []
    acceptance_rows: List[Dict[str, str]] = []
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
            task = table_row(section_rows(tasks, "Implementation Tasks"), args.task_id, "Task ID", "任务编号")
            if task is None:
                failures.append(f"任务 {args.task_id} 不存在于 {(change_dir / 'tasks.md').relative_to(project_root)}")
            else:
                status = row_value(task, "Status", "状态")
                if status not in {"Ready", "Approved", "In Progress", "Implemented", "Done", "Completed", "Delivered"}:
                    failures.append(f"任务 {args.task_id} 状态必须可执行或可完成，当前是：{status}")
                add_if_blank(failures, row_value(task, "Owner Agent", "负责人 Agent", "负责人"), f"任务 {args.task_id} 必须填写负责人 Agent")
                requirement_ref = row_value(task, "Requirement / AC", "关联验收项")
                add_if_blank(failures, requirement_ref, f"任务 {args.task_id} 必须绑定至少一个验收项 AC-*")
                linked_acceptance_ids = cell_acceptance_ids(requirement_ref)
                if not linked_acceptance_ids:
                    failures.append(f"任务 {args.task_id} 的关联验收项必须包含 AC-* 编号，当前是：{requirement_ref}")
                excluded_ref = row_value(task, "Excluded AC", "不覆盖验收项")
                if excluded_ref is None or not is_filled(excluded_ref):
                    failures.append(f"任务 {args.task_id} 必须显式填写不覆盖验收项；无不覆盖项时写 无")
                add_if_blank(failures, row_value(task, "Allowed Write Scope", "允许写入范围"), f"任务 {args.task_id} 必须填写允许写入范围")
                add_if_blank(failures, row_value(task, "Verification", "验证方式"), f"任务 {args.task_id} 必须填写验证方式")
                add_if_blank(failures, row_value(task, "Rollback / Revert Plan", "回滚 / 撤销方案"), f"任务 {args.task_id} 必须填写回滚或撤销方案")

    test_plan = read_text(project_root / "workflow" / "changes" / args.change_id / "test-plan.md")
    if test_plan is None:
        failures.append(f"缺少 workflow/changes/{args.change_id}/test-plan.md")
    else:
        artifact_row = table_row(section_rows(test_plan, "Test Case Artifacts"), args.task_id, "任务编号", "Task ID")
        if artifact_row is None:
            failures.append(f"任务 {args.task_id} 缺少测试用例产物记录")
        else:
            artifact_value = row_value(artifact_row, "测试用例产物", "Test Case Artifact")
            add_if_blank(failures, artifact_value, f"任务 {args.task_id} 测试用例产物不能为空")
            artifact_coverage = row_value(artifact_row, "覆盖验收项", "Acceptance IDs")
            add_if_blank(failures, artifact_coverage, f"任务 {args.task_id} 测试用例产物必须填写覆盖验收项")
            artifact_covered_ids = set(cell_acceptance_ids(artifact_coverage))
            for acceptance_id in linked_acceptance_ids:
                if acceptance_id not in artifact_covered_ids:
                    failures.append(f"任务 {args.task_id} 测试用例产物未覆盖绑定验收项 {acceptance_id}")
            artifact_status = row_value(artifact_row, "状态", "Status")
            if artifact_status not in {"Ready", "Approved", "Recorded"}:
                failures.append(f"任务 {args.task_id} 测试用例产物状态必须是 Ready、Approved 或 Recorded，当前是：{artifact_status}")

            artifact_type = (row_value(artifact_row, "类型", "Type") or "").lower()
            manual_only = ("manual" in artifact_type and "automated" not in artifact_type) or "cannot" in artifact_type
            test_artifacts = split_test_artifacts(artifact_value)
            if not manual_only:
                if not test_artifacts:
                    failures.append(f"任务 {args.task_id} 自动化测试必须填写至少一个测试用例产物")
                test_artifacts = validate_test_artifacts(
                    project_root,
                    args.task_id,
                    test_artifacts,
                    bool_config(real_test_config, "test_case_artifact_must_exist", True),
                    failures,
                )
            if manual_only:
                manual_row = table_row(section_rows(test_plan, "Cannot Automate"), args.task_id, "任务编号", "Task ID")
                if manual_row is None:
                    failures.append(f"任务 {args.task_id} 是人工验证时，必须填写无法自动化记录")
                else:
                    add_if_blank(failures, row_value(manual_row, "Reason", "原因"), f"任务 {args.task_id} 必须填写无法自动化原因")
                    add_if_blank(failures, row_value(manual_row, "Manual Verification Owner", "人工验证负责人"), f"任务 {args.task_id} 必须填写人工验证负责人")
                    add_if_blank(failures, row_value(manual_row, "验证记录", "Verification Record"), f"任务 {args.task_id} 必须填写人工验证记录")

        red_row = table_row(section_rows(test_plan, "Red Failure Records"), args.task_id, "任务编号", "Task ID")
        if red_row is None:
            failures.append(f"任务 {args.task_id} 缺少 Red 失败记录")
        else:
            add_if_blank(failures, row_value(red_row, "测试用例产物", "Test Case Artifact"), f"任务 {args.task_id} Red 记录必须关联测试用例产物")
            red_coverage = row_value(red_row, "覆盖验收项", "Acceptance IDs")
            add_if_blank(failures, red_coverage, f"任务 {args.task_id} Red 记录必须填写覆盖验收项")
            red_acceptance_ids = set(cell_acceptance_ids(red_coverage))
            for acceptance_id in linked_acceptance_ids:
                if acceptance_id not in red_acceptance_ids:
                    failures.append(f"任务 {args.task_id} Red 记录未覆盖绑定验收项 {acceptance_id}")
            if red_record_requires_real_command:
                red_command = add_command_failure(
                    failures,
                    row_value(red_row, "命令 / 步骤", "Command / Steps"),
                    f"任务 {args.task_id} Red 记录命令",
                    reject_placeholder_commands,
                )
            else:
                red_command = clean_command(row_value(red_row, "命令 / 步骤", "Command / Steps"))
                add_if_blank(failures, red_command, f"任务 {args.task_id} Red 记录必须填写命令或步骤")
            red_command_ready = bool(red_command) and (
                not reject_placeholder_commands or looks_like_real_command(red_command)[0]
            )
            add_if_blank(failures, row_value(red_row, "失败摘要", "Failure Summary"), f"任务 {args.task_id} Red 记录必须填写失败摘要")
            add_if_blank(failures, row_value(red_row, "记录时间", "Recorded At"), f"任务 {args.task_id} Red 记录必须填写记录时间")
            red_status = row_value(red_row, "状态", "Status")
            if red_status not in {"Failed", "Red", "Recorded"}:
                failures.append(f"任务 {args.task_id} Red 状态必须是 Failed、Red 或 Recorded，当前是：{red_status}")
            if has_backfilled_red_marker(" ".join(red_row.values())):
                failures.append(
                    f"任务 {args.task_id} Red 记录包含事后补做/倒填标记，不能作为合规 TDD Red；"
                    "请记录 TDD 流程偏差，并补回归测试或从实现前基线重新取得真实 Red"
                )

        green_row = table_row(section_rows(test_plan, "Green Pass Records"), args.task_id, "任务编号", "Task ID")
        if green_row is None:
            failures.append(f"任务 {args.task_id} 缺少 Green 通过记录")
        else:
            add_if_blank(failures, row_value(green_row, "测试用例产物", "Test Case Artifact"), f"任务 {args.task_id} Green 记录必须关联测试用例产物")
            green_coverage = row_value(green_row, "覆盖验收项", "Acceptance IDs")
            add_if_blank(failures, green_coverage, f"任务 {args.task_id} Green 记录必须填写覆盖验收项")
            green_acceptance_ids = set(cell_acceptance_ids(green_coverage))
            for acceptance_id in linked_acceptance_ids:
                if acceptance_id not in green_acceptance_ids:
                    failures.append(f"任务 {args.task_id} Green 记录未覆盖绑定验收项 {acceptance_id}")
            green_command = add_command_failure(
                failures,
                row_value(green_row, "命令 / 步骤", "Command / Steps"),
                f"任务 {args.task_id} Green 记录命令",
                reject_placeholder_commands,
            )
            green_command_ready = bool(green_command) and (
                not reject_placeholder_commands or looks_like_real_command(green_command)[0]
            )
            add_if_blank(failures, row_value(green_row, "通过摘要", "Pass Summary"), f"任务 {args.task_id} Green 记录必须填写通过摘要")
            add_if_blank(failures, row_value(green_row, "记录时间", "Recorded At"), f"任务 {args.task_id} Green 记录必须填写记录时间")
            green_status = row_value(green_row, "状态", "Status")
            if green_status not in {"Passed", "Green", "Recorded", "通过", "已记录"}:
                failures.append(f"任务 {args.task_id} Green 状态必须是 Passed、Green 或 Recorded，当前是：{green_status}")

    if (
        bool_config(real_test_config, "enabled", True)
        and bool_config(real_test_config, "commands_must_reference_test_artifact", True)
        and test_artifacts
    ):
        if red_command:
            red_covered_artifacts = validate_command_covers_artifacts(
                args.task_id, "Red", red_command, test_artifacts, failures
            )
        if green_command:
            green_covered_artifacts = validate_command_covers_artifacts(
                args.task_id, "Green", green_command, test_artifacts, failures
            )

    if (
        bool_config(real_test_config, "enabled", True)
        and bool_config(real_test_config, "red_green_must_share_test_artifact", True)
        and test_artifacts
        and red_command
        and green_command
    ):
        if not red_covered_artifacts:
            red_covered_artifacts = command_artifact_coverage(red_command, test_artifacts)
        if not green_covered_artifacts:
            green_covered_artifacts = command_artifact_coverage(green_command, test_artifacts)
        shared_artifacts = red_covered_artifacts & green_covered_artifacts
        if not shared_artifacts:
            failures.append(
                f"任务 {args.task_id} Red/Green 命令必须覆盖同一测试用例产物，"
                f"Red 覆盖：{', '.join(sorted(red_covered_artifacts)) or '无'}；"
                f"Green 覆盖：{', '.join(sorted(green_covered_artifacts)) or '无'}"
            )

    if (
        bool_config(real_test_config, "enabled", True)
        and bool_config(real_test_config, "red_command_rerun", False)
        and red_command_ready
    ):
        try:
            red_result = run_recorded_command(red_command, project_root, timeout_seconds)
        except subprocess.TimeoutExpired as error:
            failures.append(
                f"任务 {args.task_id} Red 命令复跑超时：超过 {timeout_seconds}s；输出："
                f"{command_output_excerpt(error.stdout, error.stderr)}"
            )
        else:
            expected_red_exit_code = real_test_config.get("red_expected_exit_code", "non_zero")
            if not command_exit_matches(expected_red_exit_code, red_result.returncode):
                failures.append(
                    f"任务 {args.task_id} Red 命令复跑 exit code = {red_result.returncode}，"
                    f"期望 {expected_red_exit_code}；命令：{red_command}；"
                    f"输出：{command_output_excerpt(red_result.stdout, red_result.stderr)}"
                )

    if (
        bool_config(real_test_config, "enabled", True)
        and bool_config(real_test_config, "green_command_must_execute", True)
    ):
        if green_command_ready:
            expected_green_exit_code = int_config(real_test_config, "green_expected_exit_code", 0)
            try:
                green_result = run_recorded_command(green_command, project_root, timeout_seconds)
            except subprocess.TimeoutExpired as error:
                failures.append(
                    f"任务 {args.task_id} Green 命令真实执行超时：超过 {timeout_seconds}s；输出："
                    f"{command_output_excerpt(error.stdout, error.stderr)}"
                )
            else:
                if green_result.returncode != expected_green_exit_code:
                    failures.append(
                        f"任务 {args.task_id} Green 命令真实执行失败：exit code = {green_result.returncode}，"
                        f"期望 {expected_green_exit_code}；命令：{green_command}；"
                        f"输出：{command_output_excerpt(green_result.stdout, green_result.stderr)}"
                    )
        elif test_plan is not None:
            failures.append(f"任务 {args.task_id} Green 命令未通过真实命令校验，不能执行验证")

    acceptance = read_text(project_root / "workflow" / "changes" / args.change_id / "acceptance.md")
    if acceptance is None:
        failures.append(f"缺少 workflow/changes/{args.change_id}/acceptance.md")
    elif task is not None:
        acceptance_rows = top_table_rows(acceptance)
        if not linked_acceptance_ids:
            failures.append(f"任务 {args.task_id} 必须关联至少一个验收项 AC-*")
        for acceptance_id in linked_acceptance_ids:
            row = acceptance_row_by_id(acceptance_rows, acceptance_id)
            if row is None:
                failures.append(f"acceptance.md 缺少验收项 {acceptance_id}")
                continue
            task_ref = row_value(row, "OpenSpec Task", "开发任务", "绑定任务")
            if args.task_id not in cell_codes(task_ref):
                failures.append(f"验收项 {acceptance_id} 必须反向关联任务 {args.task_id}")
            acceptance_command = row_value(row, "测试用例 / 验证命令", "测试证据")
            add_if_blank(failures, acceptance_command, f"验收项 {acceptance_id} 必须填写测试用例或验证命令")
            if (
                bool_config(real_test_config, "enabled", True)
                and bool_config(real_test_config, "acceptance_must_reference_green_evidence", True)
                and is_filled(acceptance_command)
                and not acceptance_references_green_evidence(acceptance_command, green_command, test_artifacts)
            ):
                failures.append(
                    f"验收项 {acceptance_id} 的测试用例 / 验证命令必须引用 Green 命令或当前测试用例产物"
                )
            status = row_value(row, "状态", "Status")
            if status not in {"Implemented", "Verified"}:
                failures.append(f"验收项 {acceptance_id} 状态必须是 Implemented 或 Verified，当前是：{status}")
            current_coverage_status = coverage_status(row)
            if current_coverage_status not in COVERAGE_ALLOWED_STATUSES:
                failures.append(f"验收项 {acceptance_id} 覆盖状态非法或为空：{current_coverage_status or '缺失'}")
            elif current_coverage_status == "not_covered":
                failures.append(f"验收项 {acceptance_id} 覆盖状态仍是 not_covered，任务不得声明完成")
            if current_coverage_status in {"deferred_with_approval", "out_of_scope_with_reason"}:
                add_if_blank(failures, row_value(row, "未覆盖原因", "Uncovered Reason"), f"验收项 {acceptance_id} 必须填写未覆盖原因")
                add_if_blank(failures, row_value(row, "PL 处理", "PL Decision"), f"验收项 {acceptance_id} 必须填写 PL 处理")

    check_development_coverage_statement(
        review,
        args.task_id,
        linked_acceptance_ids,
        acceptance_rows,
        failures,
    )

    check_agent_run_log(project_root, args.change_id, args.task_id, failures)

    if failures:
        print("任务完成检查：未通过")
        for failure in failures:
            print(f"- {failure}")
        print("不得声明任务完成；请补齐测试产物、Red/Green 真实命令记录、Green 命令通过结果、验收追踪或 Agent Run Log。")
        return 1

    print("任务完成检查：通过")
    print(f"任务 {args.task_id} 可以根据当前证据声明完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
