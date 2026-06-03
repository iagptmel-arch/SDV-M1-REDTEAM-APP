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
from app.services.mitre import map_to_mitre

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("/", response_model=list[VulnerabilityRead])
async def list_vulnerabilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    severity: str | None = Query(None),
    service_id: str | None = Query(None),
    cve_id: str | None = Query(None),
):
    """Retourne la liste paginée des vulnérabilités."""
    query: dict = {}
    if severity:
        query["severity"] = severity
    if service_id:
        query["service_id"] = service_id
    if cve_id:
        query["cve_id"] = cve_id

    vulns = await find_many("vulnerabilities", query, skip=skip, limit=limit)
    return [
        VulnerabilityRead(
            id=str(v["_id"]),
            service_id=v["service_id"],
            cve_id=v.get("cve_id"),
            description=v.get("description"),
            severity=v.get("severity"),
            cvss_score=v.get("cvss_score"),
            mitre_techniques=v.get("mitre_techniques", []),
            discovered_at=v.get("discovered_at"),
            campaign_id=v.get("campaign_id"),
        )
        for v in vulns
    ]


@router.get("/{vuln_id}", response_model=VulnerabilityRead)
async def get_vulnerability(vuln_id: str):
    """Retourne les détails d'une vulnérabilité, incluant les techniques MITRE."""
    vuln = await find_one("vulnerabilities", {"_id": vuln_id})
    if not vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnérabilité non trouvée",
        )

    # Enrichir avec les techniques MITRE si le service est connu
    service_id = vuln.get("service_id", "")
    service = await find_one("services", {"_id": service_id})
    if service:
        service_name = service.get("name", "")
        mitre_techs = map_to_mitre(service_name, vuln.get("cve_id"))
        vuln["mitre_techniques"] = [
            t["technique_id"] for t in mitre_techs
        ]

    return VulnerabilityRead(
        id=str(vuln["_id"]),
        service_id=vuln["service_id"],
        cve_id=vuln.get("cve_id"),
        description=vuln.get("description"),
        severity=vuln.get("severity"),
        cvss_score=vuln.get("cvss_score"),
        mitre_techniques=vuln.get("mitre_techniques", []),
        discovered_at=vuln.get("discovered_at"),
        campaign_id=vuln.get("campaign_id"),
    )


@router.post("/", response_model=VulnerabilityRead, status_code=status.HTTP_201_CREATED)
async def create_vulnerability(data: VulnerabilityCreate):
    """Crée une nouvelle vulnérabilité."""
    # Vérifier que le service parent existe
    service = await find_one("services", {"_id": data.service_id})
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service parent non trouvé",
        )

    vuln_dict = data.model_dump()

    # Enrichir avec les techniques MITRE
    service_name = service.get("name", "")
    mitre_techs = map_to_mitre(service_name, data.cve_id)
    vuln_dict["mitre_techniques"] = [t["technique_id"] for t in mitre_techs]

    vuln_id = await insert_one("vulnerabilities", vuln_dict)
    created = await find_one("vulnerabilities", {"_id": vuln_id})
    return VulnerabilityRead(
        id=str(created["_id"]),
        service_id=created["service_id"],
        cve_id=created.get("cve_id"),
        description=created.get("description"),
        severity=created.get("severity"),
        cvss_score=created.get("cvss_score"),
        mitre_techniques=created.get("mitre_techniques", []),
        discovered_at=created.get("discovered_at"),
        campaign_id=created.get("campaign_id"),
    )
