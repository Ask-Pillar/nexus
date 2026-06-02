#!/usr/bin/env python3
"""Playwright auto-collect Doubao conversations → Nexus"""
import json, time, urllib.request
from playwright.sync_api import sync_playwright

def capture(page):
    text = page.evaluate("document.body.innerText") or ""
    text = text[:5000]
    if not text.strip(): return
    data = json.dumps({"text": text, "source": "doubao-playwright"}).encode()
    try:
        urllib.request.urlopen(urllib.request.Request(
            "http://localhost:8765/ingest", data=data,
            headers={"Content-Type": "application/json"}), timeout=3)
    except: pass

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.doubao.com/chat/")
    print("浏览器已打开 doubao.com — 请登录")
    time.sleep(10)
    for _ in range(120):  # 10 min
        capture(page)
        time.sleep(5)
    browser.close()
