# 问题 ID
Q20260306-01

# 当前状态
waiting_user

# 最后更新时间
2026-03-06 22:30 +08:00

# 问题标题
websocket 鉴权缺失 token 过期校验

# 问题摘要
过期令牌放行风险

# 问题描述
连接握手仅校验签名，未校验 token 过期时间，导致过期 token 仍可能建立连接。

# 严重程度
High

# 影响对象
- `src/ws/auth_middleware.ts`
- websocket 实时频道访问控制

# 问题原因
鉴权中间件未启用 `exp` claim 校验分支，只校验了签名与 issuer。

# 核心证据路径
src/ws/auth_middleware.ts

# 待确认差异
无

# 造成问题的证据
- 代码路径：`src/ws/auth_middleware.ts`
- 日志/报错：`auth_expired_token_should_fail` 断言失败
- 配置位置：N/A
- 复现步骤：执行 websocket 鉴权单测，过期 token 用例返回连接成功。

# 影响
- 过期令牌可能继续访问实时频道，造成越权访问风险。
- 发布门禁会误判鉴权能力，增加线上安全事件概率。

# 建议解决方案
1. 在握手阶段强制校验 `exp` claim。
2. 过期 token 返回统一鉴权错误码。
3. 增加成功/失败/过期三类回归测试。

# 验收标准
1. 过期 token 握手必须失败且返回统一错误码。
2. `auth_expired_token_should_fail` 测试通过。
3. websocket 鉴权相关回归用例全部通过。

# 验证记录
- 标准 1 -> 验证动作：执行过期 token 握手集成测试 | 结果：Pass | 证据/原因：握手返回 401 与 `TOKEN_EXPIRED`。
- 标准 2 -> 验证动作：运行 `auth_expired_token_should_fail` | 结果：Pass | 证据/原因：断言通过。
- 标准 3 -> 验证动作：运行 websocket 鉴权回归测试集 | 结果：Pass | 证据/原因：相关用例全绿。

# 评论
同意修复

# 状态变更记录
- 时间：2026-03-06 22:30 +08:00 | 状态：waiting_user | 原因：新建问题并等待用户确认 | 操作者：codex | 关联提交：N/A
