"""Comprehensive automated test cases for all enterprise features.

Covers:
- Database cleanup endpoint & Redis purge
- Single Claim CRUD (Create, Read, Update, Delete) & Duplicate Prevention
- Bulk Operations (Bulk Delete, Bulk Status, Bulk Start)
- Server-side Pagination, Multi-field Search, and Sorting
- Excel (.xlsx) and CSV (.csv) Export
- Automatic Sequential Queue Runner & Manual Mode Controls
- High-Resolution Stage Execution Timing Telemetry
- Attended Chrome & AntiCaptcha Extension Integration
"""

import io
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient

from app.automation.base import BaseCourtScraper
from app.core.database import Base, engine
from app.main import app
from app.schemas.settings import SystemSettings


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure database schema is created before running enterprise tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_single_claim_create_and_duplicate_prevention():
    """Test POST /api/v1/claims creates a record and prevents duplicates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unique_claim_num = f"AUTOTEST-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        
        payload = {
            "claim_number": unique_claim_num,
            "exposure_number": "1",
            "insured_first_name": "John",
            "insured_last_name": "AutomatedInsured",
            "claimant_first_name": "Jane",
            "claimant_last_name": "AutomatedClaimant",
            "dol": "01/15/2025",
            "policy_state": "Florida",
            "loss_location_state": "Florida",
        }
        
        # 1. Create claim
        res = await client.post("/api/v1/claims", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["claim_number"] == unique_claim_num
        assert data["insured_name"] == "John AutomatedInsured"
        assert data["claimant_name"] == "Jane AutomatedClaimant"
        assert data["record_status"] == "NEW"
        # Florida bot targets should be auto-resolved to 'Yes'
        fl_broward = next(b for b in data["bots"] if "Broward" in b["name"])
        assert fl_broward["target"] == "Yes"

        # 2. Prevent duplicate claim number
        dup_res = await client.post("/api/v1/claims", json=payload)
        assert dup_res.status_code == 409
        assert "already exists" in dup_res.json()["detail"]


@pytest.mark.asyncio
async def test_single_claim_read_update_delete():
    """Test full CRUD lifecycle on a single claim record."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_num = f"CRUD-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        
        # 1. Create
        create_res = await client.post("/api/v1/claims", json={
            "claim_number": c_num,
            "insured_first_name": "Alice",
            "insured_last_name": "Original",
            "policy_state": "Texas",
            "loss_location_state": "Texas",
        })
        assert create_res.status_code == 201
        claim_id = create_res.json()["id"]

        # 2. Read (Detail)
        read_res = await client.get(f"/api/v1/claims/{claim_id}")
        assert read_res.status_code == 200
        assert read_res.json()["id"] == claim_id

        # 3. Update (Edit)
        update_res = await client.put(f"/api/v1/claims/{claim_id}", json={
            "insured_last_name": "UpdatedLastname",
            "loss_location_state": "Florida",
        })
        assert update_res.status_code == 200
        assert update_res.json()["insured_name"] == "Alice UpdatedLastname"
        assert update_res.json()["loss_location_state"] == "Florida"

        # 4. Delete
        del_res = await client.delete(f"/api/v1/claims/{claim_id}")
        assert del_res.status_code == 200
        assert del_res.json()["success"] is True

        # Verify not found after delete
        not_found_res = await client.get(f"/api/v1/claims/{claim_id}")
        assert not_found_res.status_code == 404


@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_bulk_operations():
    """Test bulk-status, bulk-start, and bulk-delete endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create 2 claims for bulk testing
        c1 = f"BULK1-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        c2 = f"BULK2-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        
        r1 = await client.post("/api/v1/claims", json={"claim_number": c1})
        r2 = await client.post("/api/v1/claims", json={"claim_number": c2})
        id1, id2 = r1.json()["id"], r2.json()["id"]

        # 1. Bulk Status update
        status_res = await client.post("/api/v1/claims/bulk-status", json={
            "claim_ids": [id1, id2],
            "status": "MANUAL_REVIEW",
        })
        assert status_res.status_code == 200
        assert status_res.json()["affected_count"] == 2

        # Verify status changed
        check1 = await client.get(f"/api/v1/claims/{id1}")
        assert check1.json()["record_status"] == "MANUAL_REVIEW"

        # 2. Bulk Start (queuing automation)
        ready_settings = SystemSettings()
        ready_settings.automation.anticaptcha_api_key = "test-only-key"
        with patch(
            "app.api.v1.endpoints.claims.get_system_settings_async",
            AsyncMock(return_value=ready_settings),
        ):
            start_res = await client.post("/api/v1/claims/bulk-start", json={
                "claim_ids": [id1, id2],
            })
        assert start_res.status_code == 200
        assert start_res.json()["affected_count"] == 2

        # 3. Bulk Delete
        del_res = await client.post("/api/v1/claims/bulk-delete", json={
            "claim_ids": [id1, id2],
        })
        assert del_res.status_code == 200
        assert del_res.json()["affected_count"] == 2

        # Verify deleted
        assert (await client.get(f"/api/v1/claims/{id1}")).status_code == 404
        assert (await client.get(f"/api/v1/claims/{id2}")).status_code == 404


@pytest.mark.asyncio
async def test_server_side_pagination_and_sorting():
    """Test server-side sorting, pagination, search, and filtering."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create records to guarantee presence
        ts = datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')
        await client.post("/api/v1/claims", json={"claim_number": f"SORTA-{ts}", "policy_state": "Florida"})
        await client.post("/api/v1/claims", json={"claim_number": f"SORTB-{ts}", "policy_state": "Texas"})

        # Test sorting
        res_desc = await client.get("/api/v1/claims?sort_by=created_at&sort_order=desc&page_size=10")
        assert res_desc.status_code == 200
        data_desc = res_desc.json()
        assert "total_pages" in data_desc
        assert len(data_desc["items"]) >= 2

        # Test search
        res_search = await client.get(f"/api/v1/claims?search=SORTA-{ts}")
        assert res_search.status_code == 200
        assert res_search.json()["total"] == 1
        assert res_search.json()["items"][0]["claim_number"] == f"SORTA-{ts}"

        # Test state filter
        res_fl = await client.get("/api/v1/claims?state=FL")
        assert res_fl.status_code == 200
        for item in res_fl.json()["items"]:
            state_val = (item.get("loss_location_state") or item.get("policy_state") or "").upper()
            assert "FL" in state_val or "FLORIDA" in state_val


@pytest.mark.asyncio
async def test_excel_and_csv_export():
    """Test GET /api/v1/claims/export for both Excel (.xlsx) and CSV (.csv)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Seed a claim via API to ensure database isn't empty
        payload = {
            "claim_number": "CSV_TEST_001",
            "loss_location_state": "FL",
            "policy_state": "FL",
            "insured_first_name": "CSV",
            "insured_last_name": "Test",
            "record_status": "Pending"
        }
        await client.post("/api/v1/claims", json=payload)

        # 1. Export CSV
        csv_res = await client.get("/api/v1/claims/export?format=csv")
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers.get("content-type", "")
        csv_content = csv_res.text
        assert "Claim Number" in csv_content
        assert "Insured Party" in csv_content
        assert "Status" in csv_content

        # 2. Export Excel
        xlsx_res = await client.get("/api/v1/claims/export?format=xlsx")
        assert xlsx_res.status_code == 200
        assert "spreadsheetml" in xlsx_res.headers.get("content-type", "")
        # Verify valid Excel binary
        df = pd.read_excel(io.BytesIO(xlsx_res.content))
        assert "Claim Number" in df.columns
        assert "Status" in df.columns


@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_automatic_queue_runner_endpoints():
    """Test automatic queue mode status, toggle, pause, and start-all."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get status
        status_res = await client.get("/api/v1/queue/auto-mode")
        assert status_res.status_code == 200
        assert "auto_queue_enabled" in status_res.json()

        # 2. Toggle ON
        ready_settings = SystemSettings()
        ready_settings.automation.anticaptcha_api_key = "test-only-key"
        with patch(
            "app.api.v1.endpoints.queue.get_system_settings_async",
            AsyncMock(return_value=ready_settings),
        ):
            toggle_on = await client.post("/api/v1/queue/auto-mode", json={"enabled": True})
        assert toggle_on.status_code == 200
        assert toggle_on.json()["auto_queue_enabled"] is True

        # 3. Pause
        pause_res = await client.post("/api/v1/queue/pause")
        assert pause_res.status_code == 200
        assert pause_res.json()["status"] == "paused"

        # Verify auto-mode is now False
        check_pause = await client.get("/api/v1/queue/auto-mode")
        assert check_pause.json()["auto_queue_enabled"] is False


@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_manual_captcha_mode_starts_without_solver_key():
    """Manual CAPTCHA mode can start claims and the queue without an API key."""
    manual_settings = SystemSettings()
    manual_settings.automation.anticaptcha_enabled = False
    manual_settings.automation.anticaptcha_api_key = ""
    solver_settings = SystemSettings()
    solver_settings.automation.anticaptcha_enabled = True
    solver_settings.automation.anticaptcha_api_key = ""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        claim_number = f"MANUAL-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        created = await client.post("/api/v1/claims", json={
            "claim_number": claim_number,
            "policy_state": "FL",
            "loss_location_state": "FL",
            "insured_first_name": "Manual",
            "insured_last_name": "Captcha",
        })
        assert created.status_code == 201
        claim_id = created.json()["id"]
        try:
            with patch(
                "app.api.v1.endpoints.queue.get_system_settings_async",
                AsyncMock(return_value=solver_settings),
            ):
                rejected = await client.post("/api/v1/queue/auto-mode", json={"enabled": True})
            assert rejected.status_code == 422

            with (
                patch("app.api.v1.endpoints.claims.get_system_settings_async", AsyncMock(return_value=manual_settings)),
                patch("app.api.v1.endpoints.queue.get_system_settings_async", AsyncMock(return_value=manual_settings)),
                patch("app.core.celery_app.celery_app.send_task"),
            ):
                started = await client.post(f"/api/v1/claims/{claim_id}/start")
                bulk = await client.post("/api/v1/claims/bulk-start", json={"claim_ids": [claim_id]})
                queue = await client.post("/api/v1/queue/auto-mode", json={"enabled": True})
            assert started.status_code == 200
            assert bulk.status_code == 200
            assert queue.status_code == 200
        finally:
            await client.post("/api/v1/queue/pause")
            await client.delete(f"/api/v1/claims/{claim_id}")


@pytest.mark.asyncio
async def test_database_cleanup_endpoint():
    """Test POST /api/v1/claims/clean purges records and flushes worker queues."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        clean_res = await client.post("/api/v1/claims/clean")
        assert clean_res.status_code == 200
        data = clean_res.json()
        assert data["success"] is True
        assert "cleared_counts" in data

        # Verify claims table is completely empty
        list_res = await client.get("/api/v1/claims")
        assert list_res.json()["total"] == 0
        assert len(list_res.json()["items"]) == 0


def test_detailed_stage_timing_telemetry_recorder():
    """Verify high-resolution stage execution timing recorder logic on BaseCourtScraper."""
    class DummyScraper(BaseCourtScraper):
        async def search_by_party_name(self, first_name, last_name, page, **kwargs):
            return []

    scraper = DummyScraper(county_name="TestCounty", base_url="https://test.court.gov")
    t1 = datetime(2026, 9, 3, 10, 15, 20, 120000)
    t2 = datetime(2026, 9, 3, 10, 15, 22, 840000)
    
    scraper.record_stage("browser_launch", "Browser Launch", t1, t2, detail="Attended Chrome + AntiCaptcha")
    
    assert "browser_launch" in scraper.stage_timings
    st = scraper.stage_timings["browser_launch"]
    assert st["name"] == "Browser Launch"
    assert st["duration_seconds"] == 2.72
    assert st["start_time"] == "10:15:20.120"
    assert st["end_time"] == "10:15:22.840"
    assert st["status"] == "SUCCESS"


def test_anticaptcha_extension_and_attended_configuration():
    """Verify Chrome extension path normalization and attended configuration flags."""
    class DummyScraper(BaseCourtScraper):
        async def search_by_party_name(self, first_name, last_name, page, **kwargs):
            return []

    ext_path = r"D:\UAIG\Bot Automation Project\anticaptcha-plugin_v0.83_1"
    scraper = DummyScraper(
        county_name="Miami-Dade",
        base_url="https://www2.miamidadeclerk.gov/ocs",
        extension_dir=ext_path,
        anticaptcha_api_key="28b486b8f31f74c6bf4453735815aa53",
        use_chrome=True,
    )
    assert scraper.extension_dir == ext_path
    assert scraper.anticaptcha_api_key == "28b486b8f31f74c6bf4453735815aa53"
    assert scraper.use_chrome is True


@pytest.mark.asyncio
async def test_file_preview_endpoint():
    """Verify POST /api/v1/ingest/preview returns record counts, file info, and schema mapping."""
    import io

    import pandas as pd
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    df = pd.DataFrame([
        {
            "Claim Number": "PREV-FL-001",
            "Insured First Name": "John",
            "Insured Last Name": "Doe",
            "DOL": "01/15/2024",
            "Policy State": "Florida",
            "Loss Location State": "Florida",
        },
        {
            "Claim Number": "PREV-TX-002",
            "Insured First Name": "Jane",
            "Insured Last Name": "Smith",
            "DOL": "02/20/2024",
            "Policy State": "Texas",
            "Loss Location State": "Texas",
        },
    ])

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ClaimsData")
    excel_content = excel_buffer.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("test_claims.xlsx", excel_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        res = await client.post("/api/v1/ingest/preview", files=files)
        assert res.status_code == 200
        data = res.json()

        assert data["filename"] == "test_claims.xlsx"
        assert data["total_records"] == 2
        assert data["valid_records"] == 2
        assert data["invalid_records"] == 0
        assert "ClaimsData" in data["sheet_names"]
        assert "Claim Number" in data["detected_columns"]
        assert data["florida_claims_count"] == 1
        assert data["texas_claims_count"] == 1
        assert len(data["preview_records"]) == 2
        assert data["preview_records"][0]["claim_number"] == "PREV-FL-001"
        assert data["preview_records"][1]["claim_number"] == "PREV-TX-002"
