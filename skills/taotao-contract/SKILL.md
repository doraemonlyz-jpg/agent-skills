---
name: taotao-contract
description: 契约优先的跨阶段切片：让 OpenAPI / proto / thrift 接口契约贯穿 ARD（盘点接口）→ Design（契约即接口设计）→ Plan（先落契约与代码生成）→ Impl（生成代码并校验实现与契约一致）→ CR（破坏性变更检测）。由 taotao-flow 的 inputSlot 机制按阶段加载同目录的 ard.md / design.md / plan.md / impl.md / cr.md，一般不单独触发；用户问"接口契约怎么管""改 proto 会不会破坏兼容""先定接口再写代码"时也可使用。相当于 soda 中 great-ui-plus 那类跨阶段切片的后端版本。
metadata:
  version: 1.0.0
  short-description: 契约优先跨阶段切片
---

# taotao-contract — 契约优先切片

## 为什么

后端需求返工最贵的一类是接口返工：字段名、类型、错误码在联调时才对齐。把契约文件当作唯一事实来源——先定契约、再生成代码和 mock、最后实现——调用方和实现方从第一天就对着同一份东西工作。

## 契约文件约定

按项目现状识别，不强行引入新格式：

| 项目 | 契约 | 代码生成 | 校验 / 破坏性检测 |
|---|---|---|---|
| HTTP（gin/echo/hertz/chi） | `api/openapi.yaml` | oapi-codegen（或项目已有方式；只用 swag 注释生成文档的项目，契约就是注释 + 生成的 swagger） | `oasdiff breaking old.yaml new.yaml`；`npx @redocly/cli lint` |
| gRPC / Connect | `api/**/*.proto` | buf generate / protoc | `buf lint`、`buf breaking --against '.git#branch=<主干>'` |
| Kitex / Thrift | `idl/**/*.thrift` | kitex 生成 | 人工比对字段编号与 required 变化 |

契约位置与生成命令写进 `docs/rules/tech-selection.md`；没有就在 design 切片里和用户确认后登记。

## 阶段文件

| 阶段 | 文件 | 做什么 |
|---|---|---|
| ARD | `ard.md` | 盘点新增/变更接口，确认契约归属与调用方 |
| Design | `design.md` | 写出契约变更（diff），作为接口设计章节的唯一来源 |
| Plan | `plan.md` | 插入「契约落地 + 生成代码」「契约 mock」任务，排在实现任务之前 |
| Impl | `impl.md` | 先跑生成，校验生成物无漂移、handler 签名与契约一致 |
| CR | `cr.md` | 破坏性变更检测，结果并入 CR 报告 |

**自门控**：每个阶段文件先读上一阶段产物中本切片的章节；上游写了「不涉及接口变更」或章节不存在，就输出「taotao-contract：本阶段不参与」并跳过。
