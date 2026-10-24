# 测试发现 Bug 清单

> 这份清单是简历"项目经历"里的核心素材：自动化测试跑出来的真实问题，带根因分析和修复建议。
> 格式：每发现一个新 Bug 就追加一条，跑回归时关掉状态。

---

## BUG-001 · 登出后 JWT Token 未实际失效（P1 安全）

| 项 | 内容 |
|---|---|
| 发现日期 | 2026-10-24 |
| 发现方式 | 接口自动化用例 `test_logout_then_token_invalid` |
| 严重级别 | **P1（安全漏洞）** |
| 模块 | 认证 / JWT 黑名单 |

### 复现步骤
1. 调用 `POST /auth/register` 注册新用户
2. 调用 `POST /auth/login` 登录拿到 token
3. 带 token 调 `GET /auth/me` → 200 正常
4. 带 token 调 `POST /auth/logout` → 返回 `{"code":0,"msg":"操作成功"}`
5. 再次带同一个 token 调 `GET /auth/me` → **仍然 200，返回完整用户信息**

### 预期结果
第 5 步应该返回 401/403，token 已被加入黑名单。

### 实际结果
第 5 步仍能正常访问，登出形同虚设。

### 根因定位
`TokenBlacklistService.java` 第 70-75 行：
```java
try {
    stringRedisTemplate.opsForValue().set(key, "1", Duration.ofMillis(tokenExpirationMs));
} catch (Exception e) {
    log.warn("[Token黑名单] 写入 Redis 失败(不影响登出响应): {}", e.getMessage());
    // ← 问题：catch 后不抛异常，登出接口返回成功，但 Redis 里根本没写进去
}
```
同理，`isBlacklisted()` 查询失败时也降级为 `return false`（第 91-94 行），即使 Redis 真挂了也不会拦截请求。

### 影响范围
- 用户主动登出后，原 token 在有效期内（默认 24h）仍可使用
- 多端登录场景下，用户以为"退出登录"了，但 token 还在裸奔
- 改密码后的全量失效逻辑（`invalidateAllUserTokens`）有同样问题

### 修复建议
1. Redis 写入失败时应抛异常，让登出接口返回 500，而不是假装成功
2. `isBlacklisted()` 查询失败时应 fail-closed（拒绝请求），而不是 fail-open（放行）
3. 增加监控：黑名单写入失败率 > 0 时告警

### 状态
- [ ] 已提交开发修复
- [ ] 已回归验证
- [x] 自动化用例已标记 `xfail`，跟踪修复后自动转 PASS

---

## 待补充

（后续跑文档上传、聊天会话模块时，发现新 Bug 继续往下追加）
