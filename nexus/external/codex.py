"""Codex API Adapter — OpenAI 编码 Agent，观察 Skills + Automations."""

from nexus.agents.observer import observe, register_pattern

CODEX_PATTERNS = {
    "skills": "Skills 超越代码生成 → 文档、原型、测试 → 符合团队标准",
    "automations": "无人值守：issue triage、告警监控、CI/CD → Agent 自主执行",
    "mcp_design": "MCP 工具设计：代码生成/理解/审查/调试/自动化 五大能力",
}


def study_codex_patterns():
    """提取 Codex 的企业级 Agent 模式."""
    for name, desc in CODEX_PATTERNS.items():
        register_pattern("codex", "enterprise_pattern", f"{name}: {desc}", confidence=0.85)
