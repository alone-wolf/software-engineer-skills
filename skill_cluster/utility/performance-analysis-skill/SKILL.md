---
name: performance-analysis-skill
description: Analyze runtime performance bottlenecks and validate optimization impact with measurable evidence. Use when latency, throughput, or resource usage is below target.
---

# Skill Name
performance-analysis-skill

## Cluster Identity
- cluster_marker: `se-skill-cluster`
- cluster_name: `software-engineering-skill-cluster`
- skill_version: `1.1.0`
- cluster_version: `1.2.0`

## Purpose
- 定位性能瓶颈并验证优化收益。

## When to Use
- 延迟、吞吐、资源占用超出目标时。
- 发布前需要性能基线与回归证据时。

## Inputs
- 关键接口/流程的性能目标与当前指标。
- Profiling/Tracing/Benchmark 结果。
- `docs/spec.md` 中相关 NFR。

## Outputs
- 性能瓶颈分析报告与优化建议。
- 优化前后对比数据与剩余风险说明。

## Operating Procedure
1. 建立性能基线。
2. 分析热点路径与资源消耗。
3. 设计最小影响优化方案并实施验证。
4. 输出优化建议与复测结果。
5. 若性能缺陷需要跟踪，创建或更新 `docs_issue/`。

## Constraints
- 无基线数据不得宣称“性能已提升”。
- 优化必须有可复现的测量方法与样本说明。
- 禁止以牺牲正确性或安全性换取短期性能指标。

## Examples
- Input: WebSocket 广播在高并发下 P95 延迟超标。
- Output: 给出热点路径证据、优化方案与复测数据。
