"""OpenClaw Gateway Bridge — 多平台消息路由接入."""

from nexus.agents.observer import observe, register_pattern

GATEWAY_PATTERNS = {
    "session_isolation": "per-message sender attribution，多人在同一群聊中区分发言人",
    "platform_routing": "Telegram/Discord/Slack/WhatsApp/Signal 统一消息格式 → 路由到 Agent",
    "dm_pairing": "私聊配对，确保消息来源可信",
}


def study_openclaw_gateway():
    """提取 OpenClaw 的网关模式."""
    for name, desc in GATEWAY_PATTERNS.items():
        register_pattern("openclaw", "gateway_pattern", f"{name}: {desc}", confidence=0.9)


def openclaw_route_message(message, platform="telegram"):
    """模拟 OpenClaw 的多平台消息路由."""
    observe("openclaw", "route_message", f"platform:{platform}")
    return {"routed_to": "mcp_agent", "message": message, "platform": platform}
