# Doubao 采集标准流程 (已验证)

## 原理

Playwright MCP 打开独立浏览器 → 登录态已保存（首次运行 doubao_login.py）→ 直接读取页面 → 存入 Nexus

## 执行

### 一次性：登录

```bash
cd nexus && python3 web/doubao_login.py
# 浏览器打开 → 登录豆包 → 等 30 秒自动保存
```

### 每次采集

```
1. skill_mcp playwright browser_navigate → https://www.doubao.com/chat/
2. skill_mcp playwright browser_evaluate → document.body.innerText → 确认已登录（含 "landon"）
3. 提取所有对话标题 → 筛选未采集的 → 逐个 browser_click → browser_evaluate → bash 写入 Nexus Core
4. 重复直到全部采完
```

### 写入命令

```bash
cd nexus && python3 -c "
import sys; sys.path.insert(0, 'sisyphus/src'); sys.path.insert(0, '.')
from nexus.core import NexusCore
NexusCore().write(title='豆包: {标题}', content='{内容}', mem_type='note', tags=['doubao'])
"
```

## 踩过的坑

| ❌ | 为什么失败 |
|----|-----------|
| Chrome CDP | 需开发模式 + user-data-dir冲突 |
| headless 自动 | 登录态不持久 |
| 浏览器插件 | 无法注入/选择器不匹配 |
| AppleScript | Chrome权限未开 |
| 剪贴板 | 输出缓冲问题 |

## ✅ 唯一可行

Playwright MCP（非 headless）→ 直接读 DOM → 绕过所有权限和安全限制
