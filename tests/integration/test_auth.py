import pytest
import httpx
from datetime import datetime


@pytest.mark.integration
@pytest.mark.auth
class TestUserRegistration:
    """用户注册功能测试"""

    def test_register_success_with_required_fields(self, client: httpx.Client, test_user_data: dict):
        """TC-REG-001: 成功注册新用户（必填字段）"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert data.get("username") == test_user_data["username"]
        assert "id" in data

    def test_register_failure_duplicate_username(self, client: httpx.Client, test_user_data: dict):
        """TC-REG-002: 注册失败 - 用户名已存在"""
        # 先注册第一个用户
        response1 = client.post(
            "/api/auth/register",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert response1.status_code == 201

        # 尝试用相同用户名注册
        response2 = client.post(
            "/api/auth/register",
            json={
                "username": test_user_data["username"],
                "password": "AnotherPass123"
            }
        )
        assert response2.status_code == 400, f"Expected 400, got {response2.status_code}"

    def test_register_success_with_email(self, client: httpx.Client):
        """TC-REG-003: 成功注册新用户（包含邮箱）"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        response = client.post(
            "/api/auth/register",
            json={
                "username": f"testuser_{timestamp}",
                "password": "Test123456",
                "email": f"test_{timestamp}@example.com"
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert data.get("email") == f"test_{timestamp}@example.com"

    def test_register_failure_duplicate_email(self, client: httpx.Client):
        """TC-REG-004: 注册失败 - 邮箱已被注册"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_email = f"test_{timestamp}@example.com"

        # 先注册第一个用户（带邮箱）
        response1 = client.post(
            "/api/auth/register",
            json={
                "username": f"user1_{timestamp}",
                "password": "Test123456",
                "email": test_email
            }
        )
        assert response1.status_code == 201

        # 尝试用相同邮箱注册
        response2 = client.post(
            "/api/auth/register",
            json={
                "username": f"user2_{timestamp}",
                "password": "Test123456",
                "email": test_email
            }
        )
        assert response2.status_code == 400, f"Expected 400, got {response2.status_code}"


@pytest.mark.integration
@pytest.mark.auth
class TestUserLogin:
    """用户登录功能测试"""

    def test_login_success_valid_credentials(self, client: httpx.Client, test_user_data: dict):
        """TC-LOG-001: 成功登录（正确的用户名和密码）"""
        # 先注册用户
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert register_response.status_code == 201

        # 然后登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert login_response.status_code == 200, f"Expected 200, got {login_response.status_code}"
        data = login_response.json()
        assert "access_token" in data
        assert data.get("access_token") is not None

    def test_login_failure_nonexistent_user(self, client: httpx.Client):
        """TC-LOG-002: 登录失败 - 用户名不存在"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent_user_99999",
                "password": "Test123456"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_login_failure_wrong_password(self, client: httpx.Client, test_user_data: dict):
        """TC-LOG-003: 登录失败 - 密码错误"""
        # 先注册用户
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert register_response.status_code == 201

        # 使用错误密码登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": "wrong_password_123"
            }
        )
        assert login_response.status_code == 401, f"Expected 401, got {login_response.status_code}"

    def test_get_current_user_success(self, client: httpx.Client, test_user_data: dict):
        """TC-LOG-004: 获取当前用户信息（需登录）"""
        # 注册
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert register_response.status_code == 201

        # 登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert login_response.status_code == 200
        access_token = login_response.json().get("access_token")

        # 获取当前用户
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200, f"Expected 200, got {me_response.status_code}"
        data = me_response.json()
        assert data.get("username") == test_user_data["username"]

    def test_get_current_user_failure_unauthorized(self, client: httpx.Client):
        """TC-LOG-005: 获取当前用户信息（未登录）"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
