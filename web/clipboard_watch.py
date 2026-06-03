#!/usr/bin/env python3
"""零操作: 监控剪贴板 → 直接写 Nexus Core（不依赖 HTTP）"""
import subprocess, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sisyphus" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nexus.core import NexusCore

core = NexusCore()
ai_markers = ["豆包", "通义", "ChatGPT", "AI助手", "assistant", "bot:", "AI:"]
last = ""

while True:
    text = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout.strip()
    if text and len(text) > 50 and text != last:
        is_ai = any(m in text[:200] for m in ai_markers)
        source = next((m for m in ai_markers if m in text[:200]), "clipboard")
        if is_ai:
            core.write(title=f"Ingested from {source}", content=text[:2000],
                       mem_type="note", tags=["clipboard", source])
            print(f"[{time.strftime('%H:%M:%S')}] ingested from {source}", flush=True)
        last = text
    time.sleep(2)
