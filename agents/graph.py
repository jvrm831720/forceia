"""ForceIA LangGraph — carrega implementação completa (P0+P1)."""
from pathlib import Path

_p = Path(__file__).resolve().parent
_src = "".join((_p / f"_graph_part_{i}.txt").read_text(encoding="utf-8") for i in range(3))
exec(compile(_src, str(_p / "graph_impl.py"), "exec"), globals())
