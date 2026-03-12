---
name: issue-engine
description: Manage defect and risk lifecycle through markdown issue files in docs_issue with filename-driven states, one-problem-one-file tracking, duplicate detection, and acceptance-criteria verification. Use when review/testing/security/performance checks identify actionable issues.
---

# Skill Name
issue-engine

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.2.0`
- cluster_version: `1.2.0`

## Purpose
- Standardize issue lifecycle with auditable, filename-driven state transitions.
- Ensure one-problem-one-file closure from discovery to verification.

## When to Use
- Any review/testing/security/performance finding appears.
- Existing issue needs reopen, defer, reject, archive, or verification updates.

## Inputs
- Findings from review/test/audit
- `docs_issue/*.md` (first-level only)
- Related code/tests evidence

## Outputs
- New or updated `docs_issue/<status>__<issue_id>__<summary>.md`
- State transition records and verification evidence
- Release gate input for unresolved high-risk items
- Trigger signal for `git-commit-push-skill` when issue reaches `resolved`

## Operating Procedure
1. Ensure `docs_issue/` exists and only use first-level files for scanning and duplicate checks.
2. Determine whether a finding is an existing issue:
3. Compare `root_cause`, `impact_object`, `core_evidence_path`; if at least two match, treat as same issue.
4. If the same issue already exists (any status), update existing file and transition status by renaming; do not create duplicates.
5. Create a new issue only when confirmed as independent.
6. New filename format must be:
7. `<status>__<issue_id>__<summary>.md`
8. New files must start at `waiting_user`.
9. `issue_id` generation rule:
10. Scan first-level files in `docs_issue/` for today `QYYYYMMDD-XX`.
11. Use `(max_sequence + 1)` for the same day; minimum width 2 digits.
12. If filename conflict occurs, rescan and reallocate; do not guess or skip silently.
13. Use legal statuses only:
14. `waiting_user`, `approved`, `in_progress`, `verifying`, `resolved`, `deferred`, `rejected`, `archived`.
15. Treat filename status as the source of truth; keep body `当前状态` synchronized.
16. After fixes, validate each acceptance criterion with explicit evidence before moving to `resolved`.
17. Reopen by renaming back to `waiting_user` if resolved/rejected/archived issue is raised again.
18. On transition to `resolved`, execute:
19. `python3 scripts/run_workflow.py hook --event issue_resolved --issue-id <issue_id> --project-root <project_root>`

## Constraints
- Do not merge unrelated problems into one issue file.
- Do not close (`resolved`) without acceptance-criteria verification evidence.
- Do not create `ISSUE-xxxx.md` style files.
- Keep `issue_id` stable across status transitions.
- Filename parse failure or severe naming corruption must stop execution for manual confirmation.

## Examples
- Input: expired-token auth bypass found during testing.
- Output: `docs_issue/waiting_user__Q20260306-01__过期令牌放行风险.md` created with evidence and acceptance criteria.
