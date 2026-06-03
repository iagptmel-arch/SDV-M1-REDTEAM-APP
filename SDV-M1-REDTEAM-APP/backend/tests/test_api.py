"""
Tests d'intégration de l'API
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
def mock_db():
    """Patche les fonctions de la base de données pour tous les tests."""
    with patch("app.api.v1.hosts.find_many", new_callable=AsyncMock) as mock_find_many, \
         patch("app.api.v1.hosts.find_one", new_callable=AsyncMock) as mock_find_one, \
         patch("app.api.v1.hosts.insert_one", new_callable=AsyncMock) as mock_insert_one, \
         patch("app.api.v1.hosts.delete_one", new_callable=AsyncMock) as mock_delete_one, \
         patch("app.api.v1.hosts.count", new_callable=AsyncMock) as mock_count, \
         patch("app.api.v1.services.find_many", new_callable=AsyncMock) as mock_svc_find_many, \
         patch("app.api.v1.services.find_one", new_callable=AsyncMock) as mock_svc_find_one, \
         patch("app.api.v1.services.insert_one", new_callable=AsyncMock) as mock_svc_insert_one, \
         patch("app.api.v1.vulnerabilities.find_many", new_callable=AsyncMock) as mock_vuln_find_many, \
         patch("app.api.v1.vulnerabilities.find_one", new_callable=AsyncMock) as mock_vuln_find_one, \
         patch("app.api.v1.vulnerabilities.insert_one", new_callable=AsyncMock) as mock_vuln_insert_one, \
         patch("app.api.v1.campaigns.find_many", new_callable=AsyncMock) as mock_camp_find_many, \
         patch("app.api.v1.campaigns.find_one", new_callable=AsyncMock) as mock_camp_find_one, \
         patch("app.api.v1.campaigns.insert_one", new_callable=AsyncMock) as mock_camp_insert_one, \
         patch("app.api.v1.campaigns.update_one", new_callable=AsyncMock) as mock_camp_update_one, \
         patch("app.api.v1.auth.find_one", new_callable=AsyncMock) as mock_auth_find_one, \
         patch("app.api.v1.auth.insert_one", new_callable=AsyncMock) as mock_auth_insert_one, \
         patch("app.api.v1.dashboard.count", new_callable=AsyncMock) as mock_dash_count, \
         patch("app.api.v1.dashboard.find_many", new_callable=AsyncMock) as mock_dash_find_many, \
         patch("app.core.database.get_db", return_value=MagicMock()) as mock_get_db:

        yield {
            "find_many": mock_find_many,
            "find_one": mock_find_one,
            "insert_one": mock_insert_one,
            "delete_one": mock_delete_one,
            "count": mock_count,
            "svc_find_many": mock_svc_find_many,
            "svc_find_one": mock_svc_find_one,
            "svc_insert_one": mock_svc_insert_one,
            "vuln_find_many": mock_vuln_find_many,
            "vuln_find_one": mock_vuln_find_one,
            "vuln_insert_one": mock_vuln_insert_one,
            "camp_find_many": mock_camp_find_many,
            "camp_find_one": mock_camp_find_one,
            "camp_insert_one": mock_camp_insert_one,
            "camp_update_one": mock_camp_update_one,
            "auth_find_one": mock_auth_find_one,
            "auth_insert_one": mock_auth_insert_one,
            "dash_count": mock_dash_count,
            "dash_find_many": mock_dash_find_many,
            "get_db": mock_get_db,
        }


@pytest.mark.asyncio
async def test_health_check():
    """Teste le endpoint health."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data


@pytest.mark.asyncio
async def test_list_hosts_empty(mock_db):
    """Teste la liste des hôtes quand il n'y en a pas."""
    mock_db["find_many"].return_value = []
    mock_db["count"].return_value = 0

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/hosts")
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_list_hosts_with_data(mock_db):
    """Teste la liste des hôtes avec des données."""
    mock_host = {
        "_id": "507f1f77bcf86cd799439011",
        "ip": "192.168.1.1",
        "hostname": "router.local",
        "os": "Linux",
        "status": "up",
        "discovered_at": "2026-01-01T00:00:00",
        "campaign_id": None,
    }
    mock_db["find_many"].return_value = [mock_host]
    mock_db["count"].return_value = 1

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/hosts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ip"] == "192.168.1.1"
        assert data[0]["hostname"] == "router.local"


@pytest.mark.asyncio
async def test_get_host(mock_db):
    """Teste la récupération d'un hôte par ID."""
    mock_host = {
        "_id": "507f1f77bcf86cd799439011",
        "ip": "192.168.1.1",
        "hostname": "router.local",
        "os": "Linux",
        "status": "up",
        "discovered_at": "2026-01-01T00:00:00",
        "campaign_id": None,
    }
    mock_db["find_one"].return_value = mock_host

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/hosts/507f1f77bcf86cd799439011")
        assert response.status_code == 200
        assert response.json()["ip"] == "192.168.1.1"


@pytest.mark.asyncio
async def test_get_host_not_found(mock_db):
    """Teste la récupération d'un hôte inexistant."""
    mock_db["find_one"].return_value = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/hosts/507f1f77bcf86cd799439099")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_host(mock_db):
    """Teste la création d'un hôte."""
    mock_db["find_one"].return_value = None  # Pas de conflit
    mock_db["insert_one"].return_value = "507f1f77bcf86cd799439011"

    # Après création, retourner l'hôte créé
    async def find_one_side_effect(collection, query):
        if query.get("_id") == "507f1f77bcf86cd799439011":
            return {
                "_id": "507f1f77bcf86cd799439011",
                "ip": "10.0.0.1",
                "hostname": None,
                "os": None,
                "status": "unknown",
                "discovered_at": "2026-01-01T00:00:00",
                "campaign_id": None,
            }
        return None

    mock_db["find_one"].side_effect = find_one_side_effect

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/hosts",
            json={"ip": "10.0.0.1"},
        )
        assert response.status_code == 201
        assert response.json()["ip"] == "10.0.0.1"


@pytest.mark.asyncio
async def test_create_host_conflict(mock_db):
    """Teste la création d'un hôte avec IP déjà existante."""
    mock_db["find_one"].return_value = {
        "_id": "existing",
        "ip": "10.0.0.1",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/hosts",
            json={"ip": "10.0.0.1"},
        )
        assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_host(mock_db):
    """Teste la suppression d'un hôte."""
    mock_db["delete_one"].return_value = True

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/v1/hosts/507f1f77bcf86cd799439011")
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_host_not_found(mock_db):
    """Teste la suppression d'un hôte inexistant."""
    mock_db["delete_one"].return_value = False

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/v1/hosts/507f1f77bcf86cd799439099")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_services(mock_db):
    """Teste la liste des services."""
    mock_svc = {
        "_id": "svc001",
        "host_id": "host001",
        "port": 22,
        "protocol": "tcp",
        "name": "ssh",
        "version": "OpenSSH_8.0",
        "banner": "SSH-2.0-OpenSSH_8.0",
        "discovered_at": "2026-01-01T00:00:00",
        "campaign_id": None,
    }
    mock_db["svc_find_many"].return_value = [mock_svc]
    mock_db["svc_find_one"].return_value = {
        "_id": "host001",
        "ip": "10.0.0.1",
        "hostname": "test-host",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/services")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["port"] == 22
        assert data[0]["name"] == "ssh"


@pytest.mark.asyncio
async def test_create_service(mock_db):
    """Teste la création d'un service."""
    mock_db["svc_find_one"].return_value = {
        "_id": "host001",
        "ip": "10.0.0.1",
    }

    mock_db["svc_insert_one"].return_value = "svc001"

    async def find_one_side_effect(collection, query):
        if collection == "services" and query.get("_id") == "svc001":
            return {
                "_id": "svc001",
                "host_id": "host001",
                "port": 80,
                "protocol": "tcp",
                "name": "http",
                "version": "Apache/2.4.49",
                "banner": None,
                "discovered_at": "2026-01-01T00:00:00",
                "campaign_id": None,
            }
        if collection == "hosts" and query.get("_id") == "host001":
            return {"_id": "host001", "ip": "10.0.0.1"}
        return None

    mock_db["svc_find_one"].side_effect = find_one_side_effect

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/services",
            json={
                "host_id": "host001",
                "port": 80,
                "protocol": "tcp",
                "name": "http",
                "version": "Apache/2.4.49",
            },
        )
        assert response.status_code == 201
        assert response.json()["port"] == 80


@pytest.mark.asyncio
async def test_auth_register(mock_db):
    """Teste l'inscription d'un utilisateur."""
    mock_db["auth_find_one"].return_value = None  # Pas d'utilisateur existant
    mock_db["auth_insert_one"].return_value = "user001"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "user_id" in data


@pytest.mark.asyncio
async def test_auth_login(mock_db):
    """Teste l'authentification."""
    from app.core.security import hash_password

    hashed = hash_password("securepass123")
    mock_db["auth_find_one"].return_value = {
        "_id": "user001",
        "username": "testuser",
        "hashed_password": hashed,
        "role": "analyst",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "securepass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_login_invalid(mock_db):
    """Teste l'authentification avec mauvais mot de passe."""
    import bcrypt
    valid_hash = bcrypt.hashpw(b"realpassword", bcrypt.gensalt()).decode("utf-8")
    mock_db["auth_find_one"].return_value = {
        "_id": "user001",
        "username": "testuser",
        "hashed_password": valid_hash,
        "role": "viewer",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_stats(mock_db):
    """Teste les statistiques du dashboard."""
    def count_side_effect(collection, query=None):
        counts = {
            "hosts": 10,
            "services": 25,
            "vulnerabilities": 8,
            "campaigns": 3,
        }
        if query and "severity" in query:
            severity_map = {
                "critical": 2,
                "high": 3,
                "medium": 2,
                "low": 1,
                "info": 0,
            }
            return severity_map.get(query["severity"], 0)
        return counts.get(collection, 0)

    mock_db["dash_count"].side_effect = count_side_effect
    from datetime import datetime
    mock_db["dash_find_many"].return_value = [
        {
            "_id": "camp001",
            "name": "Test Campaign",
            "status": "completed",
            "created_at": datetime(2026, 1, 1, 0, 0, 0),
        }
    ]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["hosts"] == 10
        assert data["services"] == 25
        assert data["vulnerabilities"] == 8
        assert data["campaigns"] == 3
        assert data["by_severity"]["critical"] == 2
        assert data["by_severity"]["high"] == 3
        assert len(data["recent_campaigns"]) == 1
