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
    
# host setup
from dataset_dashboard.services.logs import LogLinker, register_log_routes
self.log_linker = LogLinker(cfg.log_root)
register_log_routes(app.server, self.log_linker)

# table component expects a linker with .href_for(...)
from dataset_dashboard.components.table import TableComponent
self.table = TableComponent(self.log_linker, clipboard_fallback_open=cfg.clipboard_fallback_open)

from dataset_dashboard.services.logs import LogLinker
from pathlib import Path
lnk = LogLinker(Path("/tmp/drm-logs"))
print(lnk.href_for("https://example.com/test.log"))                 # https URL unchanged
print(lnk.href_for("/tmp/drm-logs/dataset-000/stage-0.log"))        # -> /logview/root/dataset-000/stage-0.log
print(lnk.href_for("/opt/elsewhere/app.log"))                       # -> /logview/mem/abs/...
print(lnk.href_for("dataset-000/stage-0.log"))                      # -> /logview/root/dataset-000/stage-0.log