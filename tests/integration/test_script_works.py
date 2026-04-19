import pytest
import httpx
from datetime import datetime


@pytest.mark.integration
@pytest.mark.script_works
class TestScriptWorks:
    """脚本作品功能测试"""

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
                "name": f"脚本测试项目_{timestamp}",
                "status": "active"
            }
        )
        assert create_response.status_code == 201
        project_id = create_response.json().get("id")

        return access_token, project_id

    def test_create_script_work_success(self, client: httpx.Client, test_user_data: dict):
        """TC-SCR-001 & TC-SCR-002: 创建测试项目并创建脚本作品"""
        access_token, project_id = self._register_login_and_create_project(client, test_user_data)

        # TC-SCR-002: 成功创建脚本作品
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_response = client.post(
            "/api/script-works",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "title": f"测试脚本作品_{timestamp}",
                "project_id": project_id,
                "description": "这是一个用于测试的脚本作品",
                "status": "draft"
            }
        )
        assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}"
        data = create_response.json()
        assert "id" in data
        assert data.get("title") == f"测试脚本作品_{timestamp}"

    def test_edit_outline_success(self, client: httpx.Client, test_user_data: dict):
        """TC-SCR-003: 成功编辑脚本大纲"""
        access_token, project_id = self._register_login_and_create_project(client, test_user_data)

        # 创建脚本作品
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_response = client.post(
            "/api/script-works",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "title": f"大纲测试作品_{timestamp}",
                "project_id": project_id,
                "status": "draft"
            }
        )
        assert create_response.status_code == 201
        script_work_id = create_response.json().get("id")

        # 编辑大纲
        test_outline = """
# 故事大纲

## 第一章：开端
- 主角介绍
- 背景设定
- 冲突初现

## 第二章：发展
- 情节推进
- 角色关系发展
- 矛盾升级
"""
        edit_response = client.put(
            f"/api/script-works/{script_work_id}/outline",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "outline": test_outline
            }
        )
        assert edit_response.status_code == 200, f"Expected 200, got {edit_response.status_code}"

    def test_verify_outline_saved(self, client: httpx.Client, test_user_data: dict):
        """TC-SCR-004: 验证脚本大纲已保存"""
        access_token, project_id = self._register_login_and_create_project(client, test_user_data)

        # 创建脚本作品
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_response = client.post(
            "/api/script-works",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "title": f"验证大纲作品_{timestamp}",
                "project_id": project_id,
                "status": "draft"
            }
        )
        assert create_response.status_code == 201
        script_work_id = create_response.json().get("id")

        # 编辑大纲
        test_outline = "测试大纲内容"
        edit_response = client.put(
            f"/api/script-works/{script_work_id}/outline",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "outline": test_outline
            }
        )
        assert edit_response.status_code == 200

        # 验证大纲已保存
        get_response = client.get(
            f"/api/script-works/{script_work_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}"
        data = get_response.json()
        assert data.get("outline") is not None
        assert len(data.get("outline", "")) > 0

    def test_edit_outline_failure_not_found(self, client: httpx.Client, test_user_data: dict):
        """TC-SCR-005: 编辑失败 - 脚本作品不存在"""
        access_token, _ = self._register_login_and_create_project(client, test_user_data)

        edit_response = client.put(
            "/api/script-works/999999999/outline",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "outline": "测试大纲"
            }
        )
        assert edit_response.status_code == 404, f"Expected 404, got {edit_response.status_code}"

    def test_edit_outline_failure_unauthorized(self, client: httpx.Client, test_user_data: dict):
        """TC-SCR-006: 编辑失败 - 未登录（无token）"""
        access_token, project_id = self._register_login_and_create_project(client, test_user_data)

        # 创建脚本作品
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_response = client.post(
            "/api/script-works",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "title": f"未授权测试作品_{timestamp}",
                "project_id": project_id,
                "status": "draft"
            }
        )
        assert create_response.status_code == 201
        script_work_id = create_response.json().get("id")

        # 不使用 token 尝试编辑
        edit_response = client.put(
            f"/api/script-works/{script_work_id}/outline",
            json={
                "outline": "测试大纲"
            }
        )
        assert edit_response.status_code == 401, f"Expected 401, got {edit_response.status_code}"

    def test_edit_characters_success(self, client: httpx.Client, test_user_data: dict):
        """TC-SCR-007: 成功编辑角色设定"""
        access_token, project_id = self._register_login_and_create_project(client, test_user_data)

        # 创建脚本作品
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_response = client.post(
            "/api/script-works",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "title": f"角色设定测试作品_{timestamp}",
                "project_id": project_id,
                "status": "draft"
            }
        )
        assert create_response.status_code == 201
        script_work_id = create_response.json().get("id")

        # 编辑角色设定
        test_characters = """
# 主要角色

## 主角：李明
- 年龄：28岁
- 职业：程序员
- 性格：内向、认真、有正义感
"""
        edit_response = client.put(
            f"/api/script-works/{script_work_id}/characters",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "characters": test_characters
            }
        )
        assert edit_response.status_code == 200, f"Expected 200, got {edit_response.status_code}"
