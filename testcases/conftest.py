# -*- coding: utf-8 -*-
"""
pytest fixture 公共夹具
- 启动时自动注册一个测试账号并登录拿 token，不依赖人工准备 admin 密码
- admin_http / normal_http 返回带 token 的 HttpRequest 实例
"""
import pytest
from faker import Faker
from common.request_util import HttpRequest, load_config
from api.auth_api import AuthApi

fake = Faker("zh_CN")


def _register_and_login(cfg, role_tag: str) -> HttpRequest:
    """自动注册一个随机账号并登录，返回带 token 的 HttpRequest"""
    http = HttpRequest(cfg["base_url"])
    auth = AuthApi(http)

    # 先尝试用配置里的账号
    resp = auth.login(cfg["admin_username"], cfg["admin_password"])
    data = resp.json().get("data") or {}
    token = data.get("token") or data.get("accessToken")

    if not token:
        # 配置里的账号登不上，自动注册一个
        username = f"qa_{role_tag}_{fake.user_name()}_{fake.random_int(10000,99999)}"
        password = "QaTest123456"
        reg = auth.register(username, password, nickname=f"自动化测试-{role_tag}")
        if reg.json().get("code") != 0:
            raise RuntimeError(f"自动注册失败: {reg.text}")
        resp = auth.login(username, password)
        data = resp.json().get("data") or {}
        token = data.get("token") or data.get("accessToken")
        if not token:
            raise RuntimeError(f"自动注册后登录失败: {resp.text}")

    http.set_token(token)
    print(f"\n[fixture] {role_tag} 账号就绪，token 前缀: {token[:20]}...")
    return http


@pytest.fixture(scope="session")
def cfg():
    return load_config()


@pytest.fixture(scope="session")
def admin_http(cfg):
    """主测试账号（有 document/chat 等权限，注册用户默认就带这些权限）"""
    yield _register_and_login(cfg, "admin")


@pytest.fixture(scope="session")
def normal_http(cfg):
    """第二个测试账号（用于权限隔离、多用户测试）"""
    yield _register_and_login(cfg, "normal")
