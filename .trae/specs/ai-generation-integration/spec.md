# AI文本生成功能接入 - Product Requirement Document

## Overview
- **Summary**: 将脚本工坊中预留的 AI 生成按钮正式接入 MiniMax 文本接口，实现递进式大纲、人物设定、分集内容生成，并支持草稿编辑、调用记录入库和提示词模板管理。
- **Purpose**: 实现完整的 AI 辅助写作工作流，让用户能够通过 AI 生成草稿内容，人工审核修改后再保存，同时完整记录所有 AI 调用作为复盘依据。
- **Target Users**: 脚本创作者、内容创作者、需要 AI 辅助写作的用户

## Goals
- 实现递进式生成：大纲 → 人物设定 → 分集，每一步可单独触发，后一步依赖前一步已保存的数据
- 生成结果仅作为草稿填充到编辑器，不自动保存，用户可自由修改后手动落库
- 每次 AI 调用（包括成功、失败、错误）都完整记录到 generation_records 表
- 提示词模板在页面可直观查看，并为未来自定义编辑预留接口

## Non-Goals (Out of Scope)
- 不实现自动流水线式端到端全量生成（必须有人工介入点）
- 不实现提示词模板的版本管理（第一版只需可查看和基础存储）
- 不实现异步任务队列（第一版采用同步调用，后续可扩展）
- 不实现 AI 生成结果的自动对比和回滚功能

## Background & Context
### 现有系统状态
1. **后端能力**：
   - 已有 `MiniMaxClient` 客户端，可调用 MiniMax 文本生成接口
   - 已有 `generation_records` 表结构，包含 generation_type、status、prompt、result、error_message、model_used、tokens_used 等字段
   - 已有 `CRUDGenerationRecord` 实现基础 CRUD 操作
   - 已有脚本作品、章节的 CRUD 接口（大纲、人物设定、章节内容的保存接口已就绪）

2. **前端状态**：
   - 页面已预留多个 AI 生成按钮，当前均为 `disabled` 状态：
     - `generate-outline-btn`：自动生成大纲
     - `generate-characters-btn`：自动生成人物设定
     - `generate-chapters-btn`：自动生成分集
     - `generate-chapter-outline-btn`：生成本集大纲
     - `generate-chapter-content-btn`：生成本集内容
   - 已有编辑器保存逻辑：`saveOutline()`、`saveCharacters()`、`saveChapter()`
   - 已有编辑框：`outline-editor`、`characters-editor`、`chapter-outline-editor`、`chapter-content-editor`

3. **数据依赖关系**：
   - 脚本作品 (`script_works`) 包含 `outline`、`characters` 字段
   - 章节 (`script_chapters`) 包含 `outline`、`content` 字段
   - 生成记录 (`generation_records`) 绑定 `script_work_id`、`project_id`、`user_id`、可选 `script_chapter_id`

### 技术栈
- 后端：FastAPI + SQLAlchemy (Async) + MySQL
- 前端：原生 JavaScript (模块化)
- AI 服务：MiniMax 文本生成 API

## Functional Requirements
- **FR-1**: 递进式生成链路
  - 生成大纲：独立调用，无需前置依赖
  - 生成人物设定：必须先有已保存的大纲，生成时自动将大纲作为上下文传入
  - 生成分集：必须先有已保存的大纲和人物设定，生成时自动将两者作为上下文传入
  - 章节级生成（大纲/内容）：依赖当前章节所属作品的大纲和人物设定

- **FR-2**: 草稿模式（核心要求）
  - AI 生成结果仅填充到对应文本编辑框，不调用保存接口
  - 用户可对生成内容进行任意增删改操作
  - 用户必须主动点击「保存」按钮才会将最终内容落库
  - 即使生成内容有错误或垃圾内容，用户仍可编辑或放弃

- **FR-3**: 调用记录持久化
  - 每次点击 AI 生成按钮都创建一条 generation_record
  - 记录包含：请求时间、generation_type、prompt、model_used、tokens_used
  - 成功时记录：result、completed_at、tokens_used
  - 失败时记录：error_message、status=FAILED
  - 所有记录绑定 project_id、user_id、script_work_id（章节生成额外绑定 script_chapter_id）
  - 记录必须如实写入，无论用户后续是否使用或修改生成结果

- **FR-4**: 提示词模板管理
  - 为每种生成类型定义默认提示词模板：OUTLINE、CHARACTERS、CHAPTER_OUTLINE、CHAPTER_CONTENT
  - 前端可查看当前使用的提示词模板（点击按钮旁的「查看提示词」或 hover 显示）
  - 提示词模板存储在后端（第一版可存在配置文件或数据库）
  - 接口预留：获取提示词模板、更新提示词模板（第一版先实现获取，更新预留）

- **FR-5**: 前端交互体验
  - 点击生成按钮时禁用按钮，显示「生成中...」状态
  - 生成成功后自动填充到编辑器，按钮恢复可用
  - 生成失败时显示错误提示，按钮恢复可用
  - 按钮状态根据依赖条件动态启用/禁用：
    - 生成大纲按钮：只要选择了作品即可用
    - 生成人设按钮：选择了作品且 outline 不为空才可用
    - 生成分集按钮：选择了作品且 outline 和 characters 都不为空才可用
  - 生成章节大纲/内容：选中章节且所属作品有 outline/characters 才可用

## Non-Functional Requirements
- **NFR-1**: API 调用可靠性
  - 调用超时处理（使用现有 MiniMaxClient 的超时机制）
  - 错误信息需前端友好展示，同时详细信息记录到数据库
  - 即使 API 调用失败，也必须先创建记录再更新为失败状态

- **NFR-2**: 用户数据隔离
  - 所有生成记录必须绑定 user_id
  - 查询和操作必须验证当前用户权限
  - 不能跨用户、跨项目访问生成记录

- **NFR-3**: 前端响应性
  - 生成过程中不阻塞整个页面
  - 状态提示清晰（toast 通知 + 按钮状态）
  - 编辑器可在生成过程中继续编辑（但生成结果会覆盖当前编辑框内容）

## Constraints
- **Technical**:
  - 必须使用现有的 `MiniMaxClient` 调用 MiniMax API
  - 必须使用现有的 `generation_records` 表结构，可扩展但不能破坏现有字段
  - 前端修改必须与现有 `script_works.js` 模块风格一致
  - 第一版采用同步调用方式，不引入新的异步任务框架

- **Business**:
  - 用户必须明确感知 AI 生成结果是草稿，不是最终版本
  - 所有 AI 调用必须可追溯、可审计
  - 提示词模板必须可配置（至少支持硬编码配置，未来支持数据库配置）

## Assumptions
- 用户已登录并选择了项目和脚本作品才能使用 AI 生成功能
- MiniMax API 配置正确（API_KEY、GroupId 等已在 settings 中配置）
- 第一版不需要流式输出，只需等待完整响应后一次性填充
- 提示词模板第一版可硬编码在后端配置中，后续迁移到数据库
- 用户理解并接受：AI 生成内容需要人工审核和修改

## Acceptance Criteria

### AC-1: 递进式生成 - 大纲生成
- **Given**: 用户已登录，选择了项目和脚本作品
- **When**: 用户点击「自动生成大纲」按钮
- **Then**: 
  1. 系统调用 MiniMax 文本生成接口
  2. 创建一条 generation_type=OUTLINE 的 generation_record
  3. 生成成功后将结果填充到 outline-editor 编辑框
  4. 不自动调用保存接口
- **Verification**: `programmatic`
- **Notes**: 验证 generation_record 被创建，编辑器内容被填充，数据库 outline 字段未变更

### AC-2: 递进式生成 - 人物设定（依赖大纲）
- **Given**: 
  1. 用户已登录，选择了项目和脚本作品
  2. 该作品的 outline 字段已有保存的内容（非空）
- **When**: 用户点击「自动生成人物设定」按钮
- **Then**: 
  1. 系统读取已保存的 outline 作为上下文
  2. 调用 MiniMax 接口时将 outline 包含在 prompt 中
  3. 创建 generation_type=CHARACTERS 的 generation_record
  4. 生成成功后将结果填充到 characters-editor 编辑框
  5. 不自动调用保存接口
- **Verification**: `programmatic`
- **Notes**: 验证请求中包含 outline 内容，generation_record 的 prompt 字段有记录

### AC-3: 递进式生成 - 依赖检查（没有大纲时无法生成人设）
- **Given**: 用户已登录，选择了项目和脚本作品，但该作品 outline 为空
- **When**: 查看「自动生成人物设定」按钮状态
- **Then**: 按钮处于禁用状态（disabled），hover 时提示「请先保存大纲」
- **Verification**: `human-judgment`

### AC-4: 草稿模式 - 用户可修改生成内容后保存
- **Given**: 
  1. 用户已点击「自动生成大纲」，AI 结果已填充到编辑框
  2. 用户在编辑框中手动修改了部分内容
- **When**: 用户点击「保存大纲」按钮
- **Then**: 
  1. 数据库保存的是用户修改后的最终内容
  2. generation_record 中的 result 仍是 AI 原始返回内容（用于对比）
- **Verification**: `programmatic`
- **Notes**: 验证数据库 outline 字段与编辑框最终内容一致，与 generation_record.result 可能不同

### AC-5: 调用记录入库 - 成功场景
- **Given**: 用户点击任意 AI 生成按钮，API 调用成功
- **When**: 生成完成后
- **Then**: generation_records 表中存在一条记录，包含：
  - generation_type 正确
  - status = COMPLETED
  - prompt 字段记录实际发送的提示词
  - result 字段记录 AI 返回的完整内容
  - model_used 记录使用的模型名称
  - tokens_used 记录 token 消耗（如 API 返回）
  - 绑定了正确的 project_id、user_id、script_work_id
- **Verification**: `programmatic`

### AC-6: 调用记录入库 - 失败场景
- **Given**: 用户点击 AI 生成按钮，API 调用失败（网络错误、超时、API 返回错误等）
- **When**: 错误发生后
- **Then**: 
  1. generation_records 表中仍存在记录
  2. status = FAILED
  3. error_message 字段记录详细错误信息
  4. 前端显示友好的错误提示
- **Verification**: `programmatic`
- **Notes**: 即使调用失败，记录也必须先创建再更新状态

### AC-7: 提示词模板可查看
- **Given**: 用户在脚本工坊页面
- **When**: 用户点击「查看提示词」或 hover 在生成按钮上
- **Then**: 可以看到当前该生成类型使用的完整提示词模板
- **Verification**: `human-judgment`
- **Notes**: 第一版只需可查看，无需编辑功能

### AC-8: 前端交互 - 生成中状态
- **Given**: 用户点击 AI 生成按钮
- **When**: API 调用进行中
- **Then**: 
  1. 按钮变为禁用状态，显示「生成中...」
  2. 页面其他操作不受阻塞
  3. 显示 loading 状态提示
- **Verification**: `human-judgment`

### AC-9: 章节级生成 - 生成本集大纲
- **Given**: 
  1. 用户已选择脚本作品，该作品有 outline 和 characters
  2. 用户已选中某个章节
- **When**: 用户点击「生成本集大纲」按钮
- **Then**: 
  1. 系统读取所属作品的 outline 和 characters 作为上下文
  2. 调用 MiniMax 接口
  3. 创建 generation_type=CHAPTER_OUTLINE 的记录，绑定 script_chapter_id
  4. 结果填充到 chapter-outline-editor 编辑框
  5. 不自动保存
- **Verification**: `programmatic`

## Open Questions
- [ ] 提示词模板第一版是硬编码在配置文件中，还是直接存入数据库？（当前倾向：配置文件 + 预留数据库表）
- [ ] 是否需要在前端展示历史生成记录列表？（第一版可以不做，仅后端记录）
- [ ] 生成失败时是否需要重试按钮？（第一版可以不做，用户可再次点击生成）
- [ ] 是否需要支持流式输出到编辑器？（第一版采用同步等待完整响应）
