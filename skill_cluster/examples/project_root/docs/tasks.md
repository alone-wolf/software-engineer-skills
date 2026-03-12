# Tasks

- [x] task_01 初始化项目骨架
  - done_criteria:
    - 项目目录结构可运行且基础依赖安装完成
  - depends_on: []

- [x] task_02 完成登录接口
  - done_criteria:
    - 登录接口返回 token 且异常路径可处理
  - depends_on: [task_01]

- [ ] task_03 实现 websocket 鉴权
  - done_criteria:
    - websocket 连接需校验 token 且拒绝过期/无效令牌
  - depends_on: [task_02]

- [ ] task_04 增加鉴权测试
  - done_criteria:
    - 覆盖成功、失败、过期三类鉴权场景
  - depends_on: [task_03]
