"""Automated test suite verifying queue operational telemetry and extracted court cases export parity.

Implementation ID: IMP-2026-1005-002
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
async def test_queue_status_operational_telemetry():
    """Verify /api/v1/queue/status returns total_claims and total_cases_extracted fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/queue/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_claims" in data
        assert isinstance(data["total_claims"], int)
        assert "total_cases_extracted" in data
        assert isinstance(data["total_cases_extracted"], int)
        assert "active_tasks" in data
        assert "completed_tasks" in data
        assert "failed_tasks" in data


@pytest.mark.asyncio
async def test_export_claims_excel_multi_sheet_and_cases_extracted():
    """Verify /api/v1/claims/export?format=xlsx produces Claims Summary & All Extracted Cases sheets."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/claims/export?format=xlsx")
        assert resp.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in resp.headers["content-type"]

        excel_bytes = resp.content
        xl = pd.ExcelFile(io.BytesIO(excel_bytes))
        assert "Claims Summary" in xl.sheet_names
        assert "All Extracted Cases" in xl.sheet_names

        df_summary = pd.read_excel(xl, sheet_name="Claims Summary")
        if not df_summary.empty:
            assert "Cases Extracted" in df_summary.columns
            assert "Extracted Case Numbers" in df_summary.columns
            assert "Extracted Case Styles" in df_summary.columns
            assert "Guidewire Pushed" in df_summary.columns
            assert "Guidewire Activity ID" in df_summary.columns


@pytest.mark.asyncio
async def test_export_claims_csv_cases_extracted():
    """Verify /api/v1/claims/export?format=csv includes Cases Extracted column."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/claims/export?format=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

        df_csv = pd.read_csv(io.BytesIO(resp.content))
        if not df_csv.empty:
            assert "Cases Extracted" in df_csv.columns
            assert "Extracted Case Numbers" in df_csv.columns
            assert "Extracted Case Styles" in df_csv.columns


@pytest.mark.asyncio
async def test_export_claims_json_cases_extracted():
    """Verify /api/v1/claims/export?format=json returns valid JSON with Cases Extracted and nested court_cases."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/claims/export?format=json")
        assert resp.status_code == 200
        assert "application/json" in resp.headers["content-type"]
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert "Cases Extracted" in data[0]
            assert "court_cases" in data[0]
            assert isinstance(data[0]["court_cases"], list)


@pytest.mark.asyncio
async def test_async_export_task_multi_sheet_and_cases_extracted():
    """Verify Celery async export engine _generate_export_data generates multi-sheet Excel with Cases Extracted."""
    res = await _generate_export_data(export_format="xlsx")
    assert res["status"] == "SUCCESS"
    target_path = Path(res["file_path"])
    assert target_path.exists()

    xl = pd.ExcelFile(target_path)
    assert "Claims Summary" in xl.sheet_names
    assert "All Extracted Cases" in xl.sheet_names

    df_summary = pd.read_excel(xl, sheet_name="Claims Summary")
    if not df_summary.empty:
        assert "Cases Extracted" in df_summary.columns
        assert "Extracted Case Numbers" in df_summary.columns
