"""
Endpoints pour la gestion des services
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import (
    insert_one,
    find_many,
    find_one,
    count,
)
from app.schemas.service import ServiceCreate, ServiceRead

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=list[ServiceRead])
async def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    protocol: str | None = Query(None),
    port_min: int | None = Query(None, ge=1, le=65535),
    port_max: int | None = Query(None, ge=1, le=65535),
    host_id: str | None = Query(None),
):
    """Retourne la liste paginée des services."""
    query: dict = {}
    if protocol:
        query["protocol"] = protocol
    if port_min is not None or port_max is not None:
        port_query: dict = {}
        if port_min is not None:
            port_query["$gte"] = port_min
        if port_max is not None:
            port_query["$lte"] = port_max
        query["port"] = port_query
    if host_id:
        query["host_id"] = host_id

    services = await find_many("services", query, skip=skip, limit=limit)
    return [
        ServiceRead(
            id=str(s["_id"]),
            host_id=s["host_id"],
            port=s["port"],
            protocol=s.get("protocol", "tcp"),
            name=s.get("name"),
            version=s.get("version"),
            banner=s.get("banner"),
            discovered_at=s.get("discovered_at"),
            campaign_id=s.get("campaign_id"),
        )
        for s in services
    ]


@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(service_id: str):
    """Retourne les détails d'un service."""
    service = await find_one("services", {"_id": service_id})
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé",
        )
    return ServiceRead(
        id=str(service["_id"]),
        host_id=service["host_id"],
        port=service["port"],
        protocol=service.get("protocol", "tcp"),
        name=service.get("name"),
        version=service.get("version"),
        banner=service.get("banner"),
        discovered_at=service.get("discovered_at"),
        campaign_id=service.get("campaign_id"),
    )


@router.post("/", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(data: ServiceCreate):
    """Crée un nouveau service."""
    # Vérifier que l'hôte parent existe
    host = await find_one("hosts", {"_id": data.host_id})
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hôte parent non trouvé",
        )

    service_dict = data.model_dump()
    service_id = await insert_one("services", service_dict)
    created = await find_one("services", {"_id": service_id})
    return ServiceRead(
        id=str(created["_id"]),
        host_id=created["host_id"],
        port=created["port"],
        protocol=created.get("protocol", "tcp"),
        name=created.get("name"),
        version=created.get("version"),
        banner=created.get("banner"),
        discovered_at=created.get("discovered_at"),
        campaign_id=created.get("campaign_id"),
    )
