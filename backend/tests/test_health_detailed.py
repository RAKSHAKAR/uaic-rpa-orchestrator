"""Automated test suite for detailed system observability and portal ping endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture(scope="module", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_health_check_basic():
    """Verify standard /health endpoint returns online and database status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "online"
        assert data["database"] == "healthy"
        assert "version" in data


@pytest.mark.asyncio
async def test_health_detailed_observability():
    """Verify /api/v1/health/detailed returns comprehensive system diagnostics across all 8 components and portals."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health/detailed")
        assert res.status_code == 200
        data = res.json()

        assert data["status"] in ("healthy", "warning", "critical")
        assert "timestamp" in data
        assert "environment" in data
        assert "version" in data

        components = data["components"]
        # Required components from Prompt Section 140
        assert "api" in components
        assert "database" in components
        assert "redis" in components
        assert "celery" in components
        assert "chrome" in components
        assert "anticaptcha" in components
        assert "guidewire" in components
        assert "storage" in components

        assert components["api"]["status"] == "healthy"
        assert components["database"]["status"] == "healthy"
        assert "connected" in components["database"]["details"]

        # Portals registry verification (all 8 portals)
        portals = data["portals"]
        expected_portals = [
            "broward",
            "hillsborough",
            "miami",
            "travis",
            "dallas",
            "harris_jp",
            "harris_district",
            "harris_cclerk",
        ]
        for pkey in expected_portals:
            assert pkey in portals
            assert portals[pkey]["key"] == pkey
            assert "url" in portals[pkey]
            assert "enabled" in portals[pkey]


@pytest.mark.asyncio
async def test_portal_ping_endpoints():
    """Verify ping endpoint handles valid and unknown portal keys."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Unknown portal
        res_unknown = await client.get("/api/v1/portals/nonexistent_portal/ping")
        assert res_unknown.status_code == 200
        data_un = res_unknown.json()
        assert data_un["reachable"] is False
        assert "Unknown portal key" in data_un["error"]

        # 2. Known portal (e.g. broward) via /api/v1/portals/broward/ping
        res_known = await client.get("/api/v1/portals/broward/ping")
        assert res_known.status_code == 200
        data_known = res_known.json()
        assert data_known["portal_key"] == "broward"
        assert "Broward" in data_known["portal_name"]
        assert "latency_ms" in data_known
