---
name: architecture-design-skill
description: Produce system architecture from approved requirements including components, data flow, interfaces, and risk controls. Use after spec finalization and before module decomposition.
---

# Skill Name
architecture-design-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.0.0`
- cluster_version: `1.1.0`

## Purpose
- Define a buildable architecture aligned with requirements.
- Make key tradeoffs explicit for future implementation and refactoring.

## When to Use
- `current_stage: architecture`
- `docs/spec.md` is stable enough for technical design.

## Inputs
- `docs/spec.md`
- Existing technical constraints (stack, hosting, compliance)

## Outputs
- `docs/architecture.md`
- Risk list and mitigation strategy section

## Operating Procedure
1. Translate FR/NFR into architectural drivers.
2. Define major components and ownership boundaries.
3. Describe core runtime/data flows and failure paths.
4. Specify integration interfaces and contracts.
5. Document tradeoffs and rejected alternatives.
6. Add operational concerns: scaling, observability, security controls.
7. Validate every major decision traces back to requirements.

## Constraints
- Do not design components with undefined responsibilities.
- Avoid premature microservice split for solo projects unless required.
- Keep architecture implementable by one developer.

## Examples
- Input: `spec.md` requires JWT websocket auth and low latency.
- Output: `architecture.md` defining gateway/auth/realtime hub and latency bottleneck controls.
