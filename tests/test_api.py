"""
简单测试 - 演示如何调用 API
运行：python tests/test_api.py

注意：需要先启动后端服务
"""
import requests

BASE = "http://localhost:9000"


def test_register_login():
    """测试注册登录"""
    print("=" * 40)
    print("测试注册登录")
    print("=" * 40)

    # 注册
    r = requests.post(f"{BASE}/api/users/register", json={
        "name": "测试用户",
        "phone": "13800138000",
        "password": "test123456",
    })
    print(f"注册: {r.status_code} {r.json()}")

    # 登录
    r = requests.post(f"{BASE}/api/users/login", json={
        "phone": "13800138000",
        "password": "test123456",
    })
    print(f"登录: {r.status_code} {r.json()}")
    token = r.json()["data"]["access_token"]

    # 获取我的信息
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/api/users/me", headers=headers)
    print(f"我的信息: {r.status_code} {r.json()}")

    return token


def test_admin_login():
    """测试管理员登录"""
    print("\n" + "=" * 40)
    print("测试管理员登录")
    print("=" * 40)

    r = requests.post(f"{BASE}/api/admins/login", json={
        "username": "admin",
        "password": "admin123",
    })
    print(f"管理员登录: {r.status_code} {r.json()}")
    return r.json()["data"]["access_token"]


def test_report(user_token):
    """测试上报"""
    print("\n" + "=" * 40)
    print("测试上报（文字）")
    print("=" * 40)

    headers = {"Authorization": f"Bearer {user_token}"}
    r = requests.post(
        f"{BASE}/api/orders/report",
        headers=headers,
        data={
            "location": "杭州市西湖区文一路100号",
            "text": "路口的路灯坏了，晚上很危险",
        }
    )
    print(f"上报结果: {r.status_code} {r.json()}")
    return r.json()["data"]["order_id"]


def test_stats(admin_token):
    """测试统计"""
    print("\n" + "=" * 40)
    print("测试统计接口")
    print("=" * 40)

    headers = {"Authorization": f"Bearer {admin_token}"}
    r = requests.get(f"{BASE}/api/stats/overview", headers=headers)
    print(f"总览: {r.status_code} {r.json()}")


if __name__ == "__main__":
    user_token = test_register_login()
    admin_token = test_admin_login()
    test_report(user_token)
    test_stats(admin_token)
