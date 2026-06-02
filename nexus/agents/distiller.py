"""Agent Distiller — 从观察模式中蒸馏内部技能."""

from pathlib import Path
from datetime import datetime, timezone
from nexus.agents.observer import get_learnings, agent_stats


class AgentDistiller:
    """将 Agent 观察模式蒸馏为 Nexus internal 技能."""

    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir or Path.home() / ".omo" / "nexus" / "skills")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def distill(self, min_confidence=0.75, min_calls=3):
        """蒸馏：高置信度模式 → internal 技能文件.

        Args:
            min_confidence: 最低置信度阈值
            min_calls: 最少调用次数

        Returns:
            蒸馏结果统计
        """
        patterns = get_learnings(min_confidence)
        stats = {s["agent"]: s for s in agent_stats()}

        distilled = []
        skipped_low_calls = []
        skipped_low_confidence = []

        for pattern in patterns:
            agent = pattern["agent"]
            agent_stat = stats.get(agent, {})
            calls = agent_stat.get("calls", 0)

            if calls < min_calls:
                skipped_low_calls.append(pattern)
                continue

            if pattern["confidence"] < min_confidence:
                skipped_low_confidence.append(pattern)
                continue

            skill_file = self._generate_skill(pattern, calls)
            distilled.append(skill_file)

        return {
            "distilled": len(distilled),
            "files": distilled,
            "skipped_low_calls": len(skipped_low_calls),
            "skipped_low_confidence": len(skipped_low_confidence),
        }

    def _generate_skill(self, pattern, calls):
        """生成 internal 技能文件."""
        agent = pattern["agent"]
        skill_name = pattern["description"].split(":")[0].strip().replace(" ", "_").lower()[:30]
        skill_type = pattern["type"]
        description = pattern["description"]
        confidence = pattern["confidence"]
        frequency = pattern.get("frequency", 1)

        skill_md = f"""---
name: {skill_name}
version: "1.0"
description: "{description}"
agent: {agent}
type: {skill_type}
confidence: {confidence:.2f}
calls_observed: {calls}
distilled_at: {_now()}
---

# {skill_name}

**来源 Agent**: {agent}
**观察次数**: {calls}
**置信度**: {confidence:.1%}
**技能类型**: {skill_type}

## 描述

{description}

## 蒸馏说明

此技能从 {agent} 的 {calls} 次执行中提取，置信度 {confidence:.1%}。
Nexus 应在类似场景自动加载此技能。
"""
        filename = f"{agent}_{skill_name}.md"
        filepath = self.output_dir / filename
        filepath.write_text(skill_md)
        return str(filepath)


def _now():
    return datetime.now(timezone.utc).isoformat()
