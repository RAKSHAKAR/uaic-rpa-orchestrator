"""Test Scraper CAPTCHA behavior (TC-CAP-001 through TC-CAP-007).

Validates that scrapers report unresolved CAPTCHA attempts as failures, while the
base class detects a resolved challenge within its configured deadline.
"""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import BaseCourtScraper, CaptchaResolutionError
from app.automation.florida import BrowardScraper
from app.automation.texas import DallasScraper, HarrisJPScraper, TravisScraper


def _build_mock_page():
    """Builds a Playwright Page mock suitable for form-filling stages."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="")
    page.evaluate = AsyncMock(return_value=None)
    page.frames = []

    mock_locator = MagicMock()
    mock_locator.first = mock_locator
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.is_visible = AsyncMock(return_value=True)
    mock_locator.wait_for = AsyncMock()
    mock_locator.fill = AsyncMock()
    mock_locator.click = AsyncMock()
    mock_locator.all_inner_texts = AsyncMock(return_value=[])

    page.locator.return_value = mock_locator
    return page


@pytest.mark.asyncio
async def test_tc_cap_001_broward_captcha_timeout_raises():
    """TC-CAP-001: Broward reports an exhausted CAPTCHA attempt."""
    scraper = BrowardScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        with pytest.raises(CaptchaResolutionError):
            await scraper.search_by_party_name("John", "Doe", page)


@pytest.mark.asyncio
async def test_tc_cap_002_travis_captcha_timeout_raises():
    """TC-CAP-002: Travis reports an exhausted CAPTCHA attempt."""
    scraper = TravisScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        with pytest.raises(CaptchaResolutionError):
            await scraper.search_by_party_name("Jane", "Smith", page)


@pytest.mark.asyncio
async def test_tc_cap_003_dallas_captcha_timeout_raises():
    """TC-CAP-003: Dallas reports an exhausted CAPTCHA attempt."""
    scraper = DallasScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        with pytest.raises(CaptchaResolutionError):
            await scraper.search_by_party_name("Alice", "Johnson", page)


@pytest.mark.asyncio
async def test_tc_cap_004_harris_jp_captcha_timeout_raises():
    """TC-CAP-004: Harris JP reports an exhausted CAPTCHA attempt."""
    scraper = HarrisJPScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        with pytest.raises(CaptchaResolutionError):
            await scraper.search_by_party_name("Bob", "Williams", page)


def test_tc_cap_005_broward_redundant_still_solving_removed():
    """TC-CAP-005: Broward source does not contain redundant 'still_solving' loop."""
    src = inspect.getsource(BrowardScraper)
    assert "while still_solving" not in src


@pytest.mark.asyncio
async def test_tc_cap_006_base_captcha_no_challenge_returns_true():
    """TC-CAP-006: BaseCourtScraper.detect_and_handle_captcha returns True when no challenge exists."""
    class SimpleScraper(BaseCourtScraper):
        async def search_by_party_name(self, first_name, last_name, page, **kwargs):
            return []

    scraper = SimpleScraper(county_name="Mock County", base_url="https://example.com")
    page = MagicMock()
    page.frames = []
    page.evaluate = AsyncMock(return_value=None)

    mock_locator = MagicMock()
    mock_locator.count = AsyncMock(return_value=0)
    page.locator.return_value = mock_locator

    result = await scraper.detect_and_handle_captcha(page, wait_seconds=1)
    assert result is True


@pytest.mark.asyncio
async def test_tc_cap_007_base_captcha_unsolved_timeout_returns_false():
    """TC-CAP-007: BaseCourtScraper.detect_and_handle_captcha returns False when challenge never resolves."""
    class SimpleScraper(BaseCourtScraper):
        async def search_by_party_name(self, first_name, last_name, page, **kwargs):
            return []

    scraper = SimpleScraper(county_name="Mock County", base_url="https://example.com")
    page = MagicMock()

    # Create a mock frame indicating reCAPTCHA challenge
    mock_frame = MagicMock()
    mock_frame.url = "https://www.google.com/recaptcha/api2/anchor"
    page.frames = [mock_frame]

    # Evaluate returns recaptcha challenge present but never solved
    async def mock_eval(script):
        if "g-recaptcha-response" in script:
            return ""  # Empty token, unsolved
        if "antigate_solver" in script:
            return "in_process"
        return "recaptcha"

    page.evaluate = AsyncMock(side_effect=mock_eval)
    page.wait_for_timeout = AsyncMock()

    result = await scraper.detect_and_handle_captcha(page, wait_seconds=1)
    assert result is False


@pytest.mark.asyncio
async def test_tc_cap_008_dismiss_captcha_challenge_popup():
    """TC-CAP-008: BaseCourtScraper.dismiss_captcha_challenge_popup simulates outside click and Escape."""
    class SimpleScraper(BaseCourtScraper):
        async def search_by_party_name(self, first_name, last_name, page, **kwargs):
            return []

    scraper = SimpleScraper(county_name="Mock County", base_url="https://example.com")
    page = MagicMock()
    page.mouse = MagicMock()
    page.mouse.click = AsyncMock()
    page.keyboard = MagicMock()
    page.keyboard.press = AsyncMock()
    page.evaluate = AsyncMock()
    page.wait_for_timeout = AsyncMock()

    await scraper.dismiss_captcha_challenge_popup(page)

    page.mouse.click.assert_awaited_once_with(50, 50)
    page.keyboard.press.assert_awaited_once_with("Escape")
    assert page.evaluate.await_count >= 1
