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
