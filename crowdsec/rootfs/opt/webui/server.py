#!/usr/bin/env python3
"""Small JSON API around cscli for the CrowdSec add-on web UI.

Listens on 127.0.0.1 only; nginx in front of it handles ingress and
restricts access to the Home Assistant supervisor.
"""

import ipaddress
import json
import os
import re
import signal
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

CSCLI = os.environ.get("CSCLI_BIN", "cscli")
CONFIG_FILE = os.environ.get("CONFIG_FILE", "/config/.storage/crowdsec/config/config.yaml")
LISTEN_HOST = os.environ.get("WEBUI_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("WEBUI_PORT", "8099"))
TIMEOUT = 120

HUB_TYPES = {
    "collections", "parsers", "scenarios", "postoverflows",
    "contexts", "appsec-configs", "appsec-rules",
}
NAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+(/[A-Za-z0-9_.\-]+)?$")
DURATION_RE = re.compile(r"^(\d+h)?(\d+m)?(\d+s)?$")
REASON_RE = re.compile(r"^[\w .,:;!?()'\-/]{0,200}$")


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def cscli(*args, as_json=True):
    cmd = [CSCLI, "-c", CONFIG_FILE, *args]
    if as_json:
        cmd += ["-o", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
    except FileNotFoundError:
        raise ApiError(500, "cscli not found")
    except subprocess.TimeoutExpired:
        raise ApiError(504, "cscli timed out")
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout).strip().splitlines()
        raise ApiError(502, msg[-1] if msg else "cscli failed")
    if not as_json:
        return proc.stdout.strip()
    out = proc.stdout.strip()
    if not out or out == "null":
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        raise ApiError(502, "cscli returned invalid JSON")


def as_list(value):
    return value if isinstance(value, list) else []


# ---------------------------------------------------------------- validators

def v_ip_or_range(value):
    value = str(value or "").strip()
    try:
        if "/" in value:
            ipaddress.ip_network(value, strict=False)
            return "range", value
        ipaddress.ip_address(value)
        return "ip", value
    except ValueError:
        raise ApiError(400, "invalid IP or range")


def v_duration(value):
    value = str(value or "4h").strip()
    if not value or not DURATION_RE.match(value):
        raise ApiError(400, "invalid duration (use e.g. 4h, 30m, 168h)")
    return value


def v_hub(body):
    kind = str(body.get("type", ""))
    name = str(body.get("name", "")).strip()
    if kind not in HUB_TYPES:
        raise ApiError(400, "invalid hub type")
    if not NAME_RE.match(name):
        raise ApiError(400, "invalid hub item name")
    return kind, name


def v_name(value, what):
    value = str(value or "").strip()
    if not re.match(r"^[A-Za-z0-9_.@\-]{1,64}$", value):
        raise ApiError(400, f"invalid {what} name")
    return value


def v_int(value, what):
    try:
        return str(int(value))
    except (TypeError, ValueError):
        raise ApiError(400, f"invalid {what}")


# ------------------------------------------------------------------ handlers

def crowdsec_pids():
    pids = []
    try:
        entries = os.listdir("/proc")
    except OSError:
        return pids
    for entry in entries:
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/comm") as fh:
                if fh.read().strip() == "crowdsec":
                    pids.append(int(entry))
        except OSError:
            continue
    return pids


def reload_crowdsec():
    """Ask the crowdsec agent to reload its configuration (SIGHUP)."""
    pids = crowdsec_pids()
    if not pids:
        raise ApiError(503, "crowdsec process not found")
    for pid in pids:
        os.kill(pid, signal.SIGHUP)
    return {"reloaded": len(pids)}


def get_status(_q):
    version = ""
    try:
        version = cscli("version", as_json=False).splitlines()[0]
    except ApiError:
        pass
    running = bool(crowdsec_pids())
    lapi = ""
    try:
        lapi = cscli("lapi", "status", as_json=False)
    except ApiError as err:
        lapi = err.message
    return {"version": version, "running": running, "lapi": lapi}


def get_decisions(q):
    args = ["decisions", "list"]
    if q.get("all") == ["1"]:
        args.append("-a")
    alerts = as_list(cscli(*args))
    rows = []
    for alert in alerts:
        source = alert.get("source") or {}
        for dec in as_list(alert.get("decisions")):
            rows.append({
                "id": dec.get("id"),
                "value": dec.get("value"),
                "scope": dec.get("scope"),
                "type": dec.get("type"),
                "origin": dec.get("origin"),
                "scenario": dec.get("scenario"),
                "duration": dec.get("duration"),
                "country": source.get("cn", ""),
                "as_name": source.get("as_name", ""),
                "alert_id": alert.get("id"),
                "created_at": alert.get("created_at"),
            })
    return rows


def add_decision(body):
    scope, value = v_ip_or_range(body.get("value"))
    duration = v_duration(body.get("duration"))
    reason = str(body.get("reason") or "manual ban from web UI").strip()
    if not REASON_RE.match(reason):
        raise ApiError(400, "invalid reason")
    kind = str(body.get("type") or "ban")
    if kind not in ("ban", "captcha"):
        raise ApiError(400, "invalid decision type")
    out = cscli("decisions", "add", f"--{scope}", value, "--duration", duration,
                "--reason", reason, "--type", kind, as_json=False)
    return {"message": out}


def delete_decision(body):
    if body.get("id") is not None:
        out = cscli("decisions", "delete", "--id", v_int(body["id"], "id"), as_json=False)
    else:
        scope, value = v_ip_or_range(body.get("value"))
        out = cscli("decisions", "delete", f"--{scope}", value, as_json=False)
    return {"message": out}


def get_alerts(q):
    limit = v_int((q.get("limit") or ["100"])[0], "limit")
    alerts = as_list(cscli("alerts", "list", "--limit", limit))
    rows = []
    for alert in alerts:
        source = alert.get("source") or {}
        rows.append({
            "id": alert.get("id"),
            "scenario": alert.get("scenario"),
            "value": source.get("value") or source.get("ip") or source.get("range"),
            "scope": source.get("scope"),
            "country": source.get("cn", ""),
            "as_name": source.get("as_name", ""),
            "events_count": alert.get("events_count"),
            "decisions": len(as_list(alert.get("decisions"))),
            "machine_id": alert.get("machine_id"),
            "created_at": alert.get("created_at") or alert.get("start_at"),
        })
    return rows


def delete_alert(body):
    out = cscli("alerts", "delete", "--id", v_int(body.get("id"), "id"), as_json=False)
    return {"message": out}


def get_hub(q):
    args = ["hub", "list"]
    if q.get("all") == ["1"]:
        args.append("-a")
    data = cscli(*args) or {}
    result = {}
    for kind, items in data.items():
        result[kind] = [{
            "name": i.get("name"),
            "status": i.get("status") or i.get("utf8_status", ""),
            "local_version": i.get("local_version", ""),
            "version": i.get("version", ""),
            "description": i.get("description", ""),
            "installed": bool(i.get("installed", i.get("local_version"))),
        } for i in as_list(items)]
    return result


def hub_install(body):
    kind, name = v_hub(body)
    return {"message": cscli(kind, "install", name, as_json=False)}


def hub_remove(body):
    kind, name = v_hub(body)
    return {"message": cscli(kind, "remove", name, as_json=False)}


def hub_upgrade(_body):
    cscli("hub", "update", as_json=False)
    return {"message": cscli("hub", "upgrade", as_json=False)}


def get_bouncers(_q):
    return as_list(cscli("bouncers", "list"))


def add_bouncer(body):
    name = v_name(body.get("name"), "bouncer")
    key = cscli("bouncers", "add", name, "-o", "raw", as_json=False)
    return {"name": name, "key": key.splitlines()[-1] if key else ""}


def delete_bouncer(body):
    name = v_name(body.get("name"), "bouncer")
    return {"message": cscli("bouncers", "delete", name, as_json=False)}


def get_machines(_q):
    return as_list(cscli("machines", "list"))


def v_allowlist_value(value):
    """An allowlist entry is an IP or a CIDR range."""
    return v_ip_or_range(value)[1]


def v_expiration(value):
    value = str(value or "").strip()
    if not value:
        return ""
    if not re.match(r"^(\d+d)?(\d+h)?(\d+m)?$", value):
        raise ApiError(400, "invalid expiration (use e.g. 7d, 24h, 30m)")
    return value


def get_allowlists(_q):
    rows = []
    for al in as_list(cscli("allowlists", "list")):
        items = []
        for item in as_list(al.get("items")):
            exp = item.get("expiration") or ""
            items.append({
                "value": item.get("value"),
                "comment": item.get("description", ""),
                # zero time means "never expires"
                "expiration": "" if exp.startswith("0001-01-01") else exp,
                "created_at": item.get("created_at"),
            })
        rows.append({
            "name": al.get("name"),
            "description": al.get("description", ""),
            "console_managed": bool(al.get("console_managed")),
            "created_at": al.get("created_at"),
            "items": items,
        })
    return rows


def create_allowlist(body):
    name = v_name(body.get("name"), "allowlist")
    desc = str(body.get("description") or name).strip()
    if not REASON_RE.match(desc):
        raise ApiError(400, "invalid description")
    return {"message": cscli("allowlists", "create", name, "-d", desc, as_json=False)}


def delete_allowlist(body):
    name = v_name(body.get("name"), "allowlist")
    return {"message": cscli("allowlists", "delete", name, as_json=False)}


def allowlist_add(body):
    name = v_name(body.get("name"), "allowlist")
    value = v_allowlist_value(body.get("value"))
    args = ["allowlists", "add", name, value]
    exp = v_expiration(body.get("expiration"))
    if exp:
        args += ["-e", exp]
    comment = str(body.get("comment") or "").strip()
    if comment:
        if not REASON_RE.match(comment):
            raise ApiError(400, "invalid comment")
        args += ["-d", comment]
    return {"message": cscli(*args, as_json=False)}


def allowlist_remove(body):
    name = v_name(body.get("name"), "allowlist")
    value = v_allowlist_value(body.get("value"))
    return {"message": cscli("allowlists", "remove", name, value, as_json=False)}


def allowlist_check(body):
    value = v_allowlist_value(body.get("value"))
    return {"message": cscli("allowlists", "check", value, as_json=False)}


def get_metrics(_q):
    return cscli("metrics") or {}


def post_reload(_body):
    return reload_crowdsec()


GET_ROUTES = {
    "/api/status": get_status,
    "/api/decisions": get_decisions,
    "/api/alerts": get_alerts,
    "/api/hub": get_hub,
    "/api/bouncers": get_bouncers,
    "/api/machines": get_machines,
    "/api/metrics": get_metrics,
    "/api/allowlists": get_allowlists,
}
POST_ROUTES = {
    "/api/decisions/add": add_decision,
    "/api/decisions/delete": delete_decision,
    "/api/alerts/delete": delete_alert,
    "/api/hub/install": hub_install,
    "/api/hub/remove": hub_remove,
    "/api/hub/upgrade": hub_upgrade,
    "/api/bouncers/add": add_bouncer,
    "/api/bouncers/delete": delete_bouncer,
    "/api/reload": post_reload,
    "/api/allowlists/create": create_allowlist,
    "/api/allowlists/delete": delete_allowlist,
    "/api/allowlists/add": allowlist_add,
    "/api/allowlists/remove": allowlist_remove,
    "/api/allowlists/check": allowlist_check,
}


class Handler(BaseHTTPRequestHandler):
    server_version = "crowdsec-webui"

    def log_message(self, fmt, *args):
        if os.environ.get("WEBUI_DEBUG"):
            sys.stderr.write("webui: " + fmt % args + "\n")

    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _dispatch(self, routes, arg_fn):
        path = urlparse(self.path).path.rstrip("/")
        handler = routes.get(path)
        if handler is None:
            return self._send(404, {"error": "not found"})
        try:
            self._send(200, handler(arg_fn()))
        except ApiError as err:
            self._send(err.status, {"error": err.message})
        except Exception as err:  # pragma: no cover - last resort
            self._send(500, {"error": str(err)})

    def do_GET(self):
        self._dispatch(GET_ROUTES, lambda: parse_qs(urlparse(self.path).query))

    def do_POST(self):
        def body():
            length = int(self.headers.get("Content-Length") or 0)
            if length > 64 * 1024:
                raise ApiError(413, "request too large")
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                raise ApiError(400, "invalid JSON")
            if not isinstance(data, dict):
                raise ApiError(400, "invalid JSON")
            return data
        self._dispatch(POST_ROUTES, body)


def main():
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    print(f"CrowdSec web UI API listening on {LISTEN_HOST}:{LISTEN_PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
