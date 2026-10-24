# -*- coding: utf-8 -*-
"""
知识库管理接口测试
覆盖：创建/重复名校验/分页/详情/删除
"""
import pytest
from common.assert_util import AssertUtil
from api.kb_api import KbApi
from faker import Faker

fake = Faker("zh_CN")


class TestKnowledgeBaseCRUD:
    def test_create_kb_success(self, admin_http):
        """正向：创建知识库成功"""
        kb = KbApi(admin_http)
        name = f"QA测试库_{fake.uuid4()[:8]}"
        resp = kb.create(name, description="自动化测试用知识库")
        AssertUtil.assert_success(resp.json())
        kb_id = resp.json()["data"]["id"]
        # 用完删掉，不污染环境
        kb.delete(kb_id)

    def test_create_kb_duplicate_name(self, admin_http):
        """反向：重复名称创建应报错"""
        kb = KbApi(admin_http)
        name = f"QA重名库_{fake.uuid4()[:8]}"
        r1 = kb.create(name)
        AssertUtil.assert_success(r1.json())
        kb_id = r1.json()["data"]["id"]
        try:
            r2 = kb.create(name)
            assert r2.json().get("code") != 0, "重名居然创建成功了？"
        finally:
            kb.delete(kb_id)

    def test_page_kb(self, admin_http):
        """正向：分页查询知识库列表"""
        kb = KbApi(admin_http)
        resp = kb.page(page_num=1, page_size=5)
        AssertUtil.assert_success(resp.json())
        data = resp.json()["data"]
        assert "list" in data or "total" in data, f"分页返回结构异常: {data}"

    def test_get_kb_not_found(self, admin_http):
        """反向：查询不存在的知识库ID"""
        kb = KbApi(admin_http)
        resp = kb.get_detail(999999999)
        assert resp.json().get("code") != 0, "不存在的知识库居然返回成功了？"

    def test_create_kb_without_token(self, cfg):
        """反向：未登录不能创建知识库"""
        from common.request_util import HttpRequest
        kb = KbApi(HttpRequest(cfg["base_url"]))
        resp = kb.create("should_not_create")
        assert resp.status_code in (401, 403), f"未登录创建应被拒绝，实际 {resp.status_code}"
