# 测试框架改造 - Product Requirement Document

## Overview
- **Summary**: 将现有的非标准测试文件（`test_config.py` 和 `test_runner.py`）改造为使用 pytest 标准库的规范测试框架，包括创建规范的测试目录结构、拆分测试文件、配置 VSCode 快捷运行等。
- **Purpose**: 建立符合 Python 生态标准的测试框架，提高测试代码的可维护性和可扩展性，同时确保开发者可以在 VSCode 中快捷运行和调试测试。
- **Target Users**: 项目开发者、测试人员

## Goals
- [G-1] 创建规范的测试目录结构（`tests/` 目录）
- [G-2] 使用 pytest 标准库替代自定义测试框架
- [G-3] 按模块拆分测试文件，便于扩展和分组
- [G-4] 配置 VSCode 以支持 pytest 快捷运行
- [G-5] 确保所有测试用例可以正常运行

## Non-Goals (Out of Scope)
- 不修改测试逻辑和测试用例的核心内容
- 不添加新的测试用例（仅改造现有测试）
- 不修改项目的业务逻辑代码
- 不修改项目的依赖版本（除了添加 pytest）

## Background & Context
- 现有测试文件位于项目根目录：
  - `test_config.py`：测试配置加载功能，使用自定义的 assert 和 print 输出
  - `test_runner.py`：测试 API 功能，包含大量测试用例，使用自定义的 TestResult 类
- 项目使用的技术栈：
  - FastAPI
  - SQLAlchemy
  - httpx
  - pydantic
- 现有测试的问题：
  1. 测试文件位置不规范（应该在 `tests/` 目录）
  2. 使用自定义测试框架，不兼容 pytest 生态
  3. 所有测试用例放在一个文件中，难以维护和扩展
  4. 无法在 VSCode 中快捷运行单个测试用例
  5. 没有使用 pytest 的 fixture、markers 等高级功能

## Functional Requirements
- **FR-1**: 创建规范的测试目录结构
  - 在项目根目录创建 `tests/` 目录
  - 根据测试类型创建子目录（如 `unit/` 单元测试，`integration/` 集成测试）
- **FR-2**: 安装并配置 pytest
  - 在 `requirements.txt` 中添加 pytest 依赖
  - 创建 `pytest.ini` 或 `pyproject.toml` 配置文件
- **FR-3**: 重构 `test_config.py` 为 pytest 测试
  - 将配置测试放在 `tests/unit/` 目录
  - 使用 pytest 的 assert 语句
  - 使用 pytest 的输出替代自定义 print
- **FR-4**: 重构 `test_runner.py` 为 pytest 测试
  - 按功能模块拆分测试文件
  - 每个模块一个测试文件（如 `test_auth.py`, `test_projects.py`, `test_script_works.py`）
  - 使用 pytest 的 fixtures 管理测试状态（如测试用户、测试项目等）
  - 使用 pytest 的 markers 对测试进行分组
- **FR-5**: 配置 VSCode 支持 pytest
  - 更新 `.vscode/settings.json` 添加 pytest 配置
  - 确保 VSCode 可以识别测试文件
  - 确保可以在 VSCode 中运行和调试单个测试用例

## Non-Functional Requirements
- **NFR-1**: 测试文件命名规范
  - 测试文件以 `test_` 开头
  - 测试函数以 `test_` 开头
  - 测试类以 `Test` 开头
- **NFR-2**: 测试目录结构清晰
  - 单元测试和集成测试分离
  - 按功能模块组织测试文件
- **NFR-3**: VSCode 集成
  - 可以通过 VSCode 测试面板运行测试
  - 可以在测试文件中点击运行单个测试

## Constraints
- **Technical**:
  - 必须使用 pytest 作为测试框架
  - 测试文件必须遵循 pytest 命名规范
  - 不能修改现有测试的业务逻辑
- **Business**:
  - 现有测试用例必须全部通过
  - 开发者学习成本低（使用标准 pytest）

## Dependencies
- pytest
- httpx（已存在）
- 项目的核心模块（core, api, db 等）

## Assumptions
- 开发者熟悉 pytest 或可以快速学习
- 现有的测试用例逻辑是正确的
- VSCode 已安装 Python 扩展
- 项目的 Python 环境已正确配置

## Acceptance Criteria

### AC-1: 测试目录结构规范
- **Given**: 项目根目录
- **When**: 检查目录结构
- **Then**: 存在 `tests/` 目录，且包含合理的子目录结构（如 `unit/` 和 `integration/`）
- **Verification**: `programmatic`
- **Notes**: 可以通过检查文件路径验证

### AC-2: pytest 已正确配置
- **Given**: 项目环境
- **When**: 运行 `pytest --version`
- **Then**: pytest 已安装且可以正常运行
- **Verification**: `programmatic`
- **Notes**: 检查输出包含 pytest 版本信息

### AC-3: 配置测试通过
- **Given**: 重构后的配置测试文件
- **When**: 运行 `pytest tests/unit/test_settings.py -v`
- **Then**: 所有配置测试用例通过
- **Verification**: `programmatic`
- **Notes**: 检查输出中所有测试标记为 PASSED

### AC-4: API 测试文件拆分正确
- **Given**: 重构后的测试目录
- **When**: 检查 `tests/integration/` 目录
- **Then**: 包含按功能模块拆分的测试文件（如 `test_auth.py`, `test_projects.py`, `test_script_works.py`）
- **Verification**: `programmatic`
- **Notes**: 检查文件是否存在

### AC-5: 所有测试用例可以运行
- **Given**: 完整的测试框架
- **When**: 运行 `pytest` 命令
- **Then**: 所有测试用例可以被发现并执行（不考虑是否通过，因为集成测试需要运行服务）
- **Verification**: `programmatic`
- **Notes**: 检查 pytest 发现的测试数量

### AC-6: VSCode 可以识别测试
- **Given**: VSCode 开发环境
- **When**: 打开测试面板或测试文件
- **Then**: VSCode 可以识别所有测试文件和测试用例
- **Verification**: `human-judgment`
- **Notes**: 需要开发者在 VSCode 中验证

### AC-7: 可以在 VSCode 中运行单个测试
- **Given**: VSCode 开发环境
- **When**: 点击测试文件中的运行按钮或测试面板中的测试
- **Then**: 可以运行单个测试用例或测试文件
- **Verification**: `human-judgment`
- **Notes**: 需要开发者在 VSCode 中验证

### AC-8: 旧测试文件可以删除
- **Given**: 重构后的测试框架
- **When**: 验证所有新测试可以正常工作后
- **Then**: 可以安全删除旧的 `test_config.py` 和 `test_runner.py`
- **Verification**: `programmatic`
- **Notes**: 删除后运行新测试确认功能正常

## Open Questions
- [ ] 集成测试是否需要单独的测试配置（如测试数据库）？
- [ ] 是否需要添加 pytest 的插件（如 pytest-asyncio 用于异步测试）？
- [ ] 测试报告的生成方式是否需要调整？
