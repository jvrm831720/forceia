"""
ForceIA Admin — loads base from main and applies P2 route mounts + version bump.
"""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

_BASE_URL = os.getenv(
    "FORCEIA_ADMIN_SOURCE_URL",
    "https://raw.githubusercontent.com/jvrm831720/forceia/main/agents/admin_server.py",
)

_src = urllib.request.urlopen(_BASE_URL, timeout=30).read().decode("utf-8")
_src = _src.replace('APP_VERSION = "1.9.1"', 'APP_VERSION = "2.6.0"', 1)
exec(compile(_src, "admin_server_base.py", "exec"), globals())

# P2 + feature packs
try:
    from p2_boot import enhance_admin_html, mount_all_feature_routes

    mount_all_feature_routes(app, require_token)  # type: ignore[name-defined]
except Exception as _e:
    try:
        log.warning("p2_boot not mounted: %s", _e)  # type: ignore[name-defined]
    except Exception:
        pass

# Serve enhanced admin UI at /
try:
    from fastapi.responses import FileResponse, HTMLResponse

    _static = Path(__file__).resolve().parent / "static"
    _web_dist = Path(__file__).resolve().parent.parent / "web" / "dist"

    @app.get("/", include_in_schema=False)  # type: ignore[name-defined]
    async def index_p2():
        spa = _web_dist / "index.html"
        if spa.exists():
            return FileResponse(spa)
        html = _static / "admin.html"
        if html.exists():
            from p2_boot import enhance_admin_html

            return HTMLResponse(enhance_admin_html(html.read_text(encoding="utf-8")))
        return HTMLResponse("UI nao encontrada", status_code=404)
except Exception:
    pass
