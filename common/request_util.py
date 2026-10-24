# -*- coding: utf-8 -*-
"""
HTTP 请求封装层
- 自动拼接 base_url
- 自动带 JWT token
- 打印请求/响应日志，方便定位问题
"""
import os
import json
import requests
import yaml


class HttpRequest:
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.token = token

    def set_token(self, token: str):
        """登录成功后调用，把 token 存起来，后续请求自动带上"""
        self.token = token

    def _headers(self, extra_headers: dict = None):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _url(self, path: str):
        return f"{self.base_url}{path}"

    def request(self, method: str, path: str, **kwargs):
        url = self._url(path)
        headers = self._headers(kwargs.pop("headers", None))
        # 文件上传时不要强制 JSON
        if kwargs.get("files"):
            headers.pop("Content-Type", None)

        print(f"\n>>> [{method}] {url}")
        if kwargs.get("params"):
            print(f"    params: {kwargs['params']}")
        if kwargs.get("json"):
            print(f"    body: {json.dumps(kwargs['json'], ensure_ascii=False)}")
        if kwargs.get("data"):
            print(f"    form: {kwargs['data']}")

        resp = self.session.request(method, url, headers=headers, timeout=30, **kwargs)

        print(f"<<< [{resp.status_code}] {url}")
        try:
            print(f"    resp: {json.dumps(resp.json(), ensure_ascii=False)[:500]}")
        except Exception:
            print(f"    resp(text): {resp.text[:500]}")
        return resp


def load_config(env: str = None) -> dict:
    """读取 config/config.yaml，返回当前环境的配置字典"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    env = env or cfg.get("env", "test")
    return cfg[env]
