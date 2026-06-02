// Nexus Web Ingest — content script
// 检测 AI 对话页面，自动采集对话内容

const SITES = {
  'douyin.com': { selector: '[data-e2e="chat-message"]', name: '豆包' },
  'doubao.com': { selector: '[class*="message"]', name: '豆包' },
  'tongyi.aliyun.com': { selector: '[class*="chat-item"]', name: '通义' },
  'chat.openai.com': { selector: '[data-message-author-role]', name: 'ChatGPT' },
  'chatgpt.com': { selector: '[data-message-author-role]', name: 'ChatGPT' },
};

const host = location.hostname.replace('www.', '');
const site = Object.entries(SITES).find(([k]) => host.includes(k));
if (!site) return;

const SITE_NAME = site[1].name;

// 监听页面变化，检测新对话
let lastCount = 0;

setInterval(() => {
  const messages = document.querySelectorAll(site[1].selector);
  if (messages.length > lastCount && messages.length > 2) {
    const text = Array.from(messages).map(m => m.textContent?.trim() || '').join('\n').slice(0, 5000);
    chrome.runtime.sendMessage({ action: 'ingest', text, source: SITE_NAME });
    lastCount = messages.length;
  }
}, 5000);
