# Nexus — Agent 中枢记忆系统

任何 Agent 的记忆、知识、技能、路由统一由 Nexus 调度。

## 快速开始

```bash
git clone --recurse-submodules git@github.com:Ask-Pillar/nexus.git
cd nexus
pip install -e .
python3 -c "from nexus.core import NexusCore; print(NexusCore().stats())"
```

## 架构

```
任何 Agent → MCP → Nexus Core
  ├── sisyphus/    记忆中枢 (Episodic)
  ├── knowledge/   知识中枢 (Semantic)
  └── procedural/  能力中枢 (Procedural, 规划中)
```

## MCP 工具 (16 个)

| 工具 | 功能 |
|------|------|
| search_memory | 检索记忆 |
| write_memory | 记录记忆 |
| get_context | 编译上下文（Agent 直接使用） |
| ingest_text | 接收外部文本自动存储 |
| rate_memory / dismiss_memory | 反馈闭环 |
| + sisyphus 原有 12 个工具 |

## 自我学习系统

Nexus 长期观察接入的 Agent 的执行模式，提取为可复用的内部技能：

- **技能蒸馏**：观察 Agent 高频任务 → 提取流程 → 内化为 Procedural 规则
- **持续演进**：Agent 版本更新 → 自动对比评估 → 选择性采纳新能力
- **多 Agent 协同**：从多个 Agent 的独立执行中学习最优路径

## 知识层

| 来源 | 接入方式 |
|------|----------|
| Obsidian vault | 自动索引 FTS5 |
| 本地文档 (PDF/Word/Excel/图片) | 分批导入，支持中断续传 |
| 浏览器插件 | Web Ingest HTTP 端点 |
| 外部知识库 | ModuleProtocol 接口 |

## 项目结构

```
nexus/
├── sisyphus/              ← git submodule，记忆引擎
├── nexus/
│   ├── core.py            ← 调度层
│   ├── protocol.py        ← 模块协议
│   └── knowledge/         ← 知识层
├── server/mcp.py          ← MCP Server
├── web/ingest.py          ← Web Ingest
├── config/nexus.yaml
└── tests/
```

## 测试

412/412 全部通过 (408 sisyphus + 4 nexus)。
