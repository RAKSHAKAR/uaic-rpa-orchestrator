"""Automated tests for 6-way browser engine matrix and defensive pre-flight validation.

Validates:
- Google Chrome: Attended (Visible GUI) & Headless (Background)
- Chromium: Attended (Visible GUI) & Headless (Background)
- Microsoft Edge: Attended (Visible GUI) & Headless (Background)
- Defensive pre-flight driver and executable validations
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.automation.browser_manager import ChromeSession
from app.core.database import Base, engine
from app.main import app


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure database schema is initialized for API tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.mark.asyncio
async def test_preflight_missing_playwright_driver_raises_runtime_error(mocker):
    """Verify that a missing Playwright driver raises a clear descriptive RuntimeError."""
    mocker.patch(
        "playwright._impl._driver.compute_driver_executable",
        return_value=(Path("C:/non_existent_driver/node.exe"), None),
    )
    session = ChromeSession(browser_engine="chromium")
    with pytest.raises(RuntimeError, match="Playwright driver executable not found"):
        await session.start()


@pytest.mark.asyncio
async def test_preflight_missing_chrome_executable_raises_runtime_error(mocker):
    """Verify that a missing Chrome executable raises a descriptive RuntimeError."""
    mocker.patch.object(ChromeSession, "find_chrome_executable", return_value=None)
    mocker.patch("app.automation.browser_manager.async_playwright")
    session = ChromeSession(browser_engine="chrome", chrome_binary_path="C:/non_existent_chrome.exe")
    with pytest.raises(RuntimeError, match="Google Chrome executable.*was not found"):
        await session.start()


@pytest.mark.asyncio
@pytest.mark.parametrize("browser_engine,headless", [
    ("chrome", False),
    ("chrome", True),
    ("chromium", False),
    ("chromium", True),
    ("msedge", False),
    ("msedge", True),
])
async def test_browser_test_endpoint_mocked_success(browser_engine, headless, mocker):
    """Unit test for /api/v1/settings/test-browser across all 6 engine and mode permutations."""
    mock_session = MagicMock()
    mock_session.extension_loaded = True
    mock_session.extension_id = "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
    mock_session.service_worker_active = True
    mock_session.warning_message = None
    mock_session.close = AsyncMock()

    async def mock_start():
        ctx = MagicMock()
        page = MagicMock()
        page.set_default_timeout = MagicMock()
        page.bring_to_front = AsyncMock()
        page.goto = AsyncMock()
        page.title = AsyncMock(return_value="Example Domain")
        page.evaluate = AsyncMock()
        page.wait_for_timeout = AsyncMock()
        ctx.new_page = AsyncMock(return_value=page)
        return ctx

    mock_session.start = mock_start

    mocker.patch("app.api.v1.endpoints.settings.ChromeSession", return_value=mock_session)
    mocker.patch("app.api.v1.endpoints.settings.ExtensionManager.resolve_extension_path", return_value=Path("./anticaptcha-plugin_v0.83"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/settings/test-browser",
            json={"browser_engine": browser_engine, "headless": headless, "timeout_seconds": 15},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["browser_engine"] == browser_engine
        assert data["headless"] == headless
        assert data["extension_loaded"] is True
        assert data["extension_id"] == "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
        assert data["service_worker_active"] is True
        assert data["error_detail"] is None
        assert "Example Domain" in data["page_title"]


@pytest.mark.asyncio
async def test_live_chrome_attended_integration():
    """Live integration test verifying that Google Chrome Attended Mode succeeds via HTTP API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=50.0) as client:
        response = await client.post(
            "/api/v1/settings/test-browser",
            json={"browser_engine": "chrome", "headless": False, "timeout_seconds": 45},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["browser_engine"] == "chrome"
        assert data["headless"] is False
        assert data["extension_loaded"] is True
        assert data["service_worker_active"] is True
        assert data["error_detail"] is None


@pytest.mark.asyncio
async def test_live_chrome_headless_integration():
    """Live integration test verifying that Google Chrome Headless Mode succeeds via HTTP API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=50.0) as client:
        response = await client.post(
            "/api/v1/settings/test-browser",
            json={"browser_engine": "chrome", "headless": True, "timeout_seconds": 45},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["browser_engine"] == "chrome"
        assert data["headless"] is True
        assert data["extension_loaded"] is True
        assert data["service_worker_active"] is True
        assert data["error_detail"] is None
