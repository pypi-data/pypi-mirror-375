from datetime import datetime, timezone
import pytz

def px(n: int) -> str:
    return f"{int(n)}px"

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def to_local_str(iso_str: str | None, tz_name: str) -> str:
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        if not dt.tzinfo:
            from datetime import timezone as tz
            dt = dt.replace(tzinfo=tz.utc)
        return dt.astimezone(pytz.timezone(tz_name)).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return str(iso_str)
 

# dataset_dashboard/constants.py
from typing import Tuple, Dict

# exact order (worst → best). keep 'other' at the end.
JOB_STATUS_ORDER = [
    "failed", "overdue", "manual", "retrying", "running",
    "allocated", "queued", "waiting", "succeeded", "other"
]

JOB_COLORS: Dict[str, str] = {
    "waiting":   "#F0E442",
    "retrying":  "#E69F00",
    "running":   "#56B4E9",
    "failed":    "#D55E00",
    "overdue":   "#A50E0E",
    "manual":    "#808080",
    "allocated": "#7759C2",
    "queued":    "#6C757D",
    "succeeded": "#009E73",
    "other":     "#999999",
}

JOB_SCORES: Dict[str, float] = {
    "failed": -1.0, "overdue": -0.8, "retrying": -0.3, "running": 0.5,
    "allocated": 0.2, "queued": 0.1, "waiting": 0.0, "manual": 0.2,
    "succeeded": 1.0, "other": 0.0,
}

def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

JOB_RGB = {k: _hex_to_rgb(v) for k, v in JOB_COLORS.items()}

# --- NEW: light-touch canonicalization map (all keys *lowercase*) ---
# We only map common variants; anything else falls back to 'other' safely.
STATUS_CANON: Dict[str, str] = {
    # success
    "success": "succeeded", "succeed": "succeeded", "ok": "succeeded", "done": "succeeded",
    # failure
    "fail": "failed", "error": "failed", "failed_job": "failed",
    # overdue / timeout
    "timeout": "overdue", "time_out": "overdue", "over_due": "overdue",
    # retrying
    "retry": "retrying", "retried": "retrying",
    # running
    "in_progress": "running", "processing": "running",
    # waiting / pending
    "pend": "waiting", "pending": "waiting",
    # queued / allocated
    "queue": "queued", "queued_up": "queued",
    "alloc": "allocated", "allocated_job": "allocated",
    # manual / paused
    "pause": "manual", "paused": "manual",
    # empty/unknown → handled in store as 'other'
}

services/StopIteration# dataset_dashboard/services/store.py
import os, json, tempfile, threading, pathlib, logging
from typing import Dict, List, Optional, Tuple
from ..constants import JOB_STATUS_ORDER, STATUS_CANON
from ..utils import utc_now_iso

log = logging.getLogger("dataset_dashboard.store")

class StoreService:
    ...
    # ---------- NEW: status normalization ----------
    _unknown_seen = set()  # type: ignore[attr-defined]

    @staticmethod
    def _canon_status(name) -> str:
        """Map common variants via STATUS_CANON; bin everything else to 'other'. Never raises."""
        try:
            s = (name or "").strip().lower()
        except Exception:
            s = ""
        if not s:
            return "other"
        s = STATUS_CANON.get(s, s)  # light-touch mapping
        if s not in JOB_STATUS_ORDER:
            # log each unknown at most once
            if s not in StoreService._unknown_seen:
                log.warning("Unknown status → 'other'", extra={"status": s})
                StoreService._unknown_seen.add(s)
            return "other"
        return s
    # ------------------------------------------------

    def _init(self) -> dict:
        return {
            "jobs": {},
            "logs": [],
            "meta": {"owner_labels": {}, "env": "demo", "last_ingest_at": None},
            "updated_at": utc_now_iso(),
        }

    def _ensure_leaf(self, store, owner: str, mode: str, data_name: str, stage: str) -> dict:
        jobs = store.setdefault("jobs", {})
        o = jobs.setdefault(owner, {})
        m = o.setdefault(mode, {})
        d = m.setdefault(data_name, {})
        leaf = d.setdefault(stage, {"chunks": [], "counts": {}, "errors": []})
        # ensure counts has *all* known keys (including 'other')
        if set(leaf.get("counts", {}).keys()) != set(JOB_STATUS_ORDER):
            leaf["counts"] = {s: 0 for s in JOB_STATUS_ORDER}
        return leaf

    def _recount(self, leaf: dict):
        leaf["counts"] = {s: 0 for s in JOB_STATUS_ORDER}
        for ch in leaf.get("chunks", []):
            st = self._canon_status(ch.get("status"))
            leaf["counts"][st] += 1

    def apply_snapshot_with_meta(self, items: List[dict], meta: Optional[dict] = None):
        store = self._load()

        # meta
        meta = meta or {}
        store_meta = store.setdefault("meta", {})
        if "env" in meta:
            store_meta["env"] = meta.get("env") or store_meta.get("env") or "demo"
        ingest_when = meta.get("last_ingest_at") or meta.get("ingested_at") or utc_now_iso()
        store_meta["last_ingest_at"] = ingest_when
        labels = store_meta.setdefault("owner_labels", {})

        # reset jobs, refill
        store["jobs"] = {}
        for it in items or []:
            owner_raw = (it.get("owner") or self.default_owner).strip()
            owner_key = owner_raw.lower()
            labels.setdefault(owner_key, owner_raw)

            mode  = (it.get("mode") or self.default_mode).strip().lower()
            dn    = it.get("data_name") or "unknown"
            stg   = (it.get("stage") or "stage").lower()

            leaf = self._ensure_leaf(store, owner_key, mode, dn, stg)
            # normalize each chunk’s status safely
            norm_chunks = []
            for ch in it.get("chunks") or []:
                ch = dict(ch or {})
                ch["status"] = self._canon_status(ch.get("status"))
                norm_chunks.append(ch)
            leaf["chunks"] = norm_chunks
            leaf["errors"] = list(it.get("errors", []))[-50:] if isinstance(it.get("errors"), list) else []
            self._recount(leaf)

        self._save(store)

table.
# dataset_dashboard/components/table.py
from ..constants import JOB_RGB

class TableComponent:
    ...
    @staticmethod
    def _shade(status: str | None, alpha=0.18):
        if not status or status not in JOB_RGB:
            # pick either a neutral white, or use the 'other' color
            # r,g,b = JOB_RGB["other"]; return {"backgroundColor": f"rgba({r},{g},{b},{alpha})"}
            return {"backgroundColor": "#FFFFFF"}
        r, g, b = JOB_RGB[status]
        return {"backgroundColor": f"rgba({r},{g},{b},{alpha})"}

test
#!/usr/bin/env python3
import requests, os
from datetime import datetime, timezone
DASH = os.getenv("DASH_URL", "http://127.0.0.1:8090/ingest_snapshot")
def iso_now(): return datetime.now(timezone.utc).isoformat()

payload = {
  "snapshot": [{
      "owner": "qsg", "mode": "live", "data_name": "dataset-xyz", "stage": "stage",
      "chunks": [
        {"id": "c0", "status": "teleporting", "proc": "https://x/p/1", "log": "/tmp/drm-logs/dataset-xyz/stage-0.log"},
        {"id": "c1", "status": "Queued_Up", "proc": "https://x/p/2", "log": "/tmp/drm-logs/dataset-xyz/stage-1.log"}
      ]
  }],
  "meta": {"env": "demo", "ingested_at": iso_now()}
}
r = requests.post(DASH, json=payload, timeout=10)
print(r.status_code, r.text)


# dataset_dashboard/port_guard.py
import os, socket, time, signal
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def _is_port_open(host: str, port: int, timeout: float = 0.2) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0

def _pidfile(port: int) -> Path:
    base = Path.home() / ".dataset_dashboard" / "pids"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{port}.pid"

def write_pidfile(port: int) -> None:
    _pidfile(port).write_text(str(os.getpid()), encoding="utf-8")

def read_pidfile(port: int) -> int | None:
    try:
        txt = _pidfile(port).read_text(encoding="utf-8").strip()
        return int(txt) if txt else None
    except Exception:
        return None

def remove_pidfile(port: int) -> None:
    try:
        _pidfile(port).unlink(missing_ok=True)  # py3.8+: wrap in try/except if older
    except Exception:
        pass

def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        # signal 0 checks existence
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # exists but we may not be able to signal it
        return True
    except Exception:
        return False

def http_shutdown(host: str, port: int, token: str | None, timeout: float = 0.8) -> bool:
    url = f"http://{host}:{port}/__shutdown__"
    data = b"token=" + (token or "").encode("utf-8")
    req = Request(url, data=data, method="POST")
    if token:
        req.add_header("X-Auth-Token", token)
    try:
        urlopen(req, timeout=timeout).read()
        return True
    except (HTTPError, URLError, TimeoutError, ConnectionError, OSError):
        return False

def kill_pid(pid: int) -> bool:
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception:
        pass
    time.sleep(0.25)
    if is_pid_running(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
        time.sleep(0.25)
    return not is_pid_running(pid)

def next_free_port(start: int, host: str = "127.0.0.1", limit: int = 20) -> int:
    port = int(start)
    for _ in range(limit):
        if not _is_port_open(host, port):
            return port
        port += 1
    return start  # fallback

def ensure_free_or_kill_own(host: str, port: int, token: str | None) -> tuple[bool, int]:
    """
    Returns (ok, port). If the desired port is busy, tries to shut down the *same app*:
      1) POST /__shutdown__ with token (localhost only)
      2) If a pidfile exists for that port, kill the PID
      3) If still busy, pick the next free port
    """
    if not _is_port_open(host, port):
        return True, port

    # try HTTP shutdown first (graceful)
    if http_shutdown("127.0.0.1", port, token):
        time.sleep(0.5)
        if not _is_port_open(host, port):
            return True, port

    # PID file path (only our app writes this)
    pid = read_pidfile(port)
    if pid and is_pid_running(pid):
        if kill_pid(pid):
            time.sleep(0.3)
            if not _is_port_open(host, port):
                remove_pidfile(port)
                return True, port

    # could be another process; pick a free port automatically
    new_port = next_free_port(port + 1, host)
    return False, new_port

from dash import Dash
import dash_bootstrap_components as dbc
import os
from flask import request, abort

from .config import load_config
from .dashboard import DashboardHost
from .inject import register_ingest_routes, register_callbacks
from .library import make_dummy_payload
from .port_guard import ensure_free_or_kill_own, write_pidfile

def create_app():
    cfg = load_config()
    app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], title=cfg.app_title)

    # local-only shutdown route (graceful)
    SHUT_TOKEN = os.getenv("SHUTDOWN_TOKEN", "")
    @app.server.post("/__shutdown__")
    def _shutdown():
        # only allow from localhost
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return abort(403)
        token = request.headers.get("X-Auth-Token") or request.form.get("token") or ""
        if token != SHUT_TOKEN:
            return abort(403)
        func = request.environ.get("werkzeug.server.shutdown")
        if func is None:
            return ("No shutdown function", 500)
        func()
        return ("OK", 200)

    host = DashboardHost(app, cfg, make_items_callable=lambda: make_dummy_payload(cfg))
    app.layout = host.layout
    register_ingest_routes(app.server, host)
    register_callbacks(app, cfg, host)
    host.start_services()
    return app, app.server

if __name__ == "__main__":
    app, server = create_app()

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("APP_PORT", "8090")))
    token = os.getenv("SHUTDOWN_TOKEN", "")

    ok, chosen_port = ensure_free_or_kill_own("127.0.0.1", port, token)
    if not ok and chosen_port != port:
        print(f"[port-guard] Port {port} busy; switching to {chosen_port}")
    write_pidfile(chosen_port)  # record *our* PID for future runs

    app.run(host=host, port=chosen_port, debug=os.getenv("DEBUG","0")=="1", use_reloader=False)

export PORT=8090
export SHUTDOWN_TOKEN=secret123
python -m dataset_dashboard.app