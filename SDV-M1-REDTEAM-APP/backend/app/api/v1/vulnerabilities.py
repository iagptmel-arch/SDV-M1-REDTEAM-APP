"""
Endpoints pour la gestion des vulnérabilités
"""

from fastapi import APIRouter

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("/")
async def list_vulnerabilities():
    """Retourne la liste des vulnérabilités identifiées."""
    return []


@router.get("/{vuln_id}")
async def get_vulnerability(vuln_id: str):
    """Retourne les détails d'une vulnérabilité."""
    return {"vuln_id": vuln_id}
