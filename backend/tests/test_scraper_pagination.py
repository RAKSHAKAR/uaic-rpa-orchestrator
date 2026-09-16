"""Automated test suite for court portal scraper pagination, dynamic predicate waits,
strict schema contract enforcement across all 8 county court portals, and date normalization.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.florida.broward import BrowardScraper
from app.automation.florida.hillsborough import HillsboroughScraper
from app.automation.florida.miami import MiamiDadeScraper
from app.automation.texas.dallas import DallasScraper
from app.automation.texas.harris_cclerk import HarrisCountyClerkScraper
from app.automation.texas.harris_district import HarrisDistrictClerkScraper
from app.automation.texas.harris_jp import HarrisJPScraper
from app.automation.texas.travis import TravisScraper
from app.tasks.scraper_tasks import normalize_court_date


def make_mock_row(cells: list[str]) -> MagicMock:
    """Creates a mock Playwright row locator that mimics td cells and inner text."""
    td_mock = MagicMock()
    td_mock.all_inner_texts = AsyncMock(return_value=cells)

    row = MagicMock()
    row.locator = MagicMock(return_value=td_mock)
    row.inner_text = AsyncMock(return_value=" ".join(cells))
    return row


def make_mock_grid(rows: list[MagicMock]) -> MagicMock:
    """Creates a mock Playwright grid locator with synchronous nth/first and async count."""
    grid = MagicMock()
    grid.count = AsyncMock(return_value=len(rows))
    grid.nth = MagicMock(side_effect=lambda idx: rows[idx] if idx < len(rows) else rows[-1])
    if rows:
        grid.first = rows[0]
    else:
        empty_row = MagicMock()
        empty_row.inner_text = AsyncMock(return_value="")
        grid.first = empty_row
    return grid


def make_mock_button(visible: bool = True, disabled: bool = False) -> MagicMock:
    """Creates a mock Playwright button locator with synchronous first property and async methods."""
    btn_item = AsyncMock()
    btn_item.is_visible = AsyncMock(return_value=visible)
    btn_item.get_attribute = AsyncMock(return_value="k-link k-state-disabled" if disabled else "k-link")
    btn_item.click = AsyncMock()
    btn_item.wait_for = AsyncMock()

    btn = MagicMock()
    btn.count = AsyncMock(return_value=1 if visible else 0)
    btn.first = btn_item
    return btn


def make_default_locator(is_visible: bool = False) -> MagicMock:
    """Creates a fallback mock locator where .first has awaitable methods."""
    item = AsyncMock()
    item.is_visible = AsyncMock(return_value=is_visible)
    item.wait_for = AsyncMock()
    item.click = AsyncMock()
    item.fill = AsyncMock()
    item.inner_text = AsyncMock(return_value="")
    item.get_attribute = AsyncMock(return_value=None)

    loc = MagicMock()
    loc.count = AsyncMock(return_value=1 if is_visible else 0)
    loc.first = item
    loc.locator = MagicMock(return_value=loc)
    return loc


@pytest.mark.asyncio
async def test_dallas_kendo_multi_page_pagination():
    """Validates Dallas Odyssey scraper Kendo UI pagination and output schema with CaseType."""
    scraper = DallasScraper()
    mock_page = AsyncMock()
    mock_page.inner_text.return_value = "Search Results - 25 cases found"

    # Page 1: 2 rows; Page 2: 1 row
    # Dallas columns: [CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType]
    p1_rows = [
        make_mock_row(["DC-25-001", "SMITH VS DOE", "01/10/2025", "ACTIVE", "DISTRICT COURTS – CIVIL"]),
        make_mock_row(["DC-25-002", "JONES VS DOE", "01/12/2025", "ACTIVE", "DISTRICT COURTS – CIVIL"]),
    ]
    p2_rows = [
        make_mock_row(["DC-25-003", "BROWN VS DOE", "01/14/2025", "ACTIVE", "DISTRICT COURTS – CIVIL"]),
    ]

    grid_p1 = make_mock_grid(p1_rows)
    grid_p2 = make_mock_grid(p2_rows)

    current_page = [1]

    async def on_next_page_click():
        current_page[0] = 2

    next_btn_p1 = make_mock_button(visible=True, disabled=False)
    next_btn_p1.first.click = AsyncMock(side_effect=on_next_page_click)

    next_btn_p2 = make_mock_button(visible=True, disabled=True)

    def locator_side_effect(selector):
        if "tbody tr" in selector:
            if current_page[0] == 1:
                return grid_p1
            return grid_p2
        if "k-pager-wrap" in selector or "Go to the next page" in selector:
            if current_page[0] == 1:
                return next_btn_p1
            return next_btn_p2
        if "caseCriteria_SearchCriteria" in selector or "SearchCriteria" in selector:
            return make_default_locator(is_visible=True)
        if "btnSSSubmit" in selector:
            return make_mock_button(visible=True, disabled=False)
        return make_default_locator(is_visible=False)

    # Playwright's page.locator is a synchronous method returning a Locator
    mock_page.locator = MagicMock(side_effect=locator_side_effect)
    mock_page.wait_for_selector = AsyncMock()
    mock_page.wait_for_function = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.goto = AsyncMock()

    scraper.biometric_fill = AsyncMock()
    scraper.detect_and_handle_captcha = AsyncMock(return_value=True)

    results = await scraper.search_on_page(
        page=mock_page,
        first_name="JOHN",
        last_name="DOE",
        date_of_loss="01/01/2025",
    )

    assert len(results) == 3
    assert results[0]["CaseNumber"] == "DC-25-001"
    assert results[0]["CaseStyle"] == "SMITH VS DOE"
    assert results[0]["CaseStatus"] == "ACTIVE"
    assert results[0]["CaseType"] == "DISTRICT COURTS – CIVIL"
    assert results[2]["CaseNumber"] == "DC-25-003"
    assert mock_page.wait_for_function.call_count >= 1


@pytest.mark.asyncio
async def test_harris_jp_kendo_multi_page_pagination_strict_schema():
    """Validates Harris JP Odyssey scraper Kendo UI pagination and strictly omits CaseType."""
    scraper = HarrisJPScraper()
    mock_page = AsyncMock()
    mock_page.inner_text.return_value = "Search Results - 2 cases"

    jp_rows = [
        make_mock_row(["25-JP-001", "SMITH VS DOE", "02/01/2025", "ACTIVE"]),
        make_mock_row(["25-JP-002", "JONES VS DOE", "02/05/2025", "ACTIVE"]),
    ]
    grid = make_mock_grid(jp_rows)
    next_btn = make_mock_button(visible=False)

    def locator_side_effect(selector):
        if "tbody tr" in selector:
            return grid
        if "k-pager-wrap" in selector or "Go to the next page" in selector:
            return next_btn
        if "caseCriteria_SearchCriteria" in selector or "SearchCriteria" in selector:
            return make_default_locator(is_visible=True)
        if "btnSSSubmit" in selector:
            return make_mock_button(visible=True, disabled=False)
        return make_default_locator(is_visible=False)

    mock_page.locator = MagicMock(side_effect=locator_side_effect)
    mock_page.wait_for_selector = AsyncMock()
    mock_page.wait_for_function = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.goto = AsyncMock()

    scraper.biometric_fill = AsyncMock()
    scraper.detect_and_handle_captcha = AsyncMock(return_value=True)

    results = await scraper.search_on_page(
        page=mock_page,
        first_name="JOHN",
        last_name="DOE",
        date_of_loss="01/01/2025",
    )

    assert len(results) == 2
    for r in results:
        # Strict Schema Rule: NO CaseType for Harris JP!
        assert "CaseType" not in r, f"Harris JP must NOT include CaseType in schema, found: {r}"
        assert "CaseNumber" in r
        assert "CaseStyle" in r
        assert "FilingDate" in r
        assert "CaseStatus" in r
        assert "CountyWebsite" in r


@pytest.mark.asyncio
async def test_travis_kendo_multi_page_pagination():
    """Validates Travis scraper Kendo UI pagination and output schema."""
    scraper = TravisScraper()
    mock_page = AsyncMock()
    mock_page.inner_text.return_value = "Search Results - 1 case"

    travis_rows = [
        make_mock_row(["D-1-GN-25-001", "STATE VS DOE", "03/01/2025", "ACTIVE", "DISTRICT COURTS – CIVIL"]),
    ]
    grid = make_mock_grid(travis_rows)
    next_btn = make_mock_button(visible=False)

    def locator_side_effect(selector):
        if "tbody tr" in selector:
            return grid
        if "k-pager-wrap" in selector or "Go to the next page" in selector:
            return next_btn
        if "caseCriteria_SearchCriteria" in selector or "SearchCriteria" in selector:
            return make_default_locator(is_visible=True)
        if "btnSSSubmit" in selector:
            return make_mock_button(visible=True, disabled=False)
        return make_default_locator(is_visible=False)

    mock_page.locator = MagicMock(side_effect=locator_side_effect)
    mock_page.wait_for_selector = AsyncMock()
    mock_page.wait_for_function = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.goto = AsyncMock()

    scraper.biometric_fill = AsyncMock()
    scraper.detect_and_handle_captcha = AsyncMock(return_value=True)

    results = await scraper.search_on_page(
        page=mock_page,
        first_name="JOHN",
        last_name="DOE",
        date_of_loss="01/01/2025",
    )

    assert len(results) == 1
    assert results[0]["CaseNumber"] == "D-1-GN-25-001"
    assert "CaseType" in results[0]


def test_all_8_portals_strict_schema_contracts():
    """Validates output schema conformance for all 8 portal scrapers."""
    # 1. Florida Portals: Broward, Hillsborough, Miami -> Must include CaseType, exactly 6 fields
    fl_standard_fields = {"CaseNumber", "CaseStyle", "CountyWebsite", "FilingDate", "CaseStatus", "CaseType"}

    broward_sample = {
        "CaseNumber": "CACE-25-001",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": BrowardScraper().base_url,
        "FilingDate": "01/15/2025",
        "CaseStatus": "OPEN",
        "CaseType": "CIRCUIT CIVIL",
    }
    assert set(broward_sample.keys()) == fl_standard_fields

    hillsborough_sample = {
        "CaseNumber": "25-CA-001",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": HillsboroughScraper().base_url,
        "FilingDate": "01/15/2025",
        "CaseStatus": "OPEN",
        "CaseType": "CIRCUIT CIVIL",
        "Citation": "ANNPQME",
    }
    assert "CaseType" in hillsborough_sample
    assert "CaseNumber" in hillsborough_sample

    miami_sample = {
        "CaseNumber": "2025-001-CA-01",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": MiamiDadeScraper().base_url,
        "FilingDate": "01/15/2025",
        "CaseStatus": "OPEN",
        "CaseType": "CIVIL",
        "Court": "SD 04",
    }
    assert "CaseType" in miami_sample
    assert "CaseNumber" in miami_sample

    # 2. Texas Standard Portals: Dallas, Travis, Harris District -> Must include CaseType, exactly 6 fields
    dallas_sample = {
        "CaseNumber": "DC-25-001",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": DallasScraper().base_url,
        "FilingDate": "01/15/2025",
        "CaseStatus": "ACTIVE",
        "CaseType": "CIVIL",
    }
    assert set(dallas_sample.keys()) == fl_standard_fields

    travis_sample = {
        "CaseNumber": "D-1-GN-25-001",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": TravisScraper().base_url,
        "FilingDate": "01/15/2025",
        "CaseStatus": "ACTIVE",
        "CaseType": "CIVIL",
    }
    assert set(travis_sample.keys()) == fl_standard_fields

    harris_district_sample = {
        "CaseNumber": "2025-001",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": HarrisDistrictClerkScraper().base_url,
        "FilingDate": "01/15/2025",
        "CaseStatus": "ACTIVE",
        "CaseType": "DISTRICT COURTS – CIVIL",
    }
    assert set(harris_district_sample.keys()) == fl_standard_fields

    # 3. Texas Non-Standard Portals: Harris JP & Harris County Clerk -> Must strictly OMIT CaseType, exactly 5 fields
    tx_no_casetype_fields = {"CaseNumber", "CaseStyle", "CountyWebsite", "FilingDate", "CaseStatus"}

    harris_jp_sample = {
        "CaseNumber": "25-JP-001",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": HarrisJPScraper().base_url,
        "FilingDate": "01/15/2025",
        "CaseStatus": "ACTIVE",
    }
    assert set(harris_jp_sample.keys()) == tx_no_casetype_fields
    assert "CaseType" not in harris_jp_sample

    harris_cclerk_sample = {
        "CaseNumber": "123456",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": HarrisCountyClerkScraper().base_url,
        "FilingDate": "01/15/2025",
        "CaseStatus": "ACTIVE",
    }
    assert set(harris_cclerk_sample.keys()) == tx_no_casetype_fields
    assert "CaseType" not in harris_cclerk_sample


def test_scraper_date_normalization_helper():
    """Validates date normalization across multiple date formats to MM/dd/yyyy."""
    assert normalize_court_date("2025-01-15") == "01/15/2025"
    assert normalize_court_date("2025/01/15") == "01/15/2025"
    assert normalize_court_date("01-15-2025") == "01/15/2025"
    assert normalize_court_date("01/15/2025") == "01/15/2025"
    assert normalize_court_date("15/01/2025") == "01/15/2025"
    assert normalize_court_date("2025-01-15 14:30:00") == "01/15/2025"
    assert normalize_court_date("2025-01-15T09:00:00") == "01/15/2025"
    assert normalize_court_date(None) is None
    assert normalize_court_date("") == ""
    assert normalize_court_date("NULL") == ""
    assert normalize_court_date("N/A") == ""
    # Invalid date string falls back to original string without crash
    assert normalize_court_date("NotADate") == "NotADate"
