# Specification

## Functional Requirements
- 用户连接 websocket 前必须完成 token 鉴权。
- 鉴权失败连接立即断开。
- 鉴权通过后仅订阅授权频道。

## Non-Functional Requirements
- 鉴权延迟 P95 < 100ms。
- 未授权连接成功率 = 0。
