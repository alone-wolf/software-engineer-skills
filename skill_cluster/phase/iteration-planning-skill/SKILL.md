---
name: iteration-planning-skill
description: Plan the next iteration from release feedback, remaining issues, and new opportunities. Use immediately after release closure.
---

# Skill Name
iteration-planning-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 发布后复盘并规划下一迭代。

## When to Use
- `current_stage: iteration`
- 发布收尾完成，需要开启下一轮生命周期时。

## Inputs
- 发布反馈、未关闭问题、性能/安全评估结果。
- `docs/tasks.md` 与上一轮迭代复盘结论。

## Outputs
- 下一迭代的目标和范围（`docs/idea.md` / `docs/tasks.md`）
- `_LLM/project_state.yaml.current_stage` 更新为 `idea`

## Operating Procedure
1. 汇总反馈与遗留问题。
2. 划分下一迭代目标、范围和优先级。
3. 回写到 `docs/idea.md` 或 `docs/tasks.md`。
4. 校验可回到 `idea` 阶段：
5. `python3 scripts/validate_workflow_state.py --next-stage idea`
6. 更新 `_LLM/project_state.yaml.current_stage = idea`，形成下一轮入口。

## Constraints
- 不得把上一轮未确认问题直接标记为已解决。
- 新迭代目标需明确可验证结果，避免泛化目标。
- 阶段切换必须回写状态文件，不能只在文档描述。

## Examples
- Input: 发布后发现两项中优先级技术债与一项新需求。
- Output: 生成下一轮 `idea` 草案并完成阶段回切。
