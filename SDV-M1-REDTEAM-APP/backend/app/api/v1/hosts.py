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


async def _build_host_read(host: dict) -> HostRead:
    """Construit un HostRead avec port_count et services résolus."""
    host_id_str = str(host["_id"])
    service_count = await count("services", {"host_id": host_id_str})
    services = await find_many("services", {"host_id": host_id_str})
    return HostRead(
        id=host_id_str,
        ip=host["ip"],
        hostname=host.get("hostname"),
        os=host.get("os"),
        mac=host.get("mac"),
        status=host.get("status", "unknown"),
        port_count=service_count,
        services=[
            {
                "id": str(s["_id"]),
                "port": s.get("port"),
                "protocol": s.get("protocol"),
                "service": s.get("service") or s.get("name"),
                "version": s.get("version"),
                "banner": s.get("banner"),
                "state": s.get("state", "open"),
            }
            for s in services
        ],
        discovered_at=host.get("discovered_at"),
        last_seen=host.get("last_seen"),
        campaign_id=host.get("campaign_id"),
    )


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
    return [await _build_host_read(h) for h in hosts]


@router.get("/{host_id}", response_model=HostRead)
async def get_host(host_id: str):
    """Retourne les détails d'un hôte."""
    host = await find_one("hosts", {"_id": host_id})
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hôte non trouvé",
        )
    return await _build_host_read(host)


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
    return await _build_host_read(created)


@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_host(host_id: str):
    """Supprime un hôte."""
    deleted = await delete_one("hosts", {"_id": host_id})
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hôte non trouvé",
        )
