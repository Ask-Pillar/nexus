"""Claude Code Adapter — 上下文管理模式 + AGENTS.md 项目感知."""

from nexus.agents.observer import observe, register_pattern

CONTEXT_PATTERNS = {
    "agents_md": "AGENTS.md 文件注入项目上下文：架构、规范、工具链 → Agent 启动时自动加载",
    "memory_md": "MEMORY.md 持久偏好：简洁回答、技术栈偏好、常用路径 → 跨 session",
    "now_md": ".remember/now.md 工作记忆：当前任务上下文，session 结束丢弃",
    "wiki": "~/.wiki 跨项目知识库：可查询的技术文档 → 语义检索层",
    "project_context": "自动检测 cwd + git remote → 加载对应的项目 AGENTS.md",
}


def study_claude_patterns():
    """提取 Claude Code 的上下文管理模式."""
    for name, desc in CONTEXT_PATTERNS.items():
        register_pattern("claude_code", "context_pattern", f"{name}: {desc}", confidence=0.9)
