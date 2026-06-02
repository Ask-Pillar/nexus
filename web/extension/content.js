// Nexus Web Ingest — 自动检测 body 文本变化
const SITES = {'doubao.com':'豆包','tongyi.aliyun.com':'通义','chat.openai.com':'ChatGPT','chatgpt.com':'ChatGPT','douyin.com':'抖音'};
const host = location.hostname.replace('www.','');
const SITE = Object.entries(SITES).find(([k])=>host.includes(k))?.[1];
if(!SITE) return;

let last='';
setInterval(()=>{
  const t = document.body.innerText?.slice(0,5000)||'';
  if(t.length > last.length + 100){chrome.runtime.sendMessage({action:'ingest',text:t,source:SITE});last=t;}
},5000);
