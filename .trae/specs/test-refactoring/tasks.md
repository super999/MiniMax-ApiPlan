# 测试框架改造 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 安装 pytest 并配置项目
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 安装 pytest 库
  - 更新 `requirements.txt` 添加 pytest 依赖
  - 创建 pytest 配置文件（`pytest.ini` 或 `pyproject.toml`）
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-1.1: 运行 `pytest --version` 成功，显示 pytest 版本
  - `programmatic` TR-1.2: `requirements.txt` 中包含 pytest 依赖
  - `programmatic` TR-1.3: 项目根目录存在 pytest 配置文件
- **Notes**: 建议使用 `pyproject.toml` 作为配置文件，更现代

## [x] Task 2: 创建规范的测试目录结构
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 在项目根目录创建 `tests/` 目录
  - 创建 `tests/unit/` 子目录（用于单元测试）
  - 创建 `tests/integration/` 子目录（用于集成测试）
  - 创建 `tests/conftest.py` 文件（用于共享 fixtures）
  - 创建 `tests/__init__.py` 文件（标识为包）
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: 存在 `tests/` 目录
  - `programmatic` TR-2.2: 存在 `tests/unit/` 子目录
  - `programmatic` TR-2.3: 存在 `tests/integration/` 子目录
  - `programmatic` TR-2.4: 存在 `tests/conftest.py` 文件
  - `programmatic` TR-2.5: 存在 `tests/__init__.py` 文件
- **Notes**: 目录结构应清晰，便于后续扩展

## [x] Task 3: 重构配置测试文件（test_config.py）
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 将 `test_config.py` 重构为 pytest 测试
  - 新文件路径：`tests/unit/test_settings.py`
  - 使用 pytest 的 assert 语句（替代自定义的 assert 和 print）
  - 移除手动的路径操作（pytest 会自动处理）
  - 使用 pytest 的 fixtures 管理配置加载
  - 按配置模块拆分测试函数（如 `test_app_config`, `test_minimax_config`, `test_database_config` 等）
- **Acceptance Criteria Addressed**: [AC-3, AC-8]
- **Test Requirements**:
  - `programmatic` TR-3.1: 存在 `tests/unit/test_settings.py` 文件
  - `programmatic` TR-3.2: 运行 `pytest tests/unit/test_settings.py -v` 所有测试通过
  - `programmatic` TR-3.3: 测试文件遵循 pytest 命名规范（函数以 `test_` 开头）
  - `programmatic` TR-3.4: 测试文件使用 pytest 的 assert 而非自定义打印输出
- **Notes**: 保持原有的测试逻辑不变，仅改造测试框架

## [x] Task 4: 创建共享 fixtures 和辅助函数
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 在 `tests/conftest.py` 中创建共享 fixtures：
    - `client`: httpx 测试客户端（用于 API 测试）
    - `test_user_data`: 生成测试用户数据的 fixture
    - `auth_headers`: 认证请求头 fixture
    - 其他可能需要的共享 fixtures
  - 创建 `tests/integration/__init__.py`
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: `tests/conftest.py` 包含共享 fixtures
  - `programmatic` TR-4.2: fixtures 可以被测试文件正确导入和使用
- **Notes**: fixtures 应使用 pytest 的 `@pytest.fixture` 装饰器

## [x] Task 5: 重构用户认证测试（test_runner.py 中的用户注册和登录部分）
- **Priority**: P1
- **Depends On**: Task 4
- **Description**: 
  - 创建 `tests/integration/test_auth.py` 文件
  - 包含以下测试用例：
    - 用户注册测试（TC-REG-001 到 TC-REG-004）
    - 用户登录测试（TC-LOG-001 到 TC-LOG-005）
  - 使用 pytest 的 fixtures 管理测试用户状态
  - 使用 pytest 的 markers 对测试进行分组（如 `@pytest.mark.auth`）
  - 移除自定义的 TestResult 类，使用 pytest 的原生 assert
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: 存在 `tests/integration/test_auth.py` 文件
  - `programmatic` TR-5.2: 测试文件包含所有原有的用户认证测试用例
  - `programmatic` TR-5.3: 使用 pytest 的 markers 进行分组
  - `programmatic` TR-5.4: 运行 `pytest tests/integration/test_auth.py -v --collect-only` 可以发现所有测试用例
- **Notes**: 集成测试需要运行的服务器，测试时需要确保服务已启动

## [x] Task 6: 重构项目管理测试（test_runner.py 中的项目创建和删除部分）
- **Priority**: P1
- **Depends On**: Task 5
- **Description**: 
  - 创建 `tests/integration/test_projects.py` 文件
  - 包含以下测试用例：
    - 项目创建测试（TC-PRJ-001 到 TC-PRJ-004）
    - 项目删除测试（TC-DEL-001 到 TC-DEL-003）
  - 使用 pytest 的 fixtures 管理测试项目状态
  - 使用 pytest 的 markers 对测试进行分组（如 `@pytest.mark.projects`）
  - 测试之间的依赖关系使用 fixtures 或 pytest 的 `depends` 插件处理
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: 存在 `tests/integration/test_projects.py` 文件
  - `programmatic` TR-6.2: 测试文件包含所有原有的项目管理测试用例
  - `programmatic` TR-6.3: 使用 pytest 的 markers 进行分组
  - `programmatic` TR-6.4: 运行 `pytest tests/integration/test_projects.py -v --collect-only` 可以发现所有测试用例
- **Notes**: 考虑使用 `pytest-dependency` 或 fixtures 处理测试依赖

## [x] Task 7: 重构脚本作品测试（test_runner.py 中的脚本大纲部分）
- **Priority**: P1
- **Depends On**: Task 6
- **Description**: 
  - 创建 `tests/integration/test_script_works.py` 文件
  - 包含以下测试用例：
    - 脚本作品测试（TC-SCR-001 到 TC-SCR-007）
  - 使用 pytest 的 fixtures 管理测试脚本作品状态
  - 使用 pytest 的 markers 对测试进行分组（如 `@pytest.mark.script_works`）
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-7.1: 存在 `tests/integration/test_script_works.py` 文件
  - `programmatic` TR-7.2: 测试文件包含所有原有的脚本作品测试用例
  - `programmatic` TR-7.3: 使用 pytest 的 markers 进行分组
  - `programmatic` TR-7.4: 运行 `pytest tests/integration/test_script_works.py -v --collect-only` 可以发现所有测试用例
- **Notes**: 保持原有的测试逻辑不变

## [x] Task 8: 配置 VSCode 支持 pytest
- **Priority**: P2
- **Depends On**: Task 3, Task 5, Task 6, Task 7
- **Description**: 
  - 更新 `.vscode/settings.json` 添加 pytest 配置
  - 配置项包括：
    - `"python.testing.pytestEnabled": true`
    - `"python.testing.unittestEnabled": false`
    - `"python.testing.pytestArgs": ["-v"]`
  - 确保 VSCode 可以识别测试文件
- **Acceptance Criteria Addressed**: [AC-6, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-8.1: VSCode 设置中 pytest 已启用
  - `human-judgement` TR-8.2: VSCode 测试面板可以显示所有测试用例
  - `human-judgement` TR-8.3: 可以在 VSCode 中点击运行单个测试用例
- **Notes**: 需要开发者在 VSCode 中验证

## [x] Task 9: 验证并清理旧测试文件
- **Priority**: P2
- **Depends On**: Task 8
- **Description**: 
  - 运行所有单元测试验证功能正常
  - 验证新测试文件覆盖了所有原有测试用例
  - 删除旧的 `test_config.py` 和 `test_runner.py` 文件
  - 更新 `.gitignore` 如果需要
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-9.1: 运行 `pytest tests/unit/ -v` 所有测试通过
  - `programmatic` TR-9.2: 旧的 `test_config.py` 和 `test_runner.py` 已被删除
  - `programmatic` TR-9.3: 运行 `pytest tests/ --collect-only` 发现的测试数量不少于原有测试数量
- **Notes**: 删除前确保所有功能已迁移并验证通过

## Task Dependencies Summary
```
Task 1 (安装 pytest)
    ↓
Task 2 (创建目录结构)
    ↓
Task 3 (重构配置测试) ──→ Task 4 (创建 fixtures)
                                    ↓
                              Task 5 (用户认证测试)
                                    ↓
                              Task 6 (项目管理测试)
                                    ↓
                              Task 7 (脚本作品测试)
                                    ↓
                              Task 8 (配置 VSCode)
                                    ↓
                              Task 9 (验证并清理)
```

## Priority Summary
- **P0 (Critical)**: Task 1, Task 2, Task 3, Task 4
- **P1 (Important)**: Task 5, Task 6, Task 7
- **P2 (Nice-to-have)**: Task 8, Task 9
