---
name: problem-definition-skill
description: Define the target problem, user pain, and measurable success criteria from clarified ideas. Use before requirements analysis.
---

# Skill Name
problem-definition-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 形成明确问题定义与成功标准。
- 消除“症状描述”和“真实问题”之间的歧义。

## When to Use
- `current_stage: problem_definition`
- `docs/idea.md` 已具备初步目标和边界。

## Inputs
- `docs/idea.md`
- 业务限制、用户反馈、现有系统痛点（若存在）。

## Outputs
- `docs/problem.md`
- 可量化成功标准与失败判定条件。

## Operating Procedure
1. 读取 `docs/idea.md`。
2. 定义问题现状、目标状态与关键差距。
3. 识别受影响对象与优先级。
4. 写出可量化成功指标与验收边界。
5. 输出 `docs/problem.md`。
6. 更新阶段到 `requirements`。

## Constraints
- 不得把解决方案细节写进问题定义。
- 成功标准必须可测量，禁止“更好/更稳定”等模糊词。
- 问题定义应保持单一主问题，避免混入多个不相关议题。

## Examples
- Input: `docs/idea.md` 描述“聊天消息偶发延迟和鉴权异常”。
- Output: `docs/problem.md` 明确“延迟 P95 超标、鉴权失效窗口”与量化目标。
