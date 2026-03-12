---
name: refactor-helper-skill
description: Support large or risky refactors with decomposition strategy, migration sequencing, and guardrail checks. Use before or during multi-step refactor work.
---

# Skill Name
refactor-helper-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 为复杂重构提供策略和迁移护栏。

## When to Use
- 多模块重构、跨阶段改造或高风险迁移前。
- 需要将大改拆分为可验证小步时。

## Inputs
- 目标重构范围、风险点、受影响模块列表。
- 现有测试能力与发布约束。

## Outputs
- 分阶段迁移计划（含回滚点与验证点）。
- 风险清单与优先级建议。

## Operating Procedure
1. 拆分重构范围与风险层级。
2. 设计渐进迁移步骤。
3. 定义每一步的完成标准与回滚条件。
4. 绑定回归检查点。
5. 将计划同步到 `docs/tasks.md` 与相关状态文件。

## Constraints
- 不得一次性改动过大导致无法回滚。
- 每个迁移步骤必须有独立验证证据。
- 风险项必须显式记录，不得隐式跳过。

## Examples
- Input: 计划将鉴权逻辑从业务层下沉到中间件层。
- Output: 生成分 3 步的迁移计划及每步回归检查项。
