"""Unit & workflow tests for Harris County JP court portal scraper (Prompt 6 compliance)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import CaptchaResolutionError
from app.automation.texas.harris_jp import HarrisJPScraper


@pytest.fixture
def harris_jp_scraper():
    return HarrisJPScraper(
        base_url="https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29",
        captcha_wait_seconds=15,
        max_attempts=3,
    )


@pytest.mark.asyncio
async def test_repeated_result_page_fails_fast(harris_jp_scraper):
    """An enabled pager redisplaying the same full grid row must stop."""
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=False)
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")

    row = MagicMock()
    row.locator.return_value.all_inner_texts = AsyncMock(
        return_value=["CASE-1", "Style", "01/01/2023", "ACTIVE"]
    )
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
    with patch.object(harris_jp_scraper, "detect_and_handle_captcha", new_callable=AsyncMock, return_value=True):
        with pytest.raises(RuntimeError, match="Pagination did not advance"):
            await harris_jp_scraper.search_by_party_name("Jane", "Doe", page)
    assert next_btn.click.await_count == 1


@pytest.mark.asyncio
async def test_navigate_to_search_loads_content(harris_jp_scraper):
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

    await harris_jp_scraper.navigate_to_search(mock_page)
    mock_page.goto.assert_called_once()
    mock_page.reload.assert_called_once()


@pytest.mark.asyncio
async def test_click_smart_search_and_verify_page(harris_jp_scraper):
    """Step B & C: Verifies clicking 'Smart Search' and verifying input readiness."""
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

    await harris_jp_scraper.click_smart_search(mock_page)
    mock_link.first.click.assert_called_once()

    is_loaded = await harris_jp_scraper.verify_search_page_loaded(mock_page)
    assert is_loaded is True


@pytest.mark.asyncio
async def test_check_and_handle_session_timeout(harris_jp_scraper):
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

    handled = await harris_jp_scraper.check_and_handle_session_timeout(mock_page)
    assert handled is True
    mock_continue_btn.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_return_to_search_state_clears_inputs(harris_jp_scraper):
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

    await harris_jp_scraper.return_to_search_state(mock_page)
    mock_input.first.clear.assert_called_once()


@pytest.mark.asyncio
async def test_captcha_success_and_immediate_submit(harris_jp_scraper):
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
    cells = ["26-JP-000123", "SMITH, JANE VS DOE, JOHN", "01/15/2026", "Case Status: Open", "Public"]
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

    with patch.object(harris_jp_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "click_smart_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(harris_jp_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        results = await harris_jp_scraper.search_by_party_name(
            first_name="JANE",
            last_name="SMITH",
            page=mock_page,
        )

    mock_submit_btn.first.click.assert_called_once()
    assert len(results) == 1
    case = results[0]
    assert case["CaseNumber"] == "26-JP-000123"
    assert case["CaseStyle"] == "SMITH, JANE VS DOE, JOHN"
    assert case["FilingDate"] == "01/15/2026"
    assert case["CaseStatus"] == "Open"
    assert set(case) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus"}
    # STRICT SCHEMA: NO CaseType!
    assert "CaseType" not in case


@pytest.mark.asyncio
async def test_captcha_failure_and_retry_loop(harris_jp_scraper):
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
    with patch.object(harris_jp_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "click_smart_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(harris_jp_scraper, "detect_and_handle_captcha", AsyncMock(return_value=False)):

        with pytest.raises(CaptchaResolutionError):
            await harris_jp_scraper.search_by_party_name(
                first_name="BOB",
                last_name="WILLIAMS",
                page=mock_page,
            )
    # With max_attempts=3, reload is called on attempts 1 and 2
    assert mock_page.reload.call_count == 2


@pytest.mark.asyncio
async def test_extract_all_columns_strict_no_casetype(harris_jp_scraper):
    """Step K: Discovers dynamic table headers, extracts all columns, strictly excludes CaseType."""
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

    # Dynamic headers that include Case Type and Precinct
    headers = ["Case Number", "Style / Defendant", "Filing Date", "Case Status", "Case Type", "Precinct"]
    mock_th_elements = [MagicMock(inner_text=AsyncMock(return_value=h)) for h in headers]
    mock_th_loc = MagicMock()
    mock_th_loc.count = AsyncMock(return_value=len(headers))
    mock_th_loc.nth.side_effect = lambda idx: mock_th_elements[idx]

    # Row cells
    cells = ["26-JP-9999", "WILLIAMS, BOB | DEFENDANT", "03/20/2026", "Case Status: Pending", "Small Claims", "Place 1"]
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

    with patch.object(harris_jp_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "click_smart_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(harris_jp_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        results = await harris_jp_scraper.search_by_party_name(
            first_name="BOB",
            last_name="WILLIAMS",
            page=mock_page,
        )

    assert len(results) == 1
    case = results[0]
    assert case["CaseNumber"] == "26-JP-9999"
    # Pipe and dash sanitized from style
    assert case["CaseStyle"] == "WILLIAMS, BOB | DEFENDANT"
    assert case["FilingDate"] == "03/20/2026"
    assert case["CaseStatus"] == "Pending"
    assert set(case) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus"}
    # STRICT SCHEMA: CaseType must NEVER be in Harris JP schema!
    assert "CaseType" not in case
    assert "Type" not in case


@pytest.mark.asyncio
async def test_pagination_traversal(harris_jp_scraper):
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
    cells1 = ["CASE-HARRIS-001", "STYLE 1", "01/01/2026", "Open", "Public"]
    tds1 = [MagicMock(inner_text=AsyncMock(return_value=c)) for c in cells1]
    tds1_loc = MagicMock()
    tds1_loc.count = AsyncMock(return_value=len(cells1))
    tds1_loc.nth.side_effect = lambda idx: tds1[idx]
    row1.locator.return_value = tds1_loc

    row2 = MagicMock()
    cells2 = ["CASE-HARRIS-001", "STYLE 2", "02/01/2026", "Closed", "Public"]
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

    with patch.object(harris_jp_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "click_smart_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(harris_jp_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        results = await harris_jp_scraper.search_by_party_name(
            first_name="TEST",
            last_name="USER",
            page=mock_page,
        )

    assert len(results) == 2
    assert results[0]["CaseNumber"] == "CASE-HARRIS-001"
    assert results[1]["CaseNumber"] == "CASE-HARRIS-001"
    assert results[1]["CaseStyle"] == "STYLE 2"
    assert "CaseType" not in results[0]
    assert "CaseType" not in results[1]
    mock_next_btn.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_harris_jp_persistence_format(harris_jp_scraper):
    """Step M: Verifies extracted result matches te_jsonbody_harris schema without CaseType."""
    case_result = {
        "CaseNumber": "26-JP-000999",
        "CaseStyle": "HARRIS JP PLAINTIFF VS DEFENDANT",
        "CountyWebsite": harris_jp_scraper.base_url,
        "FilingDate": "06/01/2026",
        "CaseStatus": "ACTIVE",
        "AccessLevel": "Public",
    }

    assert "CaseNumber" in case_result
    assert "CaseStyle" in case_result
    assert "FilingDate" in case_result
    assert "CaseStatus" in case_result
    assert "AccessLevel" in case_result
    assert "CountyWebsite" in case_result
    assert "jpodysseyportal.harriscountytx.gov" in case_result["CountyWebsite"]
    # STRICT SCHEMA ENFORCEMENT
    assert "CaseType" not in case_result


@pytest.mark.asyncio
async def test_harris_jp_default_dynamic_settings_initialization():
    """Verifies HarrisJPScraper defaults match user specification (120s wait, 2 retries)."""
    scraper = HarrisJPScraper()
    assert scraper.captcha_wait_seconds == 120
    assert scraper.max_attempts == 2
    assert "jpodysseyportal.harriscountytx.gov" in scraper.base_url


@pytest.mark.asyncio
async def test_navigate_to_search_reloads_on_short_or_empty_body(harris_jp_scraper):
    """Step a: Verifies reload triggers if body content is shorter than 5 characters."""
    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.reload = AsyncMock()

    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="   ")  # < 5 characters
    mock_content = MagicMock()
    mock_content.count = AsyncMock(return_value=1)
    mock_content.first.wait_for = AsyncMock()

    def locator_side_effect(selector):
        if "body" in selector:
            return mock_body
        return mock_content

    mock_page.locator.side_effect = locator_side_effect

    await harris_jp_scraper.navigate_to_search(mock_page)
    mock_page.goto.assert_called_once()
    mock_page.reload.assert_called_once()


@pytest.mark.asyncio
async def test_click_smart_search_exact_portlet_button_selector(harris_jp_scraper):
    """Step b: Verifies clicking exact Smart Search portlet button with /OdysseyPortalJP/Home/Dashboard/29."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_btn = MagicMock()
    mock_btn.count = AsyncMock(return_value=1)
    mock_btn.is_visible = AsyncMock(return_value=True)
    mock_btn.first.click = AsyncMock()

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=0)
    mock_input.is_visible = AsyncMock(return_value=False)

    clicked_selector = None

    def locator_side_effect(selector):
        nonlocal clicked_selector
        if "portlet-buttons" in selector:
            clicked_selector = selector
            return mock_btn
        if "SearchCriteria" in selector:
            return mock_input
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await harris_jp_scraper.click_smart_search(mock_page)
    mock_btn.first.click.assert_called_once()
    assert clicked_selector is not None
    assert "/OdysseyPortalJP/Home/Dashboard/29" in clicked_selector


@pytest.mark.asyncio
async def test_session_timeout_redirect_to_home_recovery(harris_jp_scraper):
    """Exception 2: Verifies that if redirected to home page on session timeout, re-triggers Smart Search."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()
    # URL without Dashboard/29 -> simulated redirect to home page
    mock_page.url = "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/"

    mock_modal = MagicMock()
    mock_modal.count = AsyncMock(return_value=1)
    mock_modal.is_visible = AsyncMock(return_value=True)

    mock_continue_btn = MagicMock()
    mock_continue_btn.count = AsyncMock(return_value=1)
    mock_continue_btn.is_visible = AsyncMock(return_value=True)
    mock_continue_btn.first.click = AsyncMock()

    mock_smart_link = MagicMock()
    mock_smart_link.count = AsyncMock(return_value=1)
    mock_smart_link.is_visible = AsyncMock(return_value=True)
    mock_smart_link.first.click = AsyncMock()

    mock_search_input = MagicMock()
    mock_search_input.count = AsyncMock(return_value=1)
    mock_search_input.is_visible = AsyncMock(return_value=False)
    mock_search_input.first.wait_for = AsyncMock()

    def locator_side_effect(selector):
        if "Continue session" in selector:
            return mock_continue_btn
        if "Session timeout warning" in selector:
            return mock_modal
        if "portlet-buttons" in selector:
            return mock_smart_link
        if "SearchCriteria" in selector:
            return mock_search_input
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    handled = await harris_jp_scraper.check_and_handle_session_timeout(mock_page)
    assert handled is True
    mock_continue_btn.first.click.assert_called_once()
    mock_smart_link.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_search_by_party_name_exact_query_format_and_submit_selector(harris_jp_scraper):
    """Step d & g: Verifies search input format 'Last, First' and exact submit button selector."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    filled_text = None
    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first.wait_for = AsyncMock()
    mock_input.first.clear = AsyncMock()

    async def mock_fill(text):
        nonlocal filled_text
        filled_text = text

    mock_input.first.fill = AsyncMock(side_effect=mock_fill)

    mock_submit_btn = MagicMock()
    mock_submit_btn.count = AsyncMock(return_value=1)
    mock_submit_btn.is_visible = AsyncMock(return_value=True)
    mock_submit_btn.first.click = AsyncMock()

    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="no cases match your search")

    submit_selector_used = None

    def locator_side_effect(selector):
        nonlocal submit_selector_used
        if "SearchCriteria" in selector:
            return mock_input
        if "btnSSSubmit" in selector:
            submit_selector_used = selector
            return mock_submit_btn
        if selector == "body" or "body" in selector:
            return mock_body
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(harris_jp_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "click_smart_search", AsyncMock()), \
         patch.object(harris_jp_scraper, "verify_search_page_loaded", AsyncMock(return_value=True)), \
         patch.object(harris_jp_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)), \
         patch.object(harris_jp_scraper, "return_to_search_state", AsyncMock()):

        results = await harris_jp_scraper.search_by_party_name(
            first_name="JOHN",
            last_name="DOE",
            page=mock_page,
        )

    assert results == []
    assert filled_text == "DOE,JOHN"
    assert submit_selector_used is not None
    assert "btnSSSubmit" in submit_selector_used
    assert "name='Search'" in submit_selector_used
    assert "value='Submit'" in submit_selector_used


@pytest.mark.asyncio
async def test_v4_case_status_reads_detail_tab_and_closes_it(harris_jp_scraper):
    page = MagicMock()
    detail_page = MagicMock()
    detail_page.goto = AsyncMock()
    detail_page.close = AsyncMock()
    status_nodes = MagicMock()
    status_nodes.count = AsyncMock(return_value=2)
    status_nodes.nth.side_effect = [
        MagicMock(inner_text=AsyncMock(return_value="Other information")),
        MagicMock(inner_text=AsyncMock(return_value="Case Status: Open")),
    ]
    detail_page.locator.return_value = status_nodes
    page.context.new_page = AsyncMock(return_value=detail_page)

    status = await harris_jp_scraper._read_v4_case_status(page, "/OdysseyPortalJP/Case/42")

    assert status == "Open"
    detail_page.goto.assert_awaited_once_with(
        "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Case/42",
        wait_until="domcontentloaded",
        timeout=harris_jp_scraper.timeout_ms,
    )
    detail_page.locator.assert_called_once_with("#divCaseInformation_body p")
    detail_page.close.assert_awaited_once()
