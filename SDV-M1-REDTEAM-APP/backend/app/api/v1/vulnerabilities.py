"""
Endpoints pour la gestion des vulnérabilités
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import (
    insert_one,
    find_many,
    find_one,
    count,
)
from app.schemas.vulnerability import VulnerabilityCreate, VulnerabilityRead
from app.services.mitre import map_to_mitre, enrich_mitre_techniques

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


async def _resolve_host_info(host_id: str | None) -> tuple[str | None, str | None]:
    """Résout host_ip et hostname depuis un host_id."""
    if not host_id:
        return None, None
    host = await find_one("hosts", {"_id": host_id})
    if host:
        return host.get("ip"), host.get("hostname")
    return None, None


async def _resolve_service_name(service_id: str | None) -> str | None:
    """Résout le nom d'un service depuis son ID."""
    if not service_id:
        return None
    service = await find_one("services", {"_id": service_id})
    if service:
        return service.get("service") or service.get("name")
    return None


async def _build_vuln_read(vuln: dict) -> VulnerabilityRead:
    """Construit un VulnerabilityRead avec toutes les résolutions."""
    host_id = vuln.get("host_id")
    service_id = vuln.get("service_id")
    host_ip, _ = await _resolve_host_info(host_id)
    service_name = await _resolve_service_name(service_id)

    # Enrichir les techniques MITRE : IDs → objets
    raw_mitre = vuln.get("mitre_techniques", [])
    if raw_mitre and isinstance(raw_mitre[0], str):
        mitre_techniques = enrich_mitre_techniques(raw_mitre)
    else:
        mitre_techniques = raw_mitre

    return VulnerabilityRead(
        id=str(vuln["_id"]),
        host_id=host_id,
        host_ip=host_ip,
        service_id=service_id,
        service_name=service_name,
        cve_id=vuln.get("cve_id"),
        description=vuln.get("description"),
        severity=vuln.get("severity"),
        cvss_score=vuln.get("cvss_score"),
        vector=vuln.get("vector"),
        cvss_version=vuln.get("cvss_version"),
        published=vuln.get("published"),
        mitre_techniques=mitre_techniques,
        discovered_at=vuln.get("discovered_at"),
        campaign_id=vuln.get("campaign_id"),
    )


@router.get("", response_model=list[VulnerabilityRead])
async def list_vulnerabilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    severity: str | None = Query(None),
    host_id: str | None = Query(None),
    service_id: str | None = Query(None),
    cve_id: str | None = Query(None),
):
    """Retourne la liste paginée des vulnérabilités."""
    query: dict = {}
    if severity:
        query["severity"] = severity
    if host_id:
        query["host_id"] = host_id
    if service_id:
        query["service_id"] = service_id
    if cve_id:
        query["cve_id"] = cve_id

    vulns = await find_many("vulnerabilities", query, skip=skip, limit=limit)
    return [await _build_vuln_read(v) for v in vulns]


@router.get("/{vuln_id}", response_model=VulnerabilityRead)
async def get_vulnerability(vuln_id: str):
    """Retourne les détails d'une vulnérabilité, incluant les techniques MITRE."""
    vuln = await find_one("vulnerabilities", {"_id": vuln_id})
    if not vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnérabilité non trouvée",
        )
    return await _build_vuln_read(vuln)


@router.post("", response_model=VulnerabilityRead, status_code=status.HTTP_201_CREATED)
async def create_vulnerability(data: VulnerabilityCreate):
    """Crée une nouvelle vulnérabilité."""
    vuln_dict = data.model_dump()

    # Enrichir avec les techniques MITRE si service indiqué
    if data.service_id:
        service = await find_one("services", {"_id": data.service_id})
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service parent non trouvé",
            )
        service_name = service.get("service") or service.get("name", "")
        mitre_techs = map_to_mitre(service_name, data.cve_id)
        vuln_dict["mitre_techniques"] = [t["technique_id"] for t in mitre_techs]

    vuln_id = await insert_one("vulnerabilities", vuln_dict)
    created = await find_one("vulnerabilities", {"_id": vuln_id})
    return await _build_vuln_read(created)
