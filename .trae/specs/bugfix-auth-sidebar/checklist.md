# 登录凭据持久化与侧边栏切换修复 - Verification Checklist

## JWT Secret Key 持久化验证

- [x] **Checkpoint 1**: 代码审查 - 确认 `core/settings.py` 中 `JWTSettings.secret_key` 不再使用 `secrets.token_urlsafe(32)` 动态生成
  - ✅ 已修改为固定值: `"minimax_api_plan_default_jwt_secret_key_2024_secure_abc123xyz"`
- [ ] **Checkpoint 2**: 单元测试 - 验证使用相同 secret key 签名的 token 可以被正确解码
- [ ] **Checkpoint 3**: 集成测试 - 启动服务，登录获取 token，重启服务，使用同一 token 调用 `/api/auth/me` 应返回 200
- [x] **Checkpoint 4**: 配置测试 - `public_env.data` 已添加 `JWT_SECRET_KEY` 配置项，支持环境变量覆盖

## 侧边栏切换功能验证

- [x] **Checkpoint 5**: 展开状态 - 侧边栏完全展开时，所有导航菜单文本可见，切换按钮可见且可点击
- [x] **Checkpoint 6**: 折叠功能 - 点击切换按钮后，侧边栏成功折叠为仅显示图标状态，宽度变为 72px
- [x] **Checkpoint 7**: 折叠状态可见性 - 已移除 `.sidebar.collapsed .sidebar-toggle { display: none; }`，按钮在折叠状态下可见
- [x] **Checkpoint 8**: 展开功能 - 折叠状态下点击切换按钮，侧边栏成功恢复为展开状态
- [x] **Checkpoint 9**: 完整交互循环 - 连续执行"展开->折叠->展开->折叠"，每次操作都正常工作
  - ✅ 已调整折叠状态下 `sidebar-header` 的 padding 为 `16px 8px`，确保布局正常

## 回归测试

- [ ] **Checkpoint 10**: 登录流程 - 新用户注册并登录流程正常工作
- [ ] **Checkpoint 11**: Token 有效期 - Token 在超过 `access_token_expire_minutes` 后应失效
- [ ] **Checkpoint 12**: 无效 Token - 使用被篡改的 Token 调用 `/api/auth/me` 应返回 401
- [ ] **Checkpoint 13**: 移动端响应 - 在窄屏幕（<900px）下，侧边栏的 mobile 模式仍正常工作

## 最终验收

- [ ] **Checkpoint 14**: 端到端场景 - 用户登录 -> 导航侧边栏折叠/展开 -> 重启服务 -> 刷新页面仍保持登录 -> 侧边栏功能正常

---

## 已完成的修改汇总

### 修改的文件：

1. **`core/settings.py:92`**
   - 修改前：`secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))`
   - 修改后：`secret_key: str = "minimax_api_plan_default_jwt_secret_key_2024_secure_abc123xyz"`
   - 说明：从动态生成改为固定默认值，确保服务重启后密钥一致

2. **`public_env.data` (新增 31-38 行)**
   - 新增 JWT 配置区块，包含 `JWT_SECRET_KEY`、`JWT_ALGORITHM`、`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
   - 添加注释说明生产环境建议使用自定义密钥

3. **`static/css/components/_buttons.css` (移除 155-157 行)**
   - 移除了 `.sidebar.collapsed .sidebar-toggle { display: none; }`
   - 说明：此规则导致折叠状态下切换按钮被隐藏，是 BUG 的根本原因

4. **`static/css/layout/_sidebar.css` (新增 19-21 行)**
   - 新增 `.sidebar.collapsed .sidebar-header { padding: 16px 8px; }`
   - 说明：调整折叠状态下的内边距，从 `16px 20px` 改为 `16px 8px`，确保 72px 宽度内能容纳 logo-icon 和切换按钮
