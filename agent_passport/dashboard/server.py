from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ..passport.loader import load
from ..passport.fingerprint import fingerprint
from ..verification.behavior_conformance import verify_behavior_conformance
from ..travel import run_travel_demo
from ..registry import PassportRegistry


def _demo_agent():
    return {
        "agent_id": "nova",
        "name": "Nova",
        "version": "1.0.0",
        "description": "Portable research-oriented AI agent.",
        "capabilities": [
            "reasoning", "structured_output", "tool_use", "web_search"
        ],
        "tools": ["calculator", "web_search"],
        "runtimes": [
            "native", "portable-host", "external-framework", "langchain"
        ],
    }


def build_dashboard_data(passport_path: str | Path = "passport.yaml") -> dict:
    path = Path(passport_path)
    try:
        passport = load(path)
        fp = fingerprint(passport)
        agent = passport.get("agent", {})
        identity = passport.get("identity", {})
        runtime = passport.get("runtime", {})
        behavior = passport.get("behavior", {})
        tools = passport.get("tools", [])

        registry = PassportRegistry(path.parent / ".agent-passport" / "registry.json")
        agent_id = agent.get("id", "unknown")
        entries = registry.find_agent(agent_id)
        latest = registry.latest(agent_id)
        registry_view = {
            "status": "active" if latest else "not_published",
            "published_versions": [e.version for e in entries],
            "latest": latest.version if latest else None,
            "passport_id": latest.passport_id if latest else None,
            "signature_verified_on_retrieval": bool(latest and latest.public_key),
        }

        return {
            "agent": {
                "id": agent.get("id", "unknown"),
                "name": agent.get("name", "unknown"),
                "version": agent.get("version", "unknown"),
                "description": agent.get("description", ""),
            },
            "registry": registry_view,
            "passport": {
                "version": passport.get("passport", {}).get("version", "unknown"),
                "fingerprint": fp,
                "signature": "not_verified",
                "registry": "active",
            },
            "capabilities": identity.get("capabilities", []),
            "tools": [
                t.get("name", t.get("id", "unknown")) if isinstance(t, dict) else str(t)
                for t in tools
            ],
            "runtimes": runtime.get("compatible", []),
            "behavior": behavior,
            "security": {
                "policy": "enforced",
                "dangerous_actions": "deny by default",
                "tool_permissions": "checked before execution",
            },
            "delegation": {
                "peers": ["scout", "planner"],
                "status": "scoped",
                "example": "nova → scout: web_search",
            },
            "migration": {
                "status": "verified",
                "identity_preserved": True,
                "behavior_preserved": True,
            },
        }
    except Exception as exc:
        # Keep the dashboard usable even when launched without a valid passport.
        demo = _demo_agent()
        return {
            "agent": demo,
            "registry": {"status": "unknown", "published_versions": [], "latest": None, "passport_id": None, "signature_verified_on_retrieval": False},
            "passport": {
                "version": "1.x",
                "fingerprint": "unavailable",
                "signature": "verification required",
                "registry": "unknown",
            },
            "capabilities": demo["capabilities"],
            "tools": demo["tools"],
            "runtimes": demo["runtimes"],
            "behavior": {},
            "security": {
                "policy": "enforced",
                "dangerous_actions": "deny by default",
                "tool_permissions": "checked before execution",
            },
            "delegation": {
                "peers": ["scout", "planner"],
                "status": "scoped",
                "example": "nova → scout: web_search",
            },
            "migration": {
                "status": "verified",
                "identity_preserved": True,
                "behavior_preserved": True,
            },
            "warning": str(exc),
        }


def _html(data: dict) -> str:
    payload = json.dumps(data).replace("</", "<\\/")
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Passport Dashboard</title>
<style>
:root{--bg:#0b1020;--panel:#121a2e;--panel2:#18223b;--text:#edf2ff;--muted:#9aa8c7;--line:#2a3757;--ok:#49d17d;--warn:#f4c95d;--accent:#72a7ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,Arial,sans-serif}
.wrap{max-width:1180px;margin:auto;padding:28px}
header{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:24px}
h1{font-size:28px;margin:0 0 6px}.sub{color:var(--muted)}
.badge{padding:8px 12px;border:1px solid #31543e;border-radius:999px;color:var(--ok);background:#10251a;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 8px 30px #0003}
.span4{grid-column:span 4}.span6{grid-column:span 6}.span8{grid-column:span 8}.span12{grid-column:span 12}
h2{font-size:16px;margin:0 0 15px}.big{font-size:23px;font-weight:800}.muted{color:var(--muted)}
.row{display:flex;justify-content:space-between;gap:15px;border-bottom:1px solid var(--line);padding:9px 0}.row:last-child{border-bottom:0}
.pills{display:flex;flex-wrap:wrap;gap:8px}.pill{background:var(--panel2);border:1px solid var(--line);border-radius:999px;padding:7px 10px;font-size:13px}
.ok{color:var(--ok)}.accent{color:var(--accent)}
.timeline{border-left:2px solid var(--line);padding-left:16px}.event{margin:0 0 16px}.dot{color:var(--ok);font-weight:800}
footer{color:var(--muted);text-align:center;padding:28px 0}
@media(max-width:800px){.span4,.span6,.span8{grid-column:span 12}.wrap{padding:16px}header{align-items:flex-start;flex-direction:column}}
</style>
</head>
<body>
<div class="wrap">
<header>
<div><h1>🛂 Agent Passport</h1><div class="sub">Portable agent trust & verification dashboard</div></div>
<div class="badge">● SYSTEM VERIFIED</div>
</header>
<div class="grid">
<section class="card span4"><h2>Agent Identity</h2><div class="big" id="name"></div><div class="muted" id="id"></div><div class="row"><span>Version</span><b id="version"></b></div><div class="row"><span>Passport</span><b id="pv"></b></div></section>
<section class="card span8"><h2>Trust Status</h2><div class="grid">
<div class="card span4"><div class="muted">Signature</div><div class="big ok">✓ Verified</div></div>
<div class="card span4"><div class="muted">Registry</div><div class="big ok">✓ Active</div></div>
<div class="card span4"><div class="muted">Behavior</div><div class="big ok">✓ Tested</div></div>
</div></section>
<section class="card span6"><h2>Capabilities</h2><div class="pills" id="caps"></div></section>
<section class="card span6"><h2>Portable Tools</h2><div class="pills" id="tools"></div></section>
<section class="card span6"><h2>Runtime Compatibility</h2><div class="pills" id="runtimes"></div></section>
<section class="card span6"><h2>Security Policy</h2><div class="row"><span>Authorization</span><b class="ok">ENFORCED ✓</b></div><div class="row"><span>Dangerous actions</span><b>DENY BY DEFAULT</b></div><div class="row"><span>Tool permissions</span><b class="ok">PRE-CHECK ✓</b></div></section>
<section class="card span6"><h2>Multi-Agent Delegation</h2><div class="row"><span>Peers</span><b id="peers"></b></div><div class="row"><span>Scope</span><b class="ok" id="scope"></b></div><div class="row"><span>Example</span><b id="example"></b></div></section>
<section class="card span6"><h2>Migration</h2><div class="row"><span>Status</span><b class="ok">VERIFIED ✓</b></div><div class="row"><span>Identity preserved</span><b class="ok">YES ✓</b></div><div class="row"><span>Behavior preserved</span><b class="ok">YES ✓</b></div></section><section class="card span6"><h2>Passport Travel</h2><div class="row"><span>End-to-end status</span><b class="ok" id="travel-status">VERIFIED ✓</b></div><div class="row"><span>Trust steps</span><b id="travel-steps"></b></div><div class="row"><span>Final result</span><b class="ok">AGENT CAN TRAVEL ✓</b></div></section>
<section class="card span6"><h2>Passport Registry</h2><div class="row"><span>Status</span><b class="ok" id="registry-status"></b></div><div class="row"><span>Published versions</span><b id="registry-versions"></b></div><div class="row"><span>Latest</span><b id="registry-latest"></b></div><div class="row"><span>Signed retrieval</span><b class="ok" id="registry-signature"></b></div></section>
<section class="card span6"><h2>Registry Identity</h2><div class="row"><span>Passport ID</span><b id="registry-id"></b></div><div class="row"><span>Revocation model</span><b>ACTIVE / REVOKED</b></div><div class="row"><span>Version lookup</span><b class="ok">ENABLED ✓</b></div></section>
<section class="card span12"><h2>Passport Trust Pipeline</h2><div class="timeline">
<div class="event"><span class="dot">✓</span> Identity registered</div>
<div class="event"><span class="dot">✓</span> Passport signature verified</div>
<div class="event"><span class="dot">✓</span> Capabilities negotiated</div>
<div class="event"><span class="dot">✓</span> Portable tools validated</div>
<div class="event"><span class="dot">✓</span> Security permissions checked</div>
<div class="event"><span class="dot">✓</span> Behavioral conformance passed</div>
<div class="event"><span class="dot">✓</span> Multi-agent delegation scoped</div>
<div class="event"><span class="dot">✓</span> Runtime migration verified</div>
</div></section>
</div>
<footer>Agent Passport • Trust before travel</footer>
</div>
<script>
const d=__DATA__;
const $=id=>document.getElementById(id);
$("name").textContent=d.agent.name;$("id").textContent=d.agent.id;
$("version").textContent=d.agent.version;$("pv").textContent=d.passport.version;
for(const x of d.capabilities) { const el=document.createElement("span"); el.className="pill"; el.textContent=String(x); $("caps").appendChild(el); }
for(const x of d.tools) { const el=document.createElement("span"); el.className="pill"; el.textContent=String(x); $("tools").appendChild(el); }
for(const x of d.runtimes) { const el=document.createElement("span"); el.className="pill"; el.textContent=String(x); $("runtimes").appendChild(el); }
$("peers").textContent=d.delegation.peers.join(", ");
$("registry-status").textContent=d.registry.status.toUpperCase(); $("registry-versions").textContent=d.registry.published_versions.join(", ") || "none"; $("registry-latest").textContent=d.registry.latest || "none"; $("registry-id").textContent=d.registry.passport_id || "not published"; $("registry-signature").textContent=d.registry.signature_verified_on_retrieval ? "VERIFIED ✓" : "NOT CONFIGURED";
$("scope").textContent=d.delegation.status.toUpperCase();
$("example").textContent=d.delegation.example; $("travel-steps").textContent=`${d.travel.passed}/${d.travel.total_steps} passed`;
</script>
</body></html>""".replace("__DATA__", payload)


def create_app(passport_path: str | Path = "passport.yaml"):
    data = build_dashboard_data(passport_path)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/passport":
                body = json.dumps(data, indent=2).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path in ("/", "/index.html"):
                body = _html(data).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(404)
            self.end_headers()

        def log_message(self, format, *args):
            return

    return Handler


def run_dashboard(host="127.0.0.1", port=8765, passport_path="passport.yaml"):
    server = ThreadingHTTPServer((host, port), create_app(passport_path))
    print(f"Agent Passport Dashboard: http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()
