import pytest
from core.settings import get_settings


@pytest.fixture
def clean_settings():
    get_settings.cache_clear()
    yield get_settings()
    get_settings.cache_clear()


@pytest.mark.unit
class TestAppConfig:
    def test_app_config(self, clean_settings):
        settings = clean_settings
        assert settings.app.name == "MiniMax API Plan", f"Expected 'MiniMax API Plan', got {settings.app.name}"
        assert settings.app.version == "1.0.0", f"Expected '1.0.0', got {settings.app.version}"
        assert settings.app.debug == True, f"Expected True, got {settings.app.debug}"


@pytest.mark.unit
class TestMiniMaxConfig:
    def test_minimax_config(self, clean_settings):
        settings = clean_settings
        assert settings.minimax.api_key is not None, "MINIMAX_API_KEY 不应该为 None"
        assert settings.minimax.api_key != "your_api_key_here", "MINIMAX_API_KEY 应该被 .env 中的值覆盖"
        assert settings.minimax.base_url == "https://api.minimaxi.com/v1/text/chatcompletion_v2", f"Expected 'https://api.minimaxi.com/v1/text/chatcompletion_v2', got {settings.minimax.base_url}"
        assert settings.minimax.default_model == "MiniMax-M2.7", f"Expected 'MiniMax-M2.7', got {settings.minimax.default_model}"
        assert settings.minimax.timeout == 180.0, f"Expected 180.0, got {settings.minimax.timeout}"


@pytest.mark.unit
class TestDatabaseConfig:
    def test_database_config(self, clean_settings):
        settings = clean_settings
        assert settings.database.driver == "mysql+aiomysql", f"Expected 'mysql+aiomysql', got {settings.database.driver}"
        assert settings.database.host == "192.168.9.101", f"Expected '192.168.9.101', got {settings.database.host}"
        assert settings.database.port == 3306, f"Expected 3306, got {settings.database.port}"
        assert settings.database.username == "super999", f"Expected 'super999', got {settings.database.username}"
        assert settings.database.password == "chenxiawen", f"Expected 'chenxiawen', got {settings.database.password}"
        assert settings.database.database == "minimax_api_plan", f"Expected 'minimax_api_plan', got {settings.database.database}"
        assert settings.database.charset == "utf8mb4", f"Expected 'utf8mb4', got {settings.database.charset}"
        assert settings.database.pool_size == 10, f"Expected 10, got {settings.database.pool_size}"
        assert settings.database.max_overflow == 5, f"Expected 5, got {settings.database.max_overflow}"
        assert settings.database.pool_recycle == 3600, f"Expected 3600, got {settings.database.pool_recycle}"
        assert settings.database.echo == False, f"Expected False, got {settings.database.echo}"


@pytest.mark.unit
class TestEvaluationConfig:
    def test_evaluation_config(self, clean_settings):
        settings = clean_settings
        assert settings.evaluation.enabled == False, f"Expected False, got {settings.evaluation.enabled}"
        assert settings.evaluation.model == "MiniMax-M2.7", f"Expected 'MiniMax-M2.7', got {settings.evaluation.model}"


@pytest.mark.unit
class TestDSNGeneration:
    def test_dsn_generation(self, clean_settings):
        settings = clean_settings
        dsn = settings.database.get_dsn()
        assert dsn != "", "DSN 不应该为空"
        assert "super999" in dsn, "DSN 应该包含用户名"
        assert "192.168.9.101" in dsn, "DSN 应该包含主机地址"
        assert "minimax_api_plan" in dsn, "DSN 应该包含数据库名"
