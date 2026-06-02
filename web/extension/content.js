// 全自动 — 任何页面文本变化 >100 字就推送到 Nexus
let last='', host=location.hostname.replace('www.','');
setInterval(()=>{
  const t=document.body.innerText?.slice(0,5000)||'';
  if(t.length>last.length+100){
    fetch('http://localhost:8765/ingest',{method:'POST',body:JSON.stringify({text:t,source:host})}).catch(()=>{});
    last=t;
  }
},5000);
