# taotao-contract · Design 切片

## 自门控

读 ARD 的「接口契约（taotao-contract）」章节；为「不涉及接口变更」或不存在 → 跳过。

## 确定契约文件与工具

- 已有契约文件 → 沿用；
- 没有 → 和用户确认一次：引入 `api/openapi.yaml`（HTTP）/ `.proto`（gRPC），还是本次只在 Design 里用表格定义（以后再补）。选择写进 `docs/rules/tech-selection.md`。

## 写契约变更

对每个 ARD 盘点出的接口，给出契约文件的具体改动（diff 形式），至少包含：路径/方法或 RPC 名、请求字段（类型、必填、校验）、响应结构、错误码/错误响应、示例。

```yaml
# api/openapi.yaml（节选）
  /api/v1/order/cancel:
    post:
      operationId: cancelOrder
      requestBody: { $ref: '#/components/requestBodies/CancelOrder' }
      responses:
        '200': { $ref: '#/components/responses/CancelOrderOK' }
        '409': { description: 订单状态不允许取消, content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } } }
```

变更已有接口时运行破坏性检测（`oasdiff breaking` / `buf breaking`）并贴结果；破坏性变更必须写兼容方案（新旧字段并存期、版本化路径、调用方迁移计划）。

## 产出

作为独立章节 `## 接口契约（taotao-contract）` 追加到 Design：契约文件路径、diff、破坏性检测结果、兼容方案。Design 的「接口设计」章节引用它，不再重复字段表——after_design 钩子的「接口四要素」检查以契约 diff 为准。
