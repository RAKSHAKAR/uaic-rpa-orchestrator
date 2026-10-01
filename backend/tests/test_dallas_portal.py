"""Unit & workflow tests for Dallas County court portal scraper (Prompt 5 compliance)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import CaptchaResolutionError
from app.automation.texas.dallas import DallasScraper


@pytest.fixture
def dallas_scraper():
    return DallasScraper(
        base_url="https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29",
        captcha_wait_seconds=15,
        max_attempts=3,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("source_pages", "expected_next_clicks"),
    [
        ([
            ["CASE-1", "Style A", "01/01/2023", "ACTIVE", "CIVIL"],
            ["CASE-1", "Style A", "01/01/2023", "ACTIVE", "CIVIL"],
        ], 1),
        ([
            ["CASE-1", "Style A", "01/01/2023", "ACTIVE", "CIVIL"],
            ["CASE-1", "Style B", "02/01/2023", "ACTIVE", "CIVIL"],
            ["CASE-1", "Style A", "01/01/2023", "ACTIVE", "CIVIL"],
        ], 2),
    ],
)
async def test_repeated_result_page_fails_fast(dallas_scraper, source_pages, expected_next_clicks):
    """Same-number rows with different details advance; any revisited page stops."""
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=False)
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")

    row = MagicMock()
    row.locator.return_value.all_inner_texts = AsyncMock(side_effect=source_pages)
    rows = MagicMock()
    rows.count = AsyncMock(return_value=1)
    rows.nth.return_value = row

    next_btn = MagicMock()
    next_btn.count = AsyncMock(return_value=1)
    next_btn.first = next_btn
    next_btn.is_visible = AsyncMock(return_value=True)
    next_btn.get_attribute = AsyncMock(return_value="")
    next_btn.click = AsyncMock()

    other = MagicMock()
    other.count = AsyncMock(return_value=1)
    other.first = other
    other.is_visible = AsyncMock(return_value=True)
    other.click = AsyncMock()
    other.wait_for = AsyncMock()
    other.fill = AsyncMock()

    def locator_for(selector):
        if ".k-grid-content" in selector or "table.k-selectable" in selector or "table tbody tr" in selector:
            return rows
        if "next page" in selector.lower() or "k-i-arrow-e" in selector:
            return next_btn
        return other

    page.locator.side_effect = locator_for
    with patch.object(dallas_scraper, "detect_and_handle_captcha", new_callable=AsyncMock, return_value=True):
        with pytest.raises(RuntimeError, match="Pagination did not advance"):
            await dallas_scraper.search_by_party_name("Jane", "Doe", page)
    assert next_btn.click.await_count == expected_next_clicks


@pytest.mark.asyncio
async def test_navigate_to_search_loads_content(dallas_scraper):
    """Step A: Verifies page navigation, DOM readiness, and reload on blank body."""
    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.reload = AsyncMock()

    # Body is blank -> triggers reload
    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="")
    mock_content = MagicMock()
    mock_content.count = AsyncMock(return_value=1)
    mock_content.first.wait_for = AsyncMock()

    def locator_side_effect(selector):
        if "body" in selector:
            return mock_body
        return mock_content

    mock_page.locator.side_effect = locator_side_effect

    await dallas_scraper.navigate_to_search(mock_page)
    mock_page.goto.assert_called_once()
    mock_page.reload.assert_called_once()


@pytest.mark.asyncio
async def test_click_smart_search_and_verify_page(dallas_scraper):
    """Step B & C: Verifies clicking 'Smart Search' and verifying input readiness."""
    dallas_scraper.action_pacing_ms = 375
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_link = MagicMock()
    mock_link.count = AsyncMock(return_value=1)
    mock_link.is_visible = AsyncMock(return_value=True)
    mock_link.first.click = AsyncMock()

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.is_visible = AsyncMock(return_value=False)
    mock_input.first.wait_for = AsyncMock()

    def locator_side_effect(selector):
        if "Smart Search" in selector:
            return mock_link
        if "SearchCriteria" in selector:
            return mock_input
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await dallas_scraper.click_smart_search(mock_page)
    mock_link.first.click.assert_called_once()
    mock_page.wait_for_timeout.assert_any_await(375)

    is_loaded = await dallas_scraper.verify_search_page_loaded(mock_page)
    assert is_loaded is True


@pytest.mark.asyncio
async def test_check_and_handle_session_timeout(dallas_scraper):
    """Step G: If 'Session timeout warning' appears: click 'Continue session', wait for page."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_modal = MagicMock()
    mock_modal.count = AsyncMock(return_value=1)
    mock_modal.is_visible = AsyncMock(return_value=True)

    mock_continue_btn = MagicMock()
    mock_continue_btn.count = AsyncMock(return_value=1)
    mock_continue_btn.is_visible = AsyncMock(return_value=True)
    mock_continue_btn.first.click = AsyncMock()

    def locator_side_effect(selector):
        if "Continue session" in selector:
            return mock_continue_btn
        if "Session timeout warning" in selector or "session" in selector.lower():
            return mock_modal
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    handled = await dallas_scraper.check_and_handle_session_timeout(mock_page)
    assert handled is True
    mock_continue_btn.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_return_to_search_state_clears_inputs(dallas_scraper):
    """Section 4: Verifies return_to_search_state resets inputs for next unique name."""
    mock_page = MagicMock()
    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.is_visible = AsyncMock(return_value=True)
    mock_input.first.clear = AsyncMock()

    def locator_side_effect(selector):
        if "SearchCriteria" in selector:
            return mock_input
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await dallas_scraper.return_to_search_state(mock_page)
    mock_input.first.clear.assert_called_once()


@pytest.mark.asyncio
async def test_captcha_success_and_immediate_submit(dallas_scraper):
    """Step E & I: Once CAPTCHA succeeds, immediately clicks 'Submit'."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first.wait_for = AsyncMock()
    mock_input.first.fill = AsyncMock()
    mock_input.first.clear = AsyncMock()

    mock_submit_btn = MagicMock()
    mock_submit_btn.count = AsyncMock(return_value=1)
    mock_submit_btn.is_visible = AsyncMock(return_value=True)
    mock_submit_btn.first.click = AsyncMock()

    # Results grid row
    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="Results found")

    mock_row = MagicMock()
    cells = ["DC-26-000123", "SMITH, JANE VS DOE, JOHN", "01/15/2026", "OPEN", "CIVIL", "Public"]
    tds = [MagicMock(inner_text=AsyncMock(return_value=c)) for c in cells]
    tds_loc = MagicMock()
    tds_loc.count = AsyncMock(return_value=len(cells))
    tds_loc.nth.side_effect = lambda idx: tds[idx]
    mock_row.locator.return_value = tds_loc

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=1)
    mock_rows.nth.return_value = mock_row

    # Next button disabled
    mock_next = MagicMock()
    mock_next.count = AsyncMock(return_value=1)
    mock_next.is_visible = AsyncMock(return_value=True)
    mock_next.get_attribute = AsyncMock(return_value="k-state-disabled")

    def locator_side_effect(selector):
        if "SearchCriteria" in selector:
            return mock_input
        if "btnSSSubmit" in selector:
            return mock_submit_btn
        if "tbody tr" in selector:
            return mock_rows
        if selector == "body" or "body" in selector:
            return mock_body
        if "next" in selector.lower():
            return mock_next
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(dallas_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(dallas_scraper, "click_smart_search", AsyncMock()), \
         patch.object(dallas_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(dallas_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        results = await dallas_scraper.search_by_party_name(
            first_name="JANE",
            last_name="SMITH",
            page=mock_page,
        )

    mock_submit_btn.first.click.assert_called_once()
    assert len(results) == 1
    case = results[0]
    assert case["CaseNumber"] == "DC-26-000123"
    assert case["CaseStyle"] == "SMITH, JANE VS DOE, JOHN"
    assert case["FilingDate"] == "01/15/2026"
    assert case["CaseStatus"] == "OPEN"
    assert case["CaseType"] == "CIVIL"
    assert set(case) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}


@pytest.mark.asyncio
async def test_captcha_failure_and_retry_loop(dallas_scraper):
    """Step F & H: If CAPTCHA fails, reloads and retries up to max_attempts."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.reload = AsyncMock()

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first.wait_for = AsyncMock()
    mock_input.first.fill = AsyncMock()
    mock_input.first.clear = AsyncMock()

    def locator_side_effect(selector):
        if "SearchCriteria" in selector:
            return mock_input
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    # Attempt 1: False, Attempt 2: False, Attempt 3: False -> returns []
    with patch.object(dallas_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(dallas_scraper, "click_smart_search", AsyncMock()), \
         patch.object(dallas_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(dallas_scraper, "detect_and_handle_captcha", AsyncMock(return_value=False)):

        with pytest.raises(CaptchaResolutionError):
            await dallas_scraper.search_by_party_name(
                first_name="BOB",
                last_name="WILLIAMS",
                page=mock_page,
            )
    # With max_attempts=3, reload is called on attempts 1 and 2
    assert mock_page.reload.call_count == 2


@pytest.mark.asyncio
async def test_extract_all_columns_including_access_level_and_dynamic_headers(dallas_scraper):
    """Step K: Discovers dynamic table headers and extracts all columns including Access Level."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first.wait_for = AsyncMock()
    mock_input.first.fill = AsyncMock()
    mock_input.first.clear = AsyncMock()

    mock_submit_btn = MagicMock()
    mock_submit_btn.count = AsyncMock(return_value=1)
    mock_submit_btn.is_visible = AsyncMock(return_value=True)
    mock_submit_btn.first.click = AsyncMock()

    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="Cases Found")

    # Dynamic headers
    headers = ["Case Number", "Style / Defendant", "Filing Date", "Case Status", "Type", "Access Level", "Court"]
    mock_th_elements = [MagicMock(inner_text=AsyncMock(return_value=h)) for h in headers]
    mock_th_loc = MagicMock()
    mock_th_loc.count = AsyncMock(return_value=len(headers))
    mock_th_loc.nth.side_effect = lambda idx: mock_th_elements[idx]

    # Row cells
    cells = ["DC-26-9999", "WILLIAMS, BOB | DEFENDANT", "03/20/2026", "PENDING", "COUNTY COURT", "Restricted", "192ND DISTRICT COURT"]
    tds = [MagicMock(inner_text=AsyncMock(return_value=c)) for c in cells]
    tds_loc = MagicMock()
    tds_loc.count = AsyncMock(return_value=len(cells))
    tds_loc.nth.side_effect = lambda idx: tds[idx]

    mock_row = MagicMock()
    mock_row.locator.return_value = tds_loc

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=1)
    mock_rows.nth.return_value = mock_row

    # Next button disabled
    mock_next = MagicMock()
    mock_next.count = AsyncMock(return_value=1)
    mock_next.is_visible = AsyncMock(return_value=True)
    mock_next.get_attribute = AsyncMock(return_value="k-state-disabled")

    def locator_side_effect(selector):
        if "SearchCriteria" in selector:
            return mock_input
        if "btnSSSubmit" in selector:
            return mock_submit_btn
        if "thead th" in selector:
            return mock_th_loc
        if "tbody tr" in selector:
            return mock_rows
        if "body" in selector:
            return mock_body
        if "next" in selector.lower():
            return mock_next
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(dallas_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(dallas_scraper, "click_smart_search", AsyncMock()), \
         patch.object(dallas_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(dallas_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        results = await dallas_scraper.search_by_party_name(
            first_name="BOB",
            last_name="WILLIAMS",
            page=mock_page,
        )

    assert len(results) == 1
    case = results[0]
    assert case["CaseNumber"] == "DC-26-9999"
    # Pipe and dash sanitized from style
    assert "|" not in case["CaseStyle"]
    assert case["CaseStyle"] == "WILLIAMS, BOB  DEFENDANT"
    assert case["FilingDate"] == "03/20/2026"
    assert case["CaseStatus"] == "PENDING"
    assert case["CaseType"] == "COUNTY COURT"
    assert set(case) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}


@pytest.mark.asyncio
async def test_pagination_traversal(dallas_scraper):
    """Step L: Verifies Kendo UI multi-page pagination traversal."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.wait_for_function = AsyncMock()

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first.wait_for = AsyncMock()
    mock_input.first.fill = AsyncMock()
    mock_input.first.clear = AsyncMock()

    mock_submit_btn = MagicMock()
    mock_submit_btn.count = AsyncMock(return_value=1)
    mock_submit_btn.is_visible = AsyncMock(return_value=True)
    mock_submit_btn.first.click = AsyncMock()

    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="Results found")

    # Two source rows on separate pages may share a case number in V4.
    row1 = MagicMock()
    cells1 = ["CASE-DALLAS-001", "STYLE 1", "01/01/2026", "OPEN", "CIVIL", "Public"]
    tds1 = [MagicMock(inner_text=AsyncMock(return_value=c)) for c in cells1]
    tds1_loc = MagicMock()
    tds1_loc.count = AsyncMock(return_value=len(cells1))
    tds1_loc.nth.side_effect = lambda idx: tds1[idx]
    row1.locator.return_value = tds1_loc

    row2 = MagicMock()
    cells2 = ["CASE-DALLAS-001", "STYLE 2", "02/01/2026", "CLOSED", "CIVIL", "Public"]
    tds2 = [MagicMock(inner_text=AsyncMock(return_value=c)) for c in cells2]
    tds2_loc = MagicMock()
    tds2_loc.count = AsyncMock(return_value=len(cells2))
    tds2_loc.nth.side_effect = lambda idx: tds2[idx]
    row2.locator.return_value = tds2_loc

    current_page = {"val": 1}

    def rows_count():
        return 1

    def rows_nth(idx):
        if current_page["val"] == 1:
            return row1
        return row2

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(side_effect=rows_count)
    mock_rows.nth = MagicMock(side_effect=rows_nth)

    def on_next_click():
        current_page["val"] += 1

    mock_next_btn = MagicMock()
    mock_next_btn.count = AsyncMock(return_value=1)
    mock_next_btn.is_visible = AsyncMock(return_value=True)
    mock_next_btn.first.click = AsyncMock(side_effect=on_next_click)

    def next_attr(attr):
        if current_page["val"] >= 2:
            return "k-link k-state-disabled"
        return "k-link"

    mock_next_btn.get_attribute = AsyncMock(side_effect=next_attr)

    def locator_side_effect(selector):
        if "SearchCriteria" in selector:
            return mock_input
        if "btnSSSubmit" in selector:
            return mock_submit_btn
        if "tbody tr" in selector:
            return mock_rows
        if selector == "body" or "body" in selector:
            return mock_body
        if "next" in selector.lower() or "arrow" in selector.lower():
            return mock_next_btn
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(dallas_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(dallas_scraper, "click_smart_search", AsyncMock()), \
         patch.object(dallas_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(dallas_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        results = await dallas_scraper.search_by_party_name(
            first_name="TEST",
            last_name="USER",
            page=mock_page,
        )

    assert len(results) == 2
    assert results[0]["CaseNumber"] == "CASE-DALLAS-001"
    assert results[1]["CaseNumber"] == "CASE-DALLAS-001"
    assert results[1]["CaseStyle"] == "STYLE 2"
    mock_next_btn.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_dallas_persistence_format(dallas_scraper):
    """Step M: Verifies extracted result matches te_jsonbody_dallas schema."""
    case_result = {
        "CaseNumber": "DC-26-000999",
        "CaseStyle": "DALLAS PLAINTIFF VS DEFENDANT",
        "CountyWebsite": dallas_scraper.base_url,
        "FilingDate": "06/01/2026",
        "CaseStatus": "ACTIVE",
        "CaseType": "DISTRICT COURT - CIVIL",
        "AccessLevel": "Public",
    }

    assert "CaseNumber" in case_result
    assert "CaseStyle" in case_result
    assert "FilingDate" in case_result
    assert "CaseStatus" in case_result
    assert "CaseType" in case_result
    assert "AccessLevel" in case_result
    assert "CountyWebsite" in case_result
    assert "courtsportal.dallascounty.org" in case_result["CountyWebsite"]


@pytest.mark.asyncio
async def test_dallas_default_initialization_settings():
    """Verifies default settings: 120s captcha wait, 2 max attempts, Dallas URL."""
    scraper = DallasScraper()
    assert scraper.captcha_wait_seconds == 120
    assert scraper.max_attempts == 2
    assert "courtsportal.dallascounty.org" in scraper.base_url


@pytest.mark.asyncio
async def test_navigate_to_search_reloads_on_short_body(dallas_scraper):
    """Step a: Verifies reload is triggered when body text has length < 5."""
    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.reload = AsyncMock()

    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="   ")  # whitespace only, len < 5

    def locator_side_effect(selector):
        if "body" in selector:
            return mock_body
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await dallas_scraper.navigate_to_search(mock_page)
    mock_page.goto.assert_called_once()
    mock_page.reload.assert_called_once()


@pytest.mark.asyncio
async def test_session_timeout_redirects_to_home_recovery(dallas_scraper):
    """Exception 2: Verifies restart from step b (click_smart_search) if redirected to portal home."""
    mock_page = MagicMock()
    mock_page.url = "https://courtsportal.dallascounty.org/DALLASPROD/Home/"
    mock_page.wait_for_timeout = AsyncMock()

    mock_modal = MagicMock()
    mock_modal.count = AsyncMock(return_value=1)
    mock_modal.is_visible = AsyncMock(return_value=True)

    mock_continue_btn = MagicMock()
    mock_continue_btn.count = AsyncMock(return_value=1)
    mock_continue_btn.is_visible = AsyncMock(return_value=True)
    mock_continue_btn.first.click = AsyncMock()

    def locator_side_effect(selector):
        if "Continue session" in selector:
            return mock_continue_btn
        if "Session timeout warning" in selector:
            return mock_modal
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(dallas_scraper, "click_smart_search", AsyncMock()) as mock_smart, \
         patch.object(dallas_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)) as mock_verify:
        handled = await dallas_scraper.check_and_handle_session_timeout(mock_page)

    assert handled is True
    mock_continue_btn.first.click.assert_called_once()
    mock_smart.assert_called_once()
    mock_verify.assert_called_once()


@pytest.mark.asyncio
async def test_exact_portlet_button_selector_targeted(dallas_scraper):
    """Step b: Verifies clicking exact portlet-buttons anchor for Dallas Smart Search."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_portlet_link = MagicMock()
    mock_portlet_link.count = AsyncMock(return_value=1)
    mock_portlet_link.is_visible = AsyncMock(return_value=True)
    mock_portlet_link.first.click = AsyncMock()

    captured_selectors = []

    def locator_side_effect(selector):
        captured_selectors.append(selector)
        if "a.portlet-buttons" in selector:
            return mock_portlet_link
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await dallas_scraper.click_smart_search(mock_page)
    mock_portlet_link.first.click.assert_called_once()
    assert any("/DALLASPROD/Home/Dashboard/29" in s for s in captured_selectors)


@pytest.mark.asyncio
async def test_exact_submit_button_selector_targeted(dallas_scraper):
    """Step g: Verifies clicking exact input#btnSSSubmit with name='Search' and value='Submit'."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first.wait_for = AsyncMock()
    mock_input.first.fill = AsyncMock()
    mock_input.first.clear = AsyncMock()

    mock_submit_btn = MagicMock()
    mock_submit_btn.count = AsyncMock(return_value=1)
    mock_submit_btn.is_visible = AsyncMock(return_value=True)
    mock_submit_btn.first.click = AsyncMock()

    captured_selectors = []

    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="no cases match your search")

    def locator_side_effect(selector):
        captured_selectors.append(selector)
        if "btnSSSubmit" in selector:
            return mock_submit_btn
        if "SearchCriteria" in selector:
            return mock_input
        if "body" in selector:
            return mock_body
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(dallas_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(dallas_scraper, "click_smart_search", AsyncMock()), \
         patch.object(dallas_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(dallas_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        await dallas_scraper.search_by_party_name(
            first_name="JOHN",
            last_name="DOE",
            page=mock_page,
        )

    mock_submit_btn.first.click.assert_called_once()
    assert any("input#btnSSSubmit" in s for s in captured_selectors)


@pytest.mark.asyncio
async def test_v4_case_style_reads_detail_tab_and_closes_it(dallas_scraper):
    page = MagicMock()
    detail_page = MagicMock()
    detail_page.goto = AsyncMock()
    detail_page.close = AsyncMock()
    detail_page.locator.return_value.first.inner_text = AsyncMock(return_value="SMITH - VS | JONES")
    page.context.new_page = AsyncMock(return_value=detail_page)

    style = await dallas_scraper._read_v4_case_style(page, "/DALLASPROD/Case/42")

    assert style == "SMITH  VS  JONES"
    detail_page.goto.assert_awaited_once_with(
        "https://courtsportal.dallascounty.org/DALLASPROD/Case/42",
        wait_until="domcontentloaded",
        timeout=dallas_scraper.timeout_ms,
    )
    assert "p.text-primary" in detail_page.locator.call_args.args[0]
    detail_page.close.assert_awaited_once()
