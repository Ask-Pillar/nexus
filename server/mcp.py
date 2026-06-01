"""Nexus MCP Server — extends sisyphus MCP with get_context + ingest_text"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sisyphus" / "src"))

from sisyphus.server.mcp import TOOLS as SISYPHUS_TOOLS, HANDLERS as SISYPHUS_HANDLERS, _setup, _send, _store

from nexus.core import NexusCore

core = NexusCore()

# ── new tools ──

def _handle_get_context(args: Dict[str, Any]) -> Dict[str, Any]:
    return {"context": core.get_context(args["query"], args.get("max_chars", 3000))}


def _handle_ingest_text(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args["text"]
    source = args.get("source", "web")
    core.write(
        title=f"Ingested from {source}", content=text, mem_type="note",
        tags=["ingest", source],
    )
    return {"status": "ok", "source": source}


# ── extend tools + handlers ──

TOOLS = {
    **SISYPHUS_TOOLS,
    "get_context": {
        "description": "获取编译后的记忆上下文（Agent 直接用）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_chars": {"type": "integer", "default": 3000},
            },
            "required": ["query"],
        },
    },
    "ingest_text": {
        "description": "接收外部文本，自动提取并存储",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "source": {"type": "string"},
            },
            "required": ["text"],
        },
    },
}

HANDLERS = {
    **SISYPHUS_HANDLERS,
    "get_context": _handle_get_context,
    "ingest_text": _handle_ingest_text,
}


def main():
    _setup()
    for line in sys.stdin:
        try:
            msg = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        req_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {}) or {}

        if method == "tools/list":
            _send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": [{"name": k, **v} for k, v in TOOLS.items()]}})
        elif method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments", {})
            handler = HANDLERS.get(name)
            if handler:
                try:
                    result = handler(args)
                    _send({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}})
                except Exception as e:
                    _send({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}})
            else:
                _send({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {name}"}})


if __name__ == "__main__":
    main()
