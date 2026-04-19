#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试配置读取是否正确"""

from pathlib import Path
import sys

# 添加项目根目录到路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.settings import settings, get_settings


def test_config_loading():
    """测试配置是否正确从两个文件加载"""
    
    print("=" * 60)
    print("测试配置加载")
    print("=" * 60)
    
    # 清除缓存以便重新加载
    get_settings.cache_clear()
    settings = get_settings()
    
    print("\n1. 测试 APP 配置（来自 public_env.data）:")
    print(f"   APP_NAME: {settings.app.name}")
    print(f"   APP_VERSION: {settings.app.version}")
    print(f"   APP_DEBUG: {settings.app.debug}")
    print(f"   APP_ALLOWED_ORIGINS: {settings.app.allowed_origins}")
    
    # 验证 APP 配置
    assert settings.app.name == "MiniMax API Plan", f"Expected 'MiniMax API Plan', got {settings.app.name}"
    assert settings.app.version == "1.0.0", f"Expected '1.0.0', got {settings.app.version}"
    assert settings.app.debug == True, f"Expected True, got {settings.app.debug}"
    print("   [PASS] APP 配置验证通过")
    
    print("\n2. 测试 MINIMAX 配置:")
    print(f"   MINIMAX_API_KEY (部分显示): {settings.minimax.api_key[:20] if settings.minimax.api_key else 'None'}...")
    print(f"   MINIMAX_GROUP_ID: {settings.minimax.group_id}")
    print(f"   MINIMAX_BASE_URL: {settings.minimax.base_url}")
    print(f"   MINIMAX_DEFAULT_MODEL: {settings.minimax.default_model}")
    print(f"   MINIMAX_TIMEOUT: {settings.minimax.timeout}")
    
    # 验证 MINIMAX 配置 - API_KEY 应该来自 .env，覆盖 public_env.data 中的占位符
    assert settings.minimax.api_key is not None, "MINIMAX_API_KEY 不应该为 None"
    assert settings.minimax.api_key != "your_api_key_here", "MINIMAX_API_KEY 应该被 .env 中的值覆盖"
    assert settings.minimax.base_url == "https://api.minimaxi.com/v1/text/chatcompletion_v2", f"Expected 'https://api.minimaxi.com/v1/text/chatcompletion_v2', got {settings.minimax.base_url}"
    assert settings.minimax.default_model == "MiniMax-M2.7", f"Expected 'MiniMax-M2.7', got {settings.minimax.default_model}"
    assert settings.minimax.timeout == 180.0, f"Expected 180.0, got {settings.minimax.timeout}"
    print("   [PASS] MINIMAX 配置验证通过")
    
    print("\n3. 测试 DATABASE 配置:")
    print(f"   DB_DRIVER: {settings.database.driver}")
    print(f"   DB_HOST: {settings.database.host}")
    print(f"   DB_PORT: {settings.database.port}")
    print(f"   DB_USERNAME: {settings.database.username}")
    print(f"   DB_PASSWORD (部分显示): {settings.database.password[:5] if settings.database.password else 'None'}...")
    print(f"   DB_DATABASE: {settings.database.database}")
    print(f"   DB_CHARSET: {settings.database.charset}")
    print(f"   DB_POOL_SIZE: {settings.database.pool_size}")
    print(f"   DB_MAX_OVERFLOW: {settings.database.max_overflow}")
    print(f"   DB_POOL_RECYCLE: {settings.database.pool_recycle}")
    print(f"   DB_ECHO: {settings.database.echo}")
    
    # 验证 DATABASE 配置
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
    print("   [PASS] DATABASE 配置验证通过")
    
    print("\n4. 测试 EVALUATION 配置:")
    print(f"   EVALUATION_ENABLED: {settings.evaluation.enabled}")
    print(f"   EVALUATION_MODEL: {settings.evaluation.model}")
    
    # 验证 EVALUATION 配置
    assert settings.evaluation.enabled == False, f"Expected False, got {settings.evaluation.enabled}"
    assert settings.evaluation.model == "MiniMax-M2.7", f"Expected 'MiniMax-M2.7', got {settings.evaluation.model}"
    print("   [PASS] EVALUATION 配置验证通过")
    
    print("\n5. 测试 DSN 生成:")
    dsn = settings.database.get_dsn()
    print(f"   DSN: {dsn}")
    assert dsn != "", "DSN 不应该为空"
    assert "super999" in dsn, "DSN 应该包含用户名"
    assert "192.168.9.101" in dsn, "DSN 应该包含主机地址"
    assert "minimax_api_plan" in dsn, "DSN 应该包含数据库名"
    print("   [PASS] DSN 生成验证通过")
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        test_config_loading()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
