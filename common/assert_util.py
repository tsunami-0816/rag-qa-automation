# -*- coding: utf-8 -*-
"""
断言封装层
- 统一处理 Result 结构 {code, msg, data}
- 成功码是 0（不是 200）
"""


class AssertUtil:
    @staticmethod
    def assert_success(resp_json: dict, msg: str = ""):
        """断言接口返回成功（code == 0）"""
        assert resp_json.get("code") == 0, \
            f"期望 code=0，实际 code={resp_json.get('code')}，msg={resp_json.get('msg')} {msg}"

    @staticmethod
    def assert_code(resp_json: dict, expected_code: int, msg: str = ""):
        """断言业务码等于期望值"""
        assert resp_json.get("code") == expected_code, \
            f"期望 code={expected_code}，实际 code={resp_json.get('code')}，msg={resp_json.get('msg')} {msg}"

    @staticmethod
    def assert_data_has_keys(resp_json: dict, keys: list):
        """断言返回的 data 里包含指定字段"""
        data = resp_json.get("data") or {}
        for k in keys:
            assert k in data, f"data 里缺少字段 {k}，实际 data={data}"

    @staticmethod
    def assert_http_status(resp, expected_status: int = 200):
        """断言 HTTP 状态码"""
        assert resp.status_code == expected_status, \
            f"期望 HTTP {expected_status}，实际 {resp.status_code}，body={resp.text[:200]}"
