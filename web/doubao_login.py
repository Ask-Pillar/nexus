#!/usr/bin/env python3
"""一次性豆包登录 → 保存登录态"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

STATE = Path.home() / ".omo" / "nexus" / "playwright_data" / "state.json"
STATE.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(STATE.parent), headless=False)
    page = ctx.new_page()
    page.goto("https://www.doubao.com/chat/")
    print("浏览器已打开，请登录豆包，30秒后自动保存...")
    time.sleep(30)
    ctx.storage_state(path=str(STATE))
    ctx.close()
    print(f"登录态已保存 → {STATE}")
