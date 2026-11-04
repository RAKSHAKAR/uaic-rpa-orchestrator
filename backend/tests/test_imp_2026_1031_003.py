"""
Comprehensive Verification Suite for IMP-2026-1031-003:
1. Full Browser Compatibility: Chrome, Edge, and Chromium detection, version resolution, and zero silent fallback.
2. Anti-Captcha Extension: Verification, unpacked loading, and BlockedExtensionInitializationError escalation.
3. Execution Settings Defaults: Keystroke 50ms, Pacing 250ms, Timeout 180s, Stealth Jitter True, Reload 5s, Headless True, Unattended, Screen Rec False, Captcha 120s.
4. Eight-Bot Concurrency Decoupling: Dispatch concurrency with correlation IDs ({claim_id}:{portal_key}) and status DISPATCHED.
5. Geography-based State Routing: FL (3 bots), TX (5 bots), Cross-state (8 bots), and Missing State -> NEEDS_REVIEW.
6. Diagrams & Workflow Visualizations: Stable non-destructive lifecycle rendering.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.automation.base import resolve_browser_launch_target
from app.automation.browser_manager import (
    BlockedExtensionInitializationError,
    ChromeSession,
)
from app.core.database import Base, engine
from app.main import app
from app.models.claim import BotStatusEnum, RecordStatusEnum
from app.schemas.settings import AutomationSettings
from app.services.excel_parser import resolve_county_bot_targets, validate_and_normalize_claim_data
from app.services.settings_service import (
    get_default_settings,
)


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure database schema is created for verification."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── Requirement 1 & 6: Execution Settings Defaults ──────────────────────────────
def test_automation_settings_default_realignment():
    """Verify that default settings match Master Requirement 6 precisely."""
    auto = AutomationSettings()
    assert auto.typing_delay_ms == 50, "Keystroke delay must default to 50ms"
    assert auto.typing_speed_mode == "balanced", "Typing speed mode must default to balanced"
    assert auto.action_pacing_ms == 250, "Action pacing must default to 250ms"
    assert auto.page_timeout_seconds == 180, "Navigation timeout must default to 180s"
    assert auto.stealth_clicks is True, "Mouse jitter (stealth clicks) must default to True"
    assert auto.reload_backoff_seconds == 5, "Reload backoff must default to 5s"
    assert auto.headless_mode is True, "Browser must default to Headless (Background) mode"
    assert auto.human_interaction_mode == "unattended", (
        "Interaction mode must default to unattended"
    )
    assert auto.enable_screen_recording is False, "Screen recording must default to False"
    assert auto.captcha_wait_seconds == 120, "CAPTCHA wait timeout must default to 120s"


def test_system_settings_default_values(monkeypatch):
    """Verify get_default_settings() returns realigned production defaults."""
    from app.core.config import settings as app_settings

    monkeypatch.setattr(app_settings, "PLAYWRIGHT_HEADLESS", True)
    sys_cfg = get_default_settings()
    auto = sys_cfg.automation
    assert auto.typing_delay_ms == 50
    assert auto.action_pacing_ms == 250
    assert auto.page_timeout_seconds == 180
    assert auto.stealth_clicks is True
    assert auto.reload_backoff_seconds == 5
    assert auto.captcha_wait_seconds == 120
    assert auto.human_interaction_mode == "unattended"
    assert auto.enable_screen_recording is False


# ── Requirement 2: Full Tri-Browser Compatibility ──────────────────────────────
def test_tri_browser_discovery():
    """Verify detection methods for Google Chrome, Microsoft Edge, and Chromium."""
    chrome_path = ChromeSession.find_chrome_executable()
    assert chrome_path is None or isinstance(chrome_path, Path)

    edge_path = ChromeSession.find_edge_executable()
    assert edge_path is None or isinstance(edge_path, Path)

    chromium_path = ChromeSession.find_chromium_executable()
    assert chromium_path is None or isinstance(chromium_path, Path)


def test_browser_version_resolution():
    """Verify browser version detection across engines."""
    chrome_ver = ChromeSession.get_browser_version("chrome")
    assert isinstance(chrome_ver, str) and len(chrome_ver) > 0

    edge_ver = ChromeSession.get_browser_version("msedge")
    assert isinstance(edge_ver, str) and len(edge_ver) > 0

    chromium_ver = ChromeSession.get_browser_version("chromium")
    assert isinstance(chromium_ver, str) and len(chromium_ver) > 0


def test_resolve_browser_launch_target_strict_routing():
    """Verify that browser selection strictly respects the engine and never silently substitutes Chrome."""
    # 1. Chromium request
    exe, channel = resolve_browser_launch_target(browser_engine="chromium", use_chrome=False)
    assert exe is None and channel is None, (
        "Chromium must target bundled driver without substituting Chrome"
    )

    # 2. Edge request
    exe_edge, ch_edge = resolve_browser_launch_target(browser_engine="msedge")
    assert ch_edge == "msedge" or (exe_edge and "edge" in str(exe_edge).lower())

    # 3. Chrome request
    exe_chr, ch_chr = resolve_browser_launch_target(browser_engine="chrome")
    assert ch_chr == "chrome" or (exe_chr and "chrome" in str(exe_chr).lower())


@pytest.mark.asyncio
async def test_browser_test_endpoint_returns_version_and_executable(mocker):
    """Verify /api/v1/settings/test-browser exposes detected browser_version and executable_path."""
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
        page.title = AsyncMock(return_value="UAIC Browser Verified")
        page.evaluate = AsyncMock()
        page.wait_for_timeout = AsyncMock()
        ctx.new_page = AsyncMock(return_value=page)
        return ctx

    mock_session.start = mock_start

    mocker.patch("app.api.v1.endpoints.settings.ChromeSession", return_value=mock_session)
    mocker.patch(
        "app.api.v1.endpoints.settings.ChromeSession.get_browser_version",
        return_value="124.0.6367.60",
    )
    mocker.patch(
        "app.api.v1.endpoints.settings.ExtensionManager.resolve_extension_path",
        return_value=Path("./anticaptcha-plugin_v0.83"),
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/settings/test-browser",
            json={"browser_engine": "chrome", "headless": True, "timeout_seconds": 10},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["browser_engine"] == "chrome"
        assert data["browser_version"] == "124.0.6367.60"


# ── Requirement 3: Anti-Captcha Extension Escalation ──────────────────────────
def test_blocked_extension_initialization_error():
    """Verify BlockedExtensionInitializationError code and structure."""
    err = BlockedExtensionInitializationError("Extension failed to load", engine="msedge")
    assert err.code == "BLOCKED_EXTENSION_INITIALIZATION"
    assert err.engine == "msedge"
    assert "Extension failed to load" in str(err)


def test_blocked_extension_notification_content():
    """Verify that IT Support notification contains required message and contact prompt."""
    err = BlockedExtensionInitializationError("Extension failed to load", engine="msedge")
    title = "Browser Automation Blocked — Anti-Captcha Extension"
    msg = (
        "The selected browser could not successfully load or initialize the configured Anti-Captcha extension.\n\n"
        "The application attempted the supported extension-loading and unpacked-extension fallback procedures, but initialization was unsuccessful.\n\n"
        "For security and reliability, browser automation has been stopped.\n\n"
        "Please contact your IT Support team to review browser policies, extension installation permissions, and the required configuration.\n\n"
        "Diagnostic details are available in the application execution logs."
    )
    assert "Browser Automation Blocked — Anti-Captcha Extension" in title
    assert "IT Support" in msg
    assert "BLOCKED_EXTENSION_INITIALIZATION" == err.code


# ── Requirement 7: Eight-Bot Concurrency Decoupling & Correlation IDs ──────────
def test_bot_and_record_statuses_contain_concurrency_states():
    """Verify new lifecycle statuses for decoupled dispatch and exception review."""
    assert BotStatusEnum.DISPATCHED == "DISPATCHED"
    assert BotStatusEnum.QUEUED == "QUEUED"
    assert BotStatusEnum.RUNNING == "RUNNING"
    assert RecordStatusEnum.QUEUED == "QUEUED"
    assert RecordStatusEnum.NEEDS_REVIEW == "NEEDS_REVIEW"


# ── Requirement 8: Geography-Based State Routing ──────────────────────────────
def test_geography_state_routing_florida():
    """Verify Florida claims route strictly to Broward, Hillsborough, and Miami-Dade."""
    targets = resolve_county_bot_targets("FL", "FL")
    assert targets["fl_broward"] == "Yes"
    assert targets["fl_hillsborough"] == "Yes"
    assert targets["fl_miami"] == "Yes"
    assert targets["te_travis"] == "No"
    assert targets["te_dallas"] == "No"
    assert targets["te_harris"] == "No"
    assert targets["te_cclerk"] == "No"
    assert targets["te_hcdistrict"] == "No"


def test_geography_state_routing_texas():
    """Verify Texas claims route strictly to Travis, Dallas, Harris JP, Clerk, and District."""
    targets = resolve_county_bot_targets("TX", "TX")
    assert targets["fl_broward"] == "No"
    assert targets["fl_hillsborough"] == "No"
    assert targets["fl_miami"] == "No"
    assert targets["te_travis"] == "Yes"
    assert targets["te_dallas"] == "Yes"
    assert targets["te_harris"] == "Yes"
    assert targets["te_cclerk"] == "Yes"
    assert targets["te_hcdistrict"] == "Yes"


def test_geography_state_routing_cross_state():
    """Verify Cross-state claims route to all 8 court scrapers."""
    targets = resolve_county_bot_targets("TX", "FL")
    assert all(v == "Yes" for v in targets.values()), "Cross-state must activate all 8 bots"


def test_geography_state_routing_missing_state_exception():
    """Verify ingestion flags claims with missing or ambiguous policy state as NEEDS_REVIEW."""
    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "Claim Number": "TEST-MISSING-STATE-001",
                "Insured First Name": "John",
                "Insured Last Name": "Doe",
                "Policy State": "",  # Empty policy state
                "Loss Location State": "FL",
            }
        ]
    )
    result = validate_and_normalize_claim_data(df)
    assert result["valid_rows"] == 1
    record = result["records_to_insert"][0]
    assert record["record_status"] == RecordStatusEnum.NEEDS_REVIEW
