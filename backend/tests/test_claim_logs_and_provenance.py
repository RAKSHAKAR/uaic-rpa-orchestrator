"""Tests for Claim Provenance (created_by, modified_by, created_on, modified_on)
and Unified Claim Logs & Diagnostics (audit logs, processing logs, exception logs, portal console logs).
"""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import TaskAsyncSessionLocal, init_db
from app.main import app
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.services.audit_service import log_audit_event_async


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    """Ensure database schema is ready."""
    await init_db()
    yield


@pytest.mark.asyncio
async def test_claim_model_provenance_properties():
    """Verify ClaimRecord model provenance fields and created_on/modified_on alias properties."""
    claim = ClaimRecord(
        id=str(uuid.uuid4()),
        claim_number=f"PRV-{uuid.uuid4().hex[:6].upper()}",
        insured_first_name="Jane",
        insured_last_name="Doe",
        claimant_first_name="John",
        claimant_last_name="Smith",
        created_by="test_actor",
        modified_by="test_actor",
        created_at=datetime(2026, 9, 17, 10, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 9, 17, 10, 30, 0, tzinfo=UTC),
    )

    assert claim.created_by == "test_actor"
    assert claim.modified_by == "test_actor"
    assert claim.created_on == claim.created_at
    assert claim.modified_on == claim.updated_at


@pytest.mark.asyncio
async def test_create_and_update_claim_provenance_api():
    """Verify REST API preserves creator and updater identities."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_num = f"API-{uuid.uuid4().hex[:6].upper()}"
        create_resp = await client.post(
            "/api/v1/claims",
            json={
                "claim_number": unique_num,
                "insured_first_name": "Provenance",
                "insured_last_name": "Insured",
                "claimant_first_name": "Provenance",
                "claimant_last_name": "Claimant",
                "dol": "09/17/2026",
                "policy_state": "Florida",
                "loss_location_state": "Florida",
                "created_by": "operator:ingest_specialist",
            },
            headers={"x-user-email": "operator:ingest_specialist"},
        )
        assert create_resp.status_code == 201, create_resp.text
        claim_data = create_resp.json()
        claim_id = claim_data["id"]

        assert claim_data["created_by"] == "operator:ingest_specialist"
        assert claim_data["modified_by"] == "operator:ingest_specialist"
        assert claim_data["created_on"] is not None
        assert claim_data["modified_on"] is not None

        # Update the claim with a different actor
        update_resp = await client.put(
            f"/api/v1/claims/{claim_id}",
            json={"insured_first_name": "ProvenanceUpdated"},
            headers={"x-user-email": "manager:supervisor_alice"},
        )
        assert update_resp.status_code == 200, update_resp.text
        updated_data = update_resp.json()

        assert updated_data["created_by"] == "operator:ingest_specialist"
        assert updated_data["modified_by"] == "manager:supervisor_alice"


@pytest.mark.asyncio
async def test_combined_logs_endpoint():
    """Verify GET /api/v1/claims/{id}/combined-logs returns structured audit, processing, and exception logs."""
    unique_num = f"LOG-{uuid.uuid4().hex[:6].upper()}"
    claim_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=unique_num,
            insured_first_name="Logs",
            insured_last_name="Tester",
            claimant_first_name="Target",
            claimant_last_name="Subject",
            record_status=RecordStatusEnum.SCRAPING_IN_PROGRESS,
            created_by="system:batch_import",
            modified_by="worker:scrapers",
            action_timings={
                "stages": {
                    "broward": {
                        "name": "Broward Portal Scraper",
                        "status": "FAILED",
                        "duration_seconds": 12.34,
                        "error": "Timeout waiting for reCAPTCHA resolution",
                    },
                    "hillsborough": {
                        "name": "Hillsborough Portal Scraper",
                        "status": "SUCCESS",
                        "duration_seconds": 8.5,
                        "cases_found": 2,
                    },
                }
            },
        )
        session.add(claim)
        await session.commit()

        # Add AuditLog event
        await log_audit_event_async(
            session=session,
            action="PORTAL_SCRAPING_FAILED",
            entity_type="CLAIM",
            description="Portal broward scraping encounter unhandled error",
            entity_id=claim_id,
            claim_number=unique_num,
            user_id="worker:scrapers",
            user_email="worker:scrapers",
            status="FAILED",
            details={
                "portal_key": "broward",
                "exception_type": "TimeoutError",
                "error_message": "Timeout waiting for reCAPTCHA resolution",
                "traceback": "Traceback (most recent call last):\n  File 'broward.py', line 42",
            },
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/api/v1/claims/{claim_id}/combined-logs")
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["claim_id"] == claim_id
        assert data["claim_number"] == unique_num
        assert data["created_by"] == "system:batch_import"
        assert data["modified_by"] == "worker:scrapers"
        assert data["created_on"] is not None
        assert data["modified_on"] is not None

        # Verify audit logs
        assert len(data["audit_logs"]) >= 1
        assert any(log["action"] == "PORTAL_SCRAPING_FAILED" for log in data["audit_logs"])

        # Verify processing logs extracted from stages
        assert len(data["processing_logs"]) >= 2
        stage_names = [pl["stage"] for pl in data["processing_logs"]]
        assert "broward" in stage_names
        assert "hillsborough" in stage_names

        # Verify exception logs extracted from failure audit events and failed stages
        assert len(data["exception_logs"]) >= 1
        exc = data["exception_logs"][0]
        assert exc["portal_key"] == "broward"
        assert "reCAPTCHA" in exc["message"]
