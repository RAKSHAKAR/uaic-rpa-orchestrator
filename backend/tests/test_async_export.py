"""Automated tests for asynchronous background claim dataset exports."""

from pathlib import Path
from unittest.mock import MagicMock, patch

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
async def test_generate_export_data_direct():
    """Verify in-process generation of CSV and XLSX files."""
    csv_res = await _generate_export_data(export_format="csv")
    assert csv_res["status"] == "SUCCESS"
    assert csv_res["format"] == "csv"
    assert Path(csv_res["file_path"]).exists()

    xlsx_res = await _generate_export_data(export_format="xlsx")
    assert xlsx_res["status"] == "SUCCESS"
    assert xlsx_res["format"] == "xlsx"
    assert Path(xlsx_res["file_path"]).exists()


@pytest.mark.asyncio
async def test_async_export_endpoints_api():
    """Verify POST /export-async and status polling / download endpoints."""
    mock_task = MagicMock()
    mock_task.id = "mock-export-task-123"

    transport = ASGITransport(app=app)
    with patch("app.api.v1.endpoints.claims.celery_app.send_task", return_value=mock_task):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Trigger export
            trigger_resp = await client.post(
                "/api/v1/claims/export-async",
                json={"format": "csv", "status": None},
            )
            assert trigger_resp.status_code == 200
            data = trigger_resp.json()
            assert data["success"] is True
            assert "task_id" in data

            # Test synchronous / in-process status polling
            status_resp = await client.get("/api/v1/claims/export-async/sync-test123/status")
            assert status_resp.status_code == 200
            st_data = status_resp.json()
            assert st_data["status"] == "SUCCESS"
            assert "download_url" in st_data["result"]
