# -*- coding: utf-8 -*-
"""
认证相关接口封装
对应 AuthController: /auth/**
"""
from common.request_util import HttpRequest


class AuthApi:
    def __init__(self, http: HttpRequest):
        self.http = http

    def login(self, username: str, password: str):
        """POST /auth/login  用户名密码登录，返回 {code, msg, data:{token, userInfo}}"""
        return self.http.request(
            "POST", "/auth/login",
            json={"username": username, "password": password}
        )

    def register(self, username: str, password: str, nickname: str = None, email: str = None):
        """POST /auth/register  注册新用户"""
        body = {"username": username, "password": password}
        if nickname:
            body["nickname"] = nickname
        if email:
            body["email"] = email
        return self.http.request("POST", "/auth/register", json=body)

    def me(self):
        """GET /auth/me  需要 token，返回当前登录用户信息"""
        return self.http.request("GET", "/auth/me")

    def logout(self):
        """POST /auth/logout  登出，token 加入黑名单"""
        return self.http.request("POST", "/auth/logout")

    def change_password(self, old_password: str, new_password: str):
        """PUT /auth/password  修改密码"""
        return self.http.request(
            "PUT", "/auth/password",
            params={"oldPassword": old_password, "newPassword": new_password}
        )
