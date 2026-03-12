---
name: idea-clarification-skill
description: Clarify a raw product idea into clear goals, boundaries, and assumptions. Use at project or iteration start before formal problem definition.
---

# Skill Name
idea-clarification-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 将模糊想法收敛为可定义问题。
- 为后续问题定义和需求工程提供统一输入边界。

## When to Use
- `current_stage: idea`
- 新项目启动或迭代开始时。

## Inputs
- 用户目标、业务背景、约束条件、成功标准草案。
- 历史迭代反馈（若为迭代场景）。

## Outputs
- `docs/idea.md`
- `_LLM/project_state.yaml` 中面向下一阶段的备注与阶段建议。

## Operating Procedure
1. 收集目标、用户、场景、约束。
2. 识别范围边界：明确 In Scope / Out of Scope。
3. 将关键假设写入 `docs/idea.md`，并标注待验证项。
4. 在 `_LLM/project_state.yaml.notes` 记录关键结论与风险。
5. 将阶段推进到 `problem_definition`。

## Constraints
- 不得在本阶段提前做架构或实现决策。
- 不能跳过边界定义直接进入需求拆解。
- 假设项必须可追踪，不能只停留在对话中。

## Examples
- Input: “我要做一个支持鉴权的低延迟实时聊天系统”。
- Output: `docs/idea.md` 明确目标用户、核心场景、范围边界与关键假设。
