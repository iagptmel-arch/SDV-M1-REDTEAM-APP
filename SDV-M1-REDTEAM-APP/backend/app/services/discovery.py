"""
Service de découverte réseau
Détection des hôtes actifs sur le réseau cible via ICMP, ARP, et TCP SYN.
"""

import asyncio
import ipaddress
import platform
import subprocess
import socket
from typing import Any

COMMON_PORTS = [22, 80, 443, 445, 3389, 8080, 8443]


async def _ping_host(ip: str, timeout: int = 2) -> bool:
    """Ping une adresse IP (ICMP Echo Request)."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping", param, "1", "-W", str(timeout), ip,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        return await proc.wait() == 0
    except (FileNotFoundError, asyncio.TimeoutError):
        return False


async def _tcp_syn_check(ip: str, port: int, timeout: int = 1) -> bool:
    """Vérifie si un port TCP est ouvert (connexion rapide)."""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError):
        return False


async def _arp_scan(target: str) -> list[dict[str, Any]]:
    """Tente un scan ARP via la commande arp-scan ou arp."""
    hosts: list[dict[str, Any]] = []
    try:
        proc = await asyncio.create_subprocess_exec(
            "arp-scan", "--retry=1", "--timeout=500", target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
        for line in stdout.decode(errors="ignore").splitlines():
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[0]
                mac = parts[1] if len(parts) >= 2 else None
                hosts.append({"ip": ip, "status": "up", "mac": mac, "method": "arp"})
    except (FileNotFoundError, asyncio.TimeoutError):
        pass
    return hosts


async def _resolve_hostname(ip: str) -> str | None:
    """Résout le nom d'hôte à partir d'une IP."""
    try:
        hostname, _, _ = await asyncio.get_event_loop().run_in_executor(
            None, socket.gethostbyaddr, ip
        )
        return hostname
    except (socket.herror, socket.gaierror):
        return None


async def discover_hosts(target: str, timeout: int = 30) -> list[dict[str, Any]]:
    """
    Découvre les hôtes actifs sur le réseau cible.

    Utilise une combinaison de :
    - ICMP ping sweep
    - ARP scan (si arp-scan disponible)
    - TCP SYN sur quelques ports communs

    Args:
        target: Cible (CIDR, intervalle IP, ou IP unique).
        timeout: Timeout global en secondes.

    Returns:
        Liste de dictionnaires : {ip, hostname, status, mac, os_guess, method}
    """
    discovered: list[dict[str, Any]] = []
    seen_ips: set[str] = set()

    # Résoudre la plage d'adresses
    try:
        network = ipaddress.ip_network(target, strict=False)
        ips = [str(ip) for ip in network.hosts()]
    except ValueError:
        # Peut-être un hostname ou IP unique
        try:
            ips = [str(ipaddress.ip_address(target))]
        except ValueError:
            return []

    if not ips:
        return []

    # Limiter le nombre d'IP à scanner pour éviter les timeouts
    if len(ips) > 256:
        ips = ips[:256]

    # 1. ICMP ping sweep
    ping_tasks = {ip: _ping_host(ip) for ip in ips}
    ping_results = await asyncio.gather(*ping_tasks.values())

    for ip, alive in zip(ips, ping_results):
        if alive:
            discovered.append({"ip": ip, "status": "up", "method": "icmp"})
            seen_ips.add(ip)

    # 2. ARP scan (complémentaire)
    if len(ips) <= 256:
        arp_hosts = await _arp_scan(target)
        for h in arp_hosts:
            if h["ip"] not in seen_ips:
                discovered.append(h)
                seen_ips.add(h["ip"])

    # 3. TCP SYN sur ports communs pour les IP non détectées
    tcp_check_ips = [ip for ip in ips if ip not in seen_ips]
    for ip in tcp_check_ips:
        for port in COMMON_PORTS[:3]:  # Seulement 3 ports pour rester rapide
            if await _tcp_syn_check(ip, port):
                discovered.append({"ip": ip, "status": "up", "method": f"tcp_syn_{port}"})
                seen_ips.add(ip)
                break

    # 4. Résolution des hostnames
    hostname_tasks = {h["ip"]: _resolve_hostname(h["ip"]) for h in discovered}
    hostname_results = await asyncio.gather(*hostname_tasks.values())

    for host, hostname in zip(discovered, hostname_results):
        host["hostname"] = hostname
        host.setdefault("mac", None)
        host.setdefault("os_guess", None)

    return discovered
