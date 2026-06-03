"""
Service de récupération de bannières
Identification des versions logicielles des services exposés.
"""

import asyncio
from typing import Any


async def _grab_http_banner(host: str, port: int, timeout: int = 5) -> str | None:
    """Récupère la bannière HTTP/HTTPS."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        request = (
            f"GET / HTTP/1.1\r\nHost: {host}:{port}\r\n"
            f"User-Agent: SDV-RedTeam-Scanner/1.0\r\n"
            f"Connection: close\r\n\r\n"
        )
        writer.write(request.encode())
        await writer.drain()

        response = await asyncio.wait_for(reader.read(4096), timeout=timeout)
        writer.close()
        await writer.wait_closed()

        # Extraire le Serveur header
        for line in response.decode(errors="ignore").split("\r\n"):
            if line.lower().startswith("server:"):
                return line.strip()
        # Retourner la première ligne (status line) si pas de Server header
        first_line = response.decode(errors="ignore").split("\r\n")[0]
        return f"HTTP {first_line}" if first_line else None
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError, UnicodeDecodeError):
        return None


async def _grab_ssh_banner(host: str, port: int, timeout: int = 5) -> str | None:
    """Récupère la bannière SSH."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        banner = await asyncio.wait_for(reader.readline(), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        decoded = banner.decode(errors="ignore").strip()
        return decoded if decoded else None
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError):
        return None


async def _grab_ftp_banner(host: str, port: int, timeout: int = 5) -> str | None:
    """Récupère la bannière FTP."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        banner = await asyncio.wait_for(reader.readline(), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        decoded = banner.decode(errors="ignore").strip()
        return decoded if decoded else None
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError):
        return None


async def _grab_smtp_banner(host: str, port: int, timeout: int = 5) -> str | None:
    """Récupère la bannière SMTP."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        banner = await asyncio.wait_for(reader.readline(), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        decoded = banner.decode(errors="ignore").strip()
        return decoded if decoded else None
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError):
        return None


async def _grab_pop3_banner(host: str, port: int, timeout: int = 5) -> str | None:
    """Récupère la bannière POP3."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        banner = await asyncio.wait_for(reader.readline(), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        decoded = banner.decode(errors="ignore").strip()
        return decoded if decoded else None
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError):
        return None


async def _grab_imap_banner(host: str, port: int, timeout: int = 5) -> str | None:
    """Récupère la bannière IMAP."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        banner = await asyncio.wait_for(reader.readline(), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        decoded = banner.decode(errors="ignore").strip()
        return decoded if decoded else None
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError):
        return None


# Mapping port -> fonction de grab
BANNER_GRABBERS: dict[int, Any] = {
    80: _grab_http_banner,
    443: _grab_http_banner,
    8080: _grab_http_banner,
    8443: _grab_http_banner,
    22: _grab_ssh_banner,
    21: _grab_ftp_banner,
    25: _grab_smtp_banner,
    587: _grab_smtp_banner,
    110: _grab_pop3_banner,
    143: _grab_imap_banner,
    993: _grab_imap_banner,
    995: _grab_pop3_banner,
}


async def grab_banner(
    host: str, port: int, timeout: int = 5
) -> str | None:
    """
    Tente de récupérer la bannière d'un service.

    Supporte : HTTP/HTTPS, SSH, FTP, SMTP, POP3, IMAP.

    Args:
        host: Adresse IP ou hostname cible.
        port: Port du service.
        timeout: Timeout en secondes.

    Returns:
        La bannière brute ou None si indisponible.
    """
    grabber = BANNER_GRABBERS.get(port)
    if grabber:
        return await grabber(host, port, timeout)

    # Fallback : tentative générique (envoi d'une ligne vide)
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.write(b"\r\n")
        await writer.drain()
        banner = await asyncio.wait_for(reader.readline(), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        decoded = banner.decode(errors="ignore").strip()
        return decoded if decoded else None
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError):
        return None
