"""Enhanced Guidewire payload contract tests (TC-GW-001 through TC-GW-006)."""

import uuid

import pytest

from app.services.guidewire_client import GuidewireClient, format_claim_number


@pytest.mark.asyncio
async def test_tc_gw_001_transaction_id_uuid4():
    """TC-GW-001: Payload includes TransactionId as valid UUIDv4."""
    client = GuidewireClient(mock_mode=True)
    res = await client.send_case_update(
        claim_number="0123456789",
        exposure_number="1",
        matched_cases=[{"CaseNumber": "C1", "CaseStyle": "S1"}],
    )
    payload = res["payload_sent"]
    assert "TransactionId" in payload
    # Validate UUID format
    parsed = uuid.UUID(payload["TransactionId"])
    assert parsed.version == 4


@pytest.mark.asyncio
async def test_tc_gw_002_source_system():
    """TC-GW-002: Payload includes SourceSystem = UAIC_ORCHESTRATOR."""
    client = GuidewireClient(mock_mode=True)
    res = await client.send_case_update(
        claim_number="0123456789",
        exposure_number="1",
        matched_cases=[{"CaseNumber": "C1", "CaseStyle": "S1"}],
    )
    payload = res["payload_sent"]
    assert payload.get("SourceSystem") == "UAIC_ORCHESTRATOR"


@pytest.mark.asyncio
async def test_tc_gw_003_case_type_not_in_case_items():
    """TC-GW-003: CaseItems do NOT contain CaseType field (strictly adhering to V4 contract)."""
    client = GuidewireClient(mock_mode=True)
    res = await client.send_case_update(
        claim_number="0123456789",
        exposure_number="1",
        matched_cases=[
            {
                "CaseNumber": "C1",
                "CaseStyle": "S1",
                "CaseType": "CIRCUIT CIVIL",
                "FilingDate": "2023-01-01",
            }
        ],
    )
    payload = res["payload_sent"]
    assert len(payload["CaseItems"]) == 1
    assert "CaseType" not in payload["CaseItems"][0]


def test_tc_gw_004_9_digit_claim_number_prefixed():
    """TC-GW-004: 9-digit claim number gets '0' prefix."""
    assert format_claim_number("123456789") == "0123456789"
    assert format_claim_number("0123456789") == "0123456789"


@pytest.mark.asyncio
async def test_tc_gw_005_transaction_id_unique_per_call():
    """TC-GW-005: TransactionId is unique across distinct calls."""
    client = GuidewireClient(mock_mode=True)
    res1 = await client.send_case_update("0123456789", "1", [])
    res2 = await client.send_case_update("0123456789", "1", [])
    tx1 = res1["payload_sent"]["TransactionId"]
    tx2 = res2["payload_sent"]["TransactionId"]
    assert tx1 != tx2


@pytest.mark.asyncio
async def test_tc_gw_006_suit_filed_date_included():
    """TC-GW-006: SuitFiledDate is present and formatted in CaseItems."""
    client = GuidewireClient(mock_mode=True)
    res = await client.send_case_update(
        claim_number="0123456789",
        exposure_number="1",
        matched_cases=[
            {
                "CaseNumber": "C1",
                "CaseStyle": "S1",
                "SuitFiledDate": "2023-05-15",
            }
        ],
    )
    case_item = res["payload_sent"]["CaseItems"][0]
    assert case_item["SuitFiledDate"] == "2023-05-15"
