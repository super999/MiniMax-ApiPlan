# 登录凭据持久化与侧边栏切换修复 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 修复 JWT Secret Key 动态生成问题
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 修改 `core/settings.py` 中的 `JWTSettings` 类
  - 将 `secret_key` 从 `default_factory=lambda: secrets.token_urlsafe(32)` 改为固定默认值
  - 确保可以通过环境变量 `JWT_SECRET_KEY` 覆盖默认值
  - 在 `public_env.data` 中添加 `JWT_SECRET_KEY` 配置项（可选注释说明）
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证使用相同 secret key 签名的 token 在服务重启后仍可通过 `decode_access_token` 解码
  - `programmatic` TR-1.2: 验证设置环境变量 `JWT_SECRET_KEY` 后，settings 会使用该值而非默认值
  - `programmatic` TR-1.3: 调用 `/api/auth/login` 获取 token，重启服务后调用 `/api/auth/me` 应返回 200
- **Notes**: 
  - 默认 secret key 应使用足够长且随机的字符串（建议 32+ 字符）
  - 可以在日志或注释中建议生产环境设置自定义密钥

---

## [x] Task 2: 调查侧边栏切换按钮在折叠状态下的可见性问题
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 仔细审查 `_sidebar.css` 中 `sidebar.collapsed` 状态下所有元素的样式
  - 检查 `sidebar-header` 在折叠状态下的空间计算
  - 可能的问题：
    1. `sidebar-header` 的 `padding: 16px 20px` 在折叠后占用太多空间
    2. `sidebar-toggle` 按钮没有显式的可见性保证
    3. `space-between` 布局在窄宽度下的行为问题
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `human-judgement` TR-2.1: 观察折叠状态下 `sidebar-toggle` 按钮是否可见
  - `human-judgement` TR-2.2: 点击折叠状态下的切换按钮，验证是否触发展开
- **Notes**: 此任务为调查任务，根据结果可能需要修改 Task 3 的实现方案

---

## [x] Task 3: 修复侧边栏折叠后无法展开的问题
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 根据 Task 2 的调查结果，实施修复方案
  - 可能的修复方向：
    - **方案 A**: 调整 `sidebar.collapsed` 状态下 `sidebar-header` 的 padding（减小左右 padding）
    - **方案 B**: 为 `sidebar.collapsed .sidebar-toggle` 添加显式样式，确保可见
    - **方案 C**: 重新组织 `sidebar-header` 的布局结构，确保按钮始终可访问
    - **方案 D**: 在折叠状态下改变按钮位置（例如放在侧边栏右侧边缘）
  - （可选）改进按钮图标：使用不同的图标表示"折叠"和"展开"状态
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 验证点击切换按钮后，`.sidebar` 元素的 `collapsed` 类正确切换
  - `programmatic` TR-3.2: 验证折叠状态下 `sidebar-toggle` 元素的 `display` 不是 `none`
  - `human-judgement` TR-3.3: 折叠和展开状态下，按钮均清晰可见且可点击
  - `human-judgement` TR-3.4: 完整交互流程：展开 -> 点击折叠 -> 折叠状态 -> 点击展开 -> 展开状态
- **Notes**: 优先选择改动最小的方案（方案 A 或 B）

---

## [ ] Task 4: 添加侧边栏状态持久化（可选增强）
- **Priority**: P2
- **Depends On**: Task 3
- **Description**: 
  - 在 `NavigationModule.toggleSidebar()` 中添加 localStorage 持久化
  - 在页面加载时（`initializeApp` 或 `bindWorkspaceEvents`）读取保存的状态
  - 如果保存为折叠状态，则在初始化时自动应用
- **Acceptance Criteria Addressed**: (增强功能，非原始 BUG 修复)
- **Test Requirements**:
  - `programmatic` TR-4.1: 折叠侧边栏后，localStorage 中应有保存的状态
  - `programmatic` TR-4.2: 刷新页面后，侧边栏状态应与刷新前一致
- **Notes**: 此为增强功能，如果时间允许可以实现，但不是必须修复的 BUG

---

## 任务依赖关系图

```
Task 1 (JWT Secret) ─────┐
                          │
Task 2 (侧边栏调查) ──────┼───> Task 4 (状态持久化, P2)
       │                  │
       └──> Task 3 (侧边栏修复)
```

- Task 1 和 Task 2 可以并行执行
- Task 3 依赖 Task 2 的调查结果
- Task 4 是可选增强，依赖 Task 3 完成
