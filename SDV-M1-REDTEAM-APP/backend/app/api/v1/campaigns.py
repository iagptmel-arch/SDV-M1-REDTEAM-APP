"""
Endpoints pour la gestion des campagnes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/")
async def list_campaigns():
    """Retourne la liste des campagnes."""
    return []


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Retourne les détails d'une campagne."""
    return {"campaign_id": campaign_id}
