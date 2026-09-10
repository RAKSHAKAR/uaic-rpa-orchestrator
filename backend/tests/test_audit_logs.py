"""Unit and integration tests for Audit Log model, service, redaction, and API endpoints."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import TaskAsyncSessionLocal, init_db
from app.main import app
from app.models.audit_log import AuditLog
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.services.audit_service import (
    extract_client_context,
    log_audit_event_async,
    sanitize_payload,
)


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    """Ensure database tables and columns are initialized."""
    await init_db()
    yield


def test_sanitize_payload_zero_leakage():
    """Verify recursive redaction of sensitive credentials with [REDACTED]."""
    raw_payload = {
        "user_id": "operator_1",
        "api_key": "SECRET_KEY_12345",
        "password": "MySuperSecretPassword!",
        "client_secret": "xyz789_secret",
        "access_token": "bearer eyJhbGciOi...",
        "nested_config": {
            "anticaptcha_api_key": "anti_key_999",
            "proxy_url": "http://user:pass@proxy.com:8080",
            "safe_field": "public_data",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----...",
        },
        "items": [
            {"name": "test", "token": "sensitive_token_item"},
            {"safe_array_item": 1234},
        ],
    }

    sanitized = sanitize_payload(raw_payload)

    # Verify sensitive fields are redacted
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["client_secret"] == "[REDACTED]"
    assert sanitized["access_token"] == "[REDACTED]"
    assert sanitized["nested_config"]["anticaptcha_api_key"] == "[REDACTED]"
    assert sanitized["nested_config"]["private_key"] == "[REDACTED]"
    assert sanitized["items"][0]["token"] == "[REDACTED]"

    # Verify safe fields are preserved intact
    assert sanitized["user_id"] == "operator_1"
    assert sanitized["nested_config"]["safe_field"] == "public_data"
    assert sanitized["items"][0]["name"] == "test"
    assert sanitized["items"][1]["safe_array_item"] == 1234


def test_extract_client_context_none():
    """Verify fallback defaults when request is None."""
    ctx = extract_client_context(None)
    assert ctx["ip_address"] == "127.0.0.1"
    assert ctx["user_agent"] == "system/background-worker"
    assert ctx["user_id"] == "system"
    assert ctx["user_email"] == "system@test.com"


@pytest.mark.asyncio
async def test_audit_log_service_and_db_persistence():
    """Verify writing audit log entries to the database via log_audit_event_async."""
    entry_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        res = await log_audit_event_async(
            session=session,
            action="TEST_ACTION",
            entity_type="TEST_ENTITY",
            description="Test description for audit log entry",
            user_id="test_runner",
            user_email="test@runner.com",
            ip_address="192.168.1.50",
            user_agent="pytest/8.0",
            status="SUCCESS",
            details={"test_metric": 42, "password": "should_be_masked"},
            claim_number="CLM-TEST-001",
            entity_id=entry_id,
        )
        await session.commit()

        assert res is not None
        assert res.id is not None
        assert res.action == "TEST_ACTION"
        assert res.details["test_metric"] == 42
        assert res.details["password"] == "[REDACTED]"

        # Verify reading back from DB directly
        db_log = await session.get(AuditLog, res.id)
        assert db_log is not None
        assert db_log.action == "TEST_ACTION"
        assert db_log.claim_number == "CLM-TEST-001"
        assert db_log.status == "SUCCESS"


@pytest.mark.asyncio
async def test_audit_logs_endpoints():
    """Verify GET /api/v1/audit-logs pagination, search, and filtering."""
    test_uuid = uuid.uuid4().hex[:8].upper()
    unique_action = f"ACTION_{test_uuid}"

    # Insert test events
    async with TaskAsyncSessionLocal() as session:
        await log_audit_event_async(
            session=session,
            action=unique_action,
            entity_type="CLAIM",
            description=f"Description containing unique phrase {test_uuid}",
            user_id="special_user",
            user_email="special@user.com",
            status="SUCCESS",
            details={"sample": 1},
            claim_number=f"CLM-{test_uuid}",
        )
        await log_audit_event_async(
            session=session,
            action=unique_action,
            entity_type="SETTINGS",
            description=f"Second entry for {test_uuid}",
            user_id="special_user",
            user_email="special@user.com",
            status="FAILED",
            details={"error": "test failure"},
        )
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Search by action
        res = await client.get("/api/v1/audit-logs", params={"action": unique_action})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2
        assert all(item["action"] == unique_action for item in data["items"])

        # 2. Search by query string
        res_search = await client.get("/api/v1/audit-logs", params={"search": test_uuid})
        assert res_search.status_code == 200
        search_data = res_search.json()
        assert search_data["total"] >= 2

        # 3. Filter by status
        res_status = await client.get(
            "/api/v1/audit-logs",
            params={"action": unique_action, "status": "FAILED"},
        )
        assert res_status.status_code == 200
        failed_data = res_status.json()
        assert failed_data["total"] == 1
        assert failed_data["items"][0]["status"] == "FAILED"

        # 4. Get by ID
        log_id = failed_data["items"][0]["id"]
        res_id = await client.get(f"/api/v1/audit-logs/{log_id}")
        assert res_id.status_code == 200
        assert res_id.json()["id"] == log_id


@pytest.mark.asyncio
async def test_audit_logs_stats_and_export():
    """Verify GET /api/v1/audit-logs/stats and GET /api/v1/audit-logs/export."""
    # Ensure at least one audit log exists
    async with TaskAsyncSessionLocal() as session:
        await log_audit_event_async(
            session=session,
            action="EXPORT_TEST_ACTION",
            entity_type="CLAIM",
            description="Export test audit event",
            user_id="export_tester",
            user_email="tester@test.com",
            status="SUCCESS",
        )
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test Stats
        res_stats = await client.get("/api/v1/audit-logs/stats")
        assert res_stats.status_code == 200
        stats = res_stats.json()
        assert "total_events" in stats
        assert "total_today" in stats
        assert "total_claims_ops" in stats
        assert "total_settings_ops" in stats
        assert "total_match_reviews" in stats
        assert "total_failures" in stats
        assert stats["total_events"] >= 1

        # Test CSV Export
        res_csv = await client.get("/api/v1/audit-logs/export", params={"format": "csv"})
        assert res_csv.status_code == 200
        assert "text/csv" in res_csv.headers.get("content-type", "")
        assert "User ID,User Email" in res_csv.text

        # Test JSON Export
        res_json = await client.get("/api/v1/audit-logs/export", params={"format": "json"})
        assert res_json.status_code == 200
        assert "application/json" in res_json.headers.get("content-type", "")
        export_data = res_json.json()
        assert isinstance(export_data, list)


@pytest.mark.asyncio
async def test_claim_audit_logs_and_clean_preservation():
    """Verify GET /api/v1/claims/{id}/audit-logs and verify clean preserves audit logs."""
    claim_id = str(uuid.uuid4())
    unique_clm_num = f"CLM-TEST-{uuid.uuid4().hex[:6]}"

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=unique_clm_num,
            insured_first_name="John",
            insured_last_name="Doe",
            claimant_first_name="Jane",
            claimant_last_name="Smith",
            driver_first_name="Jane",
            driver_last_name="Smith",
            policy_state="FL",
            loss_location_state="FL",
            record_status=RecordStatusEnum.NEW,
            retry_count=0,
        )
        session.add(claim)
        await log_audit_event_async(
            session=session,
            action="CLAIM_CREATED",
            entity_type="CLAIM",
            description=f"Created claim {unique_clm_num}",
            entity_id=claim_id,
            claim_number=unique_clm_num,
            status="SUCCESS",
            details={"insured": "John Doe"},
        )
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test claim-specific audit logs endpoint
        res_claim_logs = await client.get(f"/api/v1/claims/{claim_id}/audit-logs")
        assert res_claim_logs.status_code == 200
        claim_logs = res_claim_logs.json()
        assert len(claim_logs) >= 1
        assert claim_logs[0]["claim_number"] == unique_clm_num

        # Verify database cleanup does NOT delete audit logs
        # Count audit logs before clean
        async with TaskAsyncSessionLocal() as session:
            q_count = select(AuditLog)
            res_before = await session.execute(q_count)
            count_before = len(res_before.scalars().all())

        # Perform clean
        res_clean = await client.post("/api/v1/claims/clean")
        assert res_clean.status_code == 200

        # Verify audit logs still exist and have increased (because DATABASE_CLEARED was logged)
        async with TaskAsyncSessionLocal() as session:
            res_after = await session.execute(q_count)
            count_after = len(res_after.scalars().all())
            assert count_after >= count_before
