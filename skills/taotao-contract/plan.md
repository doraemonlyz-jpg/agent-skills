# taotao-contract · Plan 切片

## 自门控

读 Design 的「接口契约（taotao-contract）」章节；不存在或为「不涉及」→ 跳过。

## 插入任务

在所有实现任务之前插入（与主流程统一编号，后续任务的 Interfaces 引用这里的产出）：

```markdown
### Task 1: 契约落地与代码生成

**Files:**
- Modify: `api/openapi.yaml`（或 .proto / .thrift）
- Create/Modify: 生成目录（如 `internal/api/gen/`）

**Interfaces:**
- Produces: 生成的请求/响应类型与 server 接口（列出类型名）

- [ ] **Step 1: 按 Design 契约 diff 修改契约文件**
- [ ] **Step 2: 校验契约**

Run: `buf lint` / `npx @redocly/cli lint api/openapi.yaml`
Expected: 无错误

- [ ] **Step 3: 破坏性检测（变更已有接口时）**

Run: `buf breaking --against '.git#branch=master'` / `oasdiff breaking <旧> api/openapi.yaml`
Expected: 无破坏性变更，或只有 Design 中已声明兼容方案的那几项

- [ ] **Step 4: 生成代码并编译**

Run: `<生成命令> && go build ./...`
Expected: 成功

- [ ] **Step 5: 提交**

### Task 2: 契约 mock

- [ ] **Step 1: 按 taotao-mock 为调用方/联调准备 mock（Prism 或进程内 fake），启动命令写入 Makefile**
- [ ] **Step 2: curl / 测试验证四种场景（正常、空、错误码、超时）**
- [ ] **Step 3: 提交**
```

在 Plan 的 Global Constraints 中追加一行：`接口以 <契约文件> 为唯一事实来源；实现与契约不一致时改实现，不改契约（改契约须回到 tt:sync）`。
