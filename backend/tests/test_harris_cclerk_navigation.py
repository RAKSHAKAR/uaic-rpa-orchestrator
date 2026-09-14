"""Test Harris County Clerk navigation behavior (TC-HCC-001 through TC-HCC-003)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.texas import HarrisCountyClerkScraper


@pytest.mark.asyncio
async def test_tc_hcc_001_courts_nav_hover():
    """TC-HCC-001: COURTS nav menu is hovered when form is not yet visible."""
    scraper = HarrisCountyClerkScraper()
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()

    mock_form = MagicMock()
    mock_form.count = AsyncMock(return_value=0)
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=False)
    mock_form.wait_for = AsyncMock()

    mock_courts = MagicMock()
    mock_courts.count = AsyncMock(return_value=1)
    mock_courts.first = mock_courts
    mock_courts.hover = AsyncMock()

    mock_civil = MagicMock()
    mock_civil.count = AsyncMock(return_value=1)
    mock_civil.first = mock_civil
    mock_civil.click = AsyncMock()

    def locator_side_effect(selector):
        if "txtLastName" in selector:
            return mock_form
        if "COURTS" in selector:
            return mock_courts
        if "County Civil" in selector:
            return mock_civil
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper._navigate_to_county_civil(page)
    mock_courts.hover.assert_awaited_once()


@pytest.mark.asyncio
async def test_tc_hcc_002_county_civil_link_clicked():
    """TC-HCC-002: County Civil link is clicked after hover."""
    scraper = HarrisCountyClerkScraper()
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()

    mock_form = MagicMock()
    mock_form.count = AsyncMock(return_value=0)
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=False)
    mock_form.wait_for = AsyncMock()

    mock_courts = MagicMock()
    mock_courts.count = AsyncMock(return_value=1)
    mock_courts.first = mock_courts
    mock_courts.hover = AsyncMock()

    mock_civil = MagicMock()
    mock_civil.count = AsyncMock(return_value=1)
    mock_civil.first = mock_civil
    mock_civil.click = AsyncMock()

    def locator_side_effect(selector):
        if "txtLastName" in selector:
            return mock_form
        if "COURTS" in selector:
            return mock_courts
        if "County Civil" in selector:
            return mock_civil
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper._navigate_to_county_civil(page)
    mock_civil.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_tc_hcc_003_form_wait_for_visible():
    """TC-HCC-003: Search form wait_for is called ensuring form is ready before filling."""
    scraper = HarrisCountyClerkScraper()
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()

    mock_form = MagicMock()
    mock_form.count = AsyncMock(side_effect=[0, 1])
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=False)
    mock_form.wait_for = AsyncMock()

    mock_courts = MagicMock()
    mock_courts.count = AsyncMock(return_value=1)
    mock_courts.first = mock_courts
    mock_courts.hover = AsyncMock()

    mock_civil = MagicMock()
    mock_civil.count = AsyncMock(return_value=1)
    mock_civil.first = mock_civil
    mock_civil.click = AsyncMock()

    def locator_side_effect(selector):
        if "txtLastName" in selector:
            return mock_form
        if "COURTS" in selector:
            return mock_courts
        if "County Civil" in selector:
            return mock_civil
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper._navigate_to_county_civil(page)
    mock_form.wait_for.assert_awaited_once_with(state="visible", timeout=15000)
