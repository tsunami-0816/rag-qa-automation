# -*- coding: utf-8 -*-
"""
文档管理接口封装
对应 DocumentController: /api/document/**
"""
import os
from common.request_util import HttpRequest


class DocumentApi:
    def __init__(self, http: HttpRequest):
        self.http = http

    def upload(self, file_path: str, knowledge_base_id: int, overwrite: bool = False):
        """
        POST /api/document/upload  上传文档
        :param file_path: 本地文件路径
        :param knowledge_base_id: 知识库ID
        :param overwrite: 是否覆盖同MD5文档
        """
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            files = {"file": (filename, f, "application/octet-stream")}
            data = {
                "knowledgeBaseId": str(knowledge_base_id),
                "overwrite": str(overwrite).lower()
            }
            return self.http.request(
                "POST", "/api/document/upload",
                files=files, data=data
            )

    def download(self, document_id: int):
        """GET /api/document/{id}/download  下载原始文件"""
        return self.http.request("GET", f"/api/document/{document_id}/download")

    def upload_text_content(self, content: str, filename: str, knowledge_base_id: int, overwrite: bool = False):
        """辅助方法：直接把字符串内容当文件上传，不用提前造文件"""
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            return self.upload(tmp_path, knowledge_base_id, overwrite=overwrite)
        finally:
            os.unlink(tmp_path)
