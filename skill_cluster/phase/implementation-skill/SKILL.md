---
name: implementation-skill
description: Implement code changes for the current planned task with minimal scope and verifiable outputs. Use in implementation or issue-fixing stages after task selection from task-engine.
---

# Skill Name
implementation-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.0.0`
- cluster_version: `1.0.0`

## Purpose
- Deliver task-scoped code changes with predictable quality.
- Maintain consistency between code, tests, and state files.

## When to Use
- `current_stage: implementation`
- `current_stage: issue_fixing` with assigned issue fix task

## Inputs
- `_LLM/task_state.yaml`
- `_LLM/project_state.yaml`
- `docs/tasks.md`
- `docs/spec.md`, `docs/architecture.md` (for constraints)

## Outputs
- `src/*` code changes
- `tests/*` updates when required
- Task/notes state updates

## Operating Procedure
1. Confirm current task from `task-engine`.
2. Read requirement and architecture constraints tied to task.
3. Implement smallest viable change to satisfy done criteria.
4. Add or update tests for behavior changes.
5. Run relevant local verification commands.
6. Record what changed and why in state notes.
7. Return to `code-review-skill` or `testing-skill` based on workflow.

## Constraints
- Do not implement features not listed in current task.
- Do not skip tests for behavior-affecting changes.
- Keep commits/diffs reviewable and task-linked.

## Examples
- Input: `task_03` websocket auth middleware.
- Output: middleware implementation + auth tests + state note update.
