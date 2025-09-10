# dataset_dashboard/services/logs.py
from __future__ import annotations
import pathlib, threading, hashlib
from typing import Any, Optional
from urllib.parse import quote
from flask import Response, abort

class LogLinker:
    """
    Translates raw log paths/URLs to safe viewer hrefs your Dash app can open.

    - http(s) URLs -> returned as-is
    - absolute path inside LOG_ROOT -> "/logview/root/<rel>"
    - absolute path outside LOG_ROOT -> cached/lazy "/logview/mem/<key>" (remembers original path)
    - relative path -> treated as inside LOG_ROOT -> "/logview/root/<rel>"
    """
    def __init__(self, log_root: pathlib.Path | str):
        self.root = pathlib.Path(log_root).resolve()
        self._mem: dict[str, str] = {}        # key -> file text
        self._mem_index: dict[str, str] = {}  # key -> original absolute path
        self._lock = threading.RLock()

    def _key_for_abs(self, abs_path: pathlib.Path) -> str:
        h = hashlib.sha1(str(abs_path).encode("utf-8")).hexdigest()[:16]
        return f"abs/{h}/{abs_path.name}"

    def _read_text(self, p: pathlib.Path) -> Optional[str]:
        try:
            return p.read_text("utf-8", errors="replace")
        except Exception:
            try:
                return p.read_bytes().decode("utf-8", errors="replace")
            except Exception:
                return None

    def href_for(self, value: Optional[str]) -> Optional[str]:
        """
        Return an absolute URL (starting with "/") for the viewer routes, or None if not possible.
        """
        if not value:
            return None
        v = str(value).strip()
        if v.startswith("http://") or v.startswith("https://"):
            return v

        p = pathlib.Path(v)
        try:
            if p.is_absolute():
                abs_p = p.resolve()
                # Inside LOG_ROOT -> serve as /logview/root/<rel>
                try:
                    rel = abs_p.relative_to(self.root).as_posix()
                    return f"/logview/root/{quote(rel)}"
                except Exception:
                    # Outside LOG_ROOT -> allocate a mem key; cache now if readable
                    key = self._key_for_abs(abs_p)
                    txt = self._read_text(abs_p)
                    with self._lock:
                        self._mem_index[key] = str(abs_p)
                        if txt is not None:
                            self._mem.setdefault(key, txt)
                    return f"/logview/mem/{quote(key)}"
            else:
                # Relative -> treat as under LOG_ROOT
                rel = p.as_posix().lstrip("./")
                if ".." in rel:
                    return None
                return f"/logview/root/{quote(rel)}"
        except Exception:
            return None


def _html_page(title: str, body_text: str, full_path: Optional[str] = None) -> str:
    from html import escape
    meta_html = (
        f"<div class='meta'>Path: <code id='logpath'>{escape(full_path)}</code> "
        f"<button onclick=\"navigator.clipboard.writeText("
        f"document.getElementById('logpath').textContent)\">Copy</button></div>"
        if full_path else
        f"<div class='meta'>{escape(title)}</div>"
    )
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{escape(title)}</title>
    <style>
      body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; margin:16px; }}
      pre {{ white-space: pre-wrap; word-break: break-word; }}
      .meta {{ color:#666; margin-bottom:8px; }}
      code {{ background:#f5f5f5; padding:2px 4px; border-radius:4px; }}
      button {{ margin-left:8px; }}
    </style>
  </head>
  <body>
    {meta_html}
    <pre>{escape(body_text)}</pre>
  </body>
</html>"""


def _ensure_linker(linker_or_root: Any) -> LogLinker:
    return linker_or_root if isinstance(linker_or_root, LogLinker) else LogLinker(linker_or_root)


def register_log_routes(server, linker_or_root: LogLinker | str | pathlib.Path):
    """
    Register viewer + debug endpoints:

      GET /logview/root/<rel>  -> HTML viewer for files under LOG_ROOT
      GET /logview/mem/<key>   -> HTML viewer for cached absolute files
      GET /logs/<rel>          -> (debug) plain text under LOG_ROOT
      GET /logmem/<key>        -> (debug) plain text from mem
    """
    linker = _ensure_linker(linker_or_root)
    root = linker.root

    @server.get("/logview/root/<path:rel>")
    def logview_root(rel: str):
        clean = rel.lstrip("/").replace("\\", "/")
        if ".." in clean:
            return abort(400)
        path = (root / clean).resolve()
        try:
            path.relative_to(root)
        except Exception:
            return Response(_html_page("Log outside root", f"(outside root) {clean}"),
                            mimetype="text/html")
        if not path.exists():
            return Response(_html_page("Log not found", clean, full_path=str(path)),
                            mimetype="text/html", status=404)
        txt = linker._read_text(path) or ""
        return Response(_html_page(f"Log: {clean}", txt, full_path=str(path)),
                        mimetype="text/html")

    @server.get("/logview/mem/<path:key>")
    def logview_mem(key: str):
        clean = key.lstrip("/").replace("\\", "/")
        with linker._lock:
            txt = linker._mem.get(clean)
            origin = linker._mem_index.get(clean)

        # Lazy load if not cached yet but original path is known
        if txt is None and origin:
            p = pathlib.Path(origin)
            txt2 = linker._read_text(p)
            if txt2 is not None:
                with linker._lock:
                    linker._mem[clean] = txt2
                txt = txt2

        if txt is None:
            full = origin or clean
            return Response(_html_page("Log not available", f"(not found) {full}", full_path=origin),
                            mimetype="text/html", status=404)

        return Response(_html_page(f"Log (cached): {clean}", txt, full_path=origin),
                        mimetype="text/html")

    # Optional plain-text debug endpoints
    @server.get("/logs/<path:rel>")
    def logs_plain(rel: str):
        clean = rel.lstrip("/").replace("\\", "/")
        if ".." in clean:
            return abort(400)
        p = (root / clean).resolve()
        try:
            p.relative_to(root)
        except Exception:
            return Response(f"(outside root) {clean}", mimetype="text/plain")
        if not p.exists():
            return Response(f"(log not found: {clean})", mimetype="text/plain", status=404)
        txt = linker._read_text(p) or ""
        return Response(txt, mimetype="text/plain")

    @server.get("/logmem/<path:key>")
    def logmem_plain(key: str):
        clean = key.lstrip("/").replace("\\", "/")
        with linker._lock:
            txt = linker._mem.get(clean)
        if txt is None:
            return Response(f"(log not cached: {clean})", mimetype="text/plain", status=404)
        return Response(txt, mimetype="text/plain")


__all__ = ["LogLinker", "register_log_routes"]