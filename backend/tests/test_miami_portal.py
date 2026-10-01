"""Unit & workflow tests for Miami-Dade County court portal scraper (Prompt 3 compliance)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.base import PortalAuthenticationError, PortalConfigurationError
from app.automation.florida.miami import MiamiDadeScraper


@pytest.fixture
def miami_scraper():
    return MiamiDadeScraper(
        base_url="https://www2.miamidadeclerk.gov/ocs/",
        username="apoorvnigam07@gmail.com",
        password="TestPassword123!",
        requires_login=True,
    )


@pytest.mark.asyncio
async def test_navigate_to_search_loads_content(miami_scraper):
    """Section 3: Verifies page navigation, DOM readiness, and reload on blank body."""
    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.reload = AsyncMock()

    # Case 1: Body is blank -> should reload
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

    await miami_scraper.navigate_to_search(mock_page)
    mock_page.goto.assert_called_once()
    mock_page.reload.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_authenticated_skips_when_logged_in(miami_scraper):
    """Section 4: Verifies login is skipped if account is already authenticated."""
    mock_page = MagicMock()
    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="Welcome, Apoorv! My Desk - Case Management")
    mock_logout = MagicMock()
    mock_logout.count = AsyncMock(return_value=1)
    mock_logout.first.is_visible = AsyncMock(return_value=True)

    def locator_side_effect(selector):
        if "body" in selector:
            return mock_body
        if "Logout" in selector:
            return mock_logout
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.ensure_authenticated(mock_page)
    # Register/Login should not be clicked
    assert mock_page.goto.call_count == 0


@pytest.mark.asyncio
async def test_ensure_authenticated_executes_login_flow(miami_scraper):
    """Section 4: Verifies Login Steps A-D (Register/Login, fill credentials, submit, dismiss popup)."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.wait_for_function = AsyncMock(return_value=True)
    mock_page.keyboard.press = AsyncMock()

    mock_body = MagicMock()
    mock_body.inner_text = AsyncMock(return_value="Guest User. Please login to access services.")

    mock_reg_login = MagicMock()
    mock_reg_login.count = AsyncMock(return_value=1)
    mock_reg_login.is_visible = AsyncMock(return_value=True)
    mock_reg_login.first.click = AsyncMock()

    mock_email = MagicMock()
    mock_email.count = AsyncMock(return_value=1)
    mock_email.first.wait_for = AsyncMock()
    mock_email.first.fill = AsyncMock()
    mock_email.first.clear = AsyncMock()

    mock_pwd = MagicMock()
    mock_pwd.count = AsyncMock(return_value=1)
    mock_pwd.first.fill = AsyncMock()
    mock_pwd.first.clear = AsyncMock()

    mock_login_btn = MagicMock()
    mock_login_btn.count = AsyncMock(return_value=1)
    mock_login_btn.is_visible = AsyncMock(return_value=True)
    mock_login_btn.first.click = AsyncMock()

    def locator_side_effect(selector):
        if "body" in selector:
            return mock_body
        if "Register/Login" in selector:
            return mock_reg_login
        if "txtUserName" in selector or "email" in selector:
            return mock_email
        if "txtPassword" in selector or "password" in selector:
            return mock_pwd
        if "btnLogin" in selector or "LOGIN" in selector:
            return mock_login_btn
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.ensure_authenticated(mock_page)

    mock_reg_login.first.click.assert_called_once()
    mock_login_btn.first.click.assert_called_once()
    mock_page.wait_for_function.assert_awaited_once()
    mock_page.keyboard.press.assert_called_with("Escape")


@pytest.mark.asyncio
async def test_required_login_rejects_missing_saved_credentials():
    scraper = MiamiDadeScraper(username="", password="", requires_login=True)
    with pytest.raises(PortalConfigurationError, match="saved Miami username/password is missing"):
        await scraper.ensure_authenticated(MagicMock())


@pytest.mark.asyncio
async def test_required_login_fails_if_welcome_never_appears(miami_scraper):
    page = MagicMock()
    page.url = "https://www2.miamidadeclerk.gov/ocs"
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.wait_for_function = AsyncMock(side_effect=TimeoutError)
    page.keyboard.press = AsyncMock()
    absent = MagicMock()
    absent.count = AsyncMock(return_value=0)
    page.locator.return_value = absent

    with pytest.raises(PortalAuthenticationError, match="no authenticated Welcome control"):
        await miami_scraper.ensure_authenticated(page)


@pytest.mark.asyncio
async def test_missing_login_configuration_does_not_retry(miami_scraper):
    page = MagicMock()
    page.reload = AsyncMock()
    with patch.object(
        miami_scraper,
        "search_by_party_name",
        new_callable=AsyncMock,
        side_effect=PortalConfigurationError("missing Miami credentials"),
    ) as search:
        with pytest.raises(PortalConfigurationError):
            await miami_scraper.search_on_page(page, "Alice", "Smith")
    search.assert_awaited_once()
    page.reload.assert_not_called()


@pytest.mark.asyncio
async def test_verify_portal_url_redirects_back(miami_scraper):
    """Section 5: Verifies tab navigates back if diverted to auth portal."""
    mock_page = MagicMock()
    mock_page.url = "https://www2.miamidadeclerk.gov/usermanagementservices/login"
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()

    await miami_scraper.verify_portal_url(mock_page)
    mock_page.goto.assert_called_once_with(
        miami_scraper.base_url,
        wait_until="domcontentloaded",
        timeout=30000,
    )


@pytest.mark.asyncio
async def test_select_party_search_tab_and_refresh(miami_scraper):
    """Section 6: Step A ('Party Name') and Step B ('Refresh')."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_party = MagicMock()
    mock_party.count = AsyncMock(return_value=1)
    mock_party.is_visible = AsyncMock(return_value=True)
    mock_party.first.click = AsyncMock()

    mock_refresh = MagicMock()
    mock_refresh.count = AsyncMock(return_value=1)
    mock_refresh.is_visible = AsyncMock(return_value=True)
    mock_refresh.first.click = AsyncMock()

    def locator_side_effect(selector):
        if "Party Name" in selector or "rdoPerson" in selector:
            return mock_party
        if "Refresh" in selector:
            return mock_refresh
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.select_party_search_tab(mock_page)
    mock_party.first.click.assert_called_once()
    mock_refresh.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_dismiss_search_criteria_popup(miami_scraper):
    """Section 6: Step I - Detects 'YOUR SEARCH CRITERIA' popup and closes it."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_modal = MagicMock()
    mock_modal.count = AsyncMock(return_value=1)
    mock_modal.is_visible = AsyncMock(return_value=True)

    mock_close = MagicMock()
    mock_close.count = AsyncMock(return_value=1)
    mock_close.is_visible = AsyncMock(return_value=True)
    mock_close.first.click = AsyncMock()

    def locator_side_effect(selector):
        if "SEARCH CRITERIA" in selector:
            return mock_modal
        if "btn-close" in selector or "Close" in selector:
            return mock_close
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.check_and_dismiss_search_criteria_popup(mock_page)
    mock_close.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_verify_and_enable_table_view(miami_scraper):
    """Section 6: Step F - Verifies Table View is enabled, clicks toggle if not active."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_table = MagicMock()
    mock_table.count = AsyncMock(return_value=0)
    mock_table.is_visible = AsyncMock(return_value=False)

    mock_toggle = MagicMock()
    mock_toggle.count = AsyncMock(return_value=1)
    mock_toggle.is_visible = AsyncMock(return_value=True)
    mock_toggle.first.click = AsyncMock()

    def locator_side_effect(selector):
        if "tblResults" in selector or "table.table" in selector:
            return mock_table
        if "Table View" in selector:
            return mock_toggle
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.verify_and_enable_table_view(mock_page)
    mock_toggle.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_return_to_search_state_clears_inputs(miami_scraper):
    """Section 7: Verifies return_to_search_state resets inputs for next unique name."""
    mock_page = MagicMock()
    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.is_visible = AsyncMock(return_value=True)
    mock_last.first.clear = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.is_visible = AsyncMock(return_value=True)
    mock_first.first.clear = AsyncMock()

    mock_radio = MagicMock()
    mock_radio.count = AsyncMock(return_value=1)
    mock_radio.is_visible = AsyncMock(return_value=True)
    mock_radio.first.click = AsyncMock()

    def locator_side_effect(selector):
        if "LastName" in selector:
            return mock_last
        if "FirstName" in selector:
            return mock_first
        if "rdoPerson" in selector:
            return mock_radio
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.return_to_search_state(mock_page)
    mock_last.first.clear.assert_called_once()
    mock_first.first.clear.assert_called_once()
    mock_radio.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_search_by_party_name_table_view_and_columns(miami_scraper):
    """Section 6: Full search workflow extracting ALL columns from Table View."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    # Form inputs
    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first.wait_for = AsyncMock()
    mock_last.first.fill = AsyncMock()
    mock_last.first.clear = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.first.fill = AsyncMock()
    mock_first.first.clear = AsyncMock()

    mock_date_from = MagicMock()
    mock_date_from.count = AsyncMock(return_value=1)
    mock_date_from.first.fill = AsyncMock()

    mock_search_btn = MagicMock()
    mock_search_btn.count = AsyncMock(return_value=1)
    mock_search_btn.is_visible = AsyncMock(return_value=True)
    mock_search_btn.first.click = AsyncMock()

    # Results indicator
    mock_indicator = MagicMock()
    mock_indicator.first.wait_for = AsyncMock()

    # Dynamic Headers
    headers = ["Local Case #", "State Case #", "Section", "Case Type", "Filing Date", "Case Status", "Case Style", "Judge"]
    mock_th_elements = [MagicMock(inner_text=AsyncMock(return_value=h)) for h in headers]
    mock_th_loc = MagicMock()
    mock_th_loc.count = AsyncMock(return_value=len(headers))
    mock_th_loc.nth.side_effect = lambda idx: mock_th_elements[idx]

    # Row data: Local, State, Section, Type, FilingDate, Status, Style, Judge
    cells = ["2026-012345-CC-05", "132026CC012345000001", "05 - Civil", "COUNTY CIVIL", "04/15/2026", "OPEN", "DOE, JOHN VS SMITH, JANE", "HON. JUDGE TEST"]
    mock_td_elements = [MagicMock(inner_text=AsyncMock(return_value=c)) for c in cells]
    mock_tds_loc = MagicMock()
    mock_tds_loc.count = AsyncMock(return_value=len(cells))
    mock_tds_loc.nth.side_effect = lambda idx: mock_td_elements[idx]

    mock_row = MagicMock()
    mock_row.locator.return_value = mock_tds_loc

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(return_value=1)
    mock_rows.nth.return_value = mock_row

    # Next button (disabled)
    mock_next = MagicMock()
    mock_next.count = AsyncMock(return_value=1)
    mock_next.is_visible = AsyncMock(return_value=True)
    mock_next.get_attribute = AsyncMock(return_value="true")

    def locator_side_effect(selector):
        if "LastName" in selector:
            return mock_last
        if "FirstName" in selector:
            return mock_first
        if "filingDateFrom" in selector:
            return mock_date_from
        if "btnSearch" in selector:
            return mock_search_btn
        if "thead th" in selector:
            return mock_th_loc
        if "tbody tr" in selector:
            return mock_rows
        if "next" in selector.lower():
            return mock_next
        if "tblResults" in selector:
            return mock_indicator
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(miami_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(miami_scraper, "ensure_authenticated", AsyncMock()), \
         patch.object(miami_scraper, "verify_portal_url", AsyncMock()), \
         patch.object(miami_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        results = await miami_scraper.search_by_party_name(
            first_name="JOHN",
            last_name="DOE",
            page=mock_page,
            date_of_loss="01/01/2026",
        )

    assert len(results) == 1
    case = results[0]
    assert case["CaseNumber"] == "2026-012345-CC-05"
    assert case["CaseType"] == "COUNTY CIVIL"
    assert case["FilingDate"] == "04/15/2026"
    assert case["CaseStatus"] == "OPEN"
    assert case["CaseStyle"] == "DOE, JOHN VS SMITH, JANE"
    assert set(case) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}


@pytest.mark.asyncio
@pytest.mark.parametrize("repeated_page", [False, True])
async def test_search_by_party_name_with_pagination(miami_scraper, repeated_page):
    """Traverse new pages and reject a pager that repeats the same source rows."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    # Headers
    mock_th_loc = MagicMock()
    mock_th_loc.count = AsyncMock(return_value=0)

    # 2 pages: page 1 has case 1, page 2 has case 2
    row1 = MagicMock()
    cells1 = ["CASE-P1-001", "STATE-P1-001", "DIV A", "CIVIL", "01/10/2026", "OPEN", "DOE VS ROE"]
    tds1 = [MagicMock(inner_text=AsyncMock(return_value=c)) for c in cells1]
    tds1_loc = MagicMock()
    tds1_loc.count = AsyncMock(return_value=len(cells1))
    tds1_loc.nth.side_effect = lambda idx: tds1[idx]
    row1.locator.return_value = tds1_loc

    row2 = MagicMock()
    cells2 = cells1 if repeated_page else ["CASE-P1-001", "STATE-P2-002", "DIV B", "CIVIL", "02/10/2026", "CLOSED", "DOE VS BAKER"]
    tds2 = [MagicMock(inner_text=AsyncMock(return_value=c)) for c in cells2]
    tds2_loc = MagicMock()
    tds2_loc.count = AsyncMock(return_value=len(cells2))
    tds2_loc.nth.side_effect = lambda idx: tds2[idx]
    row2.locator.return_value = tds2_loc

    call_count = {"rows": 0, "next": 0}

    def rows_count():
        call_count["rows"] += 1
        return 1

    def rows_nth(idx):
        if call_count["rows"] <= 1:
            return row1
        return row2

    mock_rows = MagicMock()
    mock_rows.count = AsyncMock(side_effect=rows_count)
    mock_rows.nth = MagicMock(side_effect=rows_nth)

    current_page = {"val": 1}

    def on_next_click():
        current_page["val"] += 1

    mock_next_btn = MagicMock()
    mock_next_btn.count = AsyncMock(return_value=1)
    mock_next_btn.is_visible = AsyncMock(return_value=True)
    mock_next_btn.first.click = AsyncMock(side_effect=on_next_click)

    def next_attr(attr):
        if attr in ("disabled", "aria-disabled"):
            return "true" if current_page["val"] >= 2 else None
        elif attr == "class":
            return "paginate_button next disabled" if current_page["val"] >= 2 else "paginate_button next"
        return None

    mock_next_btn.get_attribute = AsyncMock(side_effect=next_attr)

    mock_search = MagicMock()
    mock_search.count = AsyncMock(return_value=1)
    mock_search.first = mock_search
    mock_search.click = AsyncMock()

    def locator_side_effect(selector):
        if "button-green" in selector:
            return mock_search
        if "tbody tr" in selector:
            return mock_rows
        if "thead th" in selector:
            return mock_th_loc
        if "next" in selector.lower():
            return mock_next_btn
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(miami_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(miami_scraper, "ensure_authenticated", AsyncMock()), \
         patch.object(miami_scraper, "verify_portal_url", AsyncMock()), \
         patch.object(miami_scraper, "detect_and_handle_captcha", AsyncMock(return_value=True)):

        if repeated_page:
            with pytest.raises(RuntimeError, match="Pagination did not advance"):
                await miami_scraper.search_by_party_name(
                    first_name="JOHN",
                    last_name="DOE",
                    page=mock_page,
                )
        else:
            results = await miami_scraper.search_by_party_name(
                first_name="JOHN",
                last_name="DOE",
                page=mock_page,
            )

    if not repeated_page:
        assert len(results) == 2
        assert results[0]["CaseNumber"] == "CASE-P1-001"
        assert results[1]["CaseNumber"] == "CASE-P1-001"
        assert results[1]["CaseStyle"] == "DOE VS BAKER"
    mock_next_btn.first.click.assert_called_once()


@pytest.mark.asyncio
async def test_miami_persistence_format(miami_scraper):
    """Section 6: Step J - Verifies extracted results match fl_jsonbody_miami schema."""
    case_result = {
        "CaseNumber": "2026-999999-CC-01",
        "LocalCaseNumber": "2026-999999-CC-01",
        "StateCaseNumber": "132026CC999999000001",
        "Section": "01 - Civil",
        "Court": "01 - Civil",
        "CaseType": "CIVIL",
        "FilingDate": "05/20/2026",
        "CaseStatus": "OPEN",
        "CaseStyle": "DOE, JOHN VS DOE, JANE",
        "CountyWebsite": miami_scraper.base_url,
    }

    assert "CaseNumber" in case_result
    assert "CaseStyle" in case_result
    assert "FilingDate" in case_result
    assert "CaseStatus" in case_result
    assert "CaseType" in case_result
    assert "CountyWebsite" in case_result
    assert case_result["CountyWebsite"] == "https://www2.miamidadeclerk.gov/ocs/"


@pytest.mark.asyncio
async def test_miami_selects_party_name_from_navbar_menu(miami_scraper):
    """Section 6: Step A - Verifies clicking 'Party Name' from navbar / navigation menu."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    nav_party_link = MagicMock()
    nav_party_link.count = AsyncMock(return_value=1)
    nav_party_link.is_visible = AsyncMock(return_value=True)
    nav_party_link.first = nav_party_link
    nav_party_link.click = AsyncMock()

    last_input = MagicMock()
    last_input.count = AsyncMock(return_value=1)
    last_input.first = last_input
    last_input.wait_for = AsyncMock()

    def locator_side_effect(selector):
        if "Party Name" in selector or "#nameSearch" in selector:
            return nav_party_link
        if "txtLastName" in selector:
            return last_input
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.select_party_search_tab(mock_page)

    nav_party_link.click.assert_called_once()
    last_input.wait_for.assert_called_once()


@pytest.mark.asyncio
async def test_miami_expands_responsive_navbar_when_collapsed(miami_scraper):
    """Section 6: Step A - Verifies expanding responsive navbar toggler if collapsed."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    navbar_toggle = MagicMock()
    navbar_toggle.count = AsyncMock(return_value=1)
    navbar_toggle.is_visible = AsyncMock(return_value=True)
    navbar_toggle.first = navbar_toggle
    navbar_toggle.click = AsyncMock()

    nav_party_link = MagicMock()
    nav_party_link.count = AsyncMock(return_value=1)
    nav_party_link.first = nav_party_link
    nav_party_link.click = AsyncMock()

    # First check: nav party is hidden (collapsed). Subsequent check: visible
    nav_party_link.is_visible = AsyncMock(side_effect=[False, True, True])

    def locator_side_effect(selector):
        if "navbar-toggler" in selector or "Toggle navigation" in selector:
            return navbar_toggle
        if "Party Name" in selector or "#nameSearch" in selector:
            return nav_party_link
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.select_party_search_tab(mock_page)

    navbar_toggle.click.assert_called_once()
    nav_party_link.click.assert_called_once()


@pytest.mark.asyncio
async def test_miami_welcome_greeting_skips_login(miami_scraper):
    """Step b.iv: Verifies login is skipped when 'Welcome, ...' account greeting is present."""
    mock_page = MagicMock()
    mock_welcome = MagicMock()
    mock_welcome.count = AsyncMock(return_value=1)
    mock_welcome.is_visible = AsyncMock(return_value=True)
    mock_welcome.inner_text = AsyncMock(return_value="Welcome, Apoorv N.")
    mock_welcome.first = mock_welcome

    def locator_side_effect(selector):
        if "View account information" in selector or "Welcome" in selector:
            return mock_welcome
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.ensure_authenticated(mock_page)
    # Neither login URL navigation nor form filling should be triggered
    assert mock_page.goto.call_count == 0


@pytest.mark.asyncio
async def test_miami_login_exact_object_selectors(miami_scraper):
    """Step b: Verifies login uses exact objects: Register/Login link, userName, password, btnCall."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.wait_for_function = AsyncMock(return_value=True)
    mock_page.keyboard.press = AsyncMock()

    mock_reg_login = MagicMock()
    mock_reg_login.count = AsyncMock(return_value=1)
    mock_reg_login.is_visible = AsyncMock(return_value=True)
    mock_reg_login.first = mock_reg_login
    mock_reg_login.click = AsyncMock()

    mock_email = MagicMock()
    mock_email.count = AsyncMock(return_value=1)
    mock_email.first = mock_email
    mock_email.wait_for = AsyncMock()
    mock_email.fill = AsyncMock()
    mock_email.clear = AsyncMock()

    mock_pwd = MagicMock()
    mock_pwd.count = AsyncMock(return_value=1)
    mock_pwd.first = mock_pwd
    mock_pwd.fill = AsyncMock()
    mock_pwd.clear = AsyncMock()

    mock_login_btn = MagicMock()
    mock_login_btn.count = AsyncMock(return_value=1)
    mock_login_btn.is_visible = AsyncMock(return_value=True)
    mock_login_btn.first = mock_login_btn
    mock_login_btn.click = AsyncMock()

    captured_selectors = []

    def locator_side_effect(selector):
        captured_selectors.append(selector)
        if "hs=OCSB" in selector or "Register/Login" in selector:
            return mock_reg_login
        if "userName" in selector:
            return mock_email
        if "password" in selector:
            return mock_pwd
        if "btnCall" in selector:
            return mock_login_btn
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.ensure_authenticated(mock_page)

    mock_reg_login.click.assert_called_once()
    mock_login_btn.click.assert_called_once()
    # Confirm exact selectors were queried
    assert any("hs=OCSB" in s for s in captured_selectors)
    assert any("userName" in s for s in captured_selectors)
    assert any("password" in s for s in captured_selectors)
    assert any("btnCall" in s for s in captured_selectors)


@pytest.mark.asyncio
async def test_miami_exact_party_name_span_and_blue_refresh_button(miami_scraper):
    """Step e: Verifies Party Name span and blue Refresh button exact selectors."""
    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_party = MagicMock()
    mock_party.count = AsyncMock(return_value=1)
    mock_party.is_visible = AsyncMock(return_value=True)
    mock_party.first = mock_party
    mock_party.click = AsyncMock()

    mock_refresh = MagicMock()
    mock_refresh.count = AsyncMock(return_value=1)
    mock_refresh.is_visible = AsyncMock(return_value=True)
    mock_refresh.first = mock_refresh
    mock_refresh.click = AsyncMock()

    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.wait_for = AsyncMock()

    captured_selectors = []

    def locator_side_effect(selector):
        captured_selectors.append(selector)
        if "subitem-color" in selector or "cursorPointer" in selector:
            return mock_party
        if "button-blue" in selector or "Refresh" in selector:
            return mock_refresh
        if "partyLastName" in selector:
            return mock_last
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    await miami_scraper.select_party_search_tab(mock_page)

    mock_party.click.assert_called_once()
    mock_refresh.click.assert_called_once()
    assert any("subitem-color" in s for s in captured_selectors)
    assert any("button-blue" in s for s in captured_selectors)


@pytest.mark.asyncio
async def test_miami_filing_date_to_always_selects_today_date(miami_scraper):
    """Step f: Verifies filingDateTo is ALWAYS populated with today's date."""
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")

    mock_page = MagicMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value=False)

    mock_last = MagicMock()
    mock_last.count = AsyncMock(return_value=1)
    mock_last.first = mock_last
    mock_last.wait_for = AsyncMock()
    mock_last.fill = AsyncMock()
    mock_last.clear = AsyncMock()

    mock_first = MagicMock()
    mock_first.count = AsyncMock(return_value=1)
    mock_first.first = mock_first
    mock_first.fill = AsyncMock()
    mock_first.clear = AsyncMock()

    mock_date_from = MagicMock()
    mock_date_from.count = AsyncMock(return_value=1)
    mock_date_from.first = mock_date_from
    mock_date_from.fill = AsyncMock()
    mock_date_from.clear = AsyncMock()

    mock_date_to = MagicMock()
    mock_date_to.count = AsyncMock(return_value=1)
    mock_date_to.first = mock_date_to
    mock_date_to.fill = AsyncMock()
    mock_date_to.clear = AsyncMock()

    mock_search = MagicMock()
    mock_search.count = AsyncMock(return_value=1)
    mock_search.is_visible = AsyncMock(return_value=True)
    mock_search.first = mock_search
    mock_search.click = AsyncMock()

    mock_table = MagicMock()
    mock_table.count = AsyncMock(return_value=0)
    mock_table.is_visible = AsyncMock(return_value=False)

    def locator_side_effect(selector):
        if "partyLastName" in selector:
            return mock_last
        if "partyFirstName" in selector:
            return mock_first
        if "filingDateFrom" in selector:
            return mock_date_from
        if "filingDateTo" in selector:
            return mock_date_to
        if "button-green" in selector or "btnSearch" in selector:
            return mock_search
        if "tblResults" in selector or "table.table" in selector:
            return mock_table
        generic = MagicMock()
        generic.count = AsyncMock(return_value=0)
        generic.is_visible = AsyncMock(return_value=False)
        return generic

    mock_page.locator.side_effect = locator_side_effect

    with patch.object(miami_scraper, "navigate_to_search", AsyncMock()), \
         patch.object(miami_scraper, "ensure_authenticated", AsyncMock()), \
         patch.object(miami_scraper, "verify_portal_url", AsyncMock()), \
         patch.object(miami_scraper, "select_party_search_tab", AsyncMock()), \
         patch.object(miami_scraper, "detect_and_handle_captcha", AsyncMock(return_value=False)) as captcha_detector, \
         patch.object(miami_scraper, "verify_and_enable_table_view", AsyncMock()), \
         patch.object(miami_scraper, "return_to_search_state", AsyncMock()):

        with pytest.raises(RuntimeError, match="without results or a verified no-match"):
            await miami_scraper.search_by_party_name(
                first_name="JANE",
                last_name="SMITH",
                page=mock_page,
                date_of_loss="2024-05-15",
            )

    # Verify filingDateTo was filled with today's date
    mock_date_to.fill.assert_called_with(today_str)
    # Verify filingDateFrom was filled with DOL
    mock_date_from.fill.assert_called_with("2024-05-15")
    # Verify search button was clicked
    mock_search.click.assert_called_once()
    # V4 submits before CAPTCHA handling; an idle reCAPTCHA badge must not block Search.
    captcha_detector.assert_not_awaited()
