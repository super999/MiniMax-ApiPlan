import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class TestResult:
    def __init__(self):
        self.test_cases = []
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = datetime.now()
    
    def add_test(self, test_id, module, description, expected, actual, status, notes=""):
        result = {
            "test_id": test_id,
            "module": module,
            "description": description,
            "expected": expected,
            "actual": actual,
            "status": status,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        self.test_cases.append(result)
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append({
                "test_id": test_id,
                "module": module,
                "description": description,
                "expected": expected,
                "actual": actual,
                "notes": notes
            })
    
    def get_summary(self):
        return {
            "total": len(self.test_cases),
            "passed": self.passed,
            "failed": self.failed,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat()
        }

def generate_test_username():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"testuser_{timestamp}"

def generate_test_email():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"test_{timestamp}@example.com"

def run_tests():
    test_result = TestResult()
    access_token = None
    test_user_id = None
    test_project_id = None
    test_script_work_id = None

    print("=" * 60)
    print("开始执行功能测试")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("模块1：用户注册功能测试")
    print("=" * 60)

    test_username = generate_test_username()
    test_password = "Test123456"
    test_email = generate_test_email()

    print("\n【TC-REG-001】成功注册新用户（必填字段）")
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": test_username,
                "password": test_password
            },
            timeout=10.0
        )
        
        if response.status_code == 201:
            data = response.json()
            test_result.add_test(
                test_id="TC-REG-001",
                module="用户注册",
                description="成功注册新用户（必填字段）",
                expected="状态码201，返回用户信息",
                actual=f"状态码{response.status_code}，用户名: {data.get('username')}",
                status="PASS"
            )
            test_user_id = data.get('id')
            print(f"  [PASS] 通过 - 用户ID: {test_user_id}")
        else:
            test_result.add_test(
                test_id="TC-REG-001",
                module="用户注册",
                description="成功注册新用户（必填字段）",
                expected="状态码201",
                actual=f"状态码{response.status_code}，响应: {response.text[:200]}",
                status="FAIL"
            )
            print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
    except Exception as e:
        test_result.add_test(
            test_id="TC-REG-001",
            module="用户注册",
            description="成功注册新用户（必填字段）",
            expected="成功注册",
            actual=f"异常: {str(e)}",
            status="FAIL"
        )
        print(f"  [FAIL] 异常 - {str(e)}")

    print("\n【TC-REG-002】注册失败 - 用户名已存在")
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": test_username,
                "password": "AnotherPass123"
            },
            timeout=10.0
        )
        
        if response.status_code == 400:
            data = response.json()
            test_result.add_test(
                test_id="TC-REG-002",
                module="用户注册",
                description="注册失败 - 用户名已存在",
                expected="状态码400，提示用户名已存在",
                actual=f"状态码{response.status_code}，消息: {data.get('detail', 'N/A')}",
                status="PASS"
            )
            print(f"  [PASS] 通过 - 正确拒绝重复注册")
        else:
            test_result.add_test(
                test_id="TC-REG-002",
                module="用户注册",
                description="注册失败 - 用户名已存在",
                expected="状态码400",
                actual=f"状态码{response.status_code}",
                status="FAIL"
            )
            print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
    except Exception as e:
        test_result.add_test(
            test_id="TC-REG-002",
            module="用户注册",
            description="注册失败 - 用户名已存在",
            expected="成功拒绝",
            actual=f"异常: {str(e)}",
            status="FAIL"
        )
        print(f"  [FAIL] 异常 - {str(e)}")

    print("\n【TC-REG-003】成功注册新用户（包含邮箱）")
    test_username2 = generate_test_username()
    test_email2 = generate_test_email()
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": test_username2,
                "password": test_password,
                "email": test_email2
            },
            timeout=10.0
        )
        
        if response.status_code == 201:
            data = response.json()
            test_result.add_test(
                test_id="TC-REG-003",
                module="用户注册",
                description="成功注册新用户（包含邮箱）",
                expected="状态码201，返回包含邮箱的用户信息",
                actual=f"状态码{response.status_code}，邮箱: {data.get('email')}",
                status="PASS"
            )
            print(f"  [PASS] 通过 - 邮箱: {data.get('email')}")
        else:
            test_result.add_test(
                test_id="TC-REG-003",
                module="用户注册",
                description="成功注册新用户（包含邮箱）",
                expected="状态码201",
                actual=f"状态码{response.status_code}",
                status="FAIL"
            )
            print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
    except Exception as e:
        test_result.add_test(
            test_id="TC-REG-003",
            module="用户注册",
            description="成功注册新用户（包含邮箱）",
            expected="成功注册",
            actual=f"异常: {str(e)}",
            status="FAIL"
        )
        print(f"  [FAIL] 异常 - {str(e)}")

    print("\n【TC-REG-004】注册失败 - 邮箱已被注册")
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": generate_test_username(),
                "password": test_password,
                "email": test_email2
            },
            timeout=10.0
        )
        
        if response.status_code == 400:
            data = response.json()
            test_result.add_test(
                test_id="TC-REG-004",
                module="用户注册",
                description="注册失败 - 邮箱已被注册",
                expected="状态码400，提示邮箱已被注册",
                actual=f"状态码{response.status_code}，消息: {data.get('detail', 'N/A')}",
                status="PASS"
            )
            print(f"  [PASS] 通过 - 正确拒绝重复邮箱")
        else:
            test_result.add_test(
                test_id="TC-REG-004",
                module="用户注册",
                description="注册失败 - 邮箱已被注册",
                expected="状态码400",
                actual=f"状态码{response.status_code}",
                status="FAIL"
            )
            print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
    except Exception as e:
        test_result.add_test(
            test_id="TC-REG-004",
            module="用户注册",
            description="注册失败 - 邮箱已被注册",
            expected="成功拒绝",
            actual=f"异常: {str(e)}",
            status="FAIL"
        )
        print(f"  [FAIL] 异常 - {str(e)}")

    print("\n" + "=" * 60)
    print("模块2：用户登录功能测试")
    print("=" * 60)

    print("\n【TC-LOG-001】成功登录（正确的用户名和密码）")
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": test_username,
                "password": test_password
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            test_result.add_test(
                test_id="TC-LOG-001",
                module="用户登录",
                description="成功登录（正确的用户名和密码）",
                expected="状态码200，返回access_token和用户信息",
                actual=f"状态码{response.status_code}，token存在: {access_token is not None}",
                status="PASS"
            )
            print(f"  [PASS] 通过 - 登录成功")
        else:
            test_result.add_test(
                test_id="TC-LOG-001",
                module="用户登录",
                description="成功登录（正确的用户名和密码）",
                expected="状态码200",
                actual=f"状态码{response.status_code}",
                status="FAIL"
            )
            print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
    except Exception as e:
        test_result.add_test(
            test_id="TC-LOG-001",
            module="用户登录",
            description="成功登录（正确的用户名和密码）",
            expected="成功登录",
            actual=f"异常: {str(e)}",
            status="FAIL"
        )
        print(f"  [FAIL] 异常 - {str(e)}")

    print("\n【TC-LOG-002】登录失败 - 用户名不存在")
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "nonexistent_user_99999",
                "password": test_password
            },
            timeout=10.0
        )
        
        if response.status_code == 401:
            test_result.add_test(
                test_id="TC-LOG-002",
                module="用户登录",
                description="登录失败 - 用户名不存在",
                expected="状态码401",
                actual=f"状态码{response.status_code}",
                status="PASS"
            )
            print(f"  [PASS] 通过 - 正确拒绝不存在的用户")
        else:
            test_result.add_test(
                test_id="TC-LOG-002",
                module="用户登录",
                description="登录失败 - 用户名不存在",
                expected="状态码401",
                actual=f"状态码{response.status_code}",
                status="FAIL"
            )
            print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
    except Exception as e:
        test_result.add_test(
            test_id="TC-LOG-002",
            module="用户登录",
            description="登录失败 - 用户名不存在",
            expected="成功拒绝",
            actual=f"异常: {str(e)}",
            status="FAIL"
        )
        print(f"  [FAIL] 异常 - {str(e)}")

    print("\n【TC-LOG-003】登录失败 - 密码错误")
    try:
        response = httpx.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": test_username,
                "password": "wrong_password_123"
            },
            timeout=10.0
        )
        
        if response.status_code == 401:
            test_result.add_test(
                test_id="TC-LOG-003",
                module="用户登录",
                description="登录失败 - 密码错误",
                expected="状态码401",
                actual=f"状态码{response.status_code}",
                status="PASS"
            )
            print(f"  [PASS] 通过 - 正确拒绝错误密码")
        else:
            test_result.add_test(
                test_id="TC-LOG-003",
                module="用户登录",
                description="登录失败 - 密码错误",
                expected="状态码401",
                actual=f"状态码{response.status_code}",
                status="FAIL"
            )
            print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
    except Exception as e:
        test_result.add_test(
            test_id="TC-LOG-003",
            module="用户登录",
            description="登录失败 - 密码错误",
            expected="成功拒绝",
            actual=f"异常: {str(e)}",
            status="FAIL"
        )
        print(f"  [FAIL] 异常 - {str(e)}")

    print("\n【TC-LOG-004】获取当前用户信息（需登录）")
    if access_token:
        try:
            response = httpx.get(
                f"{BASE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                test_result.add_test(
                    test_id="TC-LOG-004",
                    module="用户登录",
                    description="获取当前用户信息（需登录）",
                    expected="状态码200，返回当前用户信息",
                    actual=f"状态码{response.status_code}，用户名: {data.get('username')}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - 用户名: {data.get('username')}")
            else:
                test_result.add_test(
                    test_id="TC-LOG-004",
                    module="用户登录",
                    description="获取当前用户信息（需登录）",
                    expected="状态码200",
                    actual=f"状态码{response.status_code}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-LOG-004",
                module="用户登录",
                description="获取当前用户信息（需登录）",
                expected="成功获取",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")
    else:
        test_result.add_test(
            test_id="TC-LOG-004",
            module="用户登录",
            description="获取当前用户信息（需登录）",
            expected="需要有效token",
            actual="跳过 - 没有可用的token",
            status="SKIP"
        )
        print(f"  [SKIP] 跳过 - 没有可用的token")

    print("\n【TC-LOG-005】获取当前用户信息（未登录）")
    try:
        response = httpx.get(
            f"{BASE_URL}/api/auth/me",
            timeout=10.0
        )
        
        if response.status_code == 401:
            test_result.add_test(
                test_id="TC-LOG-005",
                module="用户登录",
                description="获取当前用户信息（未登录）",
                expected="状态码401，未授权",
                actual=f"状态码{response.status_code}",
                status="PASS"
            )
            print(f"  [PASS] 通过 - 正确拒绝未授权访问")
        else:
            test_result.add_test(
                test_id="TC-LOG-005",
                module="用户登录",
                description="获取当前用户信息（未登录）",
                expected="状态码401",
                actual=f"状态码{response.status_code}",
                status="FAIL"
            )
            print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
    except Exception as e:
        test_result.add_test(
            test_id="TC-LOG-005",
            module="用户登录",
            description="获取当前用户信息（未登录）",
            expected="成功拒绝",
            actual=f"异常: {str(e)}",
            status="FAIL"
        )
        print(f"  [FAIL] 异常 - {str(e)}")

    print("\n" + "=" * 60)
    print("模块3：创建项目功能测试")
    print("=" * 60)

    if not access_token:
        print("[SKIP] 跳过项目测试 - 没有可用的token")
    else:
        print("\n【TC-PRJ-001】成功创建项目（必填字段）")
        try:
            response = httpx.post(
                f"{BASE_URL}/api/projects",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "name": f"测试项目_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "status": "planning"
                },
                timeout=10.0
            )
            
            if response.status_code == 201:
                data = response.json()
                test_project_id = data.get('id')
                test_result.add_test(
                    test_id="TC-PRJ-001",
                    module="创建项目",
                    description="成功创建项目（必填字段）",
                    expected="状态码201，返回项目信息",
                    actual=f"状态码{response.status_code}，项目ID: {test_project_id}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - 项目ID: {test_project_id}")
            else:
                test_result.add_test(
                    test_id="TC-PRJ-001",
                    module="创建项目",
                    description="成功创建项目（必填字段）",
                    expected="状态码201",
                    actual=f"状态码{response.status_code}，响应: {response.text[:200]}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-PRJ-001",
                module="创建项目",
                description="成功创建项目（必填字段）",
                expected="成功创建",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")

        print("\n【TC-PRJ-002】创建失败 - 未登录（无token）")
        try:
            response = httpx.post(
                f"{BASE_URL}/api/projects",
                json={
                    "name": f"未登录项目_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "status": "planning"
                },
                timeout=10.0
            )
            
            if response.status_code == 401:
                test_result.add_test(
                    test_id="TC-PRJ-002",
                    module="创建项目",
                    description="创建失败 - 未登录（无token）",
                    expected="状态码401，未授权",
                    actual=f"状态码{response.status_code}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - 正确拒绝未授权创建")
            else:
                test_result.add_test(
                    test_id="TC-PRJ-002",
                    module="创建项目",
                    description="创建失败 - 未登录（无token）",
                    expected="状态码401",
                    actual=f"状态码{response.status_code}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-PRJ-002",
                module="创建项目",
                description="创建失败 - 未登录（无token）",
                expected="成功拒绝",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")

        print("\n【TC-PRJ-003】成功创建项目（包含描述）")
        try:
            response = httpx.post(
                f"{BASE_URL}/api/projects",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "name": f"完整项目_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "description": "这是一个用于测试的完整项目，包含描述信息",
                    "status": "active"
                },
                timeout=10.0
            )
            
            if response.status_code == 201:
                data = response.json()
                test_result.add_test(
                    test_id="TC-PRJ-003",
                    module="创建项目",
                    description="成功创建项目（包含描述）",
                    expected="状态码201，返回包含描述的项目信息",
                    actual=f"状态码{response.status_code}，描述存在: {data.get('description') is not None}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - 项目创建成功")
            else:
                test_result.add_test(
                    test_id="TC-PRJ-003",
                    module="创建项目",
                    description="成功创建项目（包含描述）",
                    expected="状态码201",
                    actual=f"状态码{response.status_code}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-PRJ-003",
                module="创建项目",
                description="成功创建项目（包含描述）",
                expected="成功创建",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")

        print("\n【TC-PRJ-004】获取项目列表")
        try:
            response = httpx.get(
                f"{BASE_URL}/api/projects",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                test_result.add_test(
                    test_id="TC-PRJ-004",
                    module="创建项目",
                    description="获取项目列表",
                    expected="状态码200，返回项目列表数组",
                    actual=f"状态码{response.status_code}，项目数量: {len(data)}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - 项目数量: {len(data)}")
            else:
                test_result.add_test(
                    test_id="TC-PRJ-004",
                    module="创建项目",
                    description="获取项目列表",
                    expected="状态码200",
                    actual=f"状态码{response.status_code}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-PRJ-004",
                module="创建项目",
                description="获取项目列表",
                expected="成功获取",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")

    print("\n" + "=" * 60)
    print("模块4：删除项目功能测试")
    print("=" * 60)

    if not access_token or not test_project_id:
        print("[SKIP] 跳过删除项目测试 - 没有可用的token或项目ID")
    else:
        print(f"\n【TC-DEL-001】成功删除项目（项目ID: {test_project_id}）")
        try:
            response = httpx.delete(
                f"{BASE_URL}/api/projects/{test_project_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                test_result.add_test(
                    test_id="TC-DEL-001",
                    module="删除项目",
                    description="成功删除项目",
                    expected="状态码200，返回成功消息",
                    actual=f"状态码{response.status_code}，消息: {data.get('message', 'N/A')}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - {data.get('message', 'N/A')}")
            else:
                test_result.add_test(
                    test_id="TC-DEL-001",
                    module="删除项目",
                    description="成功删除项目",
                    expected="状态码200",
                    actual=f"状态码{response.status_code}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-DEL-001",
                module="删除项目",
                description="成功删除项目",
                expected="成功删除",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")

        print("\n【TC-DEL-002】删除失败 - 项目不存在")
        try:
            response = httpx.delete(
                f"{BASE_URL}/api/projects/999999999",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if response.status_code == 404:
                test_result.add_test(
                    test_id="TC-DEL-002",
                    module="删除项目",
                    description="删除失败 - 项目不存在",
                    expected="状态码404，项目不存在",
                    actual=f"状态码{response.status_code}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - 正确拒绝不存在的项目")
            else:
                test_result.add_test(
                    test_id="TC-DEL-002",
                    module="删除项目",
                    description="删除失败 - 项目不存在",
                    expected="状态码404",
                    actual=f"状态码{response.status_code}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-DEL-002",
                module="删除项目",
                description="删除失败 - 项目不存在",
                expected="成功拒绝",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")

        print("\n【TC-DEL-003】删除失败 - 未登录（无token）")
        try:
            response = httpx.delete(
                f"{BASE_URL}/api/projects/1",
                timeout=10.0
            )
            
            if response.status_code == 401:
                test_result.add_test(
                    test_id="TC-DEL-003",
                    module="删除项目",
                    description="删除失败 - 未登录（无token）",
                    expected="状态码401，未授权",
                    actual=f"状态码{response.status_code}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - 正确拒绝未授权删除")
            else:
                test_result.add_test(
                    test_id="TC-DEL-003",
                    module="删除项目",
                    description="删除失败 - 未登录（无token）",
                    expected="状态码401",
                    actual=f"状态码{response.status_code}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-DEL-003",
                module="删除项目",
                description="删除失败 - 未登录（无token）",
                expected="成功拒绝",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")

    print("\n" + "=" * 60)
    print("模块5：手动编辑脚本大纲功能测试")
    print("=" * 60)

    if not access_token:
        print("[SKIP] 跳过脚本大纲测试 - 没有可用的token")
    else:
        print("\n【TC-SCR-001】创建新项目用于脚本测试")
        test_project_for_script = None
        try:
            response = httpx.post(
                f"{BASE_URL}/api/projects",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "name": f"脚本测试项目_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "status": "active"
                },
                timeout=10.0
            )
            
            if response.status_code == 201:
                data = response.json()
                test_project_for_script = data.get('id')
                test_result.add_test(
                    test_id="TC-SCR-001",
                    module="脚本大纲",
                    description="创建新项目用于脚本测试",
                    expected="状态码201，项目创建成功",
                    actual=f"状态码{response.status_code}，项目ID: {test_project_for_script}",
                    status="PASS"
                )
                print(f"  [PASS] 通过 - 项目ID: {test_project_for_script}")
            else:
                test_result.add_test(
                    test_id="TC-SCR-001",
                    module="脚本大纲",
                    description="创建新项目用于脚本测试",
                    expected="状态码201",
                    actual=f"状态码{response.status_code}",
                    status="FAIL"
                )
                print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
        except Exception as e:
            test_result.add_test(
                test_id="TC-SCR-001",
                module="脚本大纲",
                description="创建新项目用于脚本测试",
                expected="成功创建",
                actual=f"异常: {str(e)}",
                status="FAIL"
            )
            print(f"  [FAIL] 异常 - {str(e)}")

        if test_project_for_script:
            print("\n【TC-SCR-002】成功创建脚本作品")
            try:
                response = httpx.post(
                    f"{BASE_URL}/api/script-works",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "title": f"测试脚本作品_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "project_id": test_project_for_script,
                        "description": "这是一个用于测试的脚本作品",
                        "status": "draft"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    data = response.json()
                    test_script_work_id = data.get('id')
                    test_result.add_test(
                        test_id="TC-SCR-002",
                        module="脚本大纲",
                        description="成功创建脚本作品",
                        expected="状态码201，返回脚本作品信息",
                        actual=f"状态码{response.status_code}，作品ID: {test_script_work_id}",
                        status="PASS"
                    )
                    print(f"  [PASS] 通过 - 作品ID: {test_script_work_id}")
                else:
                    test_result.add_test(
                        test_id="TC-SCR-002",
                        module="脚本大纲",
                        description="成功创建脚本作品",
                        expected="状态码201",
                        actual=f"状态码{response.status_code}，响应: {response.text[:200]}",
                        status="FAIL"
                    )
                    print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
            except Exception as e:
                test_result.add_test(
                    test_id="TC-SCR-002",
                    module="脚本大纲",
                    description="成功创建脚本作品",
                    expected="成功创建",
                    actual=f"异常: {str(e)}",
                    status="FAIL"
                )
                print(f"  [FAIL] 异常 - {str(e)}")

            if test_script_work_id:
                print("\n【TC-SCR-003】成功编辑脚本大纲")
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

## 第三章：高潮
- 关键转折点
- 主要冲突爆发
- 情感高潮

## 第四章：结局
- 冲突解决
- 角色成长
- 故事收尾
"""
                try:
                    response = httpx.put(
                        f"{BASE_URL}/api/script-works/{test_script_work_id}/outline",
                        headers={"Authorization": f"Bearer {access_token}"},
                        json={
                            "outline": test_outline
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        test_result.add_test(
                            test_id="TC-SCR-003",
                            module="脚本大纲",
                            description="成功编辑脚本大纲",
                            expected="状态码200，大纲保存成功",
                            actual=f"状态码{response.status_code}，大纲已保存",
                            status="PASS"
                        )
                        print(f"  [PASS] 通过 - 大纲保存成功")
                    else:
                        test_result.add_test(
                            test_id="TC-SCR-003",
                            module="脚本大纲",
                            description="成功编辑脚本大纲",
                            expected="状态码200",
                            actual=f"状态码{response.status_code}",
                            status="FAIL"
                        )
                        print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
                except Exception as e:
                    test_result.add_test(
                        test_id="TC-SCR-003",
                        module="脚本大纲",
                        description="成功编辑脚本大纲",
                        expected="成功保存",
                        actual=f"异常: {str(e)}",
                        status="FAIL"
                    )
                    print(f"  [FAIL] 异常 - {str(e)}")

                print("\n【TC-SCR-004】验证脚本大纲已保存")
                try:
                    response = httpx.get(
                        f"{BASE_URL}/api/script-works/{test_script_work_id}",
                        headers={"Authorization": f"Bearer {access_token}"},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        outline_saved = data.get('outline') is not None and len(data.get('outline', '')) > 0
                        test_result.add_test(
                            test_id="TC-SCR-004",
                            module="脚本大纲",
                            description="验证脚本大纲已保存",
                            expected="状态码200，大纲字段非空",
                            actual=f"状态码{response.status_code}，大纲已保存: {outline_saved}",
                            status="PASS" if outline_saved else "FAIL"
                        )
                        if outline_saved:
                            print(f"  [PASS] 通过 - 大纲已正确保存")
                        else:
                            print(f"  [FAIL] 失败 - 大纲未保存")
                    else:
                        test_result.add_test(
                            test_id="TC-SCR-004",
                            module="脚本大纲",
                            description="验证脚本大纲已保存",
                            expected="状态码200",
                            actual=f"状态码{response.status_code}",
                            status="FAIL"
                        )
                        print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
                except Exception as e:
                    test_result.add_test(
                        test_id="TC-SCR-004",
                        module="脚本大纲",
                        description="验证脚本大纲已保存",
                        expected="成功验证",
                        actual=f"异常: {str(e)}",
                        status="FAIL"
                    )
                    print(f"  [FAIL] 异常 - {str(e)}")

                print("\n【TC-SCR-005】编辑失败 - 脚本作品不存在")
                try:
                    response = httpx.put(
                        f"{BASE_URL}/api/script-works/999999999/outline",
                        headers={"Authorization": f"Bearer {access_token}"},
                        json={
                            "outline": "测试大纲"
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 404:
                        test_result.add_test(
                            test_id="TC-SCR-005",
                            module="脚本大纲",
                            description="编辑失败 - 脚本作品不存在",
                            expected="状态码404，作品不存在",
                            actual=f"状态码{response.status_code}",
                            status="PASS"
                        )
                        print(f"  [PASS] 通过 - 正确拒绝不存在的作品")
                    else:
                        test_result.add_test(
                            test_id="TC-SCR-005",
                            module="脚本大纲",
                            description="编辑失败 - 脚本作品不存在",
                            expected="状态码404",
                            actual=f"状态码{response.status_code}",
                            status="FAIL"
                        )
                        print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
                except Exception as e:
                    test_result.add_test(
                        test_id="TC-SCR-005",
                        module="脚本大纲",
                        description="编辑失败 - 脚本作品不存在",
                        expected="成功拒绝",
                        actual=f"异常: {str(e)}",
                        status="FAIL"
                    )
                    print(f"  [FAIL] 异常 - {str(e)}")

                print("\n【TC-SCR-006】编辑失败 - 未登录（无token）")
                try:
                    response = httpx.put(
                        f"{BASE_URL}/api/script-works/{test_script_work_id}/outline",
                        json={
                            "outline": "测试大纲"
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 401:
                        test_result.add_test(
                            test_id="TC-SCR-006",
                            module="脚本大纲",
                            description="编辑失败 - 未登录（无token）",
                            expected="状态码401，未授权",
                            actual=f"状态码{response.status_code}",
                            status="PASS"
                        )
                        print(f"  [PASS] 通过 - 正确拒绝未授权编辑")
                    else:
                        test_result.add_test(
                            test_id="TC-SCR-006",
                            module="脚本大纲",
                            description="编辑失败 - 未登录（无token）",
                            expected="状态码401",
                            actual=f"状态码{response.status_code}",
                            status="FAIL"
                        )
                        print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
                except Exception as e:
                    test_result.add_test(
                        test_id="TC-SCR-006",
                        module="脚本大纲",
                        description="编辑失败 - 未登录（无token）",
                        expected="成功拒绝",
                        actual=f"异常: {str(e)}",
                        status="FAIL"
                    )
                    print(f"  [FAIL] 异常 - {str(e)}")

                print("\n【TC-SCR-007】成功编辑角色设定")
                test_characters = """
# 主要角色

## 主角：李明
- 年龄：28岁
- 职业：程序员
- 性格：内向、认真、有正义感
- 背景：从小在孤儿院长大，渴望找到自己的归属感

## 女主角：张小雨
- 年龄：26岁
- 职业：记者
- 性格：开朗、勇敢、追求真相
- 背景：来自富裕家庭，但选择独立生活追求新闻理想

## 反派：王总
- 年龄：45岁
- 职业：科技公司CEO
- 性格：野心勃勃、冷酷无情
- 背景：白手起家，但为了成功不择手段
"""
                try:
                    response = httpx.put(
                        f"{BASE_URL}/api/script-works/{test_script_work_id}/characters",
                        headers={"Authorization": f"Bearer {access_token}"},
                        json={
                            "characters": test_characters
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        test_result.add_test(
                            test_id="TC-SCR-007",
                            module="脚本大纲",
                            description="成功编辑角色设定",
                            expected="状态码200，角色设定保存成功",
                            actual=f"状态码{response.status_code}",
                            status="PASS"
                        )
                        print(f"  [PASS] 通过 - 角色设定保存成功")
                    else:
                        test_result.add_test(
                            test_id="TC-SCR-007",
                            module="脚本大纲",
                            description="成功编辑角色设定",
                            expected="状态码200",
                            actual=f"状态码{response.status_code}",
                            status="FAIL"
                        )
                        print(f"  [FAIL] 失败 - 状态码: {response.status_code}")
                except Exception as e:
                    test_result.add_test(
                        test_id="TC-SCR-007",
                        module="脚本大纲",
                        description="成功编辑角色设定",
                        expected="成功保存",
                        actual=f"异常: {str(e)}",
                        status="FAIL"
                    )
                    print(f"  [FAIL] 异常 - {str(e)}")

    print("\n" + "=" * 60)
    print("测试执行完成")
    print("=" * 60)

    summary = test_result.get_summary()
    print(f"\n测试统计:")
    print(f"  总测试数: {summary['total']}")
    print(f"  通过: {summary['passed']}")
    print(f"  失败: {summary['failed']}")
    print(f"  开始时间: {summary['start_time']}")
    print(f"  结束时间: {summary['end_time']}")

    if test_result.errors:
        print(f"\n发现的问题 ({len(test_result.errors)} 个):")
        for i, error in enumerate(test_result.errors, 1):
            print(f"\n  问题 {i}:")
            print(f"    测试ID: {error['test_id']}")
            print(f"    模块: {error['module']}")
            print(f"    描述: {error['description']}")
            print(f"    预期: {error['expected']}")
            print(f"    实际: {error['actual']}")
            if error['notes']:
                print(f"    备注: {error['notes']}")

    test_data = {
        "summary": summary,
        "test_cases": test_result.test_cases,
        "errors": test_result.errors
    }

    print(f"\n测试数据已准备，即将生成测试报告...")
    
    return test_data

if __name__ == "__main__":
    test_data = run_tests()
