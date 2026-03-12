---
name: skill-dispatcher
description: Dispatch the correct engineering skill based on project stage and task context. Use at the start of every Codex session or whenever current stage changes and the next executable skill must be selected deterministically.
---

# Skill Name
skill-dispatcher

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.2.0`
- cluster_version: `1.2.0`

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
- `_LLM/git_state.yaml`
- `docs/tasks.md` (when stage is `implementation`)

## Outputs
- `active_skill` update in `_LLM/project_state.yaml`
- Routed skill name and execution context
- Deterministic dispatch execution record (`notes`)

## Operating Procedure
1. Read `_LLM/project_state.yaml` and parse `current_stage`.
2. Validate stage-specific prerequisites.
3. Execute deterministic dispatch:
4. `python3 scripts/run_workflow.py dispatch --project-root <project_root>`
5. Apply routing table:
6. `idea -> idea-clarification-skill`
7. `problem_definition -> problem-definition-skill`
8. `requirements -> requirements-analysis-skill`
9. `architecture -> architecture-design-skill`
10. `module_design -> module-design-skill`
11. `task_planning -> task-planning-skill`
12. `implementation -> task-engine` then `implementation-skill`
13. `review -> code-review-skill`
14. `testing -> testing-skill`
15. `issue_fixing -> issue-engine` then `implementation-skill`
16. `refactoring -> refactoring-skill`
17. `release -> release-management-skill`
18. `iteration -> iteration-planning-skill`
19. For post-stage events, execute hooks explicitly:
20. `python3 scripts/run_workflow.py hook --event task_completed`
21. `python3 scripts/run_workflow.py hook --event issue_resolved --issue-id <issue_id>`
22. `python3 scripts/run_workflow.py hook --event release_checkpoint --release-tag <version>`

## Constraints
- Do not dispatch implementation when `docs/tasks.md` missing.
- Do not dispatch release when high-severity issues are unresolved (`waiting_user/approved/in_progress/verifying`).
- Keep routing deterministic and stateless except state-file updates.
- Do not treat “intent to trigger hook” as completed action; the command must be executed.

## Examples
- Input: `current_stage: review`
- Output: `active_skill: code-review-skill`
