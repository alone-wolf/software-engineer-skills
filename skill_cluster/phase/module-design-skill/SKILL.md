---
name: module-design-skill
description: Decompose architecture into modules with explicit responsibilities and interfaces. Use after architecture design and before task planning.
---

# Skill Name
module-design-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 将架构落地到模块级接口与职责。

## When to Use
- `current_stage: module_design`
- `docs/architecture.md` 已稳定并可进入模块拆分。

## Inputs
- `docs/spec.md`
- `docs/architecture.md`
- 关键技术约束（语言、运行环境、依赖限制）。

## Outputs
- `docs/module_design.md`
- 面向任务拆解的模块边界、接口契约与依赖关系。

## Operating Procedure
1. 读取 `docs/architecture.md`。
2. 列出模块职责、输入/输出与错误边界。
3. 定义模块间接口和数据契约。
4. 标注高风险模块与测试重点。
5. 生成 `docs/module_design.md`。
6. 更新阶段到 `task_planning`。

## Constraints
- 模块职责必须单一且可测试。
- 禁止跨模块隐式耦合（共享隐藏状态、未声明依赖）。
- 接口定义需支持后续任务级拆分与验收。

## Examples
- Input: `architecture.md` 包含 gateway、auth、realtime 三层。
- Output: `module_design.md` 定义每层职责、接口契约与依赖图。
