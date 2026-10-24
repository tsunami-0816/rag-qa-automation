# -*- coding: utf-8 -*-
"""
聊天会话管理接口测试
覆盖：创建/列表/重命名/重置/删除/未授权
SSE 流式问答不测（依赖 LLM API，留给 JMeter 压测）
"""
import pytest
from common.assert_util import AssertUtil
from api.auth_api import AuthApi
from api.chat_api import ChatApi
from faker import Faker

fake = Faker("zh_CN")


@pytest.fixture(scope="class")
def my_user_id(admin_http):
    """从 /auth/me 拿当前登录用户的 userId"""
    me = AuthApi(admin_http).me().json()["data"]
    return me["userId"]


class TestChatSession:
    def test_create_session_success(self, admin_http, my_user_id):
        """正向：创建会话成功"""
        chat = ChatApi(admin_http)
        resp = chat.create_session(my_user_id, title=f"测试会话_{fake.uuid4()[:6]}")
        AssertUtil.assert_success(resp.json())
        session_id = resp.json()["data"]["id"]
        # 清理
        chat.delete_session(session_id)

    def test_create_session_without_userid(self, admin_http):
        """反向：不传 userId 应该报错"""
        chat = ChatApi(admin_http)
        resp = chat.http.request("POST", "/chat/session", json={})
        assert resp.json().get("code") != 0, "不传 userId 居然创建成功了？"

    def test_list_sessions(self, admin_http, my_user_id):
        """正向：查询会话列表"""
        chat = ChatApi(admin_http)
        # 先建两个会话
        s1 = chat.create_session(my_user_id, title="列表测试1").json()["data"]["id"]
        s2 = chat.create_session(my_user_id, title="列表测试2").json()["data"]["id"]
        try:
            resp = chat.list_sessions(my_user_id)
            AssertUtil.assert_success(resp.json())
            assert isinstance(resp.json()["data"], list), "会话列表应该是数组"
        finally:
            chat.delete_session(s1)
            chat.delete_session(s2)

    def test_rename_session(self, admin_http, my_user_id):
        """正向：重命名会话"""
        chat = ChatApi(admin_http)
        sid = chat.create_session(my_user_id, title="原名").json()["data"]["id"]
        try:
            new_title = f"新名字_{fake.uuid4()[:6]}"
            resp = chat.rename_session(sid, my_user_id, new_title)
            AssertUtil.assert_success(resp.json())
            assert resp.json()["data"]["title"] == new_title, "重命名后标题没改过来"
        finally:
            chat.delete_session(sid)

    def test_reset_session(self, admin_http, my_user_id):
        """正向：重置会话（清空上下文）"""
        chat = ChatApi(admin_http)
        sid = chat.create_session(my_user_id).json()["data"]["id"]
        try:
            resp = chat.reset_session(sid)
            AssertUtil.assert_success(resp.json())
        finally:
            chat.delete_session(sid)

    def test_messages_of_not_exist_session(self, admin_http):
        """反向：查询不存在会话的历史消息"""
        chat = ChatApi(admin_http)
        resp = chat.get_messages(999999999)
        assert resp.json().get("code") != 0, "不存在的会话居然返回消息了？"

    def test_session_without_token(self, cfg):
        """反向：未登录不能操作会话"""
        from common.request_util import HttpRequest
        chat = ChatApi(HttpRequest(cfg["base_url"]))
        resp = chat.list_sessions(user_id=1)
        assert resp.status_code in (401, 403), f"未登录应被拒绝，实际 {resp.status_code}"
