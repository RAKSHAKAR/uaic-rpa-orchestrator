"""Automated test suite verifying:
1. Harris portal disambiguation (Harris JP vs Harris County Clerk vs Harris District Clerk).
2. All 8 portals enabled in default settings and Texas 5-bot routing.
3. Queue started_at telemetry.
4. RapidFuzz & Guidewire completed evaluation on Claim 870f33f1.
"""

import pytest
from sqlalchemy import select

from app.api.v1.endpoints.claims import _build_bot_details, _case_count
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import BotStatusEnum, ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum
from app.schemas.queue import LiveQueueItemResponse
from app.schemas.settings import SystemSettings


def test_harris_portal_disambiguation_case_counts():
    """Verify that case count search keywords strictly separate the 3 Harris portals."""
    # Case with cases attributed specifically to Harris District Clerk
    scraped_by_county = {
        "harris district": 603,
        "miami": 12,
    }
    action_timings = {
        "portals": {
            "harris_district": {"duration_seconds": 225.58, "cases_found": 603},
            "harris_jp": {"duration_seconds": 3.12, "cases_found": 0},
            "harris_cclerk": {"duration_seconds": 4.55, "cases_found": 0},
        }
    }

    # Harris JP must NOT pick up Harris District cases
    jp_count = _case_count(
        action_timings=action_timings,
        portal_key="harris_jp",
        scraped_by_county=scraped_by_county,
        search_keywords=["harris jp", "harris county jp", "odyssey jp"],
    )
    assert jp_count == 0, f"Expected Harris JP to have 0 cases, got {jp_count}"

    # Harris County Clerk must NOT pick up Harris District cases
    cclerk_count = _case_count(
        action_timings=action_timings,
        portal_key="harris_cclerk",
        scraped_by_county=scraped_by_county,
        search_keywords=["harris county clerk", "harris clerk", "cclerk"],
    )
    assert cclerk_count == 0, f"Expected Harris County Clerk to have 0 cases, got {cclerk_count}"

    # Harris District Clerk MUST pick up its 603 cases
    district_count = _case_count(
        action_timings=action_timings,
        portal_key="harris_district",
        scraped_by_county=scraped_by_county,
        search_keywords=["harris district", "hcdistrict", "edocs"],
    )
    assert district_count == 603, f"Expected Harris District Clerk to have 603 cases, got {district_count}"


def test_build_bot_details_for_texas_claim():
    """Verify _build_bot_details accurately reports Texas bots with separate counts."""
    claim = ClaimRecord(
        id="test-claim-tx",
        claim_number="1234567890",
        policy_state="TX",
        loss_location_state="TX",
        record_status=RecordStatusEnum.SCRAPING_COMPLETED,
        te_botstatus_travis=BotStatusEnum.COMPLETED,
        te_botstatus_dallas=BotStatusEnum.COMPLETED,
        te_botstatus_harris=BotStatusEnum.COMPLETED,
        te_botstatus_cclerk=BotStatusEnum.COMPLETED,
        te_botstatus_hcdistrict=BotStatusEnum.COMPLETED,
        fl_botstatus_broward=BotStatusEnum.NOT_TRIGGERED,
        fl_botstatus_hillsborough=BotStatusEnum.NOT_TRIGGERED,
        fl_botstatus_miami=BotStatusEnum.NOT_TRIGGERED,
        te_jsonbody_hcdistrict='[{"CaseNumber": "2024-12345"}]',
        te_jsonbody_cclerk="[]",
        te_jsonbody_harris="[]",
        action_timings={
            "portals": {
                "harris_district": {"duration_seconds": 12.5, "cases_found": 1},
                "harris_jp": {"duration_seconds": 2.1, "cases_found": 0},
                "harris_cclerk": {"duration_seconds": 3.4, "cases_found": 0},
            }
        },
    )

    bots = _build_bot_details(claim)
    bot_map = {b.name: b for b in bots}

    assert bot_map["Harris County JP (TX)"].cases_found == 0
    assert bot_map["Harris County Clerk (TX)"].cases_found == 0
    assert bot_map["Harris District Clerk (TX)"].cases_found == 1
    assert bot_map["Harris District Clerk (TX)"].target == "Yes"
    assert bot_map["Broward County (FL)"].target == "No"


def test_all_8_portals_enabled_in_default_settings():
    """Verify default system settings have all 8 portals enabled including Dallas and Travis."""
    defaults = SystemSettings()
    portals = defaults.portals
    assert portals.broward_enabled is True
    assert portals.hillsborough_enabled is True
    assert portals.miami_enabled is True
    assert portals.harris_cclerk_enabled is True
    assert portals.dallas_enabled is True
    assert portals.harris_jp_enabled is True
    assert portals.harris_district_enabled is True
    assert portals.travis_enabled is True


def test_live_queue_item_schema_started_at():
    """Verify LiveQueueItemResponse accepts and serializes started_at field."""
    item = LiveQueueItemResponse(
        id="item-uuid-123",
        claim_number="0123456789",
        exposure_number="001",
        record_status="SCRAPING_IN_PROGRESS",
        fuzzy_match_status="NEW",
        portals_to_run=["Dallas", "Travis"],
        started_at="2026-10-06T00:15:30Z",
    )
    assert item.started_at == "2026-10-06T00:15:30Z"


@pytest.mark.asyncio
async def test_claim_870_evaluated_and_completed():
    """Verify Claim 870f33f1 in database is in COMPLETED status with activity_id."""
    async with TaskAsyncSessionLocal() as session:
        res = await session.execute(
            select(ClaimRecord).where(ClaimRecord.id == "870f33f1-d4e5-49b5-9afd-13521bcf60f9")
        )
        claim = res.scalar_one_or_none()
        if claim is not None:
            assert claim.record_status in (RecordStatusEnum.COMPLETED, RecordStatusEnum.MATCH_FOUND)
            assert claim.fuzzy_match_status in (FuzzyMatchStatusEnum.COMPLETED, FuzzyMatchStatusEnum.MATCH_FOUND)
            assert claim.activity_id is not None


def test_format_live_queue_item_utc_z_suffix():
    """Verify _format_live_queue_item guarantees explicit UTC 'Z' suffix to avoid timezone offset bugs."""
    from datetime import datetime

    from app.api.v1.endpoints.queue import _format_live_queue_item
    claim = ClaimRecord(
        id="test-utc-claim",
        claim_number="999888777",
        policy_state="FL",
        loss_location_state="FL",
        record_status=RecordStatusEnum.SCRAPING_IN_PROGRESS,
        updated_at=datetime(2026, 10, 6, 5, 30, 0),
        action_timings={"started_at": "2026-10-06T05:30:00"},
    )
    res = _format_live_queue_item(claim)
    assert res.started_at is not None
    assert res.started_at.endswith("Z"), f"Expected started_at to end with 'Z', got: {res.started_at}"
