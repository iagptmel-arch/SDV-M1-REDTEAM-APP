"""
Endpoint de statistiques pour le tableau de bord
"""

from datetime import datetime

from fastapi import APIRouter

from app.core.database import count, find_many

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    """Retourne les statistiques globales pour le tableau de bord."""
    total_hosts = await count("hosts")
    total_services = await count("services")
    total_vulnerabilities = await count("vulnerabilities")
    total_campaigns = await count("campaigns")

    # Compter par sévérité
    by_severity = {}
    for level in ["critical", "high", "medium", "low", "info"]:
        by_severity[level] = await count(
            "vulnerabilities", {"severity": level}
        )

    # Récupérer les 5 dernières campagnes
    recent_campaigns = await find_many(
        "campaigns",
        {},
        skip=0,
        limit=5,
        sort=[("created_at", -1)],
    )

    return {
        "hosts": total_hosts,
        "services": total_services,
        "vulnerabilities": total_vulnerabilities,
        "campaigns": total_campaigns,
        "by_severity": by_severity,
        "recent_campaigns": [
            {
                "id": str(c["_id"]),
                "name": c["name"],
                "status": c.get("status", "draft"),
                "targets": c.get("targets", []),
                "created_at": c["created_at"].isoformat() if isinstance(c.get("created_at"), datetime) else str(c.get("created_at") or ""),
            }
            for c in recent_campaigns
        ],
    }
