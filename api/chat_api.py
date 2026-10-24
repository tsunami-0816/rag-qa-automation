# -*- coding: utf-8 -*-
"""
聊天会话管理接口封装
对应 ChatController: /chat/session/**
注意：流式问答 /chat/stream 是 SSE 接口，这里不测（留给 JMeter 压测）
"""
from common.request_util import HttpRequest


class ChatApi:
    def __init__(self, http: HttpRequest):
        self.http = http

    def create_session(self, user_id: int, title: str = None, knowledge_base_id: int = None):
        """POST /chat/session  创建会话"""
        body = {"userId": user_id}
        if title:
            body["title"] = title
        if knowledge_base_id:
            body["knowledgeBaseId"] = knowledge_base_id
        return self.http.request("POST", "/chat/session", json=body)

    def list_sessions(self, user_id: int, knowledge_base_id: int = None):
        """GET /chat/session/list  会话列表"""
        params = {"userId": user_id}
        if knowledge_base_id:
            params["knowledgeBaseId"] = knowledge_base_id
        return self.http.request("GET", "/chat/session/list", params=params)

    def get_messages(self, session_id: int):
        """GET /chat/session/{id}/messages  历史消息"""
        return self.http.request("GET", f"/chat/session/{session_id}/messages")

    def delete_session(self, session_id: int):
        """DELETE /chat/session/{id}  删除会话"""
        return self.http.request("DELETE", f"/chat/session/{session_id}")

    def reset_session(self, session_id: int):
        """POST /chat/session/{id}/reset  重置会话（清空上下文）"""
        return self.http.request("POST", f"/chat/session/{session_id}/reset")

    def rename_session(self, session_id: int, user_id: int, title: str):
        """PUT /chat/session/{id}  重命名"""
        return self.http.request(
            "PUT", f"/chat/session/{session_id}",
            params={"userId": user_id, "title": title}
        )
