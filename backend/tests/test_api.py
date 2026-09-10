import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure database schema is initialized for API tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["database"] == "healthy"


@pytest.mark.asyncio
async def test_claims_list_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/claims")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_claims_stats_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/claims/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_claims" in data
        assert "match_found" in data


@pytest.mark.asyncio
async def test_queue_status_endpoint():
    from unittest.mock import patch
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.api.v1.endpoints.queue.celery_app.control.ping", return_value=[]), \
             patch("redis.Redis.from_url") as mock_redis:
            mock_redis.return_value.llen.return_value = 0
            response = await client.get("/api/v1/queue/status")
            assert response.status_code == 200
            data = response.json()
            assert "active_tasks" in data
            assert "queues" in data


@pytest.mark.asyncio
async def test_settings_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # GET
        get_res = await client.get("/api/v1/settings")
        assert get_res.status_code == 200
        data = get_res.json()
        assert "automation" in data
        assert "portals" in data
        assert "integration" in data
        assert "max_captcha_attempts" in data["automation"]
        assert data["automation"]["max_captcha_attempts"] == 2

        # POST update
        data["automation"]["max_captcha_attempts"] = 7
        data["automation"]["headless_mode"] = False
        data["integration"]["guidewire_auth_type"] = "ApiKey"
        data["integration"]["guidewire_api_key"] = "test-secret-key-12345"
        update_res = await client.post("/api/v1/settings", json=data)
        assert update_res.status_code == 200
        updated_data = update_res.json()
        assert updated_data["automation"]["max_captcha_attempts"] == 7
        assert updated_data["automation"]["headless_mode"] is False
        assert updated_data["integration"]["guidewire_auth_type"] == "ApiKey"

        # Reset
        reset_res = await client.post("/api/v1/settings/reset")
        assert reset_res.status_code == 200
        reset_data = reset_res.json()
        assert reset_data["automation"]["max_captcha_attempts"] == 2


@pytest.mark.asyncio
async def test_guidewire_test_connection_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        test_payload = {
            "api_url": "https://api.guidewire.example.com/cc/rest/v1/caseupdate",
            "auth_type": "Bearer",
            "api_key": "gw_test_token_abc",
            "mock_mode": True,
        }
        res = await client.post("/api/v1/settings/test-guidewire", json=test_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["status_code"] == 200
        assert "duration_ms" in data
        assert data["duration_ms"] > 0
        assert "response_body" in data
        assert data["response_body"]["status"] == "success"
        assert "request_headers" in data


@pytest.mark.asyncio
async def test_portal_ping_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "portal_name": "Broward County Clerk (FL)",
            "url": "https://www.browardclerk.org/Web2/",
            "timeout_seconds": 10,
        }
        res = await client.post("/api/v1/settings/test-portal", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "portal_name" in data
        assert "reachable" in data
        assert "duration_ms" in data


@pytest.mark.asyncio
async def test_browser_execution_test_endpoint(monkeypatch):
    from unittest.mock import AsyncMock, MagicMock

    mock_page = MagicMock()
    mock_page.title = AsyncMock(return_value="Example Domain")
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.evaluate = AsyncMock()
    mock_page.bring_to_front = AsyncMock()

    mock_ctx = MagicMock()
    mock_ctx.new_page = AsyncMock(return_value=mock_page)

    mock_session = MagicMock()
    mock_session.start = AsyncMock(return_value=mock_ctx)
    mock_session.close = AsyncMock()
    mock_session.extension_loaded = True
    mock_session.extension_id = "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
    mock_session.service_worker_active = True
    mock_session.warning_message = None

    mock_session_cls = MagicMock(return_value=mock_session)
    mock_session_cls.find_chrome_executable.return_value = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    monkeypatch.setattr("app.api.v1.endpoints.settings.ChromeSession", mock_session_cls)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test Attended Mode
        res1 = await client.post("/api/v1/settings/test-browser", json={"headless": False, "browser_engine": "chromium"})
        assert res1.status_code == 200
        d1 = res1.json()
        assert d1["success"] is True
        assert d1["mode"] == "Attended (Visible GUI)"
        assert d1["headless"] is False
        assert d1["browser_engine"] == "chromium"
        assert d1["extension_loaded"] is True
        assert d1["extension_id"] == "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
        assert d1["service_worker_active"] is True
        assert d1["page_title"] == "Example Domain"

        # Test Headless Mode
        res2 = await client.post("/api/v1/settings/test-browser", json={"headless": True, "browser_engine": "msedge"})
        assert res2.status_code == 200
        d2 = res2.json()
        assert d2["success"] is True
        assert d2["mode"] == "Headless (Background)"
        assert d2["headless"] is True
        assert d2["browser_engine"] == "msedge"


@pytest.mark.asyncio
async def test_browser_test_endpoint_live_extension_verification(monkeypatch):
    """Verify test-browser endpoint captures extension blocked warnings for Chrome Stable."""
    from unittest.mock import AsyncMock, MagicMock

    mock_page = MagicMock()
    mock_page.title = AsyncMock(return_value="Example Domain")
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.evaluate = AsyncMock()
    mock_page.bring_to_front = AsyncMock()

    mock_ctx = MagicMock()
    mock_ctx.new_page = AsyncMock(return_value=mock_page)

    mock_session = MagicMock()
    mock_session.start = AsyncMock(return_value=mock_ctx)
    mock_session.close = AsyncMock()
    mock_session.extension_loaded = False
    mock_session.extension_id = None
    mock_session.service_worker_active = False
    mock_session.warning_message = "Google Chrome Stable on Windows ignored --load-extension."

    mock_session_cls = MagicMock(return_value=mock_session)
    mock_session_cls.find_chrome_executable.return_value = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    monkeypatch.setattr("app.api.v1.endpoints.settings.ChromeSession", mock_session_cls)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/settings/test-browser", json={"headless": False, "browser_engine": "chrome"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["browser_engine"] == "chrome"
        assert data["extension_loaded"] is False
        assert data["service_worker_active"] is False
        assert "ignored --load-extension" in data["warning"]

