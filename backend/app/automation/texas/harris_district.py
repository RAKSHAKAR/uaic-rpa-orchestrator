"""Harris County District Clerk eDocs Portal Scraper (Power Automate V4 Parity & Prompt 8 Compliance)."""

import inspect
import logging
import re
from datetime import datetime
from typing import Any

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper, CaptchaResolutionError

logger = logging.getLogger("uaic_orchestrator.automation.harris_district")


def _normalize_court_date(val: str | None) -> str | None:
    """Normalize court filing date to standard MM/dd/yyyy format."""
    if val is None:
        return None
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ["null", "none", "nan", "n/a", "-", "--"]:
        return ""
    iso_match = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", val_str)
    if iso_match:
        y, m, d = iso_match.groups()
        return f"{int(m):02d}/{int(d):02d}/{y}"
    us_match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", val_str)
    if us_match:
        m, d, y = us_match.groups()
        m_int, d_int = int(m), int(d)
        if m_int > 12 and d_int <= 12:
            m_int, d_int = d_int, m_int
        if len(y) == 2:
            y = f"20{y}" if int(y) < 50 else f"19{y}"
        return f"{m_int:02d}/{d_int:02d}/{y}"
    cleaned = val_str.split("T")[0].split()[0] if (" " in val_str or "T" in val_str) else val_str
    for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%Y/%m/%d", "%m-%d-%Y", "%d/%m/%Y", "%m/%d/%y"]:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            pass
    return val_str


async def _safe_is_visible(locator: Any) -> bool:
    """Helper to safely check visibility across real Playwright locators and test mocks."""
    try:
        if not hasattr(locator, "is_visible"):
            return False
        fn = getattr(locator, "is_visible")
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                return bool(await res)
            return bool(res)
        return False
    except Exception:
        return False


async def _safe_count(locator: Any) -> int:
    """Helper to safely count elements across real Playwright locators and test mocks."""
    try:
        if not hasattr(locator, "count"):
            return 0
        fn = getattr(locator, "count")
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                return int(await res)
            return int(res)
        return 0
    except Exception:
        return 0


async def _safe_get_attribute(locator: Any, attr: str) -> str | None:
    """Helper to safely retrieve an attribute value across Playwright locators and mocks."""
    try:
        if not hasattr(locator, "get_attribute"):
            return None
        fn = getattr(locator, "get_attribute")
        if callable(fn):
            res = fn(attr)
            if inspect.isawaitable(res):
                return await res
            return res
        return None
    except Exception:
        return None


async def _safe_inner_text(locator: Any) -> str:
    """Helper to safely retrieve inner text across Playwright locators and mocks."""
    try:
        if not hasattr(locator, "inner_text"):
            return ""
        fn = getattr(locator, "inner_text")
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                res = await res
            return res if isinstance(res, str) else ""
        return ""
    except Exception:
        return ""


async def _safe_click(locator: Any) -> None:
    """Helper to safely click element across real Playwright locators and test mocks."""
    try:
        fn = getattr(locator, "click", None)
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                await res
            return
    except Exception:
        pass
    try:
        eval_fn = getattr(locator, "evaluate", None)
        if callable(eval_fn):
            res = eval_fn("el => { if (el) { el.scrollIntoView({block: 'center', inline: 'center'}); el.click(); } }")
            if inspect.isawaitable(res):
                await res
    except Exception:
        pass


async def _safe_hover(locator: Any) -> None:
    """Helper to safely hover element across real Playwright locators and test mocks."""
    try:
        fn = getattr(locator, "hover", None)
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                await res
    except Exception:
        pass


async def _safe_reload(page: Any) -> None:
    """Helper to safely reload page without throwing unawaited mock errors."""
    try:
        reload_fn = getattr(page, "reload", None)
        if callable(reload_fn):
            res = reload_fn(wait_until="domcontentloaded")
            if inspect.isawaitable(res):
                await res
    except Exception:
        pass


async def _get_page_text(page: Any) -> str:
    """Helper to safely get page body text across Playwright Page and test mocks."""
    try:
        if hasattr(page, "inner_text"):
            fn = getattr(page, "inner_text")
            if callable(fn):
                res = fn("body")
                if inspect.isawaitable(res):
                    return str(await res or "")
                if isinstance(res, str):
                    return res
    except Exception:
        pass
    try:
        if hasattr(page, "locator"):
            return await _safe_inner_text(page.locator("body"))
    except Exception:
        pass
    return ""


def _is_valid_case_result(case_number: str, case_style: str, filing_date: str) -> bool:
    """Reject layout and empty-state cells before they can become court cases."""
    number = case_number.strip()
    return (
        bool(number)
        and number.upper() not in {"CASE NUMBER", "CASE NO.", "CASE NO", "CASE #"}
        and len(number) <= 100
        and bool(re.search(r"\d", number))
        and "no results" not in number.lower()
        and bool(case_style.strip())
        and bool(filing_date.strip())
    )


def _date_for_input(date_text: str, input_type: str | None) -> str:
    """Use the browser's ISO value for native date controls, V4 text otherwise."""
    if (input_type or "").lower() == "date":
        return datetime.strptime(date_text, "%m/%d/%Y").strftime("%Y-%m-%d")
    return date_text


HARRIS_DISTRICT_PORTAL_URL = "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"

HARRIS_DISTRICT_RESULT_READY_JS = r"""() => {
    const bodyText = document.body?.innerText || '';
    const lowerText = bodyText.toLowerCase();
    if (['your search did not return any records', 'no results found',
        'no records found', 'no cases found', 'no cases matched',
        'no data available'].some(message => lowerText.includes(message))) return true;

    const docket = document.querySelector('table.docketTable');
    if (docket) {
        const totalMatch = bodyText.match(/Total records returned from search is\s+(\d+)/i);
        const pager = document.querySelector('table.PagerContainerTable');
        const pageMatch = pager?.innerText.match(/Page\s+1\s+of\s+(\d+)/i);
        if (!totalMatch || !pageMatch) return false;

        const total = Number(totalMatch[1]);
        const pageCount = Number(pageMatch[1]);
        let expectedRows = total;
        if (pageCount > 1) {
            const pageTwo = [...pager.querySelectorAll('a[title*="Show Result"]')]
                .find(link => link.innerText.trim() === '2');
            const range = pageTwo?.title.match(/Show Result\s+(\d+)\s+to/i);
            if (!range) return false;
            expectedRows = Number(range[1]) - 1;
        }
        const dataRows = [...docket.querySelectorAll('tbody tr')].filter(row => {
            const cells = row.querySelectorAll('td');
            return cells.length >= 7 && /\d/.test(cells[0].innerText);
        });
        return dataRows.length === expectedRows;
    }

    const legacyGrid = document.querySelector(
        'table[id*="dgSearchResults"], .grid-results, table.grid'
    );
    return Boolean(legacyGrid?.querySelector('tbody tr'));
}"""


class HarrisDistrictClerkScraper(BaseCourtScraper):
    """
    Scraper for Harris County District Clerk eDocs Public Search (Power Automate V4 Parity).
    Fully compliant with Prompt 8:
    - Dynamic Settings integration (URL, browser, storage, screenshots, logging)
    - Sequential unique name processing with persistent tab/browser reuse
    - Step A: Go to HCDistrict tab, wait for load, reload if blank
    - Step B: Click 'Search Our Records'
    - Step C: Verify that the search page loads & Party Inquiry tab is active
    - Step D: Fill Last Name, First Name, File Date (From)
    - Step E: Click Search button
    - Step F: Wait for result page
    - Step I: If 'YOUR SEARCH CRITERIA' popup appears, close/cross and continue
    - Step G: Extract ALL columns (Case Number, Case Style, Filing Date, Case Status, Case Type, Citation, etc.)
    - SCHEMA: Output dictionary includes CaseType:
      CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType
    - Step H: ASP.NET GridView pagination traversal across all available pages
    - Step J: Database persistence (te_jsonbody_hcdistrict & ScrapedCourtCase)
    - Section 4: Return to clean search state between unique names
    """

    def __init__(self, base_url: str | None = None, **kwargs: Any):
        if "captcha_wait_seconds" not in kwargs:
            kwargs["captcha_wait_seconds"] = 120
        if "max_attempts" not in kwargs:
            kwargs["max_attempts"] = 2
        super().__init__(
            county_name="Harris District Clerk (TX)",
            base_url=base_url or "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx",
            **kwargs,
        )

    async def check_and_handle_search_criteria_popup(self, page: Page) -> bool:
        """
        Step I: If 'YOUR SEARCH CRITERIA' appears:
        1. Close/Cross the popup.
        2. Continue the search/result workflow.
        """
        try:
            popup_loc = page.locator(
                "div:has-text('YOUR SEARCH CRITERIA'), "
                "div:has-text('SEARCH CRITERIA'), "
                "div:has-text('NO CASES MATCHED'), "
                "#messageModal, .modal-dialog:has-text('SEARCH CRITERIA')"
            )
            if await _safe_count(popup_loc) > 0 and await _safe_is_visible(popup_loc):
                close_btn = page.locator(
                    "a#messageClose, "
                    "button:has-text('Close'), "
                    "a:has-text('Close'), "
                    "button:has-text('×'), "
                    "button:has-text('X'), "
                    ".modal-header .close, "
                    "button[aria-label*='Close' i], "
                    "#btnCriteriaClose, "
                    "button:has-text('OK')"
                )
                if await _safe_count(close_btn) > 0 and await _safe_is_visible(close_btn):
                    logger.info(f"[{self.county_name}] Step I: 'YOUR SEARCH CRITERIA' popup detected; closing...")
                    await self.biometric_click(page, close_btn.first)
                    await page.wait_for_timeout(1000)
                    return True
        except Exception as e:
            logger.debug(f"[{self.county_name}] Popup check note: {e}")
        return False

    async def return_to_search_state(self, page: Page) -> None:
        """Section 4: Return to Harris District search state (Power Automate V4 Parity: Subflow_HarrisDistrict line 93)."""
        try:
            logger.info(f"[{self.county_name}] Section 4: Returning to search state for next unique name...")
            await self.check_and_handle_search_criteria_popup(page)

            # Power Automate V4 Parity: Click Search Again button
            search_again_btn = page.locator(
                "#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnSearchAgain, "
                "input[id*='btnSearchAgain'], "
                "input[value*='Search Again' i], "
                "button:has-text('Search Again'), "
                "a:has-text('Search Again')"
            )
            if await _safe_count(search_again_btn) > 0 and await _safe_is_visible(search_again_btn.first):
                await self.biometric_click(page, search_again_btn.first)
                await page.wait_for_timeout(1000)
            else:
                try:
                    eval_fn = getattr(page, "evaluate", None)
                    if callable(eval_fn):
                        res = eval_fn("() => { const b = document.getElementById('ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnSearchAgain') || document.querySelector('input[id*=\"btnSearchAgain\"]'); if (b) b.click(); }")
                        if inspect.isawaitable(res):
                            await res
                        await self.pace_action(page)
                except Exception:
                    pass

            # Clear search input fields if still populated
            for input_sel in [
                "input#txtPartyName[name*='txtPartyName'], #txtPartyName, input[id*='txtPartyName']",
                "#partyLastName, #txtPartyLastName, input[name*='txtPartyLastName']",
                "#partyFirstName, #txtPartyFirstName, input[name*='txtPartyFirstName']",
                "input#txtPartyStartDate[name*='txtPartyStartDate'], #txtPartyStartDate, input[id*='txtFiledDateFrom'], input[id*='txtDateFrom']",
                "input#txtPartyEndDate[name*='txtPartyEndDate'], #txtPartyEndDate, input[id*='txtFiledDateTo']",
            ]:
                loc = page.locator(input_sel)
                if await _safe_count(loc) > 0 and await _safe_is_visible(loc.first):
                    clear_fn = getattr(loc.first, "clear", None)
                    if callable(clear_fn):
                        res = clear_fn()
                        if inspect.isawaitable(res):
                            await res
                    else:
                        fill_fn = getattr(loc.first, "fill", None)
                        if callable(fill_fn):
                            res = fill_fn("")
                            if inspect.isawaitable(res):
                                await res
        except Exception as e:
            logger.debug(f"[{self.county_name}] Return to search state note: {e}")

    async def _navigate_to_search_page(self, page: Page) -> None:
        """
        Step A, B, C:
        Step A: Go to HCDistrict tab, wait for load, reload if blank.
        Step B: Click 'Search Our Records'.
        Step C: Verify that the search page loads, ensure Party Inquiry is active, click reset button.
        """
        # If already on the search page with inputs visible, ensure Party Inquiry and reset
        party_input = page.locator("input#txtPartyName[name*='txtPartyName'], #txtPartyName, #partyLastName, input[name*='Party'], #txtPartyLastName")
        already_on_page = await _safe_count(party_input) > 0 and await _safe_is_visible(party_input.first)

        if not already_on_page:
            # Navigate to base URL
            await page.goto(self.base_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)

            # Check for empty body in real browser (Step a: check body length < 5)
            try:
                body_text = await _get_page_text(page)
                if not body_text or len(body_text.strip()) < 5:
                    logger.warning(f"[{self.county_name}] Step A: Blank/incomplete body detected; reloading...")
                    await _safe_reload(page)
                    await page.wait_for_timeout(2000)
            except Exception:
                pass

            # Step B: Click 'Search Our Records' if on landing page (Object: div.cardBody / Icon_Nav_Search)
            search_records_link = page.locator(
                "div.cardBody:has-text('Search Our Records'), "
                ".card-body:has-text('Search Our Records'), "
                "p.cardText:has-text('Search Our Records'), "
                "img[src*='Icon_Nav_Search'], "
                "a:has-text('Search Our Records'), "
                "span:has-text('Search Our Records'), "
                "a[href*='Search.aspx'], "
                "a[href*='Search']"
            )
            if await _safe_count(search_records_link) > 0 and await _safe_is_visible(search_records_link.first):
                logger.info(f"[{self.county_name}] Step B: Clicking 'Search Our Records'...")
                await self.biometric_click(page, search_records_link.first)
                await page.wait_for_timeout(1500)

        # Step C: Ensure Party Inquiry tab is active (Object: <input type="button" name="...$tabParty" ... id="tabParty" ...>)
        party_inquiry_link = page.locator(
            "input#tabParty[name*='tabParty'], "
            "#tabParty, "
            "input[value*='Party Inquiry' i], "
            "a:has-text('Party Inquiry'), "
            "#btnPartyInquiry, "
            "a[href*='Party'], "
            "#nav-Party"
        )
        if await _safe_count(party_inquiry_link) > 0 and await _safe_is_visible(party_inquiry_link.first):
            cls = (await _safe_get_attribute(party_inquiry_link.first, "class")) or ""
            if "active" not in cls:
                await self.biometric_click(page, party_inquiry_link.first)
                await page.wait_for_timeout(800)

        # Step C: Click reset button (Object: <input type="reset" value="reset" class="btn dcoButtons" style="margin-left:1%;">)
        reset_btn = page.locator(
            "input[type='reset'][value*='reset' i], "
            "input.dcoButtons[type='reset'], "
            "input[value='reset'], "
            "button:has-text('reset')"
        )
        if await _safe_count(reset_btn) > 0 and await _safe_is_visible(reset_btn.first):
            logger.info(f"[{self.county_name}] Step C: Clicking reset button...")
            await self.biometric_click(page, reset_btn.first)
            await page.wait_for_timeout(500)

        # Step C: Verify search input readiness
        if await _safe_count(party_input) > 0:
            wait_fn = getattr(party_input.first, "wait_for", None)
            if callable(wait_fn):
                res = wait_fn(state="visible", timeout=15000)
                if inspect.isawaitable(res):
                    await res

    async def search_by_party_name(
        self,
        first_name: str | None,
        last_name: str | None,
        page: Page,
        date_of_loss: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        l_name = (last_name or "").strip()
        f_name = (first_name or "").strip()

        if not l_name:
            return results

        # Step A, B, C: Navigation & Search Page readiness
        t_nav_start = datetime.now()
        await self._navigate_to_search_page(page)
        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=self.base_url)

        # Exception 3: CAPTCHA Retry & Refresh Loop adhering to dynamically configured Max Attempts and CAPTCHA Wait
        max_attempts = max(1, getattr(self, "max_attempts", 2))
        captcha_solved = False

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                logger.info(
                    f"[{self.county_name}] CAPTCHA Retry attempt {attempt}/{max_attempts}. "
                    f"Performing reload and returning to search page..."
                )
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=self.timeout_ms)
                    await page.wait_for_timeout(getattr(self, "reload_backoff_seconds", 2) * 1000)
                    await self._navigate_to_search_page(page)
                    await self.check_and_handle_search_criteria_popup(page)
                except Exception as e_rel:
                    logger.warning(f"[{self.county_name}] Page reload note: {e_rel}")

            # Step D: Fill search inputs (support separate inputs and combined party name)
            t_fill_start = datetime.now()
            last_input = page.locator("#partyLastName, #txtPartyLastName, input[name*='txtPartyLastName'], input[name*='partyLastName']")
            first_input = page.locator("#partyFirstName, #txtPartyFirstName, input[name*='txtPartyFirstName'], input[name*='partyFirstName']")
            party_input = page.locator(
                "input#txtPartyName[name='ctl00$ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder2$ContentPlaceHolder2$txtPartyName'], "
                "input#txtPartyName, "
                "#txtPartyName, "
                "input[id*='txtPartyName'], "
                "input[name*='txtPartyName'], "
                "#txtPartyLastName"
            )
            dol_input = page.locator(
                "input#txtPartyStartDate[name='ctl00$ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder2$ContentPlaceHolder2$txtPartyStartDate'], "
                "input#txtPartyStartDate, "
                "#txtPartyStartDate, "
                "input[id*='txtPartyStartDate'], "
                "input[name*='txtPartyStartDate'], "
                "input[id*='txtFiledDateFrom'], "
                "input[name*='txtFiledDateFrom'], "
                "input[id*='txtDateFrom'], "
                "input[id*='filingDateFrom']"
            )
            end_date_input = page.locator(
                "input#txtPartyEndDate[name='ctl00$ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder2$ContentPlaceHolder2$txtPartyEndDate'], "
                "input#txtPartyEndDate, "
                "#txtPartyEndDate, "
                "input[id*='txtPartyEndDate'], "
                "input[name*='txtPartyEndDate'], "
                "input[id*='txtFiledDateTo']"
            )

            query = f"{l_name}, {f_name}".strip(", ")
            filled_individual = False

            if await _safe_count(last_input) > 0 and await _safe_is_visible(last_input.first):
                await self.biometric_fill(last_input.first, l_name)
                if f_name and await _safe_count(first_input) > 0:
                    await self.biometric_fill(first_input.first, f_name)
                filled_individual = True
                logger.info(f"[{self.county_name}] Step D: Filled individual party fields: {l_name}, {f_name}")

            if not filled_individual and await _safe_count(party_input) > 0:
                wait_fn = getattr(party_input.first, "wait_for", None)
                if callable(wait_fn):
                    res = wait_fn(state="visible", timeout=15000)
                    if inspect.isawaitable(res):
                        await res
                await self.biometric_fill(party_input.first, query)
                logger.info(f"[{self.county_name}] Step D: Filled combined Party Name: {query}")

            # Step D: Filed Date Range (From): DOL
            if date_of_loss and await _safe_count(dol_input) > 0:
                clean_dol = _normalize_court_date(date_of_loss.strip()) or date_of_loss.strip()
                dol_type = await _safe_get_attribute(dol_input.first, "type")
                await self.biometric_fill(dol_input.first, _date_for_input(clean_dol, dol_type))
                logger.info(f"[{self.county_name}] Step D: Filled Filed Date Range From with DOL: {clean_dol}")

            # Step D: Filed Date Range (To): Today's date
            if await _safe_count(end_date_input) > 0 and await _safe_is_visible(end_date_input.first):
                today_str = datetime.now().strftime("%m/%d/%Y")
                end_type = await _safe_get_attribute(end_date_input.first, "type")
                await self.biometric_fill(end_date_input.first, _date_for_input(today_str, end_type))
                logger.info(f"[{self.county_name}] Step D: Filled Filed Date Range To with Today's Date: {today_str}")

            await page.wait_for_timeout(500)
            t_fill_end = datetime.now()
            self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=query, dol=date_of_loss)

            # CAPTCHA verification if any
            t_cap_start = datetime.now()
            captcha_ok = await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
            t_cap_end = datetime.now()
            self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end, status="SUCCESS" if captcha_ok else "TIMEOUT")

            if captcha_ok:
                captcha_solved = True
                logger.info(f"[{self.county_name}] CAPTCHA solved! Immediately submitting search...")
                break
            else:
                logger.warning(
                    f"[{self.county_name}] CAPTCHA unsolved after {self.captcha_wait_seconds}s (attempt {attempt}/{max_attempts})"
                )

        if not captcha_solved:
            logger.error(f"[{self.county_name}] CAPTCHA verification failed after {max_attempts} attempts for '{f_name} {l_name}'.")
            raise CaptchaResolutionError(f"[{self.county_name}] CAPTCHA was not resolved after {max_attempts} attempts")

        # Step E: Click Search Button (Object: <input type="submit" name="...$btnPartySearch" value="Search" id="ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch" ...>)
        t_sub_start = datetime.now()
        search_btn = page.locator(
            "input#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch"
        )
        if await _safe_count(search_btn) > 0:
            logger.info(f"[{self.county_name}] Step E: Clicking 'Search' button...")
            await self.biometric_click(page, search_btn.first)
        else:
            raise RuntimeError(f"[{self.county_name}] V4 btnPartySearch control was not found")
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # Step F & I: Check for "YOUR SEARCH CRITERIA" popup
        await self.check_and_handle_search_criteria_popup(page)

        # V4's ExtractTable waits for the result page. Wait for a visible
        # outcome before parsing so the search form's layout tables cannot be
        # mistaken for returned cases while the portal is still processing.
        wait_for_function = getattr(page, "wait_for_function", None)
        if callable(wait_for_function):
            try:
                pending_outcome = wait_for_function(
                    HARRIS_DISTRICT_RESULT_READY_JS,
                    timeout=self.timeout_ms,
                )
                if inspect.isawaitable(pending_outcome):
                    await pending_outcome
            except Exception as error:
                raise RuntimeError(
                    f"[{self.county_name}] Result page did not finish loading within the navigation timeout"
                ) from error

        # Step G & H: Extract table rows matching V4 with pagination
        # td:eq(0) -> CaseNumber
        # td:eq(1) -> CaseStyle
        # td:eq(3) -> CaseStatus
        # td:eq(5) -> FilingDate
        # td:eq(6) -> CaseType (INCLUDED for Harris District)
        t_ext_start = datetime.now()
        seen_page_signatures: set[tuple[tuple[str, ...], ...]] = set()
        page_num = 1

        while True:
            page_start_count = len(results)
            page_cells: list[tuple[str, ...]] = []
            # Re-check popup on each page
            await self.check_and_handle_search_criteria_popup(page)

            # V4 extracts the result grid, not every table on the search form.
            # The broad `table tbody tr` fallback could turn a hidden empty-state
            # or form layout cell into a case number.
            rows = page.locator(
                "table.docketTable tbody tr, table[id*='dgSearchResults'] tbody tr, "
                ".grid-results tr, table.grid tbody tr"
            )
            row_count = await _safe_count(rows)
            logger.info(f"[{self.county_name}] Page {page_num}: Found {row_count} potential result rows")

            for i in range(row_count):
                row = rows.nth(i)
                cells = []
                tds = row.locator("td")
                td_count = await _safe_count(tds)
                if td_count >= 3:
                    if hasattr(tds, "all_inner_texts"):
                        fn_ait = getattr(tds, "all_inner_texts")
                        if callable(fn_ait):
                            res_ait = fn_ait()
                            if inspect.isawaitable(res_ait):
                                cells = await res_ait
                            elif isinstance(res_ait, list):
                                cells = res_ait
                    if not cells:
                        for td_idx in range(td_count):
                            cells.append(await _safe_inner_text(tds.nth(td_idx)))

                if len(cells) >= 7:
                    page_cells.append(tuple(cells))
                    case_num = cells[0].strip()
                    style_node = tds.nth(1).locator("a strong")
                    case_style = (await _safe_inner_text(style_node.first)).strip() if await _safe_count(style_node) else ""
                    if not case_style:
                        case_style = cells[1].strip() if len(cells) > 1 else ""
                    filing_date = cells[5].strip() if len(cells) > 5 else ""
                    case_type = cells[6].strip() if len(cells) > 6 else ""

                    # V4 derives status from the first extracted cell rather
                    # than an unrelated grid column.
                    status_text = re.sub(r"[0-9]|-\s*(?:\r?\n)?", "", case_num)
                    status_text = re.sub(r"(?m)^\s*$|^\s*-\s*$|^\s*[A-Za-z]\s*$|^\s*\d+\s*$", "", status_text)
                    case_status = status_text.strip() or (cells[3].strip() if len(cells) > 3 else "")

                    if _is_valid_case_result(case_num, case_style, filing_date):
                        results.append({
                            "CaseNumber": case_num,
                            "CaseStyle": case_style,
                            "FilingDate": filing_date,
                            "CaseStatus": case_status,
                            "CaseType": case_type,
                        })

            page_signature = tuple(page_cells)
            if page_num > 1 and page_signature in seen_page_signatures:
                raise RuntimeError(f"[{self.county_name}] Pagination repeated a prior result page")
            seen_page_signatures.add(page_signature)

            # Step H: Check next page link (ASP.NET GridView pager)
            next_link = page.locator(
                "table.PagerContainerTable a[title*='Next to Page' i], "
                "table[id*='dgSearchResults'] tr.pager a:has-text('Next'), "
                "table[id*='dgSearchResults'] tr.pager a:has-text('>'), "
                "a[id*='btnNext'], a[href*='__doPostBack']:has-text('Next')"
            )
            if await _safe_count(next_link) > 0 and await _safe_is_visible(next_link.first):
                try:
                    next_page = page_num + 1
                    previous_first_row = (
                        results[page_start_count]["CaseNumber"]
                        if len(results) > page_start_count else ""
                    )
                    expected_data_rows = None
                    numbered_links = page.locator(
                        "table.PagerContainerTable a[title*='Show Result']"
                    )
                    for link_index in range(await _safe_count(numbered_links)):
                        numbered_link = numbered_links.nth(link_index)
                        if (await _safe_inner_text(numbered_link)).strip() != str(next_page):
                            continue
                        range_title = await _safe_get_attribute(numbered_link, "title") or ""
                        match = re.search(r"Show Result\s+(\d+)\s+to\s+(\d+)", range_title, re.I)
                        if match:
                            expected_data_rows = int(match.group(2)) - int(match.group(1)) + 1
                        break
                    await self.biometric_click(page, next_link.first)
                    if callable(wait_for_function):
                        pending_page = wait_for_function(
                            """({expected, requiredRows, previousFirstRow}) => {
                                const pager = document.querySelector('table.PagerContainerTable');
                                if (!pager) return Boolean(document.querySelector(
                                    'table[id*="dgSearchResults"], .grid-results, table.grid'
                                ));
                                if (!pager.innerText.includes(`Page ${expected} of`)) return false;
                                if (requiredRows === null) return true;
                                const rows = [...document.querySelectorAll(
                                    'table.docketTable tbody tr'
                                )].filter(row => {
                                    const cells = row.querySelectorAll('td');
                                    return cells.length >= 7 && /\\d/.test(cells[0].innerText);
                                });
                                return rows.length === requiredRows &&
                                    (!previousFirstRow ||
                                        rows[0].querySelector('td').innerText.trim() !== previousFirstRow);
                            }""",
                            arg={
                                "expected": next_page,
                                "requiredRows": expected_data_rows,
                                "previousFirstRow": previous_first_row,
                            },
                            timeout=self.timeout_ms,
                        )
                        if inspect.isawaitable(pending_page):
                            await pending_page
                    page_num = next_page
                except Exception as error:
                    raise RuntimeError(
                        f"[{self.county_name}] Could not advance result pagination to page {page_num + 1}"
                    ) from error
            else:
                break

        if not results:
            body_text = (await _get_page_text(page)).lower()
            if not any(message in body_text for message in (
                "your search did not return any records",
                "no results found", "no records found", "no cases found",
                "no cases matched", "no data available",
            )):
                raise RuntimeError(f"[{self.county_name}] Search completed without results or a verified no-match message")

        t_ext_end = datetime.now()
        self.record_stage(
            "result_retrieval",
            "Result Retrieval",
            t_ext_start,
            t_ext_end,
            cases_found=len(results),
            result_category="Data Found" if results else "No Record Found",
        )

        return results
