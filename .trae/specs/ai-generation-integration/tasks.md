# AI文本生成功能接入 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建提示词模板配置与管理
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 在 `core/settings.py` 或新建 `core/prompts.py` 中定义默认提示词模板
  - 为每种生成类型定义模板：OUTLINE、CHARACTERS、CHAPTER_OUTLINE、CHAPTER_CONTENT
  - 模板支持占位符替换（如 {outline}, {characters}, {chapter_title}）
  - 创建获取提示词模板的工具函数，支持根据类型获取
  - 预留未来从数据库加载的扩展点
- **Acceptance Criteria Addressed**: [AC-7, FR-4]
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证能根据 generation_type 获取对应的提示词模板
  - `programmatic` TR-1.2: 验证模板中的占位符能被正确替换
  - `human-judgement` TR-1.3: 检查模板定义位置合理，易于未来扩展
- **Notes**: 提示词内容参考 docs/ 目录下的提示词设计文档

---

## [x] Task 2: 创建后端 AI 生成 API 接口（大纲生成）
- **Priority**: P0
- **Depends On**: [Task 1]
- **Description**: 
  - 在 `api/script_work.py` 中新增 `POST /api/script-works/{script_work_id}/generate-outline` 接口
  - 接口逻辑：
    1. 校验用户权限和 script_work_id
    2. 创建 generation_record（status=PENDING）
    3. 调用 MiniMaxClient.chat() 生成文本
    4. 更新 generation_record（status=COMPLETED/FAILED，记录 result/error_message/tokens_used/model_used）
    5. 返回生成的文本内容（供前端填充编辑器）
  - 注意：**不调用任何保存接口**，只返回生成内容
- **Acceptance Criteria Addressed**: [AC-1, AC-5, AC-6, FR-1, FR-2, FR-3]
- **Test Requirements**:
  - `programmatic` TR-2.1: 接口返回 200 且包含生成的文本内容
  - `programmatic` TR-2.2: generation_records 表中创建了记录，status=COMPLETED
  - `programmatic` TR-2.3: 验证 script_works.outline 字段未被修改（证明没有自动保存）
  - `programmatic` TR-2.4: API 调用失败时，generation_record 状态为 FAILED 且记录 error_message

---

## [x] Task 3: 创建后端 AI 生成 API 接口（人物设定生成，依赖大纲）
- **Priority**: P0
- **Depends On**: [Task 2]
- **Description**: 
  - 新增 `POST /api/script-works/{script_work_id}/generate-characters` 接口
  - 接口逻辑：
    1. 校验用户权限和 script_work_id
    2. **检查 outline 是否为空**，为空则返回 400 错误（提示"请先保存大纲"）
    3. 创建 generation_record
    4. 构建提示词时，**将已保存的 outline 作为上下文**注入模板
    5. 调用 MiniMax API 生成
    6. 更新 generation_record
    7. 返回生成内容（不保存）
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-5, AC-6, FR-1, FR-2, FR-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: outline 为空时接口返回 400，提示信息正确
  - `programmatic` TR-3.2: outline 存在时，提示词中包含 outline 内容（可通过 generation_record.prompt 验证）
  - `programmatic` TR-3.3: 生成成功后 script_works.characters 字段未被修改
  - `programmatic` TR-3.4: generation_record 的 generation_type=CHARACTERS

---

## [x] Task 4: 创建后端 AI 生成 API 接口（章节级生成）
- **Priority**: P0
- **Depends On**: [Task 3]
- **Description**: 
  - 新增 `POST /api/script-works/{script_work_id}/chapters/{chapter_id}/generate-outline` 接口（生成本集大纲）
  - 新增 `POST /api/script-works/{script_work_id}/chapters/{chapter_id}/generate-content` 接口（生成本集内容）
  - 接口逻辑：
    1. 校验用户权限、script_work_id、chapter_id 归属关系
    2. 检查所属作品的 outline 是否存在（章节生成依赖作品大纲）
    3. 创建 generation_record，绑定 script_chapter_id
    4. 构建提示词时注入：作品 outline、作品 characters、当前章节信息
    5. 调用 MiniMax API
    6. 更新 generation_record
    7. 返回生成内容（不保存）
- **Acceptance Criteria Addressed**: [AC-9, AC-5, AC-6, FR-1, FR-2, FR-3]
- **Test Requirements**:
  - `programmatic` TR-4.1: 生成记录正确绑定 script_chapter_id
  - `programmatic` TR-4.2: 提示词中包含所属作品的 outline 和 characters
  - `programmatic` TR-4.3: 章节的 outline/content 字段未被自动修改
  - `programmatic` TR-4.4: generation_type 分别为 CHAPTER_OUTLINE 和 CHAPTER_CONTENT

---

## [x] Task 5: 新增获取提示词模板的 API 接口
- **Priority**: P1
- **Depends On**: [Task 1]
- **Description**: 
  - 新增 `GET /api/prompts?type={generation_type}` 接口
  - 返回指定类型的提示词模板（原始模板，未替换占位符）
  - 支持的类型：outline, characters, chapter_outline, chapter_content
  - 用于前端展示"查看提示词"功能
- **Acceptance Criteria Addressed**: [AC-7, FR-4]
- **Test Requirements**:
  - `programmatic` TR-5.1: 接口返回对应类型的提示词模板
  - `programmatic` TR-5.2: 无效类型返回 400 错误
  - `human-judgement` TR-5.3: 接口路径设计合理，符合 REST 风格

---

## [x] Task 6: 前端脚本模块 - 绑定大纲生成按钮事件
- **Priority**: P0
- **Depends On**: [Task 2]
- **Description**: 
  - 在 `static/js/modules/script_works.js` 中新增 `generateOutline()` 方法
  - 在 `bindEvents()` 中绑定 `generate-outline-btn` 按钮的 click 事件
  - 实现逻辑：
    1. 检查 currentScriptWorkId 是否存在
    2. 禁用按钮，修改文本为「生成中...」
    3. 显示 loading 提示
    4. 调用 `POST /api/script-works/{id}/generate-outline` 接口
    5. 成功时：将返回的内容填充到 `outline-editor` 编辑框，显示成功 toast
    6. 失败时：显示错误 toast
    7. 无论成功失败：恢复按钮状态
- **Acceptance Criteria Addressed**: [AC-1, AC-4, AC-8, FR-2, FR-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 点击按钮后进入生成中状态，按钮禁用
  - `human-judgement` TR-6.2: 生成成功后编辑框内容被填充，按钮恢复
  - `human-judgement` TR-6.3: 编辑框内容可手动修改（证明是草稿模式）
  - `programmatic` TR-6.4: 验证后端 generation_record 已创建

---

## [x] Task 7: 前端脚本模块 - 绑定人物设定生成按钮（含依赖检查）
- **Priority**: P0
- **Depends On**: [Task 3, Task 6]
- **Description**: 
  - 新增 `generateCharacters()` 方法
  - 绑定 `generate-characters-btn` 按钮事件
  - **实现按钮状态动态管理**：
    - 在 `loadScriptWorkDetail()`、`saveOutline()` 成功后检查 outline 是否为空
    - outline 为空时：禁用 `generate-characters-btn`，添加 tooltip「请先保存大纲」
    - outline 存在时：启用 `generate-characters-btn`
  - 生成逻辑同 Task 6，结果填充到 `characters-editor`
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-4, AC-8, FR-1, FR-2, FR-5]
- **Test Requirements**:
  - `human-judgement` TR-7.1: outline 为空时按钮禁用，有 tooltip 提示
  - `human-judgement` TR-7.2: 保存大纲后按钮自动变为可用状态
  - `human-judgement` TR-7.3: 生成内容填充到人物设定编辑框，可编辑

---

## [x] Task 8: 前端脚本模块 - 绑定章节生成按钮
- **Priority**: P0
- **Depends On**: [Task 4, Task 7]
- **Description**: 
  - 新增 `generateChapterOutline()` 和 `generateChapterContent()` 方法
  - 绑定 `generate-chapter-outline-btn` 和 `generate-chapter-content-btn` 按钮事件
  - 实现按钮状态动态管理：
    - 选中章节时检查所属作品的 outline 是否存在
    - outline 为空时禁用章节生成按钮
  - 生成结果分别填充到 `chapter-outline-editor` 和 `chapter-content-editor`
- **Acceptance Criteria Addressed**: [AC-9, AC-8, FR-1, FR-2, FR-5]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 未选中章节时章节生成按钮状态正确
  - `human-judgement` TR-8.2: 选中章节且作品有大纲时按钮可用
  - `human-judgement` TR-8.3: 生成本集大纲后内容填充到对应编辑框

---

## [x] Task 9: 前端脚本模块 - 实现提示词查看功能
- **Priority**: P1
- **Depends On**: [Task 5, Task 8]
- **Description**: 
  - 为每个生成按钮添加「查看提示词」功能
  - 方案选择：hover 显示 tooltip 或点击按钮旁的图标弹出模态框
  - 调用 `GET /api/prompts` 接口获取模板内容并展示
  - 在 HTML 中为每个生成按钮添加对应的提示词查看入口
- **Acceptance Criteria Addressed**: [AC-7, FR-4, FR-5]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 用户可以查看每种生成类型的提示词模板
  - `human-judgement` TR-9.2: 提示词展示清晰，格式易读

---

## [x] Task 10: 前端脚本模块 - 启用大纲生成按钮
- **Priority**: P0
- **Depends On**: [Task 6]
- **Description**: 
  - 修改 HTML 模板中 `generate-outline-btn` 的 `disabled` 属性（或在 JS 中动态启用）
  - 大纲生成按钮无需前置依赖，选择作品后即可用
  - 在 `loadScriptWorkDetail()` 中确认按钮状态设置正确
- **Acceptance Criteria Addressed**: [AC-1, FR-5]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 选择脚本作品后，大纲生成按钮变为可用
  - `human-judgement` TR-10.2: 未选择作品时按钮禁用

---

## [x] Task 11: 集成测试 - 端到端验证生成+保存流程
- **Priority**: P0
- **Depends On**: [Task 6, Task 7, Task 8]
- **Description**: 
  - 测试完整流程：生成大纲 -> 修改大纲 -> 保存大纲 -> 生成人设 -> 修改人设 -> 保存人设
  - 验证：
    1. AI 生成结果只填充到编辑框
    2. 用户修改后的内容与 AI 原始结果可以不同
    3. 保存时落库的是用户修改后的最终版本
    4. generation_record 中记录的是 AI 原始结果（用于对比）
- **Acceptance Criteria Addressed**: [AC-4, AC-5, FR-2, FR-3]
- **Test Requirements**:
  - `programmatic` TR-11.1: 数据库 outline 字段值 == 用户修改后的值
  - `programmatic` TR-11.2: generation_record.result 可能与数据库值不同（证明草稿模式）
  - `programmatic` TR-11.3: 两次生成（大纲、人设）都有对应的 generation_record

---

## [x] Task 12: 错误场景测试
- **Priority**: P1
- **Depends On**: [Task 11]
- **Description**: 
  - 测试各种错误场景：
    1. MiniMax API 密钥无效
    2. 网络超时
    3. API 返回错误（如 quota 不足）
  - 验证：
    1. 前端显示友好错误提示
    2. generation_record 仍被创建，status=FAILED，error_message 有详细信息
    3. 按钮状态恢复正常，用户可重试
- **Acceptance Criteria Addressed**: [AC-6, FR-3, FR-5]
- **Test Requirements**:
  - `programmatic` TR-12.1: 失败场景下 generation_record 存在且状态正确
  - `human-judgement` TR-12.2: 前端错误提示友好，不暴露敏感信息
  - `human-judgement` TR-12.3: 失败后按钮恢复可用，用户可再次点击生成
