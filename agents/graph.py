"""ForceIA LangGraph P0+P1 (payload comprimido)."""
from __future__ import annotations
import base64, zlib
from pathlib import Path
_dir = Path(__file__).resolve().parent
_b64 = (_dir / "_graph_zlib_a.b64").read_text(encoding="ascii") + (_dir / "_graph_zlib_b.b64").read_text(encoding="ascii")
_src = zlib.decompress(base64.b64decode(_b64)).decode("utf-8")
exec(compile(_src, str(_dir / "graph_impl.py"), "exec"), globals())
