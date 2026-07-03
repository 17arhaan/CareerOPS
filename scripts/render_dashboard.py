#!/usr/bin/env python3
"""Render dashboard/index.html from tracker/state.json.

Standalone HTML, beige + black palette, serif numerals. Works two ways:
  - Opened as a file (file://): "I applied" + stage edits save to the browser and copy a
    command to paste into Claude Code.
  - Served by scripts/serve_dashboard.py (http://): the same controls write straight to
    tracker/state.json, no paste needed.

    python3 scripts/render_dashboard.py
"""
import html
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "tracker" / "state.json"
STATE_EXAMPLE = ROOT / "tracker" / "state.example.json"
OUT = ROOT / "dashboard" / "index.html"

DAILY_GOAL = 10  # fallback; the real value lives in state.json settings.daily_goal
DEFAULT_TARGET = None


def ensure_state():
    """Create tracker/state.json from the example on a fresh clone."""
    if STATE.exists():
        return
    STATE.parent.mkdir(parents=True, exist_ok=True)
    if STATE_EXAMPLE.exists():
        STATE.write_text(STATE_EXAMPLE.read_text())
    else:
        STATE.write_text(json.dumps({
            "as_of": None, "applied_companies": [],
            "current_queue": {"date": None, "roles": []},
            "previously_recommended_skip_14d": [], "target_offer_date": None,
            "feedback_log": [], "settings": {"daily_goal": DAILY_GOAL},
            "contacts": []}, indent=2) + "\n")


ensure_state()
_SETTINGS = {}

TYPE_COLORS = {"onsite": "#2b4a73", "hybrid": "#a16207", "remote": "#2e6b3e"}
STAGES = ["Applied", "Screening", "Online Assessment", "Phone Screen", "Interviewing",
          "Onsite", "Offered", "Rejected", "Withdrawn"]
STAGE_COLORS = {
    "Applied": "#5b5b5b", "Screening": "#2b4a73", "Online Assessment": "#2b4a73",
    "Phone Screen": "#2b4a73", "Interviewing": "#a16207", "Onsite": "#a16207",
    "Offered": "#2e6b3e", "Rejected": "#9c2f2f", "Withdrawn": "#5b5b5b",
}


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(s[:10])
        except ValueError:
            return None


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")


def squircle(name):
    h = 0
    for ch in name or "":
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return f"hsl({h % 360}, 38%, 42%)"


def esc(s):
    return html.escape(str(s if s is not None else ""))


def resources(company):
    """Per-company research links (LeetCode, Levels, Glassdoor, alumni, recruiters)."""
    s = slug(company)
    q = company.replace(" ", "%20") if company else ""
    links = [
        ("LC", f"https://leetcode.com/company/{s}/"),
        ("Levels", f"https://www.levels.fyi/companies/{s}/salaries"),
        ("Glassdoor", f"https://www.glassdoor.com/Search/results.htm?keyword={q}"),
    ]
    school = (_SETTINGS or {}).get("alumni_school_slug")
    if school:
        links.append(("Alumni", f"https://www.linkedin.com/school/{school}/people/?keyword={q}"))
    links.append(("Recruiters", f"https://www.linkedin.com/search/results/people/?keywords={q}%20recruiter"))
    return " ".join(
        f'<a class="res" href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a>'
        for t, u in links)


def build():
    global _SETTINGS, DAILY_GOAL
    ensure_state()
    state = json.loads(STATE.read_text())
    _SETTINGS = state.get("settings") or {}
    try:
        DAILY_GOAL = max(1, int(_SETTINGS.get("daily_goal", DAILY_GOAL)))
    except (TypeError, ValueError):
        pass
    applied = state.get("applied_companies", [])
    queue = state.get("current_queue", {}) or {}
    roles = queue.get("roles", [])
    today = date.today()
    target = parse_date(state.get("target_offer_date")) or parse_date(DEFAULT_TARGET)

    def within(n):
        return sum(1 for a in applied
                   if (d := parse_date(a.get("applied_date"))) and 0 <= (today - d).days < n)

    today_count = sum(1 for a in applied if parse_date(a.get("applied_date")) == today)
    last7, last30 = within(7), within(30)

    applied_days = {parse_date(a.get("applied_date")) for a in applied}
    applied_days.discard(None)
    streak, cur = 0, today
    while cur in applied_days:
        streak += 1
        cur = date.fromordinal(cur.toordinal() - 1)

    stage_of = lambda a: a.get("stage", "Applied")
    responded = sum(1 for a in applied if stage_of(a) != "Applied")
    resp_rate = round(100 * responded / len(applied)) if applied else 0

    pipeline = {"Applied": 0, "Interviewing": 0, "Rejected": 0, "Offered": 0}
    for a in applied:
        s = stage_of(a)
        if s in ("Screening", "Online Assessment", "Phone Screen", "Interviewing", "Onsite"):
            pipeline["Interviewing"] += 1
        elif s in pipeline:
            pipeline[s] += 1
        else:
            pipeline["Applied"] += 1

    # goal math
    days_left = (target - today).days if target else None
    goal_line = ""
    if days_left is not None:
        cap = max(0, days_left) * DAILY_GOAL
        goal_line = (f'{days_left} days to target ({target.isoformat()}) &middot; '
                     f'~{cap} more applications possible at {DAILY_GOAL}/day &middot; '
                     f'7-day pace {round(last7/7, 1)}/day')

    # focus
    focus = []
    gap = max(0, DAILY_GOAL - today_count)
    focus.append(f"{gap} more application{'s' if gap != 1 else ''} to hit today's goal of {DAILY_GOAL}."
                 if gap else f"Daily goal met: {today_count}/{DAILY_GOAL} today.")
    appl_q = sum(1 for r in roles if r.get("applyable") is True)
    if appl_q:
        focus.append(f"{appl_q} confirmed-applyable role(s) waiting in today's queue.")
    stale = [a for a in applied if stage_of(a) == "Applied"
             and (d := parse_date(a.get("applied_date"))) and (today - d).days >= 7]
    if stale:
        focus.append(f"{len(stale)} application(s) silent 7+ days. Run /follow-up on the strongest.")
    focus.append("Keep LeetCode warm: run /dsa for today's company-weighted problem.")

    # 14-day bar chart
    bars = []
    for i in range(13, -1, -1):
        d = date.fromordinal(today.toordinal() - i)
        bars.append((d, sum(1 for a in applied if parse_date(a.get("applied_date")) == d)))
    max_bar = max((c for _, c in bars), default=0) or 1

    # 30-day heatmap
    heat = []
    for i in range(29, -1, -1):
        d = date.fromordinal(today.toordinal() - i)
        heat.append((d, sum(1 for a in applied if parse_date(a.get("applied_date")) == d)))

    by_source = {}
    for a in applied:
        by_source[a.get("source", "Unknown")] = by_source.get(a.get("source", "Unknown"), 0) + 1

    # ---- HTML fragments ----
    ring_pct = min(100, round(100 * today_count / DAILY_GOAL))
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    queue_rows = "\n".join(queue_row(r) for r in roles) or \
        '<div class="empty">No roles in the queue. Run <code>/daily-packet</code>.</div>'
    applyable_count = sum(1 for r in roles if r.get("applyable") is True)

    table_rows = "\n".join(
        app_row(a) for a in sorted(applied, key=lambda a: a.get("applied_date", ""), reverse=True)
    ) or '<tr><td colspan="5" class="empty">No applications logged yet.</td></tr>'

    pipe_html = "".join(
        f'<div class="pipe"><div class="pipe-n">{n}</div><div class="pipe-l">{esc(k)}</div></div>'
        for k, n in pipeline.items())

    bar_html = "".join(
        f'<div class="bar-col"><div class="bar" style="height:{round(70*c/max_bar)+2}px;'
        f'background:{"#2e6b3e" if c>=DAILY_GOAL else "#a16207" if c>0 else "#d8d0c0"}" '
        f'title="{d.isoformat()}: {c}"></div><div class="bar-x">{d.strftime("%d")}</div></div>'
        for d, c in bars)

    def heat_color(c):
        if c == 0:
            return "#e7dfce"
        if c < 3:
            return "#bcd2b6"
        if c < 6:
            return "#7fae84"
        if c < DAILY_GOAL:
            return "#4f8a5b"
        return "#2e6b3e"
    heat_html = "".join(
        f'<span class="hcell" style="background:{heat_color(c)}" title="{d.isoformat()}: {c}"></span>'
        for d, c in heat)

    src_total = sum(by_source.values()) or 1
    src_html = "".join(
        f'<div class="src"><span class="dot" style="background:{squircle(s)}"></span>'
        f'{esc(s)} <b>{n}</b> <span class="muted">({round(100*n/src_total)}%)</span></div>'
        for s, n in sorted(by_source.items(), key=lambda kv: -kv[1]))

    focus_html = "".join(f"<li>{esc(f)}</li>" for f in focus)

    body = f"""<div class="wrap">
<header>
  <h1 class="serif">CareerOPS</h1>
  <div class="live"><span class="led" id="led"></span> <span id="mode">file mode</span> &middot; {generated}</div>
</header>

<div class="card banner">
  <div><div class="serif" style="font-size:17px">Land a full-time offer by {esc(target.isoformat()) if target else "2026"}</div>
  <div class="big">{goal_line}</div></div>
  <div class="big">Today {today.isoformat()}</div>
</div>

<div class="card focus"><h2 class="sec">Today's focus</h2><ul>{focus_html}</ul></div>

<div class="stats">
  <div class="stat"><div class="ring" style="--p:{ring_pct}"><span class="serif">{today_count}/{DAILY_GOAL}</span></div><div class="l">Today</div></div>
  <div class="stat"><div class="n serif">{last7}</div><div class="l">7 days</div></div>
  <div class="stat"><div class="n serif">{last30}</div><div class="l">30 days</div></div>
  <div class="stat"><div class="n serif">{streak}</div><div class="l">Day streak</div></div>
  <div class="stat"><div class="n serif">{resp_rate}%</div><div class="l">Response</div></div>
</div>

<div class="card" style="margin-top:16px"><h2 class="sec">Pipeline &middot; {len(applied)} total applied</h2>
  <div class="pipe-row">{pipe_html}</div></div>

<div class="card">
  <h2 class="sec">Today's apply queue &middot; packet {esc(queue.get("date",""))} &middot; {applyable_count} of {len(roles)} confirmed applyable &middot; <span id="applied-count">0</span> marked applied</h2>
  {queue_rows}
</div>

<div class="grid2">
  <div class="card"><h2 class="sec">Applications, last 14 days</h2><div class="bars">{bar_html}</div></div>
  <div class="card"><h2 class="sec">By source</h2>{src_html}</div>
</div>

<div class="card"><h2 class="sec">30-day activity</h2><div class="heat">{heat_html}</div></div>

<div class="card">
  <h2 class="sec">All applications</h2>
  <input id="search" class="search" placeholder="Filter by company or role..." oninput="filterApps(this.value)">
  <table><thead><tr><th>Company</th><th>Stage</th><th>Source</th><th>Location</th><th>Applied</th></tr></thead>
  <tbody id="apptbody">{table_rows}</tbody></table>
</div>

<div class="muted" style="text-align:center;margin-top:8px">
  Rendered from tracker/state.json. Run <code>scripts/serve_dashboard.py</code> for one-click
  write-back, or open as a file to use clipboard mode.
</div>
</div>
<div id="toast" class="toast"></div>"""

    return "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">" \
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">" \
           "<title>CareerOPS</title><style>" + STYLE + "</style></head><body>" + \
           body + "<script>" + SCRIPT + "</script></body></html>"


def queue_row(r):
    t = r.get("type", "onsite")
    color = TYPE_COLORS.get(t, "#5b5b5b")
    name = r.get("company", "?")
    applyable = r.get("applyable")
    reason = r.get("applyable_reason", "")
    done = r.get("applied") is True
    if applyable is True:
        badge = '<span class="conf yes" title="Link live and JD fits 0-1 yr">YES</span>'
    elif applyable is False:
        badge = '<span class="conf no" title="Do not apply">NO</span>'
    else:
        badge = '<span class="conf unk" title="Not yet verified">?</span>'
    sub = f'{esc(name)} &middot; {esc(r.get("location",""))}'
    if reason:
        sub += f'<div class="reason">{esc(reason)}</div>'
    role = r.get("role", "")
    loc = r.get("location", "")
    url = r.get("url", "#")
    key = esc(f"{name}|{role}")
    cmd = esc(f'/log-application "{name}" "{role}" "{loc}" {url}')
    btn_txt = "Applied &#10003;" if done else "I applied"
    btn_cls = "iapplied done" if done else "iapplied"
    row_cls = "qrow applied" if done else ("qrow dim" if applyable is False else "qrow")
    return f'''<div class="{row_cls}" data-key="{key}">
      <span class="logo" style="background:{squircle(name)}">{esc(name[:1])}</span>
      <div class="qmeta"><div class="qrole">{badge} {esc(role)}</div>
      <div class="qsub">{sub}</div><div class="reslinks">{resources(name)}</div></div>
      <span class="pill" style="background:{color}">{esc(t)}</span>
      <a class="apply" href="{esc(url)}" target="_blank" rel="noopener">Apply &#8599;</a>
      <button class="{btn_cls}" data-key="{key}" data-cmd="{cmd}"
        data-company="{esc(name)}" data-role="{esc(role)}" data-loc="{esc(loc)}"
        data-url="{esc(url)}" data-type="{esc(t)}">{btn_txt}</button>
    </div>'''


def app_row(a):
    name = a.get("company", "?")
    stage = a.get("stage", "Applied")
    color = STAGE_COLORS.get(stage, "#5b5b5b")
    url = a.get("url")
    company_cell = f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(name)}</a>' if url else esc(name)
    opts = "".join(
        f'<option value="{esc(s)}"{" selected" if s == stage else ""}>{esc(s)}</option>'
        for s in STAGES)
    sel = (f'<select class="stagesel" data-id="{esc(a.get("id",""))}" '
           f'style="border-color:{color};color:{color}">{opts}</select>')
    search_blob = esc(f'{name} {a.get("role","")}').lower()
    return f'''<tr data-search="{search_blob}">
      <td>{company_cell}<div class="muted">{esc(a.get("role",""))}</div>
      <div class="reslinks">{resources(name)}</div></td>
      <td>{sel}</td>
      <td>{esc(a.get("source",""))}</td>
      <td>{esc(a.get("location",""))}</td>
      <td class="mono">{esc(a.get("applied_date",""))}</td>
    </tr>'''


STYLE = """
:root{--bg:#efe9dc;--surface:#fbf7ed;--text:#0c0c0c;--muted:#6b6357;
--line:#ddd3c2;--green:#2e6b3e;--amber:#a16207;--red:#9c2f2f;--blue:#2b4a73;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.45}
.wrap{max-width:1100px;margin:0 auto;padding:28px 20px 60px}
.serif{font-family:"Iowan Old Style","Charter",Georgia,serif}
.mono{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:12px}
.muted{color:var(--muted);font-size:12px}
header{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
header h1{font-size:20px;margin:0;letter-spacing:.3px}
.live{font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px}
.live .led{width:8px;height:8px;border-radius:50%;background:var(--amber)}
.live .led.on{background:var(--green)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:13px;padding:18px;margin-bottom:16px}
.banner{display:flex;justify-content:space-between;align-items:center}
.banner .big{font-size:13px;color:var(--muted)}
.focus ul{margin:8px 0 0;padding-left:18px}.focus li{margin:3px 0;font-size:14px}
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:13px;padding:14px;text-align:center}
.stat .n{font-size:30px}.stat .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}
.ring{--p:0;width:64px;height:64px;border-radius:50%;margin:0 auto 6px;background:conic-gradient(var(--green) calc(var(--p)*1%),#e5dcca 0);display:flex;align-items:center;justify-content:center}
.ring span{width:50px;height:50px;border-radius:50%;background:var(--surface);display:flex;align-items:center;justify-content:center;font-size:15px}
.pipe-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.pipe{text-align:center;padding:8px}.pipe-n{font-size:26px}.pipe-l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}
h2.sec{font-size:13px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin:0 0 10px}
.qrow{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}
.qrow:last-child{border-bottom:none}
.logo{width:34px;height:34px;border-radius:9px;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600;flex:0 0 auto}
.qmeta{flex:1;min-width:0}.qrole{font-size:14px;font-weight:600}.qsub{font-size:12px;color:var(--muted)}
.pill{color:#fff;font-size:11px;padding:3px 9px;border-radius:20px;text-transform:capitalize}
.apply{font-size:13px;color:var(--blue);text-decoration:none;border:1px solid var(--line);padding:5px 11px;border-radius:8px}
.apply:hover{background:#f1ead9}
.qrow.dim{opacity:.5}
.conf{font-size:10px;font-weight:700;padding:1px 6px;border-radius:5px;margin-right:6px;vertical-align:middle;color:#fff}
.conf.yes{background:#2e6b3e}.conf.no{background:#9c2f2f}.conf.unk{background:#a16207}
.reason{font-size:11px;color:var(--muted);margin-top:2px;font-style:italic}
.reslinks{margin-top:4px;display:flex;flex-wrap:wrap;gap:6px}
.res{font-size:10px;color:var(--blue);text-decoration:none;border:1px solid var(--line);padding:1px 6px;border-radius:5px}
.res:hover{background:#f1ead9}
.iapplied{font-size:13px;color:var(--green);background:none;border:1px solid var(--line);padding:5px 11px;border-radius:8px;cursor:pointer;margin-left:6px;font-family:inherit;white-space:nowrap}
.iapplied:hover{background:#eef3ec}
.iapplied.done{background:var(--green);color:#fff;border-color:var(--green)}
.qrow.applied{opacity:.6}.qrow.applied .qrole{text-decoration:line-through}
.grid2{display:grid;grid-template-columns:1.4fr 1fr;gap:16px}
.bars{display:flex;align-items:flex-end;gap:5px;height:90px;margin-top:6px}
.bar-col{flex:1;text-align:center}.bar{border-radius:3px 3px 0 0}.bar-x{font-size:9px;color:var(--muted);margin-top:3px}
.heat{display:flex;flex-wrap:wrap;gap:4px}
.hcell{width:20px;height:20px;border-radius:4px}
.src{font-size:13px;padding:3px 0}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}
.search{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:8px;margin-bottom:10px;font-size:13px;background:var(--bg)}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);padding:6px 8px;border-bottom:1px solid var(--line)}
td{padding:8px;border-bottom:1px solid var(--line);vertical-align:top}
td a{color:var(--blue);text-decoration:none}
.stagesel{font-size:12px;padding:2px 4px;border-radius:6px;border:1px solid;background:var(--surface);font-family:inherit}
.empty{color:var(--muted);font-size:13px;padding:14px;text-align:center}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#0c0c0c;color:#fbf7ed;padding:10px 16px;border-radius:10px;font-size:13px;opacity:0;transition:opacity .3s;max-width:80%;text-align:center;z-index:50;pointer-events:none}
@media(max-width:760px){.stats{grid-template-columns:repeat(2,1fr)}.grid2{grid-template-columns:1fr}.pipe-row{grid-template-columns:repeat(2,1fr)}}
"""

SCRIPT = """
(function(){
  var SERVED = location.protocol === "http:" || location.protocol === "https:";
  var KEY = "careerops_applied";
  function load(){ try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch(e){ return {}; } }
  function save(o){ localStorage.setItem(KEY, JSON.stringify(o)); }
  var state = load();
  var toastEl = document.getElementById("toast");
  function toast(m){ toastEl.textContent = m; toastEl.style.opacity = "1"; clearTimeout(toastEl._h); toastEl._h = setTimeout(function(){ toastEl.style.opacity = "0"; }, 3200); }
  function setMode(){
    var led = document.getElementById("led"), m = document.getElementById("mode");
    if (SERVED){ led.classList.add("on"); m.textContent = "live (writes to tracker)"; }
    else { m.textContent = "file mode (clipboard)"; }
  }
  function markBtn(btn, on){
    var row = btn.closest(".qrow");
    if (on){ btn.innerHTML = "Applied \\u2713"; btn.classList.add("done"); if(row) row.classList.add("applied"); }
    else { btn.textContent = "I applied"; btn.classList.remove("done"); if(row) row.classList.remove("applied"); }
  }
  function refreshCount(){ var el = document.getElementById("applied-count"); if (el) el.textContent = Object.keys(state).length; }
  async function post(path, payload){
    var r = await fetch(path, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(payload) });
    if (!r.ok) throw new Error("bad status " + r.status);
    return r.json();
  }
  // Apply buttons
  document.querySelectorAll(".iapplied").forEach(function(btn){
    var k = btn.getAttribute("data-key");
    if (!SERVED && state[k]) markBtn(btn, true);
    btn.addEventListener("click", async function(){
      var payload = {
        key: k, company: btn.dataset.company, role: btn.dataset.role,
        location: btn.dataset.loc, url: btn.dataset.url, type: btn.dataset.type
      };
      if (SERVED){
        var on = !btn.classList.contains("done");
        try {
          await post(on ? "/api/applied" : "/api/unapply", payload);
          markBtn(btn, on);
          toast(on ? "Logged to tracker." : "Removed from tracker.");
        } catch(e){ toast("Server error: " + e.message); }
        return;
      }
      // file mode
      if (state[k]){ delete state[k]; save(state); markBtn(btn, false); refreshCount(); toast("Unmarked."); return; }
      state[k] = { at: new Date().toISOString() }; save(state); markBtn(btn, true); refreshCount();
      var cmd = btn.getAttribute("data-cmd");
      if (navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(cmd).then(
          function(){ toast("Marked applied. Log command copied, paste into Claude Code to save."); },
          function(){ toast("Marked applied. Run: " + cmd); });
      } else { toast("Marked applied. Run: " + cmd); }
    });
  });
  // Stage selects (server mode only persists; file mode shows a paste hint)
  document.querySelectorAll(".stagesel").forEach(function(sel){
    sel.addEventListener("change", async function(){
      var id = sel.getAttribute("data-id"), stage = sel.value;
      if (SERVED){
        try { await post("/api/stage", { id: id, stage: stage }); toast("Stage updated: " + stage); }
        catch(e){ toast("Server error: " + e.message); }
      } else {
        toast("File mode: run  /set-stage " + id + " \\"" + stage + "\\"  in Claude Code to save.");
      }
    });
  });
  // Search filter
  window.filterApps = function(q){
    q = (q || "").toLowerCase();
    document.querySelectorAll("#apptbody tr").forEach(function(tr){
      var blob = tr.getAttribute("data-search") || "";
      tr.style.display = blob.indexOf(q) === -1 ? "none" : "";
    });
  };
  setMode(); refreshCount();
})();
"""


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build())
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
