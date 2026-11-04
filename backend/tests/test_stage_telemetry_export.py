"""Automated test suite verifying Detailed Stage Execution Telemetry export in Excel and CSV.

Implementation ID: IMP-2026-1006-003
Project: UAIC Claim & RPA Orchestrator
"""

import io
from pathlib import Path

import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import Base, engine
from app.main import app
from app.tasks.export_tasks import _generate_export_data


@pytest.fixture(autouse=True)
async def setup_database():
    """Ensure database schema is initialized for API tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_export_claims_excel_detailed_stage_telemetry_sheet():
    """Verify /api/v1/claims/export?format=xlsx produces Detailed Stage Execution Telemetry sheet."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/claims/export?format=xlsx")
        assert resp.status_code == 200
        assert (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in resp.headers["content-type"]
        )

        excel_bytes = resp.content
        xl = pd.ExcelFile(io.BytesIO(excel_bytes))
        assert "Claims Summary" in xl.sheet_names
        assert "All Extracted Cases" in xl.sheet_names
        assert "Detailed Stage Telemetry" in xl.sheet_names

        df_telemetry = pd.read_excel(xl, sheet_name="Detailed Stage Telemetry")
        expected_cols = [
            "Claim Number",
            "Telemetry Scope",
            "County Portal",
            "Stage Key",
            "Stage Name",
            "Stage Status",
            "Duration (s)",
        ]
        for col in expected_cols:
            assert col in df_telemetry.columns, (
                f"Expected {col} in Detailed Stage Execution Telemetry columns"
            )


@pytest.mark.asyncio
async def test_export_claims_csv_telemetry_view():
    """Verify /api/v1/claims/export?format=csv&view=telemetry downloads stage telemetry dataset."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/claims/export?format=csv&view=telemetry")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert "claims_stage_execution_telemetry_" in resp.headers.get("content-disposition", "")

        df_csv = pd.read_csv(io.BytesIO(resp.content))
        expected_cols = [
            "Claim Number",
            "Telemetry Scope",
            "County Portal",
            "Stage Key",
            "Stage Name",
            "Stage Status",
            "Duration (s)",
        ]
        for col in expected_cols:
            assert col in df_csv.columns, f"Expected {col} in CSV telemetry view"


@pytest.mark.asyncio
async def test_export_claims_csv_summary_stage_duration_columns():
    """Verify default summary CSV includes stage duration breakdown columns."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/claims/export?format=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

        df_csv = pd.read_csv(io.BytesIO(resp.content))
        if not df_csv.empty:
            assert "Total Scraping Duration (s)" in df_csv.columns
            assert "Stage Browser Launch (s)" in df_csv.columns
            assert "Stage Navigation (s)" in df_csv.columns
            assert "Stage Data Filling (s)" in df_csv.columns
            assert "Stage CAPTCHA Solving (s)" in df_csv.columns
            assert "Stage Submit (s)" in df_csv.columns
            assert "Stage Result Retrieval (s)" in df_csv.columns
            assert "Stage Database Save (s)" in df_csv.columns


@pytest.mark.asyncio
async def test_async_export_task_detailed_stage_telemetry():
    """Verify Celery async engine produces 3 sheets in Excel and dedicated CSV when view=telemetry."""
    # 1. Test Excel Async
    res_xlsx = await _generate_export_data(export_format="xlsx")
    assert res_xlsx["status"] == "SUCCESS"
    target_xlsx = Path(res_xlsx["file_path"])
    assert target_xlsx.exists()

    xl = pd.ExcelFile(target_xlsx)
    assert "Claims Summary" in xl.sheet_names
    assert "All Extracted Cases" in xl.sheet_names
    assert "Detailed Stage Telemetry" in xl.sheet_names

    # 2. Test CSV Async with view=telemetry
    res_csv = await _generate_export_data(export_format="csv", view="telemetry")
    assert res_csv["status"] == "SUCCESS"
    assert "stage_telemetry" in res_csv["filename"]
    target_csv = Path(res_csv["file_path"])
    assert target_csv.exists()

    df_csv = pd.read_csv(target_csv)
    assert "Telemetry Scope" in df_csv.columns
    assert "Stage Name" in df_csv.columns
