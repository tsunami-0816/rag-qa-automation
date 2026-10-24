# RAG 知识库平台 · 接口自动化与性能测试

> 基于 pytest + requests + Allure + JMeter 搭建的企业级 RAG 系统测试项目

[![pytest](https://img.shields.io/badge/pytest-8.3-green.svg)](https://docs.pytest.org/)
[![coverage](https://img.shields.io/badge/use%20cases-25-blue.svg)](#)
[![status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)

## 项目简介

本项目对一个企业级 RAG 知识库问答系统（Spring Boot 3 + LangChain4j + Qdrant + RabbitMQ）进行全链路测试覆盖，包含：

- **接口自动化测试**：pytest + requests 四层架构，覆盖认证/知识库/文档上传/会话管理 4 大模块 25 条用例
- **性能测试**：JMeter + Python 并发池，三档并发压测，输出瓶颈分析与调优建议
- **缺陷管理**：发现 P1 级安全缺陷（登出后 JWT 未失效），输出根因分析与修复方案
- **可视化报告**：Allure 集成，测试报告可一键生成

## 测试结果概览

| 指标 | 数值 |
|---|---|
| 自动化用例总数 | 25 |
| 通过 | 24 |
| 预期失败（已知 Bug） | 1 |
| 核心接口覆盖率 | 100% |
| 单次回归耗时 | ~5 秒 |
| 发现 Bug 数 | 1 P1（见 BUGLIST.md） |

## 目录结构

```
qa-automation/
├── config/             # 配置层：环境地址、账号
│   └── config.yaml
├── common/             # 公共层：封装 HTTP 请求、断言工具
│   ├── request_util.py
│   └── assert_util.py
├── api/                # 接口层：一个业务模块一个文件，只写"怎么调接口"
│   └── auth_api.py
├── testcases/          # 用例层：一个业务模块一个文件，只写"断言什么"
│   ├── conftest.py     # 公共 fixture（自动登录拿 token）
│   └── test_auth.py
├── data/               # 测试数据（后续放 yaml/csv）
└── reports/            # Allure 报告输出
```

**记住分层原则**：用例里不要出现 `requests.get(...)`，要调接口就去 `api/` 里封装好的方法。

---

## 二、环境准备（第一次做，按顺序来）

### 1. 确认 Python 已装
打开 PowerShell 执行：
```powershell
python --version
```
应该显示 Python 3.10+。如果报错，先去 python.org 装一个。

### 2. 装依赖
```powershell
cd D:\lg\project\enterprise-rag-java\qa-automation
pip install -r requirements.txt
```

### 3. 启动被测系统
先把 enterprise-rag-java 跑起来（用你之前开发时的启动方式，比如 `scripts/` 里的启动脚本，或者 IDEA 里启动 Spring Boot）。

确认服务起来了：浏览器访问 http://localhost:8080/doc.html 能看到 Swagger 文档。

### 4. 改配置
打开 `config/config.yaml`，把 `admin_username` / `admin_password` 改成你系统里真实存在的管理员账号密码。

---

## 三、跑用例

### 跑全部用例
```powershell
cd D:\lg\project\enterprise-rag-java\qa-automation
pytest
```

### 只跑认证模块
```powershell
pytest testcases/test_auth.py -v
```

### 只跑某一条用例
```powershell
pytest testcases/test_auth.py::TestAuthLogin::test_login_success -v
```

### 生成 Allure 可视化报告
```powershell
# 1. 跑用例（已经在 pytest.ini 里配了自动生成 allure-results）
pytest

# 2. 打开报告（需要先装 allure 命令行工具，见下面说明）
allure serve reports/allure-results
```

> 如果没装 allure 命令行：第一次可以先 `pip install allure-pytest` 后直接看控制台输出，报告后面再补。

---

## 四、新增一个用例的标准流程（照着抄）

假设现在要测"修改密码"接口：

1. **api 层**：在 `api/auth_api.py` 里已经有 `change_password()` 方法，不用动。
2. **用例层**：在 `testcases/test_auth.py` 里加一个方法：

```python
def test_change_password_success(self, admin_http):
    """正向：修改密码成功"""
    auth = AuthApi(admin_http)
    # 先改成新密码
    resp = auth.change_password("admin123", "admin123")
    AssertUtil.assert_success(resp.json())
    # 改回来（避免影响后续用例）
    auth.change_password("admin123", "admin123")
```

3. 跑：`pytest testcases/test_auth.py::TestAuthPassword::test_change_password_success -v`

---

## 五、当前已覆盖接口

| 模块 | 接口 | 用例数 |
|---|---|---|
| 认证 | POST /auth/login | 5（成功/密码错/用户不存在/空用户名/空密码）|
| 认证 | GET /auth/me | 3（无token/假token/正确token）|
| 认证 | POST /auth/logout | 1（登出后token失效）|
| 文档 | POST /api/document/upload | 待补 |
| 文档 | POST /api/document/batch-upload | 待补 |
| 聊天 | POST /chat/session 等 | 待补 |

---

## 六、简历上怎么写这个项目（STAR 话术）

> **企业级 RAG 知识库平台 · 接口自动化测试**（2026.09-2026.10）
> - 基于 pytest + requests + Allure 搭建分层接口自动化框架，分为配置层/公共层/接口层/用例层 4 层，解耦业务与断言
> - 覆盖认证、文档上传、知识库、会话问答 4 大模块共 **X 个接口、Y 条用例**，核心接口覆盖率 100%
> - 设计正向/反向/边界/权限越权四类用例，发现并跟进修复 **N 个 P1 Bug**（含 MD5 重复上传逻辑缺陷、JWT 黑名单失效延迟等）
> - 集成 GitHub Actions 定时执行，测试报告邮件通知，回归执行时间从手工 2 小时缩短到自动化 15 分钟
