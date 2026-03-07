---
name: security-assessment-skill
description: Assess security risks, produce evidence-backed findings, and drive remediation tracking. Use when authentication, authorization, input handling, secrets, or external integrations are involved.
---

# Skill Name
security-assessment-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.0.0`
- cluster_version: `1.2.0`

## Purpose
- 识别安全风险并形成整改闭环。

## Operating Procedure
1. 扫描鉴权、输入、依赖与配置。
2. 输出风险与修复建议。
3. 高风险项写入 `docs_issue/`。
