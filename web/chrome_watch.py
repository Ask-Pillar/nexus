#!/usr/bin/env python3
"""Zero-touch Chrome monitor via macOS Accessibility API. No extension needed."""
import json, time, sys, urllib.request
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID

last = {}
while True:
    for w in CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID):
        owner = w.get('kCGWindowOwnerName', '')
        name = w.get('kCGWindowName', '')
        if owner != 'Google Chrome' or not name or len(name) < 5: continue
        host = 'doubao.com' if 'doubao' in name.lower() else 'tongyi.aliyun.com' if 'tongyi' in name.lower() else 'chatgpt.com' if 'chatgpt' in name.lower() or 'openai' in name.lower() else 'unknown'
        if len(name) > last.get(host, '') + 50:
            data = json.dumps({"text": name[:5000], "source": host}).encode()
            try: urllib.request.urlopen(urllib.request.Request("http://localhost:8765/ingest", data=data), timeout=3)
            except: pass
            last[host] = name
            print(f"[{time.strftime('%H:%M:%S')}] {host}")
    time.sleep(3)
