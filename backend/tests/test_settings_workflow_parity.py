import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.browser_manager import ExtensionManager
from app.automation.session_runner import KNOWN_ANTICAPTCHA_IDS, SingleSessionBrowserRunner
from app.schemas.settings import AutomationSettings


def test_extension_manager_syncs_all_anticaptcha_settings():
    """Verify that sync_api_key writes all Anti-Captcha options to config_ac_api_key.js."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ext_dir = Path(tmpdir)
        js_dir = ext_dir / "js"
        js_dir.mkdir(parents=True, exist_ok=True)

        auto_cfg = AutomationSettings(
            anticaptcha_api_key="test_api_key_12345",
            anticaptcha_enabled=True,
            anticaptcha_auto_submit=True,
            anticaptcha_play_sounds=True,
            anticaptcha_solve_recaptcha2=False,
            anticaptcha_solve_invisible=True,
            anticaptcha_solve_recaptcha3=True,
            anticaptcha_recaptcha3_score=0.7,
            anticaptcha_solve_hcaptcha=False,
            anticaptcha_solve_turnstile=True,
            anticaptcha_solve_funcaptcha=False,
            anticaptcha_solve_geetest=True,
        )

        success = ExtensionManager.sync_api_key(ext_dir, auto_cfg.anticaptcha_api_key, auto_cfg)
        assert success is True

        config_file = js_dir / "config_ac_api_key.js"
        assert config_file.is_file()

        content = config_file.read_text(encoding="utf-8")
        assert "var antiCapApiKey = 'test_api_key_12345';" in content
        assert "var antiCapAutoSubmitForm = true;" in content
        assert "auto_submit_form: true" in content
        assert "play_sounds: true" in content
        assert "solve_recaptcha2: false" in content
        assert "solve_invisible_recaptcha: true" in content
        assert "solve_recaptcha3: true" in content
        assert "recaptcha3_score: 0.7" in content
        assert "solve_hcaptcha: false" in content
        assert "solve_turnstile: true" in content
        assert "solve_funcaptcha: false" in content
        assert "solve_geetest: true" in content


def test_single_session_browser_runner_receives_all_settings():
    """Verify that SingleSessionBrowserRunner captures engine, binary, and anticaptcha settings."""
    auto_cfg = AutomationSettings(
        browser_engine="chromium",
        chrome_binary_path="/custom/path/to/chrome.exe",
        anticaptcha_api_key="sync_key_999",
        stealth_clicks=True,
        typing_delay_ms=25,
        action_pacing_ms=200,
    )

    runner = SingleSessionBrowserRunner(
        headless=True,
        timeout_ms=30000,
        use_chrome=True,
        extension_dir="anticaptcha-plugin_v0.83",
        anticaptcha_api_key=auto_cfg.anticaptcha_api_key,
        anticaptcha_settings=auto_cfg,
        typing_delay_ms=auto_cfg.typing_delay_ms,
        action_pacing_ms=auto_cfg.action_pacing_ms,
        stealth_clicks=auto_cfg.stealth_clicks,
        browser_engine=auto_cfg.browser_engine,
        chrome_binary_path=auto_cfg.chrome_binary_path,
    )

    assert runner.browser_engine == "chromium"
    assert runner.chrome_binary_path == "/custom/path/to/chrome.exe"
    assert runner.anticaptcha_api_key == "sync_key_999"
    assert runner.stealth_clicks is True
    assert runner.typing_delay_ms == 25
    assert runner.action_pacing_ms == 200
    assert runner.anticaptcha_settings == auto_cfg


@pytest.mark.asyncio
async def test_single_session_tab_navigation_and_constants():
    """Verify that get_or_create_tab actively navigates to the portal URL and constants are defined."""
    assert "gcpdbjbmekkdlkpldjgffhmapgpdlcpj" in KNOWN_ANTICAPTCHA_IDS

    runner = SingleSessionBrowserRunner(headless=True, timeout_ms=30000)
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_page.is_closed.return_value = False
    mock_page.goto = AsyncMock()
    mock_page.bring_to_front = AsyncMock()
    mock_page.set_default_timeout = MagicMock()
    mock_context.pages = [mock_page]
    runner.context = mock_context

    page = await runner.get_or_create_tab("broward", "https://www.browardclerk.org/")
    assert page == mock_page
    mock_page.goto.assert_awaited_once_with(
        "https://www.browardclerk.org/",
        wait_until="domcontentloaded",
        timeout=30000,
    )
