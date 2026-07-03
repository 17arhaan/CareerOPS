#!/usr/bin/env python3
"""CareerOPS AI assistant, a job-search copilot powered by Claude (Anthropic SDK).

Grounded in the user's profile, resume, preferences, and live tracker state. It can
answer questions AND take actions (log applications, change stages, add contacts)
via tool use.

Enable it with:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
then restart scripts/serve_dashboard.py.

If the SDK or key is missing, run_chat() returns a friendly setup message instead of
crashing, so the rest of the app keeps working.
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "tracker" / "state.json"
PROFILE = ROOT / "profile" / "profile.md"
RESUME = ROOT / "resume" / "current.md"
PREFS = ROOT / "preferences" / "job-search-preferences.md"

MODEL = "claude-opus-4-8"
MAX_TOKENS = 6000

SETUP_MSG = (
    "The AI copilot just needs your Anthropic API key. One time:\n\n"
    "1. Get a key at console.anthropic.com (API Keys; billing must be set up).\n"
    "2. Paste it into the `.env` file in the project root: `ANTHROPIC_API_KEY=sk-ant-...`\n"
    "3. Restart `python3 scripts/serve_dashboard.py`.\n\n"
    "That's it. (`pip install anthropic` is already done.) Then I can answer questions and "
    "act on your tracker right here."
)

# Tool schemas exposed to Claude. Execution is supplied by the caller (the server),
# so the tools run under the same lock that guards every other state write.
TOOLS = [
    {"name": "get_state", "description": "Get the current job-search state: counts, today's queue, and the pipeline of applied companies with their stages. Call this before answering anything about progress, the queue, or what to do next.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "log_application", "description": "Log a new job application to the tracker.",
     "input_schema": {"type": "object", "properties": {
         "company": {"type": "string"}, "role": {"type": "string"},
         "location": {"type": "string"}, "url": {"type": "string"}},
         "required": ["company"]}},
    {"name": "set_stage", "description": "Update the pipeline stage of an existing application, matched by company name (most recent if several).",
     "input_schema": {"type": "object", "properties": {
         "company": {"type": "string"},
         "stage": {"type": "string", "enum": ["Applied", "Screening", "Online Assessment", "Phone Screen", "Interviewing", "Onsite", "Offered", "Rejected", "Withdrawn"]}},
         "required": ["company", "stage"]}},
    {"name": "add_contact", "description": "Add a networking contact (recruiter, alumni, referrer) to the CRM.",
     "input_schema": {"type": "object", "properties": {
         "name": {"type": "string"}, "company": {"type": "string"},
         "title": {"type": "string"},
         "status": {"type": "string", "enum": ["To Reach", "Reached Out", "Replied", "Referred", "No Reply"]}},
         "required": ["name"]}},
]


def _read(p):
    try:
        return p.read_text()
    except OSError:
        return ""


def build_system():
    state = json.loads(_read(STATE) or "{}")
    applied = state.get("applied_companies", [])
    queue = (state.get("current_queue") or {}).get("roles", [])
    summary = {
        "total_applied": len(applied),
        "target_offer_date": state.get("target_offer_date"),
        "queue_today": [f'{r.get("company")} - {r.get("role")} ({"applyable" if r.get("applyable") else "skip"})' for r in queue],
        "pipeline": [f'{a.get("company")}: {a.get("stage", "Applied")}' for a in applied],
    }
    profile = _read(PROFILE)
    if not profile.strip():
        profile = ("(No profile found. Tell the user to run /setup in Claude Code in the "
                   "project folder to personalize CareerOPS, then restart the server.)")
    return (
        "You are CareerOPS, the user's personal job-search copilot, embedded in their "
        "tracking app. Be direct and concise, peer to peer. Everything about who they are, "
        "their goal, their cover letter rules, and their writing style is in the PROFILE "
        "section below; follow it exactly (including any punctuation rules) in everything "
        "you write.\n\n"
        "You can take real actions with your tools (log applications, change stages, add "
        "contacts). When they tell you they applied somewhere, log it. When they report an "
        "interview or rejection, update the stage. Confirm what you did in one line.\n\n"
        "When asked for a cover letter, follow the profile's cover letter rules: the length, "
        "the opening, one work story plus one personal project from the flagship stories, "
        "no recruiter-bait words, and the exact signature.\n\n"
        "=== PROFILE ===\n" + profile + "\n\n"
        "=== RESUME ===\n" + _read(RESUME) + "\n\n"
        "=== PREFERENCES ===\n" + _read(PREFS) + "\n\n"
        "=== LIVE TRACKER SNAPSHOT ===\n" + json.dumps(summary, indent=2)
    )


def run_chat(history, executors):
    """history: [{role, content}]. executors: {tool_name: fn(dict)->str}. Returns reply text."""
    try:
        import anthropic
    except ImportError:
        return SETUP_MSG
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        return SETUP_MSG
    try:
        client = anthropic.Anthropic()
    except Exception:  # noqa: BLE001 — invalid config
        return SETUP_MSG

    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    system = build_system()
    try:
        for _ in range(6):  # bounded agentic loop
            resp = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS, system=system,
                thinking={"type": "adaptive"}, tools=TOOLS, messages=messages)
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text").strip() \
                    or "(no reply)"
            messages.append({"role": "assistant", "content": resp.content})
            results = []
            for b in resp.content:
                if b.type == "tool_use":
                    fn = executors.get(b.name)
                    try:
                        out = fn(b.input) if fn else f"Unknown tool {b.name}"
                    except Exception as e:  # noqa: BLE001
                        out = f"Error: {e}"
                    results.append({"type": "tool_result", "tool_use_id": b.id,
                                    "content": str(out)})
            messages.append({"role": "user", "content": results})
        return "(stopped after several tool steps; ask me to continue)"
    except anthropic.APIError as e:
        return f"AI error: {getattr(e, 'message', str(e))}"
    except Exception as e:  # noqa: BLE001
        return f"AI error: {e}"
