---
name: code-review-skill
description: Review code changes for defects, regressions, maintainability risks, and requirement mismatches. Use after implementation and before release decisions, and feed findings into issue-engine when needed.
---

# Skill Name
code-review-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- Catch issues before testing or release.
- Ensure code aligns with requirements, architecture, and task scope.

## When to Use
- `current_stage: review`
- After any non-trivial implementation or refactor.

## Inputs
- Code diff
- `docs/spec.md`, `docs/architecture.md`, `docs/tasks.md`
- Existing issues in `docs_issue/`

## Outputs
- Prioritized review findings
- Issue candidates for `issue-engine`
- Pass/fail recommendation for next stage

## Operating Procedure
1. Compare implementation against requirement acceptance criteria.
2. Inspect correctness, edge cases, error handling, and security boundaries.
3. Check architectural conformance and module boundaries.
4. Verify tests adequately cover changed behavior.
5. Classify findings by severity: blocker/high/medium/low.
6. Open or update issue files via `issue-engine` using `<status>__<issue_id>__<summary>.md`.
7. New findings must start with `waiting_user` and wait for user confirmation before execution.
8. If no blocker/high defects, allow transition to `testing`.

## Constraints
- Findings must include evidence and impacted location.
- Do not approve when critical acceptance criteria are unmet.
- Do not bypass filename-driven state transitions for issue updates.
- Keep review focused on behavior and risk, not style-only comments.

## Examples
- Input: websocket auth patch without token expiry check.
- Output: high-severity finding and issue creation request.
