# Nexus — Agent 中枢记忆系统

任何 Agent 的记忆、知识、技能、路由都走 Nexus。

## 快速开始

```bash
git clone --recurse-submodules https://github.com/your/nexus.git
cd nexus
pip install -e .
python3 -c "from nexus.core import NexusCore; print(NexusCore().stats())"
```

## 架构

```
任何 Agent → MCP → Nexus Core → sisyphus (记忆) + Obsidian (知识) + procedural (技能)
```

## MCP 工具

| 工具 | 功能 |
|------|------|
| search_memory | 检索记忆 |
| write_memory | 记录记忆 |
| get_context | 编译上下文（Agent 直接用） |
| ingest_text | 接收外部文本自动存储 |
| + sisyphus 原有 14 个工具 |

## Web Ingest

```bash
python3 web/ingest.py          # 启动 localhost:8765
curl -X POST localhost:8765/ingest -d '{"text":"hello","source":"test"}'
```

## 配置

`config/nexus.yaml`

## 文档

- `docs/HERMES-SKILLS-FORMAT.md` — 技能格式
- sisyphus/docs/ — 所有 sisyphus 文档
