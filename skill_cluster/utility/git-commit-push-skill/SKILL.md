---
name: git-commit-push-skill
description: Commit and optionally push project changes using conventional commits with safety checks for branch, staged diff, and remote availability. Use at workflow exit gates (task completion, issue resolution, release) to keep traceable history.
---

# Skill Name
git-commit-push-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- Keep engineering progress continuously traceable in git history.
- Standardize commit quality with conventional commits.
- Make push behavior optional for repos without remotes.

## When to Use
- After `task-engine` marks a task completed.
- After `issue-engine` transitions issue to `resolved`.
- During `release-management-skill` for release commits.
- Prefer execution through workflow hook entry:
- `python3 scripts/run_workflow.py hook --event <event> --project-root <project_root>`

## Inputs
- `git status --short` output
- `_LLM/project_state.yaml`, `_LLM/task_state.yaml`, `_LLM/git_state.yaml`
- Optional issue ID / task ID / release version notes

## Outputs
- Git commit with conventional commit message
- Optional `git push` result
- Updated `_LLM/git_state.yaml` (`last_commit`, `last_push_status`, `last_updated`)

## Operating Procedure
1. Validate repository context (`git rev-parse --is-inside-work-tree`).
2. Read `_LLM/git_state.yaml` and evaluate:
3. `enabled`, `auto_commit`, `push_mode` (`never|if_remote|always`).
4. Generate commit message by context:
5. Task completion -> `feat(<module>): complete <task_id>`.
6. Issue resolution -> `fix(issue): resolve <issue_id>`.
7. Release gate -> `chore(release): prepare <version_or_stage>`.
8. Stage tracked changes (`git add -A`) and commit if diff exists.
9. Push policy:
10. `never`: skip.
11. `if_remote`: push only if upstream/remote exists; otherwise skip with note.
12. `always`: attempt push; capture failure as warning.
13. Write git execution result back to `_LLM/git_state.yaml`.

## Constraints
- Do not create empty commits unless explicitly requested.
- Commit messages must follow conventional commit format.
- Push must not block local commit completion when no remote exists.
- Do not rewrite history in automation paths.

## Examples
- Input: task `task_07` completed, push mode `if_remote`.
- Output: commit `feat(auth): complete task_07`; push executed or skipped with reason.
