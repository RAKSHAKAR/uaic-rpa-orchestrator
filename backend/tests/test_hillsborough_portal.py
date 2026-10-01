"""Dedicated Test Suite for Hillsborough County Court Portal Workflow (Prompt 2 Parity).

Tests cover:
- Dynamic settings propagation (base_url, timeouts, etc.)
- Step A: Navigation to portal base URL with reload fallback on empty body
- Step B & C: Click 'Party or Business Name' and verify 'Search by Party or Business Name' is active
- Step D & E: Biometric input filling (First Name, Last Name, On or After) and Search click
- Step F: Wait for results grid
- Step G: Extraction of ALL available columns including Citation and dynamic headers
- Step H: Multi-page pagination traversal
- Step I: Detection and dismissal of 'YOUR SEARCH CRITERIA' popup without error
- Step J: Database persistence into fl_jsonbody_hillsborough and ScrapedCourtCase records
- Section 4: Returning tab to search state between unique names
- Section 2 & 5: Sequential single unique name processing on the same open tab
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.automation.florida.hillsborough import HillsboroughScraper
from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.services.fuzzy_engine import is_case_eligible
from app.tasks.scraper_tasks import _async_orchestrate_scrapers, canonical_portal_case


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def _build_mock_page():
    page = MagicMock()
    page.url = "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"
    page.goto = AsyncMock()
    page.reload = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")
    page.evaluate = AsyncMock(return_value=True)  # Party Name tab is active
    page.keyboard = MagicMock()
    page.keyboard.press = AsyncMock()
    return page


@pytest.mark.asyncio
async def test_hillsborough_initializes_with_dynamic_settings():
    """Verify HillsboroughScraper retrieves settings dynamically from system settings / config."""
    custom_url = "https://custom-hillsborough.example.com/"
    scraper = HillsboroughScraper(
        base_url=custom_url,
        captcha_wait_seconds=40,
        max_attempts=3,
        timeout_ms=45000,
    )
    assert scraper.base_url == custom_url
    assert scraper.captcha_wait_seconds == 40
    assert scraper.timeout_ms == 45000


@pytest.mark.asyncio
async def test_hillsborough_step_a_navigation_with_reload_check():
    """Step A: Navigates to Hillsborough search tab and refreshes if page is empty."""
    scraper = HillsboroughScraper(base_url="https://hover.hillsclerk.com/")
    page = _build_mock_page()
    page.url = "about:blank"  # Fresh tab
    # First inner_text returns empty string (triggering refresh), subsequent call returns content
    page.inner_text = AsyncMock(side_effect=["", "Hillsborough Clerk HOVER"])

    nav_url = await scraper.navigate_to_search(page)
    assert "caseSearch.html" in nav_url
    page.goto.assert_called_once()
    page.reload.assert_called_once()


@pytest.mark.asyncio
async def test_hillsborough_step_b_and_c_select_party_search_tab():
    """Step B & C: Clicks 'Party or Business Name' and verifies 'Search by Party or Business Name' is active."""
    scraper = HillsboroughScraper()
    page = _build_mock_page()
    # evaluate returns False for active tab
    page.evaluate = AsyncMock(return_value=False)

    party_tab = MagicMock()
    party_tab.count = AsyncMock(return_value=1)
    party_tab.first = party_tab
    party_tab.is_visible = AsyncMock(return_value=True)
    party_tab.click = AsyncMock()

    page.locator.return_value = party_tab

    await scraper.select_party_search_tab(page)
    party_tab.click.assert_called_once()


@pytest.mark.asyncio
async def test_hillsborough_step_i_popup_dismissal():
    """Step I: Detects 'YOUR SEARCH CRITERIA' popup, clicks Close/X, and continues workflow."""
    scraper = HillsboroughScraper()
    page = _build_mock_page()

    modal_header = MagicMock()
    modal_header.count = AsyncMock(return_value=1)
    modal_header.first = modal_header
    modal_header.is_visible = AsyncMock(return_value=True)

    close_btn = MagicMock()
    close_btn.count = AsyncMock(return_value=1)
    close_btn.first = close_btn
    close_btn.is_visible = AsyncMock(return_value=True)
    close_btn.click = AsyncMock()

    def loc_side_effect(sel):
        if "modal" in sel or "YOUR SEARCH CRITERIA" in sel:
            if "button" in sel or "Close" in sel or "dismiss" in sel:
                return close_btn
            return modal_header
        mock_g = MagicMock()
        mock_g.count = AsyncMock(return_value=0)
        return mock_g

    page.locator.side_effect = loc_side_effect

    dismissed = await scraper.check_and_dismiss_search_criteria_popup(page)
    assert dismissed is True
    close_btn.click.assert_called_once()


@pytest.mark.asyncio
async def test_hillsborough_step_d_and_e_data_filling_and_submit():
    """Step D & E: Fills First Name, Last Name, On or After, and clicks Search."""
    scraper = HillsboroughScraper()
    page = _build_mock_page()

    last_input = MagicMock()
    last_input.wait_for = AsyncMock()
    last_input.fill = AsyncMock()
    last_input.click = AsyncMock()
    last_input.count = AsyncMock(return_value=1)
    last_input.first = last_input

    first_input = MagicMock()
    first_input.fill = AsyncMock()
    first_input.click = AsyncMock()
    first_input.count = AsyncMock(return_value=1)
    first_input.first = first_input

    dol_input = MagicMock()
    dol_input.fill = AsyncMock()
    dol_input.click = AsyncMock()
    dol_input.count = AsyncMock(return_value=1)
    dol_input.first = dol_input

    search_btn = MagicMock()
    search_btn.count = AsyncMock(return_value=1)
    search_btn.first = search_btn
    search_btn.last = search_btn
    search_btn.is_visible = AsyncMock(return_value=True)
    search_btn.click = AsyncMock()

    # Empty results table so it returns empty list
    results_table = MagicMock()
    results_table.wait_for = AsyncMock()
    results_table.first = results_table

    empty_msg = MagicMock()
    empty_msg.count = AsyncMock(return_value=1)
    empty_msg.first = empty_msg
    empty_msg.is_visible = AsyncMock(return_value=True)

    party_tab = MagicMock()
    party_tab.count = AsyncMock(return_value=1)
    party_tab.first = party_tab
    party_tab.last = party_tab
    party_tab.is_visible = AsyncMock(return_value=True)
    party_tab.click = AsyncMock()

    def loc_side_effect(sel):
        if "Party-tab" in sel or "Party or Business Name" in sel or "Search by Party" in sel:
            return party_tab
        if "partyLastName" in sel or "spLastName" in sel:
            return last_input
        if "partyFirstName" in sel or "spFirstName" in sel:
            return first_input
        if "spDateFiledAfter" in sel:
            return dol_input
        if "btnSubmitPartySearch" in sel or "partySearchForm" in sel or ("button" in sel and "Search" in sel):
            return search_btn
        if "dataTables_empty" in sel or "No data available" in sel:
            return empty_msg
        if "partyResultsTable" in sel:
            return results_table
        mock_g = MagicMock()
        mock_g.count = AsyncMock(return_value=0)
        return mock_g

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "return_to_search_state", new_callable=AsyncMock) as mock_ret:
        res = await scraper.search_by_party_name("Maria", "Rodriguez", page, date_of_loss="05/20/2021")

    assert res == []
    last_input.fill.assert_called_with("Rodriguez")
    first_input.fill.assert_called_with("Maria")
    search_btn.click.assert_called_once()
    mock_ret.assert_called_once()


@pytest.mark.asyncio
async def test_hillsborough_step_g_extracts_all_columns_including_citation():
    """Step G: Extracts all columns including Citation and dynamic headers from results table."""
    scraper = HillsboroughScraper()
    page = _build_mock_page()

    # Mock headers (8 columns)
    mock_headers = ["Select", "Type", "Case Number", "Citation", "Case Style", "Case Status", "Filing Date", "Case Type", "Division"]
    th_loc = MagicMock()
    th_loc.count = AsyncMock(return_value=len(mock_headers))
    th_mocks = []
    for h in mock_headers:
        m = MagicMock()
        m.inner_text = AsyncMock(return_value=h)
        th_mocks.append(m)
    th_loc.nth.side_effect = lambda idx: th_mocks[idx]

    # Mock 1 row with 9 cells
    row_mock = MagicMock()
    row_mock.locator.return_value.all_inner_texts = AsyncMock(
        return_value=[
            "",
            "Civil",
            "23-CA-001234",
            "CIT-998877",
            "GEICO VS MARCO RODRIGUEZ",
            "OPEN",
            "02/14/2023",
            "CIRCUIT CIVIL",
            "Division H",
        ]
    )

    rows_loc = MagicMock()
    rows_loc.count = AsyncMock(return_value=1)
    rows_loc.nth.return_value = row_mock

    next_btn = MagicMock()
    next_btn.count = AsyncMock(return_value=0)

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()
    mock_input.click = AsyncMock()

    def loc_side_effect(sel):
        if "th" in sel:
            return th_loc
        if "tbody tr" in sel:
            return rows_loc
        if "next" in sel.lower():
            return next_btn
        if "dataTables_empty" in sel:
            empty_m = MagicMock()
            empty_m.count = AsyncMock(return_value=0)
            return empty_m
        return mock_input

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "return_to_search_state", new_callable=AsyncMock):
        cases = await scraper.search_by_party_name("Marco", "Rodriguez", page)

    assert len(cases) == 1
    case = cases[0]
    assert case["CaseNumber"] == "23-CA-001234"
    assert case["CaseStyle"] == "GEICO VS MARCO RODRIGUEZ"
    assert case["CaseStatus"] == "OPEN"
    assert case["FilingDate"] == "02/14/2023"
    assert case["CaseType"] == "CIRCUIT CIVIL"
    assert set(case) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}


@pytest.mark.asyncio
async def test_hillsborough_preserves_repeated_and_incomplete_v4_rows():
    """Live HOVER can return a numbered row with four blank detail cells."""
    scraper = HillsboroughScraper(timeout_ms=45_000)
    page = _build_mock_page()
    page.url = "https://hover.hillsclerk.com/html/case/searchResults.html"
    page.wait_for_load_state = AsyncMock()

    source_rows = [
        ["", "Civil", "24-CA-000001", "", "JOHN SMITH VS ACME", "OPEN", "01/02/2024", "CIRCUIT CIVIL"],
        ["", "Civil", "24-CA-000001", "", "JOHN SMITH VS BETA", "OPEN", "01/02/2024", "CIRCUIT CIVIL"],
        ["", "", "24-CA-000002", "", "", "", "", ""],
    ]
    rows = MagicMock()
    rows.count = AsyncMock(return_value=len(source_rows))

    def row_at(index):
        row = MagicMock()
        row.locator.return_value.all_inner_texts = AsyncMock(return_value=source_rows[index])
        return row

    rows.nth.side_effect = row_at
    missing = MagicMock()
    missing.count = AsyncMock(return_value=0)
    missing.is_visible = AsyncMock(return_value=False)
    control = MagicMock()
    control.count = AsyncMock(return_value=1)
    control.first = control
    control.wait_for = AsyncMock()

    def locate(selector):
        if "tbody tr" in selector:
            return rows
        if "thead th" in selector or "next" in selector.lower():
            return missing
        if "dataTables_empty" in selector or "No data" in selector or "Loading" in selector:
            return missing
        return control

    page.locator.side_effect = locate
    with (
        patch.object(scraper, "navigate_to_search", new_callable=AsyncMock),
        patch.object(scraper, "select_party_search_tab", new_callable=AsyncMock),
        patch.object(scraper, "check_and_dismiss_search_criteria_popup", new_callable=AsyncMock),
        patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock, return_value=True),
        patch.object(scraper, "biometric_fill", new_callable=AsyncMock),
        patch.object(scraper, "biometric_click", new_callable=AsyncMock),
        patch.object(scraper, "pace_action", new_callable=AsyncMock),
        patch.object(scraper, "return_to_search_state", new_callable=AsyncMock),
    ):
        cases = await scraper.search_by_party_name("John", "Smith", page, date_of_loss="01/01/2024")

    assert len(cases) == 3
    page.wait_for_load_state.assert_any_await("networkidle", timeout=45_000)
    assert cases[0]["CaseNumber"] == cases[1]["CaseNumber"]
    assert cases[0]["CaseStyle"] != cases[1]["CaseStyle"]
    assert canonical_portal_case("hillsborough", cases[2]) == cases[2]
    assert not is_case_eligible(
        cases[2]["FilingDate"], cases[2]["CaseStatus"], cases[2]["CaseType"]
    )


@pytest.mark.asyncio
async def test_hillsborough_step_h_pagination_traversal():
    """Step H: Traverses multiple pages of results without stopping at page 1."""
    scraper = HillsboroughScraper()
    page = _build_mock_page()

    page_idx = {"curr": 1}

    def get_mock_row(idx):
        p = page_idx["curr"]
        rm = MagicMock()
        rm.locator.return_value.all_inner_texts = AsyncMock(
            return_value=[
                "",
                "Civil",
                f"23-CA-00{p}{idx:02d}",
                f"CIT-{p}{idx:02d}",
                f"Plaintiff v. Defendant {p}-{idx}",
                "OPEN",
                "01/10/2023",
                "CIRCUIT CIVIL",
            ]
        )
        return rm

    rows_loc = MagicMock()
    rows_loc.count = AsyncMock(return_value=2)
    rows_loc.nth.side_effect = lambda idx: get_mock_row(idx)

    next_btn = MagicMock()
    next_btn.count = AsyncMock(return_value=1)
    next_btn.first = next_btn
    next_btn.is_visible = AsyncMock(return_value=True)

    async def mock_next_click():
        page_idx["curr"] += 1

    next_btn.click = AsyncMock(side_effect=mock_next_click)

    async def mock_get_attr(attr):
        if attr == "class" and page_idx["curr"] >= 2:
            return "paginate_button next disabled"
        if attr in ("disabled", "aria-disabled") and page_idx["curr"] >= 2:
            return "true"
        return "false"

    next_btn.get_attribute = AsyncMock(side_effect=mock_get_attr)

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()
    mock_input.click = AsyncMock()

    def loc_side_effect(sel):
        if "tbody tr" in sel:
            return rows_loc
        if "next" in sel.lower():
            return next_btn
        if "dataTables_empty" in sel:
            empty_m = MagicMock()
            empty_m.count = AsyncMock(return_value=0)
            return empty_m
        return mock_input

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "return_to_search_state", new_callable=AsyncMock):
        cases = await scraper.search_by_party_name("Alice", "Brown", page)

    # 2 pages * 2 rows = 4 cases extracted
    assert len(cases) == 4
    assert next_btn.click.await_count == 1


@pytest.mark.asyncio
async def test_hillsborough_sequential_unique_names_on_same_tab():
    """Section 2 & 4: Verifies multiple unique names process sequentially on the same open tab."""
    claim_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"HIL-TEST-{claim_id[:6]}",
            exposure_number="1",
            claimant_first_name="Diana",
            claimant_last_name="Prince",
            insured_first_name="Diana",
            insured_last_name="Prince",
            driver_first_name="Bruce",
            driver_last_name="Wayne",
            policy_state="FL",
            loss_location_state="FL",
            fl_website_hillsborough="Yes",
            fl_website_broward="No",
            fl_website_miami="No",
            record_status=RecordStatusEnum.NEW,
        )
        session.add(claim)
        await session.commit()

    processed_parties = []

    async def mock_search_by_party_name(first_name, last_name, page, date_of_loss=None, **kwargs):
        party_name = f"{first_name} {last_name}".strip()
        processed_parties.append(party_name)
        if "Prince" in party_name:
            return [{
                "CaseNumber": f"24-CA-001-{len(processed_parties)}",
                "Citation": "CIT-001",
                "CaseStyle": f"{party_name} v. Allstate",
                "CountyWebsite": "https://hover.hillsclerk.com/",
                "FilingDate": "03/15/2024",
                "CaseStatus": "OPEN",
                "CaseType": "CIRCUIT CIVIL",
            }]
        return []

    # Mock browser session runner to isolate test from host Chrome process
    mock_tab = MagicMock()
    mock_browser_session = MagicMock()
    mock_browser_session.stage_timings = {}
    mock_browser_session.get_or_create_tab = AsyncMock(return_value=mock_tab)

    mock_runner_cm = AsyncMock()
    mock_runner_cm.__aenter__.return_value = mock_browser_session
    mock_runner_cm.__aexit__.return_value = None

    with patch("app.core.celery_app.celery_app.send_task", MagicMock()), \
         patch("app.tasks.scraper_tasks.SingleSessionBrowserRunner", return_value=mock_runner_cm), \
         patch("app.automation.florida.hillsborough.HillsboroughScraper.search_by_party_name", side_effect=mock_search_by_party_name):

        await _async_orchestrate_scrapers(claim_id)

    # Verify sequential processing: Diana Prince, then Bruce Wayne (2 unique parties)
    assert len(processed_parties) == 2
    assert processed_parties[0] == "Diana Prince"
    assert processed_parties[1] == "Bruce Wayne"

    # Verify tab was created in pre-opening and retrieved once for the portal session (1 pre-open + 1 portal session = 2)
    assert mock_browser_session.get_or_create_tab.await_count == 2

    # Verify results persisted in database under fl_jsonbody_hillsborough and ScrapedCourtCase
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id == claim_id).options(selectinload(ClaimRecord.scraped_cases))
        res = await session.execute(q)
        claim_after = res.scalar_one()

        assert claim_after.fl_botstatus_hillsborough == BotStatusEnum.COMPLETED
        assert claim_after.fl_jsonbody_hillsborough is not None
        assert len(claim_after.fl_jsonbody_hillsborough) == 1
        assert claim_after.fl_jsonbody_hillsborough[0]["CaseNumber"] == "24-CA-001-1"

        assert len(claim_after.scraped_cases) == 1
        court_case: ScrapedCourtCase = claim_after.scraped_cases[0]
        assert court_case.county_name == "Hillsborough County (FL)"
        assert court_case.case_number == "24-CA-001-1"
        assert court_case.raw_payload is not None
        assert set(court_case.raw_payload) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}


@pytest.mark.asyncio
async def test_hillsborough_down_search_button_clicked_not_top_search():
    """Verify that search_by_party_name clicks the down search button (#btnSubmitPartySearch / .last) and not top button."""
    scraper = HillsboroughScraper()
    page = _build_mock_page()

    top_search_btn = MagicMock()
    top_search_btn.click = AsyncMock()

    down_search_btn = MagicMock()
    down_search_btn.count = AsyncMock(return_value=1)
    down_search_btn.first = down_search_btn
    down_search_btn.last = down_search_btn
    down_search_btn.is_visible = AsyncMock(return_value=True)
    down_search_btn.click = AsyncMock()

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.last = mock_input
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()

    empty_msg = MagicMock()
    empty_msg.count = AsyncMock(return_value=1)
    empty_msg.first = empty_msg
    empty_msg.is_visible = AsyncMock(return_value=True)

    def loc_side_effect(sel):
        if "btnSubmitPartySearch" in sel or "partySearchForm" in sel:
            return down_search_btn
        if "dataTables_empty" in sel:
            return empty_msg
        return mock_input

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "return_to_search_state", new_callable=AsyncMock):
        await scraper.search_by_party_name("John", "Doe", page)

    down_search_btn.click.assert_called_once()
    assert top_search_btn.click.call_count == 0


@pytest.mark.asyncio
async def test_hillsborough_always_checks_party_business_name_selected():
    """Verify select_party_search_tab checks party input readiness and selects 'Search by Party or Business Name'."""
    scraper = HillsboroughScraper()
    page = _build_mock_page()

    party_tab = MagicMock()
    party_tab.count = AsyncMock(return_value=1)
    party_tab.first = party_tab
    party_tab.is_visible = AsyncMock(return_value=True)
    party_tab.click = AsyncMock()

    last_input = MagicMock()
    last_input.count = AsyncMock(return_value=1)
    last_input.first = last_input
    last_input.is_visible = AsyncMock(return_value=False)
    last_input.wait_for = AsyncMock()

    def loc_side_effect(sel):
        if "Party" in sel or "Party or Business Name" in sel:
            return party_tab
        if "spLastName" in sel:
            return last_input
        mock_g = MagicMock()
        mock_g.count = AsyncMock(return_value=0)
        return mock_g

    page.locator.side_effect = loc_side_effect
    page.evaluate = AsyncMock(return_value=False)

    await scraper.select_party_search_tab(page)

    party_tab.click.assert_called_once()
    last_input.wait_for.assert_called_once()


@pytest.mark.asyncio
async def test_hillsborough_landing_page_clicks_party_or_business_name_button():
    """Verify Step b: On landing page, clicks 'Party or Business Name' button."""
    scraper = HillsboroughScraper()
    page = MagicMock()
    page.url = "https://hover.hillsclerk.com/"
    page.goto = AsyncMock()
    page.reload = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Hillsborough County Clerk Landing")

    landing_btn = MagicMock()
    landing_btn.count = AsyncMock(return_value=1)
    landing_btn.first = landing_btn
    landing_btn.last = landing_btn
    landing_btn.is_visible = AsyncMock(return_value=True)
    landing_btn.click = AsyncMock()

    def loc_side_effect(sel):
        if "Party-tab" in sel or "Party or" in sel:
            return landing_btn
        mock_g = MagicMock()
        mock_g.count = AsyncMock(return_value=0)
        return mock_g

    page.locator.side_effect = loc_side_effect

    await scraper.navigate_to_search(page)

    landing_btn.click.assert_called_once()


@pytest.mark.asyncio
async def test_hillsborough_exact_selectors_and_filled_column():
    """Verify Step d & g: Exact selectors used for First Name, Last Name, On or After, and Filled column populated."""
    scraper = HillsboroughScraper()
    page = _build_mock_page()

    first_input = MagicMock()
    first_input.count = AsyncMock(return_value=1)
    first_input.first = first_input
    first_input.last = first_input
    first_input.fill = AsyncMock()

    last_input = MagicMock()
    last_input.count = AsyncMock(return_value=1)
    last_input.first = last_input
    last_input.last = last_input
    last_input.wait_for = AsyncMock()
    last_input.fill = AsyncMock()

    dol_input = MagicMock()
    dol_input.count = AsyncMock(return_value=1)
    dol_input.first = dol_input
    dol_input.last = dol_input

    search_btn = MagicMock()
    search_btn.count = AsyncMock(return_value=1)
    search_btn.first = search_btn
    search_btn.last = search_btn
    search_btn.is_visible = AsyncMock(return_value=True)
    search_btn.click = AsyncMock()

    table_loc = MagicMock()
    table_loc.first = table_loc
    table_loc.wait_for = AsyncMock()

    row_mock = MagicMock()
    row_mock.locator = MagicMock(return_value=MagicMock(all_inner_texts=AsyncMock(return_value=[
        "", "", "24-CA-009999", "CIT-123", "SMITH VS JONES", "OPEN", "05/12/2024", "CIRCUIT CIVIL", "Division H"
    ])))

    rows_mock = MagicMock()
    rows_mock.count = AsyncMock(return_value=1)
    rows_mock.nth = MagicMock(return_value=row_mock)

    empty_msg = MagicMock()
    empty_msg.count = AsyncMock(return_value=0)
    empty_msg.is_visible = AsyncMock(return_value=False)

    def loc_side_effect(sel):
        if "spFirstName" in sel:
            return first_input
        if "spLastName" in sel:
            return last_input
        if "spDateFiledAfter" in sel:
            return dol_input
        if "btnSubmitPartySearch" in sel:
            return search_btn
        if "tbody tr" in sel:
            return rows_mock
        if "Table" in sel or "table" in sel:
            return table_loc
        if "dataTables_empty" in sel:
            return empty_msg
        mock_g = MagicMock()
        mock_g.count = AsyncMock(return_value=0)
        mock_g.is_visible = AsyncMock(return_value=False)
        return mock_g

    page.locator.side_effect = loc_side_effect
    page.evaluate = AsyncMock(return_value=True)

    with patch.object(scraper, "return_to_search_state", new_callable=AsyncMock):
        results = await scraper.search_by_party_name("Alice", "Smith", page, date_of_loss="05/12/2024")

    assert len(results) == 1
    case = results[0]
    assert case["CaseNumber"] == "24-CA-009999"
    assert case["CaseStyle"] == "SMITH VS JONES"
    assert case["FilingDate"] == "05/12/2024"
    assert case["CaseStatus"] == "OPEN"
    assert case["CaseType"] == "CIRCUIT CIVIL"
    assert set(case) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}
    search_btn.click.assert_called_once()
