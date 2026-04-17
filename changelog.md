# MiniMax 生产力平台 更新日志

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
