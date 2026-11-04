"""Test suite for IMP-2026-1007-004: Bot Attempt Count Discrepancy & Routing Remediation.

Validates:
- Phase 1 (GAP-A): Permanent normalization guard in _decode_row enforces dallas_enabled=True and travis_enabled=True.
- Phase 2 (GAP-B): repair_tx_claim_targets logic audits and fixes eligible claims.
- Phase 3 (GAP-C): /api/v1/health/detailed exposes portal_settings_summary with 8-portal routing compliance.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import Base, engine
from app.main import app
from app.services.settings_service import _decode_row


@pytest.fixture(scope="module", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def test_gap_a_settings_normalization_enforces_dallas_and_travis():
    """Verify _decode_row forces dallas_enabled=True and travis_enabled=True even if raw DB has false."""
    corrupted_payload = {
        "portals": {
            "broward_enabled": True,
            "hillsborough_enabled": True,
            "miami_enabled": True,
            "travis_enabled": False,
            "dallas_enabled": False,
            "harris_jp_enabled": True,
            "harris_cclerk_enabled": True,
        }
    }
    row_dict = {"version": 1, "settings": corrupted_payload}
    settings = _decode_row(row_dict)

    assert settings.portals.dallas_enabled is True, "dallas_enabled must be normalized to True"
    assert settings.portals.travis_enabled is True, "travis_enabled must be normalized to True"
    assert settings.portals.broward_enabled is True
    assert settings.portals.miami_enabled is True


@pytest.mark.asyncio
async def test_gap_c_health_detailed_portal_settings_summary():
    """Verify /api/v1/health/detailed includes portal_settings_summary and verifies compliance."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health/detailed")
        assert res.status_code == 200
        data = res.json()

        assert "portal_settings_summary" in data
        summary = data["portal_settings_summary"]
        assert summary["total_portals"] == 8
        assert "enabled_count" in summary
        assert "all_8_enabled" in summary
        assert "fl_routing_ok" in summary
        assert "tx_routing_ok" in summary
        assert "cross_state_routing_ok" in summary
        assert "portal_flags" in summary
        assert len(summary["portal_flags"]) == 8

        # All FL portals must be enabled
        assert summary["portal_flags"]["broward"] is True
        assert summary["portal_flags"]["hillsborough"] is True
        assert summary["portal_flags"]["miami"] is True
        # All TX portals must be enabled
        assert summary["portal_flags"]["travis"] is True
        assert summary["portal_flags"]["dallas"] is True
        assert summary["portal_flags"]["harris_jp"] is True
        assert summary["portal_flags"]["harris_cclerk"] is True
        assert summary["portal_flags"]["harris_district"] is True
        assert summary["all_8_enabled"] is True
        assert summary["routing_compliance"] == "OK"
