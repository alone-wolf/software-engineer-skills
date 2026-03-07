---
name: task-engine
description: Parse and manage engineering tasks from docs/tasks.md with synchronized task state updates in _LLM/task_state.yaml. Use before implementation/testing to select, advance, and complete task-driven work.
---

# Skill Name
task-engine

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.0.0`
- cluster_version: `1.2.0`

## Purpose
- Keep implementation strictly task-driven.
- Synchronize task selection and completion status.

## When to Use
- Before coding in `implementation` stage.
- After task completion to move to next task.
- During session start to recover in-progress task context.

## Inputs
- `docs/tasks.md`
- `_LLM/task_state.yaml`
- `_LLM/project_state.yaml`

## Outputs
- Updated `_LLM/task_state.yaml`
- Updated `_LLM/project_state.yaml.current_task`
- Trigger signal for `git-commit-push-skill` on task completion
- Optional task progression notes in `notes`

## Operating Procedure
1. Parse `docs/tasks.md` checkboxes and task IDs.
2. Read `_LLM/task_state.yaml` for current progress.
3. Select current executable task:
4. Prefer existing `in_progress` task.
5. Else choose first unchecked task.
6. Mark state as `in_progress` and set `current_task`.
7. After implementation/test confirmation, move task to `completed_tasks` and choose next.
8. Sync `current_task` back to `_LLM/project_state.yaml`.
9. When a task transitions to completed, call `git-commit-push-skill`.

## Constraints
- Do not execute tasks absent from `docs/tasks.md`.
- Do not mark task complete without evidence (code/tests/docs updates).
- Keep task IDs stable; avoid free-text renaming mid-iteration.

## Examples
- Input: unchecked `task_03` is first pending task.
- Output: `_LLM/task_state.yaml.current_task = task_03`.
