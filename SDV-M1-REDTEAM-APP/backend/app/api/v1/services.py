"""
Endpoints pour la gestion des services
"""

from fastapi import APIRouter

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/")
async def list_services():
    """Retourne la liste des services détectés."""
    return []


@router.get("/{service_id}")
async def get_service(service_id: str):
    """Retourne les détails d'un service."""
    return {"service_id": service_id}
