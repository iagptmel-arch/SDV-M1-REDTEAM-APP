"""
Endpoints pour la gestion des hôtes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.database import (
    insert_one,
    find_many,
    find_one,
    update_one,
    delete_one,
    count,
)
from app.schemas.host import HostCreate, HostRead, HostUpdate

router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get("/", response_model=list[HostRead])
async def list_hosts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
):
    """Retourne la liste paginée des hôtes."""
    query: dict = {}
    if status_filter:
        query["status"] = status_filter
    if search:
        query["$or"] = [
            {"ip": {"$regex": search, "$options": "i"}},
            {"hostname": {"$regex": search, "$options": "i"}},
        ]
    hosts = await find_many("hosts", query, skip=skip, limit=limit)
    total = await count("hosts", query)
    return [
        HostRead(
            id=str(h["_id"]),
            ip=h["ip"],
            hostname=h.get("hostname"),
            os=h.get("os"),
            status=h.get("status", "unknown"),
            discovered_at=h.get("discovered_at"),
            campaign_id=h.get("campaign_id"),
        )
        for h in hosts
    ]


@router.get("/{host_id}", response_model=HostRead)
async def get_host(host_id: str):
    """Retourne les détails d'un hôte."""
    host = await find_one("hosts", {"_id": host_id})
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hôte non trouvé",
        )
    return HostRead(
        id=str(host["_id"]),
        ip=host["ip"],
        hostname=host.get("hostname"),
        os=host.get("os"),
        status=host.get("status", "unknown"),
        discovered_at=host.get("discovered_at"),
        campaign_id=host.get("campaign_id"),
    )


@router.post("/", response_model=HostRead, status_code=status.HTTP_201_CREATED)
async def create_host(data: HostCreate):
    """Crée un nouvel hôte."""
    existing = await find_one("hosts", {"ip": data.ip})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un hôte avec cette IP existe déjà",
        )
    host_dict = data.model_dump()
    host_dict["status"] = "unknown"
    host_id = await insert_one("hosts", host_dict)
    created = await find_one("hosts", {"_id": host_id})
    return HostRead(
        id=str(created["_id"]),
        ip=created["ip"],
        hostname=created.get("hostname"),
        os=created.get("os"),
        status=created.get("status", "unknown"),
        discovered_at=created.get("discovered_at"),
        campaign_id=created.get("campaign_id"),
    )


@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_host(host_id: str):
    """Supprime un hôte."""
    deleted = await delete_one("hosts", {"_id": host_id})
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hôte non trouvé",
        )
