#!/usr/bin/env python3
"""Workflow runner for stage dispatch and post-stage hooks."""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path


def now_date() -> str:
    return dt.date.today().isoformat()


def parse_top_level_kv(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"missing file: {path}")

    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith(" ") or ":" not in raw:
            continue
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("- "):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def format_scalar(value: str | bool | None) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    if text == "":
        return '""'
    if any(ch in text for ch in (":", "#")) or text != text.strip():
        return f'"{text}"'
    return text


def update_top_level_kv(path: Path, updates: dict[str, str | bool | None]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    applied: set[str] = set()
    updated_lines: list[str] = []

    for raw in lines:
        if not raw or raw.startswith(" ") or ":" not in raw:
            updated_lines.append(raw)
            continue
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("- "):
            updated_lines.append(raw)
            continue
        key, _ = raw.split(":", 1)
        key = key.strip()
        if key in updates:
            updated_lines.append(f"{key}: {format_scalar(updates[key])}")
            applied.add(key)
        else:
            updated_lines.append(raw)

    for key, value in updates.items():
        if key not in applied:
            updated_lines.append(f"{key}: {format_scalar(value)}")

    path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    return default


def parse_dispatcher_routes(path: Path) -> tuple[dict[str, str | list[str]], dict[str, list[str]]]:
    if not path.exists():
        raise FileNotFoundError(f"missing dispatcher routes file: {path}")

    routes: dict[str, str | list[str]] = {}
    hooks: dict[str, list[str]] = {}
    section: str | None = None
    current_list_key: str | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        text = raw.strip()

        if indent == 0 and text.endswith(":"):
            section = text[:-1]
            current_list_key = None
            continue

        if section not in {"routes", "post_stage_hooks"}:
            continue

        target: dict[str, str | list[str]] = routes if section == "routes" else hooks
        if indent == 2 and ":" in text:
            key, value = text.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                target[key] = value
                current_list_key = None
            else:
                target[key] = []
                current_list_key = key
            continue

        if indent == 4 and text.startswith("- "):
            if current_list_key is None:
                raise ValueError(f"invalid list item without parent key: {raw}")
            current_value = target.get(current_list_key)
            if not isinstance(current_value, list):
                raise ValueError(f"parent key is not a list: {current_list_key}")
            current_value.append(text[2:].strip())
            continue

    typed_hooks: dict[str, list[str]] = {}
    for event, value in hooks.items():
        if isinstance(value, list):
            typed_hooks[event] = value
        else:
            typed_hooks[event] = [value]

    return routes, typed_hooks


def run_git(args: list[str], cwd: Path) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return 127, "git command not found"
    output = (proc.stdout or proc.stderr or "").strip()
    return proc.returncode, output


def is_git_repo(path: Path) -> bool:
    code, _ = run_git(["rev-parse", "--is-inside-work-tree"], path)
    return code == 0


def has_git_changes(path: Path) -> bool:
    code, output = run_git(["status", "--porcelain"], path)
    return code == 0 and bool(output.strip())


def has_git_remote(path: Path) -> bool:
    code, output = run_git(["remote"], path)
    return code == 0 and bool(output.strip())


def git_head_short(path: Path) -> str:
    code, output = run_git(["rev-parse", "--short", "HEAD"], path)
    if code != 0:
        return ""
    return output.strip()


def safe_token(raw: str | None, fallback: str) -> str:
    value = (raw or "").strip()
    if not value or value == "null":
        value = fallback
    return value.replace(" ", "-")


def build_commit_message(
    event: str,
    project_state: dict[str, str],
    task_state: dict[str, str],
    issue_id: str | None,
    release_tag: str | None,
    scope: str | None,
) -> str:
    if event == "task_completed":
        task_id = safe_token(task_state.get("current_task") or project_state.get("current_task"), "task")
        commit_scope = safe_token(scope, "task")
        return f"feat({commit_scope}): complete {task_id}"
    if event == "issue_resolved":
        resolved_issue = safe_token(issue_id, "tracked-issue")
        return f"fix(issue): resolve {resolved_issue}"
    if event == "release_checkpoint":
        tag = safe_token(release_tag, "checkpoint")
        return f"chore(release): checkpoint {tag}"
    return f"chore(workflow): run {safe_token(event, 'hook')}"


def execute_git_commit_push(
    project_root: Path,
    event: str,
    issue_id: str | None,
    release_tag: str | None,
    scope: str | None,
    dry_run: bool,
) -> int:
    git_state_path = project_root / "_LLM" / "git_state.yaml"
    project_state_path = project_root / "_LLM" / "project_state.yaml"
    task_state_path = project_root / "_LLM" / "task_state.yaml"

    git_state = parse_top_level_kv(git_state_path)
    enabled = parse_bool(git_state.get("enabled"), default=True)
    auto_commit = parse_bool(git_state.get("auto_commit"), default=True)
    push_mode = (git_state.get("push_mode") or "if_remote").strip()

    if not enabled:
        print("[SKIP] git hook disabled by _LLM/git_state.yaml (enabled=false)")
        return 0
    if not auto_commit:
        print("[SKIP] git hook disabled by _LLM/git_state.yaml (auto_commit=false)")
        return 0
    if not is_git_repo(project_root):
        print("[ERROR] current project is not a git repository")
        return 1
    if not has_git_changes(project_root):
        update_top_level_kv(
            git_state_path,
            {
                "last_push_status": "skipped:no_changes",
                "last_updated": now_date(),
            },
        )
        print("[SKIP] no changes to commit")
        return 0

    project_state = parse_top_level_kv(project_state_path)
    task_state = parse_top_level_kv(task_state_path)
    commit_message = build_commit_message(
        event=event,
        project_state=project_state,
        task_state=task_state,
        issue_id=issue_id,
        release_tag=release_tag,
        scope=scope,
    )

    if dry_run:
        print(f"[DRY RUN] would commit with message: {commit_message}")
        return 0

    add_code, add_output = run_git(["add", "-A"], project_root)
    if add_code != 0:
        print(f"[ERROR] git add failed: {add_output}")
        return 1

    commit_code, commit_output = run_git(["commit", "-m", commit_message], project_root)
    if commit_code != 0:
        print(f"[ERROR] git commit failed: {commit_output}")
        return 1

    push_status = "skipped:push_mode_never"
    push_failed = False

    if push_mode == "never":
        push_status = "skipped:push_mode_never"
    elif push_mode == "if_remote":
        if not has_git_remote(project_root):
            push_status = "skipped:no_remote"
        else:
            push_code, push_output = run_git(["push"], project_root)
            if push_code == 0:
                push_status = "pushed"
            else:
                push_status = f"failed:{push_output}"
                push_failed = False
    elif push_mode == "always":
        push_code, push_output = run_git(["push"], project_root)
        if push_code == 0:
            push_status = "pushed"
        else:
            push_status = f"failed:{push_output}"
            push_failed = True
    else:
        push_status = f"skipped:unknown_push_mode:{push_mode}"

    update_top_level_kv(
        git_state_path,
        {
            "last_commit": git_head_short(project_root),
            "last_push_status": push_status,
            "last_updated": now_date(),
        },
    )

    print(f"[DONE] git commit created: {commit_message}")
    print(f"[DONE] push_status: {push_status}")
    return 1 if push_failed else 0


def run_dispatch(project_root: Path) -> int:
    project_state_path = project_root / "_LLM" / "project_state.yaml"
    dispatcher_path = project_root / "skill_cluster" / "system" / "dispatcher_routes.yaml"
    if not dispatcher_path.exists():
        # fallback to current repository root layout (when called from this repo)
        dispatcher_path = Path(__file__).resolve().parents[1] / "skill_cluster" / "system" / "dispatcher_routes.yaml"

    project_state = parse_top_level_kv(project_state_path)
    routes, _ = parse_dispatcher_routes(dispatcher_path)
    current_stage = project_state.get("current_stage")
    if not current_stage:
        print("[ERROR] current_stage missing in _LLM/project_state.yaml")
        return 1

    route = routes.get(current_stage)
    if route is None:
        print(f"[ERROR] no route found for stage: {current_stage}")
        return 1

    pipeline = route if isinstance(route, list) else [route]
    active_skill = pipeline[0]
    update_top_level_kv(
        project_state_path,
        {
            "active_skill": active_skill,
            "last_updated": now_date(),
            "notes": f"dispatch stage {current_stage} -> {' -> '.join(pipeline)}",
        },
    )

    print(f"[DONE] current_stage: {current_stage}")
    print(f"[DONE] active_skill: {active_skill}")
    print(f"[DONE] pipeline: {' -> '.join(pipeline)}")
    return 0


def run_hook(
    project_root: Path,
    event: str,
    issue_id: str | None,
    release_tag: str | None,
    scope: str | None,
    dry_run: bool,
) -> int:
    dispatcher_path = project_root / "skill_cluster" / "system" / "dispatcher_routes.yaml"
    if not dispatcher_path.exists():
        dispatcher_path = Path(__file__).resolve().parents[1] / "skill_cluster" / "system" / "dispatcher_routes.yaml"

    _, hooks = parse_dispatcher_routes(dispatcher_path)
    hook_skills = hooks.get(event, [])
    if not hook_skills:
        print(f"[SKIP] no hooks configured for event: {event}")
        return 0

    print(f"[INFO] hook event: {event}")
    print(f"[INFO] configured hooks: {', '.join(hook_skills)}")

    status = 0
    for skill in hook_skills:
        if skill == "git-commit-push-skill":
            rc = execute_git_commit_push(
                project_root=project_root,
                event=event,
                issue_id=issue_id,
                release_tag=release_tag,
                scope=scope,
                dry_run=dry_run,
            )
            status = max(status, rc)
        else:
            print(f"[SKIP] no executable binding for hook skill: {skill}")
    return status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run workflow dispatch and post-stage hooks.")
    subparsers = parser.add_subparsers(dest="command")

    dispatch_parser = subparsers.add_parser("dispatch", help="Dispatch active skill by current stage.")
    dispatch_parser.add_argument(
        "--project-root",
        default=".",
        help="Target project root (default: current directory).",
    )

    hook_parser = subparsers.add_parser("hook", help="Execute post-stage hook event.")
    hook_parser.add_argument(
        "--project-root",
        default=".",
        help="Target project root (default: current directory).",
    )
    hook_parser.add_argument(
        "--event",
        required=True,
        help="Hook event name (e.g. task_completed, issue_resolved, release_checkpoint).",
    )
    hook_parser.add_argument(
        "--issue-id",
        default=None,
        help="Issue ID used for issue_resolved commit messages.",
    )
    hook_parser.add_argument(
        "--release-tag",
        default=None,
        help="Release tag/version used for release_checkpoint commit messages.",
    )
    hook_parser.add_argument(
        "--scope",
        default=None,
        help="Commit scope for task_completed messages.",
    )
    hook_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without writing git commits.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()
    project_root = Path(getattr(args, "project_root", ".")).expanduser().resolve()

    try:
        if args.command == "dispatch":
            return run_dispatch(project_root)
        if args.command == "hook":
            return run_hook(
                project_root=project_root,
                event=args.event,
                issue_id=args.issue_id,
                release_tag=args.release_tag,
                scope=args.scope,
                dry_run=args.dry_run,
            )
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}")
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
