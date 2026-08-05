"""ForceIA Admin — payload comprimido (P2 mounts)."""
from __future__ import annotations
import base64, zlib
from pathlib import Path
_b64 = (Path(__file__).resolve().parent / "_admin_zlib.b64").read_text(encoding="ascii")
_src = zlib.decompress(base64.b64decode(_b64)).decode("utf-8")
exec(compile(_src, str(Path(__file__).resolve().parent / "admin_server_impl.py"), "exec"), globals())
