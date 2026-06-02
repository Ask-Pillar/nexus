#!/usr/bin/env python3
"""Doubao 自动采集 - 每30分钟抓新对话 → Nexus | 异常通知 macOS"""
import json, time, sqlite3, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sisyphus" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from playwright.sync_api import sync_playwright

DOUBAO = "https://www.doubao.com/chat/"
STATEDB = Path.home() / ".omo" / "nexus" / "doubao_state.db"
INTERVAL = 1800

def notify(title, msg):
    subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "{title}"'], capture_output=True)

def init_db():
    STATEDB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(STATEDB))
    c.execute("CREATE TABLE IF NOT EXISTS seen (title TEXT PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT)")
    c.commit(); c.close()

def seen(title):
    c = sqlite3.connect(str(STATEDB)); r = c.execute("SELECT 1 FROM seen WHERE title=?", (title,)).fetchone(); c.close(); return bool(r)

def mark(title):
    c = sqlite3.connect(str(STATEDB)); c.execute("INSERT OR REPLACE INTO seen VALUES (?)", (title,)); c.commit(); c.close()

def save(title, content):
    from nexus.core import NexusCore
    NexusCore().write(title=f"豆包: {title}", content=content[:2000], mem_type="note", tags=["doubao","auto"])

def run():
    collected, errors = 0, 0
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(DOUBAO, wait_until="networkidle", timeout=30000)
            time.sleep(3)
            text = page.evaluate("document.body.innerText").strip()
        except Exception as e:
            notify("采集失败", f"doubao.com 不可达: {e}"); return

        if "登录" in text[:300] and "你好" not in text[:200]:
            notify("采集失败", "豆包未登录"); browser.close(); return

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        collecting = False
        for line in lines:
            if collecting and len(line) > 1 and line not in ("新对话","更多","快速","帮我写作","编程","AI 创作","云盘","图像生成","PPT 生成"):
                if seen(line) or len(line) < 2: continue
                try:
                    page.locator(f"text={line}").first.click(timeout=5000)
                    time.sleep(2)
                    conv = page.evaluate("document.body.innerText").strip()
                    save(line, conv[:2000]); mark(line); collected += 1
                except: errors += 1; continue
            if line == "历史对话": collecting = True
        browser.close()
    if collected: notify("采集完成", f"+{collected} 条豆包对话")
    print(f"[{time.strftime('%H:%M:%S')}] +{collected} err={errors}")

if __name__ == "__main__":
    init_db()
    run()
