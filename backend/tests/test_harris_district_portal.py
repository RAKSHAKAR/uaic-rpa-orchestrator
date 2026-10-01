"""Comprehensive unit tests for Harris County District Clerk (HCDistrict) portal automation (Prompt 8 compliance).

Validates:
- Dynamic settings configuration & custom URL initialization
- Step A: Page navigation, readiness wait, and blank body reload handling
- Step B & C: Click "Search Our Records", Party Inquiry selection, and form readiness verification
- Step D: Form data filling (Last Name, First Name, File Date From with DOL normalization)
- Step E: Search button click and execution
- Step F & I: 'YOUR SEARCH CRITERIA' popup detection and dismissal
- Step G: All-column extraction with strict schema compliance (CaseType MUST BE INCLUDED)
- Step H: ASP.NET GridView pagination traversal across multiple result pages
- Section 4: return_to_search_state resets between unique names while tab stays open
- Sequential unique name processing and browser tab reuse
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import async_playwright

from app.automation.texas.harris_district import (
    HARRIS_DISTRICT_RESULT_READY_JS,
    HarrisDistrictClerkScraper,
    _date_for_input,
    _is_valid_case_result,
    _normalize_court_date,
)


def test_live_empty_state_cannot_be_reported_as_harris_district_case():
    """The live portal's no-results panel must not become a case number."""
    live_empty_cell = (
        "No results found.Click the\nCreate button below for a Certified "
        "Letter of Disposition or enter additional information.\nDriver License:"
    )
    assert not _is_valid_case_result(live_empty_cell, "", "")
    assert not _is_valid_case_result("Case Number", "Case Style", "01/15/2023")
    assert _is_valid_case_result("2023-12345", "SMITH VS DOE", "01/15/2023")
    assert _is_valid_case_result(
        "263937901010 - 2\nActive - CRIMINAL",
        "THE STATE OF TEXAS VS SMITH",
        "09/11/2026",
    )


def test_native_date_input_receives_iso_value_without_changing_v4_text_format():
    assert _date_for_input("01/15/2023", "date") == "2023-01-15"
    assert _date_for_input("01/15/2023", "text") == "01/15/2023"


@pytest.mark.asyncio
async def test_result_readiness_waits_for_all_advertised_first_page_rows():
    """The court may display its pager before the first page finishes rendering."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content("""
                <p>Total records returned from search is 4.</p>
                <table class="PagerContainerTable"><tr><td>Page 1 of 2</td>
                    <td><a title="Show Result 3 to 4 of 4">2</a></td></tr></table>
                <table class="docketTable"><tbody>
                    <tr><td>Case (Cause) Number</td></tr>
                    <tr><td>2026-1</td><td>Style</td><td></td><td></td>
                        <td></td><td>09/01/2026</td><td>Type</td></tr>
                </tbody></table>
            """)
            assert await page.evaluate(HARRIS_DISTRICT_RESULT_READY_JS) is False
            await page.evaluate("""() => document.querySelector('.docketTable tbody')
                .insertAdjacentHTML('beforeend', `<tr><td>2026-2</td><td>Style</td>
                <td></td><td></td><td></td><td>09/02/2026</td><td>Type</td></tr>`)""")
            assert await page.evaluate(HARRIS_DISTRICT_RESULT_READY_JS) is True
            await page.set_content("<p>Your search did not return any records.</p>")
            assert await page.evaluate(HARRIS_DISTRICT_RESULT_READY_JS) is True
        finally:
            await browser.close()


@pytest.fixture
def scraper():
    return HarrisDistrictClerkScraper(
        base_url="https://www.hcdistrictclerk.com/",
        captcha_wait_seconds=10,
        max_attempts=3,
    )


def test_hcdistrict_dynamic_settings_init():
    """Verify that custom dynamic settings can be injected without hardcoded URLs."""
    custom_url = "https://custom-hcdistrict.harriscountytx.gov/"
    s = HarrisDistrictClerkScraper(
        base_url=custom_url,
        captcha_wait_seconds=25,
        max_attempts=4,
    )
    assert s.base_url == custom_url
    assert s.captcha_wait_seconds == 25
    assert s.max_attempts == 4
    assert s.county_name == "Harris District Clerk (TX)"


def test_date_normalization_helper():
    """Verify DOL date normalization to standard MM/dd/yyyy format."""
    assert _normalize_court_date("2025-01-15") == "01/15/2025"
    assert _normalize_court_date("2025/01/15") == "01/15/2025"
    assert _normalize_court_date("01-15-2025") == "01/15/2025"
    assert _normalize_court_date("01/15/2025") == "01/15/2025"
    assert _normalize_court_date("15/01/2025") == "01/15/2025"
    assert _normalize_court_date("2025-01-15 14:30:00") == "01/15/2025"
    assert _normalize_court_date("2025-01-15T09:00:00") == "01/15/2025"
    assert _normalize_court_date(None) is None
    assert _normalize_court_date("") == ""
    assert _normalize_court_date("NULL") == ""
    assert _normalize_court_date("N/A") == ""
    assert _normalize_court_date("NotADate") == "NotADate"


@pytest.mark.asyncio
async def test_step_a_b_c_navigation_and_search_records_click(scraper):
    """Step A, B, C: Page navigation, click 'Search Our Records', Party Inquiry, and form verification."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Harris County District Clerk Portal Content")

    mock_form = MagicMock()
    mock_form.count = AsyncMock(side_effect=[0, 1])
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=False)
    mock_form.wait_for = AsyncMock()

    mock_search_link = MagicMock()
    mock_search_link.count = AsyncMock(return_value=1)
    mock_search_link.first = mock_search_link
    mock_search_link.is_visible = AsyncMock(return_value=True)
    mock_search_link.click = AsyncMock()

    mock_party_inquiry = MagicMock()
    mock_party_inquiry.count = AsyncMock(return_value=1)
    mock_party_inquiry.first = mock_party_inquiry
    mock_party_inquiry.is_visible = AsyncMock(return_value=True)
    mock_party_inquiry.click = AsyncMock()

    def locator_side_effect(selector):
        if "txtPartyName" in selector or "partyLastName" in selector:
            return mock_form
        if "Search Our Records" in selector or "Search.aspx" in selector:
            return mock_search_link
        if "Party Inquiry" in selector:
            return mock_party_inquiry
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper._navigate_to_search_page(page)

    page.goto.assert_awaited_once_with(scraper.base_url, wait_until="domcontentloaded")
    mock_search_link.click.assert_awaited_once()
    mock_party_inquiry.click.assert_awaited_once()
    mock_form.wait_for.assert_awaited_once_with(state="visible", timeout=15000)


@pytest.mark.asyncio
async def test_step_a_blank_body_reload(scraper):
    """Step A: Blank body triggers reload."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="   ")
    page.reload = AsyncMock()
    page.evaluate = MagicMock()

    mock_form = MagicMock()
    mock_form.count = AsyncMock(side_effect=[0, 1])
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=False)

    def locator_side_effect(selector):
        if "txtPartyName" in selector or "partyLastName" in selector:
            return mock_form
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper._navigate_to_search_page(page)

    page.goto.assert_awaited_once_with(scraper.base_url, wait_until="domcontentloaded")
    page.reload.assert_awaited_once()


@pytest.mark.asyncio
async def test_step_i_popup_dismissal(scraper):
    """Step I: If 'YOUR SEARCH CRITERIA' popup appears, close/cross it and continue."""
    page = MagicMock()
    page.wait_for_timeout = AsyncMock()

    mock_popup = MagicMock()
    mock_popup.count = AsyncMock(return_value=1)
    mock_popup.is_visible = AsyncMock(return_value=True)

    mock_close_btn = MagicMock()
    mock_close_btn.count = AsyncMock(return_value=1)
    mock_close_btn.first = mock_close_btn
    mock_close_btn.is_visible = AsyncMock(return_value=True)
    mock_close_btn.click = AsyncMock()

    def locator_side_effect(selector):
        if "SEARCH CRITERIA" in selector:
            return mock_popup
        if "messageClose" in selector or "Close" in selector:
            return mock_close_btn
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    dismissed = await scraper.check_and_handle_search_criteria_popup(page)
    assert dismissed is True
    mock_close_btn.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_section_4_return_to_search_state(scraper):
    """Section 4: return_to_search_state clears inputs between unique names."""
    page = MagicMock()
    page.wait_for_timeout = AsyncMock()

    mock_party = MagicMock()
    mock_party.count = AsyncMock(return_value=1)
    mock_party.first = mock_party
    mock_party.is_visible = AsyncMock(return_value=True)
    mock_party.clear = AsyncMock()

    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.is_visible = AsyncMock(return_value=True)
    mock_last.clear = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.first = mock_first
    mock_first.is_visible = AsyncMock(return_value=True)
    mock_first.clear = AsyncMock()

    mock_date = MagicMock()
    mock_date.count = AsyncMock(return_value=1)
    mock_date.first = mock_date
    mock_date.is_visible = AsyncMock(return_value=True)
    mock_date.clear = AsyncMock()

    def locator_side_effect(selector):
        if "txtPartyName" in selector:
            return mock_party
        if "partyLastName" in selector:
            return mock_last
        if "partyFirstName" in selector:
            return mock_first
        if "txtPartyStartDate" in selector or "txtFiledDateFrom" in selector:
            return mock_date
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper.return_to_search_state(page)

    mock_party.clear.assert_awaited_once()
    mock_last.clear.assert_awaited_once()
    mock_first.clear.assert_awaited_once()
    mock_date.clear.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_by_party_name_full_workflow_and_schema(scraper):
    """
    Step D, E, F, G, H, J:
    Validates full search execution, popup handling, all-column extraction,
    and STRICT SCHEMA compliance (CaseType INCLUDED).
    """
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Content")

    # Form locators
    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.is_visible = AsyncMock(return_value=True)
    mock_last.wait_for = AsyncMock()
    mock_last.fill = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.first = mock_first
    mock_first.is_visible = AsyncMock(return_value=True)
    mock_first.fill = AsyncMock()

    mock_dol = MagicMock()
    mock_dol.count = AsyncMock(return_value=1)
    mock_dol.first = mock_dol
    mock_dol.is_visible = AsyncMock(return_value=True)
    mock_dol.fill = AsyncMock()

    # Search button
    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.first = mock_search_btn
    mock_search_btn.click = AsyncMock()

    # Results grid with 2 rows:
    # td:eq(0) -> CaseNumber
    # td:eq(1) -> CaseStyle
    # td:eq(2) -> Other
    # td:eq(3) -> CaseStatus
    # td:eq(4) -> Other
    # td:eq(5) -> FilingDate
    # td:eq(6) -> CaseType
    mock_row1 = MagicMock()
    mock_tds1 = MagicMock()
    mock_tds1.count = AsyncMock(return_value=7)
    mock_tds1.all_inner_texts = AsyncMock(return_value=[
        "2023-12345", "SMITH, JOHN VS DOE, JANE", "001", "ACTIVE", "CIVIL", "01/15/2023", "MOTOR VEHICLE ACCIDENT"
    ])
    mock_row1.locator.return_value = mock_tds1

    mock_row2 = MagicMock()
    mock_tds2 = MagicMock()
    mock_tds2.count = AsyncMock(return_value=7)
    mock_tds2.all_inner_texts = AsyncMock(return_value=[
        "2024-67890", "SMITH, JOHN VS ROE, RICHARD", "002", "DISPOSED", "CIVIL", "05/20/2024", "CONTRACT - OTHER"
    ])
    mock_row2.locator.return_value = mock_tds2

    # V4 preserves separate result rows even when multiple party roles point
    # to the same case number.
    mock_row3 = MagicMock()
    mock_tds3 = MagicMock()
    mock_tds3.count = AsyncMock(return_value=7)
    mock_tds3.all_inner_texts = AsyncMock(return_value=[
        "2023-12345", "SMITH, JOHN VS DOE, JANE", "SECOND PARTY ROLE", "ACTIVE", "CIVIL", "01/15/2023", "MOTOR VEHICLE ACCIDENT"
    ])
    mock_row3.locator.return_value = mock_tds3

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=3)
    mock_rows.nth.side_effect = [mock_row1, mock_row2, mock_row3]

    # Pagination: no next link on this page
    mock_pager = MagicMock()
    mock_pager.count = AsyncMock(return_value=0)
    mock_pager.first = mock_pager
    mock_pager.is_visible = AsyncMock(return_value=False)

    def locator_side_effect(selector):
        if "partyLastName" in selector:
            return mock_last
        if "partyFirstName" in selector:
            return mock_first
        if "txtPartyStartDate" in selector or "txtFiledDateFrom" in selector:
            return mock_dol
        if "btnPartySearch" in selector or "btnSearch" in selector:
            return mock_search_btn
        if "dgSearchResults" in selector and "pager" in selector:
            return mock_pager
        if "dgSearchResults" in selector or "grid-results" in selector or "table tbody tr" in selector:
            return mock_rows
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    results = await scraper.search_by_party_name(
        first_name="John",
        last_name="Smith",
        page=page,
        date_of_loss="2023-01-15",
    )

    # The live page also has an earlier Google site-search button. The V4
    # party submit must be selected by its exact control ID.
    page.locator.assert_any_call(
        "input#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch"
    )

    assert len(results) == 3

    # CRITICAL: Verify CaseType is present and schema matches EXACT requirements for Harris District
    expected_fields = {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}
    for case in results:
        assert set(case.keys()) == expected_fields
        assert "CaseType" in case
        assert case["CaseType"] != ""

    assert results[0]["CaseNumber"] == "2023-12345"
    assert results[0]["CaseStyle"] == "SMITH, JOHN VS DOE, JANE"
    assert results[0]["FilingDate"] == "01/15/2023"
    assert results[0]["CaseStatus"] == "ACTIVE"
    assert results[0]["CaseType"] == "MOTOR VEHICLE ACCIDENT"

    assert results[1]["CaseNumber"] == "2024-67890"
    assert results[1]["CaseStyle"] == "SMITH, JOHN VS ROE, RICHARD"
    assert results[1]["FilingDate"] == "05/20/2024"
    assert results[1]["CaseStatus"] == "DISPOSED"
    assert results[1]["CaseType"] == "CONTRACT - OTHER"
    assert results[2]["CaseNumber"] == "2023-12345"


@pytest.mark.asyncio
async def test_pagination_traversal(scraper):
    """Step H: Verify traversal through multi-page results."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Content")

    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.is_visible = AsyncMock(return_value=True)
    mock_last.fill = AsyncMock()

    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.first = mock_search_btn
    mock_search_btn.click = AsyncMock()

    # Page 1 row
    mock_row_p1 = MagicMock()
    mock_tds_p1 = MagicMock()
    mock_tds_p1.count = AsyncMock(return_value=7)
    mock_tds_p1.all_inner_texts = AsyncMock(return_value=[
        "PAGE1-001", "STYLE PAGE 1", "", "ACTIVE", "", "01/01/2023", "CIVIL 1"
    ])
    mock_row_p1.locator.return_value = mock_tds_p1

    mock_rows_p1 = MagicMock()
    mock_rows_p1.count = AsyncMock(return_value=1)
    mock_rows_p1.nth.return_value = mock_row_p1

    # Page 2 row
    mock_row_p2 = MagicMock()
    mock_tds_p2 = MagicMock()
    mock_tds_p2.count = AsyncMock(return_value=7)
    mock_tds_p2.all_inner_texts = AsyncMock(return_value=[
        "PAGE2-002", "STYLE PAGE 2", "", "ACTIVE", "", "02/02/2023", "CIVIL 2"
    ])
    mock_row_p2.locator.return_value = mock_tds_p2

    mock_rows_p2 = MagicMock()
    mock_rows_p2.count = AsyncMock(return_value=1)
    mock_rows_p2.nth.return_value = mock_row_p2

    # Next page pager button: visible on page 1, absent on page 2
    mock_pager = MagicMock()
    mock_pager.count = AsyncMock(side_effect=[1, 0])
    mock_pager.first = mock_pager
    mock_pager.is_visible = AsyncMock(side_effect=[True, False])
    mock_pager.click = AsyncMock()

    row_cycle = [mock_rows_p1, mock_rows_p2]
    call_idx = {"rows": 0}

    def locator_side_effect(selector):
        if "partyLastName" in selector:
            return mock_last
        if "btnPartySearch" in selector or "btnSearch" in selector:
            return mock_search_btn
        if "dgSearchResults" in selector and "pager" in selector:
            return mock_pager
        if "dgSearchResults" in selector or "grid-results" in selector or "table tbody tr" in selector:
            curr = row_cycle[min(call_idx["rows"], len(row_cycle) - 1)]
            call_idx["rows"] += 1
            return curr
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    results = await scraper.search_by_party_name(
        first_name="Jane",
        last_name="Doe",
        page=page,
    )

    assert len(results) == 2
    assert results[0]["CaseNumber"] == "PAGE1-001"
    assert results[0]["CaseType"] == "CIVIL 1"
    assert results[1]["CaseNumber"] == "PAGE2-002"
    assert results[1]["CaseType"] == "CIVIL 2"
    mock_pager.click.assert_awaited_once()
    assert any(
        "table.PagerContainerTable a[title*='Next to Page' i]" in call.args[0]
        for call in page.locator.call_args_list
    )


@pytest.mark.asyncio
async def test_sequential_multiple_unique_names_on_same_page(scraper):
    """
    Sections 2 & 4: Validates sequential execution of Name 1 and Name 2 on the same page.
    Asserts return_to_search_state is called between names without page reload or closure.
    """
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Content")

    # Inputs
    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.is_visible = AsyncMock(return_value=True)
    mock_last.fill = AsyncMock()
    mock_last.clear = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.first = mock_first
    mock_first.is_visible = AsyncMock(return_value=True)
    mock_first.fill = AsyncMock()
    mock_first.clear = AsyncMock()

    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.first = mock_search_btn
    mock_search_btn.click = AsyncMock()

    # Results for Name 1
    mock_row1 = MagicMock()
    mock_tds1 = MagicMock()
    mock_tds1.count = AsyncMock(return_value=7)
    mock_tds1.all_inner_texts = AsyncMock(return_value=[
        "N1-001", "DOE, JOHN VS X", "", "OPEN", "", "01/01/2023", "FAMILY"
    ])
    mock_row1.locator.return_value = mock_tds1

    mock_rows1 = MagicMock()
    mock_rows1.count = AsyncMock(return_value=1)
    mock_rows1.nth.return_value = mock_row1

    # Results for Name 2
    mock_row2 = MagicMock()
    mock_tds2 = MagicMock()
    mock_tds2.count = AsyncMock(return_value=7)
    mock_tds2.all_inner_texts = AsyncMock(return_value=[
        "N2-002", "SMITH, BOB VS Y", "", "ACTIVE", "", "02/02/2023", "TORTS"
    ])
    mock_row2.locator.return_value = mock_tds2

    mock_rows2 = MagicMock()
    mock_rows2.count = AsyncMock(return_value=1)
    mock_rows2.nth.return_value = mock_row2

    mock_pager = MagicMock()
    mock_pager.count = AsyncMock(return_value=0)
    mock_pager.first = mock_pager
    mock_pager.is_visible = AsyncMock(return_value=False)

    call_count = {"search": 0}

    def locator_side_effect(selector):
        if "partyLastName" in selector:
            return mock_last
        if "partyFirstName" in selector:
            return mock_first
        if "btnPartySearch" in selector or "btnSearch" in selector:
            return mock_search_btn
        if "dgSearchResults" in selector and "pager" in selector:
            return mock_pager
        if "dgSearchResults" in selector or "grid-results" in selector or "table tbody tr" in selector:
            if call_count["search"] == 1:
                return mock_rows1
            return mock_rows2
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    # Execute Name 1
    call_count["search"] = 1
    res1 = await scraper.search_by_party_name(first_name="John", last_name="Doe", page=page)
    assert len(res1) == 1
    assert res1[0]["CaseNumber"] == "N1-001"
    assert res1[0]["CaseType"] == "FAMILY"

    # Reset search state for Name 2
    await scraper.return_to_search_state(page)
    mock_last.clear.assert_awaited()

    # Execute Name 2
    call_count["search"] = 2
    res2 = await scraper.search_by_party_name(first_name="Bob", last_name="Smith", page=page)
    assert len(res2) == 1
    assert res2[0]["CaseNumber"] == "N2-002"
    assert res2[0]["CaseType"] == "TORTS"


def test_hcdistrict_default_settings():
    """Verify default scraper settings conform to Texas portal specification (120s wait, 2 attempts)."""
    s = HarrisDistrictClerkScraper()
    assert s.captcha_wait_seconds == 120
    assert s.max_attempts == 2
    assert s.base_url == "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"


@pytest.mark.asyncio
async def test_step_c_reset_button_click(scraper):
    """Step C: Verify reset button is clicked upon reaching Party Inquiry search form."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Valid body text with enough length")

    mock_form = MagicMock()
    mock_form.count = AsyncMock(side_effect=[0, 1])
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=False)
    mock_form.wait_for = AsyncMock()

    mock_search_link = MagicMock()
    mock_search_link.count = AsyncMock(return_value=1)
    mock_search_link.first = mock_search_link
    mock_search_link.is_visible = AsyncMock(return_value=True)
    mock_search_link.click = AsyncMock()

    mock_party_inquiry = MagicMock()
    mock_party_inquiry.count = AsyncMock(return_value=1)
    mock_party_inquiry.first = mock_party_inquiry
    mock_party_inquiry.is_visible = AsyncMock(return_value=True)
    mock_party_inquiry.get_attribute = AsyncMock(return_value="btn")
    mock_party_inquiry.click = AsyncMock()

    mock_reset_btn = MagicMock()
    mock_reset_btn.count = AsyncMock(return_value=1)
    mock_reset_btn.first = mock_reset_btn
    mock_reset_btn.is_visible = AsyncMock(return_value=True)
    mock_reset_btn.click = AsyncMock()

    def locator_side_effect(selector):
        if "txtPartyName" in selector or "partyLastName" in selector:
            return mock_form
        if "Search Our Records" in selector or "Search.aspx" in selector:
            return mock_search_link
        if "tabParty" in selector or "Party Inquiry" in selector:
            return mock_party_inquiry
        if "reset" in selector or "dcoButtons" in selector:
            return mock_reset_btn
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper._navigate_to_search_page(page)

    mock_reset_btn.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_step_d_date_range_inputs_and_today_end_date(scraper):
    """Step D: Verify DOL is entered in txtPartyStartDate and today's date in txtPartyEndDate."""
    from datetime import datetime

    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Your search did not return any records.")

    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.is_visible = AsyncMock(return_value=True)
    mock_last.fill = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.first = mock_first
    mock_first.is_visible = AsyncMock(return_value=True)
    mock_first.fill = AsyncMock()

    mock_dol = MagicMock()
    mock_dol.count = AsyncMock(return_value=1)
    mock_dol.first = mock_dol
    mock_dol.is_visible = AsyncMock(return_value=True)
    mock_dol.fill = AsyncMock()

    mock_end_date = MagicMock()
    mock_end_date.count = AsyncMock(return_value=1)
    mock_end_date.first = mock_end_date
    mock_end_date.is_visible = AsyncMock(return_value=True)
    mock_end_date.fill = AsyncMock()

    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.first = mock_search_btn
    mock_search_btn.click = AsyncMock()

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=0)

    def locator_side_effect(selector):
        if "partyLastName" in selector:
            return mock_last
        if "partyFirstName" in selector:
            return mock_first
        if "txtPartyStartDate" in selector or "txtFiledDateFrom" in selector:
            return mock_dol
        if "txtPartyEndDate" in selector or "txtFiledDateTo" in selector:
            return mock_end_date
        if "btnPartySearch" in selector or "btnSearch" in selector:
            return mock_search_btn
        if "dgSearchResults" in selector or "grid-results" in selector or "table tbody tr" in selector:
            return mock_rows
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    results = await scraper.search_by_party_name(
        first_name="Jane",
        last_name="Doe",
        page=page,
        date_of_loss="2022-08-10",
    )

    assert results == []

    # Check DOL filled in txtPartyStartDate
    mock_dol.fill.assert_awaited_once_with("08/10/2022")

    # Check today's date filled in txtPartyEndDate
    today_str = datetime.now().strftime("%m/%d/%Y")
    mock_end_date.fill.assert_awaited_once_with(today_str)


@pytest.mark.asyncio
async def test_step_e_exact_search_button_selector(scraper):
    """Step E: Verify exact btnPartySearch button selector is prioritized and clicked."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="No records found")

    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.is_visible = AsyncMock(return_value=True)
    mock_last.fill = AsyncMock()

    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.first = mock_search_btn
    mock_search_btn.click = AsyncMock()

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=0)

    clicked_selector = []

    def locator_side_effect(selector):
        if "partyLastName" in selector:
            return mock_last
        if "btnPartySearch" in selector:
            clicked_selector.append(selector)
            return mock_search_btn
        if "dgSearchResults" in selector or "grid-results" in selector or "table tbody tr" in selector:
            return mock_rows
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper.search_by_party_name(first_name="", last_name="Smith", page=page)

    mock_search_btn.click.assert_awaited_once()
    assert any("btnPartySearch" in sel for sel in clicked_selector)


@pytest.mark.asyncio
async def test_section_4_clears_end_date_input(scraper):
    """Section 4: Verify return_to_search_state clears txtPartyEndDate as well."""
    page = MagicMock()
    page.wait_for_timeout = AsyncMock()

    mock_end_date = MagicMock()
    mock_end_date.count = AsyncMock(return_value=1)
    mock_end_date.first = mock_end_date
    mock_end_date.is_visible = AsyncMock(return_value=True)
    mock_end_date.clear = AsyncMock()

    def locator_side_effect(selector):
        if "txtPartyEndDate" in selector:
            return mock_end_date
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper.return_to_search_state(page)

    mock_end_date.clear.assert_awaited_once()
