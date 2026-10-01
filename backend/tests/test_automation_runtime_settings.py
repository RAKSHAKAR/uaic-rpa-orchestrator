"""Focused coverage for runtime settings applied by the browser automation layer."""

import asyncio
from time import perf_counter
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.base import BaseCourtScraper, PortalSearchError
from app.automation.browser_manager import (
    BrowserManager,
    CaptchaManager,
    ChromeSession,
    ExtensionManager,
    TabManager,
)
from app.automation.session_runner import SingleSessionBrowserRunner
from app.schemas.settings import AutomationSettings


class _SearchScraper(BaseCourtScraper):
    def __init__(self):
        super().__init__(
            county_name="Test County",
            base_url="https://example.test/search",
            max_attempts=2,
            reload_backoff_seconds=0,
        )
        self.fail = False
        self.search_calls = 0

    async def search_by_party_name(self, first_name, last_name, page, **kwargs):
        self.search_calls += 1
        if self.fail:
            raise ValueError("search form failed")
        return []


@pytest.mark.asyncio
async def test_failed_search_is_not_recorded_as_verified_empty_result():
    scraper = _SearchScraper()
    scraper.fail = True
    scraper.detect_security_block = AsyncMock(return_value=(False, "", 0))
    page = MagicMock()
    page.reload = AsyncMock()

    with pytest.raises(PortalSearchError, match="after 2 attempts"):
        await scraper.search_on_page(page, "Jane", "Doe")

    assert scraper.search_calls == 2
    page.reload.assert_awaited_once()

    scraper.fail = False
    assert await scraper.search_on_page(page, "Jane", "Doe") == []


@pytest.mark.asyncio
async def test_captcha_returns_as_soon_as_token_is_verified():
    scraper = _SearchScraper()
    frame = MagicMock()
    frame.url = "https://www.google.com/recaptcha/api2/anchor"
    frame.locator.return_value.count = AsyncMock(return_value=0)
    frame.evaluate = AsyncMock(return_value=False)
    page = MagicMock()
    page.frames = [frame]
    page.evaluate = AsyncMock(side_effect=lambda script: "g-recaptcha-response" in script)
    page.mouse.click = AsyncMock()
    page.keyboard.press = AsyncMock()
    page.wait_for_timeout = AsyncMock()

    started = perf_counter()
    assert await scraper.detect_and_handle_captcha(page, wait_seconds=2) is True
    assert perf_counter() - started < 1


@pytest.mark.asyncio
async def test_captcha_deadline_caps_all_detection_and_polling_work():
    scraper = _SearchScraper()
    frame = MagicMock()
    frame.url = "https://www.google.com/recaptcha/api2/anchor"
    frame.locator.return_value.count = AsyncMock(return_value=0)
    frame.evaluate = AsyncMock(return_value=False)
    page = MagicMock()
    page.frames = [frame]
    page.evaluate = AsyncMock(return_value=False)

    started = perf_counter()
    assert await scraper.detect_and_handle_captcha(page, wait_seconds=0.2) is False
    assert perf_counter() - started < 0.7


@pytest.mark.asyncio
async def test_legacy_captcha_manager_obeys_deadline_without_post_solve_delay():
    manager = CaptchaManager(timeout_seconds=120, poll_interval_ms=500)
    page = MagicMock()
    page.evaluate = AsyncMock(side_effect=[True, "SOLVED"])
    started = perf_counter()
    assert await manager.detect_and_solve(page) is True
    assert perf_counter() - started < 0.5

    slow_page = MagicMock()

    async def slow_detection(_script):
        await asyncio.sleep(1)
        return True

    slow_page.evaluate = AsyncMock(side_effect=slow_detection)
    started = perf_counter()
    assert await manager.detect_and_solve(slow_page, wait_seconds=0.05) is False
    assert perf_counter() - started < 0.3


@pytest.mark.asyncio
async def test_tab_managers_use_configured_timeout_and_portal_url():
    page = MagicMock()
    page.is_closed.return_value = False
    page.bring_to_front = AsyncMock()
    page.goto = AsyncMock()
    context = MagicMock()
    context.pages = [page]

    manager = TabManager(context, timeout_ms=180_000)
    await manager.get_or_create_tab("custom", "https://example.test/custom")
    page.set_default_navigation_timeout.assert_called_with(180_000)
    page.goto.assert_awaited_once_with(
        "https://example.test/custom", wait_until="domcontentloaded", timeout=180_000
    )

    page.goto.reset_mock()
    runner = SingleSessionBrowserRunner(timeout_ms=180_000)
    runner.context = context
    await runner.get_or_create_tab("custom", "https://example.test/custom")
    page.set_default_navigation_timeout.assert_called_with(180_000)
    page.goto.assert_awaited_once_with(
        "https://example.test/custom", wait_until="domcontentloaded", timeout=180_000
    )


@pytest.mark.asyncio
async def test_explicit_missing_browser_profile_fails_instead_of_using_default(tmp_path):
    runner = SingleSessionBrowserRunner(
        user_data_dir=str(tmp_path / "missing-profile"),
    )
    with pytest.raises(ValueError, match="Configured Chrome User Data Directory"):
        await runner.__aenter__()


def test_extension_runtime_payload_matches_all_user_toggles():
    cfg = AutomationSettings(
        anticaptcha_enabled=False,
        anticaptcha_auto_submit=True,
        anticaptcha_play_sounds=True,
        anticaptcha_solve_recaptcha2=False,
        anticaptcha_solve_invisible=False,
        anticaptcha_solve_recaptcha3=False,
        anticaptcha_recaptcha3_score=0.7,
        anticaptcha_solve_hcaptcha=False,
        anticaptcha_solve_turnstile=False,
        anticaptcha_solve_funcaptcha=False,
        anticaptcha_solve_geetest=False,
    )
    payload = ExtensionManager.runtime_config("  example_key  ", cfg)
    assert payload["account_key"] == "example_key"
    assert payload["enable"] is False
    assert payload["auto_submit_form"] is True
    assert payload["play_sounds"] is True
    assert payload["solve_recaptcha2"] is False
    assert payload["solve_invisible_recaptcha"] is False
    assert payload["solve_recaptcha3"] is False
    assert payload["recaptcha3_score"] == 0.7
    assert payload["solve_hcaptcha"] is False
    assert payload["solve_turnstile"] is False
    assert payload["solve_funcaptcha"] is False
    assert payload["solve_geetest"] is False


def test_browser_manager_passes_settings_to_session_and_managers():
    cfg = AutomationSettings(
        captcha_wait_seconds=120,
        page_timeout_seconds=180,
        anticaptcha_api_key="configured_key",
        anticaptcha_enabled=False,
    )
    manager = BrowserManager(auto_cfg=cfg, anticaptcha_api_key="stale_key")
    assert manager.session.auto_cfg is cfg
    assert manager.session.anticaptcha_api_key == "configured_key"
    assert manager.captcha_manager.timeout_seconds == 120
    assert manager.timeout_ms == 180_000


def test_profile_preflight_preserves_existing_plugin_preferences_without_settings(tmp_path, mocker):
    extension_dir = tmp_path / "extension"
    config_file = extension_dir / "js" / "config_ac_api_key.js"
    config_file.parent.mkdir(parents=True)
    config_file.write_text(
        "var antiCapApiKey = 'keep_key';\nvar solve_turnstile = false;\n",
        encoding="utf-8",
    )
    (extension_dir / "manifest.json").write_text("{}", encoding="utf-8")
    profile_dir = tmp_path / "profile"
    mocker.patch.object(ChromeSession, "get_persistent_profile_dir", return_value=profile_dir)
    mocker.patch.object(ChromeSession, "find_default_chrome_user_data_dir", return_value=None)

    ChromeSession.configure_and_pin_profile(
        profile_dir=profile_dir,
        api_key="keep_key",
        extension_path=extension_dir,
    )
    assert config_file.read_text(encoding="utf-8") == (
        "var antiCapApiKey = 'keep_key';\nvar solve_turnstile = false;\n"
    )

    ChromeSession.configure_and_pin_profile(
        profile_dir=profile_dir,
        api_key="keep_key",
        extension_path=extension_dir,
        auto_cfg=AutomationSettings(anticaptcha_enabled=False, anticaptcha_solve_turnstile=False),
    )
    assert "enable: false" in config_file.read_text(encoding="utf-8")
    assert "solve_turnstile: false" in config_file.read_text(encoding="utf-8")
