# Software Engineering Skill Cluster（单人开发者 + Codex）

一个面向 **单人开发者 + AI 编程助手（Codex）** 的软件工程 Skill 集群。

目标是让 Codex 在项目中按阶段化工程流程工作（需求、架构、任务、实现、审查、测试、发布、迭代），并通过状态文件在不同 Session 间保持连续性，避免无结构的“想到哪写到哪”。

## 项目分析（当前仓库现状）

该仓库当前已经完成了第一版可用资产，核心特点如下：

1. 流程完整：覆盖 idea -> release -> iteration 的全生命周期。
2. 架构清晰：已拆分 Workflow、Phase、Utility、System 四类 Skill。
3. 状态驱动：通过 `_LLM/project_state.yaml`、`_LLM/task_state.yaml`、`_LLM/git_state.yaml` 管理会话进度。
4. 闭环治理：通过 `docs_issue/*.md` 做问题发现、修复、复检、关闭。
5. 可复用模板：提供 task/issue/state/skill 模板与示例工程。

简要评估：

- 优点：模块化程度高、流程可追踪、对单人开发足够轻量。
- 风险点：已提供基础自动化脚本，但仍需按项目实际补充更细粒度校验（例如任务依赖约束、覆盖率门禁）。
- 适用性：非常适合作为“AI 工程流程标准骨架”，可直接复制到新项目使用。

## 目录结构

```text
skill_cluster/
  workflow/      # 工作流控制与调度
  phase/         # 各阶段技能（需求、架构、实现、测试等）
  utility/       # 横切能力（安全、性能、文档、重构辅助）
  system/        # 状态机/路由/系统级技能与总设计文档
  templates/     # 可复用模板（state/task/issue/skill）
  examples/      # 示例工程骨架与样例状态
```

## 文档分层（避免冗余）

1. Skill 正文（规则真值）：`skill_cluster/**/SKILL.md`
2. Skill 依赖文档（设计与路由）：`skill_cluster/system/*.md|*.yaml`、`skill_cluster/templates/*.md`
3. 项目使用文档（面向使用者）：`README.md`、`START_PY_USAGE.md`

Issue 规则以 `skill_cluster/system/issue-engine/SKILL.md` 与 `skill_cluster/templates/issue-template.md` 为准，其它文档只做引用与摘要。

## 核心设计

### 1) Workflow Controller
- 生命周期门禁控制。
- 管理阶段进入/退出条件。

### 2) Skill Dispatcher
- 根据 `current_stage` 选择并激活 Skill。
- 路由表见 `skill_cluster/system/dispatcher_routes.yaml`。

### 3) Task Engine
- 读取 `docs/tasks.md`。
- 更新 `_LLM/task_state.yaml`，同步当前任务。

### 4) Issue Engine
- 问题落盘到 `docs_issue/<status>__<issue_id>__<summary>.md`。
- 文件名中的 `status` 是唯一真值来源，状态流转必须通过重命名完成。
- 完整状态集合与流转规则以 `skill_cluster/system/issue-engine/SKILL.md` 为准。

### 5) Git Ops
- 在关键阶段出口自动调用 `git-commit-push-skill`。
- commit 使用 conventional commits，push 按策略可选执行（无 remote 时允许跳过）。

### 6) State Machine
- 状态机定义见 `skill_cluster/system/workflow_state_machine.yaml`。
- 禁止跳过关键阶段（例如从需求前直接进入实现）。

## 已提供的关键文档

1. 总体设计文档：
   - `skill_cluster/system/software_engineering_skill_cluster_design.md`
2. 状态机与路由：
   - `skill_cluster/system/workflow_state_machine.yaml`
   - `skill_cluster/system/dispatcher_routes.yaml`
3. 模板：
   - `skill_cluster/templates/skill-template.md`
   - `skill_cluster/templates/project_state.template.yaml`
   - `skill_cluster/templates/task_state.template.yaml`
   - `skill_cluster/templates/git_state.template.yaml`
   - `skill_cluster/templates/tasks-template.md`
   - `skill_cluster/templates/issue-template.md`
4. 示例工程：
   - `skill_cluster/examples/project_root/`

## Skill 清单（简版）

### Workflow
- `software-engineering-workflow`
- `skill-dispatcher`

### System
- `task-engine`
- `issue-engine`

### Phase
- `idea-clarification-skill`
- `problem-definition-skill`
- `requirements-analysis-skill`
- `architecture-design-skill`
- `module-design-skill`
- `task-planning-skill`
- `implementation-skill`
- `code-review-skill`
- `testing-skill`
- `refactoring-skill`
- `release-management-skill`
- `iteration-planning-skill`

### Utility
- `security-assessment-skill`
- `performance-analysis-skill`
- `documentation-generation-skill`
- `refactor-helper-skill`
- `git-commit-push-skill`

## 推荐执行顺序

```text
idea-clarification-skill
-> problem-definition-skill
-> requirements-analysis-skill
-> architecture-design-skill
-> module-design-skill
-> task-planning-skill
-> task-engine
-> implementation-skill
-> git-commit-push-skill (task completed)
-> code-review-skill
-> testing-skill
-> issue-engine
-> git-commit-push-skill (issue resolved)
-> refactoring-skill
-> release-management-skill
-> git-commit-push-skill (release checkpoint)
-> iteration-planning-skill
```

## 快速开始（在你的项目中落地）

1. 复制以下目录到你的项目根目录：
   - `skill_cluster/templates/*`
   - `skill_cluster/examples/project_root/docs`（按需）
2. 初始化状态文件：
   - `_LLM/project_state.yaml`（参考 `project_state.template.yaml`）
   - `_LLM/task_state.yaml`（参考 `task_state.template.yaml`）
   - `_LLM/git_state.yaml`（参考 `git_state.template.yaml`）
3. 创建任务与文档：
   - `docs/idea.md`
   - `docs/problem.md`
   - `docs/spec.md`
   - `docs/architecture.md`
   - `docs/tasks.md`（推荐每个任务包含 `done_criteria` 与 `depends_on`）
4. 每次 Codex Session 固定流程：
   - 读取 `_LLM/project_state.yaml`
   - 运行 `python3 scripts/run_workflow.py dispatch` 选择当前 Skill
   - 按 Task 实现/审查/测试
   - 发现问题写入 `docs_issue/`（文件名使用 `<status>__<issue_id>__<summary>.md`）
   - 在阶段出口运行 `python3 scripts/run_workflow.py hook --event <event>` 触发自动 commit（push 按策略）
   - 回写三个 state 文件

## 统一脚本入口

项目现在使用单一脚本 `start.py` 处理两类任务：

1. 项目初始化（当前目录）：`python3 start.py init`
2. 全局技能安装：`python3 start.py install`

固定规则：
1. `init` 只创建当前项目所需目录和文件。
2. `init` 默认会检查并初始化 git 仓库（默认分支 `main`，可通过参数覆盖）。
3. `install` 只安装到 Codex 全局目录 `~/.codex/skills`。
4. 不允许将 skills 安装到软件工程项目根目录。
5. `init` 会生成 `docs/issue-file-template.md`，`docs_issue/` 仅用于真实问题文件。
6. `install --undo` 仅删除通过“marker + SKILL name”校验为本项目来源的技能目录。
7. `init --undo` 默认需要二次确认；非交互环境需显式 `--yes`。
8. 支持反向操作：
   - `python3 start.py init --undo`
   - `python3 start.py install --undo`

完整参数说明见 `START_PY_USAGE.md`。

## 流程自动化脚本

项目已提供轻量执行脚本：

1. `python3 scripts/run_workflow.py dispatch`
   - 读取 `_LLM/project_state.yaml.current_stage` 并写回 `active_skill`。
2. `python3 scripts/run_workflow.py hook --event task_completed`
   - 执行阶段出口 hook（当前内置 `git-commit-push-skill`）。
3. `python3 scripts/validate_workflow_state.py --next-stage implementation`
   - 校验状态机阶段合法性、关键文档门禁与 release 阶段高优先级 issue 阻塞。

## Codex 操作规约（建议强制）

1. 开始任务前必须先读状态文件和 docs。
2. 没有 `docs/tasks.md` 不允许直接做复杂实现。
3. 发现问题必须落盘到 `docs_issue/`，不能只停留在对话里。
4. 重大变更必须同步更新 `docs/spec.md` 或 `docs/architecture.md`。
5. 始终遵循 task-driven development。

## 下一步建议

1. 增加自动化脚本：
   - `scripts/run_workflow.py`（调度与阶段出口 hook）
   - `scripts/validate_workflow_state.py`（状态机与门禁校验）
   - `python3 scripts/check_skill_versions.py`（校验 cluster_version 一致性）
2. 增加质量门禁：
   - pre-commit 检查 `project_state.yaml` 是否更新
   - release 前检查高优先级 issue 是否为 0
3. 为每个 Skill 补充 `agents/openai.yaml`，方便在技能面板中展示。
