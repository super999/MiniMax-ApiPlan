# MiniMax 生产力平台 更新日志

## [2026-04-17] - 脚本工坊底座搭建

### 新增功能

1. **数据模型设计**
   - **ScriptWork（脚本作品）**：包含 title、description、outline、characters、status 等字段
   - **ScriptChapter（脚本章节）**：包含 title、chapter_number、outline、content、status 等字段
   - **ScriptVersion（脚本版本）**：用于版本历史管理，支持作品级和章节级版本
   - **GenerationRecord（生成记录）**：记录 AI 生成过程，包含 prompt、result、status、tokens_used 等

2. **状态管理**
   - 脚本作品状态：`draft`（草稿）、`generating`（生成中）、`completed`（已完成）、`failed`（失败）
   - 脚本章节状态：`draft`（草稿）、`generating`（生成中）、`completed`（已完成）、`failed`（失败）
   - 生成记录状态：`pending`（待处理）、`processing`（处理中）、`completed`（已完成）、`failed`（失败）、`cancelled`（已取消）

3. **CRUD 操作层**
   - **CRUDScriptWork**：支持按项目查询、带章节详情查询、大纲/角色设定更新
   - **CRUDScriptChapter**：支持按作品查询、按章节号查询、自动生成章节号、内容/大纲更新
   - **CRUDScriptVersion**：支持按作品/章节查询、获取最新版本、获取最大版本号
   - **CRUDGenerationRecord**：支持按作品/章节查询、获取待处理记录、状态更新

4. **API 端点设计**
   - **作品管理**：
     - `POST /api/script-works` - 创建脚本作品
     - `GET /api/script-works` - 获取项目下的所有脚本作品（含章节数量统计）
     - `GET /api/script-works/{id}` - 获取作品详情（含完整章节列表）
     - `PUT /api/script-works/{id}` - 更新作品基本信息
     - `PUT /api/script-works/{id}/outline` - 保存作品大纲
     - `PUT /api/script-works/{id}/characters` - 保存角色设定
     - `DELETE /api/script-works/{id}` - 删除作品（软删除）
   
   - **章节管理**：
     - `POST /api/script-works/{work_id}/chapters` - 创建章节（支持自动生成章节号）
     - `GET /api/script-works/{work_id}/chapters/{chapter_id}` - 获取章节详情
     - `PUT /api/script-works/{work_id}/chapters/{chapter_id}` - 更新章节内容
     - `DELETE /api/script-works/{work_id}/chapters/{chapter_id}` - 删除章节（软删除）

5. **权限校验机制**
   - 所有 API 端点都需要登录认证（`get_current_user`）
   - 操作前校验项目归属权限
   - 操作前校验作品归属权限
   - 操作前校验章节归属权限
   - 所有 CRUD 操作继承自 `CRUDUserIsolatedBase`，确保用户隔离

6. **编辑器友好的数据结构**
   - **作品列表**：包含章节数量统计，适合左侧列表展示
   - **作品详情**：包含完整章节列表，适合右侧编辑区导航
   - **章节详情**：包含完整内容和状态，适合编辑器渲染

### 数据隔离保证

1. **每条数据都带 `project_id` 和 `user_id`**
   - `script_works` 表：`project_id`、`user_id`
   - `script_chapters` 表：`project_id`、`user_id`、`script_work_id`
   - `script_versions` 表：`project_id`、`user_id`、`script_work_id`、`script_chapter_id`
   - `generation_records` 表：`project_id`、`user_id`、`script_work_id`、`script_chapter_id`

2. **查询时强制过滤**
   - 所有查询都通过 `user_id` 过滤
   - 所有查询都通过 `project_id` 过滤（当涉及项目时）
   - 所有查询都通过 `is_deleted = False` 过滤（软删除支持）

3. **修改时权限校验**
   - 创建时自动注入当前用户 `user_id`
   - 更新时校验 `db_obj.user_id == user_id`
   - 删除时同时校验 `id` 和 `user_id`

### 新增文件

- **db/models/script_work.py**：脚本作品数据模型
- **db/models/script_chapter.py**：脚本章节数据模型
- **db/models/script_version.py**：脚本版本数据模型
- **db/models/generation_record.py**：生成记录数据模型
- **db/crud/script_work.py**：脚本作品 CRUD 操作
- **db/crud/script_chapter.py**：脚本章节 CRUD 操作
- **db/crud/script_version.py**：脚本版本 CRUD 操作
- **db/crud/generation_record.py**：生成记录 CRUD 操作
- **api/script_work.py**：脚本工坊 API 端点

### 修改文件

- **main.py**：导入并注册 `script_work_router` 路由

---

## [2026-04-17] - 控制台首页功能补齐

### 新增功能

1. **首页核心模块**
   - 添加了当前登录用户信息显示（欢迎卡片）
   - 添加了我的项目列表区域
   - 添加了快捷操作区（新建项目、脚本工坊、视觉工坊、配音实验室）
   - 添加了最近活动占位区
   - 添加了系统状态/欢迎说明

2. **项目优先设计**
   - 首页突出显示"我的项目"区域
   - 提供了多个"创建项目"入口：
     - 快捷操作区的"新建项目"按钮
     - 项目区域标题旁的"新建项目"按钮
     - 空状态中的"创建第一个项目"按钮

3. **空状态设计**
   - 当用户没有项目时，显示明确的空状态引导
   - 包含图标、标题、描述和"创建第一个项目"按钮
   - 避免了大面积空白

4. **数据对接**
   - 对接了现有的用户鉴权接口（/api/auth/me）
   - 对接了项目接口（/api/projects）
   - 真实拉取当前用户信息和项目列表
   - 不再使用静态假数据

5. **快捷入口**
   - 添加了"新建项目"按钮（打开创建项目模态框）
   - 添加了"进入脚本工坊"按钮（跳转到脚本工坊页面）
   - 添加了"进入视觉工坊"按钮（跳转到视觉工坊页面）
   - 添加了"进入配音实验室"按钮（跳转到配音实验室页面）

6. **数据隔离**
   - 所有API调用都使用当前登录用户的token
   - 后端API已经实现了用户隔离
   - 用户只能看到自己的项目和自己的信息

7. **创建项目功能**
   - 添加了创建项目的模态框
   - 支持输入项目名称、项目描述（可选）、项目状态
   - 对接了后端的创建项目API（POST /api/projects）
   - 项目创建成功后自动刷新项目列表

### 文件修改

- **templates/index.html**:
  - 添加了快捷操作区域（quick-actions-section）
  - 添加了我的项目区域（projects-section），包含空状态和项目列表
  - 添加了最近活动区域（recent-activity-section）
  - 添加了创建项目的模态框（create-project-modal）

- **static/css/style.css**:
  - 添加了快捷操作按钮样式（.quick-actions-section, .quick-action-btn）
  - 添加了项目区域样式（.projects-section, .section-header, .projects-grid, .project-card）
  - 添加了空状态样式（.empty-state）
  - 添加了最近活动样式（.recent-activity-section, .activity-placeholder, .activity-item）
  - 优化了表单控件样式（.form-group input, .form-group textarea, .form-group select）

- **static/js/app.js**:
  - 添加了 `loadUserProjects()` 函数：加载用户项目列表
  - 添加了 `renderProjects()` 函数：渲染项目列表
  - 添加了 `createProjectCard()` 函数：创建项目卡片
  - 添加了 `updateProjectStats()` 函数：更新项目统计数据
  - 添加了 `handleDeleteProject()` 函数：处理删除项目
  - 添加了 `openCreateProjectModal()` 函数：打开创建项目模态框
  - 添加了 `closeCreateProjectModal()` 函数：关闭创建项目模态框
  - 添加了 `clearCreateProjectForm()` 函数：清空创建项目表单
  - 添加了 `showCreateProjectError()` 函数：显示创建项目错误
  - 添加了 `handleCreateProject()` 函数：处理创建项目提交
  - 添加了 `bindDashboardEvents()` 函数：绑定首页事件
  - 修改了 `showWorkspace()` 函数：添加了 `loadUserProjects()` 调用
  - 修改了 `bindWorkspaceEvents()` 函数：添加了 `bindDashboardEvents()` 调用

---

## [2026-04-17] - 表单控件样式优化

### 问题修复

1. **创建新项目模态框控件样式不一致**
   - 项目描述文本域（textarea）没有应用与输入框相同的样式
   - 项目状态下拉框（select）没有应用与输入框相同的样式

### 优化内容

1. **统一表单控件样式**
   - 将 `.form-group input` 样式扩展为同时支持 `input`、`textarea`、`select` 元素
   - 为 `textarea` 添加了专门的样式：
     - 垂直可调整大小（resize: vertical）
     - 最小高度 120px
     - 行高 1.5 提高可读性
   - 为 `select` 添加了专门的样式：
     - 自定义下拉箭头（使用 SVG 图标）
     - 移除默认浏览器样式（appearance: none）
     - 右侧内边距为图标留出空间
   - 统一了焦点状态样式：
     - 蓝色边框（var(--primary-color)）
     - 蓝色光晕效果（box-shadow）
   - 统一了占位符文本样式：
     - 使用灰色（var(--text-muted)）

2. **样式一致性**
   - 所有表单控件现在使用相同的：
     - 圆角（var(--radius-md)）
     - 边框样式（1px solid var(--border-color)）
     - 内边距（12px 16px）
     - 字体大小（0.875rem）
     - 过渡动画（border-color 和 box-shadow）

### 文件修改

- **static/css/style.css**:
  - 修改了 `.form-group input` 为 `.form-group input, .form-group textarea, .form-group select`
  - 添加了 `.form-group textarea` 专门样式
  - 添加了 `.form-group select` 专门样式（包含自定义下拉箭头）
  - 修改了 `.form-group input:focus` 为同时支持 `textarea` 和 `select`
  - 添加了 `.form-group input::placeholder, .form-group textarea::placeholder` 样式

### 效果对比

**优化前：**
- 项目名称输入框：有圆角、边框、聚焦效果
- 项目描述文本域：默认浏览器样式，无圆角、无聚焦效果
- 项目状态下拉框：默认浏览器样式，无圆角、无聚焦效果

**优化后：**
- 项目名称输入框：保持原有样式
- 项目描述文本域：与输入框相同的圆角、边框、聚焦效果
- 项目状态下拉框：与输入框相同的圆角、边框、聚焦效果，带有自定义下拉箭头

---

## 更新日志格式说明

本文档记录了 MiniMax 生产力平台的所有重要修改。每次修改都应该：

1. **添加日期**：格式为 `[YYYY-MM-DD]`
2. **添加标题**：简要描述修改的内容
3. **分类描述**：
   - **新增功能**：新添加的功能
   - **问题修复**：修复的 bug 或问题
   - **优化内容**：对现有功能的改进
4. **文件修改**：列出所有修改的文件及其修改内容

### 版本号说明

由于项目仍在早期开发阶段，暂时使用日期作为版本标识。未来可能会引入语义化版本号（SemVer）。

### 提交规范

每次提交代码前，请确保：
1. 更新此 changelog.md 文件
2. 清晰描述修改的内容和原因
3. 列出所有修改的文件
