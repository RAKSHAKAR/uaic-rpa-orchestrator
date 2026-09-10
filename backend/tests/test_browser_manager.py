"""Automated tests for modern Python 3.14 browser automation architecture.

Covers:
- CountySiteAdapter Protocol runtime verification
- ExtensionManager path resolution & API key synchronization
- CaptchaManager condition-based detection & polling
- ChromeSession executable resolution & options
- TabManager page reuse and lifecycle
- SiteAutomationManager registration and adapter dispatch
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.browser_manager import (
    CaptchaManager,
    ChromeSession,
    CountySiteAdapter,
    ExtensionManager,
    SiteAutomationManager,
    TabManager,
)


class DummyCountyAdapter:
    def __init__(self):
        self.county_name = "Test County"
        self.base_url = "https://test.court.gov"

    async def search(self, first_name, last_name, page, date_of_loss=None, **kwargs):
        return [{"CaseNumber": "12345", "CaseStyle": f"{last_name}, {first_name}"}]

    async def extract_results(self, page, **kwargs):
        return []

    async def cleanup(self, page, **kwargs):
        pass


def test_county_site_adapter_protocol():
    """Verify CountySiteAdapter protocol compliance."""
    adapter = DummyCountyAdapter()
    assert isinstance(adapter, CountySiteAdapter)
    assert adapter.county_name == "Test County"
    assert adapter.base_url == "https://test.court.gov"


def test_extension_manager_resolution_and_sync(tmp_path):
    """Verify ExtensionManager discovers extension and writes config with full auto-seeding."""
    dummy_ext = tmp_path / "dummy_extension"
    dummy_ext.mkdir()
    (dummy_ext / "manifest.json").write_text('{"name": "AntiCaptcha"}', encoding="utf-8")

    resolved = ExtensionManager.resolve_extension_path(dummy_ext)
    assert resolved == dummy_ext.resolve()

    sync_success = ExtensionManager.sync_api_key(dummy_ext, "test_api_key_12345")
    assert sync_success is True

    config_file = dummy_ext / "js" / "config_ac_api_key.js"
    assert config_file.exists()
    text = config_file.read_text(encoding="utf-8")
    assert "test_api_key_12345" in text
    assert "solve_turnstile" in text
    assert "solve_recaptcha2" in text
    assert "initAntiCaptchaStorage" in text


@pytest.mark.asyncio
async def test_profile_preferences_pinned_extensions(tmp_path, mocker):
    """Verify ChromeSession writes pinned_extensions and developer_mode to Default/Preferences."""
    import json
    session = ChromeSession(
        user_data_dir=str(tmp_path),
        browser_engine="chromium",
    )
    mock_context = MagicMock()
    mock_context.service_workers = []
    mock_context.background_pages = []

    mock_chromium = MagicMock()
    mock_chromium.launch_persistent_context = AsyncMock(return_value=mock_context)

    mock_pw_instance = MagicMock()
    mock_pw_instance.chromium = mock_chromium

    mocker.patch(
        "app.automation.browser_manager.async_playwright",
        return_value=MagicMock(start=AsyncMock(return_value=mock_pw_instance))
    )

    await session.start()
    pref_file = tmp_path / "Default" / "Preferences"
    assert pref_file.exists()
    prefs = json.loads(pref_file.read_text(encoding="utf-8"))
    assert prefs["extensions"]["developer_mode"] is True
    assert "gcpdbjbmekkdlkpldjgffhmapgpdlcpj" in prefs["extensions"]["pinned_extensions"]



def test_chrome_session_executable_discovery():
    """Verify ChromeSession locates Chrome or returns None cleanly."""
    exe = ChromeSession.find_chrome_executable()
    # On Windows dev machine with Chrome installed, it should find chrome.exe
    if exe:
        assert isinstance(exe, Path)
        assert exe.name.lower() == "chrome.exe"
        assert exe.exists()


def test_chrome_session_engine_arguments():
    """Verify ChromeSession initializes browser engines (chromium, msedge, chrome) properly."""
    session_default = ChromeSession()
    assert session_default.browser_engine == "chromium"

    session_edge = ChromeSession(browser_engine="msedge")
    assert session_edge.browser_engine == "msedge"

    session_chrome = ChromeSession(browser_engine="chrome", chrome_binary_path=r"C:\Custom\chrome.exe")
    assert session_chrome.browser_engine == "chrome"
    assert session_chrome.chrome_binary_path == r"C:\Custom\chrome.exe"


@pytest.mark.asyncio
async def test_modern_headless_extension_args(tmp_path, mocker):
    """Verify ChromeSession configures headless=False and --headless=new when loading extensions headless."""
    dummy_ext = tmp_path / "ext"
    dummy_ext.mkdir()
    (dummy_ext / "manifest.json").write_text('{"name": "test"}', encoding="utf-8")

    session = ChromeSession(
        headless=True,
        extension_path=dummy_ext,
        browser_engine="msedge",
    )

    # Mock playwright launch
    mock_context = MagicMock()
    mock_context.service_workers = []
    mock_context.background_pages = []

    mock_chromium = MagicMock()
    mock_chromium.launch_persistent_context = AsyncMock(return_value=mock_context)

    mock_pw_instance = MagicMock()
    mock_pw_instance.chromium = mock_chromium

    mocker.patch(
        "app.automation.browser_manager.async_playwright",
        return_value=MagicMock(start=AsyncMock(return_value=mock_pw_instance))
    )

    ctx = await session.start()
    assert ctx == mock_context

    call_kwargs = mock_chromium.launch_persistent_context.call_args.kwargs
    # In Playwright, to load extensions headless, context headless must be False with --headless=new in args
    assert call_kwargs["headless"] is False
    assert "--headless=new" in call_kwargs["args"]
    assert call_kwargs["channel"] == "msedge"



@pytest.mark.asyncio
async def test_captcha_manager_condition_based_solving():
    """Verify CaptchaManager polls DOM condition and returns immediately when resolved."""
    cm = CaptchaManager(timeout_seconds=5, poll_interval_ms=100)
    mock_page = MagicMock()

    # First check indicates challenge present, second evaluate indicates SOLVED
    eval_side_effects = [
        True,       # _is_challenge_present: True
        "SOLVED",   # evaluate in polling loop: 'SOLVED'
    ]
    mock_page.evaluate = AsyncMock(side_effect=eval_side_effects)
    mock_page.wait_for_timeout = AsyncMock()

    solved = await cm.detect_and_solve(mock_page)
    assert solved is True
    assert mock_page.evaluate.call_count == 2


@pytest.mark.asyncio
async def test_captcha_manager_no_challenge_fast_path():
    """Verify CaptchaManager returns immediately if no challenge exists."""
    cm = CaptchaManager(timeout_seconds=5)
    mock_page = MagicMock()
    mock_page.evaluate = AsyncMock(return_value=False)

    solved = await cm.detect_and_solve(mock_page)
    assert solved is True
    assert mock_page.evaluate.call_count == 1


@pytest.mark.asyncio
async def test_tab_manager_lifecycle():
    """Verify TabManager creates, maps, and closes portal tabs."""
    mock_context = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.is_closed = MagicMock(return_value=False)
    mock_page1.bring_to_front = AsyncMock()
    mock_page1.goto = AsyncMock()
    mock_page1.close = AsyncMock()

    mock_context.pages = [mock_page1]
    mock_context.new_page = AsyncMock(return_value=mock_page1)

    tm = TabManager(mock_context)
    page = await tm.get_or_create_tab("broward", "https://broward.court.gov")
    assert page == mock_page1
    assert "broward" in tm.tabs

    await tm.close_all()
    assert len(tm.tabs) == 0


@pytest.mark.asyncio
async def test_site_automation_manager_dispatch():
    """Verify SiteAutomationManager registers adapters and routes searches."""
    mock_bm = MagicMock()
    mock_tm = MagicMock()
    mock_page = MagicMock()
    mock_tm.get_or_create_tab = AsyncMock(return_value=mock_page)
    mock_bm.tab_manager = mock_tm

    sm = SiteAutomationManager(mock_bm)
    adapter = DummyCountyAdapter()
    sm.register_adapter("test_portal", adapter)

    results = await sm.run_portal_search("test_portal", "John", "Doe")
    assert len(results) == 1
    assert results[0]["CaseNumber"] == "12345"
    assert results[0]["CaseStyle"] == "Doe, John"


@pytest.mark.asyncio
async def test_chrome_profile_seeding_and_args(tmp_path, mocker):
    """Verify ChromeSession seeds profile from user Chrome directory and suppresses --load-extension."""
    mock_source = tmp_path / "mock_chrome_source"
    mock_source_default = mock_source / "Default"
    mock_source_default.mkdir(parents=True)
    (mock_source / "Local State").write_text('{"local": true}', encoding="utf-8")
    (mock_source_default / "Preferences").write_text('{"pref": true}', encoding="utf-8")
    (mock_source_default / "Secure Preferences").write_text('{"secure": true}', encoding="utf-8")

    mocker.patch.object(ChromeSession, "find_default_chrome_user_data_dir", return_value=mock_source)

    captured_kwargs = {}

    mock_context = MagicMock()
    mock_context.service_workers = [MagicMock(url="chrome-extension://gcpdbjbmekkdlkpldjgffhmapgpdlcpj/js/service_worker.js")]
    mock_context.background_pages = []
    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value=True)
    mock_page.close = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)

    mock_chromium = MagicMock()
    async def mock_launch(**kwargs):
        nonlocal captured_kwargs
        captured_kwargs = kwargs
        return mock_context

    mock_chromium.launch_persistent_context = mock_launch
    mock_pw_instance = MagicMock(chromium=mock_chromium)

    mocker.patch(
        "app.automation.browser_manager.async_playwright",
        return_value=MagicMock(start=AsyncMock(return_value=mock_pw_instance)),
    )

    session = ChromeSession(
        browser_engine="chrome",
        extension_path=Path(r".\anticaptcha-plugin_v0.83"),
    )
    await session.start()

    # Verify profile was seeded with user data files
    assert (session.profile_to_use / "Local State").exists()
    assert (session.profile_to_use / "Default" / "Secure Preferences").exists()

    # Verify --load-extension WAS passed in args when extension is configured
    passed_args = captured_kwargs.get("args", [])
    assert any(a.startswith("--load-extension=") for a in passed_args)
    assert any(a.startswith("--disable-extensions-except=") for a in passed_args)


@pytest.mark.asyncio
async def test_engine_specific_user_agent_injection(mocker):
    """Verify ChromeSession injects engine-tailored User-Agent string."""
    captured_kwargs = {}

    mock_context = MagicMock(service_workers=[], background_pages=[])
    mock_chromium = MagicMock()
    async def mock_launch(**kwargs):
        nonlocal captured_kwargs
        captured_kwargs = kwargs
        return mock_context

    mock_chromium.launch_persistent_context = mock_launch
    mock_pw_instance = MagicMock(chromium=mock_chromium)

    mocker.patch(
        "app.automation.browser_manager.async_playwright",
        return_value=MagicMock(start=AsyncMock(return_value=mock_pw_instance)),
    )

    # Test msedge
    session_edge = ChromeSession(browser_engine="msedge")
    await session_edge.start()
    assert "Edg/" in captured_kwargs["user_agent"]

    # Test chromium
    session_cr = ChromeSession(browser_engine="chromium")
    await session_cr.start()
    assert "Edg/" not in captured_kwargs["user_agent"]
    assert "Chrome/124" in captured_kwargs["user_agent"]


def test_is_extension_configured(tmp_path):
    """Verify ExtensionManager.is_extension_configured detects configured vs unconfigured status."""
    ext_dir = tmp_path / "extension"
    ext_dir.mkdir()
    js_dir = ext_dir / "js"
    js_dir.mkdir()

    # Case 1: No file
    assert ExtensionManager.is_extension_configured(ext_dir, "test_api_key_123") is False

    # Case 2: Configured with matching key
    config_file = js_dir / "config_ac_api_key.js"
    config_file.write_text("var antiCapApiKey = 'test_api_key_123'; solve_turnstile = true;", encoding="utf-8")
    assert ExtensionManager.is_extension_configured(ext_dir, "test_api_key_123") is True

    # Case 3: Different key
    assert ExtensionManager.is_extension_configured(ext_dir, "other_key_999") is False


@pytest.mark.asyncio
async def test_edge_preferences_pinned_and_toolbar_flags(tmp_path, mocker):
    """Verify ChromeSession generates Edge toolbar pinning, migration flags, and suppression args."""
    import json

    captured_kwargs = {}
    mock_context = MagicMock(service_workers=[], background_pages=[])
    mock_chromium = MagicMock()
    async def mock_launch(**kwargs):
        nonlocal captured_kwargs
        captured_kwargs = kwargs
        return mock_context

    mock_chromium.launch_persistent_context = mock_launch
    mock_pw_instance = MagicMock(chromium=mock_chromium)

    mocker.patch(
        "app.automation.browser_manager.async_playwright",
        return_value=MagicMock(start=AsyncMock(return_value=mock_pw_instance)),
    )

    session = ChromeSession(
        browser_engine="msedge",
        user_data_dir=str(tmp_path),
    )
    await session.start()

    # Verify Preferences file written with Edge toolbar preferences
    pref_file = tmp_path / "Default" / "Preferences"
    assert pref_file.exists()
    prefs = json.loads(pref_file.read_text(encoding="utf-8"))

    # Extension pinned & migration set
    assert "gcpdbjbmekkdlkpldjgffhmapgpdlcpj" in prefs["extensions"]["pinned_extensions"]
    assert prefs["extensions"]["pinned_extension_migration"] is True
    assert prefs["browser"]["show_extensions_toolbar_menu"] is True

    # Launch args contain first-run suppression
    args = captured_kwargs.get("args", [])
    assert "--no-first-run" in args
    assert "--disable-features=msFirstRunExperience,msEdgeWelcomePage" in args


@pytest.mark.asyncio
async def test_extension_configuration_skips_when_already_configured(mocker):
    """Verify that when extension is already configured, ChromeSession skips opening popup_v3.html."""
    mock_worker = MagicMock()
    mock_worker.url = "chrome-extension://gcpdbjbmekkdlkpldjgffhmapgpdlcpj/worker.js"
    mock_worker.evaluate = AsyncMock(return_value={"account_key": "my_api_key", "enable": True})

    mock_context = MagicMock(service_workers=[mock_worker], background_pages=[])
    mock_context.new_page = AsyncMock()

    mock_chromium = MagicMock()
    mock_chromium.launch_persistent_context = AsyncMock(return_value=mock_context)
    mock_pw_instance = MagicMock(chromium=mock_chromium)

    mocker.patch(
        "app.automation.browser_manager.async_playwright",
        return_value=MagicMock(start=AsyncMock(return_value=mock_pw_instance)),
    )

    session = ChromeSession(
        browser_engine="msedge",
        extension_path=Path(r".\anticaptcha-plugin_v0.83"),
        anticaptcha_api_key="my_api_key",
    )
    await session.start()

    assert session.extension_loaded is True
    assert session.service_worker_active is True
    # new_page was NEVER called because popup setup was skipped!
    mock_context.new_page.assert_not_called()

