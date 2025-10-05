# astroatlas_clean_en.py
import webview
from string import Template

CROP_PX  = 0
ZOOM_PCT = 105
RA, DEC, FOV = 56.75, 24.12, 2.0
BACKGROUND = "PanSTARRS"

HTML_TMPL = Template("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AstroAtlas</title>
<style>
  html,body{margin:0;height:100%;background:#000;overflow:hidden}
  #stage{position:fixed; inset:0; overflow:hidden; background:#000}
  #wwtFrame{
    position:absolute; top:0; left:0;
    width: calc(100vw + ${CROP_PX}px);
    height: 100vh;
    transform: translateX(${CROP_PX}px);
    border:0;
    z-index: 0;
  }
  .title{
    position:fixed; top:10px; left:50%; transform:translateX(-50%);
    padding:6px 12px; border-radius:10px; background:rgba(0,0,0,.55);
    color:#eee; font:700 16px system-ui; letter-spacing:.5px; z-index:10; pointer-events:none;
  }
  .obj-panel{
    position:fixed; top:16px; right:16px;
    width: 300px; max-height: 82vh; overflow:auto;
    padding:12px; border-radius:12px;
    background:rgba(0,0,0,.55); backdrop-filter: blur(4px);
    box-shadow: 0 6px 20px rgba(0,0,0,.3);
    z-index:11; color:#e8e8e8; font:500 13px system-ui;
  }
  .obj-panel h3{ margin:0 0 8px; font:700 14px/1.2 system-ui; color:#fff; letter-spacing:.3px; }
  .obj-btn{
    width:100%; text-align:left;
    padding:10px 12px; margin:8px 0;
    border-radius:10px; border:1px solid rgba(255,255,255,.15);
    background:rgba(255,255,255,.06); color:#eee; font:600 13px system-ui;
    cursor:pointer; transition: background .15s ease, transform .06s ease;
  }
  .obj-btn:hover{ background:rgba(255,255,255,.12); }
  .obj-btn:active{ transform: translateY(1px); }
  .tooltip{
    position:fixed; max-width:360px; padding:10px 12px; border-radius:12px;
    background:rgba(15,15,20,.94); color:#dcdcdc; font:500 12.5px/1.4 system-ui; z-index:9999;
    border:1px solid rgba(255,255,255,.12); box-shadow:0 8px 20px rgba(0,0,0,.35);
    pointer-events:none; opacity:0; transform: translateY(4px); transition: .12s opacity,.12s transform;
  }
  .tooltip.show{ opacity:1; transform: translateY(0); }
  .tooltip b{ color:#fff; }
  .tooltip .muted{ color:#aeb0b6; }
</style>
</head>
<body>
  <div class="title">AstroAtlas</div>

  <div id="stage">
    <iframe id="wwtFrame" src="https://web.wwtassets.org/research/latest/" allowfullscreen></iframe>
  </div>

  <div id="panel" class="obj-panel">
    <h3>Objects</h3>
    <div id="objList"></div>
  </div>

  <div id="tooltip" class="tooltip" role="tooltip"></div>

<script>
  document.addEventListener('DOMContentLoaded', ()=>{ document.body.style.zoom = '${ZOOM_PCT}%'; });

  const OBJECTS = [
    {
      name: 'Sun',
      scriptURL: 'https://web.wwtassets.org/research/latest/?script=eyJldmVudCI6ImNlbnRlcl9vbl9jb29yZGluYXRlcyIsInJhIjoxOTEuODY3ODY2NTAwNDA5MywiZGVjIjotNS4wNTYxMzg4NjkyMzc2NzgsImZvdiI6MC44Nzc5ODQ0NDY3MjEyMTU4LCJyb2xsIjowLCJpbnN0YW50Ijp0cnVlfQ%3D%3D%2CeyJldmVudCI6InNldF9iYWNrZ3JvdW5kX2J5X25hbWUiLCJuYW1lIjoiRGlnaXRpemVkIFNreSBTdXJ2ZXkgKENvbG9yKSJ9',
      infoHTML: `<b>Sun</b><br><span class="muted">Known:</span> since prehistoric times.<br><span class="muted">Missions:</span> Parker Solar Probe (since 2018).<br><span class="muted">Size:</span> diameter ≈ <b>1,392,700 km</b>.`
    },
    {
      name: 'Moon',
      scriptURL: 'https://web.wwtassets.org/research/latest/?script=eyJldmVudCI6ImNlbnRlcl9vbl9jb29yZGluYXRlcyIsInJhIjozNTUuMzg1ODcwMzA4NjY5NDQsImRlYyI6LTIuMTE1MTY1NzQ3NDgwNTk3LCJmb3YiOjAuNzk4MTY3Njc4ODM3NDY5MSwicm9sbCI6MCwiaW5zdGFudCI6dHJ1ZX0%3D%2CeyJldmVudCI6InNldF9iYWNrZ3JvdW5kX2J5X25hbWUiLCJuYW1lIjoiRGlnaXRpemVkIFNreSBTdXJ2ZXkgKENvbG9yKSJ9#',
      infoHTML: `<b>Moon</b><br><span class="muted">Known:</span> since prehistoric times.<br><span class="muted">Missions:</span> Apollo 8 (1968) — 17 (1972).<br><span class="muted">Size:</span> diameter ≈ <b>3,474.8 km</b>.`
    },
    {
      name: 'Pleiades (Seven Sisters)',
      scriptURL: 'https://web.wwtassets.org/research/latest/?script=eyJldmVudCI6ImNlbnRlcl9vbl9jb29yZGluYXRlcyIsInJhIjo1Ni42MDI2NDU4NjYxNTMxMDQsImRlYyI6MjQuMjQxNDU0NzEwNTMyOTEzLCJmb3YiOjIuNTE4MDM0ODAxNTQ3ODQ1NSwicm9sbCI6MCwiaW5zdGFudCI6dHJ1ZX0%3D%2CeyJldmVudCI6InNldF9iYWNrZ3JvdW5kX2J5X25hbWUiLCJuYW1lIjoiRGlnaXRpemVkIFNreSBTdXJ2ZXkgKENvbG9yKSJ9#',
      infoHTML: `<b>Pleiades</b> in the constellation <b>Taurus</b>.<br><span class="muted">Known:</span> since prehistoric times.<br><span class="muted">Apparent size:</span> ≈ <b>~1.8°</b>; <span class="muted">physical size:</span> ≈ <b>~17 ly</b>.`
    }
  ];

  const list = document.getElementById('objList');
  const tip  = document.getElementById('tooltip');

  function btnTemplate(obj){
    const btn=document.createElement('button');
    btn.className='obj-btn'; btn.textContent=obj.name;
    btn.addEventListener('mouseenter',e=>{ tip.innerHTML=obj.infoHTML; tip.classList.add('show'); moveTooltip(e); });
    btn.addEventListener('mousemove', moveTooltip);
    btn.addEventListener('mouseleave', ()=> tip.classList.remove('show'));
    btn.addEventListener('click', ()=> gotoByScript(obj.scriptURL));
    return btn;
  }
  OBJECTS.forEach(o=> list.appendChild(btnTemplate(o)));

  function moveTooltip(ev){
    const pad=10; let x=ev.clientX+pad, y=ev.clientY+pad;
    const w=tip.offsetWidth, h=tip.offsetHeight;
    if(x+w>innerWidth-8) x=innerWidth-w-8;
    if(y+h>innerHeight-8) y=innerHeight-h-8;
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }

  const frame  = document.getElementById("wwtFrame");
  const APP_ORIGIN = "https://web.wwtassets.org";
  const postRaw = (msg)=> frame.contentWindow.postMessage(msg, APP_ORIGIN);
  let wwtReady=false; const queue=[];
  function post(msg){ if(wwtReady) postRaw(msg); else queue.push(msg); }

  function gotoByScript(url){
    wwtReady=false; queue.length=0;
    frame.src = url;
    onceFrameLoaded(()=>{
      startHandshake(()=>{
        hideChromeSoft();
      });
    });
  }

  function hideChromeSoft(){
    [100, 400, 900].forEach(d => setTimeout(()=> post({
      event:"modify_settings", target:"app",
      settings:[{ name:"hide_all_chrome", value:true }]
    }), d));
  }

  let pingToken = Math.random().toString(36).slice(2);
  function sendPing(){ postRaw({ event:"ping_pong", token: pingToken }); }
  window.addEventListener('message', (ev)=>{
    if(ev.origin!==APP_ORIGIN || !ev.data) return;
    if(ev.data.event==='ping_pong' && ev.data.token===pingToken){
      wwtReady=true;
      while(queue.length) postRaw(queue.shift());
    }
  });

  onceFrameLoaded(()=>{
    startHandshake(()=>{
      post({ event:"set_background_by_name", name: "${BACKGROUND}" });
      post({ event:"center_on_coordinates", ra:${RA}, dec:${DEC}, fov:${FOV}, instant:true });
      hideChromeSoft();
    });
  });

  function onceFrameLoaded(cb){
    if(frame.contentWindow && frame.contentDocument ? frame.contentDocument.readyState==='complete' : false){
      setTimeout(cb, 0);
    } else {
      frame.addEventListener('load', function onl(){ frame.removeEventListener('load', onl); setTimeout(cb, 50); });
    }
  }
  function startHandshake(cb){
    const t1 = setInterval(()=>{ if(wwtReady){ clearInterval(t1); return; } sendPing(); }, 200);
    const t2 = setInterval(()=>{ if(!wwtReady) return; clearInterval(t2); cb&&cb(); }, 100);
  }
</script>
</body>
</html>
""")

HTML = HTML_TMPL.substitute(
    CROP_PX=CROP_PX,
    ZOOM_PCT=ZOOM_PCT,
    BACKGROUND=BACKGROUND,
    RA=RA,
    DEC=DEC,
    FOV=FOV
)

if __name__ == "__main__":
    webview.create_window("AstroAtlas", html=HTML, width=1280, height=800, resizable=True)
    webview.start(debug=False)
