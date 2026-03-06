---
name: task-planning-skill
description: Decompose architecture and module design into executable tasks with sequencing and acceptance criteria. Use before implementation to generate docs/tasks.md for task-engine consumption.
---

# Skill Name
task-planning-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.0.0`
- cluster_version: `1.0.0`

## Purpose
- Turn design artifacts into actionable implementation backlog.
- Establish sequencing that minimizes blockers and rework.

## When to Use
- `current_stage: task_planning`
- `docs/architecture.md` and module design are available.

## Inputs
- `docs/spec.md`
- `docs/architecture.md`
- `docs/module_design.md` (if exists)

## Outputs
- `docs/tasks.md`
- Initial `_LLM/task_state.yaml` bootstrap data (if absent)

## Operating Procedure
1. Extract implementation units from architecture/modules.
2. Split into tasks sized for one focused coding session.
3. Assign deterministic task IDs (`task_01`, `task_02`, ...).
4. For each task, define done criteria and dependencies.
5. Order tasks by risk-first and dependency-first principles.
6. Emit checklist format for machine parsing by task-engine.
7. Mark stage ready for `implementation`.

## Constraints
- Do not create tasks without measurable done criteria.
- Keep single task scope narrow enough for atomic review/testing.
- Avoid mixing refactor-only tasks into MVP path unless blocking.

## Examples
- Input: architecture with auth, channels, message fanout.
- Output: tasks for auth middleware, ACL checks, fanout routing, integration tests.
