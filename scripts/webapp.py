#!/usr/bin/env python3
"""Front-end for the CareerOPS web app. Holds APP_HTML, served by serve_dashboard.py.

Fully client-rendered: fetches /api/state, writes through the POST endpoints in
serve_dashboard.py. No build step, no external libraries. Loading splash, light/dark
themes, confetti, a networking CRM, an interview round logger, settings, and keyboard
shortcuts are all in here.
"""

APP_HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CareerOPS</title>
<style>
:root{--bg:#efe9dc;--surface:#fbf7ed;--surface2:#f4eee0;--text:#0c0c0c;--muted:#6b6357;
--line:#ddd3c2;--green:#2e6b3e;--amber:#a16207;--red:#9c2f2f;--blue:#2b4a73;--radius:14px;
--shadow:0 1px 3px rgba(0,0,0,.06);}
[data-theme="dark"]{--bg:#16140e;--surface:#211e16;--surface2:#2b271f;--text:#f1ebda;
--muted:#a59c89;--line:#3a352b;--green:#5bbf76;--amber:#d99a2b;--red:#e0736b;--blue:#6fa8e0;
--shadow:0 1px 4px rgba(0,0,0,.4);}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.45;transition:background .35s,color .35s}
.serif{font-family:"Iowan Old Style","Charter",Georgia,serif}
.mono{font-family:ui-monospace,"SF Mono",Menlo,monospace}
.muted{color:var(--muted);font-size:12px}
a{color:var(--blue)}
/* splash */
#splash{position:fixed;inset:0;z-index:200;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;transition:opacity .5s}
#splash.hide{opacity:0;pointer-events:none}
.splash-logo{font-family:"Iowan Old Style",Georgia,serif;font-size:42px;font-weight:700;letter-spacing:.5px;background:linear-gradient(90deg,var(--green),var(--blue));-webkit-background-clip:text;background-clip:text;color:transparent;animation:pop .6s ease}
.splash-sub{color:var(--muted);font-size:13px;letter-spacing:3px;text-transform:uppercase}
.spinner{width:34px;height:34px;border:3px solid var(--line);border-top-color:var(--green);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes pop{0%{transform:scale(.8);opacity:0}100%{transform:scale(1);opacity:1}}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
/* top bar */
.topbar{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--surface) 92%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.topinner{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:16px;padding:11px 20px}
.brand{font-family:"Iowan Old Style",Georgia,serif;font-size:20px;font-weight:700;letter-spacing:.3px;cursor:default;background:linear-gradient(90deg,var(--green),var(--blue));-webkit-background-clip:text;background-clip:text;color:transparent}
.nav{display:flex;gap:3px;flex:1;flex-wrap:wrap}
.tab{font-size:13px;padding:7px 12px;border-radius:9px;cursor:pointer;color:var(--muted);border:1px solid transparent;user-select:none;transition:background .15s}
.tab:hover{background:var(--surface2)}
.tab.active{background:var(--text);color:var(--surface)}
.tab .k{font-size:9px;opacity:.5;margin-left:4px}
.chip{font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px;white-space:nowrap}
.led{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 0 0 var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--green) 60%,transparent)}70%{box-shadow:0 0 0 6px transparent}100%{box-shadow:0 0 0 0 transparent}}
.iconbtn{cursor:pointer;border:1px solid var(--line);background:var(--surface);border-radius:9px;padding:6px 9px;font-size:14px;line-height:1}
.iconbtn:hover{background:var(--surface2)}
.wrap{max-width:1180px;margin:0 auto;padding:22px 20px 90px}
.view{animation:fade .28s ease}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px;margin-bottom:16px;box-shadow:var(--shadow)}
h2.sec{font-size:12px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin:0 0 12px;display:flex;justify-content:space-between;align-items:center;gap:8px}
.row{display:flex;gap:16px;flex-wrap:wrap}
.banner{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.banner .t{font-family:"Iowan Old Style",Georgia,serif;font-size:18px}
.btn{font-size:13px;padding:7px 13px;border-radius:9px;border:1px solid var(--line);background:var(--surface);cursor:pointer;font-family:inherit;color:var(--text);transition:transform .08s,background .15s}
.btn:hover{background:var(--surface2)}.btn:active{transform:scale(.96)}
.btn.primary{background:var(--green);color:#fff;border-color:var(--green)}
.btn.danger{color:var(--red);border-color:color-mix(in srgb,var(--red) 40%,var(--line))}
.btn.sm{padding:4px 9px;font-size:12px}
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:14px;text-align:center;box-shadow:var(--shadow);transition:transform .15s}
.stat:hover{transform:translateY(-2px)}
.stat .n{font-size:30px;font-family:"Iowan Old Style",Georgia,serif}
.stat .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}
.ring{--p:0;width:62px;height:62px;border-radius:50%;margin:0 auto 6px;background:conic-gradient(var(--green) calc(var(--p)*1%),var(--surface2) 0);display:flex;align-items:center;justify-content:center;transition:--p .6s}
.ring span{width:48px;height:48px;border-radius:50%;background:var(--surface);display:flex;align-items:center;justify-content:center;font-size:14px;font-family:"Iowan Old Style",Georgia,serif}
.pipe-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.pipe{text-align:center;padding:8px}.pipe .n{font-size:26px;font-family:"Iowan Old Style",Georgia,serif}
.pipe .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}
.qrow{display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid var(--line)}
.qrow:last-child{border-bottom:none}
.qrow.applied{opacity:.55}.qrow.applied .qrole{text-decoration:line-through}
.logo{width:36px;height:36px;border-radius:9px;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex:0 0 auto}
.qmeta{flex:1;min-width:0}.qrole{font-size:14px;font-weight:600}.qsub{font-size:12px;color:var(--muted)}
.reason{font-size:11px;color:var(--muted);font-style:italic;margin-top:2px}
.pill{color:#fff;font-size:11px;padding:3px 9px;border-radius:20px;text-transform:capitalize}
.conf{font-size:10px;font-weight:700;padding:1px 6px;border-radius:5px;margin-right:6px;color:#fff}
.conf.yes{background:var(--green)}.conf.no{background:var(--red)}.conf.unk{background:var(--amber)}
.reslinks{margin-top:5px;display:flex;flex-wrap:wrap;gap:6px}
.res{font-size:10px;color:var(--blue);text-decoration:none;border:1px solid var(--line);padding:1px 6px;border-radius:5px}
.res:hover{background:var(--surface2)}
.linkbtn{font-size:13px;text-decoration:none;border:1px solid var(--line);padding:6px 11px;border-radius:8px;color:var(--blue);white-space:nowrap}
.kanban{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;align-items:start}
.kcol{background:var(--surface2);border:1px solid var(--line);border-radius:var(--radius);padding:10px;min-height:80px}
.kcol h3{font-size:12px;margin:0 0 8px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);display:flex;justify-content:space-between}
.kcard{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:9px;margin-bottom:8px;box-shadow:var(--shadow);animation:fade .3s}
.kcard .c{font-weight:600;font-size:13px}.kcard .r{font-size:11px;color:var(--muted)}
.kcard select{margin-top:6px;width:100%;font-size:11px;padding:3px;border-radius:6px;border:1px solid var(--line);background:var(--surface2);font-family:inherit;color:var(--text)}
.toolbar{display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.search,input.fld,select.fld{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px;background:var(--bg);font-family:inherit;color:var(--text)}
.search{flex:1;min-width:200px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);padding:7px 8px;border-bottom:1px solid var(--line)}
td{padding:9px 8px;border-bottom:1px solid var(--line);vertical-align:top}
.stagesel{font-size:12px;padding:3px 5px;border-radius:6px;border:1px solid;background:var(--surface);font-family:inherit}
.note{width:100%;margin-top:6px;font-size:12px;padding:5px;border:1px solid var(--line);border-radius:6px;background:var(--surface2);font-family:inherit;resize:vertical;color:var(--text)}
.tag{font-size:10px;padding:2px 7px;border-radius:20px;color:#fff;display:inline-block}
.bars{display:flex;align-items:flex-end;gap:5px;height:120px;margin-top:6px}
.bar-col{flex:1;text-align:center}.bar{border-radius:3px 3px 0 0;transition:height .4s}.bar-x{font-size:9px;color:var(--muted);margin-top:3px}
.heat{display:flex;flex-wrap:wrap;gap:4px}.hcell{width:20px;height:20px;border-radius:4px}
.donut{width:130px;height:130px;border-radius:50%;flex:0 0 auto}
.legend{font-size:13px}.legend div{padding:3px 0}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px}
.funnel{display:flex;flex-direction:column;gap:6px}
.fbar{display:flex;align-items:center;gap:10px;font-size:13px}.fbar .track{height:22px;border-radius:6px;min-width:2px;transition:width .4s}
.focus li{margin:4px 0;font-size:14px}
.modal{position:fixed;inset:0;background:rgba(12,12,12,.5);display:none;align-items:center;justify-content:center;z-index:120}
.modal.open{display:flex;animation:fade .2s}
.sheet{background:var(--surface);border-radius:16px;padding:22px;width:min(560px,92vw);max-height:88vh;overflow:auto;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.sheet h3{margin:0 0 14px;font-family:"Iowan Old Style",Georgia,serif}
.frow{display:flex;flex-direction:column;gap:4px;margin-bottom:10px}.frow label{font-size:12px;color:var(--muted)}
.frow input,.frow select,.frow textarea{padding:8px;border:1px solid var(--line);border-radius:8px;font-size:14px;background:var(--bg);font-family:inherit;color:var(--text)}
.toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:#0c0c0c;color:#fbf7ed;padding:11px 17px;border-radius:11px;font-size:13px;opacity:0;transition:opacity .3s;z-index:150;pointer-events:none;max-width:80%;text-align:center}
.empty{color:var(--muted);font-size:13px;padding:18px;text-align:center}
.confetti{position:fixed;top:-10px;width:9px;height:14px;z-index:140;pointer-events:none;border-radius:2px}
.chatfab{position:fixed;right:22px;bottom:22px;z-index:90;width:56px;height:56px;border-radius:50%;background:var(--green);color:#fff;border:none;cursor:pointer;font-size:24px;box-shadow:0 6px 20px rgba(0,0,0,.25);transition:transform .12s}
.chatfab:hover{transform:scale(1.07)}
.chatpanel{position:fixed;right:22px;bottom:88px;z-index:95;width:min(390px,92vw);height:min(560px,75vh);background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.3);display:none;flex-direction:column;overflow:hidden}
.chatpanel.open{display:flex;animation:fade .2s}
.chathead{padding:12px 16px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}
.chathead .t{font-family:"Iowan Old Style",Georgia,serif;font-weight:700}
.chatbody{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px}
.chatmsg{max-width:85%;padding:9px 12px;border-radius:12px;font-size:13px;white-space:pre-wrap;line-height:1.5}
.chatmsg.user{align-self:flex-end;background:var(--blue);color:#fff;border-bottom-right-radius:3px}
.chatmsg.bot{align-self:flex-start;background:var(--surface2);border:1px solid var(--line);border-bottom-left-radius:3px}
.chatmsg.bot code{background:var(--bg);padding:1px 4px;border-radius:4px;font-size:12px}
.chatform{display:flex;gap:8px;padding:12px;border-top:1px solid var(--line)}
.chatform input{flex:1;padding:9px 11px;border:1px solid var(--line);border-radius:10px;font-size:13px;background:var(--bg);color:var(--text);font-family:inherit}
.chatform button{background:var(--green);color:#fff;border:none;border-radius:10px;padding:0 14px;cursor:pointer}
.chathint{font-size:11px;color:var(--muted);padding:0 14px 8px}
.dots span{display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--muted);margin:0 1px;animation:blink 1.2s infinite}
.dots span:nth-child(2){animation-delay:.2s}.dots span:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,60%,100%{opacity:.2}30%{opacity:1}}
/* run center */
.runwrap{position:relative}
.runbtn{display:flex;align-items:center;gap:6px;font-size:13px;padding:7px 13px;border-radius:9px;border:1px solid var(--green);background:var(--green);color:#fff;cursor:pointer;font-family:inherit;transition:transform .08s,filter .15s}
.runbtn:hover{filter:brightness(1.08)}.runbtn:active{transform:scale(.96)}
.runmenu{position:absolute;top:115%;right:0;background:var(--surface);border:1px solid var(--line);border-radius:12px;box-shadow:0 14px 44px rgba(0,0,0,.2);padding:6px;display:none;z-index:80;min-width:250px}
.runmenu.open{display:block;animation:fade .15s}
.runmenu button{display:block;width:100%;text-align:left;background:none;border:none;padding:8px 10px;border-radius:8px;cursor:pointer;font-size:13px;color:var(--text);font-family:inherit}
.runmenu button:hover{background:var(--surface2)}
.runmenu .sub{font-size:10px;color:var(--muted);display:block;margin-top:1px}
.runpill{display:flex;align-items:center;gap:6px;font-size:12px;color:#fff;background:var(--amber);padding:5px 11px;border-radius:20px;cursor:pointer;white-space:nowrap}
.minispin{width:10px;height:10px;border:2px solid rgba(255,255,255,.4);border-top-color:#fff;border-radius:50%;animation:spin .8s linear infinite;flex:0 0 auto}
pre.logpre{background:var(--surface2);border:1px solid var(--line);border-radius:10px;padding:12px;font-size:11.5px;line-height:1.5;max-height:52vh;overflow:auto;white-space:pre-wrap;font-family:ui-monospace,"SF Mono",Menlo,monospace}
/* docs */
.docs{display:grid;grid-template-columns:290px 1fr;gap:16px;align-items:start}
.doclist{max-height:70vh;overflow:auto;padding-right:4px}
.docitem{padding:8px 10px;border-radius:9px;cursor:pointer;font-size:13px;border:1px solid transparent}
.docitem:hover{background:var(--surface2)}
.docitem.active{background:var(--surface2);border-color:var(--line)}
.docitem .sub{font-size:10px;color:var(--muted);margin-top:1px}
.dirtabs{display:flex;gap:5px;margin-bottom:12px;flex-wrap:wrap}
.dirtab{font-size:12px;padding:5px 11px;border-radius:8px;cursor:pointer;color:var(--muted);border:1px solid var(--line);user-select:none}
.dirtab.active{background:var(--text);color:var(--surface);border-color:var(--text)}
.mdview{font-size:14px;line-height:1.65;max-height:72vh;overflow:auto}
.mdview h1,.mdview h2,.mdview h3,.mdview h4{font-family:"Iowan Old Style",Georgia,serif;margin:14px 0 6px}
.mdview h1{font-size:22px}.mdview h2{font-size:18px}.mdview h3{font-size:15px}
.mdview code{background:var(--surface2);padding:1px 5px;border-radius:5px;font-size:12.5px}
.mdview a{color:var(--blue)}
.mdview ul{margin:6px 0;padding-left:20px}.mdview li{margin:3px 0}
.mdview hr{border:none;border-top:1px solid var(--line);margin:12px 0}
/* command palette */
.palette{position:fixed;inset:0;background:rgba(12,12,12,.45);display:none;align-items:flex-start;justify-content:center;padding-top:14vh;z-index:170}
.palette.open{display:flex;animation:fade .12s}
.palbox{background:var(--surface);border:1px solid var(--line);border-radius:14px;width:min(560px,92vw);box-shadow:0 24px 80px rgba(0,0,0,.35);overflow:hidden}
.palbox input{width:100%;padding:14px 16px;border:none;outline:none;background:transparent;font-size:15px;color:var(--text);font-family:inherit;border-bottom:1px solid var(--line);box-sizing:border-box}
.palist{max-height:330px;overflow:auto;padding:6px}
.palitem{padding:9px 12px;border-radius:8px;cursor:pointer;font-size:13.5px;display:flex;justify-content:space-between;align-items:center}
.palitem.sel,.palitem:hover{background:var(--surface2)}
.palitem .k{font-size:10px;color:var(--muted);font-family:ui-monospace,Menlo,monospace}
@media(max-width:820px){.stats{grid-template-columns:repeat(2,1fr)}.kanban{grid-template-columns:1fr 1fr}.pipe-row{grid-template-columns:repeat(2,1fr)}.docs{grid-template-columns:1fr}.doclist{max-height:34vh}}
</style></head>
<body>
<div id="splash"><div class="splash-logo">CareerOPS</div><div class="spinner"></div><div class="splash-sub">command center</div></div>
<div class="topbar"><div class="topinner">
  <div class="brand">CareerOPS</div>
  <div class="nav" id="nav"></div>
  <div class="chip" id="goalchip"></div>
  <span id="runpill" class="runpill" style="display:none" onclick="showRunLog()" title="A headless run is in progress. Click for the log."><span class="minispin"></span> running</span>
  <div class="runwrap">
    <button class="runbtn" id="runbtn" onclick="toggleRunMenu(event)" title="Run automation (or press k)">&#9654; Run</button>
    <div class="runmenu" id="runmenu"></div>
  </div>
  <div class="iconbtn" id="themebtn" title="Toggle theme (d)" onclick="toggleTheme()">&#9789;</div>
  <div class="chip"><span class="led"></span> live</div>
</div></div>
<div class="wrap"><div class="view" id="view"></div></div>
<div class="modal" id="modal"><div class="sheet" id="sheet"></div></div>
<div class="palette" id="palette"><div class="palbox">
  <input id="palinput" placeholder="Type a command... (run autopilot, go to queue, add, theme)" oninput="palRender()" onkeydown="palKey(event)">
  <div class="palist" id="palist"></div>
</div></div>
<div class="toast" id="toast"></div>

<button class="chatfab" id="chatfab" title="Ask your AI copilot" onclick="toggleChat()">&#128172;</button>
<div class="chatpanel" id="chatpanel">
  <div class="chathead"><span class="t">AI Copilot</span><span class="iconbtn" onclick="toggleChat()">&#10005;</span></div>
  <div class="chatbody" id="chatbody"></div>
  <div class="chathint">Try: "I applied to Stripe SDE1", "move Barclays to Interviewing", "write a cover letter for PropertyGuru", "what should I do today?"</div>
  <form class="chatform" id="chatform" onsubmit="return sendChat(event)">
    <input id="chatinput" placeholder="Ask or tell me to do something..." autocomplete="off">
    <button type="submit">Send</button>
  </form>
</div>

<script>
const STAGES=["Applied","Screening","Online Assessment","Phone Screen","Interviewing","Onsite","Offered","Rejected","Withdrawn"];
const STAGECOL={"Applied":"#5b5b5b","Screening":"#2b4a73","Online Assessment":"#2b4a73","Phone Screen":"#2b4a73","Interviewing":"#a16207","Onsite":"#a16207","Offered":"#2e6b3e","Rejected":"#9c2f2f","Withdrawn":"#5b5b5b"};
const TYPECOL={onsite:"#2b4a73",hybrid:"#a16207",remote:"#2e6b3e"};
const CONTACT_STATUS={"To Reach":"#5b5b5b","Reached Out":"#2b4a73","Replied":"#a16207","Referred":"#2e6b3e","No Reply":"#9c2f2f"};
const OUTCOMES=["Pending","Passed","Failed","Cancelled"];
const TABS=["Overview","Queue","Pipeline","Applications","Analytics","Network","Prep","Docs","Settings"];
const RUNS=[["/autopilot","Autopilot","refresh + packet + follow-ups + morning brief"],
  ["/daily-packet","Daily packet","10 fresh verified roles + cover letters"],
  ["/refresh-tracker","Refresh tracker","pull Gmail confirmations into the pipeline"],
  ["/weekly-digest","Weekly digest","recap, response rate, follow-up list"],
  ["/status","Status briefing","goal pace, queue, one action"]];
let S={}, TAB="Overview", q="";

const esc=s=>(s==null?"":String(s)).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const slug=s=>(s||"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
const goal=()=>(S.settings&&S.settings.daily_goal)||10;
const today=()=>new Date(new Date().toDateString());
const pd=s=>{if(!s)return null;const d=new Date(s.slice(0,10));return isNaN(d)?null:new Date(d.toDateString());};
const dago=s=>{const d=pd(s);return d?Math.floor((today()-d)/864e5):null;};
function squircle(n){let h=0;for(const c of (n||""))h=(h*31+c.charCodeAt(0))>>>0;return`hsl(${h%360},38%,46%)`;}
function toast(m){const t=document.getElementById("toast");t.textContent=m;t.style.opacity="1";clearTimeout(t._h);t._h=setTimeout(()=>t.style.opacity="0",3200);}
async function api(path,body){const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body||{})});if(!r.ok)throw new Error("HTTP "+r.status);return r.json();}
async function loadState(first){S=await (await fetch("/api/state")).json();render();if(first){setTimeout(()=>document.getElementById("splash").classList.add("hide"),350);}checkGoal();}

function resources(c){const s=slug(c),qq=encodeURIComponent(c||""),st=(S.settings||{});
  const L=[["LC",`https://leetcode.com/company/${s}/`],["Levels",`https://www.levels.fyi/companies/${s}/salaries`],["Glassdoor",`https://www.glassdoor.com/Search/results.htm?keyword=${qq}`]];
  if(st.alumni_school_slug)L.push(["Alumni",`https://www.linkedin.com/school/${st.alumni_school_slug}/people/?keyword=${qq}`]);
  L.push(["Recruiters",`https://www.linkedin.com/search/results/people/?keywords=${qq}%20recruiter`]);
  return `<div class="reslinks">`+L.map(([t,u])=>`<a class="res" href="${u}" target="_blank" rel="noopener">${t}</a>`).join("")+`</div>`;}

function metrics(){
  const A=S.applied_companies||[], t=today(), G=goal();
  const within=n=>A.filter(a=>{const d=dago(a.applied_date);return d!=null&&d>=0&&d<n;}).length;
  const days=new Set(A.map(a=>{const d=pd(a.applied_date);return d?+d:null;}).filter(Boolean));
  let streak=0,cur=+t;while(days.has(cur)){streak++;cur-=864e5;}
  const stageOf=a=>a.stage||"Applied";
  const responded=A.filter(a=>stageOf(a)!=="Applied").length;
  const pipe={Applied:0,Interviewing:0,Rejected:0,Offered:0};
  A.forEach(a=>{const s=stageOf(a);if(["Screening","Online Assessment","Phone Screen","Interviewing","Onsite"].includes(s))pipe.Interviewing++;else if(pipe[s]!=null)pipe[s]++;else pipe.Applied++;});
  const todayN=A.filter(a=>dago(a.applied_date)===0).length;
  const target=pd(S.target_offer_date), dleft=target?Math.round((target-t)/864e5):null;
  return {A,G,todayN,w7:within(7),w30:within(30),streak,resp:A.length?Math.round(100*responded/A.length):0,pipe,dleft};
}

function renderNav(){
  document.getElementById("nav").innerHTML=TABS.map((x,i)=>`<div class="tab ${x===TAB?"active":""}" onclick="setTab('${x}')">${x}<span class="k">${i+1}</span></div>`).join("");
  const m=metrics();
  document.getElementById("goalchip").innerHTML=m.dleft!=null?`<b>${m.dleft}</b>&nbsp;days to ${esc(S.target_offer_date)}`:`<span class="btn sm" onclick="setTab('Settings')">set goal</span>`;
}
function setTab(t){TAB=t;q="";render();if(t==="Docs")loadDocs();window.scrollTo({top:0,behavior:"smooth"});}

function render(){renderNav();const v=document.getElementById("view");v.style.animation="none";v.offsetHeight;v.style.animation="";
  v.innerHTML=({Overview:vOverview,Queue:vQueue,Pipeline:vPipeline,Applications:vApps,Analytics:vAnalytics,Network:vNetwork,Prep:vPrep,Docs:vDocs,Settings:vSettings}[TAB]||vOverview)();
  document.getElementById("modal").onclick=e=>{if(e.target.id==="modal")closeModal();};}

function vOverview(){
  const m=metrics(), roles=(S.current_queue||{}).roles||[];
  const appl=roles.filter(r=>r.applyable===true).length;
  const stale=m.A.filter(a=>(a.stage||"Applied")==="Applied"&&dago(a.applied_date)>=7);
  const focus=[];const gap=Math.max(0,m.G-m.todayN);
  focus.push(gap?`${gap} more application${gap!==1?"s":""} to hit today's goal of ${m.G}.`:`Daily goal met: ${m.todayN}/${m.G} today. Nice.`);
  if(appl)focus.push(`${appl} confirmed-applyable role(s) waiting in the Queue tab.`);
  if(stale.length)focus.push(`${stale.length} application(s) silent 7+ days. Try /follow-up.`);
  focus.push(`Keep LeetCode warm: open Prep for today's problem.`);
  const ring=Math.min(100,Math.round(100*m.todayN/m.G));
  const pace=(m.w7/7).toFixed(1), cap=m.dleft!=null?Math.max(0,m.dleft)*m.G:"-";
  return `
  <div class="card banner">
    <div><div class="t">${S.target_offer_date?`Land an offer by ${esc(S.target_offer_date)}`:"Land your next offer (set a target date in Settings)"}</div>
    <div class="muted">${m.dleft!=null?`${m.dleft} days left &middot; ~${cap} more applications possible at ${m.G}/day &middot; 7-day pace ${pace}/day`:""}</div></div>
    <button class="btn primary" onclick="addModal()">+ Log application</button>
  </div>
  <div class="card"><h2 class="sec">Today's focus</h2><ul style="margin:0;padding-left:18px">${focus.map(f=>`<li class="focus">${esc(f)}</li>`).join("")}</ul></div>
  <div class="stats">
    <div class="stat"><div class="ring" style="--p:${ring}"><span>${m.todayN}/${m.G}</span></div><div class="l">Today</div></div>
    <div class="stat"><div class="n">${m.w7}</div><div class="l">7 days</div></div>
    <div class="stat"><div class="n">${m.w30}</div><div class="l">30 days</div></div>
    <div class="stat"><div class="n">${m.streak}</div><div class="l">Streak</div></div>
    <div class="stat"><div class="n">${m.resp}%</div><div class="l">Response</div></div>
  </div>
  <div class="card" style="margin-top:16px"><h2 class="sec">Pipeline &middot; ${m.A.length} total applied</h2>
    <div class="pipe-row">${Object.entries(m.pipe).map(([k,n])=>`<div class="pipe"><div class="n">${n}</div><div class="l">${k}</div></div>`).join("")}</div></div>
  <div class="card"><h2 class="sec">30-day activity</h2><div class="heat">${heatmap()}</div></div>`;
}
function heatmap(){const A=S.applied_companies||[],t=today(),out=[];const col=c=>c===0?"var(--surface2)":c<3?"#bcd2b6":c<6?"#7fae84":c<goal()?"#4f8a5b":"#2e6b3e";
  for(let i=29;i>=0;i--){const d=new Date(+t-i*864e5);const c=A.filter(a=>{const x=pd(a.applied_date);return x&&+x===+d;}).length;out.push(`<span class="hcell" title="${d.toISOString().slice(0,10)}: ${c}" style="background:${col(c)}"></span>`);}return out.join("");}

function vQueue(){
  const roles=(S.current_queue||{}).roles||[];
  if(!roles.length)return `<div class="card empty">No roles queued. Run <code>/daily-packet</code> in Claude Code.</div>`;
  const rows=roles.map((r,i)=>{const done=r.applied===true,t=r.type||"onsite";
    const badge=r.applyable===true?`<span class="conf yes">YES</span>`:r.applyable===false?`<span class="conf no">NO</span>`:`<span class="conf unk">?</span>`;
    return `<div class="qrow ${done?"applied":""}"><span class="logo" style="background:${squircle(r.company)}">${esc((r.company||"?")[0])}</span>
      <div class="qmeta"><div class="qrole">${badge} ${esc(r.role||"")}</div><div class="qsub">${esc(r.company)} &middot; ${esc(r.location||"")}</div>
      ${r.applyable_reason?`<div class="reason">${esc(r.applyable_reason)}</div>`:""}${resources(r.company)}</div>
      <span class="pill" style="background:${TYPECOL[t]||"#5b5b5b"}">${esc(t)}</span>
      <a class="linkbtn" href="${esc(r.url||"#")}" target="_blank" rel="noopener">Apply &#8599;</a>
      <button class="btn sm ${done?"":"primary"}" onclick="toggleApplied(${i})">${done?"Applied ✓":"I applied"}</button></div>`;}).join("");
  return `<div class="card"><h2 class="sec"><span>Today's queue &middot; packet ${esc((S.current_queue||{}).date||"")}</span></h2>${rows}</div>`;
}
async function toggleApplied(i){const r=(S.current_queue||{}).roles[i];const on=!(r.applied===true);
  try{await api(on?"/api/applied":"/api/unapply",{key:`${r.company}|${r.role}`,company:r.company,role:r.role,location:r.location,url:r.url,type:r.type});toast(on?"Logged to tracker.":"Removed.");await loadState();}catch(e){toast("Error: "+e.message);}}

function vPipeline(){
  const A=S.applied_companies||[];
  const cols=[["Applied",["Applied"]],["Screening",["Screening","Online Assessment","Phone Screen"]],["Interviewing",["Interviewing","Onsite"]],["Offered",["Offered"]],["Closed",["Rejected","Withdrawn"]]];
  const html=cols.map(([name,st])=>{const items=A.filter(a=>st.includes(a.stage||"Applied"));
    return `<div class="kcol"><h3><span>${name}</span><span>${items.length}</span></h3>${items.map(kcard).join("")||'<div class="muted" style="padding:6px">empty</div>'}</div>`;}).join("");
  return `<div class="card"><h2 class="sec">Pipeline board &middot; change stage on any card</h2><div class="kanban">${html}</div></div>`;
}
function kcard(a){const d=dago(a.applied_date);
  return `<div class="kcard"><div class="c">${esc(a.company)}</div><div class="r">${esc(a.role||"")}</div><div class="r mono">${d!=null?d+"d ago":""}${(a.rounds||[]).length?" &middot; "+a.rounds.length+" round(s)":""}</div>
    <select onchange="setStage('${esc(a.id)}',this.value)">${STAGES.map(s=>`<option ${s===(a.stage||"Applied")?"selected":""}>${s}</option>`).join("")}</select></div>`;}
async function setStage(id,stage){try{await api("/api/stage",{id,stage});toast("Stage: "+stage);if(stage==="Offered")confetti();await loadState();}catch(e){toast("Error: "+e.message);}}

function vApps(){
  let A=(S.applied_companies||[]).slice().sort((a,b)=>(b.applied_date||"").localeCompare(a.applied_date||""));
  if(q)A=A.filter(a=>`${a.company} ${a.role||""}`.toLowerCase().includes(q));
  const rows=A.map(a=>{const col=STAGECOL[a.stage||"Applied"];const nr=(a.rounds||[]).length;
    return `<tr><td>${a.url?`<a href="${esc(a.url)}" target="_blank" rel="noopener">${esc(a.company)}</a>`:esc(a.company)}
      <div class="muted">${esc(a.role||"")}</div>${resources(a.company)}
      <textarea class="note" rows="1" placeholder="note..." onchange="saveNote('${esc(a.id)}',this.value)">${esc(a.note||"")}</textarea></td>
      <td><select class="stagesel" style="border-color:${col};color:${col}" onchange="setStage('${esc(a.id)}',this.value)">${STAGES.map(s=>`<option ${s===(a.stage||"Applied")?"selected":""}>${s}</option>`).join("")}</select></td>
      <td>${esc(a.source||"")}</td><td>${esc(a.location||"")}</td><td class="mono">${esc(a.applied_date||"")}</td>
      <td><button class="btn sm" onclick="roundsModal('${esc(a.id)}')">Rounds${nr?" ("+nr+")":""}</button> <button class="btn sm danger" onclick="delApp('${esc(a.id)}')">del</button></td></tr>`;}).join("");
  return `<div class="card"><h2 class="sec"><span>Applications &middot; ${A.length}</span><button class="btn primary sm" onclick="addModal()">+ Add</button></h2>
    <div class="toolbar"><input class="search" id="appsearch" placeholder="Filter by company or role... (/)" value="${esc(q)}" oninput="q=this.value.toLowerCase();render();document.getElementById('appsearch').focus()"></div>
    <table><thead><tr><th>Company</th><th>Stage</th><th>Source</th><th>Location</th><th>Applied</th><th></th></tr></thead>
    <tbody>${rows||'<tr><td colspan=6 class="empty">No applications.</td></tr>'}</tbody></table></div>`;
}
async function saveNote(id,note){try{await api("/api/note",{id,note});toast("Note saved.");(S.applied_companies||[]).forEach(a=>{if(a.id===id)a.note=note;});}catch(e){toast("Error: "+e.message);}}
async function delApp(id){if(!confirm("Delete this application?"))return;try{await api("/api/delete",{id});toast("Deleted.");await loadState();}catch(e){toast("Error: "+e.message);}}

function vNetwork(){
  const C=S.contacts||[];
  const rows=C.map(c=>{const col=CONTACT_STATUS[c.status||"To Reach"];
    return `<tr><td><b>${esc(c.name||"?")}</b><div class="muted">${esc(c.title||"")}</div>${c.link?`<a class="res" href="${esc(c.link)}" target="_blank">profile</a>`:""}</td>
      <td>${esc(c.company||"")}</td>
      <td><select class="stagesel" style="border-color:${col};color:${col}" onchange="contactUpd('${c.id}','status',this.value)">${Object.keys(CONTACT_STATUS).map(s=>`<option ${s===(c.status||"To Reach")?"selected":""}>${s}</option>`).join("")}</select></td>
      <td><input class="note" value="${esc(c.note||"")}" onchange="contactUpd('${c.id}','note',this.value)"></td>
      <td><button class="btn sm danger" onclick="contactDel('${c.id}')">del</button></td></tr>`;}).join("");
  return `<div class="card"><h2 class="sec"><span>Networking CRM &middot; ${C.length} contact(s)</span><button class="btn primary sm" onclick="contactModal()">+ Contact</button></h2>
    <p class="muted" style="margin:-4px 0 12px">Track referral paths. Run <code>/referral &lt;company&gt;</code> to find alumni and draft outreach, then log them here.</p>
    <table><thead><tr><th>Person</th><th>Company</th><th>Status</th><th>Note</th><th></th></tr></thead>
    <tbody>${rows||'<tr><td colspan=5 class="empty">No contacts yet. Add one or run /referral.</td></tr>'}</tbody></table></div>`;
}
async function contactUpd(id,field,val){try{await api("/api/contact",{op:"update",id,[field]:val});(S.contacts||[]).forEach(c=>{if(c.id===id)c[field]=val;});toast("Updated.");}catch(e){toast("Error: "+e.message);}}
async function contactDel(id){if(!confirm("Delete contact?"))return;try{await api("/api/contact",{op:"delete",id});toast("Deleted.");await loadState();}catch(e){toast("Error: "+e.message);}}

function vAnalytics(){
  const A=S.applied_companies||[],t=today();let mx=1,arr=[];
  for(let i=13;i>=0;i--){const d=new Date(+t-i*864e5);const c=A.filter(a=>{const x=pd(a.applied_date);return x&&+x===+d;}).length;arr.push([d,c]);mx=Math.max(mx,c);}
  const bars=arr.map(([d,c])=>`<div class="bar-col"><div class="bar" style="height:${Math.round(100*c/mx)+2}px;background:${c>=goal()?"#2e6b3e":c>0?"#a16207":"var(--surface2)"}" title="${d.toISOString().slice(0,10)}: ${c}"></div><div class="bar-x">${d.getDate()}</div></div>`).join("");
  const bs={};A.forEach(a=>bs[a.source||"Unknown"]=(bs[a.source||"Unknown"]||0)+1);
  const tot=Object.values(bs).reduce((x,y)=>x+y,0)||1;let acc=0,seg=[],leg="";
  Object.entries(bs).sort((a,b)=>b[1]-a[1]).forEach(([k,n])=>{const c=squircle(k);seg.push(`${c} ${acc/tot*360}deg ${(acc+n)/tot*360}deg`);acc+=n;leg+=`<div><span class="dot" style="background:${c}"></span>${esc(k)} <b>${n}</b> <span class="muted">(${Math.round(100*n/tot)}%)</span></div>`;});
  const donut=`<div class="donut" style="background:conic-gradient(${seg.join(",")})"></div>`;
  const grp={Applied:0,Screening:0,Interviewing:0,Offered:0,Closed:0};
  A.forEach(a=>{const s=a.stage||"Applied";if(s==="Applied")grp.Applied++;else if(["Screening","Online Assessment","Phone Screen"].includes(s))grp.Screening++;else if(["Interviewing","Onsite"].includes(s))grp.Interviewing++;else if(s==="Offered")grp.Offered++;else grp.Closed++;});
  const fmax=Math.max(...Object.values(grp),1);
  const fcol={Applied:"#5b5b5b",Screening:"#2b4a73",Interviewing:"#a16207",Offered:"#2e6b3e",Closed:"#9c2f2f"};
  const funnel=Object.entries(grp).map(([k,n])=>`<div class="fbar"><span style="width:90px">${k}</span><div class="track" style="width:${Math.round(100*n/fmax)}%;background:${fcol[k]}"></div><b>${n}</b></div>`).join("");
  return `<div class="card"><h2 class="sec">Applications, last 14 days</h2><div class="bars">${bars}</div></div>
    <div class="row"><div class="card" style="flex:1;min-width:280px"><h2 class="sec">By source</h2><div class="row" style="align-items:center"><div>${donut}</div><div class="legend">${leg||'<span class="muted">no data</span>'}</div></div></div>
    <div class="card" style="flex:1;min-width:280px"><h2 class="sec">Pipeline funnel</h2><div class="funnel">${funnel}</div></div></div>`;
}

function vPrep(){
  const A=S.applied_companies||[],roles=(S.current_queue||{}).roles||[];
  const companies=[...new Set([...roles.map(r=>r.company),...A.filter(a=>!["Applied","Rejected","Withdrawn"].includes(a.stage||"Applied")).map(a=>a.company)])].filter(Boolean);
  const cards=companies.map(c=>`<div class="qrow"><span class="logo" style="background:${squircle(c)}">${esc(c[0])}</span>
    <div class="qmeta"><div class="qrole">${esc(c)}</div><div class="reslinks">
    <a class="res" href="https://leetcode.com/company/${slug(c)}/" target="_blank">LeetCode Qs</a>
    <a class="res" href="https://www.glassdoor.com/Interview/${encodeURIComponent(c)}-interview-questions-SRCH.htm" target="_blank">Glassdoor Qs</a>
    <a class="res" href="https://www.geeksforgeeks.org/?s=${encodeURIComponent(c)}%20interview" target="_blank">GFG</a></div></div></div>`).join("");
  return `<div class="card"><h2 class="sec">Interview prep hub</h2>
    <p class="muted" style="margin:0 0 10px">Run <code>/interview-prep</code>, <code>/mock-interview</code>, or <code>/dsa</code> in Claude Code for AI prep. Quick links per active company:</p>
    ${cards||'<div class="empty">No companies in queue or active pipeline yet.</div>'}</div>`;
}

function vSettings(){
  return `<div class="card"><h2 class="sec">Settings</h2>
    <div class="frow" style="max-width:280px"><label>Your first name (copilot greeting)</label><input id="s_name" class="fld" value="${esc((S.settings||{}).user_name||"")}"></div>
    <div class="frow" style="max-width:280px"><label>School LinkedIn slug (alumni links)</label><input id="s_school" class="fld" placeholder="e.g. stanford-university" value="${esc((S.settings||{}).alumni_school_slug||"")}"></div>
    <div class="frow" style="max-width:280px"><label>Daily application goal</label><input id="s_goal" class="fld" type="number" min="1" value="${goal()}"></div>
    <div class="frow" style="max-width:280px"><label>Target offer date</label><input id="s_target" class="fld" type="date" value="${esc(S.target_offer_date||"")}"></div>
    <div class="frow" style="max-width:280px"><label>Theme</label><div class="row"><button class="btn" onclick="setTheme('light')">Light</button><button class="btn" onclick="setTheme('dark')">Dark</button></div></div>
    <button class="btn primary" onclick="saveSettings()">Save</button>
    <hr style="border:none;border-top:1px solid var(--line);margin:18px 0">
    <h2 class="sec">Data</h2>
    <p class="muted">Source of truth is <code>tracker/state.json</code>. Slash commands and this app both write to it.</p>
    <a class="btn" href="/api/state" target="_blank">View raw state JSON</a>
    <div style="margin-top:14px"><b>Keyboard:</b> <span class="muted">k or &#8984;K command palette &middot; 1-9 switch tabs &middot; n add &middot; / search &middot; d theme &middot; c copilot</span></div></div>`;
}
async function saveSettings(){try{await api("/api/settings",{daily_goal:document.getElementById("s_goal").value,user_name:document.getElementById("s_name").value.trim(),alumni_school_slug:document.getElementById("s_school").value.trim()});const tv=document.getElementById("s_target").value;await api("/api/goal",{date:tv});toast("Settings saved.");await loadState();}catch(e){toast("Error: "+e.message);}}

/* ---- modals ---- */
function closeModal(){document.getElementById("modal").classList.remove("open");}
function openSheet(html){document.getElementById("sheet").innerHTML=html;document.getElementById("modal").classList.add("open");}
function field(id,label,type){return `<div class="frow"><label>${label}</label><input id="${id}" ${type?`type="${type}"`:""} placeholder="${label}"></div>`;}
function addModal(){openSheet(`<h3>Log an application</h3>${field("f_company","company")}${field("f_role","role")}${field("f_location","location")}${field("f_url","url")}${field("f_source","source")}
  <div class="frow"><label>stage</label><select id="f_stage">${STAGES.map(s=>`<option>${s}</option>`).join("")}</select></div>
  <div class="frow"><label>applied date</label><input id="f_date" type="date" value="${new Date().toISOString().slice(0,10)}"></div>
  <div class="row" style="justify-content:flex-end;margin-top:8px"><button class="btn" onclick="closeModal()">Cancel</button><button class="btn primary" onclick="submitAdd()">Save</button></div>`);
  setTimeout(()=>document.getElementById("f_company").focus(),50);}
async function submitAdd(){const g=id=>document.getElementById(id).value.trim();
  const p={company:g("f_company"),role:g("f_role"),location:g("f_location"),url:g("f_url"),source:g("f_source"),stage:g("f_stage"),applied_date:g("f_date")};
  if(!p.company){toast("Company required.");return;}
  try{await api("/api/add",p);closeModal();toast("Application added.");await loadState();}catch(e){toast("Error: "+e.message);}}

function contactModal(){openSheet(`<h3>Add contact</h3>${field("c_name","name")}${field("c_title","title")}${field("c_company","company")}${field("c_link","LinkedIn / email")}
  <div class="frow"><label>status</label><select id="c_status">${Object.keys(CONTACT_STATUS).map(s=>`<option>${s}</option>`).join("")}</select></div>${field("c_note","note")}
  <div class="row" style="justify-content:flex-end"><button class="btn" onclick="closeModal()">Cancel</button><button class="btn primary" onclick="submitContact()">Save</button></div>`);
  setTimeout(()=>document.getElementById("c_name").focus(),50);}
async function submitContact(){const g=id=>document.getElementById(id).value.trim();
  const p={op:"add",name:g("c_name"),title:g("c_title"),company:g("c_company"),link:g("c_link"),status:document.getElementById("c_status").value,note:g("c_note")};
  if(!p.name){toast("Name required.");return;}
  try{await api("/api/contact",p);closeModal();toast("Contact added.");await loadState();}catch(e){toast("Error: "+e.message);}}

function roundsModal(appId){const a=(S.applied_companies||[]).find(x=>String(x.id)===String(appId));if(!a)return;
  const list=(a.rounds||[]).map(r=>`<div class="qrow"><div class="qmeta"><div class="qrole">${esc(r.type||"Round")} <span class="tag" style="background:${r.outcome==="Passed"?"#2e6b3e":r.outcome==="Failed"?"#9c2f2f":"#a16207"}">${esc(r.outcome||"Pending")}</span></div><div class="qsub mono">${esc(r.date||"")}</div>${r.notes?`<div class="reason">${esc(r.notes)}</div>`:""}</div><button class="btn sm danger" onclick="roundDel('${appId}','${r.id}')">del</button></div>`).join("")||'<div class="empty">No rounds logged.</div>';
  openSheet(`<h3>${esc(a.company)} &middot; interview rounds</h3>${list}
    <hr style="border:none;border-top:1px solid var(--line);margin:14px 0">
    <div class="frow"><label>round type</label><input id="r_type" placeholder="Phone screen / DSA / System design / Onsite / HR"></div>
    <div class="frow"><label>date</label><input id="r_date" type="date" value="${new Date().toISOString().slice(0,10)}"></div>
    <div class="frow"><label>outcome</label><select id="r_outcome">${OUTCOMES.map(o=>`<option>${o}</option>`).join("")}</select></div>
    <div class="frow"><label>notes</label><textarea id="r_notes" rows="2" placeholder="questions asked, how it went..."></textarea></div>
    <div class="row" style="justify-content:flex-end"><button class="btn" onclick="closeModal()">Close</button><button class="btn primary" onclick="roundAdd('${appId}')">Add round</button></div>`);}
async function roundAdd(appId){const g=id=>document.getElementById(id).value.trim();
  try{await api("/api/round",{op:"add",appId,type:g("r_type"),date:g("r_date"),outcome:document.getElementById("r_outcome").value,notes:g("r_notes")});toast("Round added.");await loadState();roundsModal(appId);}catch(e){toast("Error: "+e.message);}}
async function roundDel(appId,roundId){try{await api("/api/round",{op:"delete",appId,roundId});toast("Round deleted.");await loadState();roundsModal(appId);}catch(e){toast("Error: "+e.message);}}

/* ---- run center ---- */
let RUNNING=false;
function renderRunMenu(){document.getElementById("runmenu").innerHTML=RUNS.map(([cmd,l,sub])=>`<button onclick="startRun('${cmd}')">${esc(l)}<span class="sub">${esc(sub)}</span></button>`).join("")+`<button onclick="showRunLog()">View latest run log<span class="sub">output of the last headless run</span></button>`;}
function toggleRunMenu(e){e.stopPropagation();document.getElementById("runmenu").classList.toggle("open");}
async function startRun(cmd){document.getElementById("runmenu").classList.remove("open");
  try{const r=await api("/api/run",{command:cmd});
    if(r.ok){toast("Started "+cmd+" in the background. The pill up top shows progress.");await pollRun();}
    else toast(r.error||"Could not start.");}
  catch(e){toast("Error: "+e.message);}}
async function pollRun(){try{const r=await(await fetch("/api/runstatus")).json();
  const pill=document.getElementById("runpill");
  if(r.running){pill.style.display="flex";RUNNING=true;}
  else{pill.style.display="none";
    if(RUNNING){RUNNING=false;toast("Run finished. Refreshing...");await loadState();if(TAB==="Docs")loadDocs();}}}
  catch(e){}}
async function showRunLog(){let r={};try{r=await(await fetch("/api/runstatus")).json();}catch(e){r={tail:"Error: "+e.message};}
  openSheet(`<h3>${r.running?"Run in progress":"Latest run"} <span class="muted mono">${esc(r.log||"")}</span></h3>
    <pre class="logpre">${esc(r.tail||"(no output yet; headless runs flush their transcript at the end)")}</pre>
    <div class="row" style="justify-content:flex-end;margin-top:10px"><button class="btn" onclick="showRunLog()">Refresh</button><button class="btn primary" onclick="closeModal()">Close</button></div>`);}

/* ---- docs ---- */
const DOCDIRS=[["briefs","Briefs"],["packets","Packets"],["coverletters","Letters"],["notes","Notes"]];
let DOCDIR="briefs",DOCFILES=[],DOCSEL=null,DOCTXT="",DOCBUSY=false;
function md(t){let h=esc(t);
  h=h.replace(/^#{4,6} (.*)$/gm,"<h4>$1</h4>").replace(/^### (.*)$/gm,"<h3>$1</h3>").replace(/^## (.*)$/gm,"<h2>$1</h2>").replace(/^# (.*)$/gm,"<h1>$1</h1>");
  h=h.replace(/^\s*---+\s*$/gm,"<hr>");
  h=h.replace(/\*\*([^*]+)\*\*/g,"<b>$1</b>").replace(/`([^`]+)`/g,"<code>$1</code>");
  h=h.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
  h=h.replace(/^(?:&gt;|>) ?(.*)$/gm,'<span class="muted">$1</span>');
  h=h.replace(/^[-*] (.*)$/gm,"<li>$1</li>").replace(/(?:<li>.*<\/li>\n?)+/g,m=>"<ul>"+m.replace(/\n/g,"")+"</ul>");
  h=h.replace(/\n{2,}/g,"<br><br>").replace(/\n/g,"<br>");
  return h;}
function prettyDoc(n){return n.replace(/\.md$/,"").replace(/-/g," ");}
function vDocs(){
  const tabs=DOCDIRS.map(([d,l])=>`<span class="dirtab ${d===DOCDIR?"active":""}" onclick="setDocDir('${d}')">${l}</span>`).join("");
  const list=DOCFILES.map(f=>`<div class="docitem ${f.name===DOCSEL?"active":""}" onclick="openDoc('${esc(f.name)}')"><div>${esc(prettyDoc(f.name))}</div><div class="sub">${new Date(f.mtime*1000).toLocaleString()} &middot; ${(f.size/1024).toFixed(1)} kb</div></div>`).join("")
    ||`<div class="empty">${DOCBUSY?"Loading...":"Nothing here yet. Hit &#9654; Run &rarr; Autopilot and this fills itself."}</div>`;
  const body=DOCSEL?`<div class="mdview">${md(DOCTXT)}</div>`:'<div class="empty">Select a document.</div>';
  return `<div class="card"><h2 class="sec">Documents &middot; briefs, packets, and letters land here automatically</h2>
    <div class="dirtabs">${tabs}</div>
    <div class="docs"><div class="doclist">${list}</div><div class="card" style="margin:0">${body}</div></div></div>`;}
async function setDocDir(d){DOCDIR=d;DOCSEL=null;DOCTXT="";await loadDocs();}
async function loadDocs(){DOCBUSY=true;try{const r=await(await fetch("/api/docs?dir="+DOCDIR)).json();DOCFILES=r.files||[];DOCBUSY=false;
  if(!DOCSEL&&DOCFILES.length)return openDoc(DOCFILES[0].name);if(TAB==="Docs")render();}
  catch(e){DOCBUSY=false;toast("Error: "+e.message);}}
async function openDoc(name){DOCSEL=name;
  try{const r=await(await fetch(`/api/doc?dir=${DOCDIR}&name=${encodeURIComponent(name)}`)).json();DOCTXT=r.content||r.error||"";}
  catch(e){DOCTXT="Error: "+e.message;}
  if(TAB==="Docs")render();}

/* ---- command palette ---- */
let PALSEL=0;
function palActions(){const a=[];
  RUNS.forEach(([cmd,l,sub])=>a.push({label:"Run: "+l,k:cmd,run:()=>startRun(cmd)}));
  TABS.forEach((t,i)=>a.push({label:"Go to "+t,k:String(i+1),run:()=>setTab(t)}));
  a.push({label:"Log an application",k:"n",run:()=>addModal()});
  a.push({label:"Add a networking contact",k:"",run:()=>{setTab("Network");contactModal();}});
  a.push({label:"Open AI copilot",k:"c",run:()=>toggleChat()});
  a.push({label:"View latest run log",k:"",run:()=>showRunLog()});
  a.push({label:"Toggle theme",k:"d",run:()=>toggleTheme()});
  return a;}
function openPalette(){const p=document.getElementById("palette");p.classList.add("open");
  const i=document.getElementById("palinput");i.value="";PALSEL=0;palRender();setTimeout(()=>i.focus(),40);}
function closePalette(){document.getElementById("palette").classList.remove("open");}
function palFiltered(){const q=(document.getElementById("palinput").value||"").toLowerCase();
  return palActions().filter(a=>a.label.toLowerCase().includes(q));}
function palRender(){const list=palFiltered();PALSEL=Math.min(PALSEL,Math.max(0,list.length-1));
  document.getElementById("palist").innerHTML=list.map((a,i)=>`<div class="palitem ${i===PALSEL?"sel":""}" onmousedown="palGo(${i})">${esc(a.label)}<span class="k">${esc(a.k||"")}</span></div>`).join("")||'<div class="empty">No matches.</div>';}
function palGo(i){const list=palFiltered();if(list[i]){closePalette();list[i].run();}}
function palKey(e){
  if(e.key==="ArrowDown"){PALSEL++;palRender();e.preventDefault();}
  else if(e.key==="ArrowUp"){PALSEL=Math.max(0,PALSEL-1);palRender();e.preventDefault();}
  else if(e.key==="Enter"){palGo(PALSEL);e.preventDefault();}
  else if(e.key==="Escape"){closePalette();}}

/* ---- theme ---- */
function applyTheme(t){document.documentElement.dataset.theme=t;document.getElementById("themebtn").innerHTML=t==="dark"?"&#9728;":"&#9789;";localStorage.setItem("careerops_theme",t);}
function setTheme(t){applyTheme(t);toast(t[0].toUpperCase()+t.slice(1)+" theme.");}
function toggleTheme(){applyTheme(document.documentElement.dataset.theme==="dark"?"light":"dark");}

/* ---- confetti + goal ---- */
function confetti(){const cols=["#2e6b3e","#a16207","#2b4a73","#9c2f2f","#e9c46a"];
  for(let i=0;i<90;i++){const c=document.createElement("div");c.className="confetti";c.style.left=Math.random()*100+"vw";c.style.background=cols[i%cols.length];c.style.transform=`rotate(${Math.random()*360}deg)`;
    const dur=2+Math.random()*2;c.animate([{transform:`translateY(0) rotate(0)`,opacity:1},{transform:`translateY(${80+Math.random()*20}vh) rotate(${Math.random()*720}deg)`,opacity:.9}],{duration:dur*1000,easing:"cubic-bezier(.2,.6,.4,1)"});
    document.body.appendChild(c);setTimeout(()=>c.remove(),dur*1000);}}
function checkGoal(){const m=metrics();const key="careerops_goalhit";const todayStr=new Date().toISOString().slice(0,10);
  if(m.todayN>=m.G&&localStorage.getItem(key)!==todayStr){localStorage.setItem(key,todayStr);confetti();toast("Daily goal hit. "+m.todayN+"/"+m.G+". Keep going!");}}

/* ---- keyboard ---- */
document.addEventListener("keydown",e=>{
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){openPalette();e.preventDefault();return;}
  const tag=(e.target.tagName||"").toLowerCase();if(["input","textarea","select"].includes(tag))return;
  if(e.key>="1"&&e.key<="9"){setTab(TABS[+e.key-1]);}
  else if(e.key==="k"){openPalette();e.preventDefault();}
  else if(e.key==="n"){addModal();}
  else if(e.key==="d"){toggleTheme();}
  else if(e.key==="/"){if(TAB!=="Applications")setTab("Applications");setTimeout(()=>{const s=document.getElementById("appsearch");if(s)s.focus();},60);e.preventDefault();}
  else if(e.key==="Escape"){closeModal();closePalette();}});
document.addEventListener("click",()=>{const m=document.getElementById("runmenu");if(m)m.classList.remove("open");});

/* ---- AI copilot chat ---- */
let chatHistory=[], chatBusy=false;
function toggleChat(){const p=document.getElementById("chatpanel");p.classList.toggle("open");
  if(p.classList.contains("open")){if(!chatHistory.length){const nm=(S.settings||{}).user_name;botSay(`Hey${nm?" "+nm:""}. I can answer questions and act on your tracker. What do you need?`);}setTimeout(()=>document.getElementById("chatinput").focus(),60);}}
function fmtChat(t){return esc(t).replace(/`([^`]+)`/g,"<code>$1</code>").replace(/\n/g,"<br>");}
function addMsg(role,text){const b=document.getElementById("chatbody");const d=document.createElement("div");d.className="chatmsg "+role;d.innerHTML=fmtChat(text);b.appendChild(d);b.scrollTop=b.scrollHeight;return d;}
function botSay(t){addMsg("bot",t);}
async function sendChat(e){e.preventDefault();if(chatBusy)return false;
  const inp=document.getElementById("chatinput");const text=inp.value.trim();if(!text)return false;
  inp.value="";addMsg("user",text);chatHistory.push({role:"user",content:text});chatBusy=true;
  const b=document.getElementById("chatbody");const typing=document.createElement("div");typing.className="chatmsg bot";typing.innerHTML='<span class="dots"><span></span><span></span><span></span></span>';b.appendChild(typing);b.scrollTop=b.scrollHeight;
  try{const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({messages:chatHistory})});
    const data=await r.json();typing.remove();const reply=data.reply||data.error||"(no reply)";
    addMsg("bot",reply);chatHistory.push({role:"assistant",content:reply});
    await loadState();/* reflect any actions the bot took */}
  catch(err){typing.remove();botSay("Error: "+err.message);}
  chatBusy=false;return false;}
document.addEventListener("keydown",e=>{if(e.key==="c"&&!["input","textarea","select"].includes((e.target.tagName||"").toLowerCase())){toggleChat();}});

applyTheme(localStorage.getItem("careerops_theme")||"light");
renderRunMenu();
document.getElementById("palette").addEventListener("click",e=>{if(e.target.id==="palette")closePalette();});
loadState(true);
setInterval(loadState,30000);
pollRun();
setInterval(pollRun,6000);
</script>
</body></html>
"""
