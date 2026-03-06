---
name: issue-engine
description: Manage defect and risk lifecycle through markdown issue files in docs_issue with filename-driven states, one-problem-one-file tracking, duplicate detection, and acceptance-criteria verification. Use when review/testing/security/performance checks identify actionable issues.
---

# Skill Name
issue-engine

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.1.0`

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

## Operating Procedure
1. Ensure `docs_issue/` exists and only use first-level files for scanning and duplicate checks.
2. Before creating a new file, perform duplicate detection using summary, root cause, impact object, and core evidence path.
3. If the same issue already exists (any status), update the existing file and transition status by renaming file; do not create duplicates.
4. Create new issue file only when confirmed as independent issue.
5. Create new files with status `waiting_user` and filename format:
6. `<status>__<issue_id>__<summary>.md`
7. Use legal statuses only:
8. `waiting_user`, `approved`, `in_progress`, `verifying`, `resolved`, `deferred`, `rejected`, `archived`.
9. Treat filename status as the source of truth; keep body `当前状态` synchronized.
10. After fixes, validate each acceptance criterion with explicit evidence before moving to `resolved`.
11. Reopen by renaming back to `waiting_user` if resolved/rejected/archived issue is raised again.

## Constraints
- Do not merge unrelated problems into one issue file.
- Do not close (`resolved`) without acceptance-criteria verification evidence.
- Do not create `ISSUE-xxxx.md` style files.
- Keep `issue_id` stable across status transitions.

## Examples
- Input: expired-token auth bypass found during testing.
- Output: `docs_issue/waiting_user__Q20260306-01__过期令牌放行风险.md` created with evidence and acceptance criteria.
