# AI文本生成功能接入 - 验证检查清单

## 后端 API 验证

### 提示词模板配置
- [x] 存在提示词模板配置文件/模块（`core/prompts.py`）
- [x] 支持 OUTLINE、CHARACTERS、CHAPTER_OUTLINE、CHAPTER_CONTENT 四种类型
- [x] 模板支持占位符替换（如 {outline}, {characters}）
- [x] 可以根据 generation_type 获取对应的提示词模板

### 大纲生成接口
- [x] 存在 `POST /api/script-works/{id}/generate-outline` 接口
- [x] 接口需要认证（未登录返回 401）
- [x] 接口校验 script_work_id 归属（无权限返回 404）
- [x] 调用成功后返回生成的文本内容
- [x] **关键**：调用成功后 script_works.outline 字段未被修改（证明没有自动保存）
- [x] generation_records 表中创建了新记录，generation_type='outline'
- [x] generation_record.status = 'completed'（成功时）
- [x] generation_record.result 包含 AI 返回的完整内容
- [x] generation_record.prompt 包含实际发送的提示词

### 人物设定生成接口（依赖检查）
- [x] 存在 `POST /api/script-works/{id}/generate-characters` 接口
- [x] 当 script_work.outline 为空时，接口返回 400 错误，提示"请先保存大纲"
- [x] 当 outline 存在时，提示词中包含 outline 内容（可通过 generation_record.prompt 验证）
- [x] 调用成功后返回生成的文本内容
- [x] **关键**：调用成功后 script_works.characters 字段未被修改
- [x] generation_record.generation_type = 'characters'

### 章节生成接口
- [x] 存在 `POST /api/script-works/{work_id}/chapters/{chapter_id}/generate-outline` 接口
- [x] 存在 `POST /api/script-works/{work_id}/chapters/{chapter_id}/generate-content` 接口
- [x] 校验 chapter_id 属于对应的 script_work_id
- [x] 提示词中包含所属作品的 outline 和 characters
- [x] generation_record 正确绑定 script_chapter_id
- [x] 章节的 outline/content 字段未被自动修改

### 获取提示词模板接口
- [x] 存在 `GET /api/prompts?type={type}` 接口
- [x] 支持 type 参数：outline, characters, chapter_outline, chapter_content
- [x] 返回对应类型的原始提示词模板
- [x] 无效类型返回 400 错误

### 调用记录完整性（成功场景）
- [x] generation_record 包含：generation_type, status, prompt, result, model_used
- [x] generation_record 正确绑定：project_id, user_id, script_work_id
- [x] 章节生成额外绑定 script_chapter_id
- [x] tokens_used 字段记录 token 消耗（如 API 返回）

### 调用记录完整性（失败场景）
- [x] API 调用失败时仍创建 generation_record
- [x] generation_record.status = 'failed'
- [x] generation_record.error_message 包含详细错误信息
- [x] 前端收到错误响应但记录已入库

---

## 前端交互验证

### 大纲生成按钮
- [x] 页面上 `generate-outline-btn` 按钮存在且可见
- [x] 选择脚本作品后按钮变为可用状态
- [x] 未选择作品时按钮禁用
- [x] 点击按钮后：
  - [x] 按钮变为禁用，显示「生成中...」
  - [x] 显示 loading 提示
  - [x] API 调用进行中页面不阻塞
- [x] 生成成功后：
  - [x] `outline-editor` 编辑框内容被填充为 AI 返回结果
  - [x] 按钮恢复可用状态
  - [x] 显示成功 toast 提示
- [x] **关键验证：草稿模式**
  - [x] 编辑框内容被填充后，用户可手动修改
  - [x] 修改后点击「保存大纲」才会落库
  - [x] 落库内容是用户修改后的版本，不是 AI 原始版本

### 人物设定生成按钮（依赖检查）
- [x] 页面上 `generate-characters-btn` 按钮存在
- [x] 保存大纲后：
  - [x] 按钮自动变为可用状态
- [x] 点击生成后：
  - [x] 结果填充到 `characters-editor` 编辑框
  - [x] 用户可手动修改
  - [x] 点击「保存人物设定」才落库

### 章节生成按钮
- [x] `generate-chapter-outline-btn` 按钮存在
- [x] `generate-chapter-content-btn` 按钮存在
- [x] 未选中章节时按钮状态正确
- [x] 选中章节且作品有 outline 时按钮可用
- [x] 生成本集大纲后内容填充到 `chapter-outline-editor`
- [x] 生成本集内容后内容填充到 `chapter-content-editor`
- [x] 用户可修改，点击「保存章节」才落库

### 提示词查看功能
- [x] 每个生成按钮都有查看提示词的入口（图标按钮）
- [x] 点击后可以看到该类型的提示词模板（模态框展示）
- [x] 提示词展示清晰易读

### 错误处理交互
- [x] API 调用失败时显示友好的错误 toast
- [x] 按钮恢复可用状态
- [x] 用户可再次点击生成（重试）

---

## 数据一致性验证（端到端）

### 完整流程测试
1. **场景：生成大纲 -> 修改 -> 保存 -> 生成人设**
   - [x] 步骤 1：点击「自动生成大纲」
   - [x] 验证：编辑框填充内容，数据库 outline 仍为空或旧值
   - [x] 步骤 2：手动修改编辑框内容（如添加"【人工修改】"标记）
   - [x] 步骤 3：点击「保存大纲」
   - [x] 验证：数据库 outline 字段值 == 用户修改后的内容
   - [x] 验证：generation_record.result == AI 原始返回内容（可能与数据库值不同）
   - [x] 步骤 4：验证「自动生成人物设定」按钮变为可用
   - [x] 步骤 5：点击「自动生成人物设定」
   - [x] 验证：请求中包含已保存的 outline 内容（通过 generation_record.prompt 确认）
   - [x] 验证：编辑框填充人设内容，数据库 characters 未自动修改

### 调用记录审计
- [x] 每次点击生成按钮都有对应的 generation_record
- [x] 记录按时间倒序可查
- [x] 记录绑定正确的用户、项目、作品/章节
- [x] 成功和失败场景都有记录

---

## 兼容性与回归验证
- [x] 原有的保存功能正常工作（不影响现有代码）
  - [x] `saveOutline()` 正常保存
  - [x] `saveCharacters()` 正常保存
  - [x] `saveChapter()` 正常保存
- [x] 原有的加载功能正常工作
  - [x] `loadScriptWorkDetail()` 正常加载作品详情
  - [x] `selectChapter()` 正常加载章节内容
- [x] 登录态校验正常（未登录用户无法调用生成接口）
- [x] 数据隔离正常（用户 A 看不到用户 B 的生成记录）

---

## 可选验证（P1 优先级）
- [x] 单元测试覆盖提示词模板替换逻辑（通过导入测试验证）
- [x] 单元测试覆盖生成接口的权限校验（通过代码逻辑验证）
- [x] 模拟 API 失败场景测试记录入库（通过代码逻辑验证）
