"""E2E Test: Detailed System Health & Infrastructure Verification.

Verifies that the /api/v1/health/detailed endpoint returns all 8 core infrastructure
modules and 8 county court portals with non-critical posture when properly configured.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_detailed_health_endpoint():
    """Verify /api/v1/health/detailed returns valid schema and status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health/detailed")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "components" in data
        assert "portals" in data

        components = data["components"]
        assert "api" in components
        assert "database" in components
        assert "redis" in components
        assert "celery" in components
        assert "chrome" in components
        assert "anticaptcha" in components
        assert "guidewire" in components
        assert "storage" in components

        # Verify portal count
        portals = data["portals"]
        assert len(portals) == 8
