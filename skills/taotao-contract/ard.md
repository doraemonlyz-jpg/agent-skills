# taotao-contract · ARD 切片

## 前置确认

根据 PRD 和影响域判断本需求是否涉及接口新增或变更（HTTP 路由、RPC 方法、MQ 消息体、对外回调）。明显不涉及时直接产出「不涉及接口变更」，不打扰用户；拿不准时问一次：

```
本需求是否新增或修改对外接口（HTTP / RPC / MQ）？
a. 是  b. 否  c. 不确定，先按"是"盘点
```

## 盘点

| 接口 | 类型 | 新增/变更 | 调用方 | 契约文件 | 契约负责人 | 是否兼容 |
|---|---|---|---|---|---|---|
| `POST /api/v1/order/cancel` | HTTP | 新增 | App、客服后台 | api/openapi.yaml | 本服务 | — |

- 契约文件现状：用 `git ls-files | grep -E '\.(proto|thrift)$|openapi.*\.ya?ml$|swagger'` 找；都没有时记录"无契约文件"，在 design 切片决定是否引入。
- 变更已有接口时先判断兼容性：删字段、改类型、改语义、required 变化都算破坏性，需要在 ARD 风险里写兼容期方案。

## 产出

交回 tt:ard，落盘时作为独立章节 `## 接口契约（taotao-contract）` 写入 ARD；不涉及时章节内容为「不涉及接口变更」。
