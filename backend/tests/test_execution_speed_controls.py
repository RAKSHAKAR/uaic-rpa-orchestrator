from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import BaseCourtScraper, PortalSearchError
from app.automation.session_runner import SingleSessionBrowserRunner
from app.schemas.settings import AutomationSettings
from app.services.settings_service import get_default_settings


class DummyScraper(BaseCourtScraper):
    async def search_by_party_name(self, first_name, last_name, date_of_loss=None):
        return []

    async def search_on_page(self, page, first_name, last_name, date_of_loss=None):
        return []


@pytest.mark.asyncio
async def test_biometric_fill_turbo_mode_uses_instant_fill():
    """Verify that typing_speed_mode='turbo' and typing_delay_ms=0 invokes locator.fill directly (~2ms)."""
    scraper = DummyScraper(
        county_name="TestCounty",
        base_url="https://test.court.local",
        typing_speed_mode="turbo",
        typing_delay_ms=0,
    )
    mock_locator = MagicMock()
    mock_locator.clear = AsyncMock()
    mock_locator.fill = AsyncMock()
    mock_locator.press_sequentially = AsyncMock()

    await scraper.biometric_fill(mock_locator, "John Doe")

    mock_locator.clear.assert_awaited_once()
    mock_locator.fill.assert_awaited_once_with("John Doe")
    mock_locator.press_sequentially.assert_not_called()


@pytest.mark.asyncio
async def test_biometric_fill_custom_delay_uses_press_sequentially():
    """Verify that typing_delay_ms > 0 invokes native locator.press_sequentially in a single call."""
    scraper = DummyScraper(
        county_name="TestCounty",
        base_url="https://test.court.local",
        typing_speed_mode="fast",
        typing_delay_ms=15,
    )
    mock_locator = MagicMock()
    mock_locator.clear = AsyncMock()
    mock_locator.fill = AsyncMock()
    mock_locator.press_sequentially = AsyncMock()

    await scraper.biometric_fill(mock_locator, "Jane Smith")

    mock_locator.clear.assert_awaited_once()
    mock_locator.press_sequentially.assert_awaited_once_with("Jane Smith", delay=15)
    mock_locator.fill.assert_not_called()


@pytest.mark.asyncio
async def test_biometric_click_snappy_mode():
    """Verify that stealth_clicks=False performs direct snappy locator.click()."""
    scraper = DummyScraper(
        county_name="TestCounty",
        base_url="https://test.court.local",
        stealth_clicks=False,
    )
    mock_page = MagicMock()
    mock_locator = MagicMock()
    mock_locator.click = AsyncMock()

    await scraper.biometric_click(mock_page, mock_locator)

    mock_locator.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_pace_action_applies_timeout():
    """Verify that pace_action calls page.wait_for_timeout with action_pacing_ms."""
    scraper = DummyScraper(
        county_name="TestCounty",
        base_url="https://test.court.local",
        action_pacing_ms=250,
    )
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    await scraper.pace_action(mock_page)

    mock_page.wait_for_timeout.assert_awaited_once_with(250)


@pytest.mark.asyncio
async def test_configured_action_pacing_applies_after_fill_and_click():
    """Both ordinary field entry and button clicks honor the configured delay."""
    scraper = DummyScraper(
        county_name="TestCounty",
        base_url="https://test.court.local",
        action_pacing_ms=275,
    )
    locator = MagicMock()
    locator.clear = AsyncMock()
    locator.fill = AsyncMock()
    locator.bounding_box = AsyncMock(return_value=None)
    locator.click = AsyncMock()
    page = MagicMock()
    page.wait_for_timeout = AsyncMock()

    with patch("asyncio.sleep", new_callable=AsyncMock) as sleep:
        await scraper.biometric_fill(locator, "Jane Smith")
        sleep.assert_awaited_once_with(0.275)

    await scraper.biometric_click(page, locator)
    page.wait_for_timeout.assert_awaited_once_with(275)
    locator.fill.assert_awaited_once_with("Jane Smith")
    locator.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_field_entry_raises_after_dom_fallback_fails():
    scraper = DummyScraper("TestCounty", "https://test.court.local", action_pacing_ms=0)
    locator = MagicMock()
    locator.clear = AsyncMock(side_effect=RuntimeError("field blocked"))
    locator.evaluate = AsyncMock(side_effect=RuntimeError("DOM blocked"))

    with pytest.raises(PortalSearchError, match="Field entry failed"):
        await scraper.biometric_fill(locator, "Jane Smith")

    locator.evaluate.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_click_raises_after_force_and_dom_fallbacks_fail():
    scraper = DummyScraper("TestCounty", "https://test.court.local", action_pacing_ms=0)
    page = MagicMock()
    locator = MagicMock()
    locator.bounding_box = AsyncMock(return_value=None)
    locator.click = AsyncMock(side_effect=RuntimeError("click blocked"))
    locator.evaluate = AsyncMock(side_effect=RuntimeError("DOM blocked"))

    with pytest.raises(PortalSearchError, match="Click failed"):
        await scraper.biometric_click(page, locator)

    assert locator.click.await_count == 2
    locator.evaluate.assert_awaited_once()


@pytest.mark.asyncio
async def test_offscreen_click_scrolls_then_uses_actionable_locator():
    """An attended viewport must not accept a mouse click below its visible area."""
    scraper = DummyScraper("TestCounty", "https://test.court.local", action_pacing_ms=0)
    page = MagicMock()
    page.viewport_size = {"width": 1200, "height": 900}
    page.mouse.move = AsyncMock()
    page.mouse.down = AsyncMock()
    page.mouse.up = AsyncMock()
    locator = MagicMock()
    locator.scroll_into_view_if_needed = AsyncMock()

    async def box_after_scroll():
        locator.scroll_into_view_if_needed.assert_awaited_once()
        return {"x": 100, "y": 969, "width": 120, "height": 30}

    locator.bounding_box = AsyncMock(side_effect=box_after_scroll)
    locator.click = AsyncMock()

    await scraper.biometric_click(page, locator)

    locator.click.assert_awaited_once_with()
    page.mouse.move.assert_not_awaited()
    page.mouse.down.assert_not_awaited()


def test_automation_settings_speed_schema():
    """Verify AutomationSettings has correct defaults for execution speed and typing dynamics."""
    settings = AutomationSettings()
    assert settings.typing_speed_mode == "turbo"
    assert settings.typing_delay_ms == 0
    assert settings.action_pacing_ms == 100
    assert settings.stealth_clicks is False
    assert settings.captcha_wait_seconds == 120  # Isolated and preserved


def test_system_settings_defaults_preserve_speed_controls():
    """Verify SystemSettings default initialization includes speed parameters."""
    sys_settings = get_default_settings()
    auto = sys_settings.automation
    assert isinstance(auto, AutomationSettings)
    assert auto.typing_speed_mode == "turbo"
    assert auto.typing_delay_ms == 0
    assert auto.action_pacing_ms == 100
    assert auto.stealth_clicks is False


def test_single_session_runner_stores_speed_parameters():
    """Verify SingleSessionBrowserRunner accepts and persists speed configuration."""
    runner = SingleSessionBrowserRunner(
        typing_speed_mode="fast",
        typing_delay_ms=25,
        action_pacing_ms=200,
        stealth_clicks=True,
    )
    assert runner.typing_speed_mode == "fast"
    assert runner.typing_delay_ms == 25
    assert runner.action_pacing_ms == 200
    assert runner.stealth_clicks is True
