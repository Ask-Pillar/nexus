#!/usr/bin/env python3
"""零操作: 监控剪贴板，检测到 AI 对话内容自动发 Nexus"""
import subprocess, json, urllib.request, time

last = ""
while True:
    text = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout.strip()
    if text and len(text) > 50 and text != last:
        # 检测是否是 AI 对话（含常见标记）
        ai_markers = ["豆包", "通义", "ChatGPT", "AI助手", "assistant", "bot:", "AI:"]
        is_ai = any(m in text[:200] for m in ai_markers)
        source = next((m for m in ai_markers if m in text[:200]), "clipboard")
        if is_ai:
            data = json.dumps({"text": text[:5000], "source": source}).encode()
            try:
                req = urllib.request.Request("http://localhost:8765/ingest", data=data,
                                             headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=3)
                print(f"[{time.strftime('%H:%M:%S')}] ingested from {source}")
            except Exception as e:
                print(f"error: {e}")
        last = text
    time.sleep(2)
