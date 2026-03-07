#!/usr/bin/env python3
"""Validate skill version metadata consistency."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_VERSION_RE = re.compile(r"^- skill_version:\s*`([^`]+)`\s*$", re.MULTILINE)
CLUSTER_VERSION_RE = re.compile(r"^- cluster_version:\s*`([^`]+)`\s*$", re.MULTILINE)


def extract_version(pattern: re.Pattern[str], content: str, field: str, path: Path) -> str:
    match = pattern.search(content)
    if not match:
        raise ValueError(f"{path}: missing {field}")
    return match.group(1)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skill_files = sorted((root / "skill_cluster").rglob("SKILL.md"))
    if not skill_files:
        print("[ERROR] no SKILL.md files found under skill_cluster/")
        return 1

    cluster_versions: dict[str, list[Path]] = {}
    failures: list[str] = []

    for skill_md in skill_files:
        content = skill_md.read_text(encoding="utf-8")
        try:
            skill_version = extract_version(SKILL_VERSION_RE, content, "skill_version", skill_md)
            cluster_version = extract_version(
                CLUSTER_VERSION_RE, content, "cluster_version", skill_md
            )
        except ValueError as exc:
            failures.append(str(exc))
            continue

        cluster_versions.setdefault(cluster_version, []).append(skill_md)
        print(
            f"[OK] {skill_md.relative_to(root)} | skill_version={skill_version} "
            f"| cluster_version={cluster_version}"
        )

    if failures:
        print("\n[ERROR] invalid metadata:")
        for item in failures:
            print(f"- {item}")
        return 1

    if len(cluster_versions) != 1:
        print("\n[ERROR] cluster_version is inconsistent:")
        for version, paths in sorted(cluster_versions.items()):
            print(f"- {version}: {len(paths)} file(s)")
            for path in paths:
                print(f"  - {path.relative_to(root)}")
        return 1

    only_version = next(iter(cluster_versions))
    print(
        f"\n[PASS] cluster_version is consistent: {only_version} "
        f"({len(skill_files)} SKILL.md files)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
