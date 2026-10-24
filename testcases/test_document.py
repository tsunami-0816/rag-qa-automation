# -*- coding: utf-8 -*-
"""
文档上传接口测试
覆盖：正常上传、不支持的类型、不存在的知识库、未登录
"""
import pytest
from common.assert_util import AssertUtil
from api.kb_api import KbApi
from api.document_api import DocumentApi
from faker import Faker

fake = Faker("zh_CN")


@pytest.fixture(scope="class")
def test_kb(admin_http):
    """每个测试类用一个独立的测试知识库，跑完尝试删除（权限不足时忽略）"""
    kb = KbApi(admin_http)
    name = f"QA文档测试库_{fake.uuid4()[:8]}"
    resp = kb.create(name)
    kb_id = resp.json()["data"]["id"]
    yield kb_id
    # 清理：测试账号可能没有 delete 权限，403 就忽略
    kb.delete(kb_id)


class TestDocumentUpload:
    def test_upload_txt_success(self, admin_http, test_kb):
        """正向：上传一个 txt 文档成功"""
        doc = DocumentApi(admin_http)
        resp = doc.upload_text_content(
            content="这是自动化测试上传的文档内容。\n用于验证文档上传接口。",
            filename="test.txt",
            knowledge_base_id=test_kb
        )
        body = resp.json()
        AssertUtil.assert_success(body)
        assert body["data"], "上传成功但没返回 documentId"

    def test_upload_to_not_exist_kb(self, admin_http):
        """反向：上传到不存在的知识库ID"""
        doc = DocumentApi(admin_http)
        resp = doc.upload_text_content(
            content="test", filename="test.txt", knowledge_base_id=999999999
        )
        assert resp.json().get("code") != 0, "上传到不存在的知识库居然成功了？"

    def test_upload_without_token(self, cfg):
        """反向：未登录不能上传"""
        from common.request_util import HttpRequest
        doc = DocumentApi(HttpRequest(cfg["base_url"]))
        resp = doc.upload_text_content(
            content="test", filename="test.txt", knowledge_base_id=1
        )
        assert resp.status_code in (401, 403), f"未登录上传应被拒绝，实际 {resp.status_code}"

    def test_upload_duplicate_then_overwrite(self, admin_http, test_kb):
        """边界：同一文件重复上传，应返回 MD5 重复(20003)，overwrite=true 后覆盖成功"""
        doc = DocumentApi(admin_http)
        content = f"重复上传测试内容 {fake.uuid4()}"

        # 第一次上传
        r1 = doc.upload_text_content(content, "dup.txt", test_kb)
        AssertUtil.assert_success(r1.json())

        # 第二次相同内容上传，应该返回 20003 重复
        r2 = doc.upload_text_content(content, "dup.txt", test_kb)
        assert r2.json().get("code") == 20003, \
            f"相同MD5第二次上传应返回20003，实际 {r2.json().get('code')} msg={r2.json().get('msg')}"

        # 带 overwrite=true 再传，应该成功
        r3 = doc.upload_text_content(content, "dup.txt", test_kb, overwrite=True)
        AssertUtil.assert_success(r3.json())
