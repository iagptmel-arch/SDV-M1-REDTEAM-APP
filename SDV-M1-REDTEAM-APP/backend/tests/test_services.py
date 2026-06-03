"""
Tests unitaires des services métier
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestSeverity:
    """Tests du calcul de sévérité."""

    def test_calculate_severity(self):
        from app.services.vulnerability import calculate_severity

        assert calculate_severity(9.5) == "critical"
        assert calculate_severity(9.0) == "critical"
        assert calculate_severity(7.5) == "high"
        assert calculate_severity(7.0) == "high"
        assert calculate_severity(5.0) == "medium"
        assert calculate_severity(4.0) == "medium"
        assert calculate_severity(2.0) == "low"
        assert calculate_severity(0.1) == "low"
        assert calculate_severity(0.0) == "info"


class TestDiscoverHosts:
    """Tests de la découverte réseau."""

    @pytest.mark.asyncio
    async def test_discover_hosts_empty_target(self):
        from app.services.discovery import discover_hosts

        result = await discover_hosts("invalid_target")
        assert result == []

    @pytest.mark.asyncio
    async def test_discover_hosts_single_ip(self):
        from app.services.discovery import discover_hosts

        with patch("app.services.discovery._ping_host", new_callable=AsyncMock) as mock_ping, \
             patch("app.services.discovery._arp_scan", new_callable=AsyncMock) as mock_arp:
            mock_ping.return_value = True
            mock_arp.return_value = []
            result = await discover_hosts("192.168.1.1")
            assert len(result) == 1
            assert result[0]["ip"] == "192.168.1.1"
            assert result[0]["status"] == "up"

    @pytest.mark.asyncio
    async def test_discover_hosts_no_response(self):
        from app.services.discovery import discover_hosts

        with patch("app.services.discovery._ping_host", new_callable=AsyncMock) as mock_ping, \
             patch("app.services.discovery._arp_scan", new_callable=AsyncMock) as mock_arp, \
             patch("app.services.discovery._tcp_syn_check", new_callable=AsyncMock) as mock_tcp:

            mock_ping.return_value = False
            mock_arp.return_value = []
            mock_tcp.return_value = False

            result = await discover_hosts("192.168.1.1")
            assert len(result) == 0


class TestScanPorts:
    """Tests du scan de ports."""

    @pytest.mark.asyncio
    async def test_scan_ports_tcp(self):
        from app.services.scanner import scan_ports

        with patch("app.services.scanner._tcp_scan_port", new_callable=AsyncMock) as mock_tcp:
            mock_tcp.return_value = {
                "port": 80,
                "protocol": "tcp",
                "state": "open",
                "name": "http",
                "version": None,
            }
            result = await scan_ports("192.168.1.1", ports=[80])
            assert len(result) == 1
            assert result[0]["port"] == 80
            assert result[0]["state"] == "open"

    @pytest.mark.asyncio
    async def test_scan_ports_all_closed(self):
        from app.services.scanner import scan_ports

        with patch("app.services.scanner._tcp_scan_port", new_callable=AsyncMock) as mock_tcp:
            mock_tcp.return_value = {
                "port": 80,
                "protocol": "tcp",
                "state": "closed",
                "name": None,
                "version": None,
            }
            result = await scan_ports("192.168.1.1", ports=[80, 443])
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_scan_ports_default_ports(self):
        from app.services.scanner import scan_ports, COMMON_TCP_PORTS

        with patch("app.services.scanner._tcp_scan_port", new_callable=AsyncMock) as mock_tcp:
            mock_tcp.return_value = {
                "port": 22,
                "protocol": "tcp",
                "state": "open",
                "name": "ssh",
                "version": None,
            }
            result = await scan_ports("192.168.1.1")
            # Doit scanner les ports communs par défaut
            assert mock_tcp.called


class TestGrabBanner:
    """Tests du banner grabbing."""

    @pytest.mark.asyncio
    async def test_grab_banner_ssh(self):
        from app.services.banner import grab_banner

        mock_reader = AsyncMock()
        mock_reader.readline.return_value = b"SSH-2.0-OpenSSH_8.0\n"

        with patch("app.services.banner.asyncio.open_connection", new_callable=AsyncMock) as mock_conn:
            mock_conn.return_value = (mock_reader, AsyncMock())
            result = await grab_banner("192.168.1.1", 22, timeout=5)
            assert result == "SSH-2.0-OpenSSH_8.0"

    @pytest.mark.asyncio
    async def test_grab_banner_http(self):
        from app.services.banner import grab_banner

        mock_reader = AsyncMock()
        mock_reader.read.return_value = (
            b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.49\r\n\r\n"
        )

        with patch("app.services.banner.asyncio.open_connection", new_callable=AsyncMock) as mock_conn:
            mock_conn.return_value = (mock_reader, AsyncMock())
            result = await grab_banner("192.168.1.1", 80, timeout=5)
            assert result == "Server: Apache/2.4.49"

    @pytest.mark.asyncio
    async def test_grab_banner_connection_refused(self):
        from app.services.banner import grab_banner

        with patch("app.services.banner.asyncio.open_connection", new_callable=AsyncMock) as mock_conn:
            mock_conn.side_effect = ConnectionRefusedError()
            result = await grab_banner("192.168.1.1", 22, timeout=5)
            assert result is None

    @pytest.mark.asyncio
    async def test_grab_banner_timeout(self):
        from app.services.banner import grab_banner

        with patch("app.services.banner.asyncio.open_connection", new_callable=AsyncMock) as mock_conn:
            mock_conn.side_effect = TimeoutError()
            result = await grab_banner("192.168.1.1", 22, timeout=1)
            assert result is None

    @pytest.mark.asyncio
    async def test_grab_banner_generic_fallback(self):
        from app.services.banner import grab_banner

        mock_reader = AsyncMock()
        mock_reader.readline.return_value = b"220 FTP server ready\n"

        with patch("app.services.banner.asyncio.open_connection", new_callable=AsyncMock) as mock_conn:
            mock_conn.return_value = (mock_reader, AsyncMock())
            # Port 21 devrait matcher FTP grabber, mais on teste un port non standard
            result = await grab_banner("192.168.1.1", 12345, timeout=5)
            # Le fallback envoie \r\n et lit la réponse
            assert result is not None


class TestSearchCves:
    """Tests de la recherche CVE."""

    @pytest.mark.asyncio
    async def test_search_cves_success(self):
        from app.services.vulnerability import search_cves

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "vulnerabilities": [
                {
                    "cve": {
                        "id": "CVE-2024-1234",
                        "descriptions": [
                            {
                                "lang": "en",
                                "value": "Test vulnerability description",
                            }
                        ],
                        "metrics": {
                            "cvssMetricV31": [
                                {
                                    "cvssData": {
                                        "baseScore": 7.5,
                                        "baseSeverity": "HIGH",
                                    }
                                }
                            ]
                        },
                        "published": "2024-01-15T00:00:00.000",
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            results = await search_cves("openssh", "8.0")
            assert len(results) >= 1
            assert results[0]["cve_id"] == "CVE-2024-1234"
            assert results[0]["severity"] == "high"
            assert results[0]["cvss_score"] == 7.5

    @pytest.mark.asyncio
    async def test_search_cves_api_error(self):
        from app.services.vulnerability import search_cves, _CACHE
        import httpx

        # Vider le cache pour éviter la pollution entre tests
        for k in list(_CACHE.keys()):
            del _CACHE[k]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.HTTPError("API Error")
            results = await search_cves("unknownservice", "9.9.9")
            # Doit retourner une liste vide en cas d'erreur sans cache
            assert results == []

    @pytest.mark.asyncio
    async def test_search_cves_empty_results(self):
        from app.services.vulnerability import search_cves

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"vulnerabilities": []}

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            results = await search_cves("non-existent-service", "0.0")
            assert results == []


class TestMapToMitre:
    """Tests du mapping MITRE ATT&CK."""

    def test_map_ssh(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("ssh")
        assert len(results) >= 2
        technique_ids = [t["technique_id"] for t in results]
        assert "T1021.004" in technique_ids
        assert "T1110" in technique_ids

    def test_map_http(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("http")
        assert len(results) >= 2
        technique_ids = [t["technique_id"] for t in results]
        assert "T1190" in technique_ids
        assert "T1071.001" in technique_ids

    def test_map_https(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("https")
        assert len(results) >= 2

    def test_map_ftp(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("ftp")
        assert len(results) >= 2
        technique_ids = [t["technique_id"] for t in results]
        assert "T1048" in technique_ids

    def test_map_smb(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("smb")
        assert len(results) >= 2
        technique_ids = [t["technique_id"] for t in results]
        assert "T1021.002" in technique_ids
        assert "T1550.002" in technique_ids

    def test_map_unknown_service(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("unknown_service")
        assert results == []

    def test_map_with_cve(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("http", cve_id="CVE-2021-41773")
        assert len(results) >= 1
        assert results[0]["technique_id"] == "T1190"

    def test_map_normalizes_service_name(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("OpenSSH")
        technique_ids = [t["technique_id"] for t in results]
        assert "T1021.004" in technique_ids

        results2 = map_to_mitre("APACHE HTTPD")
        technique_ids2 = [t["technique_id"] for t in results2]
        assert "T1190" in technique_ids2

    def test_map_rdp(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("rdp")
        assert len(results) >= 2
        technique_ids = [t["technique_id"] for t in results]
        assert "T1021.001" in technique_ids

    def test_map_dns(self):
        from app.services.mitre import map_to_mitre

        results = map_to_mitre("dns")
        assert len(results) >= 1
        technique_ids = [t["technique_id"] for t in results]
        assert "T1071.004" in technique_ids


class TestPingHost:
    """Tests de la fonction ping interne."""

    @pytest.mark.asyncio
    async def test_ping_host_success(self):
        from app.services.discovery import _ping_host

        mock_process = AsyncMock()
        mock_process.wait.return_value = 0

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_sub:
            mock_sub.return_value = mock_process
            result = await _ping_host("192.168.1.1", timeout=1)
            assert result is True

    @pytest.mark.asyncio
    async def test_ping_host_failure(self):
        from app.services.discovery import _ping_host

        mock_process = AsyncMock()
        mock_process.wait.return_value = 1

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_sub:
            mock_sub.return_value = mock_process
            result = await _ping_host("192.168.1.1", timeout=1)
            assert result is False


class TestTCPScanPort:
    """Tests du scan TCP interne."""

    @pytest.mark.asyncio
    async def test_tcp_scan_open(self):
        from app.services.scanner import _tcp_scan_port

        with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_conn:
            mock_writer = AsyncMock()
            mock_conn.return_value = (AsyncMock(), mock_writer)
            result = await _tcp_scan_port("192.168.1.1", 80)
            assert result["state"] == "open"
            assert result["port"] == 80

    @pytest.mark.asyncio
    async def test_tcp_scan_closed(self):
        from app.services.scanner import _tcp_scan_port

        with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_conn:
            mock_conn.side_effect = ConnectionRefusedError()
            result = await _tcp_scan_port("192.168.1.1", 80)
            assert result["state"] == "closed"
