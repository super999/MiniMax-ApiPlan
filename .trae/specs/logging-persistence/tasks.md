# 日志持久化功能 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 在 settings.py 中添加 LogSettings 配置类
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 在 `core/settings.py` 中添加 `LogSettings` 配置类
  - 配置项包括：`level`（日志级别，默认 "DEBUG"）、`file_enabled`（是否启用文件输出，默认 True）、`file_path`（日志文件路径，默认 "logs/app.log"）、`rotation_days`（保留天数，默认 7）
  - 集成到现有的 `Settings` 类中
  - 使用 `pydantic-settings` 的 `env_prefix="LOG_"` 机制
- **Acceptance Criteria Addressed**: [AC-3, AC-5]
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证 `get_settings().log.level` 默认为 "DEBUG"
  - `programmatic` TR-1.2: 验证 `settings.log.file_enabled` 默认为 True
  - `programmatic` TR-1.3: 验证可以通过 `LOG_LEVEL` 环境变量修改日志级别

## [x] Task 2: 修改 logger.py 支持文件输出和配置读取
- **Priority**: P0
- **Depends On**: [Task 1]
- **Description**: 
  - 修改 `core/logger.py` 的 `setup_logger()` 函数
  - 从 `settings.log` 读取配置而非硬编码
  - 添加 `TimedRotatingFileHandler` 实现日志文件按天轮转
  - 日志文件路径：`logs/app.log`，轮转后命名为 `app.log.YYYY-MM-DD`
  - 日志格式与现有保持一致：`%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - 确保 `console_handler` 保留，日志同时输出到控制台和文件
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-6]
- **Test Requirements**:
  - `programmatic` TR-2.1: 验证 `setup_logger()` 返回的 logger 同时有 StreamHandler 和 FileHandler（当 file_enabled=True）
  - `programmatic` TR-2.2: 验证日志级别默认为 DEBUG
  - `programmatic` TR-2.3: 验证 `get_logger()` 能正确获取已配置的 logger
  - `human-judgement` TR-2.4: 检查代码可读性，日志初始化逻辑清晰

## [x] Task 3: 更新 main.py 确保日志正确初始化
- **Priority**: P0
- **Depends On**: [Task 2]
- **Description**: 
  - 检查 `main.py` 中现有的日志初始化逻辑
  - 确保在 `setup_logger()` 调用之前，settings 已可用
  - 添加一些 DEBUG 级别的日志输出用于测试（如在 lifespan 中）
  - 确保现有日志调用不受影响
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-6]
- **Test Requirements**:
  - `programmatic` TR-3.1: 验证 `main.py` 启动时能正确初始化日志系统
  - `programmatic` TR-3.2: 验证 DEBUG 级别的日志能够被输出

## [ ] Task 4: 添加日志功能单元测试
- **Priority**: P1
- **Depends On**: [Task 1, Task 2]
- **Description**: 
  - 在 `tests/unit/` 目录下添加 `test_logger.py` 测试文件
  - 测试日志级别配置功能
  - 测试日志文件输出功能（可使用临时目录）
  - 测试 `get_logger()` 功能
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-4.1: 单元测试全部通过
  - `programmatic` TR-4.2: 测试覆盖日志文件写入功能
  - `programmatic` TR-4.3: 测试覆盖日志级别过滤功能

## [x] Task 5: 运行程序验证日志功能（端到端验证）
- **Priority**: P0
- **Depends On**: [Task 1, Task 2, Task 3]
- **Description**: 
  - 实际运行 `main.py` 启动应用
  - 检查 `logs/` 目录是否自动创建
  - 检查日志文件是否生成
  - 验证日志文件中包含 DEBUG 级别的日志
  - 访问 `/health` 或其他接口触发更多日志输出
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-5.1: `logs/app.log` 文件存在
  - `programmatic` TR-5.2: 日志文件中包含 "DEBUG" 级别的日志条目
  - `programmatic` TR-5.3: 控制台也同时输出相同的日志
