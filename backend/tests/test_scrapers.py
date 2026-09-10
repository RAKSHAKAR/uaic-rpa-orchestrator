"""Unit and integration tests for Florida and Texas court portal scrapers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import BaseCourtScraper
from app.automation.florida import BrowardScraper, HillsboroughScraper, MiamiDadeScraper
from app.automation.texas import (
    DallasScraper,
    HarrisCountyClerkScraper,
    HarrisDistrictClerkScraper,
    HarrisJPScraper,
    TravisScraper,
)

# ============================================================================
# 1. BaseCourtScraper Tests
# ============================================================================

class ConcreteCourtScraper(BaseCourtScraper):
    async def search_by_party_name(self, first_name, last_name, page, **kwargs):
        return []


def test_base_court_scraper_initialization():
    scraper = ConcreteCourtScraper(
        county_name="Test County",
        base_url="https://example.com/court",
        headless=True,
        max_attempts=3,
        timeout_ms=15000,
        captcha_wait_seconds=10,
    )
    assert scraper.county_name == "Test County"
    assert scraper.base_url == "https://example.com/court"
    assert scraper.headless is True
    assert scraper.max_attempts == 3
    assert scraper.timeout_ms == 15000
    assert scraper.captcha_wait_seconds == 10


@pytest.mark.asyncio
async def test_base_court_scraper_captcha_detection_none_found():
    scraper = ConcreteCourtScraper(county_name="Test County", base_url="https://example.com")
    mock_page = MagicMock()
    mock_locator = MagicMock()
    mock_locator.count = AsyncMock(return_value=0)
    mock_page.locator.return_value = mock_locator

    result = await scraper.detect_and_handle_captcha(mock_page, wait_seconds=1)
    assert result is True

    result = await scraper.detect_and_handle_captcha(mock_page, wait_seconds=1)
    assert result is True


# ============================================================================
# 2. Florida Scraper Tests
# ============================================================================

def test_miami_scraper_initialization():
    scraper = MiamiDadeScraper(
        username="test@test.com",
        password="SecretPassword123",
        requires_login=True,
    )
    assert scraper.county_name == "Miami-Dade County (FL)"
    assert "miamidadeclerk.gov" in scraper.base_url
    assert scraper.username == "test@test.com"
    assert scraper.password == "SecretPassword123"
    assert scraper.requires_login is True


@pytest.mark.asyncio
async def test_miami_scraper_empty_last_name():
    scraper = MiamiDadeScraper()
    mock_page = MagicMock()
    results = await scraper.search_by_party_name("Sergio", "", mock_page)
    assert results == []


@pytest.mark.asyncio
async def test_miami_scraper_card_view_extraction():
    """Simulates the exact Card View HTML text extracted in Frame 030 of the Florida recording."""
    scraper = MiamiDadeScraper(requires_login=False)

    card_text = """
    MIGUEL TOLEDO ET AL VS SERGIO GONZALEZ ET AL
    Local Case Number
    2026-111719-CC-26
    State Case Number
    132026CC11171901GE26
    Section
    SD 04 - South Dade 04
    Case Type
    EVR
    Filing Date
    08/21/2026
    Case Status
    OPEN
    """

    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.inner_text = AsyncMock(return_value="")

    # Search inputs
    mock_last_input = MagicMock()
    mock_last_input.count = AsyncMock(return_value=1)
    mock_last_input.first.wait_for = AsyncMock()
    mock_last_input.first.fill = AsyncMock()

    mock_first_input = MagicMock()
    mock_first_input.count = AsyncMock(return_value=1)
    mock_first_input.first.fill = AsyncMock()

    mock_date_from = MagicMock()
    mock_date_from.count = AsyncMock(return_value=1)
    mock_date_from.first.fill = AsyncMock()

    mock_date_to = MagicMock()
    mock_date_to.count = AsyncMock(return_value=1)
    mock_date_to.first.fill = AsyncMock()

    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.first.click = AsyncMock()

    # Cards locator
    mock_card = MagicMock()
    mock_card.inner_text = AsyncMock(return_value=card_text)
    mock_tds = MagicMock()
    mock_tds.count = AsyncMock(return_value=0)
    mock_card.locator.return_value = mock_tds

    mock_cards = MagicMock()
    mock_cards.count = AsyncMock(return_value=1)
    mock_cards.nth.return_value = mock_card

    def locator_side_effect(selector):
        if "LastName" in selector:
            return mock_last_input
        elif "FirstName" in selector:
            return mock_first_input
        elif "DateFrom" in selector:
            return mock_date_from
        elif "DateTo" in selector:
            return mock_date_to
        elif "Search" in selector or "SEARCH" in selector:
            return mock_search_btn
        elif "card" in selector or "grdResults" in selector:
            return mock_cards
        mock_generic = MagicMock()
        mock_generic.count = AsyncMock(return_value=0)
        return mock_generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):
        results = await scraper.search_by_party_name("SERGIO", "GONZALEZ", mock_page)

    assert len(results) == 1
    record = results[0]
    assert record["CaseNumber"] == "2026-111719-CC-26"
    assert "SERGIO GONZALEZ" in record["CaseStyle"]
    assert record["FilingDate"] == "08/21/2026"
    assert record["CaseStatus"] == "OPEN"
    assert record["CaseType"] == "EVR"
    assert record["Court"] == "SD 04 - South Dade 04"


def test_hillsborough_scraper_initialization():
    scraper = HillsboroughScraper()
    assert scraper.county_name == "Hillsborough County (FL)"
    assert "hillsclerk.com" in scraper.base_url


@pytest.mark.asyncio
async def test_hillsborough_scraper_empty_last_name():
    scraper = HillsboroughScraper()
    mock_page = MagicMock()
    results = await scraper.search_by_party_name("Crystal", "", mock_page)
    assert results == []


@pytest.mark.asyncio
async def test_hillsborough_scraper_table_extraction():
    """Simulates the 8-column layout from Frame 040/050 of the Florida recording."""
    scraper = HillsboroughScraper()

    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()

    # Inputs
    mock_tab = MagicMock()
    mock_tab.count = AsyncMock(return_value=1)
    mock_tab.first.click = AsyncMock()

    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first.wait_for = AsyncMock()
    mock_last.first.fill = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.first.fill = AsyncMock()

    mock_btn = MagicMock()
    mock_btn.count = AsyncMock(return_value=1)
    mock_btn.first.click = AsyncMock()

    mock_empty = MagicMock()
    mock_empty.count = AsyncMock(return_value=0)

    # 8-column row: [Icons, View, CaseNumber, Citation, CaseStyle, CaseStatus, Filed, CaseType]
    mock_row = MagicMock()
    mock_tds = MagicMock()
    mock_tds.all_inner_texts = AsyncMock(return_value=[
        "",                                         # Col 0: Action icon
        "",                                         # Col 1: View icon
        "26-TR-067231",                             # Col 2: Case Number
        "ANNPQME",                                  # Col 3: Citation
        "STATE OF FLORIDA VS GONZALEZ, SERGIO",     # Col 4: Case Style
        "CLOSED",                                   # Col 5: Case Status
        "2026-05-14",                               # Col 6: Filed Date
        "CIVIL TRAFFIC",                            # Col 7: Case Type
    ])
    mock_row.locator.return_value = mock_tds

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=1)
    mock_rows.nth.return_value = mock_row

    def locator_side_effect(selector):
        if "Party-tab" in selector:
            return mock_tab
        elif "partyLastName" in selector:
            return mock_last
        elif "partyFirstName" in selector:
            return mock_first
        elif "partySearchBtn" in selector:
            return mock_btn
        elif "dataTables_empty" in selector:
            return mock_empty
        elif "partyResultsTable" in selector or "dataTable" in selector:
            return mock_rows
        mock_generic = MagicMock()
        mock_generic.count = AsyncMock(return_value=0)
        return mock_generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):
        results = await scraper.search_by_party_name("SERGIO", "GONZALEZ", mock_page)

    assert len(results) == 1
    res = results[0]
    assert res["CaseNumber"] == "26-TR-067231"
    assert res["Citation"] == "ANNPQME"
    assert "GONZALEZ, SERGIO" in res["CaseStyle"]
    assert res["CaseStatus"] == "CLOSED"
    assert res["FilingDate"] == "2026-05-14"
    assert res["CaseType"] == "CIVIL TRAFFIC"


def test_broward_scraper_initialization():
    scraper = BrowardScraper()
    assert scraper.county_name == "Broward County (FL)"
    assert "browardclerk.org" in scraper.base_url


@pytest.mark.asyncio
async def test_turnstile_active_click_and_resolution():
    """Verify that detect_and_handle_captcha executes active click on Turnstile checkbox and detects solve token."""
    scraper = BrowardScraper()
    mock_page = MagicMock()
    mock_page.frames = []

    # Mock Turnstile challenge frame
    mock_frame = MagicMock()
    mock_frame.url = "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile"
    mock_cb = MagicMock()
    mock_cb.count = AsyncMock(return_value=1)
    mock_cb.first.click = AsyncMock()
    mock_frame.locator.return_value = mock_cb
    mock_frame.inner_text = AsyncMock(return_value="Success!")
    mock_page.frames = [mock_frame]

    # Container locators on page
    mock_recaptcha = MagicMock()
    mock_recaptcha.count = AsyncMock(return_value=0)
    mock_turnstile_container = MagicMock()
    mock_turnstile_container.count = AsyncMock(return_value=1)

    def locator_side_effect(selector):
        if "recaptcha" in selector or "hcaptcha" in selector:
            return mock_recaptcha
        elif "cf-turnstile" in selector or "challenges" in selector:
            return mock_turnstile_container
        mock_generic = MagicMock()
        mock_generic.count = AsyncMock(return_value=0)
        return mock_generic

    mock_page.locator.side_effect = locator_side_effect
    mock_page.wait_for_timeout = AsyncMock()
    # Mock evaluate returning True for cf-turnstile-response
    mock_page.evaluate = AsyncMock(return_value=True)

    result = await scraper.detect_and_handle_captcha(mock_page, wait_seconds=1)

    assert result is True
    # Verify the checkbox inside the Turnstile frame was clicked
    mock_cb.first.click.assert_awaited_once()



# ============================================================================
# 3. Texas Scraper Tests
# ============================================================================

def test_texas_scrapers_initialization():
    travis = TravisScraper()
    assert travis.county_name == "Travis County (TX)"
    assert "traviscountytx.gov" in travis.base_url

    dallas = DallasScraper()
    assert dallas.county_name == "Dallas County (TX)"
    assert "dallascounty.org" in dallas.base_url

    harris_jp = HarrisJPScraper()
    assert harris_jp.county_name == "Harris County JP (TX)"
    assert "harriscountytx.gov" in harris_jp.base_url

    harris_cclerk = HarrisCountyClerkScraper()
    assert harris_cclerk.county_name == "Harris County Clerk (TX)"
    assert "cclerk.hctx.net" in harris_cclerk.base_url

    harris_dist = HarrisDistrictClerkScraper()
    assert harris_dist.county_name == "Harris District Clerk (TX)"
    assert "hcdistrictclerk.com" in harris_dist.base_url


@pytest.mark.asyncio
async def test_travis_scraper_empty_last_name():
    scraper = TravisScraper()
    mock_page = MagicMock()
    results = await scraper.search_by_party_name("Jane", "", mock_page)
    assert results == []


@pytest.mark.asyncio
async def test_dallas_scraper_empty_last_name():
    scraper = DallasScraper()
    mock_page = MagicMock()
    results = await scraper.search_by_party_name("Bob", "", mock_page)
    assert results == []


@pytest.mark.asyncio
async def test_turnstile_detection_and_interactive_click():
    """Verify detect_and_handle_captcha actively clicks Turnstile checkbox and resolves token."""
    from unittest.mock import AsyncMock
    scraper = BrowardScraper()

    mock_checkbox = MagicMock()
    mock_checkbox.click = AsyncMock()

    mock_cb_locator = MagicMock()
    mock_cb_locator.count = AsyncMock(return_value=1)
    mock_cb_locator.first = mock_checkbox

    mock_turnstile_frame = MagicMock()
    mock_turnstile_frame.url = "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/turnstile"
    mock_turnstile_frame.locator = MagicMock(return_value=mock_cb_locator)
    mock_turnstile_frame.inner_text = AsyncMock(return_value="Success!")

    mock_container_locator = MagicMock()
    mock_container_locator.count = AsyncMock(return_value=1)

    mock_page = MagicMock()
    mock_page.frames = [mock_turnstile_frame]
    mock_page.locator = MagicMock(return_value=mock_container_locator)
    mock_page.wait_for_timeout = AsyncMock()
    # evaluate returns true for token found
    mock_page.evaluate = AsyncMock(return_value=True)

    solved = await scraper.detect_and_handle_captcha(mock_page, wait_seconds=2)
    assert solved is True
    # Verify checkbox inside turnstile challenge was clicked
    mock_checkbox.click.assert_awaited_once()

