# 日志持久化功能 - Product Requirement Document

## Overview
- **Summary**: 为 MiniMaxApiPlan 项目实现日志持久化功能，使日志不仅输出到控制台，还能保存到文件中，并支持日志级别等配置。
- **Purpose**: 解决当前日志仅打印在控制台、无法持久化的问题，方便开发调试和问题排查。
- **Target Users**: 项目开发者、运维人员、需要排查问题的人员

## Goals
- 日志能够同时输出到控制台和文件
- 日志级别支持配置，默认为 DEBUG 级别
- 日志文件按日期或大小轮转，避免单个文件过大
- 配置项与现有 Settings 系统集成

## Non-Goals (Out of Scope)
- 不实现日志收集上报到外部系统（如 ELK）
- 不修改现有业务代码的日志打印逻辑
- 不实现日志可视化 Web 界面

## Background & Context
- 现有日志系统 `core/logger.py` 仅配置了 `StreamHandler`，日志只输出到控制台
- 现有配置系统 `core/settings.py` 使用 `pydantic-settings`，已有 AppSettings、MiniMaxSettings 等配置类
- 日志级别当前硬编码为 `logging.INFO`
- 项目使用 FastAPI 框架，`main.py` 中调用 `setup_logger()` 初始化日志

## Functional Requirements
- **FR-1**: 日志必须持久化保存到文件中
  - 日志同时输出到控制台和文件
  - 日志文件路径可配置
- **FR-2**: 日志级别支持配置
  - 默认为 DEBUG 级别
  - 可通过环境变量或配置文件修改
- **FR-3**: 日志文件轮转
  - 支持按日期轮转（每天一个日志文件）
  - 支持保留指定天数的日志文件
- **FR-4**: 配置与现有系统集成
  - 在 `core/settings.py` 中添加 LogSettings 配置类
  - 使用现有的 `env_prefix` 和 `env_file` 机制

## Non-Functional Requirements
- **NFR-1**: 日志格式保持统一
  - 控制台和文件使用相同的日志格式：`%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - 时间格式：`%Y-%m-%d %H:%M:%S`
- **NFR-2**: 性能影响最小化
  - 使用标准库 `logging.handlers` 中的 TimedRotatingFileHandler
  - 不引入额外的外部依赖
- **NFR-3**: 兼容性
  - 现有调用 `setup_logger()` 和 `get_logger()` 的代码无需修改即可正常工作

## Constraints
- **Technical**:
  - 只能使用 Python 标准库 `logging` 模块，不引入新的日志库（如 loguru）
  - 必须与现有的 `pydantic-settings` 配置系统集成
  - 日志轮转使用标准库的 `TimedRotatingFileHandler`
- **Business**:
  - 默认日志级别为 DEBUG，方便开发调试
  - 日志文件应保存在项目目录下的 `logs/` 文件夹中

## Assumptions
- 日志文件不需要压缩归档
- 日志轮转按天进行即可满足需求
- 保留 7 天的日志文件是合理的默认值
- 现有的日志调用方式（使用 `logger.info()`, `logger.debug()` 等）保持不变

## Acceptance Criteria

### AC-1: 日志输出到文件
- **Given**: 程序正常运行
- **When**: 程序打印任意日志
- **Then**: 日志同时出现在控制台和日志文件中
- **Verification**: `programmatic`
- **Notes**: 运行程序后检查 `logs/` 目录下是否有日志文件生成

### AC-2: 日志级别默认为 DEBUG
- **Given**: 未配置任何日志级别相关的环境变量
- **When**: 程序启动并打印 DEBUG 级别的日志
- **Then**: DEBUG 级别日志能够正常输出到控制台和文件
- **Verification**: `programmatic`
- **Notes**: 需确认日志文件中包含 DEBUG 级别的日志条目

### AC-3: 日志级别可配置
- **Given**: 设置环境变量 `LOG_LEVEL=WARNING`
- **When**: 程序打印 INFO 和 WARNING 级别的日志
- **Then**: 只有 WARNING 及以上级别的日志被输出
- **Verification**: `programmatic`

### AC-4: 日志文件轮转
- **Given**: 日志系统配置为按天轮转
- **When**: 跨天时程序继续运行
- **Then**: 新的日志写入新日期命名的日志文件
- **Verification**: `human-judgment`
- **Notes**: 可通过修改系统时间或模拟来验证

### AC-5: 配置系统集成
- **Given**: LogSettings 已添加到 Settings
- **When**: 调用 `get_settings()`
- **Then**: 可以通过 `settings.log.level` 等属性访问日志配置
- **Verification**: `programmatic`

### AC-6: 现有日志代码兼容
- **Given**: 现有代码使用 `get_logger(__name__)` 获取 logger
- **When**: 调用 `logger.debug()`, `logger.info()` 等方法
- **Then**: 日志正常工作，行为与修改前一致（除了新增文件输出）
- **Verification**: `programmatic`

## Open Questions
- [ ] 日志文件是否需要按模块分文件？（当前假设全部日志写入一个文件）
- [ ] 是否需要支持按文件大小轮转而非仅按日期？（当前假设按天即可）
