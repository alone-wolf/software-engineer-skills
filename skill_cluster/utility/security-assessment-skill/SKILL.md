---
name: security-assessment-skill
description: Assess security risks, produce evidence-backed findings, and drive remediation tracking. Use when authentication, authorization, input handling, secrets, or external integrations are involved.
---

# Skill Name
security-assessment-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 识别安全风险并形成整改闭环。

## When to Use
- 涉及鉴权、输入处理、密钥管理、外部依赖或暴露接口时。
- `review/testing/release` 前需要执行安全门禁时。

## Inputs
- 目标代码/配置/依赖清单。
- `docs/spec.md`、`docs/architecture.md`、历史安全问题记录。

## Outputs
- 风险清单（含严重度、证据、修复建议）。
- 需跟踪问题写入 `docs_issue/`（一问题一文件）。

## Operating Procedure
1. 扫描鉴权、输入、依赖与配置。
2. 按严重度分类并给出可执行修复建议。
3. 高风险项写入 `docs_issue/`，并补充验收标准。
4. 需要执行闭环时走 `issue-engine` 状态流转。

## Constraints
- 风险结论必须有证据，不能仅凭主观判断。
- `High/Critical` 风险不得在 release 前忽略。
- 发现问题后必须落盘，不能只停留在口头建议。

## Examples
- Input: 新增 OAuth 回调接口且缺少 state 校验。
- Output: 生成 High 风险项并创建 issue 文件跟踪修复。
