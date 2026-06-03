"""
Service de mapping MITRE ATT&CK
Correspondance entre services/vulnérabilités et techniques MITRE.
"""

from typing import Any

# Table de correspondance statique service → techniques MITRE ATT&CK
# Source : https://attack.mitre.org/
MITRE_MAPPING: dict[str, list[dict[str, str]]] = {
    "ssh": [
        {
            "technique_id": "T1021.004",
            "technique_name": "Remote Services: SSH",
            "tactic": "Lateral Movement",
            "description": "Adversaires peuvent utiliser SSH pour se déplacer latéralement.",
        },
        {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "tactic": "Credential Access",
            "description": "Adversaires peuvent tenter de forcer l'authentification SSH.",
        },
    ],
    "http": [
        {
            "technique_id": "T1190",
            "technique_name": "Exploit Public-Facing Application",
            "tactic": "Initial Access",
            "description": "Adversaires peuvent exploiter une vulnérabilité dans une application exposée.",
        },
        {
            "technique_id": "T1071.001",
            "technique_name": "Web Protocols",
            "tactic": "Command and Control",
            "description": "Adversaires peuvent utiliser HTTP/HTTPS pour le C2.",
        },
    ],
    "https": [
        {
            "technique_id": "T1190",
            "technique_name": "Exploit Public-Facing Application",
            "tactic": "Initial Access",
            "description": "Adversaires peuvent exploiter une vulnérabilité dans une application exposée.",
        },
        {
            "technique_id": "T1071.001",
            "technique_name": "Web Protocols",
            "tactic": "Command and Control",
            "description": "Adversaires peuvent utiliser HTTP/HTTPS pour le C2.",
        },
    ],
    "ftp": [
        {
            "technique_id": "T1048",
            "technique_name": "Exfiltration Over Alternative Protocol",
            "tactic": "Exfiltration",
            "description": "Adversaires peuvent exfiltrer des données via FTP.",
        },
        {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "tactic": "Credential Access",
            "description": "Adversaires peuvent tenter de forcer l'authentification FTP.",
        },
    ],
    "smb": [
        {
            "technique_id": "T1021.002",
            "technique_name": "Remote Services: SMB/Windows Admin Shares",
            "tactic": "Lateral Movement",
            "description": "Adversaires peuvent utiliser SMB pour se déplacer latéralement.",
        },
        {
            "technique_id": "T1550.002",
            "technique_name": "Use Alternate Authentication Material: Pass the Hash",
            "tactic": "Defense Evasion",
            "description": "Adversaires peuvent utiliser Pass the Hash via SMB.",
        },
    ],
    "mysql": [
        {
            "technique_id": "T1213",
            "technique_name": "Data from Information Repositories",
            "tactic": "Collection",
            "description": "Adversaires peuvent extraire des données depuis des bases de données.",
        },
    ],
    "postgresql": [
        {
            "technique_id": "T1213",
            "technique_name": "Data from Information Repositories",
            "tactic": "Collection",
            "description": "Adversaires peuvent extraire des données depuis des bases de données.",
        },
    ],
    "rdp": [
        {
            "technique_id": "T1021.001",
            "technique_name": "Remote Services: Remote Desktop Protocol",
            "tactic": "Lateral Movement",
            "description": "Adversaires peuvent utiliser RDP pour se déplacer latéralement.",
        },
        {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "tactic": "Credential Access",
            "description": "Adversaires peuvent tenter de forcer l'authentification RDP.",
        },
    ],
    "telnet": [
        {
            "technique_id": "T1021",
            "technique_name": "Remote Services",
            "tactic": "Lateral Movement",
            "description": "Adversaires peuvent utiliser Telnet pour se déplacer latéralement.",
        },
    ],
    "dns": [
        {
            "technique_id": "T1071.004",
            "technique_name": "DNS",
            "tactic": "Command and Control",
            "description": "Adversaires peuvent utiliser le protocole DNS pour le C2.",
        },
    ],
    "smtp": [
        {
            "technique_id": "T1071.003",
            "technique_name": "Mail Protocols",
            "tactic": "Command and Control",
            "description": "Adversaires peuvent utiliser SMTP pour le C2.",
        },
    ],
}

# Mapping CVE-ID spécifique vers techniques MITRE (extensions futures)
CVE_MITRE_MAPPING: dict[str, list[dict[str, str]]] = {
    # Exemples de CVE notables
    "CVE-2021-41773": [
        {
            "technique_id": "T1190",
            "technique_name": "Exploit Public-Facing Application",
            "tactic": "Initial Access",
            "description": "CVE-2021-41773 : Path traversal dans Apache HTTP Server 2.4.49.",
        },
    ],
    "CVE-2021-44228": [
        {
            "technique_id": "T1190",
            "technique_name": "Exploit Public-Facing Application",
            "tactic": "Initial Access",
            "description": "CVE-2021-44228 (Log4Shell) : RCE dans Apache Log4j 2.",
        },
        {
            "technique_id": "T1059",
            "technique_name": "Command and Scripting Interpreter",
            "tactic": "Execution",
            "description": "Log4Shell permet l'exécution de code à distance.",
        },
    ],
    "CVE-2023-44487": [
        {
            "technique_id": "T1499",
            "technique_name": "Endpoint Denial of Service",
            "tactic": "Impact",
            "description": "CVE-2023-44487 : HTTP/2 Rapid Reset Attack.",
        },
    ],
}


def _normalize_service_name(service_name: str) -> str:
    """Normalise le nom du service pour la recherche dans le mapping."""
    name = service_name.lower().strip()
    # Mapping des alias courants
    alias_map = {
        "apache": "http",
        "apache httpd": "http",
        "apache http server": "http",
        "nginx": "http",
        "iis": "http",
        "httpd": "http",
        "http": "http",
        "https": "https",
        "openssh": "ssh",
        "ssh": "ssh",
        "ftpd": "ftp",
        "ftp": "ftp",
        "samb": "smb",
        "samba": "smb",
        "smb": "smb",
        "microsoft-ds": "smb",
        "mysql": "mysql",
        "mariadb": "mysql",
        "postgresql": "postgresql",
        "postgres": "postgresql",
        "rdp": "rdp",
        "ms-wbt-server": "rdp",
        "telnet": "telnet",
        "dns": "dns",
        "domain": "dns",
        "smtp": "smtp",
        "submission": "smtp",
    }
    return alias_map.get(name, name)


def map_to_mitre(
    service_name: str, cve_id: str | None = None
) -> list[dict[str, str]]:
    """
    Associe un service ou une CVE aux techniques MITRE ATT&CK.

    Args:
        service_name: Nom du service (ex: "ssh", "http", "ftp").
        cve_id: Identifiant CVE optionnel pour un mapping plus précis.

    Returns:
        Liste de dictionnaires : {technique_id, technique_name, tactic, description}
    """
    results: list[dict[str, str]] = []
    seen: set[str] = set()

    # 1. Mapping par CVE (le plus précis)
    if cve_id and cve_id.upper() in CVE_MITRE_MAPPING:
        for tech in CVE_MITRE_MAPPING[cve_id.upper()]:
            if tech["technique_id"] not in seen:
                results.append(tech)
                seen.add(tech["technique_id"])

    # 2. Mapping par service
    normalized = _normalize_service_name(service_name)
    if normalized in MITRE_MAPPING:
        for tech in MITRE_MAPPING[normalized]:
            if tech["technique_id"] not in seen:
                results.append(tech)
                seen.add(tech["technique_id"])

    return results


# Index global de toutes les techniques MITRE (ID → objet)
_ALL_TECHNIQUES: dict[str, dict[str, str]] = {}

for _techs in list(MITRE_MAPPING.values()) + list(CVE_MITRE_MAPPING.values()):
    for _t in _techs:
        _ALL_TECHNIQUES[_t["technique_id"]] = {
            "id": _t["technique_id"],
            "name": _t["technique_name"],
            "tactic": _t["tactic"],
            "description": _t["description"],
        }


def enrich_mitre_techniques(technique_ids: list[str]) -> list[dict[str, str]]:
    """
    Convertit une liste d'IDs de techniques MITRE en objets enrichis.

    Args:
        technique_ids: Liste d'IDs (ex: ["T1190", "T1499"])

    Returns:
        Liste d'objets {id, name, tactic, description}
    """
    results = []
    seen = set()
    for tid in technique_ids:
        if tid in _ALL_TECHNIQUES and tid not in seen:
            results.append(_ALL_TECHNIQUES[tid])
            seen.add(tid)
        elif tid not in seen:
            results.append({
                "id": tid,
                "name": tid,
                "tactic": "Unknown",
                "description": "Technique non référencée dans la base.",
            })
            seen.add(tid)
    return results
