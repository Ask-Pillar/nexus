// 页面加载立即抓，之后每 5 秒检测
(function(){
  const h=location.hostname.replace('www.','');
  const push=t=>fetch('http://localhost:8765/ingest',{method:'POST',body:JSON.stringify({text:t,source:h})}).catch(()=>{});
  let last=document.body.innerText?.slice(0,5000)||''; push(last);
  setInterval(()=>{
    const n=document.body.innerText?.slice(0,5000)||'';
    if(n.length>last.length+100){push(n);last=n;}
  },5000);
})();
