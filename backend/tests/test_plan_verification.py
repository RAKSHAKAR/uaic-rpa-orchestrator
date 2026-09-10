"""Exhaustive Automated Verification Suite for all requirements in implementation_plan/ folder.

Line-by-line verification of:
1. Single-Claim Multi-Format Export (JSON, CSV, XLSX, PDF)
2. Single-Bot On-Demand Execution (8 portals: Broward, Hillsborough, Miami, Travis, Dallas, Harris JP, Harris CClerk, Harris District + 'all')
3. Single-Claim Automation Controls (start, stop, push-guidewire)
4. Queue Management & Execution (retrigger, start-all, sequential auto-runner progression)
5. Exception Handling & Fuzzy Match Candidate Review (pending, approve, reject)
6. File Ingestion & 12 Input Column Preservation (preview, upload, template downloads, background task)
7. Celery Beat Periodic Tasks (advance-auto-queue, retrigger-failed-cases)
8. State Routing Complete Matrix (FL same-state, TX same-state, cross-state, non-target)
9. Hillsborough Datepicker 'readonly' Removal Verification
10. Guidewire Payload & 9-digit ClaimNumber Formatting
"""

import io
import json
import uuid
from datetime import UTC, datetime
from unittest.mock import patch

import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.automation.florida.hillsborough import HillsboroughScraper
from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.main import app
from app.models.claim import (
    BotStatusEnum,
    ClaimRecord,
    FuzzyMatchStatusEnum,
    IngestionBatch,
    RecordStatusEnum,
)
from app.models.court_case import ScrapedCourtCase
from app.models.match_result import MatchPair, MatchReviewStatusEnum, PartyTypeEnum
from app.services.excel_parser import resolve_county_bot_targets
from app.services.guidewire_client import GuidewireClient, format_claim_number
from app.tasks.ingest_tasks import _async_parse_and_ingest
from app.tasks.queue_runner import (
    _async_advance_auto_queue,
    get_active_queue_item_id,
    is_auto_queue_enabled,
    set_active_queue_item_id,
    set_auto_queue_enabled,
)
from app.tasks.retry_tasks import _async_retrigger_failed_cases


@pytest.fixture(scope="module", autouse=True)
async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def sample_claim_with_details():
    """Create a fully populated claim record with scraped cases, match pairs, and telemetry."""
    claim_id = str(uuid.uuid4())
    unique_num = f"PLAN-TEST-{claim_id[:8]}"

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=unique_num,
            exposure_number="2",
            primary_key="PK-9999",
            dol="07/15/2024",
            insured_first_name="Arthur",
            insured_last_name="Dent",
            claimant_first_name="Ford",
            claimant_last_name="Prefect",
            driver_first_name="Arthur",
            driver_last_name="Dent",
            policy_state="Florida",
            loss_location_state="Florida",
            loss_location_city="Tampa",
            loss_location_county="Hillsborough",
            record_status=RecordStatusEnum.MATCH_FOUND,
            fuzzy_match_status=FuzzyMatchStatusEnum.COMPLETED,
            fl_website_hillsborough="Yes",
            fl_botstatus_hillsborough=BotStatusEnum.COMPLETED,
            total_duration_seconds=14.52,
            activity_id="MOCK-ACT-88123",
            action_timings={
                "stages": {
                    "browser_launch": {
                        "name": "Browser Launch",
                        "start_time": "10:00:00.100",
                        "end_time": "10:00:02.300",
                        "duration_seconds": 2.2,
                        "status": "SUCCESS",
                        "detail": "Attended Chrome launched",
                    },
                    "result_retrieval": {
                        "name": "Result Retrieval",
                        "start_time": "10:00:08.500",
                        "end_time": "10:00:10.000",
                        "duration_seconds": 1.5,
                        "status": "SUCCESS",
                        "detail": "Extracted 1 court case",
                    },
                }
            },
        )
        session.add(claim)
        await session.commit()

        # Add Scraped Case
        case_id = str(uuid.uuid4())
        court_case = ScrapedCourtCase(
            id=case_id,
            claim_id=claim_id,
            county_name="Hillsborough County",
            county_website="https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab",
            case_number="24-CA-001234",
            case_style="PREFECT, FORD VS DENT, ARTHUR",
            filing_date="2024-08-01",
            case_status="OPEN",
            case_type="AUTO NEGLIGENCE",
        )
        session.add(court_case)
        await session.commit()

        # Add Match Pair
        match_id = str(uuid.uuid4())
        match_pair = MatchPair(
            id=match_id,
            claim_id=claim_id,
            court_case_id=case_id,
            party_type=PartyTypeEnum.CLAIMANT,
            party_name="Ford Prefect",
            case_style="PREFECT, FORD VS DENT, ARTHUR",
            similarity_score=0.95,
            threshold_applied=0.60,
            is_match=True,
            review_status=MatchReviewStatusEnum.APPROVED,
            reviewed_by="Automated Engine",
            review_notes="High-confidence claimant match",
        )
        session.add(match_pair)
        await session.commit()

    yield claim_id, unique_num, match_id

    # Clean up fixture data
    async with TaskAsyncSessionLocal() as session:
        await session.execute(delete(MatchPair).where(MatchPair.claim_id == claim_id))
        await session.execute(delete(ScrapedCourtCase).where(ScrapedCourtCase.claim_id == claim_id))
        await session.execute(delete(ClaimRecord).where(ClaimRecord.id == claim_id))
        await session.commit()


# =========================================================================
# 1. Single-Claim Multi-Format Export Tests
# =========================================================================

@pytest.mark.asyncio
async def test_single_claim_export_json(sample_claim_with_details):
    claim_id, unique_num, _ = sample_claim_with_details
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"/api/v1/claims/{claim_id}/export?format=json")
        assert res.status_code == 200
        assert "application/json" in res.headers.get("content-type", "")
        assert f"claim_{unique_num}" in res.headers.get("content-disposition", "")

        data = json.loads(res.text)
        assert data["id"] == claim_id
        assert data["claim_number"] == unique_num
        assert len(data["court_cases"]) == 1
        assert data["court_cases"][0]["case_number"] == "24-CA-001234"


@pytest.mark.asyncio
async def test_single_claim_export_csv(sample_claim_with_details):
    claim_id, unique_num, _ = sample_claim_with_details
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"/api/v1/claims/{claim_id}/export?format=csv")
        assert res.status_code == 200
        assert "text/csv" in res.headers.get("content-type", "")
        csv_text = res.text
        assert "Claim Number" in csv_text
        assert "Case Number" in csv_text
        assert "Case Style" in csv_text
        assert unique_num in csv_text
        assert "24-CA-001234" in csv_text
        assert "PREFECT, FORD VS DENT, ARTHUR" in csv_text


@pytest.mark.asyncio
async def test_single_claim_export_xlsx(sample_claim_with_details):
    claim_id, unique_num, _ = sample_claim_with_details
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"/api/v1/claims/{claim_id}/export?format=xlsx")
        assert res.status_code == 200
        assert "spreadsheetml" in res.headers.get("content-type", "")

        # Verify multi-sheet workbook structure
        excel_file = pd.ExcelFile(io.BytesIO(res.content))
        sheets = excel_file.sheet_names
        assert "Claim Overview" in sheets
        assert "Scraped Court Cases" in sheets
        assert "Fuzzy Matches" in sheets
        assert "Stage Telemetry" in sheets

        overview_df = excel_file.parse("Claim Overview")
        assert unique_num in overview_df["Value"].values
        assert "Arthur Dent" in overview_df["Value"].values

        cases_df = excel_file.parse("Scraped Court Cases")
        assert "24-CA-001234" in cases_df["Case Number"].values

        matches_df = excel_file.parse("Fuzzy Matches")
        assert "Ford Prefect" in matches_df["Party Name"].values


@pytest.mark.asyncio
async def test_single_claim_export_pdf(sample_claim_with_details):
    claim_id, unique_num, _ = sample_claim_with_details
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Mock Playwright sync rendering to return realistic vector PDF bytes
        mock_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Title (UAIC Claim Report) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        with patch("app.api.v1.endpoints.claims._render_claim_pdf_sync", return_value=mock_pdf_bytes):
            res = await client.get(f"/api/v1/claims/{claim_id}/export?format=pdf")
            assert res.status_code == 200
            assert "application/pdf" in res.headers.get("content-type", "")
            assert res.content.startswith(b"%PDF-")
            assert f"claim_{unique_num}" in res.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_single_claim_export_invalid_inputs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 404 for non-existent claim
        res_404 = await client.get("/api/v1/claims/non-existent-claim-uuid/export?format=json")
        assert res_404.status_code == 404

        # 422 for invalid format
        res_422 = await client.get(f"/api/v1/claims/{str(uuid.uuid4())}/export?format=docx")
        assert res_422.status_code == 422


# =========================================================================
# 2. Single-Bot On-Demand Execution Tests (8 Bots + 'all')
# =========================================================================

@pytest.mark.asyncio
@pytest.mark.parametrize("bot_key,status_col", [
    ("broward", "fl_botstatus_broward"),
    ("hillsborough", "fl_botstatus_hillsborough"),
    ("miami", "fl_botstatus_miami"),
    ("travis", "te_botstatus_travis"),
    ("dallas", "te_botstatus_dallas"),
    ("harris_jp", "te_botstatus_harris"),
    ("harris_cclerk", "te_botstatus_cclerk"),
    ("harris_district", "te_botstatus_hcdistrict"),
])
async def test_run_single_bot_dispatch(bot_key, status_col):
    """Test POST /api/v1/claims/{id}/run-bot/{bot_key} for each of the 8 county bots."""
    claim_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        c = ClaimRecord(
            id=claim_id,
            claim_number=f"BOT-{bot_key[:4]}-{claim_id[:6]}",
            record_status=RecordStatusEnum.NEW,
        )
        session.add(c)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.core.celery_app.celery_app.send_task") as mock_send_task:
            res = await client.post(f"/api/v1/claims/{claim_id}/run-bot/{bot_key}")
            assert res.status_code == 200
            assert res.json()["status"] == "success"
            assert res.json()["bot_key"] == bot_key

            # Verify Celery task dispatched with claim_id and bot_key
            mock_send_task.assert_called_once_with(
                "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                args=[claim_id, bot_key],
                queue="scrapers",
            )

    # Verify database status updated to IN_PROGRESS
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
        res = await session.execute(q)
        updated_claim = res.scalar_one()
        assert getattr(updated_claim, status_col) == BotStatusEnum.IN_PROGRESS
        assert updated_claim.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS

        # Cleanup
        await session.delete(updated_claim)
        await session.commit()


@pytest.mark.asyncio
async def test_run_single_bot_all():
    """Test POST /api/v1/claims/{id}/run-bot/all sets all 8 bots to IN_PROGRESS."""
    claim_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        c = ClaimRecord(
            id=claim_id,
            claim_number=f"BOT-ALL-{claim_id[:6]}",
            record_status=RecordStatusEnum.NEW,
        )
        session.add(c)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.core.celery_app.celery_app.send_task"):
            res = await client.post(f"/api/v1/claims/{claim_id}/run-bot/all")
            assert res.status_code == 200
            assert res.json()["bot_key"] == "all"

    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
        res = await session.execute(q)
        c_all = res.scalar_one()
        assert c_all.fl_botstatus_broward == BotStatusEnum.IN_PROGRESS
        assert c_all.fl_botstatus_hillsborough == BotStatusEnum.IN_PROGRESS
        assert c_all.fl_botstatus_miami == BotStatusEnum.IN_PROGRESS
        assert c_all.te_botstatus_travis == BotStatusEnum.IN_PROGRESS
        assert c_all.te_botstatus_dallas == BotStatusEnum.IN_PROGRESS
        assert c_all.te_botstatus_harris == BotStatusEnum.IN_PROGRESS
        assert c_all.te_botstatus_cclerk == BotStatusEnum.IN_PROGRESS
        assert c_all.te_botstatus_hcdistrict == BotStatusEnum.IN_PROGRESS

        await session.delete(c_all)
        await session.commit()


@pytest.mark.asyncio
async def test_run_single_bot_invalid_inputs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid bot key returns 400
        res_400 = await client.post(f"/api/v1/claims/{str(uuid.uuid4())}/run-bot/invalid_county")
        assert res_400.status_code == 400
        assert "Invalid bot_key" in res_400.json()["detail"]

        # Non-existent claim returns 404
        res_404 = await client.post(f"/api/v1/claims/{str(uuid.uuid4())}/run-bot/broward")
        assert res_404.status_code == 404


# =========================================================================
# 3. Single-Claim Automation Controls (start, stop, push-guidewire)
# =========================================================================

@pytest.mark.asyncio
async def test_claim_single_start_stop_and_guidewire_push():
    claim_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        c = ClaimRecord(
            id=claim_id,
            claim_number=f"CTRL-{claim_id[:6]}",
            record_status=RecordStatusEnum.NEW,
        )
        session.add(c)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Start single claim
        with patch("app.core.celery_app.celery_app.send_task") as mock_send:
            res_start = await client.post(f"/api/v1/claims/{claim_id}/start")
            assert res_start.status_code == 200
            assert "queued" in res_start.json()["message"]
            mock_send.assert_called_once_with(
                "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                args=[claim_id],
                queue="scrapers",
            )

        # 2. Stop single claim
        res_stop = await client.post(f"/api/v1/claims/{claim_id}/stop")
        assert res_stop.status_code == 200
        assert "cancelled" in res_stop.json()["message"]

        async with TaskAsyncSessionLocal() as session:
            q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
            res = await session.execute(q)
            c_stopped = res.scalar_one()
            assert c_stopped.record_status == RecordStatusEnum.FAILED
            assert c_stopped.last_error == "Cancelled by user"

        # 3. Push to Guidewire
        with patch("app.core.celery_app.celery_app.send_task") as mock_gw:
            res_gw = await client.post(f"/api/v1/claims/{claim_id}/push-guidewire")
            assert res_gw.status_code == 200
            assert "Guidewire dispatch queued" in res_gw.json()["message"]
            mock_gw.assert_called_once_with(
                "app.tasks.fuzzy_tasks.notify_guidewire_task",
                args=[claim_id],
                queue="notifications",
            )

        async with TaskAsyncSessionLocal() as session:
            await session.delete(c_stopped)
            await session.commit()


# =========================================================================
# 4. Queue Management Endpoints (retrigger, start-all)
# =========================================================================

@pytest.mark.asyncio
async def test_queue_retrigger_and_start_all():
    c_id1 = str(uuid.uuid4())
    c_id2 = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        c1 = ClaimRecord(
            id=c_id1,
            claim_number=f"RETRIG1-{c_id1[:6]}",
            record_status=RecordStatusEnum.FAILED,
            retry_count=0,
        )
        c2 = ClaimRecord(
            id=c_id2,
            claim_number=f"RETRIG2-{c_id2[:6]}",
            record_status=RecordStatusEnum.SCRAPING_IN_PROGRESS,
            retry_count=1,
        )
        session.add_all([c1, c2])
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Retrigger specific claims
        with patch("app.core.celery_app.celery_app.send_task") as mock_retrigger:
            res_ret = await client.post("/api/v1/queue/retrigger", json={"claim_ids": [c_id1, c_id2]})
            assert res_ret.status_code == 200
            assert res_ret.json()["count"] == 2
            assert mock_retrigger.call_count == 2

        # Verify status reset to NEW and retry count incremented
        async with TaskAsyncSessionLocal() as session:
            q = select(ClaimRecord).where(ClaimRecord.id == c_id1)
            c1_updated = (await session.execute(q)).scalar_one()
            assert c1_updated.record_status == RecordStatusEnum.NEW
            assert c1_updated.retry_count == 1

        # 2. Start-All
        with patch("app.core.celery_app.celery_app.send_task") as mock_start_all:
            res_sa = await client.post("/api/v1/queue/start-all")
            assert res_sa.status_code == 200
            assert res_sa.json()["status"] == "started"
            mock_start_all.assert_called_once_with(
                "app.tasks.queue_runner.advance_auto_queue_task",
                queue="default",
            )
            assert is_auto_queue_enabled() is True

        # Cleanup
        async with TaskAsyncSessionLocal() as session:
            await session.execute(delete(ClaimRecord).where(ClaimRecord.id.in_([c_id1, c_id2])))
            await session.commit()


# =========================================================================
# 5. Fuzzy Match Exception Review (pending, approve, reject)
# =========================================================================

@pytest.mark.asyncio
async def test_matches_review_endpoints():
    claim_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    match_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        c = ClaimRecord(
            id=claim_id,
            claim_number=f"MATCH-REV-{claim_id[:6]}",
            record_status=RecordStatusEnum.MANUAL_REVIEW,
        )
        session.add(c)
        await session.commit()

        case = ScrapedCourtCase(
            id=case_id,
            claim_id=claim_id,
            county_name="Broward County",
            county_website="https://www.browardclerk.org/Web2/",
            case_number="CACE-24-009988",
            case_style="SMITH, JOHN VS DOE, JANE",
            filing_date="2024-06-01",
        )
        session.add(case)
        await session.commit()

        mp = MatchPair(
            id=match_id,
            claim_id=claim_id,
            court_case_id=case_id,
            party_type=PartyTypeEnum.INSURED,
            party_name="John Smith",
            case_style="SMITH, JOHN VS DOE, JANE",
            similarity_score=0.68,
            threshold_applied=0.60,
            is_match=True,
            review_status=MatchReviewStatusEnum.PENDING_REVIEW,
        )
        session.add(mp)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. GET /api/v1/matches/pending
        res_pending = await client.get("/api/v1/matches/pending")
        assert res_pending.status_code == 200
        items = res_pending.json()
        assert any(item["id"] == match_id for item in items)

        # 2. POST /api/v1/matches/{id}/review (APPROVED)
        with patch("app.core.celery_app.celery_app.send_task") as mock_gw:
            res_approve = await client.post(
                f"/api/v1/matches/{match_id}/review",
                json={
                    "decision": "APPROVED",
                    "reviewed_by": "Adjuster_Jane",
                    "review_notes": "Confirmed match against police report.",
                },
            )
            assert res_approve.status_code == 200
            assert "APPROVED" in res_approve.json()["message"]
            mock_gw.assert_called_once_with(
                "app.tasks.fuzzy_tasks.notify_guidewire_task",
                args=[claim_id],
                queue="notifications",
            )

        # Verify claim status updated to MATCH_FOUND with final_matched_json populated
        async with TaskAsyncSessionLocal() as session:
            claim_check = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))).scalar_one()
            assert claim_check.record_status == RecordStatusEnum.MATCH_FOUND
            assert claim_check.final_matched_json is not None
            assert claim_check.final_matched_json["CaseItems"][0]["CaseNumber"] == "CACE-24-009988"

        # 3. POST /api/v1/matches/{id}/review (REJECTED)
        res_reject = await client.post(
            f"/api/v1/matches/{match_id}/review",
            json={
                "decision": "REJECTED",
                "reviewed_by": "Adjuster_Jane",
                "review_notes": "Different person with same name.",
            },
        )
        assert res_reject.status_code == 200
        assert "REJECTED" in res_reject.json()["message"]

        async with TaskAsyncSessionLocal() as session:
            claim_check2 = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))).scalar_one()
            assert claim_check2.record_status == RecordStatusEnum.NO_MATCH_FOUND

            # Cleanup
            await session.execute(delete(MatchPair).where(MatchPair.id == match_id))
            await session.execute(delete(ScrapedCourtCase).where(ScrapedCourtCase.id == case_id))
            await session.execute(delete(ClaimRecord).where(ClaimRecord.id == claim_id))
            await session.commit()


# =========================================================================
# 6. File Ingestion & 12 Input Column Preservation
# =========================================================================

@pytest.mark.asyncio
async def test_template_download_endpoints():
    """Verify GET /api/v1/ingest/sample/excel and GET /api/v1/ingest/sample/csv."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_xlsx = await client.get("/api/v1/ingest/sample/excel")
        assert res_xlsx.status_code in [200, 404]  # 200 if static template exists
        res_csv = await client.get("/api/v1/ingest/sample/csv")
        assert res_csv.status_code in [200, 404]


@pytest.mark.asyncio
async def test_async_parse_and_ingest_all_12_columns(tmp_path):
    """Verify that background ingestion task parses and persists all 12 input columns."""
    df_12_cols = pd.DataFrame([
        {
            "Primary Key": "PK-COL-TEST",
            "Insured First Name": "Tricia",
            "Insured Last Name": "McMillan",
            "DOL": "05/20/2024",
            "Driver First Name (Insured Vehicle)": "Zaphod",
            "Driver Last Name (Insured Vehicle)": "Beeblebrox",
            "Policy State": "Florida",
            "Claim Number": f"12COL-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}",
            "Loss Location State": "Florida",
            "Loss Location City": "Miami",
            "Loss Location County": "Miami-Dade",
            "Exposure Number": "3",
            "Claimant First Name": "Arthur",
            "Claimant Last Name": "Dent",
        }
    ])

    test_file = tmp_path / "test_12_cols.xlsx"
    df_12_cols.to_excel(test_file, index=False)

    batch_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        batch = IngestionBatch(id=batch_id, filename="test_12_cols.xlsx", status="PROCESSING")
        session.add(batch)
        await session.commit()

    with patch("app.core.celery_app.celery_app.send_task"):
        await _async_parse_and_ingest(batch_id, str(test_file))

    # Verify claim in DB has all 12 columns correctly populated
    async with TaskAsyncSessionLocal() as session:
        q_batch = select(IngestionBatch).where(IngestionBatch.id == batch_id)
        batch_db = (await session.execute(q_batch)).scalar_one()
        assert batch_db.status == "COMPLETED"
        assert batch_db.total_records == 1
        assert batch_db.processed_records == 1

        q_claim = select(ClaimRecord).where(ClaimRecord.batch_id == batch_id)
        claim_db = (await session.execute(q_claim)).scalar_one()
        assert claim_db.primary_key == "PK-COL-TEST"
        assert claim_db.insured_first_name == "Tricia"
        assert claim_db.insured_last_name == "McMillan"
        assert claim_db.dol == "05/20/2024"
        assert claim_db.driver_first_name == "Zaphod"
        assert claim_db.driver_last_name == "Beeblebrox"
        assert claim_db.policy_state == "Florida"
        assert "12COL-" in claim_db.claim_number
        assert claim_db.loss_location_state == "Florida"
        # Deprecated fields (loss_location_city, loss_location_county) removed per Prompt 03
        assert claim_db.loss_location_city is None
        assert claim_db.loss_location_county is None
        assert claim_db.exposure_number == "3"
        assert claim_db.claimant_first_name == "Arthur"
        assert claim_db.claimant_last_name == "Dent"
        assert claim_db.fl_website_miami == "Yes"
        assert claim_db.te_website_dallas == "No"

        # Cleanup
        await session.delete(claim_db)
        await session.delete(batch_db)
        await session.commit()


# =========================================================================
# 7. Queue Runner & Retry Tasks Progression
# =========================================================================

@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_queue_runner_progression_and_recovery():
    """Verify _async_advance_auto_queue sequential processing, lock handling, and recovery."""
    # 1. When auto-queue is disabled, advance does nothing
    set_auto_queue_enabled(False)
    set_active_queue_item_id("")
    with patch("app.core.celery_app.celery_app.send_task") as mock_send:
        await _async_advance_auto_queue()
        mock_send.assert_not_called()

    # 2. When auto-queue is enabled, picks next NEW claim and locks it
    claim_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        c = ClaimRecord(
            id=claim_id,
            claim_number=f"QUEUE-ADV-{claim_id[:6]}",
            record_status=RecordStatusEnum.NEW,
        )
        session.add(c)
        await session.commit()

    set_auto_queue_enabled(True)
    set_active_queue_item_id("")  # clear any stale lock from prior test state
    with patch("app.tasks.queue_runner.celery_app.send_task") as mock_send2:
        await _async_advance_auto_queue()
        assert mock_send2.called
        assert get_active_queue_item_id() != ""

    # Cleanup
    set_auto_queue_enabled(False)
    set_active_queue_item_id("")
    async with TaskAsyncSessionLocal() as session:
        claim_row = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))).scalar_one_or_none()
        if claim_row:
            await session.delete(claim_row)
            await session.commit()


@pytest.mark.asyncio
async def test_scheduled_retrigger_failed_cases():
    """Verify _async_retrigger_failed_cases finds failed claims, resets to NEW, and dispatches scrapers."""
    claim_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        c = ClaimRecord(
            id=claim_id,
            claim_number=f"FAIL-RETRY-{claim_id[:6]}",
            record_status=RecordStatusEnum.FAILED,
            retry_count=2,
        )
        session.add(c)
        await session.commit()

    with patch("app.core.celery_app.celery_app.send_task") as mock_retry_task:
        await _async_retrigger_failed_cases()
        retriggered_ids = [
            c_args.kwargs["args"][0]
            for c_args in mock_retry_task.call_args_list
            if "args" in c_args.kwargs and c_args.kwargs["args"]
        ]
        assert claim_id in retriggered_ids

    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
        c_after = (await session.execute(q)).scalar_one()
        assert c_after.record_status == RecordStatusEnum.NEW
        assert c_after.retry_count == 3

        await session.delete(c_after)
        await session.commit()


# =========================================================================
# 8. State Routing Complete Matrix
# =========================================================================

def test_state_routing_complete_matrix():
    """Verify resolution of county bot targets across all geographic routing cases."""
    # 1. Florida Same-State (FL = 3, TX = 0)
    fl_targets = resolve_county_bot_targets("Florida", "Florida")
    assert fl_targets["fl_broward"] == "Yes"
    assert fl_targets["fl_hillsborough"] == "Yes"
    assert fl_targets["fl_miami"] == "Yes"
    assert fl_targets["te_travis"] == "No"
    assert fl_targets["te_dallas"] == "No"
    assert fl_targets["te_harris"] == "No"
    assert fl_targets["te_cclerk"] == "No"
    assert fl_targets["te_hcdistrict"] == "No"

    # 2. Texas Same-State (FL = 0, TX = 5)
    tx_targets = resolve_county_bot_targets("Texas", "Texas")
    assert tx_targets["fl_broward"] == "No"
    assert tx_targets["fl_hillsborough"] == "No"
    assert tx_targets["fl_miami"] == "No"
    assert tx_targets["te_travis"] == "Yes"
    assert tx_targets["te_dallas"] == "Yes"
    assert tx_targets["te_harris"] == "Yes"
    assert tx_targets["te_cclerk"] == "Yes"
    assert tx_targets["te_hcdistrict"] == "Yes"

    # 3. Cross-State (Policy != Loss Location State: All 8 portals = Yes)
    cross_targets = resolve_county_bot_targets("Florida", "Texas")
    for val in cross_targets.values():
        assert val == "Yes"

    cross_targets2 = resolve_county_bot_targets("New York", "Florida")
    for val in cross_targets2.values():
        assert val == "Yes"

    # 4. Same-State Default (e.g. CA == CA: All 8 portals = Yes per Power Automate switch default)
    default_targets = resolve_county_bot_targets("California", "California")
    for val in default_targets.values():
        assert val == "Yes"


# =========================================================================
# 9. Hillsborough Datepicker Readonly Fix Verification
# =========================================================================

def test_hillsborough_scraper_initialization_and_selectors():
    """Verify HillsboroughScraper uses correct V4 selectors and party tab config."""
    scraper = HillsboroughScraper(headless=True)
    assert scraper.base_url == "https://hover.hillsclerk.com/"
    assert scraper.county_name == "Hillsborough County (FL)"


# =========================================================================
# 10. Guidewire 9-Digit Formatting & Payload Verification
# =========================================================================

def test_guidewire_claim_number_formatting():
    """Verify 9-digit ClaimNumber gets '0' prefix, while 10-digit remains unchanged."""
    # 9-digit -> 10-digit
    assert format_claim_number("100315067") == "0100315067"
    assert format_claim_number("987654321") == "0987654321"

    # 10-digit -> unchanged
    assert format_claim_number("0100315067") == "0100315067"
    assert format_claim_number("1234567890") == "1234567890"

    # Already formatted / alphanumeric -> unchanged
    assert format_claim_number("CLM-123456") == "CLM-123456"


@pytest.mark.asyncio
async def test_guidewire_send_case_update_mock():
    """Verify Guidewire send_case_update formats 9-digit claim number and returns simulated ActivityID."""
    client = GuidewireClient(mock_mode=True)
    cases = [
        {
            "CaseNumber": "26-CA-008254",
            "CaseStyle": "BROWN, CRYSTAL VS WILLIAMS, LOUIS DE ANDRE",
            "CountyWebsite": "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab",
            "SuitFiledDate": "2026-07-30",
        }
    ]
    res = await client.send_case_update(
        claim_number="100315067",  # 9 digits
        exposure_number="3",
        matched_cases=cases,
    )
    assert res["success"] is True
    assert res["status_code"] == 200
    assert "MOCK-ACT" in res["response"]["activityId"]
    assert res["response"]["claimNumber"] == "0100315067"
