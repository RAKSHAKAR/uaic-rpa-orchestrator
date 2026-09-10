"""Unit and integration tests for Error Screenshots, Storage Providers, and Operator Diagnostics."""

import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.database import TaskAsyncSessionLocal, init_db
from app.main import app
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.models.error_screenshot import ErrorScreenshot
from app.schemas.settings import StorageSettings, StorageTestRequest
from app.services.settings_service import get_system_settings_async, save_system_settings_async
from app.services.storage_service import StorageService


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    """Ensure database tables and columns are initialized."""
    await init_db()
    yield


@pytest.mark.asyncio
async def test_storage_service_local_save_and_test():
    """Verify saving screenshot bytes locally and testing local storage provider."""
    test_filename = f"test_error_{uuid.uuid4().hex[:8]}.png"
    dummy_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"

    res = await StorageService.save_screenshot_bytes(
        filename=test_filename,
        image_bytes=dummy_bytes,
        storage_cfg=StorageSettings(storage_provider="local"),
    )
    assert res["stored_provider"] == "local"
    assert Path(res["local_path"]).exists()
    assert res["size_bytes"] == len(dummy_bytes)

    # Test connection endpoint logic
    test_req = StorageTestRequest(storage_provider="local")
    test_res = await StorageService.test_connection(test_req)
    assert test_res.success is True
    assert test_res.storage_provider == "local"
    assert test_res.duration_ms >= 0


@pytest.mark.asyncio
async def test_claim_screenshots_endpoints():
    """Verify GET /api/v1/claims/{id}/screenshots and GET image endpoints."""
    claim_id = str(uuid.uuid4())
    shot_id = str(uuid.uuid4())
    test_filename = f"{claim_id}_broward_{uuid.uuid4().hex[:6]}.png"

    # Create dummy PNG on disk in SCREENSHOTS_DIR
    settings.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    local_img_path = settings.SCREENSHOTS_DIR / test_filename
    local_img_path.write_bytes(b"\x89PNG\r\n\x1a\nDummyImageData")

    # Insert Claim and ErrorScreenshot in DB
    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"CLM-{claim_id[:6]}",
            exposure_number="1",
            claimant_first_name="Test",
            claimant_last_name="User",
            record_status=RecordStatusEnum.FAILED,
        )
        session.add(claim)

        shot = ErrorScreenshot(
            id=shot_id,
            claim_id=claim_id,
            portal_key="broward",
            portal_name="Broward County (FL)",
            page_url="https://www.browardclerk.org/Web2/",
            page_title="Broward County Clerk Case Search",
            exception_message="Timeout waiting for CAPTCHA response token",
            attempt_number=1,
            storage_provider="local",
            file_path=test_filename,
        )
        session.add(shot)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Fetch screenshot list for claim
        res = await client.get(f"/api/v1/claims/{claim_id}/screenshots")
        assert res.status_code == 200
        shots_data = res.json()
        assert len(shots_data) == 1
        assert shots_data[0]["id"] == shot_id
        assert shots_data[0]["portal_key"] == "broward"
        assert shots_data[0]["storage_provider"] == "local"
        assert shots_data[0]["exception_message"] == "Timeout waiting for CAPTCHA response token"
        assert "/image" in shots_data[0]["image_url"]

        # 2. Fetch binary image
        img_res = await client.get(f"/api/v1/claims/{claim_id}/screenshots/{shot_id}/image")
        assert img_res.status_code == 200
        assert img_res.headers["content-type"] == "image/png"
        assert img_res.content == b"\x89PNG\r\n\x1a\nDummyImageData"

        # 3. Test storage connection API endpoint
        storage_test_res = await client.post(
            "/api/v1/settings/test-storage",
            json={"storage_provider": "local"},
        )
        assert storage_test_res.status_code == 200
        test_body = storage_test_res.json()
        assert test_body["success"] is True
        assert test_body["storage_provider"] == "local"


@pytest.mark.asyncio
async def test_capture_screenshot_toggle_behavior():
    """Verify that capture_screenshot_on_error skips capture when toggle is disabled."""
    from app.automation.florida.broward import BrowardScraper

    scraper = BrowardScraper(base_url="https://www.browardclerk.org/Web2/")
    mock_page = MagicMock()
    mock_page.screenshot = AsyncMock()

    # Disable toggle in settings
    curr_settings = await get_system_settings_async()
    updated = curr_settings.model_copy(deep=True)
    updated.storage.capture_error_screenshots = False
    await save_system_settings_async(updated)

    result = await scraper.capture_screenshot_on_error(
        page=mock_page,
        claim_id=str(uuid.uuid4()),
        portal_key="broward",
        attempt=1,
    )
    assert result is None
    # Verify screenshot was never taken to conserve storage
    mock_page.screenshot.assert_not_called()

    # Re-enable toggle
    updated.storage.capture_error_screenshots = True
    await save_system_settings_async(updated)
