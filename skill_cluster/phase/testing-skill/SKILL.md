---
name: testing-skill
description: Design and execute tests for implemented tasks and issue fixes, then record evidence-based outcomes. Use after review or fix completion to validate acceptance criteria and release readiness.
---

# Skill Name
testing-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- Validate implemented behavior against requirements.
- Provide objective quality gate evidence for workflow transitions.

## When to Use
- `current_stage: testing`
- Post-fix regression verification in `issue_fixing`

## Inputs
- `docs/spec.md`
- `docs/tasks.md`
- Current code and test suite
- Open issues related to tested scope

## Outputs
- Test results summary
- `tests/*` additions or fixes
- Issue updates for failed acceptance criteria

## Operating Procedure
1. Map current task requirements to test cases.
2. Execute unit/integration/regression tests relevant to changed scope.
3. Record pass/fail with concise evidence.
4. For failures, route to `issue-engine` with reproducible details and create/update `<status>__<issue_id>__<summary>.md`.
5. Add missing tests for uncovered acceptance criteria.
6. Confirm no blocker/high unresolved issues (`waiting_user/approved/in_progress/verifying`) before release transition.

## Constraints
- Do not claim pass without actual execution evidence.
- Keep test scope traceable to task IDs and acceptance criteria.
- Re-run impacted tests after every issue fix.

## Examples
- Input: auth middleware change.
- Output: passing auth success/failure/expired-token tests and updated issue status.
