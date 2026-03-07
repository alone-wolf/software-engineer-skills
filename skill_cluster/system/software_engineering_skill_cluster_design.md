# Software Engineering Skill Cluster 设计（Solo Dev + Codex）

## 1. 概述

### 1.1 设计目标
1. 让 Codex 在单人项目中按软件工程阶段化流程工作，而不是一次性无结构编码。
2. 通过统一状态文件实现跨 Session 连续性，避免“上下文丢失导致重复决策”。
3. 通过模块化 Skill 组合实现可替换、可裁剪、可迭代的流程系统。
4. 以简单稳定优先，避免企业级重流程开销。

### 1.2 为什么采用 Skill 集群而不是单 Skill
1. 单 Skill 难以同时覆盖需求、架构、实现、测试、发布等异构任务，容易臃肿且触发不精确。
2. Skill 集群允许“阶段职责单一”，每个 Skill 只处理一个阶段目标，稳定性更高。
3. 集群可按项目规模裁剪，例如小项目可以跳过复杂 Utility Skill。
4. 通过 Dispatcher + State Machine，能让 AI 行为可预测、可审计。

### 1.3 系统设计原则
1. Task-driven Development：实现工作必须由 `docs/tasks.md` 驱动。
2. State-first Execution：每次会话先读 `_LLM/project_state.yaml` 再行动。
3. Artifact-first Traceability：每阶段必须产出可落盘文档或代码资产。
4. One-way Stage Gate：阶段切换有进入/退出条件，减少回滚混乱。
5. Issue Closed Loop：发现问题必须进入 `docs_issue/` 并复检关闭。
6. Minimal Process：仅保留单人开发必要控制点。
7. VCS Traceability：关键阶段出口应自动生成可追踪 git commit。

## 2. Skill Architecture

### 2.1 核心组件
1. Workflow Controller：生命周期控制与阶段门禁。
2. Skill Dispatcher：按状态选择并调用当前 Skill。
3. Task Engine：读取 `docs/tasks.md`，维护 `_LLM/task_state.yaml`。
4. Issue Engine：维护 `docs_issue/*.md` 问题单与整改闭环。
5. Phase Skills：阶段技能，生成文档/代码/测试。
6. Utility Skills：横切能力，如安全、性能、重构、文档。
7. Artifact Layer：项目资产层，承接所有落盘产物。
8. Git Ops：关键节点自动提交与可选推送策略。

### 2.2 组件职责

| Component | Primary Responsibility | 关键输入 | 关键输出 |
|---|---|---|---|
| Workflow Controller | 管理生命周期状态与门禁 | `_LLM/project_state.yaml` | 更新后的状态、下一阶段建议 |
| Skill Dispatcher | 基于阶段选择 Skill 并传参 | `current_stage/current_task` | `active_skill`、执行上下文 |
| Task Engine | 任务解析与进度推进 | `docs/tasks.md`、`_LLM/task_state.yaml` | 当前任务、任务状态更新 |
| Issue Engine | 问题登记、整改、复检 | 测试/审计发现项 | `docs_issue/<status>__<issue_id>__<summary>.md`、状态变更记录 |
| Phase Skills | 每阶段产出工程资产 | 当前阶段输入文档 | `docs/*.md`、`src/*`、`tests/*` |
| Utility Skills | 提供横向质量增强 | 代码、测试、指标 | 审计报告、性能报告、重构建议 |
| Git Ops | 提交与推送策略执行 | git 变更、`_LLM/git_state.yaml` | commit 记录、可选 push 结果 |
| Artifact Layer | 统一资产存储 | 全部流程输入输出 | 规范化工程文档与代码资产 |

## 3. Skill Catalog（建议清单）

### 3.1 Workflow Skills

| Skill Name | Purpose | When to Use | Inputs | Outputs | Typical Workflow |
|---|---|---|---|---|---|
| `software-engineering-workflow` | 控制端到端流程 | 新项目启动或阶段迁移 | `project_state.yaml` + docs | 阶段决策、门禁检查 | 读状态 -> 校验入口 -> 调度下一阶段 |
| `skill-dispatcher` | 统一调度技能 | 每次 Session 开始 | `current_stage`、任务状态 | `active_skill` | 解析状态 -> 选择 Skill -> 下发上下文 |

### 3.2 Task System Skills

| Skill Name | Purpose | When to Use | Inputs | Outputs | Typical Workflow |
|---|---|---|---|---|---|
| `task-engine` | 任务选择与进度更新 | 进入实现/测试前 | `docs/tasks.md`、`task_state.yaml` | `current_task`、状态推进 | 解析任务 -> 选任务 -> 写状态 |

### 3.3 Issue System Skills

| Skill Name | Purpose | When to Use | Inputs | Outputs | Typical Workflow |
|---|---|---|---|---|---|
| `issue-engine` | 问题全生命周期管理 | 审查/测试发现问题时 | 缺陷证据、影响评估 | `docs_issue/<status>__<issue_id>__<summary>.md` | 建单 -> 确认 -> 修复 -> 复检 -> 归档 |

### 3.4 Phase Skills

| Skill Name | Purpose | When to Use | Inputs | Outputs | Typical Workflow |
|---|---|---|---|---|---|
| `idea-clarification-skill` | 澄清目标与边界 | 项目初始阶段 | 原始想法 | `docs/idea.md` | 拆目标 -> 定边界 -> 形成问题陈述 |
| `problem-definition-skill` | 明确定义问题 | 想法澄清后 | `idea.md` | `docs/problem.md` | 用户/痛点/成功标准定义 |
| `requirements-analysis-skill` | 需求工程与验收标准 | 问题定义后 | `problem.md` | `docs/spec.md` | FR/NFR -> 边界 -> AC |
| `architecture-design-skill` | 系统架构设计 | 需求冻结后 | `spec.md` | `docs/architecture.md` | 组件/数据流/风险设计 |
| `module-design-skill` | 模块接口与职责细化 | 架构完成后 | `architecture.md` | `docs/module_design.md` | 模块拆分 -> API/契约 |
| `task-planning-skill` | 任务拆解与排期 | 模块设计后 | `module_design.md` | `docs/tasks.md` | 拆任务 -> 定依赖 -> 优先级 |
| `implementation-skill` | 按任务实现代码 | 有可执行任务时 | `tasks.md`、`task_state.yaml` | `src/*` 变更、实现记录 | 选任务 -> 编码 -> 自检 |
| `code-review-skill` | 代码审计与风险识别 | 实现后提交前 | diff、规范、架构约束 | 审查结论、Issue 输入 | 静态审查 -> 风险分类 |
| `testing-skill` | 测试设计与执行 | 审查后或修复后 | 需求/代码 | `tests/*`、测试报告 | 写测例 -> 执行 -> 记录缺陷 |
| `refactoring-skill` | 结构性优化 | 缺陷收敛后 | 代码异味、性能债务 | 重构变更、回归结果 | 识别异味 -> 小步重构 |
| `release-management-skill` | 发布准备与验收 | 迭代完成时 | 测试/Issue状态 | 发布清单、版本记录 | 发布门禁 -> 变更说明 |
| `iteration-planning-skill` | 版本迭代规划 | 发布后 | 发布反馈、遗留问题 | 下迭代目标与任务草案 | 复盘 -> 新需求入池 |

### 3.5 Utility Skills

| Skill Name | Purpose | When to Use | Inputs | Outputs | Typical Workflow |
|---|---|---|---|---|---|
| `security-assessment-skill` | 安全评估与整改建议 | 涉及鉴权、输入、外部依赖时 | 代码、配置、接口 | 安全问题列表、修复建议 | 扫描关键面 -> 证据化输出 |
| `performance-analysis-skill` | 性能瓶颈定位 | 响应慢、资源高时 | profiler/benchmark 数据 | 性能报告、优化建议 | 建基线 -> 定位热点 -> 验证提升 |
| `documentation-generation-skill` | 自动化文档生产 | 阶段产出缺文档时 | 现有代码与规格 | API/模块/运维文档 | 提取事实 -> 生成文档 |
| `refactor-helper-skill` | 辅助重构策略与脚手架 | 大规模重构前 | 架构与调用关系 | 重构计划、迁移步骤 | 风险分层 -> 渐进迁移 |
| `git-commit-push-skill` | 统一 commit/push 自动化策略 | 任务完成、问题解决、发布门禁 | git diff、`git_state.yaml` | conventional commit、可选 push 结果 | 识别上下文 -> 提交 -> 按策略 push |

## 4. Skill Invocation Order（标准流程）

`idea-clarification-skill`
-> `problem-definition-skill`
-> `requirements-analysis-skill`
-> `architecture-design-skill`
-> `module-design-skill`
-> `task-planning-skill`
-> `task-engine`
-> `implementation-skill`
-> `git-commit-push-skill`（task completed）
-> `code-review-skill`
-> `testing-skill`
-> `issue-engine`
-> `git-commit-push-skill`（issue resolved）
-> `refactoring-skill`
-> `release-management-skill`
-> `git-commit-push-skill`（release checkpoint）
-> `iteration-planning-skill`

### 4.1 阶段转换逻辑
1. 前一阶段输出文档存在且通过最低验收标准，才可进入下一阶段。
2. `implementation` 前必须有 `docs/tasks.md` 且 `_LLM/task_state.yaml` 有当前任务。
3. `review/testing` 若发现问题，强制进入 `issue_fixing`（由 `issue-engine` 管理）。
4. `issue_fixing` 完成后返回 `review` 或 `testing` 复检。
5. `release` 仅在关键任务完成、阻断级 Issue 清零时允许进入。
6. `iteration` 生成下一轮任务后，状态回到 `idea` 或 `requirements`。

## 5. Workflow State Machine

### 5.1 状态枚举
`idea` -> `problem_definition` -> `requirements` -> `architecture` -> `module_design` -> `task_planning` -> `implementation` -> `review` -> `testing` -> `issue_fixing` -> `refactoring` -> `release` -> `iteration`

### 5.2 进入条件（Entry）
1. `idea`：新项目或新迭代启动。
2. `problem_definition`：`idea.md` 已形成核心目标与边界。
3. `requirements`：`problem.md` 明确目标用户、场景、成功标准。
4. `architecture`：`spec.md` 冻结 MVP 范围与验收标准。
5. `module_design`：`architecture.md` 已定义组件和接口风格。
6. `task_planning`：模块职责与接口契约可执行。
7. `implementation`：`tasks.md` 与 `task_state.yaml` 有当前任务。
8. `review`：存在可审查代码变更。
9. `testing`：审查通过或完成修复。
10. `issue_fixing`：存在打开状态 Issue。
11. `refactoring`：功能稳定但有结构性债务。
12. `release`：测试通过且高优先级 Issue 已关闭。
13. `iteration`：版本发布完成并进入下一轮规划。

### 5.3 退出条件（Exit）
1. 每个状态都需产出明确资产（文档、代码、报告或 Issue 更新）。
2. `implementation` 必须完成当前任务并更新 `_LLM/task_state.yaml`。
3. `review/testing` 若无阻断问题可退出；否则转 `issue_fixing`。
4. `issue_fixing` 仅在复检通过后可退出。
5. `release` 完成后必须更新版本记录与迭代入口信息。

### 5.4 转换规则
1. 默认线性前进。
2. 任一状态可因阻断问题回退到 `issue_fixing`。
3. 禁止跨越 `requirements` 直接进入 `implementation`。
4. Dispatcher 仅允许执行与 `current_stage` 一致或“问题修复”相关技能。

## 6. Skill Dispatcher Design

### 6.1 输入
1. `_LLM/project_state.yaml`
2. `_LLM/task_state.yaml`（可选）
3. `_LLM/git_state.yaml`（可选）
4. `docs/tasks.md`（可选）

### 6.2 调度策略
1. 读取 `current_stage`。
2. 校验阶段依赖资产是否满足。
3. 不满足则返回上游补齐建议并阻止编码。
4. 满足则写入 `active_skill` 并执行。
5. 执行后更新 `last_updated`、`notes`、必要时更新 `current_stage`。

### 6.3 路由表示例
- `idea` -> `idea-clarification-skill`
- `requirements` -> `requirements-analysis-skill`
- `implementation` -> `task-engine` then `implementation-skill`
- `review` -> `code-review-skill`
- `testing` -> `testing-skill`
- `issue_fixing` -> `issue-engine` + `implementation-skill`

## 7. Project State File Design

路径：`_LLM/project_state.yaml`

```yaml
project_name: example_project
current_stage: implementation
current_task: task_03
progress: 35%
active_skill: implementation-skill
last_updated: 2026-03-06
notes: implementing websocket authentication
```

### 7.1 会话规则
1. 每个 Codex Session 开始先读取此文件。
2. 根据 `current_stage` 选择 Skill。
3. Skill 执行后必须更新该文件。
4. 禁止通过“文件是否存在”推断阶段。

## 7.2 Git State File Design

路径：`_LLM/git_state.yaml`

```yaml
enabled: true
default_branch: main
auto_commit: true
push_mode: if_remote
commit_message_convention: conventional_commits
last_commit: ""
last_push_status: never
last_updated: 2026-03-07
notes: ""
```

会话规则：
1. 若 `enabled: true`，阶段出口按策略触发 `git-commit-push-skill`。
2. `push_mode` 支持 `never/if_remote/always`。
3. push 失败不应回滚已完成 commit，但必须记录状态。

## 8. Task Engine Design

### 8.1 输入输出
1. 输入：`docs/tasks.md`、`_LLM/task_state.yaml`。
2. 输出：更新后的 `_LLM/task_state.yaml` 与任务日志备注。

### 8.2 `docs/tasks.md` 建议格式
```md
# Tasks
- [x] task_01 初始化项目骨架
- [x] task_02 完成登录接口
- [ ] task_03 实现 websocket 鉴权
- [ ] task_04 增加鉴权测试
```

### 8.3 `task_state.yaml` 示例
```yaml
current_task: task_03
completed_tasks:
  - task_01
  - task_02
status: in_progress
last_updated: 2026-03-06
```

### 8.4 引擎职责
1. 解析任务列表并识别可执行任务。
2. 选择当前任务（默认首个未完成任务，或按优先级标签）。
3. 在任务完成后更新 `completed_tasks` 与 `status`。
4. 同步 `project_state.yaml.current_task`。

## 9. Issue Engine Design

### 9.1 存储
路径：`docs_issue/`，每个问题一个 Markdown 文件。

### 9.2 Issue 模板
- 模板文件：`skill_cluster/templates/issue-template.md`
- 初始化后项目内模板：`docs/issue-file-template.md`
- 字段定义、时间格式、状态记录以模板为准，避免在多文档重复维护同一结构。

### 9.3 状态流
文件命名格式：`<status>__<issue_id>__<summary>.md`

- 状态机权威定义：`system/issue-engine/SKILL.md`
- 默认流程：`waiting_user` -> `approved` -> `in_progress` -> `verifying` -> `resolved`
- 扩展状态：`deferred`、`rejected`、`archived`

### 9.4 引擎职责
1. 审查/测试发现问题时先做第一层去重扫描，再决定是否建单。
2. 新建问题文件必须以 `waiting_user` 状态创建。
3. 用户确认后通过文件重命名进入 `approved/in_progress`。
4. 修复完成进入 `verifying`，基于验收标准验证通过后进入 `resolved`。
5. 复检失败或复发问题通过重命名回到 `waiting_user`，不得新建重复问题。

## 10. Skill Repository Structure

```text
skill_cluster/
  workflow/
    software-engineering-workflow/
      SKILL.md
    skill-dispatcher/
      SKILL.md
  phase/
    idea-clarification-skill/SKILL.md
    problem-definition-skill/SKILL.md
    requirements-analysis-skill/SKILL.md
    architecture-design-skill/SKILL.md
    module-design-skill/SKILL.md
    task-planning-skill/SKILL.md
    implementation-skill/SKILL.md
    code-review-skill/SKILL.md
    testing-skill/SKILL.md
    refactoring-skill/SKILL.md
    release-management-skill/SKILL.md
    iteration-planning-skill/SKILL.md
  utility/
    security-assessment-skill/SKILL.md
    performance-analysis-skill/SKILL.md
    documentation-generation-skill/SKILL.md
    refactor-helper-skill/SKILL.md
    git-commit-push-skill/SKILL.md
  system/
    task-engine/SKILL.md
    issue-engine/SKILL.md
    software_engineering_skill_cluster_design.md
  templates/
    skill-template.md
  examples/
    project_root/
      src/
      tests/
      docs/
      docs_issue/
      _LLM/
```

## 11. Project Structure（目标项目依赖结构）

```text
project_root/
  src/
  tests/
  docs/
    idea.md
    problem.md
    spec.md
    architecture.md
    tasks.md
  docs_issue/
  _LLM/
    project_state.yaml
    task_state.yaml
    git_state.yaml
```

## 12. Skill Interaction Model

1. Workflow Controller 决定“现在处于哪个阶段”。
2. Skill Dispatcher 决定“当前应执行哪个 Skill”。
3. Task Engine 决定“当前应完成哪个任务”。
4. Phase Skill 执行“本阶段实际产出”。
5. Code Review/Testing 发现问题后交给 Issue Engine。
6. Utility Skill 在任意阶段按需插入，结果回写 Artifact Layer。
7. 全流程以 `_LLM/project_state.yaml` 作为单一事实源。
8. Git 相关动作由 `git-commit-push-skill` 在阶段出口统一执行并回写 `_LLM/git_state.yaml`。

## 13. Codex Operating Protocol（运行规则）

1. 开始任何任务前必须读取 `_LLM/project_state.yaml` 与 `docs/` 核心文档。
2. 没有 `docs/tasks.md` 时不得直接实现复杂功能。
3. 发现问题必须写入 `docs_issue/`，不得只在对话中口头记录。
4. 重大修改必须更新相应文档（`spec.md`、`architecture.md`、`tasks.md`）。
5. 开发遵循 task-driven development：先任务、后实现、再审查与测试。
6. 每次会话结束前必须更新 `_LLM/project_state.yaml` 与 `_LLM/task_state.yaml`。
7. 问题状态以文件名为唯一真值来源；状态变更必须重命名问题文件。
8. 任务完成、问题关闭、发布检查点应触发自动 commit（push 依据 `git_state.yaml.push_mode`）。

## 14. Skill Template（模板）

模板文件：`skill_cluster/templates/skill-template.md`

包含字段：
1. Skill Name
2. Purpose
3. When to Use
4. Inputs
5. Outputs
6. Operating Procedure
7. Constraints
8. Examples

## 15. Example Skills

完整示例已提供于以下路径：
1. `workflow/software-engineering-workflow/SKILL.md`
2. `workflow/skill-dispatcher/SKILL.md`
3. `system/task-engine/SKILL.md`
4. `system/issue-engine/SKILL.md`
5. `phase/requirements-analysis-skill/SKILL.md`
6. `phase/architecture-design-skill/SKILL.md`
7. `phase/task-planning-skill/SKILL.md`
8. `phase/implementation-skill/SKILL.md`
9. `phase/code-review-skill/SKILL.md`
10. `phase/testing-skill/SKILL.md`

## 16. Versioning Policy（版本策略）

1. `skill_version`：按单个 skill 独立演进，允许不同 skill 使用不同版本号。
2. `cluster_version`：表示技能集群整体版本，所有 `SKILL.md` 必须保持一致。
3. 每次集群级规则或系统行为变更时，统一提升 `cluster_version`。
4. 一致性检查命令：`python3 scripts/check_skill_versions.py`。
