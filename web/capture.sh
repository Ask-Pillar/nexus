#!/bin/bash
# 快捷键脚本 — 抓取 Chrome 当前页面文字 → Nexus
# 绑定: 系统设置 → 键盘 → 快捷键 → 添加 → 选此脚本 → 绑定 Cmd+Shift+N

PAGE_TEXT=$(osascript -l JavaScript -e '
var chrome = Application("Google Chrome");
var tab = chrome.windows[0].activeTab();
tab.execute({javascript: "document.body.innerText.slice(0,5000)"});
' 2>/dev/null)

if [ -n "$PAGE_TEXT" ]; then
  HOST=$(osascript -l JavaScript -e '
    var chrome = Application("Google Chrome");
    chrome.windows[0].activeTab().url().split("/")[2].replace("www.","");
  ' 2>/dev/null)
  
  curl -s -X POST http://localhost:8765/ingest \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "import json; print(json.dumps({'text':'$PAGE_TEXT','source':'${HOST:-chrome}'}))")"
  
  osascript -e 'display notification "已发送到 Nexus" with title "Nexus Ingest"'
fi
