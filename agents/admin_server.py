"""
ForceIA Admin — loads base from main and applies P2 route mounts + version bump.
"""
from __future__ import annotations

import os
import urllib.request

_BASE_URL = os.getenv(
    "FORCEIA_ADMIN_SOURCE_URL",
    "https://raw.githubusercontent.com/jvrm831720/forceia/main/agents/admin_server.py",
)

_src = urllib.request.urlopen(_BASE_URL, timeout=30).read().decode("utf-8")
_src = _src.replace('APP_VERSION = "1.9.1"', 'APP_VERSION = "2.6.0"', 1)
exec(compile(_src, "admin_server_base.py", "exec"), globals())

# P2 + feature packs
try:
    from p2_boot import mount_all_feature_routes

    mount_all_feature_routes(app, require_token)  # type: ignore[name-defined]
except Exception as _e:
    try:
        log.warning("p2_boot not mounted: %s", _e)  # type: ignore[name-defined]
    except Exception:
        pass
