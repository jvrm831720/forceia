"""ForceIA LangGraph P0+P1 (payload comprimido)."""
from __future__ import annotations
import base64, zlib
from pathlib import Path
_b64 = (Path(__file__).resolve().parent / "_graph_zlib.b64").read_text(encoding="ascii")
_src = zlib.decompress(base64.b64decode(_b64)).decode("utf-8")
exec(compile(_src, str(Path(__file__).resolve().parent / "graph_impl.py"), "exec"), globals())
