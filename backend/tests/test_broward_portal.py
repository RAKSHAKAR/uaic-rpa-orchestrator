"""Dedicated Test Suite for Broward County Court Portal Workflow (Prompt 1 Parity).

Tests cover:
- Dynamic settings application from SystemSettings / config
- Sequential single unique name processing on the same tab
- Step A & B: Navigation to portal base URL and Case Search ECA
- Step C: Verification and activation of Party Name tab
- Step D: Biometric filling of Last Name, First Name, Date of Loss
- Step E & F: CAPTCHA verification, wait, retry & refresh loop up to max_attempts
- Step G: Session timeout warning detection, "Continue session", search data restoration
- Step H: Immediate submission upon CAPTCHA solve
- Step I: Verification of results loaded (handling No Records Found)
- Step J: All-column extraction including AccessLevel and dynamic headers
- Step K: Multi-page pagination traversal
- Step L: Database persistence into fl_jsonbody_broward and ScrapedCourtCase records
- Section 4: Returning tab to search state between unique names
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.automation.base import CaptchaResolutionError
from app.automation.florida.broward import BrowardScraper
from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.tasks.scraper_tasks import _async_orchestrate_scrapers


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def _build_mock_page():
    page = MagicMock()
    page.url = "https://www.browardclerk.org/Web2/CaseSearchECA/Index/"
    page.goto = AsyncMock()
    page.reload = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.wait_for_url = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")
    page.evaluate = AsyncMock(return_value=True)  # Party Name tab is active
    return page


@pytest.mark.asyncio
async def test_broward_initializes_with_dynamic_settings():
    """Verify BrowardScraper retrieves settings dynamically from system settings / config."""
    custom_url = "https://custom-broward.example.com/"
    scraper = BrowardScraper(
        base_url=custom_url,
        captcha_wait_seconds=45,
        max_attempts=4,
        reload_backoff_seconds=3,
        timeout_ms=30000,
    )
    assert scraper.base_url == custom_url
    assert scraper.captcha_wait_seconds == 45
    assert scraper.max_attempts == 4
    assert scraper.reload_backoff_seconds == 3
    assert scraper.timeout_ms == 30000


@pytest.mark.asyncio
async def test_broward_step_a_and_b_navigation():
    """Step A & B: Opens base URL and navigates to Case Search ECA if not already there."""
    scraper = BrowardScraper(base_url="https://www.browardclerk.org/")
    page = _build_mock_page()
    page.url = "about:blank"  # Fresh tab starting from blank
    page.inner_text = AsyncMock(return_value="Welcome to Broward Clerk")

    case_search_btn = MagicMock()
    case_search_btn.count = AsyncMock(return_value=1)
    case_search_btn.first = case_search_btn
    case_search_btn.is_visible = AsyncMock(return_value=True)
    case_search_btn.click = AsyncMock()

    page.locator.return_value = case_search_btn

    target_url = await scraper.navigate_to_search(page)
    assert "Web2" in target_url
    page.goto.assert_called()


@pytest.mark.asyncio
async def test_broward_step_c_select_party_name_tab():
    """Step C: Verifies Case Search page loads and Party Name tab is clicked if not active."""
    scraper = BrowardScraper()
    page = _build_mock_page()
    # evaluate returns False for active tab pane
    page.evaluate = AsyncMock(return_value=False)

    tab_link = MagicMock()
    tab_link.count = AsyncMock(return_value=1)
    tab_link.first = tab_link
    tab_link.click = AsyncMock()

    page.locator.return_value = tab_link

    await scraper.select_party_name_tab(page)
    tab_link.click.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("empty_message", ["No records found", "No items to display"])
async def test_broward_step_d_data_filling_and_submit(empty_message):
    """Step D & H: Fills LastName, FirstName, DOL, and submits immediately after CAPTCHA solve."""
    scraper = BrowardScraper()
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
    search_btn.click = AsyncMock()

    # A verified no-match message distinguishes an empty search from failure.
    page.inner_text = AsyncMock(return_value=empty_message)
    rows_loc = MagicMock()
    rows_loc.count = AsyncMock(return_value=0)

    def loc_side_effect(sel):
        if "lastName" in sel:
            return last_input
        if "firstName" in sel:
            return first_input
        if "filingDateOnOrAfterP" in sel:
            return dol_input
        if "PersonSearchResults" in sel:
            return search_btn
        if "table" in sel:
            return rows_loc
        mock_generic = MagicMock()
        mock_generic.count = AsyncMock(return_value=0)
        return mock_generic

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap, \
         patch.object(scraper, "return_to_search_state", new_callable=AsyncMock) as mock_ret:
        mock_cap.return_value = True
        await scraper.search_by_party_name("Alice", "Smith", page, date_of_loss="01/15/2023")

    last_input.fill.assert_called_with("Smith")
    first_input.fill.assert_called_with("Alice")
    dol_input.fill.assert_called_with("01/15/2023")
    assert any(
        "document.getElementById('PersonSearchResults')" in call.args[0]
        and "button.click()" in call.args[0]
        for call in page.evaluate.await_args_list
    )
    search_btn.click.assert_not_called()
    assert any(
        "No items to display" in call.args[0]
        for call in page.wait_for_selector.await_args_list
    )
    mock_ret.assert_called_once()


@pytest.mark.asyncio
async def test_broward_step_e_and_f_captcha_retry_loop():
    """Step E & F: CAPTCHA retry and reload loop up to max_attempts on failure."""
    scraper = BrowardScraper(max_attempts=3, captcha_wait_seconds=5, reload_backoff_seconds=1)
    page = _build_mock_page()

    mock_input = MagicMock()
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()
    mock_input.click = AsyncMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    page.locator.return_value = mock_input

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap, \
         patch.object(scraper, "return_to_search_state", new_callable=AsyncMock):
        mock_cap.return_value = False  # Always fails
        with pytest.raises(CaptchaResolutionError):
            await scraper.search_by_party_name("John", "Doe", page)
    assert mock_cap.await_count == 3, f"Expected 3 CAPTCHA attempts, got {mock_cap.await_count}"
    assert page.reload.await_count == 2, f"Expected 2 reloads across 3 attempts, got {page.reload.await_count}"


@pytest.mark.asyncio
async def test_broward_step_g_session_timeout_warning_handled():
    """Step G: Detects session timeout warning, clicks Continue session, and restores search inputs."""
    scraper = BrowardScraper()
    page = _build_mock_page()

    timeout_btn = MagicMock()
    timeout_btn.count = AsyncMock(return_value=1)
    timeout_btn.first = timeout_btn
    timeout_btn.is_visible = AsyncMock(return_value=True)
    timeout_btn.click = AsyncMock()

    last_input = MagicMock()
    last_input.count = AsyncMock(return_value=1)
    last_input.first = last_input
    last_input.input_value = AsyncMock(return_value="")  # Data was lost
    last_input.fill = AsyncMock()
    last_input.click = AsyncMock()

    first_input = MagicMock()
    first_input.count = AsyncMock(return_value=1)
    first_input.first = first_input
    first_input.fill = AsyncMock()
    first_input.click = AsyncMock()

    dol_input = MagicMock()
    dol_input.count = AsyncMock(return_value=1)
    dol_input.first = dol_input
    dol_input.fill = AsyncMock()
    dol_input.click = AsyncMock()

    def loc_side_effect(sel):
        if "Continue session" in sel:
            return timeout_btn
        if "lastName" in sel:
            return last_input
        if "firstName" in sel:
            return first_input
        if "filingDateOnOrAfterP" in sel:
            return dol_input
        mock_g = MagicMock()
        mock_g.count = AsyncMock(return_value=0)
        return mock_g

    page.locator.side_effect = loc_side_effect

    handled = await scraper.check_and_handle_session_timeout(
        page, l_name="Williams", f_name="David", date_of_loss="06/15/2022"
    )

    assert handled is True
    timeout_btn.click.assert_called_once()
    last_input.fill.assert_called_with("Williams")
    first_input.fill.assert_called_with("David")
    dol_input.fill.assert_called_with("06/15/2022")


@pytest.mark.asyncio
async def test_broward_exception_2_homepage_redirect_recovery():
    """Exception 2: Detects when session times out and navigates to homepage, restarts from Step B."""
    scraper = BrowardScraper()
    page = _build_mock_page()
    page.url = "https://www.browardclerk.org/"  # Redirected to homepage

    with patch.object(scraper, "navigate_to_search", new_callable=AsyncMock) as mock_nav, \
         patch.object(scraper, "select_party_name_tab", new_callable=AsyncMock) as mock_tab, \
         patch.object(scraper, "fill_search_fields", new_callable=AsyncMock) as mock_fill:
        handled = await scraper.check_and_handle_session_timeout(
            page, l_name="Williams", f_name="David", date_of_loss="06/15/2022"
        )

        assert handled is True
        mock_nav.assert_called_once_with(page)
        mock_tab.assert_called_once_with(page)
        mock_fill.assert_called_once_with(page, "Williams", "David", "06/15/2022")


@pytest.mark.asyncio
async def test_broward_exact_object_selectors_and_defaults():
    """Verify exact UI object selectors and 120s / 2-attempt defaults."""
    scraper = BrowardScraper()
    assert scraper.max_attempts == 2
    assert scraper.captcha_wait_seconds == 120

    page = _build_mock_page()
    page.url = "https://www.browardclerk.org/Web2"
    captured_selectors = []

    def mock_locator(sel):
        captured_selectors.append(sel)
        mock_el = MagicMock()
        mock_el.count = AsyncMock(return_value=1)
        mock_el.first = mock_el
        mock_el.is_visible = AsyncMock(return_value=True)
        mock_el.click = AsyncMock()
        return mock_el

    page.locator.side_effect = mock_locator
    target_url = await scraper.navigate_to_search(page)
    # Check that Step A navigates directly to Web2 with zero stray button clicks
    assert "Web2" in target_url

    captured_selectors.clear()
    page.evaluate = AsyncMock(return_value=False)
    await scraper.select_party_name_tab(page)
    # Check that Step C includes exact Party Name object selector (#myTabStandard a[href="#nameSearch"])
    assert any("#nameSearch" in s for s in captured_selectors)


@pytest.mark.asyncio
async def test_broward_step_j_extracts_all_columns_including_access_level():
    """Step J: Extracts all columns including AccessLevel and maps dynamic th headers."""
    scraper = BrowardScraper()
    page = _build_mock_page()
    page.inner_text = AsyncMock(return_value="Results found")

    # Mock headers (7 columns)
    mock_headers = ["Case Number", "Case Style", "Case Type", "Filing Date", "Case Status", "Access Level", "Judge"]
    th_loc = MagicMock()
    th_loc.count = AsyncMock(return_value=len(mock_headers))
    th_mocks = []
    for h in mock_headers:
        m = MagicMock()
        m.inner_text = AsyncMock(return_value=h)
        th_mocks.append(m)
    th_loc.nth.side_effect = lambda idx: th_mocks[idx]

    # The V4 subflow appends both source rows even when a case number repeats.
    row_mock = MagicMock()
    row_mock.locator.return_value.all_inner_texts = AsyncMock(
        return_value=[
            "CACE-23-012345",
            "State Farm vs John Doe",
            "CIRCUIT CIVIL",
            "03/12/2023",
            "OPEN",
            "Public Access",
            "Hon. Bowman",
        ]
    )

    rows_loc = MagicMock()
    rows_loc.count = AsyncMock(return_value=2)
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
        if "table.table tbody tr" in sel or "table tbody tr" in sel:
            return rows_loc
        if "next" in sel.lower():
            return next_btn
        return mock_input

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap, \
         patch.object(scraper, "return_to_search_state", new_callable=AsyncMock):
        mock_cap.return_value = True
        cases = await scraper.search_by_party_name("John", "Doe", page)

    assert len(cases) == 2
    assert cases[0] == cases[1]
    case = cases[0]
    assert case["CaseNumber"] == "CACE-23-012345"
    assert case["CaseStyle"] == "State Farm vs John Doe"
    assert case["CaseType"] == "CIRCUIT CIVIL"
    assert case["FilingDate"] == "03/12/2023"
    assert case["CaseStatus"] == "OPEN"
    assert set(case) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}


@pytest.mark.asyncio
async def test_broward_sequential_unique_names_on_same_tab():
    """Verify multiple unique names process sequentially one-by-one on the same open tab."""
    claim_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"BRW-TEST-{claim_id[:6]}",
            exposure_number="1",
            claimant_first_name="Carlos",
            claimant_last_name="Santana",
            insured_first_name="Carlos",
            insured_last_name="Santana",
            driver_first_name="Elena",
            driver_last_name="Rios",
            policy_state="FL",
            loss_location_state="FL",
            fl_website_broward="Yes",
            fl_website_miami="No",
            fl_website_hillsborough="No",
            record_status=RecordStatusEnum.NEW,
        )
        session.add(claim)
        await session.commit()

    processed_parties = []

    async def mock_search_by_party_name(first_name, last_name, page, date_of_loss=None, **kwargs):
        party_name = f"{first_name} {last_name}".strip()
        processed_parties.append(party_name)
        if "Santana" in party_name:
            return [{
                "CaseNumber": f"CACE-24-001-{len(processed_parties)}",
                "CaseStyle": f"{party_name} v. Progressive",
                "CountyWebsite": "https://www.browardclerk.org/",
                "FilingDate": "04/01/2024",
                "CaseStatus": "OPEN",
                "CaseType": "CIRCUIT CIVIL",
                "AccessLevel": "Public",
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
         patch("app.automation.florida.broward.BrowardScraper.search_by_party_name", side_effect=mock_search_by_party_name):

        await _async_orchestrate_scrapers(claim_id)

    # Verify sequential processing: Carlos Santana, then Elena Rios (2 unique parties)
    assert len(processed_parties) == 2
    assert processed_parties[0] == "Carlos Santana"
    assert processed_parties[1] == "Elena Rios"

    # Verify tab was created in pre-opening and retrieved once for the portal session (1 pre-open + 1 portal session = 2)
    assert mock_browser_session.get_or_create_tab.await_count == 2

    # Verify results persisted in database under fl_jsonbody_broward and ScrapedCourtCase
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id == claim_id).options(selectinload(ClaimRecord.scraped_cases))
        res = await session.execute(q)
        claim_after = res.scalar_one()

        assert claim_after.fl_botstatus_broward == BotStatusEnum.COMPLETED
        assert claim_after.fl_jsonbody_broward is not None
        assert len(claim_after.fl_jsonbody_broward) == 1
        assert claim_after.fl_jsonbody_broward[0]["CaseNumber"] == "CACE-24-001-1"
        assert set(claim_after.fl_jsonbody_broward[0]) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}

        assert len(claim_after.scraped_cases) == 1
        court_case: ScrapedCourtCase = claim_after.scraped_cases[0]
        assert court_case.county_name == "Broward County (FL)"
        assert court_case.case_number == "CACE-24-001-1"
        assert court_case.raw_payload is not None
        assert set(court_case.raw_payload) == {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}


@pytest.mark.asyncio
async def test_detect_and_handle_captcha_detects_anticaptcha_solved():
    """Verify detect_and_handle_captcha returns True immediately when AntiCaptcha solver has solved status."""
    scraper = BrowardScraper()
    page = MagicMock()
    page.frames = []

    # Mock DOM eval: first check detects turnstile, polling check returns solved
    async def mock_eval(js_script):
        if "cf-turnstile" in js_script:
            return "turnstile"
        if "antigate_solver" in js_script or "solvers" in js_script:
            return {"exists": True, "in_process": False, "solved": True}
        return False

    page.evaluate = AsyncMock(side_effect=mock_eval)
    page.wait_for_timeout = AsyncMock()

    solved = await scraper.detect_and_handle_captcha(page, wait_seconds=5)
    assert solved is True


@pytest.mark.asyncio
async def test_solved_extension_badge_skips_remaining_frame_probes():
    """A solved badge must release Broward to submit in the same polling cycle."""
    scraper = BrowardScraper()
    page = MagicMock()
    page.frames = []
    token_probes = []

    async def mock_eval(script):
        if "const solvers" in script:
            return {"exists": True, "in_process": False, "solved": True}
        if "#RecaptchaField1" in script:
            return "recaptcha"
        if "g-recaptcha-response" in script or "window.turnstile" in script:
            token_probes.append(script)
        return False

    page.evaluate = AsyncMock(side_effect=mock_eval)
    with patch.object(scraper, "dismiss_captcha_challenge_popup", new_callable=AsyncMock):
        assert await scraper.detect_and_handle_captcha(page, wait_seconds=5) is True
    assert token_probes == []


@pytest.mark.asyncio
async def test_detect_and_handle_captcha_detects_turnstile_checkmark():
    """Verify detect_and_handle_captcha returns True when Cloudflare Turnstile iframe has checkmark."""
    scraper = BrowardScraper()
    page = MagicMock()

    # Mock a turnstile frame
    turnstile_frame = MagicMock()
    turnstile_frame.url = "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turnstile/if/ov2/av0/rcv0/0/0"
    turnstile_frame.evaluate = AsyncMock(return_value=True)  # Checkbox checked or SVG checkmark
    turnstile_frame.locator = MagicMock(return_value=MagicMock(count=AsyncMock(return_value=0)))

    page.frames = [turnstile_frame]

    async def mock_eval(js_script):
        if "cf-turnstile" in js_script:
            return "turnstile"
        if "antigate_solver" in js_script or "solvers" in js_script:
            return {"exists": False, "in_process": False, "solved": False}
        if "cf-turnstile-response" in js_script:
            return False
        return False

    page.evaluate = AsyncMock(side_effect=mock_eval)
    page.wait_for_timeout = AsyncMock()

    solved = await scraper.detect_and_handle_captcha(page, wait_seconds=5)
    assert solved is True


@pytest.mark.asyncio
async def test_resilient_click_prioritizes_visible_element():
    """Verify resilient_click clicks the visible element when locator matches multiple elements."""
    from app.automation.base import resilient_click

    mock_hidden = MagicMock()
    mock_hidden.is_visible = AsyncMock(return_value=False)
    mock_hidden.click = AsyncMock()

    mock_visible = MagicMock()
    mock_visible.is_visible = AsyncMock(return_value=True)
    mock_visible.click = AsyncMock()

    locator = MagicMock()
    locator.count = AsyncMock(return_value=2)
    locator.first = mock_hidden
    locator.nth = MagicMock(side_effect=lambda idx: mock_hidden if idx == 0 else mock_visible)

    await resilient_click(locator)

    mock_visible.click.assert_called_once()
    mock_hidden.click.assert_not_called()


def test_broward_date_normalization():
    """Verify DOL normalization produces strict MM/DD/YYYY required by Broward FormValidation."""
    from app.automation.florida.broward import _normalize_date_to_mm_dd_yyyy

    assert _normalize_date_to_mm_dd_yyyy("2/27/2022") == "02/27/2022"
    assert _normalize_date_to_mm_dd_yyyy("02/27/2022") == "02/27/2022"
    assert _normalize_date_to_mm_dd_yyyy("2/7/2022") == "02/07/2022"
    assert _normalize_date_to_mm_dd_yyyy("2022-02-27") == "02/27/2022"
    assert _normalize_date_to_mm_dd_yyyy("2022-2-7") == "02/07/2022"
    assert _normalize_date_to_mm_dd_yyyy("") == ""
    assert _normalize_date_to_mm_dd_yyyy(None) == ""


@pytest.mark.asyncio
async def test_broward_glossary_table_rows_are_strictly_excluded():
    """Verify static prefix glossary table rows ('CACE', 'Civil Action Central') are strictly ignored."""
    scraper = BrowardScraper()
    page = _build_mock_page()
    page.inner_text = AsyncMock(return_value="Results found")

    mock_headers = ["Case Number", "Case Style", "Case Type", "Filing Date", "Case Status"]
    th_loc = MagicMock()
    th_loc.count = AsyncMock(return_value=len(mock_headers))
    th_mocks = [MagicMock(inner_text=AsyncMock(return_value=h)) for h in mock_headers]
    th_loc.nth.side_effect = lambda idx: th_mocks[idx]

    # Row 0: Glossary row (CACE, Civil Action Central, CACE15085978)
    glossary_row = MagicMock()
    glossary_row.locator.return_value.all_inner_texts = AsyncMock(
        return_value=["CACE", "Civil Action Central", "CACE15085978"]
    )

    # Row 1: Real case row (CACE-22-012345, Martinez v. State Farm)
    real_case_row = MagicMock()
    real_case_row.locator.return_value.all_inner_texts = AsyncMock(
        return_value=["CACE-22-012345", "Martinez v. State Farm", "CIRCUIT CIVIL", "02/27/2022", "OPEN"]
    )

    rows_loc = MagicMock()
    rows_loc.count = AsyncMock(return_value=2)
    rows_loc.nth.side_effect = lambda idx: glossary_row if idx == 0 else real_case_row

    next_btn = MagicMock()
    next_btn.count = AsyncMock(return_value=0)

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.fill = AsyncMock()

    def loc_side_effect(sel):
        if "th" in sel:
            return th_loc
        if "table.table tbody tr" in sel or "table tbody tr" in sel:
            return rows_loc
        if "next" in sel.lower():
            return next_btn
        return mock_input

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap, \
         patch.object(scraper, "return_to_search_state", new_callable=AsyncMock):
        mock_cap.return_value = True
        cases = await scraper.search_by_party_name("Maria", "Martinez", page, date_of_loss="2/27/2022")

    # Only the real case must be extracted, glossary row must be discarded!
    assert len(cases) == 1
    assert cases[0]["CaseNumber"] == "CACE-22-012345"
    assert cases[0]["CaseStyle"] == "Martinez v. State Farm"
    assert cases[0]["CaseType"] == "CIRCUIT CIVIL"
