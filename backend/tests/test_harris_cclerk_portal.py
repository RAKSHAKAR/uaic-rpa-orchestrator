"""Comprehensive unit tests for Harris County Clerk (CClerk) portal automation (Prompt 7 compliance).

Validates:
- Dynamic settings configuration & custom URL initialization
- Step A: Page navigation, readiness wait, and blank body reload handling
- Step B & C: COURTS menu hover, County Civil submenu click, and form readiness verification
- Step D: Form data filling (Last Name, First Name, File Date From with DOL normalization)
- Step E: Search button click and execution
- Step F & I: 'YOUR SEARCH CRITERIA' popup detection and dismissal
- Step G: All-column extraction with strict schema compliance (STRICTLY NO CaseType)
- Step H: ASP.NET GridView pagination traversal across multiple result pages
- Section 4: return_to_search_state resets between unique names while tab stays open
- Sequential unique name processing and browser tab reuse
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.texas.harris_cclerk import (
    HarrisCountyClerkScraper,
    _normalize_court_date,
)


@pytest.fixture
def scraper():
    return HarrisCountyClerkScraper(
        base_url="https://www.cclerk.hctx.net/Applications/WebSearch/",
        captcha_wait_seconds=10,
        max_attempts=3,
    )


def test_harris_cclerk_dynamic_settings_init():
    """Verify that custom dynamic settings can be injected without hardcoded URLs."""
    custom_url = "https://custom-cclerk.hctx.net/WebSearch/"
    s = HarrisCountyClerkScraper(
        base_url=custom_url,
        captcha_wait_seconds=25,
        max_attempts=4,
    )
    assert s.base_url == custom_url
    assert s.captcha_wait_seconds == 25
    assert s.max_attempts == 4
    assert s.county_name == "Harris County Clerk (TX)"


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
async def test_step_a_b_c_navigation_and_form_ready(scraper):
    """Step A, B, C: Page navigation, COURTS hover, County Civil click, form verification."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Harris County Clerk Portal Content")

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

    page.goto.assert_awaited_once_with(scraper.base_url, wait_until="domcontentloaded")
    mock_courts.hover.assert_awaited_once()
    mock_civil.click.assert_awaited_once()
    mock_form.wait_for.assert_awaited_once_with(state="visible", timeout=15000)


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
        if "txtLastName" in selector:
            return mock_last
        if "txtFirstName" in selector:
            return mock_first
        if "txtDateFrom" in selector:
            return mock_date
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper.return_to_search_state(page)

    mock_last.clear.assert_awaited_once()
    mock_first.clear.assert_awaited_once()
    mock_date.clear.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_by_party_name_full_workflow_and_strict_schema(scraper):
    """
    Step D, E, F, G, H, J:
    Validates full search execution, popup handling, all-column extraction,
    and STRICT SCHEMA compliance (NO CaseType).
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

    # Results grid with 2 rows
    mock_row1 = MagicMock()
    mock_tds1 = MagicMock()
    mock_tds1.count = AsyncMock(return_value=6)
    mock_tds1.all_inner_texts = AsyncMock(return_value=[
        "123456", "ACTIVE", "01/15/2023", "Court 1", "Civil", "DOE, JOHN VS ROE, JANE"
    ])
    mock_row1.locator.return_value = mock_tds1

    mock_row2 = MagicMock()
    mock_tds2 = MagicMock()
    mock_tds2.count = AsyncMock(return_value=6)
    mock_tds2.all_inner_texts = AsyncMock(return_value=[
        "123456", "CLOSED", "05/20/2024", "Court 2", "Civil", "DOE, JOHN VS SMITH, BOB"
    ])
    mock_row2.locator.return_value = mock_tds2

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=2)
    mock_rows.nth.side_effect = [mock_row1, mock_row2]

    # Pagination: no next link on this page
    mock_pager = MagicMock()
    mock_pager.count = AsyncMock(return_value=0)
    mock_pager.first = mock_pager
    mock_pager.is_visible = AsyncMock(return_value=False)

    def locator_side_effect(selector):
        if "txtLastName" in selector:
            return mock_last
        if "txtFirstName" in selector:
            return mock_first
        if "txtDateFrom" in selector:
            return mock_dol
        if "btnSearch" in selector:
            return mock_search_btn
        if "grd" in selector and "pager" in selector:
            return mock_pager
        if "grd" in selector:
            return mock_rows
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    results = await scraper.search_by_party_name(
        first_name="John",
        last_name="Doe",
        page=page,
        date_of_loss="2023-01-10",
    )

    # Verify search input fills
    mock_last.fill.assert_awaited_once_with("Doe")
    mock_first.fill.assert_awaited_once_with("John")
    mock_dol.fill.assert_awaited_once_with("01/10/2023")
    mock_search_btn.click.assert_awaited_once()

    # Verify extraction results
    assert len(results) == 2
    assert results[0]["CaseNumber"] == "123456"
    assert results[0]["CaseStatus"] == "ACTIVE"
    assert results[0]["FilingDate"] == "01/15/2023"
    assert results[0]["CaseStyle"] == "DOE, JOHN VS ROE, JANE"

    assert results[1]["CaseNumber"] == "123456"
    assert results[1]["CaseStatus"] == "CLOSED"

    # STRICT SCHEMA CHECK (CRITICAL BUSINESS RULE)
    expected_keys = {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus"}
    for r in results:
        assert set(r.keys()) == expected_keys
        assert "CaseType" not in r, "Harris County Clerk MUST NOT include CaseType!"


@pytest.mark.asyncio
async def test_pagination_traversal(scraper):
    """Step H: Verify multi-page traversal using Next link."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Content")

    # Form locators
    mock_form = MagicMock()
    mock_form.count = AsyncMock(return_value=1)
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=True)
    mock_form.wait_for = AsyncMock()
    mock_form.fill = AsyncMock()

    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.first = mock_search_btn
    mock_search_btn.click = AsyncMock()

    # Page 1 row
    row_p1 = MagicMock()
    tds_p1 = MagicMock()
    tds_p1.count = AsyncMock(return_value=6)
    tds_p1.all_inner_texts = AsyncMock(return_value=["CASE-PAGE-1", "ACTIVE", "01/01/2023", "C1", "Type", "STYLE 1"])
    row_p1.locator.return_value = tds_p1

    # Page 2 row
    row_p2 = MagicMock()
    tds_p2 = MagicMock()
    tds_p2.count = AsyncMock(return_value=6)
    tds_p2.all_inner_texts = AsyncMock(return_value=["CASE-PAGE-2", "CLOSED", "02/01/2023", "C2", "Type", "STYLE 2"])
    row_p2.locator.return_value = tds_p2

    rows_p1 = MagicMock()
    rows_p1.count = AsyncMock(return_value=1)
    rows_p1.nth.return_value = row_p1

    rows_p2 = MagicMock()
    rows_p2.count = AsyncMock(return_value=1)
    rows_p2.nth.return_value = row_p2

    # Next page link (available on page 1, not on page 2)
    next_btn = MagicMock()
    next_btn.click = AsyncMock()

    mock_pager = MagicMock()
    mock_pager.count = AsyncMock(side_effect=[1, 0])
    mock_pager.first = next_btn
    mock_pager.is_visible = AsyncMock(side_effect=[True, False])

    grd_calls = 0

    def locator_side_effect(selector):
        nonlocal grd_calls
        if "txtLastName" in selector or "txtFirstName" in selector or "txtDateFrom" in selector:
            return mock_form
        if "btnSearch" in selector:
            return mock_search_btn
        if "pager" in selector or "Next" in selector:
            return mock_pager
        if "grd" in selector:
            grd_calls += 1
            return rows_p1 if grd_calls == 1 else rows_p2
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    results = await scraper.search_by_party_name("Jane", "Doe", page)

    # Next link clicked to get page 2
    assert next_btn.click.await_count >= 1
    case_numbers = [r["CaseNumber"] for r in results]
    assert "CASE-PAGE-1" in case_numbers
    assert "CASE-PAGE-2" in case_numbers


@pytest.mark.asyncio
async def test_repeated_result_page_fails_before_second_next_click(scraper):
    """An ASP.NET pager that redisplays the same full row must stop extraction."""
    page = MagicMock()
    page.wait_for_timeout = AsyncMock()
    scraper._navigate_to_county_civil = AsyncMock()
    scraper.check_and_handle_search_criteria_popup = AsyncMock(return_value=False)
    scraper.detect_and_handle_captcha = AsyncMock(return_value=True)

    form = MagicMock()
    form.count = AsyncMock(return_value=1)
    form.first = form
    form.wait_for = AsyncMock()
    form.fill = AsyncMock()
    form.is_visible = AsyncMock(return_value=True)

    search_btn = MagicMock()
    search_btn.count = AsyncMock(return_value=1)
    search_btn.first = search_btn
    search_btn.is_visible = AsyncMock(return_value=True)
    search_btn.click = AsyncMock()

    row = MagicMock()
    tds = MagicMock()
    tds.count = AsyncMock(return_value=6)
    tds.all_inner_texts = AsyncMock(return_value=["CASE-1", "ACTIVE", "01/01/2023", "C1", "Civil", "STYLE"])
    row.locator.return_value = tds
    rows = MagicMock()
    rows.count = AsyncMock(return_value=1)
    rows.nth.return_value = row

    next_btn = MagicMock()
    next_btn.click = AsyncMock()
    pager = MagicMock()
    pager.count = AsyncMock(return_value=1)
    pager.first = next_btn
    pager.is_visible = AsyncMock(return_value=True)

    def locator_for(selector):
        if "txtLastName" in selector or "txtFirstName" in selector or "txtDateFrom" in selector:
            return form
        if "btnSearch" in selector:
            return search_btn
        if "pager" in selector or "Next" in selector:
            return pager
        if "grd" in selector:
            return rows
        missing = MagicMock()
        missing.count = AsyncMock(return_value=0)
        missing.is_visible = AsyncMock(return_value=False)
        return missing

    page.locator.side_effect = locator_for

    with pytest.raises(RuntimeError, match="Pagination did not advance"):
        await scraper.search_by_party_name("Jane", "Doe", page)
    assert next_btn.click.await_count == 1


@pytest.mark.asyncio
async def test_step_a_blank_body_reload(scraper):
    """Step A: Verify that blank body in real browser session triggers page reload."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.reload = AsyncMock()
    page.evaluate = AsyncMock()  # Simulates browser page (not function)
    page.inner_text = AsyncMock(return_value="")  # Blank body

    mock_form = MagicMock()
    mock_form.count = AsyncMock(return_value=1)
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=True)

    page.locator.return_value = mock_form

    await scraper._navigate_to_county_civil(page)

    page.goto.assert_awaited_once_with(scraper.base_url, wait_until="domcontentloaded")
    page.reload.assert_awaited_once_with(wait_until="domcontentloaded")


@pytest.mark.asyncio
async def test_sequential_multiple_unique_names_on_same_page(scraper):
    """
    Sections 2 & 4:
    Verify that multiple unique names are processed sequentially on the same page/tab,
    with return_to_search_state resetting the inputs between names without closing page.
    """
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="No records found")

    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.is_visible = AsyncMock(return_value=True)
    mock_last.wait_for = AsyncMock()
    mock_last.fill = AsyncMock()
    mock_last.clear = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.first = mock_first
    mock_first.is_visible = AsyncMock(return_value=True)
    mock_first.fill = AsyncMock()
    mock_first.clear = AsyncMock()

    mock_dol = MagicMock()
    mock_dol.count = AsyncMock(return_value=1)
    mock_dol.first = mock_dol
    mock_dol.is_visible = AsyncMock(return_value=True)
    mock_dol.fill = AsyncMock()
    mock_dol.clear = AsyncMock()

    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.first = mock_search_btn
    mock_search_btn.click = AsyncMock()

    # Empty results row for clean test
    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=0)

    def locator_side_effect(selector):
        if "txtLastName" in selector:
            return mock_last
        if "txtFirstName" in selector:
            return mock_first
        if "txtDateFrom" in selector:
            return mock_dol
        if "btnSearch" in selector:
            return mock_search_btn
        if "grd" in selector:
            return mock_rows
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        fallback.is_visible = AsyncMock(return_value=False)
        return fallback

    page.locator.side_effect = locator_side_effect

    # Process Name 1
    res1 = await scraper.search_by_party_name("Alice", "Smith", page, date_of_loss="2023-05-01")
    assert isinstance(res1, list)
    assert mock_last.fill.await_count == 1
    assert mock_first.fill.await_count == 1

    # Reset state between unique names
    await scraper.return_to_search_state(page)
    # mock_last.clear is called once in biometric_fill and once in return_to_search_state = 2
    assert mock_last.clear.await_count == 2
    assert mock_first.clear.await_count == 2

    # Process Name 2 on same page
    res2 = await scraper.search_by_party_name("Bob", "Johnson", page, date_of_loss="2024-02-14")
    assert isinstance(res2, list)
    assert mock_last.fill.await_count == 2
    assert mock_first.fill.await_count == 2

    # Reset state again
    await scraper.return_to_search_state(page)
    assert mock_last.clear.await_count == 4
    assert mock_first.clear.await_count == 4


@pytest.mark.asyncio
async def test_harris_cclerk_default_initialization_settings():
    """Verify default settings: 120s captcha wait, 2 max attempts, CClerk URL."""
    scraper = HarrisCountyClerkScraper()
    assert scraper.captcha_wait_seconds == 120
    assert scraper.max_attempts == 2
    assert "cclerk.hctx.net" in scraper.base_url


@pytest.mark.asyncio
async def test_step_d_exact_txtfrom2_selector_targeted(scraper):
    """Step d: Verify exact input#ctl00_ContentPlaceHolder1_txtFrom2 is targeted for File Date (From)."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="No records found")

    captured_selectors = []

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.is_visible = AsyncMock(return_value=True)
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()
    mock_input.clear = AsyncMock()

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=0)

    def locator_side_effect(selector):
        captured_selectors.append(selector)
        if "grd" in selector:
            return mock_rows
        return mock_input

    page.locator.side_effect = locator_side_effect

    await scraper.search_by_party_name("Jane", "Doe", page, date_of_loss="01/15/2024")

    assert any("txtFrom2" in s for s in captured_selectors), "Selector list should prioritize txtFrom2"
    assert any("ctl00_ContentPlaceHolder1_txtFrom2" in s for s in captured_selectors)


@pytest.mark.asyncio
async def test_step_e_exact_btnsearch_selector_targeted(scraper):
    """Step e: Verify exact input#ctl00_ContentPlaceHolder1_btnSearch is targeted for Search button."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="No records found")

    captured_selectors = []

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.is_visible = AsyncMock(return_value=True)
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()
    mock_input.clear = AsyncMock()
    mock_input.click = AsyncMock()

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=0)

    def locator_side_effect(selector):
        captured_selectors.append(selector)
        if "grd" in selector:
            return mock_rows
        return mock_input

    page.locator.side_effect = locator_side_effect

    await scraper.search_by_party_name("Jane", "Doe", page)

    assert any("ctl00_ContentPlaceHolder1_btnSearch" in s for s in captured_selectors)
    assert any("btnSearch" in s and "value='Search'" in s for s in captured_selectors)


@pytest.mark.asyncio
async def test_live_no_data_radio_controls_are_not_case_rows(scraper):
    """The live no-match page has a three-cell Party/Attorney/Company table."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="No data found.")

    control = MagicMock()
    control.count = AsyncMock(return_value=1)
    control.first = control
    control.is_visible = AsyncMock(return_value=True)
    control.wait_for = AsyncMock()
    control.fill = AsyncMock()
    control.click = AsyncMock()

    radio_cells = MagicMock()
    radio_cells.count = AsyncMock(return_value=3)
    radio_cells.all_inner_texts = AsyncMock(return_value=["Party", "Attorney", "Company"])
    radio_row = MagicMock()
    radio_row.locator.return_value = radio_cells
    rows = MagicMock()
    rows.count = AsyncMock(return_value=1)
    rows.nth.return_value = radio_row

    empty_pager = MagicMock()
    empty_pager.count = AsyncMock(return_value=0)

    def locator_side_effect(selector):
        if "tbody tr" in selector:
            return rows
        if "pager" in selector or "Next" in selector:
            return empty_pager
        return control

    page.locator.side_effect = locator_side_effect

    assert await scraper.search_by_party_name("Audit", "Zyxqtest", page) == []
    control.click.assert_awaited()


@pytest.mark.asyncio
async def test_step_a_short_body_reload(scraper):
    """Step a: Verify that short/incomplete body text (< 5 characters) triggers reload."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.reload = AsyncMock()
    page.inner_text = AsyncMock(return_value="abc")  # len < 5

    mock_form = MagicMock()
    mock_form.count = AsyncMock(return_value=1)
    mock_form.first = mock_form
    mock_form.is_visible = AsyncMock(return_value=True)

    page.locator.return_value = mock_form

    await scraper._navigate_to_county_civil(page)

    page.goto.assert_awaited_once_with(scraper.base_url, wait_until="domcontentloaded")
    page.reload.assert_awaited_once_with(wait_until="domcontentloaded")


@pytest.mark.asyncio
async def test_step_b_exact_county_civil_href_targeted(scraper):
    """Step b: Verify exact href for County Civil submenu is targeted."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Full Content Loaded")

    captured_selectors = []

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
        captured_selectors.append(selector)
        if "txtLastName" in selector:
            return mock_form
        if "COURTS" in selector:
            return mock_courts
        if "County Civil" in selector or "CourtSearch.aspx?CaseType=Civil" in selector:
            return mock_civil
        fallback = MagicMock()
        fallback.count = AsyncMock(return_value=0)
        fallback.first = fallback
        return fallback

    page.locator.side_effect = locator_side_effect

    await scraper._navigate_to_county_civil(page)

    assert any("/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil" in s for s in captured_selectors)
    mock_civil.click.assert_awaited_once()
