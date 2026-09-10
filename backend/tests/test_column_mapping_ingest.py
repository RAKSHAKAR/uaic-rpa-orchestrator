"""Unit and integration tests for Column Mapping, Pre-Ingestion Validation, Duplicate Strategies, and Failed Rows CSV Export."""

import json
import os

import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.ingest import UPLOAD_DIR
from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.claim import ClaimRecord
from app.services.excel_parser import (
    auto_detect_column_mapping,
    validate_and_normalize_claim_data,
)
from app.tasks.ingest_tasks import _async_parse_and_ingest


@pytest.mark.asyncio
async def test_auto_detect_column_mapping_exact_and_fuzzy():
    """Verify auto-detection identifies exact aliases and fuzzy column header variants."""
    non_standard_columns = [
        "Claim#",
        "Insured FName",
        "Insured LName",
        "Claimant First",
        "Claimant Last",
        "Date of Loss",
        "Loss State",
        "Loss City",
        "Policy St",
    ]

    recs = auto_detect_column_mapping(non_standard_columns)
    mapping_dict = {r["target_key"]: r for r in recs}

    assert mapping_dict["claim_number"]["source_column"] == "Claim#"
    assert mapping_dict["claim_number"]["confidence"] in ["EXACT", "HIGH_FUZZY"]

    assert mapping_dict["dol"]["source_column"] == "Date of Loss"
    assert mapping_dict["dol"]["confidence"] in ["EXACT", "HIGH_FUZZY"]

    assert mapping_dict["loss_location_state"]["source_column"] == "Loss State"
    assert mapping_dict["policy_state"]["source_column"] == "Policy St"


@pytest.mark.asyncio
async def test_validate_spreadsheet_mapping_missing_claim_number():
    """Verify validation detects missing claim number and flags row as INVALID."""
    df = pd.DataFrame([
        {"MyClaim": "CLM-1001", "MyName": "John Doe", "AccidentDate": "2024-01-15"},
        {"MyClaim": "", "MyName": "Jane Smith", "AccidentDate": "2024-02-20"},
        {"MyClaim": None, "MyName": "Bob Brown", "AccidentDate": "2024-03-25"},
    ])

    mapping = {
        "claim_number": "MyClaim",
        "insured_first_name": "MyName",
        "dol": "AccidentDate",
    }

    result = validate_and_normalize_claim_data(df, column_mapping=mapping)

    assert result["total_rows"] == 3
    assert result["valid_rows"] == 1
    assert result["invalid_rows"] == 2
    assert len(result["issues"]) == 2
    assert result["issues"][0]["issue_type"] == "INVALID"
    assert result["issues"][1]["issue_type"] == "INVALID"


@pytest.mark.asyncio
async def test_validate_spreadsheet_mapping_duplicate_in_file():
    """Verify validation flags multiple occurrences of the same claim number within spreadsheet."""
    df = pd.DataFrame([
        {"Claim Number": "DUP-FILE-99", "Insured First Name": "Alice"},
        {"Claim Number": "UNIQUE-01", "Insured First Name": "Charlie"},
        {"Claim Number": "DUP-FILE-99", "Insured First Name": "Alice Repeat"},
    ])

    result = validate_and_normalize_claim_data(df, duplicate_strategy="SKIP")

    assert result["total_rows"] == 3
    assert result["valid_rows"] == 2
    assert result["duplicate_rows"] == 1
    assert len(result["records_to_insert"]) == 2
    assert any(i["issue_type"] == "DUPLICATE_IN_FILE" for i in result["issues"])


@pytest.mark.asyncio
async def test_validate_endpoint_database_duplicate_check():
    """Verify POST /api/v1/ingest/validate checks database and flags DUPLICATE_IN_DB."""
    async with AsyncSessionLocal() as session:
        # Seed an existing claim in database
        existing_claim = ClaimRecord(
            claim_number="DB-EXISTS-777",
            insured_first_name="PreExisting",
            policy_state="Florida",
        )
        session.add(existing_claim)
        await session.commit()

    # Create CSV with the same claim number
    csv_content = (
        b"CaseIdentifier,PolicyHolder,DateOfLoss\n"
        b"DB-EXISTS-777,PreExisting Holder,05/10/2023\n"
        b"BRAND-NEW-888,New Holder,06/12/2023\n"
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("claims_validate.csv", csv_content, "text/csv")}
        mapping = json.dumps({
            "claim_number": "CaseIdentifier",
            "insured_first_name": "PolicyHolder",
            "dol": "DateOfLoss",
        })
        data = {"mapping": mapping, "duplicate_strategy": "SKIP"}

        res = await client.post("/api/v1/ingest/validate", files=files, data=data)
        assert res.status_code == 200
        val_data = res.json()

        assert val_data["total_rows"] == 2
        assert val_data["valid_rows"] == 1  # Brand new row valid, duplicate skipped
        assert val_data["duplicate_rows"] == 1
        assert any(i["issue_type"] == "DUPLICATE_IN_DB" for i in val_data["issues"])
        assert any(i["claim_number"] == "DB-EXISTS-777" for i in val_data["issues"])


import uuid


@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_upload_with_custom_mapping_and_failed_rows_csv_export():
    """Verify POST /api/v1/ingest/upload with custom mapping, batch status polling, and failed rows CSV export."""
    u_id = uuid.uuid4().hex[:6]
    claim_num = f"MAP-{u_id}"
    csv_content = (
        f"ReferenceNo,First,Last,EventDate,LossState\n"
        f"{claim_num},John,Doe,04/01/2024,Florida\n"
        f",Blank,Claim,04/02/2024,Florida\n"  # Invalid (blank claim)
        f"{claim_num},John,Duplicate,04/03/2024,Florida\n"  # In-file duplicate
    ).encode()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("custom_mapped.csv", csv_content, "text/csv")}
        mapping = json.dumps({
            "claim_number": "ReferenceNo",
            "insured_first_name": "First",
            "insured_last_name": "Last",
            "dol": "EventDate",
            "loss_location_state": "LossState",
        })
        data = {"mapping": mapping, "duplicate_strategy": "SKIP"}


        upload_res = await client.post("/api/v1/ingest/upload", files=files, data=data)
        assert upload_res.status_code == 200
        batch_info = upload_res.json()
        batch_id = batch_info["id"]

        # Directly run parser async logic for testing without waiting on Celery worker.
        # Note: both this call and the upload endpoint above require Redis (celery_app.send_task).
        # This test is guarded by @pytest.mark.requires_redis.
        file_path = os.path.join(UPLOAD_DIR, f"{batch_id}_custom_mapped.csv")

        await _async_parse_and_ingest(
            batch_id=batch_id,
            file_path=file_path,
            column_mapping=json.loads(mapping),
            duplicate_strategy="SKIP",
        )

        # 1. Verify GET /api/v1/ingest/batches/{batch_id}
        status_res = await client.get(f"/api/v1/ingest/batches/{batch_id}")
        assert status_res.status_code == 200
        batch_data = status_res.json()
        assert batch_data["status"] == "COMPLETED"
        assert batch_data["total_records"] == 3
        assert batch_data["processed_records"] == 1
        assert batch_data["invalid_records"] == 1
        assert batch_data["duplicate_records"] == 1

        # 2. Verify GET /api/v1/ingest/batches/{batch_id}/failed-rows
        failed_csv_res = await client.get(f"/api/v1/ingest/batches/{batch_id}/failed-rows")
        assert failed_csv_res.status_code == 200
        assert "text/csv" in failed_csv_res.headers["content-type"]
        csv_text = failed_csv_res.text
        assert f"Duplicate claim number '{claim_num}'" in csv_text

