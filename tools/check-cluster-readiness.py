#!/usr/bin/env python3
"""Check minimal OpenClaw cluster readiness from project workflow config."""

import argparse
import sys
from pathlib import Path


DEFAULT_REQUIRED = ("hr", "ceo", "pl", "pm", "architect", "qa")
DEFAULT_ROLE_NAME_MAP = {
    "architect": "sa",
    "backend": "be",
    "frontend": "fe",
    "ops": "op",
    "ai-engineer": "ai",
}
DEFAULT_ROLE_TEMPLATE_DIR = {
    "sa": "architect",
    "architect": "architect",
    "be": "backend",
    "backend": "backend",
    "fe": "frontend",
    "frontend": "frontend",
    "op": "ops",
    "ops": "ops",
    "ai": "ai-engineer",
    "ai-engineer": "ai-engineer",
}

FORBIDDEN_ROLE_WORKSPACE_ENTRIES = (
    "workflow",
    "openspec",
    "docs",
    "tools",
    "skills",
    "backend",
    "frontend",
    "admin",
    "tests",
    "PROJECT.md",
)


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def normalize_prompt_text(text):
    return text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"


def strip_front_matter(text):
    lines = normalize_prompt_text(text).splitlines()
    if not lines or lines[0].strip() != "---":
        return "\n".join(lines).strip() + "\n"
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).strip() + "\n"
    return "\n".join(lines).strip() + "\n"


def expected_runtime_prompt(role_dir):
    agents_path = role_dir / "AGENTS.md"
    skill_path = role_dir / "SKILL.md"
    if not agents_path.exists() or not skill_path.exists():
        return "", ""
    soul_text = normalize_prompt_text(read_text(agents_path))
    skill_text = strip_front_matter(read_text(skill_path))
    agents_text = soul_text.rstrip() + "\n\n---\n\n" + skill_text.rstrip() + "\n"
    return agents_text, soul_text


def prompt_matches(path, expected):
    return normalize_prompt_text(read_text(path)) == normalize_prompt_text(expected)


def parse_scalar(text, key, default=""):
    prefix = key + ":"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):].strip().strip("\"'")
    return default


def looks_absolute_path(value):
    return value.startswith("/") or (len(value) > 2 and value[1] == ":" and value[2] in ("\\", "/"))


def parse_list(text, key, fallback):
    values = []
    in_key = False
    key_prefix = key + ":"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == key_prefix:
            in_key = True
            key_indent = len(line) - len(line.lstrip())
            continue
        if in_key:
            indent = len(line) - len(line.lstrip())
            if stripped.startswith("- "):
                values.append(stripped[2:].strip().strip("\"'"))
                continue
            if stripped and indent <= key_indent:
                break
    return values or list(fallback)


def parse_map(text, key, fallback):
    values = dict(fallback)
    in_key = False
    key_prefix = key + ":"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == key_prefix:
            in_key = True
            key_indent = len(line) - len(line.lstrip())
            continue
        if in_key:
            indent = len(line) - len(line.lstrip())
            if stripped and indent <= key_indent:
                break
            if ":" in stripped and not stripped.startswith("- "):
                alias_key, alias_value = [part.strip().strip("\"'") for part in stripped.split(":", 1)]
                if alias_key and alias_value:
                    values[alias_key] = alias_value
    return values


def parse_role_name_map(text, base=None):
    mapping = dict(DEFAULT_ROLE_NAME_MAP if base is None else base)
    if text:
        for item in text.split(","):
            item = item.strip()
            if not item:
                continue
            if "=" not in item:
                raise SystemExit("Invalid --role-name-map item, expected role=workspace_name: %s" % item)
            role, workspace_name = [part.strip() for part in item.split("=", 1)]
            if role and workspace_name:
                mapping[role] = workspace_name
    return mapping


def role_workspace_path(role, cluster_root, role_workspace_root, role_name_map):
    workspace_name = role_name_map.get(role, role)
    if role_workspace_root:
        return role_workspace_root / workspace_name
    return cluster_root / "agents" / workspace_name


def main():
    parser = argparse.ArgumentParser(description="Check OpenClaw cluster readiness config.")
    parser.add_argument("--project-root", default=".", help="Generated project root.")
    parser.add_argument("--cluster-root", default="", help="Optional cluster root to inspect.")
    parser.add_argument("--role-workspace-root", default="", help="Optional existing OpenClaw role workspace root, e.g. /root/.openclaw/workspace.")
    parser.add_argument("--role-name-map", default="", help="Comma-separated canonical-role=workspace-name overrides.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    cluster_root = Path(args.cluster_root).resolve() if args.cluster_root else None
    role_workspace_root = Path(args.role_workspace_root).resolve() if args.role_workspace_root else None
    role_name_map = parse_role_name_map(args.role_name_map)
    role_name_overrides = parse_role_name_map(args.role_name_map, {})
    problems = []

    cluster_config = project_root / "workflow" / "cluster.config.yaml"
    communication_config = project_root / "workflow" / "communication.config.yaml"
    if not cluster_config.exists():
        problems.append("Missing workflow/cluster.config.yaml")
        cluster_text = ""
    else:
        cluster_text = read_text(cluster_config)
    if not communication_config.exists():
        problems.append("Missing workflow/communication.config.yaml")
        communication_text = ""
    else:
        communication_text = read_text(communication_config)

    if parse_scalar(cluster_text, "owner_agent") != "hr":
        problems.append("cluster.owner_agent must be hr")
    if parse_scalar(cluster_text, "workflow_owner") != "pl":
        problems.append("cluster.workflow_owner must be pl")
    configured_cluster_root = parse_scalar(cluster_text, "cluster_root")
    if not configured_cluster_root or not looks_absolute_path(configured_cluster_root):
        problems.append("cluster.cluster_root must be an absolute path, e.g. /root/.openclaw/workspace/main/openclaw-clusters/main")
    if "/workspace/hr" in configured_cluster_root or "\\workspace\\hr" in configured_cluster_root:
        problems.append("cluster.cluster_root must not be inside the HR role workspace")
    if "provider: msg" not in communication_text or "sessions_send" not in communication_text:
        problems.append("communication required bus must include msg / sessions_send")
    if "provider: feishu" not in communication_text:
        problems.append("communication visibility channel should include feishu")
    if "cluster_connectivity_self_test_required: true" not in communication_text:
        problems.append("communication policy must require cluster connectivity self-test")
    if "ack_only: true" not in communication_text:
        problems.append("connectivity self-test must be ACK-only")
    if "ack_timeout_seconds: 15" not in communication_text:
        problems.append("connectivity self-test ACK timeout should be 15 seconds")
    if "dispatch_mode: parallel_when_supported" not in communication_text:
        problems.append("connectivity self-test should use parallel dispatch when supported")
    if "ACK cluster_connectivity_self_test <role>" not in communication_text:
        problems.append("connectivity self-test must define exact ACK template")
    if "required_agent_ack_failure_blocks_prd_intake: true" not in communication_text:
        problems.append("required agent ack failure must block PRD intake")
    if "health_sync_required: true" not in communication_text:
        problems.append("connectivity self-test must require health sync")
    if "prd_intake_allowed_when_ready: true" not in communication_text:
        problems.append("PRD intake must only be allowed after health is ready")
    permissions_text = read_text(project_root / "workflow" / "permissions.config.yaml")
    if "global_workspace_rule:" not in permissions_text:
        problems.append("permissions must define global_workspace_rule")
    if "role_workspace_is_runtime_shell_only: true" not in permissions_text:
        problems.append("role workspace must be runtime shell only")
    if "project_artifacts_must_be_under_canonical_project_root: true" not in permissions_text:
        problems.append("project artifacts must be restricted to canonical project root")
    if "hard_gate:" not in cluster_text or "connectivity self-test" not in cluster_text:
        problems.append("cluster hard_gate must require connectivity self-test")

    required_agents = parse_list(cluster_text, "required_agents", DEFAULT_REQUIRED)
    startup_order = parse_list(cluster_text, "startup_order", required_agents)
    owner_agent = parse_scalar(cluster_text, "owner_agent", "hr")
    aliases = parse_map(cluster_text, "aliases", role_name_map)
    aliases.update(role_name_overrides)
    role_to_template_dir = parse_map(cluster_text, "role_to_template_dir", DEFAULT_ROLE_TEMPLATE_DIR)
    connectivity_test_targets = parse_list(
        cluster_text,
        "connectivity_test_targets",
        [role for role in startup_order if role != owner_agent],
    )
    missing_required = [role for role in startup_order if role not in required_agents]
    if missing_required:
        problems.append(
            "required_agents must include every startup_order role for connectivity self-test: %s"
            % ", ".join(missing_required)
        )
    expected_targets = [role for role in startup_order if role != owner_agent]
    missing_targets = [role for role in expected_targets if role not in connectivity_test_targets]
    extra_targets = [role for role in connectivity_test_targets if role not in expected_targets]
    if missing_targets:
        problems.append(
            "connectivity_test_targets must include every startup_order role except owner_agent: %s"
            % ", ".join(missing_targets)
        )
    if extra_targets:
        problems.append(
            "connectivity_test_targets must not include owner_agent or non-startup roles: %s"
            % ", ".join(extra_targets)
        )
    for role in required_agents:
        template_dir = role_to_template_dir.get(role, role)
        role_dir = project_root / "skills" / template_dir
        for filename in ("AGENTS.md", "SKILL.md"):
            if not (role_dir / filename).exists():
                problems.append("Missing skills/%s/%s for role %s" % (template_dir, filename, role))
        if not (role_dir / "ROLE.md").exists():
            problems.append("Missing skills/%s/ROLE.md maintenance reference for role %s" % (template_dir, role))

    if cluster_root:
        for role in required_agents:
            role_workspace = role_workspace_path(role, cluster_root, role_workspace_root, aliases)
            template_dir = role_to_template_dir.get(role, role)
            role_dir = project_root / "skills" / template_dir
            expected_agents, expected_soul = expected_runtime_prompt(role_dir)
            if not role_workspace.exists():
                problems.append("Missing role workspace in cluster root: %s" % role_workspace)
                continue
            if not (role_workspace / "PROJECT_WORKSPACE.md").exists():
                problems.append("Missing PROJECT_WORKSPACE.md in role workspace: %s" % role_workspace)
            if not (role_workspace / "AGENTS.md").exists():
                problems.append("Missing root runtime prompt AGENTS.md in role workspace: %s" % role_workspace)
            elif expected_agents and not prompt_matches(role_workspace / "AGENTS.md", expected_agents):
                problems.append(
                    "Runtime prompt AGENTS.md for role %s is stale; HR must force-overwrite it from skills/%s/AGENTS.md + SKILL.md"
                    % (role, template_dir)
                )
            if not (role_workspace / "SOUL.md").exists():
                problems.append("Missing root runtime prompt SOUL.md in role workspace: %s" % role_workspace)
            elif expected_soul and not prompt_matches(role_workspace / "SOUL.md", expected_soul):
                problems.append(
                    "Runtime prompt SOUL.md for role %s is stale; HR must force-overwrite it from skills/%s/AGENTS.md"
                    % (role, template_dir)
                )
            if not (role_workspace / ".openclaw-agent" / "AGENTS.md").exists():
                problems.append("Missing compatibility runtime prompt .openclaw-agent/AGENTS.md in role workspace: %s" % role_workspace)
            elif expected_agents and not prompt_matches(role_workspace / ".openclaw-agent" / "AGENTS.md", expected_agents):
                problems.append(
                    "Compatibility prompt .openclaw-agent/AGENTS.md for role %s is stale; HR must force-overwrite it"
                    % role
                )
            if not (role_workspace / ".openclaw-agent" / "SOUL.md").exists():
                problems.append("Missing compatibility runtime prompt .openclaw-agent/SOUL.md in role workspace: %s" % role_workspace)
            elif expected_soul and not prompt_matches(role_workspace / ".openclaw-agent" / "SOUL.md", expected_soul):
                problems.append(
                    "Compatibility prompt .openclaw-agent/SOUL.md for role %s is stale; HR must force-overwrite it"
                    % role
                )
            for entry in FORBIDDEN_ROLE_WORKSPACE_ENTRIES:
                if (role_workspace / entry).exists():
                    problems.append("Role workspace contains forbidden project artifact path: %s" % (role_workspace / entry))
        plan = cluster_root / "runtime" / "openclaw-agent-plan.md"
        if not plan.exists():
            problems.append("Missing runtime/openclaw-agent-plan.md in cluster root")
        process_status = cluster_root / "runtime" / "openclaw-process-status.md"
        if not process_status.exists():
            problems.append("Missing runtime/openclaw-process-status.md in cluster root")

    if problems:
        print("Cluster readiness: FAILED")
        for problem in problems:
            print("- %s" % problem)
        return 1

    print("Cluster readiness: OK")
    print("Required agents: %s" % ", ".join(required_agents))
    return 0


if __name__ == "__main__":
    sys.exit(main())
