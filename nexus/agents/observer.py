"""Agent Observer — 观察接入 Agent 的执行，提取模式用于蒸馏."""

from nexus.agents.registry import AgentRegistry

_registry = AgentRegistry()


def observe(agent, task, tool_used=None, success=True, duration_ms=0, quality_score=None):
    """Log an agent execution for later pattern extraction."""
    _registry.log_call(agent, task, tool_used, success, duration_ms, quality_score)


def register_pattern(agent, pattern_type, description, confidence=0.5):
    """Register a discovered pattern."""
    _registry.log_pattern(agent, pattern_type, description, confidence)


def get_learnings(min_confidence=0.7):
    """Get patterns ready for distillation into internal skills."""
    return _registry.get_patterns(min_confidence=min_confidence)


def agent_stats(agent=None):
    """Get agent performance statistics."""
    return _registry.get_call_stats(agent)


def list_agents():
    """List all registered agents."""
    return _registry.list_agents()
