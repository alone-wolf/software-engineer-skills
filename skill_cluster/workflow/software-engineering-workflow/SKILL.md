---
name: software-engineering-workflow
description: Orchestrate the full solo software engineering lifecycle for Codex sessions. Use when a project needs stage-gated execution from idea to iteration, strict state-file driven progression, and consistent handoff across sessions.
---

# Skill Name
software-engineering-workflow

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- Control lifecycle execution from `idea` to `iteration`.
- Enforce stage entry/exit conditions.
- Keep progress consistent across Codex sessions.

## When to Use
- Start of a new project or new iteration.
- Session handoff where stage continuity is critical.
- Any case requiring gated transition instead of ad-hoc coding.

## Inputs
- `_LLM/project_state.yaml`
- `_LLM/task_state.yaml`
- `_LLM/git_state.yaml`
- `docs/idea.md`, `docs/problem.md`, `docs/spec.md`, `docs/architecture.md`, `docs/tasks.md`
- `docs_issue/*.md`

## Outputs
- Updated `_LLM/project_state.yaml`
- Stage transition decision and next-skill recommendation
- Blocking reasons when gate checks fail

## Operating Procedure
1. Read `_LLM/project_state.yaml` and identify `current_stage`.
2. Validate mandatory artifacts for current stage.
3. If preconditions fail, stop transition and emit remediation actions.
4. Select next stage according to state machine rules.
5. Update `active_skill`, `last_updated`, `notes`, and optional `current_stage`.
6. Hand off to `skill-dispatcher` for concrete skill execution.
7. At stage exit gates (task completed / issue resolved / release checkpoint), trigger `git-commit-push-skill`.

## Constraints
- Do not infer stage from file existence alone.
- Do not bypass `requirements` or `task_planning` before implementation.
- Route review/testing defects to `issue-engine` before release and enforce filename-driven issue states.
- Respect `_LLM/git_state.yaml.push_mode`; do not force push when remote is unavailable.

## Examples
- Input: `current_stage: task_planning` and `docs/tasks.md` ready.
- Output: transition to `implementation` with `active_skill: task-engine`.
