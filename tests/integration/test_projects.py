import pytest
import httpx
from datetime import datetime


@pytest.mark.integration
@pytest.mark.projects
class TestProjectCreation:
    """项目创建功能测试"""

    def _register_and_login(self, client: httpx.Client, test_user_data: dict):
        """辅助函数：注册并登录用户"""
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
        return login_response.json().get("access_token")

    def test_create_project_success_required_fields(self, client: httpx.Client, test_user_data: dict):
        """TC-PRJ-001: 成功创建项目（必填字段）"""
        access_token = self._register_and_login(client, test_user_data)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": f"测试项目_{timestamp}",
                "status": "planning"
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "id" in data
        assert data.get("name") == f"测试项目_{timestamp}"

    def test_create_project_failure_unauthorized(self, client: httpx.Client):
        """TC-PRJ-002: 创建失败 - 未登录（无token）"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        response = client.post(
            "/api/projects",
            json={
                "name": f"未登录项目_{timestamp}",
                "status": "planning"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_create_project_success_with_description(self, client: httpx.Client, test_user_data: dict):
        """TC-PRJ-003: 成功创建项目（包含描述）"""
        access_token = self._register_and_login(client, test_user_data)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": f"完整项目_{timestamp}",
                "description": "这是一个用于测试的完整项目，包含描述信息",
                "status": "active"
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert data.get("description") is not None

    def test_get_projects_list_success(self, client: httpx.Client, test_user_data: dict):
        """TC-PRJ-004: 获取项目列表"""
        access_token = self._register_and_login(client, test_user_data)

        # 先创建一个项目
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": f"列表测试项目_{timestamp}",
                "status": "planning"
            }
        )
        assert create_response.status_code == 201

        # 获取项目列表
        list_response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert list_response.status_code == 200, f"Expected 200, got {list_response.status_code}"
        data = list_response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


@pytest.mark.integration
@pytest.mark.projects
class TestProjectDeletion:
    """项目删除功能测试"""

    def _register_login_and_create_project(self, client: httpx.Client, test_user_data: dict):
        """辅助函数：注册、登录并创建项目"""
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

        # 创建项目
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_response = client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": f"删除测试项目_{timestamp}",
                "status": "planning"
            }
        )
        assert create_response.status_code == 201
        project_id = create_response.json().get("id")

        return access_token, project_id

    def test_delete_project_success(self, client: httpx.Client, test_user_data: dict):
        """TC-DEL-001: 成功删除项目"""
        access_token, project_id = self._register_login_and_create_project(client, test_user_data)

        # 删除项目
        delete_response = client.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        data = delete_response.json()
        assert "message" in data

    def test_delete_project_failure_not_found(self, client: httpx.Client, test_user_data: dict):
        """TC-DEL-002: 删除失败 - 项目不存在"""
        access_token, _ = self._register_login_and_create_project(client, test_user_data)

        # 尝试删除不存在的项目
        delete_response = client.delete(
            "/api/projects/999999999",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert delete_response.status_code == 404, f"Expected 404, got {delete_response.status_code}"

    def test_delete_project_failure_unauthorized(self, client: httpx.Client):
        """TC-DEL-003: 删除失败 - 未登录（无token）"""
        # 尝试删除项目但不提供 token
        delete_response = client.delete("/api/projects/1")
        assert delete_response.status_code == 401, f"Expected 401, got {delete_response.status_code}"
