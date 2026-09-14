"""Test Scraper CAPTCHA behavior (TC-CAP-001 through TC-CAP-007).

Validates that scrapers handle CAPTCHA timeouts gracefully (returning empty results
instead of raising fatal RuntimeErrors) and that the base class handles detection correctly.
"""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import BaseCourtScraper
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
async def test_tc_cap_001_broward_captcha_timeout_returns_empty():
    """TC-CAP-001: Broward returns [] on CAPTCHA timeout, does NOT raise RuntimeError."""
    scraper = BrowardScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        res = await scraper.search_by_party_name("John", "Doe", page)
        assert res == []


@pytest.mark.asyncio
async def test_tc_cap_002_travis_captcha_timeout_returns_empty():
    """TC-CAP-002: Travis returns [] on CAPTCHA timeout, does NOT raise RuntimeError."""
    scraper = TravisScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        res = await scraper.search_by_party_name("Jane", "Smith", page)
        assert res == []


@pytest.mark.asyncio
async def test_tc_cap_003_dallas_captcha_timeout_returns_empty():
    """TC-CAP-003: Dallas returns [] on CAPTCHA timeout, does NOT raise RuntimeError."""
    scraper = DallasScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        res = await scraper.search_by_party_name("Alice", "Johnson", page)
        assert res == []


@pytest.mark.asyncio
async def test_tc_cap_004_harris_jp_captcha_timeout_returns_empty():
    """TC-CAP-004: Harris JP returns [] on CAPTCHA timeout, does NOT raise RuntimeError."""
    scraper = HarrisJPScraper()
    page = _build_mock_page()

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = False
        res = await scraper.search_by_party_name("Bob", "Williams", page)
        assert res == []


def test_tc_cap_005_broward_redundant_still_solving_removed():
    """TC-CAP-005: Broward source does not contain redundant 'still_solving' loop."""
    src = inspect.getsource(BrowardScraper)
    assert "while still_solving" not in src
    assert "raise RuntimeError" not in src


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
