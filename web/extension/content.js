// Nexus Web Ingest — content script
// 自动 + 手动采集 AI 对话内容

const SITES = {
  'douyin.com': { selector: '[data-e2e="chat-message"]', name: '豆包' },
  'doubao.com': { selector: '[class*="message"], [class*="chat"]', name: '豆包' },
  'tongyi.aliyun.com': { selector: '[class*="chat-item"], [class*="message"]', name: '通义' },
  'chat.openai.com': { selector: '[data-message-author-role]', name: 'ChatGPT' },
  'chatgpt.com': { selector: '[data-message-author-role]', name: 'ChatGPT' },
};

const host = location.hostname.replace('www.', '');
const site = Object.entries(SITES).find(([k]) => host.includes(k));
if (!site) return;
const SITE_NAME = site[1].name;

// 暴露手动采集函数，popup 可以调用
window.__nexus_capture = function() {
  const allText = document.body.innerText?.slice(0, 5000) || '';
  chrome.runtime.sendMessage({ action: 'ingest', text: allText, source: SITE_NAME });
  return '已采集 ' + allText.length + ' 字符 → Nexus';
};

// 自动检测（兜底）
let lastCount = 0;
setInterval(() => {
  const messages = document.querySelectorAll(site[1].selector);
  if (!messages.length) return; // 选择器不匹配，等手动
  if (messages.length > lastCount && messages.length > 2) {
    const text = Array.from(messages).map(m => m.textContent?.trim() || '').join('\n').slice(0, 5000);
    chrome.runtime.sendMessage({ action: 'ingest', text, source: SITE_NAME });
    lastCount = messages.length;
  }
}, 5000);
