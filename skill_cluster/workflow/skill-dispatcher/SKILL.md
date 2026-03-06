---
name: skill-dispatcher
description: Dispatch the correct engineering skill based on project stage and task context. Use at the start of every Codex session or whenever current stage changes and the next executable skill must be selected deterministically.
---

# Skill Name
skill-dispatcher

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.1.0`

## Purpose
- Map stage state to executable skill.
- Enforce deterministic routing for reproducible AI behavior.

## When to Use
- Every session start after reading state files.
- Immediately after a stage transition.
- Before any implementation activity.

## Inputs
- `_LLM/project_state.yaml`
- `_LLM/task_state.yaml`
- `docs/tasks.md` (when stage is `implementation`)

## Outputs
- `active_skill` update in `_LLM/project_state.yaml`
- Routed skill name and execution context

## Operating Procedure
1. Read `_LLM/project_state.yaml` and parse `current_stage`.
2. Validate stage-specific prerequisites.
3. Apply routing table:
4. `idea -> idea-clarification-skill`
5. `problem_definition -> problem-definition-skill`
6. `requirements -> requirements-analysis-skill`
7. `architecture -> architecture-design-skill`
8. `module_design -> module-design-skill`
9. `task_planning -> task-planning-skill`
10. `implementation -> task-engine` then `implementation-skill`
11. `review -> code-review-skill`
12. `testing -> testing-skill`
13. `issue_fixing -> issue-engine` then `implementation-skill`
14. `refactoring -> refactoring-skill`
15. `release -> release-management-skill`
16. `iteration -> iteration-planning-skill`
17. Write selected skill to `active_skill` with updated timestamp.

## Constraints
- Do not dispatch implementation when `docs/tasks.md` missing.
- Do not dispatch release when high-severity issues are unresolved (`waiting_user/approved/in_progress/verifying`).
- Keep routing deterministic and stateless except state-file updates.

## Examples
- Input: `current_stage: review`
- Output: `active_skill: code-review-skill`
