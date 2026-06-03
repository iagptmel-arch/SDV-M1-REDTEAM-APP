"""
Endpoints pour la gestion des hôtes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get("/")
async def list_hosts():
    """Retourne la liste des hôtes découverts."""
    return []


@router.get("/{host_id}")
async def get_host(host_id: str):
    """Retourne les détails d'un hôte."""
    return {"host_id": host_id}
