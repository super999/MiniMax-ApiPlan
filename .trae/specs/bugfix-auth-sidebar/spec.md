# 登录凭据持久化与侧边栏切换修复 - Product Requirement Document

## Overview
- **Summary**: 修复两个现有系统BUG：1) JWT Secret Key 动态生成导致服务重启后登录凭据失效；2) 侧边栏缩进后无法展开的交互问题。
- **Purpose**: 提升用户体验，确保系统重启后用户无需重复登录，同时修复侧边栏导航的可用性问题。
- **Target Users**: 所有使用 MiniMax 生产力平台的用户，尤其是需要重启服务的开发/运维人员。

## Goals
- **Goal 1**: 实现登录凭据跨服务重启的持久性，JWT Token 在有效期内可正常使用
- **Goal 2**: 修复侧边栏缩进/展开交互，确保用户可以在两种状态间自由切换

## Non-Goals (Out of Scope)
- 不实现"记住我"功能（前端已经在 localStorage 存储 token）
- 不修改登录/注册的业务逻辑
- 不实现新的导航功能，仅修复现有切换功能
- 不添加 JWT 刷新令牌（refresh token）机制

## Background & Context

### 问题 1：服务重启后登录凭据丢失
当前实现在 `core/settings.py:92`：
```python
secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
```

- JWT_SECRET_KEY 每次服务启动时通过 `secrets.token_urlsafe(32)` 动态生成
- 用户登录时获得的 JWT Token 是用当时的 secret_key 签名的
- 服务重启后，新的 secret_key 无法验证旧的 Token
- 结果：虽然前端 localStorage 中仍保存着 Token，但后端验证失败，用户需要重新登录

### 问题 2：侧边栏缩进后无法展开
当前实现分析：
- 侧边栏切换按钮 ID: `sidebar-toggle`，位于 `sidebar-header` 内
- 点击逻辑：`NavigationModule.toggleSidebar()` 切换 `collapsed` CSS 类
- 折叠后侧边栏宽度：`--sidebar-collapsed-width: 72px`
- `sidebar-header` 的 padding: `16px 20px`（左右各 20px）

问题分析：
1. 折叠后可用空间：72px - 20px*2 = 32px
2. Logo 图标（1.5rem ≈ 24px）+ 切换按钮（20px SVG）在 `space-between` 布局下可能显示异常
3. 按钮图标没有变化（始终是汉堡菜单），用户可能不知道点击哪里展开

## Functional Requirements

### FR-1: JWT Secret Key 配置持久化
- 支持从环境变量 `JWT_SECRET_KEY` 读取固定的 secret key
- 如果环境变量未设置，应使用一个固定的默认值（而非每次动态生成）
- 保持现有的 JWT 有效期配置（默认 24 小时）

### FR-2: 侧边栏折叠状态交互修复
- 确保侧边栏切换按钮在折叠状态下始终可见且可点击
- （可选）改进按钮图标：折叠时显示"展开"图标，展开时显示"折叠"图标
- 保持侧边栏折叠状态的 localStorage 持久化（如果还没有实现）

## Non-Functional Requirements

### NFR-1: 安全性
- 如果使用默认 secret key，应确保足够的长度和复杂度
- 生产环境应建议用户设置自定义的 `JWT_SECRET_KEY` 环境变量

### NFR-2: 兼容性
- 修复后不应影响现有的登录/验证逻辑
- Token 格式保持不变，现有已登录用户在服务重启后应继续有效

### NFR-3: 可用性
- 侧边栏切换交互应直观，用户能够理解如何在两种状态间切换

## Constraints

- **Technical**: 
  - 使用现有的 `python-jose` 库进行 JWT 处理
  - 使用 Pydantic Settings 进行配置管理
  - 前端使用原生 JavaScript，不引入新框架

- **Business**:
  - 最小化改动，避免引入新的依赖或配置文件

## Assumptions

- 用户知道如何设置环境变量或修改 `.env` 文件（生产环境）
- 现有前端 localStorage 中存储 Token 的逻辑无需修改
- 侧边栏切换事件绑定逻辑正确，只是 CSS 或可见性问题

## Acceptance Criteria

### AC-1: 服务重启后登录状态保持
- **Given**: 用户已成功登录系统，获得有效的 JWT Token
- **When**: 重启 uvicorn 或 Python 服务
- **Then**: 用户刷新页面后，无需重新登录即可进入工作台
- **Verification**: `programmatic`
- **Notes**: 验证 Token 在服务重启前后都能通过 `/api/auth/me` 端点验证

### AC-2: 环境变量 Secret Key 优先
- **Given**: 环境变量 `JWT_SECRET_KEY` 已设置为自定义值
- **When**: 服务启动并生成/验证 Token
- **Then**: 应使用环境变量中的值作为 secret key，而非默认值
- **Verification**: `programmatic`

### AC-3: 侧边栏可正常折叠
- **Given**: 用户处于工作台页面，侧边栏处于展开状态
- **When**: 点击侧边栏头部的切换按钮
- **Then**: 侧边栏应折叠为仅显示图标的状态
- **Verification**: `programmatic` + `human-judgment`

### AC-4: 侧边栏可正常展开
- **Given**: 侧边栏处于折叠状态
- **When**: 用户点击切换按钮
- **Then**: 侧边栏应恢复为展开状态
- **Verification**: `programmatic` + `human-judgment`

### AC-5: 切换按钮始终可见
- **Given**: 侧边栏处于折叠或展开状态
- **When**: 观察侧边栏头部
- **Then**: 切换按钮应始终可见且可交互
- **Verification**: `human-judgment`

## Open Questions

- [ ] 生产环境是否需要强制要求设置 `JWT_SECRET_KEY`，还是可以使用默认值？
- [ ] 侧边栏状态（折叠/展开）是否需要在页面刷新后保持？（当前可能没有持久化）
