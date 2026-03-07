#!/usr/bin/env python3
"""Validate workflow state machine gates for a project."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


UNRESOLVED_STATUSES = {"waiting_user", "approved", "in_progress", "verifying"}
HIGH_RISK_LEVELS = {"high", "critical"}


def parse_top_level_kv(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"missing file: {path}")

    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith(" ") or ":" not in raw:
            continue
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("- "):
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def parse_state_machine(path: Path) -> tuple[list[str], list[tuple[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f"missing state machine file: {path}")

    states: list[str] = []
    transitions: list[tuple[str, str]] = []
    section: str | None = None
    current_from: str | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        text = raw.strip()

        if indent == 0 and text.endswith(":"):
            section = text[:-1]
            current_from = None
            continue

        if section == "states" and indent == 2 and text.startswith("- "):
            states.append(text[2:].strip())
            continue

        if section == "transitions":
            if indent == 2 and text.startswith("- from:"):
                current_from = text.split(":", 1)[1].strip()
                continue
            if indent == 4 and text.startswith("to:") and current_from:
                to_stage = text.split(":", 1)[1].strip()
                transitions.append((current_from, to_stage))
                continue

    return states, transitions


def parse_issue_severity(issue_path: Path) -> str | None:
    content = issue_path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^# 严重程度\s*$\n([^\n]+)$", content)
    if not match:
        return None
    return match.group(1).strip().lower()


def scan_blocking_release_issues(issue_dir: Path) -> list[Path]:
    if not issue_dir.exists():
        return []

    blocked: list[Path] = []
    for issue_file in sorted(issue_dir.glob("*.md")):
        parts = issue_file.name.split("__", 2)
        if len(parts) != 3:
            continue
        status = parts[0]
        if status not in UNRESOLVED_STATUSES:
            continue
        severity = parse_issue_severity(issue_file)
        if severity in HIGH_RISK_LEVELS:
            blocked.append(issue_file)
    return blocked


def validate_required_files(project_root: Path, current_stage: str) -> list[str]:
    stage_requirements: dict[str, list[str]] = {
        "problem_definition": ["docs/idea.md"],
        "requirements": ["docs/problem.md"],
        "architecture": ["docs/spec.md"],
        "module_design": ["docs/architecture.md"],
        "task_planning": ["docs/module_design.md"],
        "implementation": ["docs/tasks.md", "_LLM/task_state.yaml"],
        "review": ["docs/tasks.md", "_LLM/task_state.yaml"],
        "testing": ["docs/tasks.md", "_LLM/task_state.yaml"],
        "issue_fixing": ["docs/tasks.md"],
        "refactoring": ["docs/tasks.md"],
        "release": ["docs/tasks.md"],
        "iteration": ["docs/tasks.md"],
    }
    missing: list[str] = []
    for rel in stage_requirements.get(current_stage, []):
        if not (project_root / rel).exists():
            missing.append(rel)
    return missing


def validate_transition_requirements(project_root: Path, current_stage: str, next_stage: str) -> list[str]:
    transition_requirements: dict[tuple[str, str], list[str]] = {
        ("idea", "problem_definition"): ["docs/idea.md"],
        ("problem_definition", "requirements"): ["docs/problem.md"],
        ("requirements", "architecture"): ["docs/spec.md"],
        ("architecture", "module_design"): ["docs/architecture.md"],
        ("module_design", "task_planning"): ["docs/module_design.md"],
        ("task_planning", "implementation"): ["docs/tasks.md", "_LLM/task_state.yaml"],
    }
    missing: list[str] = []
    for rel in transition_requirements.get((current_stage, next_stage), []):
        if not (project_root / rel).exists():
            missing.append(rel)
    return missing


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate workflow state and stage gates.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Target project root (default: current directory).",
    )
    parser.add_argument(
        "--next-stage",
        default=None,
        help="Optional next stage to validate transition legality.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()

    state_machine_path = project_root / "skill_cluster" / "system" / "workflow_state_machine.yaml"
    if not state_machine_path.exists():
        state_machine_path = (
            Path(__file__).resolve().parents[1] / "skill_cluster" / "system" / "workflow_state_machine.yaml"
        )

    project_state_path = project_root / "_LLM" / "project_state.yaml"
    task_state_path = project_root / "_LLM" / "task_state.yaml"
    issue_dir = project_root / "docs_issue"

    failures: list[str] = []

    if not project_state_path.exists():
        failures.append("missing _LLM/project_state.yaml")
    if not task_state_path.exists():
        failures.append("missing _LLM/task_state.yaml")
    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    states, transitions = parse_state_machine(state_machine_path)
    transition_set = set(transitions)

    project_state = parse_top_level_kv(project_state_path)
    current_stage = (project_state.get("current_stage") or "").strip()
    if not current_stage:
        failures.append("current_stage is empty in _LLM/project_state.yaml")
    elif current_stage not in states:
        failures.append(f"unknown current_stage: {current_stage}")

    missing_stage_files = validate_required_files(project_root, current_stage)
    for rel in missing_stage_files:
        failures.append(f"missing stage prerequisite for {current_stage}: {rel}")

    if args.next_stage:
        next_stage = args.next_stage.strip()
        if next_stage not in states:
            failures.append(f"unknown next stage: {next_stage}")
        elif (current_stage, next_stage) not in transition_set:
            failures.append(f"illegal transition: {current_stage} -> {next_stage}")
        for rel in validate_transition_requirements(project_root, current_stage, next_stage):
            failures.append(f"missing transition prerequisite for {current_stage}->{next_stage}: {rel}")

    release_gate_check = current_stage == "release" or args.next_stage == "release"
    if release_gate_check:
        blocked = scan_blocking_release_issues(issue_dir)
        for issue_file in blocked:
            failures.append(f"release blocked by unresolved high-risk issue: {issue_file.name}")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print(f"[PASS] current_stage valid: {current_stage}")
    if args.next_stage:
        print(f"[PASS] transition valid: {current_stage} -> {args.next_stage}")
    if release_gate_check:
        print("[PASS] no unresolved high-risk issues block release")
    return 0


if __name__ == "__main__":
    sys.exit(main())
