# MiniMax API 配置修复计划

## 问题诊断

### 当前问题
1. **默认 URL 已废弃**：代码中默认 `https://api.minimax.chat/v1/text/chatcompletion_v2` 已无法使用
2. **正确 URL**：`https://api.minimaxi.com/v1/text/chatcompletion_v2`（用户配置）
3. **默认模型错误**：代码中默认 `abab6.5s-chat`，正确的是 `MiniMax-M2.7`
4. **超时时间太短**：默认 60s 对于长文本生成可能不够
5. **环境变量读取问题**：用户有 `.env` 文件但可能未被正确读取

### 日志证据
```
请求 URL: https://api.minimaxi.com/v1/text/chatcompletion_v2
超时时间配置: 60.0s
实际耗时: 60252.64ms
```

## 修复内容

### 1. 更新默认配置 (`core/settings.py`)

**修改 `MiniMaxSettings` 默认值：**
- `base_url`: `https://api.minimax.chat/...` → `https://api.minimaxi.com/...`
- `default_model`: `abab6.5s-chat` → `MiniMax-M2.7`
- `timeout`: `120.0`（已改，但需确保生效）

### 2. 验证环境变量读取

**检查点：**
- pydantic-settings 的 `env_file` 配置
- `.env` 文件位置（应该在项目根目录）
- 环境变量名称是否正确（`MINIMAX_` 前缀）

### 3. 增加调试日志

**在 `settings.py` 或启动时添加：**
- 打印实际加载的配置值（脱敏 API Key）
- 确认环境变量是否被正确读取

### 4. 更新 `.env.example`

**同步更新示例配置文件：**
- 更新 `MINIMAX_BASE_URL`
- 更新 `MINIMAX_DEFAULT_MODEL`

## 涉及文件

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `core/settings.py` | 修改 | 更新默认配置值 |
| `.env.example` | 修改 | 同步更新示例配置 |
| `clients/minimax_client.py` | 可能修改 | 增加配置加载时的日志 |

## 测试验证

### 修复后测试步骤
1. 重启服务
2. 查看启动日志，确认配置是否正确加载
3. 测试 AI 生成大纲功能
4. 检查日志中的：
   - `base_url` 是否为 `api.minimaxi.com`
   - `model` 是否为 `MiniMax-M2.7`
   - `timeout` 是否为 `120.0s`

### 预期结果
```
MiniMaxClient 配置: 
base_url=https://api.minimaxi.com/v1/text/chatcompletion_v2, 
default_model=MiniMax-M2.7, 
timeout=120.0s, 
...
```

## 风险处理

### 风险1：用户 `.env` 文件位置不对
**处理**：确认 `.env` 文件是否在项目根目录（与 `main.py` 同级）

### 风险2：环境变量名称不一致
**处理**：确认变量前缀是 `MINIMAX_` 而不是其他

### 风险3：pydantic-settings 版本问题
**处理**：检查 `pydantic-settings` 是否正确安装和配置

## 执行顺序

1. 检查 `.env` 文件位置和内容
2. 更新 `core/settings.py` 默认值
3. 更新 `.env.example`
4. 启动服务验证配置加载
5. 测试 AI 生成功能
