"""Test pop-up handlers for session timeout and search criteria dialogs (TC-POP-001 through TC-POP-004)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.base import BaseCourtScraper


class MockScraper(BaseCourtScraper):
    async def search_by_party_name(self, first_name, last_name, page, **kwargs):
        return []


@pytest.mark.asyncio
async def test_tc_pop_001_dismiss_search_criteria_popup_when_visible():
    """TC-POP-001: _dismiss_search_criteria_popup clicks close button when visible."""
    scraper = MockScraper(county_name="Test County", base_url="https://example.com")
    page = MagicMock()

    mock_btn = MagicMock()
    mock_btn.count = AsyncMock(return_value=1)
    mock_btn.is_visible = AsyncMock(return_value=True)
    mock_btn.click = AsyncMock()
    mock_btn.first = mock_btn

    page.locator.return_value = mock_btn
    page.wait_for_timeout = AsyncMock()

    await scraper._dismiss_search_criteria_popup(page)
    mock_btn.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_tc_pop_002_dismiss_search_criteria_popup_noop_when_absent():
    """TC-POP-002: _dismiss_search_criteria_popup is a no-op when modal button absent."""
    scraper = MockScraper(county_name="Test County", base_url="https://example.com")
    page = MagicMock()

    mock_btn = MagicMock()
    mock_btn.count = AsyncMock(return_value=0)
    mock_btn.is_visible = AsyncMock(return_value=False)
    mock_btn.click = AsyncMock()
    mock_btn.first = mock_btn

    page.locator.return_value = mock_btn
    page.wait_for_timeout = AsyncMock()

    await scraper._dismiss_search_criteria_popup(page)
    mock_btn.click.assert_not_awaited()


@pytest.mark.asyncio
async def test_tc_pop_003_dismiss_session_timeout_popup_when_visible():
    """TC-POP-003: _dismiss_session_timeout_popup clicks Continue button when visible."""
    scraper = MockScraper(county_name="Test County", base_url="https://example.com")
    page = MagicMock()

    mock_btn = MagicMock()
    mock_btn.count = AsyncMock(return_value=1)
    mock_btn.is_visible = AsyncMock(return_value=True)
    mock_btn.click = AsyncMock()
    mock_btn.first = mock_btn

    page.locator.return_value = mock_btn
    page.wait_for_timeout = AsyncMock()

    await scraper._dismiss_session_timeout_popup(page)
    mock_btn.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_tc_pop_004_dismiss_session_timeout_popup_noop_when_absent():
    """TC-POP-004: _dismiss_session_timeout_popup is a no-op when timeout modal absent."""
    scraper = MockScraper(county_name="Test County", base_url="https://example.com")
    page = MagicMock()

    mock_btn = MagicMock()
    mock_btn.count = AsyncMock(return_value=0)
    mock_btn.is_visible = AsyncMock(return_value=False)
    mock_btn.click = AsyncMock()
    mock_btn.first = mock_btn

    page.locator.return_value = mock_btn
    page.wait_for_timeout = AsyncMock()

    await scraper._dismiss_session_timeout_popup(page)
    mock_btn.click.assert_not_awaited()
