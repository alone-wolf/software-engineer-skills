---
name: refactoring-skill
description: Improve code structure, readability, and maintainability without changing external behavior. Use after functional stability when technical debt blocks velocity.
---

# Skill Name
refactoring-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 在不改行为前提下降低技术债务。

## When to Use
- `current_stage: refactoring`
- 或 `issue_fixing` 阶段中存在结构性问题需要重构时。

## Inputs
- 当前代码与测试基线。
- Review/Testing/Issue 产出的技术债证据。
- `docs/architecture.md`、`docs/tasks.md` 中的约束。

## Outputs
- 结构改进后的代码与回归测试结果。
- 受影响文档与状态文件更新记录。

## Operating Procedure
1. 识别代码异味与风险。
2. 拆分为可独立验证的小步重构任务。
3. 每步执行后运行受影响测试，确保行为不变。
4. 若出现回归，立即回滚到上一步并记录原因。
5. 更新任务/状态与文档。

## Constraints
- 不得在同一提交中混入新功能需求。
- 必须有回归验证证据，禁止“未测试即宣称不改行为”。
- 变更应保持可 review 的原子粒度。

## Examples
- Input: 业务逻辑与 IO 严重耦合导致测试困难。
- Output: 抽离纯函数与接口层，测试覆盖提升且行为保持一致。
