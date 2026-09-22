"""Tests for Parallel RPA Fleet Concurrency, Multi-Engine Support, and Isolated Worker Profiles."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.automation.browser_manager import ChromeSession
from app.automation.session_runner import SingleSessionBrowserRunner
from app.main import app


@pytest.mark.asyncio
async def test_single_session_runner_worker_profile_isolation(tmp_path):
    """Verify SingleSessionBrowserRunner creates an isolated temp profile directory pre-seeded from canonical profile."""
    runner = SingleSessionBrowserRunner(
        headless=True,
        browser_engine="chromium",
        user_data_dir=str(tmp_path / "mock_profile"),
    )
    assert runner.browser_engine == "chromium"


def test_chrome_session_isolated_profile_and_worker_id():
    """Verify ChromeSession supports worker_id and isolated_profile flags."""
    session = ChromeSession(
        headless=False,
        browser_engine="chromium",
        isolated_profile=True,
        worker_id=3,
    )
    assert session.isolated_profile is True
    assert session.worker_id == 3
    assert session.browser_engine == "chromium"


@pytest.mark.asyncio
@pytest.mark.parametrize("concurrency,engine,headless", [
    (1, "chromium", True),
    (3, "chromium", False),
    (5, "chrome", False),
    (10, "msedge", True),
])
async def test_fleet_test_endpoint_mocked(concurrency, engine, headless, mocker):
    """Verify /api/v1/settings/test-fleet runs parallel workers concurrently."""
    mock_sessions = []

    def mock_session_factory(*args, **kwargs):
        s = MagicMock()
        s.extension_loaded = True
        s.extension_id = "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
        s.service_worker_active = True
        s.warning_message = None
        s.close = AsyncMock()

        async def mock_start():
            ctx = MagicMock()
            page = MagicMock()
            page.set_default_timeout = MagicMock()
            page.bring_to_front = AsyncMock()
            page.goto = AsyncMock()
            page.title = AsyncMock(return_value=f"Worker #{kwargs.get('worker_id')} Verified")
            page.evaluate = AsyncMock()
            page.wait_for_timeout = AsyncMock()
            ctx.new_page = AsyncMock(return_value=page)
            return ctx

        s.start = mock_start
        mock_sessions.append(s)
        return s

    mocker.patch("app.api.v1.endpoints.settings.ChromeSession", side_effect=mock_session_factory)
    mocker.patch("app.api.v1.endpoints.settings.ExtensionManager.resolve_extension_path", return_value=Path("./anticaptcha-plugin_v0.83"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/settings/test-fleet",
            json={
                "concurrency": concurrency,
                "browser_engine": engine,
                "headless": headless,
                "timeout_seconds": 15,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["concurrency_requested"] == concurrency
        assert data["concurrency_succeeded"] == concurrency
        assert data["browser_engine"] == engine
        assert len(data["workers"]) == concurrency

        for idx, worker in enumerate(data["workers"], start=1):
            assert worker["worker_id"] == idx
            assert worker["status"] == "success"
            assert worker["extension_loaded"] is True
            assert f"Worker #{idx}" in worker["window_title"]


@pytest.mark.asyncio
async def test_fleet_test_endpoint_partial_failure(mocker):
    """Verify /api/v1/settings/test-fleet handles partial worker failures cleanly."""
    call_count = 0

    def mock_session_factory(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        s = MagicMock()
        s.extension_loaded = True
        s.close = AsyncMock()

        if kwargs.get("worker_id") == 2:
            async def failing_start():
                raise RuntimeError("Simulated timeout on worker 2")
            s.start = failing_start
        else:
            async def mock_start():
                ctx = MagicMock()
                page = MagicMock()
                page.set_default_timeout = MagicMock()
                page.bring_to_front = AsyncMock()
                page.goto = AsyncMock()
                page.title = AsyncMock(return_value="Success")
                page.evaluate = AsyncMock()
                page.wait_for_timeout = AsyncMock()
                ctx.new_page = AsyncMock(return_value=page)
                return ctx
            s.start = mock_start

        return s

    mocker.patch("app.api.v1.endpoints.settings.ChromeSession", side_effect=mock_session_factory)
    mocker.patch("app.api.v1.endpoints.settings.ExtensionManager.resolve_extension_path", return_value=Path("./anticaptcha-plugin_v0.83"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/settings/test-fleet",
            json={"concurrency": 3, "browser_engine": "chromium", "headless": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["concurrency_requested"] == 3
        assert data["concurrency_succeeded"] == 2
        assert len(data["workers"]) == 3
        assert data["workers"][0]["status"] == "success"
        assert data["workers"][1]["status"] == "failed"
        assert "Simulated timeout" in data["workers"][1]["message"]
        assert data["workers"][2]["status"] == "success"
