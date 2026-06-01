"""Agent Registry — 管理所有接入 Agent 的画像和观察数据."""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict


AGENT_PROFILES = {
    "hermes": {
        "type": "agent",
        "interface": "mcp",
        "skills": ["security_audit", "code_review", "skill_creation", "self_learning"],
        "strengths": ["Python", "Go", "Docker", "K8s"],
        "description": "Nous Research 的自学习 Agent，擅长安全审计和技能自动创建",
        "version": "latest",
    },
    "openclaw": {
        "type": "agent",
        "interface": "gateway",
        "skills": ["message_routing", "multi_platform", "agent_orchestration"],
        "strengths": ["Telegram", "Discord", "Slack", "WhatsApp"],
        "description": "多平台消息网关，支持 Agent 编排",
        "version": "v2026.5.28",
    },
    "qoder": {
        "type": "agent",
        "interface": "mcp",
        "skills": ["code_review", "ci_cd", "subagent_delegation"],
        "strengths": ["GitHub Actions", "PR Review", "CI Pipeline"],
        "description": "GitHub CI/CD Agent，支持子 Agent 和 MCP",
        "version": "latest",
    },
    "claude_code": {
        "type": "agent",
        "interface": "mcp",
        "skills": ["code_generation", "context_management", "project_awareness"],
        "strengths": ["TypeScript", "Python", "React"],
        "description": "Anthropic 的编码 Agent，AGENTS.md 上下文模式",
        "version": "latest",
    },
    "codex": {
        "type": "agent",
        "interface": "api",
        "skills": ["code_generation", "automation", "skill_execution"],
        "strengths": ["multi_language", "enterprise", "automation"],
        "description": "OpenAI 的编码 Agent，Skills + Automations",
        "version": "latest",
    },
}


class AgentRegistry:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path or Path.home() / ".omo" / "nexus" / "agents.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                task TEXT NOT NULL,
                tool_used TEXT,
                success INTEGER DEFAULT 1,
                duration_ms INTEGER,
                quality_score REAL,
                observed_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                description TEXT,
                frequency INTEGER DEFAULT 1,
                confidence REAL DEFAULT 0.5,
                extracted_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def register_agent(self, name, profile=None):
        """Register a new agent or update profile."""
        profile = profile or AGENT_PROFILES.get(name, {})
        return profile

    def log_call(self, agent, task, tool_used=None, success=True, duration_ms=0, quality_score=None):
        """Log an agent call for observation."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO agent_calls VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
            (agent, task, tool_used, 1 if success else 0, duration_ms, quality_score, _now()),
        )
        conn.commit()
        conn.close()

    def log_pattern(self, agent, pattern_type, description, confidence=0.5):
        """Log a discovered pattern for distillation."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO agent_patterns VALUES (NULL, ?, ?, ?, 1, ?, ?)",
            (agent, pattern_type, description, confidence, _now()),
        )
        conn.commit()
        conn.close()

    def get_call_stats(self, agent=None, days=30):
        """Get call statistics for an agent."""
        conn = sqlite3.connect(str(self.db_path))
        query = "SELECT agent, COUNT(*) as calls, AVG(duration_ms) as avg_ms, AVG(quality_score) as avg_quality FROM agent_calls WHERE observed_at > ?"
        params = [_days_ago(days)]
        if agent:
            query += " AND agent = ?"
            params.append(agent)
        query += " GROUP BY agent"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [{"agent": r[0], "calls": r[1], "avg_ms": r[2], "avg_quality": r[3]} for r in rows]

    def get_patterns(self, agent=None, min_confidence=0.5):
        """Get extracted patterns ready for distillation."""
        conn = sqlite3.connect(str(self.db_path))
        query = "SELECT agent, pattern_type, description, frequency, confidence FROM agent_patterns WHERE confidence >= ?"
        params = [min_confidence]
        if agent:
            query += " AND agent = ?"
            params.append(agent)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [{"agent": r[0], "type": r[1], "description": r[2], "frequency": r[3], "confidence": r[4]} for r in rows]

    def list_agents(self):
        return {name: profile for name, profile in AGENT_PROFILES.items()}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _days_ago(days):
    from datetime import timedelta
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
