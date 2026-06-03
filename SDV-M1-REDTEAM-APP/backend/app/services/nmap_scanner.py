"""
Scanner réseau basé sur Nmap
Remplace les services discovery + scanner Python par des appels nmap réels.
"""

import asyncio
import ipaddress
import json
import logging
import xml.etree.ElementTree as ET
from typing import Any

logger = logging.getLogger("nmap_scanner")

# Chemin vers nmap
NMAP_BIN = "nmap"


async def _run_nmap(args: list[str], timeout: int = 300) -> str:
    """Exécute nmap et retourne la sortie brute."""
    cmd = [NMAP_BIN] + args
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        if proc.returncode != 0:
            logger.warning(f"nmap retour {proc.returncode}: {stderr.decode()[:200]}")
        return stdout.decode(errors="ignore")
    except asyncio.TimeoutError:
        proc.kill()
        logger.warning(f"nmap timeout après {timeout}s")
        return ""


def _parse_nmap_xml(xml_output: str) -> list[dict[str, Any]]:
    """Parse la sortie XML de nmap (-oX -) en liste de hosts."""
    hosts: list[dict[str, Any]] = []
    try:
        root = ET.fromstring(xml_output)
        for host_elem in root.findall("host"):
            host: dict[str, Any] = {
                "ip": "",
                "hostname": "",
                "mac": "",
                "os_guess": "",
                "status": "down",
                "services": [],
            }

            # Statut
            status = host_elem.find("status")
            if status is not None:
                host["status"] = status.get("state", "down")

            # Adresses (IPv4, IPv6, MAC)
            for addr in host_elem.findall("address"):
                addr_type = addr.get("addrtype", "")
                if addr_type in ("ipv4", "ipv6") and not host["ip"]:
                    host["ip"] = addr.get("addr", "")
                elif addr_type == "mac":
                    host["mac"] = addr.get("addr", "")

            # Hostname
            hostnames = host_elem.find("hostnames")
            if hostnames is not None:
                hn = hostnames.find("hostname")
                if hn is not None:
                    host["hostname"] = hn.get("name", "")

            # OS detection
            os_elem = host_elem.find("os")
            if os_elem is not None:
                osmatch = os_elem.find("osmatch")
                if osmatch is not None:
                    host["os_guess"] = osmatch.get("name", "")

            # Ports
            ports = host_elem.find("ports")
            if ports is not None:
                for port_elem in ports.findall("port"):
                    svc: dict[str, Any] = {
                        "port": 0,
                        "protocol": "tcp",
                        "state": "closed",
                        "name": "unknown",
                        "version": "",
                        "banner": "",
                    }
                    svc["port"] = int(port_elem.get("portid", 0))
                    svc["protocol"] = port_elem.get("protocol", "tcp")

                    state_elem = port_elem.find("state")
                    if state_elem is not None:
                        svc["state"] = state_elem.get("state", "closed")

                    svc_elem = port_elem.find("service")
                    if svc_elem is not None:
                        svc["name"] = svc_elem.get("name", "unknown")
                        # product (ex: "OpenSSH") est plus précis que le nom
                        product = svc_elem.get("product")
                        if product:
                            svc["name"] = product.lower().replace(" ", "_")
                        svc["version"] = svc_elem.get("version", "")

                    host["services"].append(svc)

            hosts.append(host)
    except ET.ParseError as e:
        logger.error(f"Erreur parse XML nmap: {e}")
    return hosts


async def discover_hosts_nmap(
    target: str, timeout: int = 120
) -> list[dict[str, Any]]:
    """
    Découvre les hôtes actifs via nmap ping sweep (-sn).

    Args:
        target: Cible (CIDR, IP, range).
        timeout: Timeout en secondes.

    Returns:
        Liste de dicts : {ip, hostname, mac, os_guess, status, services}
    """
    logger.info(f"nmap discovery: {target}")
    xml_out = await _run_nmap(
        ["-sn", "-oX", "-", "--host-timeout", "5s", target],
        timeout=timeout,
    )
    hosts = _parse_nmap_xml(xml_out)

    # Ne garder que les hôtes up
    hosts = [h for h in hosts if h["status"] == "up"]

    # Résoudre les hostnames via DNS si nmap ne les a pas trouvés
    for h in hosts:
        if not h["hostname"]:
            try:
                h["hostname"] = await asyncio.get_event_loop().run_in_executor(
                    None, __import__("socket").gethostbyaddr, h["ip"]
                )[0]
            except Exception:
                pass

    logger.info(f"  → {len(hosts)} hôte(s) up")
    return hosts


async def scan_ports_nmap(
    host: str,
    ports: str | None = None,
    timeout: int = 300,
    detect_os: bool = True,
) -> list[dict[str, Any]]:
    """
    Scanne les ports d'un hôte avec nmap -sS -sV -O (SYN stealth + version + OS).

    Args:
        host: Adresse IP.
        ports: Ports à scanner (ex: "22,80,443" ou "1-1000").
               None = les 1000 ports les plus communs.
        timeout: Timeout en secondes.
        detect_os: Activer la détection d'OS (nécessite root).

    Returns:
        Liste de services : {port, protocol, state, name, version, banner}
    """
    logger.info(f"nmap scan: {host} ports={ports or 'top1000'} OS={detect_os}")

    cmd = ["-sS", "-sV", "--version-intensity", "5", "-oX", "-", "--host-timeout", "120s"]
    if detect_os:
        cmd.extend(["-O", "--osscan-guess"])
    if ports:
        cmd.extend(["-p", ports])
    cmd.append(host)

    xml_out = await _run_nmap(cmd, timeout=timeout)
    hosts = _parse_nmap_xml(xml_out)

    services: list[dict[str, Any]] = []
    os_guess = ""
    for h in hosts:
        if h["ip"] == host:
            os_guess = h.get("os_guess", "")
            for svc in h["services"]:
                if svc["state"] == "open":
                    services.append(svc)

    logger.info(f"  → {len(services)} service(s) ouvert(s) OS={os_guess or '?'}")
    return services, os_guess


async def full_scan_nmap(
    target: str,
    ports: str | None = None,
    timeout: int = 600,
) -> list[dict[str, Any]]:
    """
    Scan complet d'une cible : découverte + scan ports + OS + versions.

    Args:
        target: Cible (CIDR, IP, range).
        ports: Ports à scanner (None = top 1000).
        timeout: Timeout global.

    Returns:
        Liste de hosts avec leurs services.
    """
    logger.info(f"nmap full scan: {target} ports={ports or 'top1000'}")

    cmd = ["-sV", "-O", "--osscan-guess", "-oX", "-"]
    if ports:
        cmd.extend(["-p", ports])
    cmd.append(target)

    xml_out = await _run_nmap(cmd, timeout=timeout)
    hosts = _parse_nmap_xml(xml_out)

    # Ne garder que les hôtes up
    hosts = [h for h in hosts if h["status"] == "up"]
    logger.info(f"  → {len(hosts)} hôte(s) avec services")
    return hosts
