# -*- coding: utf-8 -*-
"""
认证模块接口测试用例
覆盖：登录（成功/失败/边界）、获取当前用户、登出
对应接口：
  POST /auth/login
  GET  /auth/me
  POST /auth/logout
  POST /auth/register
"""
import pytest
from common.request_util import HttpRequest, load_config
from common.assert_util import AssertUtil
from api.auth_api import AuthApi
from faker import Faker

fake = Faker("zh_CN")


class TestAuthLogin:
    """登录接口测试"""

    def test_login_success(self, cfg):
        """正向：正确账号密码能登录成功，返回 token"""
        http = HttpRequest(cfg["base_url"])
        auth = AuthApi(http)
        # 先注册一个临时用户，避免依赖固定 admin 密码
        username = f"qa_login_{fake.user_name()}_{fake.random_int(10000,99999)}"
        password = "QaTest123456"
        reg = auth.register(username, password)
        assert reg.json().get("code") == 0, f"前置注册失败: {reg.text}"

        resp = auth.login(username, password)
        AssertUtil.assert_http_status(resp, 200)
        body = resp.json()
        AssertUtil.assert_success(body)
        # data 里至少要有 token 字段
        data = body.get("data") or {}
        token = data.get("token") or data.get("accessToken")
        assert token, f"登录成功但没拿到 token，实际 data={data}"
        assert data.get("username") == username, f"返回的 username 不匹配: {data}"

    def test_login_wrong_password(self, cfg):
        """反向：密码错误，应该返回错误，不能登录"""
        http = HttpRequest(cfg["base_url"])
        auth = AuthApi(http)
        resp = auth.login(cfg["admin_username"], "wrong_password_xxx_不存在")
        body = resp.json()
        assert body.get("code") != 0, f"密码错误居然登录成功了？body={body}"
        assert body.get("data") is None

    def test_login_user_not_exist(self, cfg):
        """反向：用户不存在"""
        http = HttpRequest(cfg["base_url"])
        auth = AuthApi(http)
        resp = auth.login("not_exist_user_xyz_9999", "any_password")
        body = resp.json()
        assert body.get("code") != 0, f"不存在的用户居然登录成功了？body={body}"
        assert body.get("data") is None

    def test_login_empty_username(self, cfg):
        """边界：用户名为空"""
        http = HttpRequest(cfg["base_url"])
        auth = AuthApi(http)
        resp = auth.login("", "123456")
        body = resp.json()
        assert body.get("code") != 0, "用户名为空居然登录成功了？"

    def test_login_empty_password(self, cfg):
        """边界：密码为空"""
        http = HttpRequest(cfg["base_url"])
        auth = AuthApi(http)
        resp = auth.login(cfg["admin_username"], "")
        body = resp.json()
        assert body.get("code") != 0, "密码为空居然登录成功了？"


class TestAuthMe:
    """获取当前用户接口测试"""

    def test_me_without_token(self, cfg):
        """反向：不带 token 访问 /auth/me，应该 401"""
        http = HttpRequest(cfg["base_url"])
        auth = AuthApi(http)
        resp = auth.me()
        assert resp.status_code == 401, f"未带 token 居然返回 {resp.status_code}"

    def test_me_with_invalid_token(self, cfg):
        """反向：带一个假 token"""
        http = HttpRequest(cfg["base_url"], token="fake_token_123456")
        auth = AuthApi(http)
        resp = auth.me()
        assert resp.status_code in (401, 403), f"假 token 应该被拒绝，实际 {resp.status_code}"

    def test_me_success(self, admin_http):
        """正向：带正确 token 能拿到当前用户信息"""
        auth = AuthApi(admin_http)
        resp = auth.me()
        body = resp.json()
        AssertUtil.assert_success(body)
        AssertUtil.assert_data_has_keys(body, ["userId", "username"])


class TestAuthLogout:
    """登出测试 - 用临时用户，避免污染 admin session"""

    @pytest.mark.xfail(
        reason="已知BUG(P1)：登出后JWT仍可用。根因：TokenBlacklistService写入Redis失败时被静默catch，"
               "登出接口返回成功但黑名单未实际生效。需修：Redis写入失败应抛异常或返回错误码。",
        strict=False
    )
    def test_logout_then_token_invalid(self, cfg):
        """登出后，原来的 token 应该立刻失效"""
        # 1. 先注册一个临时用户
        http = HttpRequest(cfg["base_url"])
        auth = AuthApi(http)
        tmp_user = f"qa_{fake.user_name()}_{fake.random_int(1000,9999)}"
        tmp_pwd = "Test123456"
        reg_resp = auth.register(tmp_user, tmp_pwd, nickname="QA临时用户")
        if reg_resp.json().get("code") != 0:
            pytest.skip(f"注册失败（可能已有同名用户）: {reg_resp.text}")

        # 2. 登录拿 token
        login_resp = auth.login(tmp_user, tmp_pwd)
        token = (login_resp.json().get("data") or {}).get("token")
        assert token, f"临时用户登录失败: {login_resp.text}"
        http.set_token(token)

        # 3. 登出前 /auth/me 应该成功
        me_before = auth.me()
        assert me_before.json().get("code") == 0, "登出前应该能访问 /auth/me"

        # 4. 登出
        logout_resp = auth.logout()
        assert logout_resp.status_code == 200

        # 5. 登出后再访问 /auth/me 应该 401/403
        me_after = auth.me()
        assert me_after.status_code in (401, 403), \
            f"登出后 token 应该失效，实际 HTTP {me_after.status_code}"
