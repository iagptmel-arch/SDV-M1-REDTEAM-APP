"""
Pipeline d'exécution d'une campagne
Orchestre : découverte → scan ports → bannières → CVE → MITRE
Utilise nmap pour les scans réseau (parallélisé par hôte).
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from app.core.database import (
    insert_one,
    find_one,
    update_one,
    find_many,
)
from app.services.nmap_scanner import discover_hosts_nmap, scan_ports_nmap
from app.services.vulnerability import search_cves
from app.services.mitre import map_to_mitre, enrich_mitre_techniques
from app.services.banner import grab_banner

logger = logging.getLogger("pipeline")

# Cache des services pour éviter les appels NVD redondants
_cve_cache: dict[str, list[dict]] = {}
# Verrou pour les mises à jour de campagne (éviter les race conditions)
_campaign_lock = asyncio.Lock()


async def _run_with_timeout(coro, timeout_sec: float, default=None):
    """Exécute une coroutine avec timeout, retourne `default` si timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_sec)
    except asyncio.TimeoutError:
        return default
    except Exception:
        return default


async def _update_summary(
    campaign_id: str, hosts: int, services: int, vulns: int
) -> None:
    """Met à jour le résumé de campagne de manière atomique."""
    async with _campaign_lock:
        await update_one("campaigns", {"_id": campaign_id}, {
            "summary": {
                "hosts": hosts,
                "services": services,
                "vulnerabilities": vulns,
            },
        })


async def _process_host(
    host_info: dict, campaign_id: str
) -> tuple[int, int, int]:
    """
    Traite un hôte complet : insertion DB → scan ports → services → CVE → MITRE.

    Returns:
        (nb_services, nb_vulns) pour cet hôte.
    """
    ip = host_info.get("ip", "")
    if not ip or host_info.get("status") != "up":
        return 0, 0

    logger.info(f"  📍 Hôte: {ip}")

    # Insérer/mettre à jour l'hôte
    host_doc = {
        "ip": ip,
        "hostname": host_info.get("hostname"),
        "mac": host_info.get("mac"),
        "os": host_info.get("os_guess"),
        "status": "up",
        "discovered_at": datetime.utcnow().isoformat(),
        "campaign_id": campaign_id,
    }
    existing_host = await find_one("hosts", {"ip": ip})
    if existing_host:
        host_id = str(existing_host["_id"])
        await update_one("hosts", {"_id": host_id}, host_doc)
    else:
        host_id = await insert_one("hosts", host_doc)

    # Scan ports via nmap -sS -sV -O (timeout 300s)
    scan_result = await _run_with_timeout(
        scan_ports_nmap(ip, timeout=300), timeout_sec=330, default=([], "")
    )
    if isinstance(scan_result, tuple):
        services, os_guess = scan_result
    else:
        services, os_guess = scan_result or [], ""

    # Si l'OS a été détecté par nmap, mettre à jour l'hôte
    if os_guess and not host_doc.get("os"):
        host_doc["os"] = os_guess
        await update_one("hosts", {"_id": host_id}, {"os": os_guess})

    logger.info(f"      → {len(services)} service(s) ouvert(s)")

    host_svc_count = 0
    host_vuln_count = 0

    for svc in services:
        port = svc.get("port", 0)
        if not port:
            continue
        protocol = svc.get("protocol", "tcp")
        svc_name = svc.get("name") or "unknown"
        svc_version = svc.get("version") or ""
        banner = svc.get("banner") or ""

        # Si nmap n'a pas récupéré de bannière, essayer grab_banner
        if not banner:
            banner = await _run_with_timeout(
                grab_banner(ip, port), timeout_sec=8, default=None
            )

        # Service enrichi
        service_doc = {
            "host_id": host_id,
            "ip": ip,
            "port": port,
            "protocol": protocol,
            "name": svc_name,
            "service": svc_name,
            "version": svc_version,
            "banner": banner,
            "state": "open",
            "discovered_at": datetime.utcnow().isoformat(),
            "campaign_id": campaign_id,
        }

        existing_svc = await find_one("services", {
            "host_id": host_id, "port": port, "protocol": protocol
        })
        if existing_svc:
            svc_id = str(existing_svc["_id"])
            await update_one("services", {"_id": svc_id}, service_doc)
        else:
            svc_id = await insert_one("services", service_doc)

        # Recherche CVE (timeout 20s)
        cves = []
        if svc_name not in ("unknown", "") and svc_version:
            cache_key = f"{svc_name}:{svc_version}"
            if cache_key in _cve_cache:
                cves = _cve_cache[cache_key]
            else:
                cves = await _run_with_timeout(
                    search_cves(svc_name, svc_version), timeout_sec=20, default=[]
                ) or []
                _cve_cache[cache_key] = cves

        # Mapping MITRE (synchrone, rapide)
        mitre_dicts = map_to_mitre(svc_name)
        mitre_ids_list = [m["technique_id"] for m in mitre_dicts if "technique_id" in m]
        mitre_techniques = enrich_mitre_techniques(mitre_ids_list)

        for cve in cves:
            vuln_doc = {
                "host_id": host_id,
                "service_id": svc_id,
                "cve_id": cve.get("cve_id", ""),
                "name": cve.get("name", ""),
                "description": cve.get("description", ""),
                "severity": cve.get("severity", "info"),
                "cvss_score": cve.get("cvss_score", 0.0),
                "service_name": svc_name,
                "mitre_techniques": mitre_techniques,
                "discovered_at": datetime.utcnow().isoformat(),
                "campaign_id": campaign_id,
            }
            existing_vuln = await find_one("vulnerabilities", {
                "host_id": host_id, "cve_id": vuln_doc["cve_id"]
            })
            if not existing_vuln:
                await insert_one("vulnerabilities", vuln_doc)
                host_vuln_count += 1

        host_svc_count += 1

    return host_svc_count, host_vuln_count


async def run_campaign_pipeline(campaign_id: str) -> None:
    """
    Lance le pipeline complet pour une campagne.
    Les hôtes sont scannés en parallèle pour accélérer le traitement.
    """
    logger.info(f"🚀 Démarrage pipeline campagne {campaign_id}")

    # 1. Charger la campagne
    campaign = await find_one("campaigns", {"_id": campaign_id})
    if not campaign:
        logger.error(f"Campagne {campaign_id} introuvable")
        return

    targets = campaign.get("targets", [])
    if not targets:
        logger.warning(f"Aucune cible pour la campagne {campaign_id}")
        await update_one("campaigns", {"_id": campaign_id}, {
            "status": "failed",
            "error": "Aucune cible spécifiée",
            "completed_at": datetime.utcnow(),
        })
        return

    # 2. Marquer comme en cours
    await update_one("campaigns", {"_id": campaign_id}, {
        "status": "running",
        "started_at": datetime.utcnow(),
    })

    total_hosts = 0
    total_services = 0
    total_vulns = 0

    try:
        for target in targets:
            logger.info(f"  🎯 Cible: {target}")

            # --- Étape 1 : Découverte via nmap -sn (timeout 120s) ---
            hosts = await _run_with_timeout(
                discover_hosts_nmap(target, timeout=120), timeout_sec=150, default=[]
            ) or []
            logger.info(f"    → {len(hosts)} hôte(s) actif(s)")

            if not hosts:
                continue

            # --- Étape 2 : Scan de tous les hôtes en parallèle ---
            # Limiter à 5 hôtes simultanés pour ne pas saturer le réseau
            semaphore = asyncio.Semaphore(5)

            async def _process_one(h: dict) -> tuple[int, int]:
                async with semaphore:
                    return await _process_host(h, campaign_id)

            tasks = [_process_one(h) for h in hosts]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, Exception):
                    logger.warning(f"Erreur sur un hôte: {r}")
                    continue
                svc, vuln = r
                total_services += svc
                total_vulns += vuln
                total_hosts += 1

            # Mise à jour progressive du résumé
            await _update_summary(
                campaign_id, total_hosts, total_services, total_vulns
            )

        # Succès
        await update_one("campaigns", {"_id": campaign_id}, {
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "summary": {
                "hosts": total_hosts,
                "services": total_services,
                "vulnerabilities": total_vulns,
            },
        })
        logger.info(f"✅ Pipeline terminé : {total_hosts}h / {total_services}s / {total_vulns}v")

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"❌ Pipeline échoué: {error_detail}")
        await update_one("campaigns", {"_id": campaign_id}, {
            "status": "failed",
            "error": str(e)[:500],
            "completed_at": datetime.utcnow(),
        })
