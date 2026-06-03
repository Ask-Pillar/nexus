#!/usr/bin/env python3
"""Doubao 自动采集 - 直接读 DOM 获取对话链接, 逐个提取内容 → Nexus"""
import json, time, sqlite3, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sisyphus" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from playwright.sync_api import sync_playwright

DOUBAO = "https://www.doubao.com/chat/"
STATEDB = Path.home() / ".omo" / "nexus" / "doubao_state.db"
INTERVAL = 21600

def notify(title, msg):
    subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "{title}"'], capture_output=True)

def init_db():
    STATEDB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(STATEDB))
    c.execute("CREATE TABLE IF NOT EXISTS seen (url TEXT PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT)")
    c.commit(); c.close()

def seen(url): 
    c = sqlite3.connect(str(STATEDB)); r = c.execute("SELECT 1 FROM seen WHERE url=?", (url,)).fetchone(); c.close(); return bool(r)
def mark(url): 
    c = sqlite3.connect(str(STATEDB)); c.execute("INSERT OR REPLACE INTO seen VALUES (?)", (url,)); c.commit(); c.close()

def save(title, content):
    from nexus.core import NexusCore
    NexusCore().write(title=f"豆包: {title}", content=content[:2000], mem_type="note", tags=["doubao","auto"])

def run():
    collected, errors = 0, 0
    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(
                str(Path.home() / ".omo" / "nexus" / "playwright_data"), headless=True)
            page = ctx.new_page()
            page.goto(DOUBAO, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
        except Exception as e:
            notify("采集失败", str(e)); return

        text = page.evaluate("document.body.innerText").strip()
        if "登录" in text[:300] and "landon" not in text:
            notify("采集失败", "豆包未登录"); ctx.close(); return

        # 提取所有对话链接
        links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a[href*="/chat/"]'))
                .filter(a => a.textContent.trim().length > 2)
                .map(a => ({title: a.textContent.trim().slice(0, 60), url: a.href}));
        }""")

        for link in links[:10]:  # 每次最多取10条
            if seen(link["url"]): continue
            try:
                page.goto(link["url"], wait_until="domcontentloaded", timeout=15000)
                time.sleep(3)
                conv = page.evaluate("document.body.innerText").strip()
                save(link["title"], conv[:2000])
                mark(link["url"])
                collected += 1
            except: errors += 1

        ctx.close()
    if collected: notify("采集完成", f"+{collected} 条")
    print(f"[{time.strftime('%H:%M:%S')}] +{collected} err={errors}")

if __name__ == "__main__":
    init_db()
    run()
