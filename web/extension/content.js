// Nexus Web Ingest — 直接 POST 到 localhost，不经过 background
const SITES = {'doubao.com':'豆包','tongyi.aliyun.com':'通义','chat.openai.com':'ChatGPT','chatgpt.com':'ChatGPT','douyin.com':'抖音'};
const host = location.hostname.replace('www.','');
const SITE = Object.entries(SITES).find(([k])=>host.includes(k))?.[1];
if(!SITE) return;

let last='';
setInterval(()=>{
  const t = document.body.innerText?.slice(0,5000)||'';
  if(t.length > last.length + 100){
    fetch('http://localhost:8765/ingest',{method:'POST',body:JSON.stringify({text:t,source:SITE})});
    last=t;
  }
},5000);

chrome.runtime.onMessage.addListener((msg,s,r)=>{if(msg.action==='capture'){const t=document.body.innerText?.slice(0,5000)||'';fetch('http://localhost:8765/ingest',{method:'POST',body:JSON.stringify({text:t,source:SITE})});r('OK');}});