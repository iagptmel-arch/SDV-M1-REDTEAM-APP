"""
Endpoints pour la gestion des campagnes
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import (
    insert_one,
    find_many,
    find_one,
    update_one,
    count,
)
from app.schemas.campaign import CampaignCreate, CampaignRead, CampaignUpdate

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=list[CampaignRead])
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: str | None = Query(None, alias="status"),
):
    """Retourne la liste paginée des campagnes."""
    query: dict = {}
    if status_filter:
        query["status"] = status_filter
    campaigns = await find_many("campaigns", query, skip=skip, limit=limit)
    return [
        CampaignRead(
            id=str(c["_id"]),
            name=c["name"],
            description=c.get("description"),
            targets=c.get("targets", []),
            status=c.get("status", "draft"),
            created_at=c.get("created_at"),
            started_at=c.get("started_at"),
            completed_at=c.get("completed_at"),
            created_by=c.get("created_by"),
        )
        for c in campaigns
    ]


@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(campaign_id: str):
    """Retourne les détails d'une campagne."""
    campaign = await find_one("campaigns", {"_id": campaign_id})
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campagne non trouvée",
        )
    return CampaignRead(
        id=str(campaign["_id"]),
        name=campaign["name"],
        description=campaign.get("description"),
        targets=campaign.get("targets", []),
        status=campaign.get("status", "draft"),
        created_at=campaign.get("created_at"),
        started_at=campaign.get("started_at"),
        completed_at=campaign.get("completed_at"),
        created_by=campaign.get("created_by"),
    )


@router.post("/", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
async def create_campaign(data: CampaignCreate):
    """Crée une nouvelle campagne."""
    campaign_dict = data.model_dump()
    campaign_dict["status"] = "draft"
    campaign_id = await insert_one("campaigns", campaign_dict)
    created = await find_one("campaigns", {"_id": campaign_id})
    return CampaignRead(
        id=str(created["_id"]),
        name=created["name"],
        description=created.get("description"),
        targets=created.get("targets", []),
        status=created.get("status", "draft"),
        created_at=created.get("created_at"),
        started_at=created.get("started_at"),
        completed_at=created.get("completed_at"),
        created_by=created.get("created_by"),
    )


@router.patch("/{campaign_id}", response_model=CampaignRead)
async def update_campaign(campaign_id: str, data: CampaignUpdate):
    """Met à jour une campagne (statut, nom, etc.)."""
    existing = await find_one("campaigns", {"_id": campaign_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campagne non trouvée",
        )

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}

    # Gestion automatique des dates
    if "status" in update_data:
        if update_data["status"] == "running" and existing.get("status") != "running":
            update_data["started_at"] = datetime.utcnow()
        elif update_data["status"] == "completed":
            update_data["completed_at"] = datetime.utcnow()

    if update_data:
        await update_one("campaigns", {"_id": campaign_id}, update_data)

    updated = await find_one("campaigns", {"_id": campaign_id})
    return CampaignRead(
        id=str(updated["_id"]),
        name=updated["name"],
        description=updated.get("description"),
        targets=updated.get("targets", []),
        status=updated.get("status", "draft"),
        created_at=updated.get("created_at"),
        started_at=updated.get("started_at"),
        completed_at=updated.get("completed_at"),
        created_by=updated.get("created_by"),
    )
