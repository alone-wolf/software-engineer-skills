---
name: requirements-analysis-skill
description: Transform problem definition into implementable software requirements with acceptance criteria. Use after problem definition and before architecture design to produce a clear spec for task planning and testing.
---

# Skill Name
requirements-analysis-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.0.0`
- cluster_version: `1.1.0`

## Purpose
- Convert problem statement into structured FR/NFR requirements.
- Define acceptance criteria that can drive tests and release gates.

## When to Use
- `current_stage: requirements`
- Existing `docs/problem.md` is available and needs formalization.

## Inputs
- `docs/problem.md`
- `docs/idea.md` (optional context)
- Constraints from product/domain decisions

## Outputs
- `docs/spec.md`
- Requirement traceability notes (requirement -> acceptance criteria)

## Operating Procedure
1. Read `docs/problem.md` and extract actors, scenarios, constraints.
2. Define Functional Requirements (FR) with unambiguous behavior.
3. Define Non-Functional Requirements (NFR): security, performance, reliability, observability.
4. Add out-of-scope and assumptions.
5. Write acceptance criteria per requirement in testable terms.
6. Confirm requirements are implementation-independent and measurable.
7. Update `_LLM/project_state.yaml` to next stage candidate `architecture`.

## Constraints
- Do not embed architecture decisions in requirements.
- Avoid vague language like “fast”, “stable” without metrics.
- Keep MVP boundary explicit to avoid scope creep.

## Examples
- Input: “Need websocket chat with secure auth and low latency.”
- Output: `spec.md` with FR auth flow, FR channel ACL, NFR latency P95 target, and testable AC.
