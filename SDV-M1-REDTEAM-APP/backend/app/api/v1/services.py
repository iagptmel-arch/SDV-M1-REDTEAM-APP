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


async def _resolve_host_ip(host_id: str) -> str | None:
    """Résout l'IP d'un hôte à partir de son ID."""
    host = await find_one("hosts", {"_id": host_id})
    return host.get("ip") if host else None


async def _build_service_read(service: dict) -> ServiceRead:
    """Construit un ServiceRead avec host_ip résolu."""
    host_ip = await _resolve_host_ip(service["host_id"])
    return ServiceRead(
        id=str(service["_id"]),
        host_id=service["host_id"],
        host_ip=host_ip,
        port=service["port"],
        protocol=service.get("protocol", "tcp"),
        service=service.get("service") or service.get("name"),
        name=service.get("name"),
        version=service.get("version"),
        banner=service.get("banner"),
        state=service.get("state", "open"),
        discovered_at=service.get("discovered_at"),
        campaign_id=service.get("campaign_id"),
    )


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
    return [await _build_service_read(s) for s in services]


@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(service_id: str):
    """Retourne les détails d'un service."""
    service = await find_one("services", {"_id": service_id})
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé",
        )
    return await _build_service_read(service)


@router.post("/", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(data: ServiceCreate):
    """Crée un nouveau service."""
    host = await find_one("hosts", {"_id": data.host_id})
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hôte parent non trouvé",
        )

    service_dict = data.model_dump()
    service_id = await insert_one("services", service_dict)
    created = await find_one("services", {"_id": service_id})
    return await _build_service_read(created)
