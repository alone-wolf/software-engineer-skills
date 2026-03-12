# start.py 使用文档（固定操作逻辑）

`start.py` 是统一入口脚本，提供两个固定职责：

1. `init`：仅在**当前项目路径**初始化工程目录和文件。
2. `install`：仅将 skills 安装到 Codex **全局** skills 目录。

不允许将 skills 安装到某软件工程项目根目录下。

## 1. 命令总览

```bash
python3 start.py init [options]
python3 start.py install [options]
```

## 2. init 模式（当前项目初始化）

用途：在你当前所在项目目录中创建软件工程流程所需目录和文件。

### 2.1 基本用法

```bash
python3 start.py init
```

### 2.2 关键参数

- `--project-name <name>`：写入 `_LLM/project_state.yaml` 的项目名
- `--no-git`：跳过 git 仓库初始化，并将 `_LLM/git_state.yaml.enabled` 置为 `false`
- `--git-main-branch <name>`：初始化 git 仓库时使用的默认分支名（默认 `main`）
- `--with-example-docs`：用示例填充 `docs/idea.md`、`docs/problem.md`、`docs/spec.md`、`docs/architecture.md`
- `--minimal`：仅初始化 `_LLM/*.yaml + docs/tasks.md`
- `--force`：覆盖已存在的受管文件
- `--dry-run`：只预览，不落盘
- `--yes`：`init --undo` 时跳过二次确认（非交互环境执行回滚需显式指定）

### 2.3 init 的反向操作

```bash
python3 start.py init --undo
```

行为：删除 `init` 管理的文件，并尝试删除空目录（`docs/`、`docs_issue/`、`_LLM/`）。

- 默认（非 `--minimal`）会回滚完整初始化文件集。
- `--minimal --undo` 只回滚最小文件集（`_LLM/*.yaml + docs/tasks.md`）。
- 可配合 `--dry-run` 预览删除清单。
- 非交互环境执行 `init --undo` 时，需显式加 `--yes`。

### 2.4 init 生成的 Issue 相关资产

- `docs/issue-file-template.md`：问题文件模板（不会放在 `docs_issue/` 内）。
- `docs_issue/.gitkeep`：空目录占位文件。

`docs_issue/` 目录第一层仅用于真实问题文件，命名必须符合：

```text
<status>__<issue_id>__<summary>.md
```

状态值与字段结构以初始化生成的 `docs/issue-file-template.md` 为准。

状态变更必须通过重命名文件完成（文件名状态是唯一真值来源）。完整规则见 `skill_cluster/system/issue-engine/SKILL.md`。

### 2.5 init 生成的 Git 相关资产

- `_LLM/git_state.yaml`：Git 自动提交策略状态文件。
- 默认会在当前目录检查并初始化 Git 仓库：
  - 已存在仓库：不重复初始化，且 `git_state.default_branch` 会对齐当前仓库 `HEAD` 分支
  - 不存在仓库：创建并设置默认分支（默认 `main`）
- 可用 `--no-git` 跳过初始化。

### 2.6 tasks 模板建议

`docs/tasks.md` 建议按模板增加结构化字段，便于 `task-engine` 做确定性调度：

```text
- [ ] task_03 实现 websocket 鉴权
  - done_criteria:
    - websocket 连接必须校验 token 且拒绝过期令牌
  - depends_on: [task_02]
```

## 3. install 模式（全局 skills 安装）

用途：将 skills 安装到 Codex 全局目录：

```text
~/.codex/skills
```

脚本会固定写入全局目录，不提供 `--dest` 或项目级目标目录参数。

### 3.1 基本用法

```bash
python3 start.py install
```

### 3.2 参数

- `--source <path>`：skill 源目录（默认 `<script_dir>/skill_cluster`）
- `--method copy|auto|symlink|junction`：安装方式（默认 `copy`）
- `--only <skill-name>`：只安装指定 skill（可重复）
- `--list`：仅列出可安装 skill 名称
- `--force`：覆盖已存在 skill 目录
- `--dry-run`：只预览，不落盘

### 3.3 install 的反向操作

```bash
python3 start.py install --undo
```

行为：从全局目录卸载本体系技能。

- 不加 `--only`：卸载当前源目录发现的全部 skill。
- 加 `--only`：仅卸载指定 skill。
- 可配合 `--dry-run` 预览删除清单。
- 卸载前会校验目标 skill 目录是否同时满足：
  - 存在本项目 marker 文件 `.se_skill_cluster_marker`
  - `SKILL.md` 中 `name` 与目标 skill 名称一致
  - marker 与 `SKILL.md` 的 cluster 标识匹配本体系
- 不满足条件将 `skip` 并输出 warning，避免误删外部来源同名技能。

示例：

```bash
python3 start.py install --undo
python3 start.py install --undo --only task-engine --only issue-engine
python3 start.py install --undo --dry-run
```

## 4. 安装方式建议

- 默认推荐：`copy`
  - 最稳妥，不依赖软链接权限。
- 自动降级：`auto`
  - Windows：`symlink -> junction -> copy`
  - Linux/macOS：`symlink -> copy`

## 5. 常见问题

### 5.1 为什么 init 不再复制 skill_cluster 到项目根目录

因为操作逻辑已固化：
- `init` 只做项目目录初始化。
- `install` 才负责全局 skills 安装。

### 5.2 技能安装/卸载后 Codex 没变化

重启 Codex 后再使用。

### 5.3 `--only` 报未知 skill

先执行：

```bash
python3 start.py install --list
```

确认名称后再安装或卸载。

## 6. 配套自动化脚本

- 调度当前阶段技能：

```bash
python3 scripts/run_workflow.py dispatch
```

- 执行阶段出口 hook（例如任务完成后自动 git 提交）：

```bash
python3 scripts/run_workflow.py hook --event task_completed
python3 scripts/run_workflow.py hook --event issue_resolved --issue-id Q20260307-01
python3 scripts/run_workflow.py hook --event release_checkpoint --release-tag v1.2.0
```

- 校验状态机与阶段门禁：

```bash
python3 scripts/validate_workflow_state.py
python3 scripts/validate_workflow_state.py --next-stage implementation
```
