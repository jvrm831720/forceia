"""Mount P2 + feature route packs on the FastAPI admin app."""
from __future__ import annotations


def mount_all_feature_routes(app, require_admin) -> None:
    import logging
    log = logging.getLogger("forceia.admin")
    packs = [
        ("elite_routes", "mount_elite_routes"),
        ("skills_routes", "mount_skills_routes"),
        ("product_routes", "mount_product_routes"),
        ("trust_routes", "mount_trust_routes"),
        ("p2_routes", "mount_p2_routes"),
    ]
    for mod_name, fn_name in packs:
        try:
            mod = __import__(mod_name)
            getattr(mod, fn_name)(app, require_admin)
        except Exception as e:
            log.warning("%s not mounted: %s", mod_name, e)

    try:
        from pathlib import Path
        static_dir = Path(__file__).resolve().parent / "static"
        register_admin_ui_hooks(app, static_dir)
    except Exception as e:
        log.warning("admin UI hooks not mounted: %s", e)


def enhance_admin_html(raw: str) -> str:
    css = """
.badge{display:inline-flex;align-items:center;gap:4px;padding:2px 7px;border-radius:999px;font-size:10.5px;font-weight:600;border:1px solid var(--line);background:rgba(255,255,255,.04);white-space:nowrap}
.badge.hot{color:#34d399;border-color:rgba(52,211,153,.35);background:rgba(52,211,153,.1)}
.badge.warm{color:#ffb020;border-color:rgba(255,176,32,.35);background:rgba(255,176,32,.1)}
.badge.cold{color:#8b96b0}.badge.risk{color:#fb7185}
.badge.intent{color:#a78bfa;border-color:rgba(167,139,250,.35)}
.intel-row{display:flex;gap:10px;flex-wrap:wrap;margin:8px 0 4px}
.intel-chip{font-family:var(--mono);font-size:11px;padding:6px 10px;border-radius:10px;background:rgba(255,255,255,.04);border:1px solid var(--line);color:var(--muted)}
.intel-chip strong{color:var(--ink)}
.bulk-box{margin-top:14px;padding:14px;border-radius:12px;border:1px dashed var(--line-strong);background:rgba(255,255,255,.02)}
.bulk-box textarea{width:100%;min-height:110px;background:rgba(0,0,0,.25);border:1px solid var(--line);border-radius:10px;color:var(--ink);padding:10px;font-family:var(--mono);font-size:12px}
.bulk-box .hint{font-size:12px;color:var(--muted);margin:6px 0 10px}
.bulk-actions{display:flex;gap:8px;align-items:center;margin-top:8px}
.bulk-result{font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:8px}
"""
    if ".badge.hot" not in raw:
        raw = raw.replace("</style>", css + "\n</style>")
    old = '<div id="view-leads" class="panel-view"><div class="card leads-card"><h2>Leads recentes</h2><div id="leads-wrap"><div class="empty">Sem leads</div></div></div></div>'
    new = (
        '<div id="view-leads" class="panel-view"><div class="card leads-card">'
        '<h2>Leads · inteligência</h2><div id="intel-chips" class="intel-row"></div>'
        '<div id="leads-wrap"><div class="empty">Sem leads</div></div>'
        '<div class="bulk-box"><div style="font-weight:600;margin-bottom:4px">Import em massa</div>'
        '<div class="hint">JSON array ou CSV (phone, name, company, email, stage). Máx. 500.</div>'
        '<textarea id="bulk-in" placeholder="[{&quot;phone&quot;:&quot;11999990000&quot;,&quot;name&quot;:&quot;Ana&quot;}]"></textarea>'
        '<div class="bulk-actions"><button class="btn btn-primary" id="btn-bulk">Importar</button>'
        '<label style="font-size:12px;color:var(--muted);display:flex;gap:6px;align-items:center">'
        '<input type="checkbox" id="bulk-twenty" /> sync Twenty</label></div>'
        '<div class="bulk-result" id="bulk-result"></div></div></div></div>'
    )
    if 'id="bulk-in"' not in raw:
        raw = raw.replace(old, new)
    if "admin_p2.js" not in raw:
        raw = raw.replace("</body>", '<script src="/static/admin_p2.js"></script>\n</body>')
    return raw


def register_admin_ui_hooks(app, static_dir) -> None:
    from pathlib import Path
    from fastapi.responses import HTMLResponse, Response

    @app.get("/static/admin_p2.js", include_in_schema=False)
    async def _p2_js():
        p = Path(static_dir) / "admin_p2.js"
        if p.exists():
            return Response(p.read_text(encoding="utf-8"), media_type="application/javascript")
        return Response("/* missing */", media_type="application/javascript")

    @app.get("/console", include_in_schema=False)
    async def _console():
        p = Path(static_dir) / "admin.html"
        if not p.exists():
            return HTMLResponse("<h1>admin missing</h1>", status_code=404)
        return HTMLResponse(enhance_admin_html(p.read_text(encoding="utf-8")))
