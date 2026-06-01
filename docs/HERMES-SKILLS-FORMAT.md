# Hermes Skills 格式（采纳为 Nexus Procedural 层标准）

## 格式

```markdown
---
name: code_security_audit
version: "1.0"
description: "对代码进行安全审计，检查 SQL 注入、XSS、CSRF 等常见漏洞"
triggers:
  - "审计代码"
  - "安全检查"
  - "漏洞扫描"
tools:
  - bandit
  - trivy
steps:
  1: "AST 扫描 → 检测 subprocess / eval / exec 调用"
  2: "OWASP Top 10 检查 → SQL 注入 / XSS / CSRF / SSRF"
  3: "依赖漏洞 → bandit + trivy 组合"
  4: "网络请求 → 检测所有外部 API 调用"
  5: "生成报告 → 标注风险等级 (high/medium/low)"
distilled_from: hermes
confidence: 0.94
---

## 执行步骤

1. 先用 bandit 扫描 Python 代码中的安全漏洞
2. 再用 trivy 检查容器镜像和依赖
3. 人工审查所有标记为 high risk 的发现
4. 生成 Markdown 报告，按风险等级排序
```

## 匹配规则

Triggers 匹配用户输入的关键词。命中后加载完整 skill。

## 蒸馏标记

`distilled_from` 记录技能来源。Nexus 可追溯所有 internal 技能的原始 Agent。
