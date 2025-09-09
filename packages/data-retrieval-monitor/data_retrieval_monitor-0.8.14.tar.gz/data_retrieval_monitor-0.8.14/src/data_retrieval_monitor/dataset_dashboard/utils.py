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
    
def _clipboard_button(self, text: str):
    """
    Small clipboard icon that copies EXACTLY the provided raw string.
    Never pass components/dicts here — only the raw path string.
    """
    text = "" if text is None else str(text)
    icon = html.Span(
        "📋",
        title=f"Copy: {text}",
        style={
            "display": "inline-block",
            "fontSize": "12px",
            "opacity": 0.9,
            "cursor": "pointer",
            "verticalAlign": "middle",
        },
    )
    overlay = dcc.Clipboard(
        content=text,           # ← RAW PATH ONLY
        title="Copy",
        style={
            "position": "absolute",
            "left": 0,
            "top": 0,
            "width": "1.6em",
            "height": "1.4em",
            "opacity": 0.01,    # not 0 so it receives clicks
            "zIndex": 5,
            "cursor": "pointer",
            "border": 0,
            "background": "transparent",
        },
    )
    # spacing before next chunk
    return html.Span(
        [icon, overlay],
        style={"position": "relative", "display": "inline-block", "marginLeft": "4px", "marginRight": "10px"},
    )


def _chunk_badge_and_links(self, ch: dict, idx: int):
    """
    Render one chunk: [badge] [p] [l + clipboard].
    - Badge text: c{idx}
    - 'p' opens ch['proc'] if present
    - 'l' opens the viewer URL; tooltip shows FULL raw path
    - Clipboard copies the RAW path (not the viewer URL)
    """
    label   = f"c{idx}"
    st      = (ch.get("status") or "waiting").lower()
    proc    = ch.get("proc")
    raw     = ch.get("log")
    raw_str = str(raw) if raw is not None else None
    href    = self.linker.href_for(raw_str) if raw_str else None

    # badge
    badge = html.Span(
        label,
        title=str(ch.get("id") or label),
        style={
            "display": "inline-block",
            "padding": "2px 6px",
            "borderRadius": "8px",
            "fontSize": "12px",
            "marginRight": "6px",
            **self._shade(st, 0.35),
        },
    )
    bits = [badge]

    # proc link
    if proc:
        bits.append(
            html.A(
                "p",
                href=proc,
                target="_blank",
                title="proc",
                style={"marginRight": "6px", "textDecoration": "underline", "fontSize": "12px"},
            )
        )

    # log link + clipboard (RAW PATH for clipboard, 'l' label for link)
    if raw_str and href:
        bits.append(
            html.A(
                "l",
                href=href,
                target="_blank",
                title=raw_str,   # tooltip shows full path
                style={"textDecoration": "underline", "fontSize": "12px", "marginRight": "0"},
            )
        )
        bits.append(self._clipboard_button(raw_str))  # ← copy RAW path
    elif raw_str:
        # No viewer URL possible, still allow copying the RAW path
        bits.append(html.Span("l", title=raw_str, style={"fontSize": "12px"}))
        bits.append(self._clipboard_button(raw_str))

    return bits

def href_for(self, value: str | None) -> str | None:
    if not value:
        return None
    v = str(value).strip()
    if v.startswith("http://") or v.startswith("https://"):
        return v

    p = pathlib.Path(v)
    try:
        if p.is_absolute():
            abs_p = p.resolve()
            try:
                rel = abs_p.relative_to(self.root).as_posix()
                return f"/logview/root/{quote(rel)}"   # absolute URL
            except Exception:
                # outside LOG_ROOT → always create a mem key; cache text if readable now
                key = self._key_for_abs(abs_p)
                txt = self._read_text(abs_p)
                with self._lock:
                    # initialize index once
                    if not hasattr(self, "_mem_index"):
                        self._mem_index = {}
                    self._mem_index[key] = str(abs_p)      # track origin always
                    if txt is not None:
                        self._mem.setdefault(key, txt)
                return f"/logview/mem/{quote(key)}"       # absolute URL
        else:
            rel = p.as_posix().lstrip("./")
            if ".." in rel:
                return None
            return f"/logview/root/{quote(rel)}"          # absolute URL
    except Exception:
        return None
    
    def __init__(self, log_root: pathlib.Path | str):
        self.root = pathlib.Path(log_root).resolve()
        self._mem = {}
        self._mem_index = {}      # key -> original absolute path
        self._lock = threading.RLock()

@server.get("/logview/mem/<path:key>")
def logview_mem(key: str):
    clean = key.lstrip("/").replace("\\", "/")
    with linker._lock:
        txt = linker._mem.get(clean)
        origin = linker._mem_index.get(clean)

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

def _html_page(title: str, body_text: str, full_path: str | None = None) -> str:
    from html import escape
    meta_html = (
        f"<div class='meta'>Path: <code id='logpath'>{escape(full_path)}</code> "
        f"<button onclick=\"navigator.clipboard.writeText(document.getElementById('logpath').textContent)\">Copy</button></div>"
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