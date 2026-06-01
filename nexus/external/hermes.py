"""Hermes Agent Adapter — 技能系统 + 安全审计模式."""

from nexus.agents.observer import observe, register_pattern

SKILL_PATTERNS = {
    "security_audit": {
        "steps": [
            "AST 扫描 → 检测 subprocess/eval/exec",
            "OWASP Top 10 → SQL注入/XSS/CSRF",
            "依赖漏洞 → 第三方库版本检查",
            "网络请求 → 外部 API 调用审计",
            "生成报告 → Markdown 按风险排序",
        ],
        "tools": ["bandit", "trivy"],
        "success_pattern": "先工具扫描 → 再人工审查 high risk → 最后生成报告",
    },
    "code_review": {
        "steps": [
            "读取变更文件 → 理解上下文",
            "检查命名规范 → 函数/变量命名",
            "检查逻辑错误 → 边界条件、空值",
            "检查性能 → 不必要的循环/IO",
            "生成 Review 评论",
        ],
        "tools": [],
        "success_pattern": "逐文件检查 → 分类标注 → 给出具体建议",
    },
}

# Hermes 特有的安全机制值得学习
SECURITY_PATTERNS = {
    "file_locking": "fcntl/msvcrt 文件锁防止多进程写冲突",
    "injection_scan": "写入前扫描 prompt injection/exfiltration 模式",
    "prompt_cache": "冻结快照模式：session 内不变，保留 Anthropic prefix cache",
    "one_provider": "最多一个外部 memory provider，防止 tool schema 膨胀",
}


def study_hermes_skills():
    """提取 Hermes 的技能创建模式供 Nexus 学习."""
    for skill_name, skill in SKILL_PATTERNS.items():
        # 注册为可观察模式
        steps_text = " → ".join(skill["steps"])
        description = f"技能: {skill_name} | 流程: {steps_text} | 工具: {','.join(skill['tools'])}"
        register_pattern("hermes", "skill_workflow", description, confidence=0.9)

    for pattern_name, description in SECURITY_PATTERNS.items():
        register_pattern("hermes", "security_pattern", f"{pattern_name}: {description}", confidence=0.85)


def hermes_security_audit(code_path):
    """模拟 Hermes 的安全审计流程（实际执行时调 CLI 工具）."""
    import subprocess

    results = []
    observe("hermes", "security_audit", "bandit")

    try:
        bandit_result = subprocess.run(
            ["bandit", "-r", code_path, "-f", "json"],
            capture_output=True, text=True, timeout=60,
        )
        if bandit_result.returncode == 0:
            results.append({"tool": "bandit", "output": bandit_result.stdout[:1000]})
    except Exception:
        pass

    register_pattern("hermes", "tool_usage", "bandit + trivy 组合审计", confidence=0.8)
    return results
