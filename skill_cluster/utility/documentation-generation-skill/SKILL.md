---
name: documentation-generation-skill
description: Generate and update engineering documentation from code and existing artifacts. Use when docs are missing, outdated, or required for handoff/release.
---

# Skill Name
documentation-generation-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 自动化生成并维护工程文档。

## When to Use
- 文档缺失、过期或发布前需要对齐时。
- 重大代码改动后需要同步规格/架构/操作说明时。

## Inputs
- 当前代码、测试、配置与现有 `docs/*`。
- `_LLM/project_state.yaml` 当前阶段信息。

## Outputs
- 更新后的 `docs/spec.md`、`docs/architecture.md`、`docs/tasks.md` 或使用文档。
- 文档变更摘要与一致性检查结论。

## Operating Procedure
1. 读取代码与现有 docs。
2. 生成或更新目标文档。
3. 校验文档与实现一致性。
4. 记录更新范围、未覆盖项和后续维护建议。

## Constraints
- 文档内容必须以代码事实为准，禁止臆测接口行为。
- 变更应最小化并保持术语一致。
- 不得覆盖用户已明确标注为手工维护的段落（若有标注）。

## Examples
- Input: 新增消息重试机制但 `architecture.md` 未同步。
- Output: 更新架构文档并补充重试流程与失败路径说明。
