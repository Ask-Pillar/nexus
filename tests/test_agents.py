"""Tests for agent registry and adapters."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sisyphus" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nexus.agents.registry import AgentRegistry, AGENT_PROFILES
from nexus.agents import observer
from nexus.external import hermes, openclaw, qoder, codex


class TestAgentRegistry:
    def test_list_agents(self):
        profiles = AGENT_PROFILES
        assert "hermes" in profiles
        assert "openclaw" in profiles
        assert "qoder" in profiles
        assert "claude_code" in profiles
        assert "codex" in profiles

    def test_log_and_retrieve(self, tmp_path):
        reg = AgentRegistry(tmp_path / "test.db")
        reg.log_call("hermes", "security_audit", "bandit", True, 1500, 0.9)
        reg.log_call("hermes", "code_review", None, True, 800, 0.85)
        stats = reg.get_call_stats("hermes")
        assert len(stats) == 1
        assert stats[0]["calls"] == 2

    def test_patterns(self, tmp_path):
        reg = AgentRegistry(tmp_path / "test.db")
        reg.log_pattern("hermes", "skill", "安全审计 5 步流程", 0.9)
        patterns = reg.get_patterns("hermes", min_confidence=0.5)
        assert len(patterns) == 1


class TestAgentAdapters:
    def test_hermes_study(self):
        hermes.study_hermes_skills()
        patterns = observer.get_learnings()
        assert len(patterns) >= 1

    def test_hermes_audit(self, tmp_path):
        code_dir = tmp_path / "src"
        code_dir.mkdir()
        (code_dir / "test.py").write_text("import os\nos.system('ls')")
        result = hermes.hermes_security_audit(str(code_dir))
        assert isinstance(result, list)

    def test_openclaw_study(self):
        openclaw.study_openclaw_gateway()
        patterns = observer.get_learnings()
        assert any(p["agent"] == "openclaw" for p in patterns)

    def test_qoder_study(self):
        qoder.study_qoder_patterns()
        patterns = observer.get_learnings()
        assert any(p["agent"] == "qoder" for p in patterns)

    def test_codex_study(self):
        codex.study_codex_patterns()
        patterns = observer.get_learnings()
        assert any(p["agent"] == "codex" for p in patterns)
