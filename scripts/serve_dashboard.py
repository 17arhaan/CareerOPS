#!/usr/bin/env python3
"""CareerOPS web app server with full write-back to tracker/state.json.

    python3 scripts/serve_dashboard.py        # then open http://localhost:8787

Serves the client-rendered app (scripts/webapp.py) and a JSON API:
  GET  /                 -> the app
  GET  /api/state        -> tracker/state.json
  POST /api/applied      -> log an application from a queue role
  POST /api/unapply      -> undo that
  POST /api/add          -> add a manual application
  POST /api/delete       -> delete an application by id
  POST /api/stage        -> change an application's stage
  POST /api/note         -> set an application's note
  POST /api/goal         -> set the target offer date

Localhost only, single lock around writes. Safe for one user. Every write also refreshes
the static dashboard/index.html snapshot.
"""
import json
import os
import threading
import time
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


def _load_dotenv():
    """Load KEY=VALUE lines from a project-root .env into the environment (no deps).
    Lets the AI copilot read ANTHROPIC_API_KEY from a file instead of `export`."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and val and not os.environ.get(key):
            os.environ[key] = val


_load_dotenv()

import assistant  # noqa: E402 — imported after .env load so the key is visible
import render_dashboard as rd  # noqa: E402
from webapp import APP_HTML  # noqa: E402

PORT = 8787
LOCK = threading.Lock()


def load_state():
    return json.loads(rd.STATE.read_text())


def save_state(state):
    state["as_of"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rd.STATE.write_text(json.dumps(state, indent=2) + "\n")
    try:
        rd.OUT.write_text(rd.build())  # keep the static snapshot fresh too
    except Exception:  # noqa: BLE001
        pass


def source_from_url(url):
    u = (url or "").lower()
    for host, name in [("indeed.", "Indeed"), ("linkedin.", "LinkedIn"),
                       ("greenhouse.", "Greenhouse"), ("lever.co", "Lever"),
                       ("ashbyhq.", "Ashby"), ("myworkdayjobs.", "Workday"),
                       ("naukri.", "Naukri")]:
        if host in u:
            return name
    return "Portal"


def h_applied(p):
    state = load_state()
    apps = state.setdefault("applied_companies", [])
    company, role = p.get("company", ""), p.get("role", "")
    if not any(a.get("company") == company and a.get("role") == role for a in apps):
        apps.append({
            "id": f"ui-{rd.slug(company)}-{date.today().isoformat()}",
            "company": company, "role": role, "location": p.get("location", ""),
            "url": p.get("url", ""), "source": source_from_url(p.get("url", "")),
            "applied_date": date.today().isoformat(), "stage": "Applied"})
    for r in state.get("current_queue", {}).get("roles", []):
        if f'{r.get("company")}|{r.get("role")}' == p.get("key"):
            r["applied"] = True
    save_state(state)
    return {"ok": True}


def h_unapply(p):
    state = load_state()
    company, role = p.get("company", ""), p.get("role", "")
    state["applied_companies"] = [
        a for a in state.get("applied_companies", [])
        if not (a.get("company") == company and a.get("role") == role
                and str(a.get("id", "")).startswith("ui-"))]
    for r in state.get("current_queue", {}).get("roles", []):
        if f'{r.get("company")}|{r.get("role")}' == p.get("key"):
            r.pop("applied", None)
    save_state(state)
    return {"ok": True}


def h_add(p):
    state = load_state()
    company = p.get("company", "")
    state.setdefault("applied_companies", []).append({
        "id": f"ui-{rd.slug(company)}-{date.today().isoformat()}-{len(state['applied_companies'])}",
        "company": company, "role": p.get("role", ""), "location": p.get("location", ""),
        "url": p.get("url", ""),
        "source": p.get("source") or source_from_url(p.get("url", "")),
        "applied_date": p.get("applied_date") or date.today().isoformat(),
        "stage": p.get("stage", "Applied")})
    save_state(state)
    return {"ok": True}


def h_delete(p):
    state = load_state()
    state["applied_companies"] = [a for a in state.get("applied_companies", [])
                                  if str(a.get("id", "")) != str(p.get("id"))]
    save_state(state)
    return {"ok": True}


def h_stage(p):
    state = load_state()
    for a in state.get("applied_companies", []):
        if str(a.get("id", "")) == str(p.get("id")):
            a["stage"] = p.get("stage", "Applied")
    save_state(state)
    return {"ok": True}


def h_note(p):
    state = load_state()
    for a in state.get("applied_companies", []):
        if str(a.get("id", "")) == str(p.get("id")):
            a["note"] = p.get("note", "")
    save_state(state)
    return {"ok": True}


def h_goal(p):
    state = load_state()
    state["target_offer_date"] = p.get("date") or None
    save_state(state)
    return {"ok": True}


def h_settings(p):
    state = load_state()
    s = state.setdefault("settings", {})
    if "daily_goal" in p:
        try:
            s["daily_goal"] = max(1, int(p["daily_goal"]))
        except (TypeError, ValueError):
            pass
    for key in ("user_name", "alumni_school_slug"):
        if key in p:
            val = str(p[key] or "").strip()
            if val:
                s[key] = val
            else:
                s.pop(key, None)
    save_state(state)
    return {"ok": True}


def _uid(prefix):
    return f"{prefix}-{int(time.time() * 1000)}"


def h_contact(p):
    state = load_state()
    cs = state.setdefault("contacts", [])
    op = p.get("op")
    if op == "add":
        cs.append({"id": _uid("c"), "company": p.get("company", ""), "name": p.get("name", ""),
                   "title": p.get("title", ""), "status": p.get("status", "To Reach"),
                   "link": p.get("link", ""), "note": p.get("note", "")})
    elif op == "update":
        for c in cs:
            if str(c.get("id")) == str(p.get("id")):
                for k in ("company", "name", "title", "status", "link", "note"):
                    if k in p:
                        c[k] = p[k]
    elif op == "delete":
        state["contacts"] = [c for c in cs if str(c.get("id")) != str(p.get("id"))]
    save_state(state)
    return {"ok": True}


def h_round(p):
    state = load_state()
    op = p.get("op")
    for a in state.get("applied_companies", []):
        if str(a.get("id")) == str(p.get("appId")):
            rounds = a.setdefault("rounds", [])
            if op == "add":
                rounds.append({"id": _uid("r"), "date": p.get("date", date.today().isoformat()),
                               "type": p.get("type", ""), "notes": p.get("notes", ""),
                               "outcome": p.get("outcome", "Pending")})
            elif op == "delete":
                a["rounds"] = [r for r in rounds if str(r.get("id")) != str(p.get("roundId"))]
    save_state(state)
    return {"ok": True}


# ---- AI assistant executors (each acquires LOCK for its own write) ----
def exec_get_state(_):
    state = load_state()
    applied = state.get("applied_companies", [])
    q = (state.get("current_queue") or {}).get("roles", [])
    return json.dumps({
        "total_applied": len(applied),
        "today_queue": [{"company": r.get("company"), "role": r.get("role"),
                         "applyable": r.get("applyable")} for r in q],
        "pipeline": [{"company": a.get("company"), "role": a.get("role"),
                      "stage": a.get("stage", "Applied"), "applied_date": a.get("applied_date")}
                     for a in applied]})


def exec_log_application(args):
    with LOCK:
        h_add({"company": args.get("company", ""), "role": args.get("role", ""),
               "location": args.get("location", ""), "url": args.get("url", ""),
               "stage": "Applied"})
    return f"Logged application: {args.get('company')} ({args.get('role', 'role n/a')})."


def exec_set_stage(args):
    company, stage = args.get("company", ""), args.get("stage", "Applied")
    with LOCK:
        state = load_state()
        matches = [a for a in state.get("applied_companies", [])
                   if a.get("company", "").lower() == company.lower()]
        if not matches:
            return f"No application found for {company}. Log it first?"
        matches.sort(key=lambda a: a.get("applied_date", ""), reverse=True)
        matches[0]["stage"] = stage
        save_state(state)
    return f"Set {company} to {stage}."


def exec_add_contact(args):
    with LOCK:
        h_contact({"op": "add", "name": args.get("name", ""), "company": args.get("company", ""),
                   "title": args.get("title", ""), "status": args.get("status", "To Reach")})
    return f"Added contact {args.get('name')}{' at ' + args.get('company') if args.get('company') else ''}."


CHAT_EXECUTORS = {"get_state": exec_get_state, "log_application": exec_log_application,
                  "set_stage": exec_set_stage, "add_contact": exec_add_contact}


def handle_chat(payload):
    reply = assistant.run_chat(payload.get("messages", []), CHAT_EXECUTORS)
    return {"reply": reply}


ROUTES = {"/api/applied": h_applied, "/api/unapply": h_unapply, "/api/add": h_add,
          "/api/delete": h_delete, "/api/stage": h_stage, "/api/note": h_note,
          "/api/goal": h_goal, "/api/settings": h_settings, "/api/contact": h_contact,
          "/api/round": h_round}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, APP_HTML, "text/html; charset=utf-8")
        elif path == "/api/state":
            self._send(200, rd.STATE.read_text(), "application/json")
        else:
            self._send(404, '{"error":"not found"}')

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or "{}")
        except Exception as e:  # noqa: BLE001
            return self._send(400, json.dumps({"error": str(e)}))
        # Chat runs the model loop without the global lock (its tool writes lock individually).
        if path == "/api/chat":
            try:
                self._send(200, json.dumps(handle_chat(payload)))
            except Exception as e:  # noqa: BLE001
                self._send(500, json.dumps({"error": str(e)}))
            return
        fn = ROUTES.get(path)
        if not fn:
            return self._send(404, '{"error":"unknown endpoint"}')
        try:
            with LOCK:
                result = fn(payload)
            self._send(200, json.dumps(result))
        except Exception as e:  # noqa: BLE001
            self._send(500, json.dumps({"error": str(e)}))


def main():
    print(f"CareerOPS app live at http://localhost:{PORT}   (Ctrl+C to stop)")
    print("Every action writes straight to tracker/state.json.")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
