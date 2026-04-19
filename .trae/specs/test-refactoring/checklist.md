# 测试框架改造 - Verification Checklist

## 安装与配置检查
- [x] pytest 已正确安装（运行 `pytest --version` 验证）
- [x] `requirements.txt` 已添加 pytest 依赖
- [x] 项目根目录存在 pytest 配置文件（`pyproject.toml` 或 `pytest.ini`）

## 目录结构检查
- [x] 项目根目录存在 `tests/` 目录
- [x] 存在 `tests/unit/` 子目录（单元测试）
- [x] 存在 `tests/integration/` 子目录（集成测试）
- [x] 存在 `tests/__init__.py` 文件
- [x] 存在 `tests/conftest.py` 文件（共享 fixtures）

## 单元测试检查（配置测试）
- [x] 存在 `tests/unit/test_settings.py` 文件
- [x] 测试文件遵循 pytest 命名规范（函数以 `test_` 开头）
- [x] 测试使用 pytest 的 assert 语句而非自定义打印输出
- [x] 运行 `pytest tests/unit/test_settings.py -v` 所有测试通过
- [x] 测试覆盖了所有原有配置测试用例（APP、MINIMAX、DATABASE、EVALUATION、DSN）

## 共享 Fixtures 检查
- [x] `tests/conftest.py` 包含必要的共享 fixtures
- [x] 至少包含：httpx 客户端 fixture、测试用户数据 fixture、认证请求头 fixture
- [x] fixtures 使用 pytest 的 `@pytest.fixture` 装饰器
- [x] fixtures 可以被测试文件正确导入和使用

## 集成测试文件拆分检查
- [x] 存在 `tests/integration/test_auth.py`（用户认证测试）
- [x] 存在 `tests/integration/test_projects.py`（项目管理测试）
- [x] 存在 `tests/integration/test_script_works.py`（脚本作品测试）
- [x] 存在 `tests/integration/__init__.py` 文件

## 用户认证测试检查
- [x] `tests/integration/test_auth.py` 包含所有原有的注册测试用例（TC-REG-001 到 TC-REG-004）
- [x] `tests/integration/test_auth.py` 包含所有原有的登录测试用例（TC-LOG-001 到 TC-LOG-005）
- [x] 测试使用 pytest 的 markers 进行分组（如 `@pytest.mark.auth`）
- [x] 移除了自定义的 TestResult 类，使用 pytest 原生 assert
- [x] 运行 `pytest tests/integration/test_auth.py -v --collect-only` 可以发现所有测试用例

## 项目管理测试检查
- [x] `tests/integration/test_projects.py` 包含所有原有的项目创建测试用例（TC-PRJ-001 到 TC-PRJ-004）
- [x] `tests/integration/test_projects.py` 包含所有原有的项目删除测试用例（TC-DEL-001 到 TC-DEL-003）
- [x] 测试使用 pytest 的 markers 进行分组（如 `@pytest.mark.projects`）
- [x] 测试之间的依赖关系使用 fixtures 或依赖管理
- [x] 运行 `pytest tests/integration/test_projects.py -v --collect-only` 可以发现所有测试用例

## 脚本作品测试检查
- [x] `tests/integration/test_script_works.py` 包含所有原有的脚本测试用例（TC-SCR-001 到 TC-SCR-007）
- [x] 测试使用 pytest 的 markers 进行分组（如 `@pytest.mark.script_works`）
- [x] 测试使用 fixtures 管理测试状态（测试项目、测试脚本作品）
- [x] 运行 `pytest tests/integration/test_script_works.py -v --collect-only` 可以发现所有测试用例

## 整体测试验证
- [x] 运行 `pytest tests/ --collect-only` 可以发现所有测试用例
- [x] 运行 `pytest tests/unit/ -v` 所有单元测试通过
- [x] 测试文件数量和测试用例数量不少于原有测试

## VSCode 集成检查（人工验证）
- [x] VSCode 设置中 pytest 已启用（`.vscode/settings.json` 配置正确）
- [ ] VSCode 测试面板可以显示所有测试用例
- [ ] 可以在 VSCode 中点击运行单个测试用例
- [ ] 可以在 VSCode 中调试测试用例
- [ ] 测试文件中的测试函数旁显示运行按钮

## 清理检查
- [x] 旧的 `test_config.py` 文件已删除
- [x] 旧的 `test_runner.py` 文件已删除
- [ ] `.gitignore` 已更新（如果需要）
- [ ] 项目根目录没有遗留的测试相关临时文件

## 分组功能验证
- [x] 可以通过 markers 分组运行测试（如 `pytest -m auth`）
- [x] 可以通过目录分组运行测试（如 `pytest tests/unit/` 或 `pytest tests/integration/`）
- [x] 可以通过文件名分组运行测试（如 `pytest tests/integration/test_auth.py`）
