import pytest
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"


def generate_test_username() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"testuser_{timestamp}"


def generate_test_email() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"test_{timestamp}@example.com"


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def client(base_url: str) -> httpx.Client:
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        yield client


@pytest.fixture
def test_user_data() -> dict:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "username": f"testuser_{timestamp}",
        "password": "Test123456",
        "email": f"test_{timestamp}@example.com"
    }


@pytest.fixture
def auth_headers() -> dict:
    headers = {}
    yield headers


@pytest.fixture
def test_project_data() -> dict:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "name": f"测试项目_{timestamp}",
        "status": "planning",
        "description": "这是一个测试项目"
    }


@pytest.fixture
def test_script_work_data() -> dict:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "title": f"测试脚本作品_{timestamp}",
        "status": "draft",
        "description": "这是一个测试脚本作品"
    }


@pytest.fixture
def registered_user(client: httpx.Client, test_user_data: dict) -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 201, f"注册失败: {response.text}"
    return {
        "id": response.json().get("id"),
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }


@pytest.fixture
def logged_in_user(client: httpx.Client, registered_user: dict, auth_headers: dict) -> dict:
    response = client.post(
        "/api/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )
    assert response.status_code == 200, f"登录失败: {response.text}"
    access_token = response.json().get("access_token")
    auth_headers["Authorization"] = f"Bearer {access_token}"
    return {
        "id": registered_user["id"],
        "username": registered_user["username"],
        "access_token": access_token
    }


@pytest.fixture
def test_project(client: httpx.Client, logged_in_user: dict, test_project_data: dict) -> dict:
    response = client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {logged_in_user['access_token']}"},
        json={
            "name": test_project_data["name"],
            "status": test_project_data["status"]
        }
    )
    assert response.status_code == 201, f"创建项目失败: {response.text}"
    return response.json()


@pytest.fixture
def test_script_work(client: httpx.Client, logged_in_user: dict, test_project: dict, test_script_work_data: dict) -> dict:
    response = client.post(
        "/api/script-works",
        headers={"Authorization": f"Bearer {logged_in_user['access_token']}"},
        json={
            "title": test_script_work_data["title"],
            "project_id": test_project["id"],
            "status": test_script_work_data["status"]
        }
    )
    assert response.status_code == 201, f"创建脚本作品失败: {response.text}"
    return response.json()
