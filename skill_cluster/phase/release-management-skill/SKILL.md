---
name: release-management-skill
description: Perform release gating, final verification, and version artifact preparation. Use when iteration scope is complete and quality gates are satisfied.
---

# Skill Name
release-management-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 管理发布门禁与版本产物。

## When to Use
- `current_stage: release`
- 测试通过且阻塞级问题已处理后。

## Inputs
- `docs/spec.md`、`docs/tasks.md`
- `docs_issue/*.md` 状态与严重度
- `_LLM/project_state.yaml`、`_LLM/git_state.yaml`
- 发布版本标识（如 `v1.2.0`）

## Outputs
- 发布检查结论与发布说明（changelog/release note）
- 发布检查点 commit（按策略可选 push）
- 阶段推进到 `iteration`

## Operating Procedure
1. 执行发布门禁校验：
2. `python3 scripts/validate_workflow_state.py --next-stage iteration`
3. 检查测试结果与 `docs_issue/` 中未关闭高风险问题。
4. 生成发布说明与版本记录。
5. 触发阶段出口 hook：
6. `python3 scripts/run_workflow.py hook --event release_checkpoint --release-tag <version>`
7. 更新阶段到 `iteration`，并记录发布结论。

## Constraints
- 未通过门禁校验不得进入发布。
- 发现 `High/Critical` 未解决问题时禁止推进。
- 发布记录必须可追踪到任务、问题与提交。

## Examples
- Input: 版本 `v1.2.0`，测试通过且无阻塞问题。
- Output: 生成发布说明并创建 `chore(release): checkpoint v1.2.0` 提交。
