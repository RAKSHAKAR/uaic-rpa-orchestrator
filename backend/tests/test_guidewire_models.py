"""Unit tests for Guidewire integration, fuzzy filtering, and automation settings persistence models."""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.core.database import TaskAsyncSessionLocal, init_db
from app.models import (
    AutomationSetting,
    Claim,
    ClaimRecord,
    FilteredOutCase,
    GuidewireActivity,
    RecordStatusEnum,
    SettingsAuditLog,
)


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure database schema is created and initialized."""
    await init_db()
    yield


@pytest.mark.asyncio
async def test_claim_alias_identity():
    """Verify Claim is an alias for ClaimRecord."""
    assert Claim is ClaimRecord
    c = Claim(claim_number="CLM-TEST-001")
    assert isinstance(c, ClaimRecord)


@pytest.mark.asyncio
async def test_guidewire_activity_lifecycle_and_relationship():
    """Verify GuidewireActivity model persistence, payload storage, and relationship with Claim."""
    claim_id = str(uuid.uuid4())
    trans_id = uuid.uuid4()
    activity_id = uuid.uuid4()

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="0123456789",
            insured_first_name="John",
            insured_last_name="Doe",
            record_status=RecordStatusEnum.COMPLETED,
        )
        session.add(claim)

        activity = GuidewireActivity(
            id=activity_id,
            claim_id=claim_id,
            transaction_id=trans_id,
            claim_number="0123456789",
            exposure_number="001",
            request_payload={
                "ClaimNumber": "0123456789",
                "ExposureNumber": "001",
                "CaseItems": [{"CaseNumber": "2024-CA-001", "CaseStyle": "DOE VS SMITH"}],
            },
            response_payload={"activityId": "ACT-8472910", "status": "Success"},
            http_status=200,
            status="SUCCESS",
            guidewire_claim_id="gw_claim_991",
            guidewire_activity_id="ACT-8472910",
            error_details=None,
        )
        session.add(activity)
        await session.commit()

    # Query back with relationships
    async with TaskAsyncSessionLocal() as session:
        query = (
            select(ClaimRecord)
            .where(ClaimRecord.id == claim_id)
            .options(selectinload(ClaimRecord.guidewire_activities))
        )
        res = await session.execute(query)
        fetched_claim = res.scalar_one()

        assert len(fetched_claim.guidewire_activities) == 1
        act = fetched_claim.guidewire_activities[0]
        assert act.claim_number == "0123456789"
        assert act.http_status == 200
        assert act.status == "SUCCESS"
        assert act.guidewire_activity_id == "ACT-8472910"
        assert act.request_payload["ExposureNumber"] == "001"
        assert act.response_payload["activityId"] == "ACT-8472910"
        assert act.claim.id == claim_id

        # Clean up
        await session.delete(fetched_claim)
        await session.commit()


@pytest.mark.asyncio
async def test_guidewire_activity_transaction_id_unique_constraint():
    """Verify transaction_id is unique across GuidewireActivity records."""
    claim_id_1 = str(uuid.uuid4())
    claim_id_2 = str(uuid.uuid4())
    shared_trans_id = uuid.uuid4()

    async with TaskAsyncSessionLocal() as session:
        c1 = ClaimRecord(id=claim_id_1, claim_number="CLM-UNIQ-1")
        c2 = ClaimRecord(id=claim_id_2, claim_number="CLM-UNIQ-2")
        session.add_all([c1, c2])

        act1 = GuidewireActivity(
            claim_id=claim_id_1,
            transaction_id=shared_trans_id,
            claim_number="CLM-UNIQ-1",
            request_payload={"test": 1},
        )
        session.add(act1)
        await session.commit()

        # Duplicate transaction_id should violate unique constraint
        act2 = GuidewireActivity(
            claim_id=claim_id_2,
            transaction_id=shared_trans_id,
            claim_number="CLM-UNIQ-2",
            request_payload={"test": 2},
        )
        session.add(act2)
        with pytest.raises(IntegrityError):
            await session.commit()

        await session.rollback()

    # Clean up
    async with TaskAsyncSessionLocal() as session:
        rec1 = await session.get(ClaimRecord, claim_id_1)
        rec2 = await session.get(ClaimRecord, claim_id_2)
        if rec1:
            await session.delete(rec1)
        if rec2:
            await session.delete(rec2)
        await session.commit()


@pytest.mark.asyncio
async def test_filtered_out_case_lifecycle_and_relationship():
    """Verify FilteredOutCase records cases matched by fuzzy logic but excluded prior to Guidewire."""
    claim_id = str(uuid.uuid4())
    case_id = uuid.uuid4()

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="CLM-FILTER-001",
            insured_first_name="Jane",
            insured_last_name="Smith",
        )
        session.add(claim)

        filtered_case = FilteredOutCase(
            id=case_id,
            claim_id=claim_id,
            case_number="2024-CC-998811",
            case_style="JANE SMITH VS ROBERT ROE",
            case_type="TRAFFIC INFRACTION",
            case_status="CLOSED",
            filing_date=datetime(2024, 3, 15, tzinfo=UTC),
            fuzzy_score=0.85,
            exclusion_reasons={
                "case_type_whitelisted": False,
                "reason": "Traffic infraction excluded from civil claims push",
            },
        )
        session.add(filtered_case)
        await session.commit()

    # Query back with relationship
    async with TaskAsyncSessionLocal() as session:
        query = (
            select(ClaimRecord)
            .where(ClaimRecord.id == claim_id)
            .options(selectinload(ClaimRecord.filtered_cases))
        )
        res = await session.execute(query)
        fetched_claim = res.scalar_one()

        assert len(fetched_claim.filtered_cases) == 1
        fc = fetched_claim.filtered_cases[0]
        assert fc.case_number == "2024-CC-998811"
        assert fc.fuzzy_score == 0.85
        assert fc.case_type == "TRAFFIC INFRACTION"
        assert fc.exclusion_reasons["case_type_whitelisted"] is False
        assert fc.claim.id == claim_id

        # Clean up
        await session.delete(fetched_claim)
        await session.commit()


@pytest.mark.asyncio
async def test_claim_cascade_deletes_guidewire_and_filtered_records():
    """Verify deleting a Claim cascade-deletes its GuidewireActivity and FilteredOutCase children."""
    claim_id = str(uuid.uuid4())
    act_id = uuid.uuid4()
    fcase_id = uuid.uuid4()

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(id=claim_id, claim_number="CLM-CASCADE-TEST")
        session.add(claim)

        act = GuidewireActivity(
            id=act_id,
            claim_id=claim_id,
            transaction_id=uuid.uuid4(),
            claim_number="CLM-CASCADE-TEST",
            request_payload={"test": "data"},
        )
        fc = FilteredOutCase(
            id=fcase_id,
            claim_id=claim_id,
            case_number="2024-CC-001",
            case_style="CASCADE TEST",
            fuzzy_score=0.75,
            exclusion_reasons={"rule": "cascade_test"},
        )
        session.add_all([act, fc])
        await session.commit()

    # Delete parent claim
    async with TaskAsyncSessionLocal() as session:
        c = await session.get(ClaimRecord, claim_id)
        assert c is not None
        await session.delete(c)
        await session.commit()

    # Verify children are cascade-deleted
    async with TaskAsyncSessionLocal() as session:
        assert await session.get(ClaimRecord, claim_id) is None
        assert await session.get(GuidewireActivity, act_id) is None
        assert await session.get(FilteredOutCase, fcase_id) is None


@pytest.mark.asyncio
async def test_automation_settings_and_audit_log():
    """Verify AutomationSetting and SettingsAuditLog lifecycle and audit relationships."""
    setting_key = "matcher.auto_threshold"
    log_id = uuid.uuid4()

    async with TaskAsyncSessionLocal() as session:
        # Clean existing if present
        existing = await session.get(AutomationSetting, setting_key)
        if existing:
            await session.delete(existing)
            await session.commit()

        setting = AutomationSetting(
            key=setting_key,
            value={"threshold": 0.65, "algorithm": "token_sort_ratio"},
            category="matcher",
        )
        session.add(setting)

        audit = SettingsAuditLog(
            id=log_id,
            key=setting_key,
            old_value={"threshold": 0.60},
            new_value={"threshold": 0.65, "algorithm": "token_sort_ratio"},
            updated_by="admin@uaic.com",
        )
        session.add(audit)
        await session.commit()

    # Query back
    async with TaskAsyncSessionLocal() as session:
        query = (
            select(AutomationSetting)
            .where(AutomationSetting.key == setting_key)
            .options(selectinload(AutomationSetting.audit_logs))
        )
        res = await session.execute(query)
        fetched_setting = res.scalar_one()

        assert fetched_setting.key == setting_key
        assert fetched_setting.category == "matcher"
        assert fetched_setting.value["threshold"] == 0.65
        assert len(fetched_setting.audit_logs) == 1

        audit_entry = fetched_setting.audit_logs[0]
        assert audit_entry.old_value == {"threshold": 0.60}
        assert audit_entry.new_value["threshold"] == 0.65
        assert audit_entry.updated_by == "admin@uaic.com"
        assert audit_entry.setting.key == setting_key

        # Cascade delete setting
        await session.delete(fetched_setting)
        await session.commit()

    # Verify audit log was cascade deleted
    async with TaskAsyncSessionLocal() as session:
        assert await session.get(AutomationSetting, setting_key) is None
        assert await session.get(SettingsAuditLog, log_id) is None
