#!/usr/bin/env python3
"""Check minimal required MSG bus + best-effort Feishu visibility readiness."""

import argparse
import sys
from pathlib import Path


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main():
    parser = argparse.ArgumentParser(description="Check communication readiness config and optional ledger.")
    parser.add_argument("--project-root", default=".", help="Generated project root.")
    parser.add_argument("--change-id", default="", help="Optional CR id for ledger check.")
    parser.add_argument("--require-ledger", action="store_true", help="Require workflow/changes/<CR-ID>/communication-ledger.md.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = project_root / "workflow" / "communication.config.yaml"
    problems = []
    if not config_path.exists():
        problems.append("Missing workflow/communication.config.yaml")
        config_text = ""
    else:
        config_text = read_text(config_path)

    if "provider: msg" not in config_text or "sessions_send" not in config_text:
        problems.append("Required bus must be msg / sessions_send")
    if "provider: feishu" not in config_text:
        problems.append("Visibility channel should be feishu")
    if "mode: group_chat" not in config_text:
        problems.append("Feishu visibility channel should be group_chat")
    if "require_ack: true" not in config_text:
        problems.append("Communication must require ack")
    if "all_cross_agent_messages_must_use_delivery_ledger: true" not in config_text:
        problems.append("Delivery ledger policy must be enabled")
    if "msg_required_for_delivery: true" not in config_text:
        problems.append("MSG required delivery policy must be enabled")
    if "cluster_connectivity_self_test_required: true" not in config_text:
        problems.append("Cluster connectivity self-test policy must be enabled")
    if "required_agent_ack_failure_blocks_prd_intake: true" not in config_text:
        problems.append("Required agent ack failure must block PRD intake")
    if "every_startup_role_ack_required_for_cluster_ready: true" not in config_text:
        problems.append("Every startup role must ack before cluster ready")
    if "no_oral_ack_without_msg_delivery: true" not in config_text:
        problems.append("Oral ack without MSG delivery must be forbidden")
    if "connectivity_self_test:" not in config_text:
        problems.append("Missing connectivity_self_test contract")
    if "ack_only: true" not in config_text:
        problems.append("Connectivity self-test must be ACK-only")
    if "ack_timeout_seconds: 15" not in config_text:
        problems.append("Connectivity self-test ACK timeout should be 15 seconds")
    if "dispatch_mode: parallel_when_supported" not in config_text:
        problems.append("Connectivity self-test should use parallel dispatch when supported")
    if "ACK cluster_connectivity_self_test <role>" not in config_text:
        problems.append("Connectivity self-test must define exact ACK template")
    if "source: workflow/cluster.config.yaml|connectivity_test_targets" not in config_text:
        problems.append("Connectivity self-test targets must come from connectivity_test_targets")
    if "owner_agent_excluded: true" not in config_text:
        problems.append("Connectivity self-test targets must exclude owner_agent")
    if "require_ack_from_each_connectivity_target: true" not in config_text:
        problems.append("Connectivity self-test must require ack from each connectivity target")
    if "coverage_rule:" not in config_text or "startup_order" not in config_text or "except owner_agent" not in config_text:
        problems.append("Connectivity self-test must require connectivity_test_targets to cover startup_order except owner_agent")
    if "health_sync_required: true" not in config_text:
        problems.append("Connectivity self-test must require health sync")
    if "prd_intake_allowed_when_ready: true" not in config_text:
        problems.append("PRD intake must only be allowed after health is ready")
    if "success_rule:" not in config_text or "cluster_status=ready" not in config_text:
        problems.append("Connectivity self-test must define a health success rule")

    if args.require_ledger:
        if not args.change_id:
            problems.append("--change-id is required with --require-ledger")
        else:
            ledger = project_root / "workflow" / "changes" / args.change_id / "communication-ledger.md"
            if not ledger.exists():
                problems.append("Missing communication ledger: %s" % ledger)

    if problems:
        print("Communication readiness: FAILED")
        for problem in problems:
            print("- %s" % problem)
        return 1

    print("Communication readiness: OK")
    print("Required bus: msg / sessions_send")
    print("Visibility channel: feishu group_chat")
    print("Connectivity self-test: required before PRD intake")
    return 0


if __name__ == "__main__":
    sys.exit(main())
