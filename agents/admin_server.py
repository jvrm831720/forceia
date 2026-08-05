"""ForceIA Admin — assembled from source chunks."""
from pathlib import Path
_dir = Path(__file__).resolve().parent
_src = ''.join((_dir / f'_admin_src_{i}.txt').read_text(encoding='utf-8') for i in range(3))
exec(compile(_src, str(_dir / 'admin_server_impl.py'), 'exec'), globals())
