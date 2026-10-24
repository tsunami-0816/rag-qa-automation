# -*- coding: utf-8 -*-
"""
知识库管理接口封装
对应 AdminKnowledgeBaseController: /api/admin/knowledge-base/**
"""
from common.request_util import HttpRequest


class KbApi:
    def __init__(self, http: HttpRequest):
        self.http = http

    def create(self, name: str, description: str = None):
        """POST /api/admin/knowledge-base  创建知识库"""
        body = {"name": name}
        if description:
            body["description"] = description
        return self.http.request("POST", "/api/admin/knowledge-base", json=body)

    def delete(self, kb_id: int):
        """DELETE /api/admin/knowledge-base/{id}  删除知识库"""
        return self.http.request("DELETE", f"/api/admin/knowledge-base/{kb_id}")

    def get_detail(self, kb_id: int):
        """GET /api/admin/knowledge-base/{id}  知识库详情"""
        return self.http.request("GET", f"/api/admin/knowledge-base/{kb_id}")

    def page(self, name: str = None, page_num: int = 1, page_size: int = 10):
        """GET /api/admin/knowledge-base  分页列表"""
        params = {"pageNum": page_num, "pageSize": page_size}
        if name:
            params["name"] = name
        return self.http.request("GET", "/api/admin/knowledge-base", params=params)
