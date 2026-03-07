#!/usr/bin/env python3
"""Unified entrypoint for skill-cluster initialization and global skill installation.

Commands:
  init      Initialize project engineering artifacts in current project directory.
  install   Install/list skills into Codex global skills directory.

"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileStats:
    created: list[str] = field(default_factory=list)
    overwritten: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


@dataclass
class InstallStats:
    created: list[str] = field(default_factory=list)
    overwritten: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    method_used: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


MARKER_FILENAME = ".se_skill_cluster_marker"
EXPECTED_CLUSTER_MARKER = "se-skill-cluster"
EXPECTED_CLUSTER_NAME = "software-engineering-skill-cluster"
EXPECTED_OWNER_PROJECT = "software_engineer_skills"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified tool for project initialization and Codex global skill installation."
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize project docs/state/templates in current project directory.",
    )
    init_parser.add_argument(
        "--project-name",
        default=None,
        help="Project name for _LLM/project_state.yaml (default: current directory name).",
    )
    init_doc_group = init_parser.add_mutually_exclusive_group()
    init_doc_group.add_argument(
        "--with-example-docs",
        action="store_true",
        help="Seed docs/idea.md, problem.md, spec.md, architecture.md with example content.",
    )
    init_doc_group.add_argument(
        "--minimal",
        action="store_true",
        help="Initialize only _LLM state files and docs/tasks.md (skip docs_issue and design docs).",
    )
    init_parser.add_argument(
        "--undo",
        action="store_true",
        help="Reverse init operation by removing managed files from current project directory.",
    )
    init_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive confirmation prompt for init --undo.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files managed by this script.",
    )
    init_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned operations without modifying files.",
    )

    install_parser = subparsers.add_parser(
        "install",
        help="Install or list skills for Codex global skills directory.",
    )
    install_parser.add_argument(
        "--source",
        default=None,
        help="Skill cluster root path (default: <script_dir>/skill_cluster).",
    )
    install_parser.add_argument(
        "--method",
        choices=("copy", "auto", "symlink", "junction"),
        default="copy",
        help="Install method (default: copy). auto: Windows symlink->junction->copy, Unix symlink->copy.",
    )
    install_parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Install only the given skill name. Can be repeated.",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing destination skill directories.",
    )
    install_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without writing files.",
    )
    install_parser.add_argument(
        "--list",
        action="store_true",
        help="List discovered skills and exit.",
    )
    install_parser.add_argument(
        "--undo",
        action="store_true",
        help="Reverse install operation by uninstalling skills from global directory.",
    )

    return parser


def log_file_action(kind: str, rel_path: Path, stats: FileStats) -> None:
    item = str(rel_path)
    if kind == "created":
        stats.created.append(item)
    elif kind == "overwritten":
        stats.overwritten.append(item)
    else:
        stats.skipped.append(item)


def ensure_dir(path: Path, target_root: Path, dry_run: bool, stats: FileStats) -> None:
    if path.exists():
        return
    rel = path.relative_to(target_root)
    if dry_run:
        log_file_action("created", rel, stats)
        return
    path.mkdir(parents=True, exist_ok=True)
    log_file_action("created", rel, stats)


def write_text_file(
    path: Path,
    content: str,
    target_root: Path,
    force: bool,
    dry_run: bool,
    stats: FileStats,
) -> None:
    rel = path.relative_to(target_root)
    if path.exists() and not force:
        log_file_action("skipped", rel, stats)
        return

    if dry_run:
        log_file_action("overwritten" if path.exists() else "created", rel, stats)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    action = "overwritten" if path.exists() else "created"
    path.write_text(content, encoding="utf-8")
    log_file_action(action, rel, stats)


def delete_path(
    path: Path,
    target_root: Path,
    dry_run: bool,
    stats: FileStats,
) -> None:
    rel = path.relative_to(target_root)
    exists = path.exists() or path.is_symlink()
    if not exists:
        log_file_action("skipped", rel, stats)
        return

    if dry_run:
        stats.deleted.append(str(rel))
        return

    remove_path(path)
    stats.deleted.append(str(rel))


def remove_empty_dir(
    path: Path,
    target_root: Path,
    dry_run: bool,
    stats: FileStats,
) -> None:
    rel = path.relative_to(target_root)
    if not path.exists() or not path.is_dir():
        return
    if any(path.iterdir()):
        return
    if dry_run:
        stats.deleted.append(str(rel))
        return
    path.rmdir()
    stats.deleted.append(str(rel))


def copy_file(
    src: Path,
    dst: Path,
    target_root: Path,
    force: bool,
    dry_run: bool,
    stats: FileStats,
) -> None:
    rel = dst.relative_to(target_root)
    if dst.exists() and not force:
        log_file_action("skipped", rel, stats)
        return

    if dry_run:
        log_file_action("overwritten" if dst.exists() else "created", rel, stats)
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    action = "overwritten" if dst.exists() else "created"
    shutil.copy2(src, dst)
    log_file_action(action, rel, stats)


def with_updated_state_template(content: str, project_name: str, today: str) -> str:
    lines = content.splitlines()
    updated: list[str] = []
    for line in lines:
        if line.startswith("project_name:"):
            updated.append(f"project_name: {project_name}")
        elif line.startswith("last_updated:"):
            updated.append(f"last_updated: {today}")
        else:
            updated.append(line)
    return "\n".join(updated) + "\n"


def with_updated_task_state_template(content: str, today: str) -> str:
    lines = content.splitlines()
    updated: list[str] = []
    for line in lines:
        if line.startswith("last_updated:"):
            updated.append(f"last_updated: {today}")
        else:
            updated.append(line)
    return "\n".join(updated) + "\n"


def placeholder_doc(title: str) -> str:
    return f"# {title}\n\n待补充。\n"


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def parse_simple_key_value(content: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip("'\"")
    return parsed


def parse_skill_meta(skill_md_path: Path) -> dict[str, str]:
    if not skill_md_path.exists():
        return {}

    parsed: dict[str, str] = {}
    for raw_line in skill_md_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("name:"):
            parsed["name"] = line.split(":", 1)[1].strip().strip("'\"")
        elif line.startswith("- cluster_marker:"):
            parsed["cluster_marker"] = line.split(":", 1)[1].strip().strip("'\"`")
        elif line.startswith("- cluster_name:"):
            parsed["cluster_name"] = line.split(":", 1)[1].strip().strip("'\"`")
    return parsed


def validate_uninstall_target(destination_dir: Path, expected_skill_name: str) -> tuple[bool, str]:
    marker_path = destination_dir / MARKER_FILENAME
    if not marker_path.exists():
        return False, f"missing marker file '{MARKER_FILENAME}'"

    marker_meta = parse_simple_key_value(marker_path.read_text(encoding="utf-8"))
    if marker_meta.get("owner_project") != EXPECTED_OWNER_PROJECT:
        return False, "marker owner_project mismatch"
    if marker_meta.get("cluster_marker") != EXPECTED_CLUSTER_MARKER:
        return False, "marker cluster_marker mismatch"
    if marker_meta.get("cluster_name") != EXPECTED_CLUSTER_NAME:
        return False, "marker cluster_name mismatch"
    if marker_meta.get("skill_name") != expected_skill_name:
        return False, "marker skill_name mismatch"

    skill_md = destination_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "missing SKILL.md"

    skill_meta = parse_skill_meta(skill_md)
    if skill_meta.get("name") != expected_skill_name:
        return False, "SKILL.md name mismatch"
    if skill_meta.get("cluster_marker") != EXPECTED_CLUSTER_MARKER:
        return False, "SKILL.md cluster_marker mismatch"
    if skill_meta.get("cluster_name") != EXPECTED_CLUSTER_NAME:
        return False, "SKILL.md cluster_name mismatch"

    return True, "ok"


def validate_source_skill_for_install(source_dir: Path, expected_skill_name: str) -> tuple[bool, str]:
    marker_path = source_dir / MARKER_FILENAME
    if not marker_path.exists():
        return False, f"missing source marker '{MARKER_FILENAME}'"

    marker_meta = parse_simple_key_value(marker_path.read_text(encoding="utf-8"))
    if marker_meta.get("owner_project") != EXPECTED_OWNER_PROJECT:
        return False, "source marker owner_project mismatch"
    if marker_meta.get("cluster_marker") != EXPECTED_CLUSTER_MARKER:
        return False, "source marker cluster_marker mismatch"
    if marker_meta.get("cluster_name") != EXPECTED_CLUSTER_NAME:
        return False, "source marker cluster_name mismatch"
    if marker_meta.get("skill_name") != expected_skill_name:
        return False, "source marker skill_name mismatch"

    skill_md = source_dir / "SKILL.md"
    skill_meta = parse_skill_meta(skill_md)
    if skill_meta.get("name") != expected_skill_name:
        return False, "source SKILL.md name mismatch"
    return True, "ok"


def is_windows() -> bool:
    return os.name == "nt"


def resolve_method_order(method: str) -> list[str]:
    if method != "auto":
        return [method]
    if is_windows():
        return ["symlink", "junction", "copy"]
    return ["symlink", "copy"]


def create_junction(source_dir: Path, destination_dir: Path) -> None:
    if not is_windows():
        raise OSError("junction is only supported on Windows")
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(destination_dir), str(source_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = (result.stderr or result.stdout or "").strip()
        raise OSError(stderr or "mklink /J failed")


def install_dir_with_method(source_dir: Path, destination_dir: Path, method: str) -> None:
    if method == "symlink":
        destination_dir.symlink_to(source_dir.resolve(), target_is_directory=True)
        return
    if method == "junction":
        create_junction(source_dir.resolve(), destination_dir)
        return
    if method == "copy":
        shutil.copytree(source_dir, destination_dir)
        return
    raise ValueError(f"Unsupported method: {method}")


def discover_skills(skill_cluster_root: Path) -> dict[str, Path]:
    skill_md_files = list(skill_cluster_root.rglob("SKILL.md"))
    if not skill_md_files:
        raise ValueError(f"No SKILL.md found under: {skill_cluster_root}")

    mapping: dict[str, Path] = {}
    duplicates: dict[str, list[Path]] = {}

    for skill_md in skill_md_files:
        skill_dir = skill_md.parent
        skill_name = skill_dir.name
        if skill_name in mapping:
            duplicates.setdefault(skill_name, [mapping[skill_name]]).append(skill_dir)
        else:
            mapping[skill_name] = skill_dir

    if duplicates:
        lines = []
        for name, paths in sorted(duplicates.items()):
            joined = ", ".join(str(path) for path in paths)
            lines.append(f"{name}: {joined}")
        raise ValueError("Duplicate skill directory names found: " + " | ".join(lines))

    return dict(sorted(mapping.items(), key=lambda item: item[0]))


def select_skills(discovered: dict[str, Path], only: list[str]) -> dict[str, Path]:
    if not only:
        return discovered

    wanted = set(only)
    missing = sorted(name for name in wanted if name not in discovered)
    if missing:
        raise ValueError(
            "Unknown skill name(s): " + ", ".join(missing) + ". Use install --list to inspect names."
        )

    return {name: path for name, path in discovered.items() if name in wanted}


def ensure_install_root(path: Path, dry_run: bool, stats: InstallStats) -> None:
    if path.exists():
        return
    if dry_run:
        stats.created.append(str(path))
        return
    path.mkdir(parents=True, exist_ok=True)
    stats.created.append(str(path))


def install_one_skill(
    skill_name: str,
    source_dir: Path,
    destination_root: Path,
    method: str,
    force: bool,
    dry_run: bool,
    stats: InstallStats,
) -> None:
    destination_dir = destination_root / skill_name
    exists = destination_dir.exists() or destination_dir.is_symlink()

    if exists:
        try:
            if destination_dir.resolve() == source_dir.resolve() and not force:
                stats.skipped.append(str(destination_dir))
                return
        except FileNotFoundError:
            pass

    if exists and not force:
        stats.skipped.append(str(destination_dir))
        return

    if dry_run:
        if exists:
            stats.overwritten.append(str(destination_dir))
        else:
            stats.created.append(str(destination_dir))
        stats.method_used[skill_name] = resolve_method_order(method)[0]
        return

    if exists:
        remove_path(destination_dir)

    method_chain = resolve_method_order(method)
    chosen_method: str | None = None
    last_error: Exception | None = None

    for candidate in method_chain:
        try:
            install_dir_with_method(source_dir, destination_dir, candidate)
            chosen_method = candidate
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            stats.warnings.append(
                f"{skill_name}: method '{candidate}' failed ({exc}); "
                f"{'trying fallback' if candidate != method_chain[-1] else 'no fallback left'}."
            )
            if destination_dir.exists() or destination_dir.is_symlink():
                remove_path(destination_dir)

    if chosen_method is None:
        raise RuntimeError(
            f"Failed to install '{skill_name}' using methods {method_chain}. "
            f"Last error: {last_error}"
        )

    stats.method_used[skill_name] = chosen_method
    if exists:
        stats.overwritten.append(str(destination_dir))
    else:
        stats.created.append(str(destination_dir))


def run_install(
    source_root: Path,
    destination_root: Path,
    method: str,
    only: list[str],
    force: bool,
    dry_run: bool,
) -> tuple[InstallStats, dict[str, Path]]:
    discovered = discover_skills(source_root)
    selected = select_skills(discovered, only)

    stats = InstallStats()
    ensure_install_root(destination_root, dry_run, stats)

    for skill_name, source_dir in selected.items():
        valid_source, reason = validate_source_skill_for_install(source_dir, skill_name)
        if not valid_source:
            raise ValueError(f"{skill_name}: {reason}")
        install_one_skill(
            skill_name=skill_name,
            source_dir=source_dir,
            destination_root=destination_root,
            method=method,
            force=force,
            dry_run=dry_run,
            stats=stats,
        )

    return stats, selected


def print_file_stats(stats: FileStats) -> None:
    if stats.created:
        print("\n[created]")
        for item in stats.created:
            print(f"- {item}")
    if stats.overwritten:
        print("\n[overwritten]")
        for item in stats.overwritten:
            print(f"- {item}")
    if stats.deleted:
        print("\n[deleted]")
        for item in stats.deleted:
            print(f"- {item}")
    if stats.skipped:
        print("\n[skipped]")
        for item in stats.skipped:
            print(f"- {item}")


def print_install_stats(
    stats: InstallStats,
    source_root: Path,
    destination_root: Path,
    method: str,
    selected_count: int,
    dry_run: bool,
) -> None:
    mode = "DRY RUN" if dry_run else "DONE"
    print(f"[{mode}] Installed skills to: {destination_root}")
    print(f"source: {source_root}")
    print(f"method: {method} ({' -> '.join(resolve_method_order(method))})")
    print(f"selected: {selected_count}")

    if stats.created:
        print("\n[created]")
        for item in stats.created:
            print(f"- {item}")
    if stats.overwritten:
        print("\n[overwritten]")
        for item in stats.overwritten:
            print(f"- {item}")
    if stats.deleted:
        print("\n[deleted]")
        for item in stats.deleted:
            print(f"- {item}")
    if stats.skipped:
        print("\n[skipped]")
        for item in stats.skipped:
            print(f"- {item}")
    if stats.method_used:
        print("\n[method_used]")
        for name in sorted(stats.method_used):
            print(f"- {name}: {stats.method_used[name]}")
    if stats.warnings:
        print("\n[warnings]")
        for item in stats.warnings:
            print(f"- {item}")


def print_uninstall_stats(
    stats: InstallStats,
    destination_root: Path,
    selected_count: int,
    dry_run: bool,
) -> None:
    mode = "DRY RUN" if dry_run else "DONE"
    print(f"[{mode}] Uninstalled skills from: {destination_root}")
    print(f"selected: {selected_count}")

    if stats.deleted:
        print("\n[deleted]")
        for item in stats.deleted:
            print(f"- {item}")
    if stats.skipped:
        print("\n[skipped]")
        for item in stats.skipped:
            print(f"- {item}")
    if stats.warnings:
        print("\n[warnings]")
        for item in stats.warnings:
            print(f"- {item}")


def handle_init(args: argparse.Namespace, script_root: Path) -> int:
    source_cluster = script_root / "skill_cluster"
    source_templates = source_cluster / "templates"
    source_examples = source_cluster / "examples" / "project_root"

    target_root = Path.cwd().resolve()
    stats = FileStats()

    if args.undo:
        if args.with_example_docs:
            print("[ERROR] --undo 与 --with-example-docs 不能同时使用。")
            return 1
        if not args.dry_run and not args.yes:
            if not sys.stdin.isatty():
                print("[ERROR] init --undo 在非交互模式下需要 --yes 以确认删除。")
                return 1
            print("[CONFIRM] init --undo 将删除当前目录下受管文件与空目录。")
            confirmed = input("输入 YES 确认继续: ").strip()
            if confirmed != "YES":
                print("[CANCELLED] 已取消 init --undo。")
                return 1

        managed_files = [
            target_root / "_LLM" / "project_state.yaml",
            target_root / "_LLM" / "task_state.yaml",
            target_root / "docs" / "tasks.md",
        ]
        if not args.minimal:
            managed_files.extend(
                [
                    target_root / "docs" / "idea.md",
                    target_root / "docs" / "problem.md",
                    target_root / "docs" / "spec.md",
                    target_root / "docs" / "architecture.md",
                    target_root / "docs" / "issue-file-template.md",
                    target_root / "docs_issue" / ".gitkeep",
                ]
            )

        for path in managed_files:
            delete_path(path, target_root, args.dry_run, stats)

        remove_empty_dir(target_root / "docs_issue", target_root, args.dry_run, stats)
        remove_empty_dir(target_root / "_LLM", target_root, args.dry_run, stats)
        remove_empty_dir(target_root / "docs", target_root, args.dry_run, stats)

        mode = "DRY RUN" if args.dry_run else "DONE"
        print(f"[{mode}] Init reverse completed: {target_root}")
        print_file_stats(stats)
        return 0

    if not source_cluster.exists():
        print("[ERROR] 未找到 skill_cluster 目录，请确认脚本所在位置。")
        return 1

    project_name = args.project_name or target_root.name
    today = dt.date.today().isoformat()

    if not args.dry_run:
        target_root.mkdir(parents=True, exist_ok=True)

    docs_dir = target_root / "docs"
    issues_dir = target_root / "docs_issue"
    llm_dir = target_root / "_LLM"

    ensure_dir(docs_dir, target_root, args.dry_run, stats)
    ensure_dir(llm_dir, target_root, args.dry_run, stats)
    if not args.minimal:
        ensure_dir(issues_dir, target_root, args.dry_run, stats)

    project_state_src = source_templates / "project_state.template.yaml"
    task_state_src = source_templates / "task_state.template.yaml"

    project_state_content = with_updated_state_template(
        project_state_src.read_text(encoding="utf-8"), project_name, today
    )
    task_state_content = with_updated_task_state_template(
        task_state_src.read_text(encoding="utf-8"), today
    )

    write_text_file(
        llm_dir / "project_state.yaml",
        project_state_content,
        target_root,
        args.force,
        args.dry_run,
        stats,
    )
    write_text_file(
        llm_dir / "task_state.yaml",
        task_state_content,
        target_root,
        args.force,
        args.dry_run,
        stats,
    )

    copy_file(
        source_templates / "tasks-template.md",
        docs_dir / "tasks.md",
        target_root,
        args.force,
        args.dry_run,
        stats,
    )

    if not args.minimal:
        copy_file(
            source_templates / "issue-template.md",
            docs_dir / "issue-file-template.md",
            target_root,
            args.force,
            args.dry_run,
            stats,
        )

        seed_docs = {
            "idea.md": "Idea",
            "problem.md": "Problem Definition",
            "spec.md": "Specification",
            "architecture.md": "Architecture",
        }
        for filename, title in seed_docs.items():
            dst = docs_dir / filename
            if args.with_example_docs:
                src = source_examples / "docs" / filename
                copy_file(src, dst, target_root, args.force, args.dry_run, stats)
            else:
                write_text_file(
                    dst,
                    placeholder_doc(title),
                    target_root,
                    args.force,
                    args.dry_run,
                    stats,
                )

    if not args.minimal:
        write_text_file(
            issues_dir / ".gitkeep",
            "",
            target_root,
            force=False,
            dry_run=args.dry_run,
            stats=stats,
        )

    mode = "DRY RUN" if args.dry_run else "DONE"
    print(f"[{mode}] Skills 集群初始化完成: {target_root}")
    print(f"project_name: {project_name}")
    print_file_stats(stats)

    print("\nNext steps:")
    if args.minimal:
        print("1. 先完善 docs/tasks.md 的任务拆分与验收标准。")
        print("2. 每次 Codex 会话前先读取 _LLM/project_state.yaml。")
        print("3. 需要完整流程时，可补充 docs_issue/ 与 docs/spec/architecture 文档。")
    else:
        print("1. 根据业务完善 docs/idea.md、docs/problem.md、docs/spec.md。")
        print("2. 在 docs/tasks.md 拆分任务后，再进入 implementation 阶段。")
        print("3. 问题文件命名必须使用 <status>__<issue_id>__<summary>.md。")
        print("4. 状态集合与字段格式以 docs/issue-file-template.md 为准。")
        print("5. docs_issue 仅存放问题文件；状态变更必须通过重命名。")
        print("6. 每次 Codex 会话前先读取 _LLM/project_state.yaml。")

    return 0


def handle_install(args: argparse.Namespace, script_root: Path) -> int:
    source_root = (
        Path(args.source).expanduser().resolve()
        if args.source
        else (script_root / "skill_cluster").resolve()
    )
    if not source_root.exists():
        print(f"[ERROR] skill_cluster root not found: {source_root}")
        return 1

    try:
        discovered = discover_skills(source_root)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}")
        return 1

    if args.list:
        if args.undo:
            print("[ERROR] --list 与 --undo 不能同时使用。")
            return 1
        print("Discovered skills:")
        for idx, name in enumerate(discovered.keys(), start=1):
            print(f"{idx}. {name}")
        return 0

    try:
        selected = select_skills(discovered, args.only)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}")
        return 1

    codex_home = (Path.home() / ".codex").resolve()
    destination_root = codex_home / "skills"

    if args.undo:
        uninstall_stats = InstallStats()
        for skill_name in selected:
            destination_dir = destination_root / skill_name
            exists = destination_dir.exists() or destination_dir.is_symlink()
            if not exists:
                uninstall_stats.skipped.append(str(destination_dir))
                continue

            allowed, reason = validate_uninstall_target(destination_dir, skill_name)
            if not allowed:
                uninstall_stats.skipped.append(str(destination_dir))
                uninstall_stats.warnings.append(
                    f"{skill_name}: skip uninstall because {reason}."
                )
                continue

            if args.dry_run:
                uninstall_stats.deleted.append(str(destination_dir))
                continue

            try:
                remove_path(destination_dir)
                uninstall_stats.deleted.append(str(destination_dir))
            except Exception as exc:  # noqa: BLE001
                uninstall_stats.warnings.append(
                    f"{skill_name}: failed to remove {destination_dir} ({exc})"
                )

        print_uninstall_stats(
            stats=uninstall_stats,
            destination_root=destination_root,
            selected_count=len(selected),
            dry_run=args.dry_run,
        )

        if not args.dry_run:
            print("\nRestart Codex to apply skill removal.")
        return 0

    try:
        install_stats, _ = run_install(
            source_root=source_root,
            destination_root=destination_root,
            method=args.method,
            only=args.only,
            force=args.force,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}")
        return 1

    print_install_stats(
        stats=install_stats,
        source_root=source_root,
        destination_root=destination_root,
        method=args.method,
        selected_count=len(selected),
        dry_run=args.dry_run,
    )

    if not args.dry_run:
        print("\nRestart Codex to pick up new skills.")

    return 0


def main() -> int:
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args(sys.argv[1:])
    script_root = Path(__file__).resolve().parent

    if args.command == "init":
        return handle_init(args, script_root)
    if args.command == "install":
        return handle_install(args, script_root)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
