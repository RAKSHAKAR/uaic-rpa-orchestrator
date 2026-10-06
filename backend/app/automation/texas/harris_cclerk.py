"""Harris County Clerk WebSearch Portal Scraper (Power Automate V4 Parity & Prompt 7 Compliance)."""

import inspect
import logging
import re
from datetime import datetime
from typing import Any

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper, CaptchaResolutionError

logger = logging.getLogger("uaic_orchestrator.automation.harris_cclerk")


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
                return str(await res or "")
            return str(res or "")
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


HARRIS_CCLERK_PORTAL_URL = "https://www.cclerk.hctx.net/Applications/WebSearch/"


class HarrisCountyClerkScraper(BaseCourtScraper):
    """
    Scraper for Harris County Clerk WebSearch (Power Automate V4 Parity).
    Strict Schema: Output does NOT contain CaseType.
    Fully compliant with Prompt 7:
    - Dynamic Settings integration (URL, browser, storage, screenshots, logging)
    - Sequential unique name processing with persistent tab/browser reuse
    - Step A: Go to CClerk tab, wait for load, reload if blank
    - Step B: Click 'County Civil' inside submenu of 'COURTS'
    - Step C: Verify that County Civil search form loads
    - Step D: Fill Last Name, First Name, File Date (From)
    - Step E: Click Search button
    - Step F: Wait for result page
    - Step I: If 'YOUR SEARCH CRITERIA' popup appears, close/cross and continue
    - Step G: Extract ALL columns (Case Number, Case Style, Filing Date, Case Status, Citation, etc.)
    - STRICT SCHEMA: Output dictionary strictly contains:
      CaseNumber, CaseStyle, FilingDate, CaseStatus (NO CaseType!)
    - Step H: ASP.NET GridView pagination traversal across all available pages
    - Step J: Database persistence (te_jsonbody_cclerk & ScrapedCourtCase)
    - Section 4: Return to clean search state between unique names
    """

    def __init__(self, base_url: str | None = None, **kwargs: Any):
        if "captcha_wait_seconds" not in kwargs:
            kwargs["captcha_wait_seconds"] = 120
        if "max_attempts" not in kwargs:
            kwargs["max_attempts"] = 2
        super().__init__(
            county_name="Harris County Clerk (TX)",
            base_url=base_url or "https://www.cclerk.hctx.net/Applications/WebSearch/",
            **kwargs,
        )

    async def check_and_handle_search_criteria_popup(self, page: Page) -> bool:
        """
        Step I: If 'YOUR SEARCH CRITERIA' appears:
        1. Close/Cross the popup.
        2. Continue the workflow.
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
        """Section 4: Return to Harris County Clerk search state (Power Automate V4 Parity: Subflow_Cclerk line 65)."""
        try:
            logger.info(f"[{self.county_name}] Section 4: Returning to search state for next unique name...")
            await self.check_and_handle_search_criteria_popup(page)

            # Power Automate V4 Parity: Click Clear button first
            clear_btn = page.locator(
                "input#ctl00_ContentPlaceHolder1_btnClear, "
                "#ctl00_ContentPlaceHolder1_btnClear, "
                "input[id*='btnClear'], "
                "input[name*='btnClear'], "
                "input[value='Clear' i], "
                "input[type='submit'][value='Clear'], "
                "button:has-text('Clear')"
            )
            if await _safe_count(clear_btn) > 0 and await _safe_is_visible(clear_btn.first):
                await self.biometric_click(page, clear_btn.first)
                await page.wait_for_timeout(800)

            # Clear search inputs if still populated
            for input_sel in [
                "input#ctl00_ContentPlaceHolder1_txtLastName[name='ctl00$ContentPlaceHolder1$txtLastName'], #ctl00_ContentPlaceHolder1_txtLastName, input[name*='txtLastName']",
                "input#ctl00_ContentPlaceHolder1_txtFirstName[name='ctl00$ContentPlaceHolder1$txtFirstName'], #ctl00_ContentPlaceHolder1_txtFirstName, input[name*='txtFirstName']",
                "input#ctl00_ContentPlaceHolder1_txtFrom2[name='ctl00$ContentPlaceHolder1$txtFrom2'], #ctl00_ContentPlaceHolder1_txtFrom2, input[name*='txtFrom2'], #ctl00_ContentPlaceHolder1_txtDateFrom, input[name*='DateFrom']",
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

    async def _navigate_to_county_civil(self, page: Page) -> None:
        """
        Step A, B, C:
        Step A: Go to CClerk tab, wait for page load, reload if blank.
        Step B: Click 'County Civil' inside submenu of 'COURTS'.
        Step C: Verify that County Civil search form loads.
        """
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

        form = page.locator("input#ctl00_ContentPlaceHolder1_txtLastName[name='ctl00$ContentPlaceHolder1$txtLastName'], input#ctl00_ContentPlaceHolder1_txtLastName, input[name*='txtLastName']")
        form_count = await _safe_count(form)
        form_visible = await _safe_is_visible(form.first) if form_count > 0 else False

        if not form_count > 0 or not form_visible:
            # Step B: Hover 'COURTS' and click 'County Civil' (Object: <a href="/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil">County Civil</a>)
            courts_menu = page.locator(
                "a:has-text('COURTS'), "
                "li.dropdown:has-text('COURTS'), "
                "#nav a:has-text('COURTS')"
            )
            if await _safe_count(courts_menu) > 0:
                await _safe_hover(courts_menu.first)
                await page.wait_for_timeout(500)

            civil_link = page.locator(
                "a[href*='/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil'], "
                "a[href*='CourtSearch.aspx?CaseType=Civil'], "
                "a[href*='CaseType=Civil'], "
                "a:has-text('County Civil')"
            )
            if await _safe_count(civil_link) > 0:
                await self.biometric_click(page, civil_link.first)
                await page.wait_for_timeout(1500)

            # Step C: ASP.NET can display a blank document shell before the
            # County Civil form arrives. Wait for the V4 Last Name control.
            if isinstance(page, Page):
                await form.first.wait_for(state="visible", timeout=self.timeout_ms)
            elif await _safe_count(form) > 0:
                wait_fn = getattr(form.first, "wait_for", None)
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

        # Step A, B, C: Navigation & County Civil form readiness
        t_nav_start = datetime.now()
        await self._navigate_to_county_civil(page)
        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=self.base_url)

        # Exception 3: CAPTCHA Retry & Refresh Loop adhering to dynamically configured Max Attempts and CAPTCHA Wait
        max_attempts = max(1, getattr(self, "max_attempts", 2))
        captcha_solved = False

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                logger.info(
                    f"[{self.county_name}] CAPTCHA Retry attempt {attempt}/{max_attempts}. "
                    f"Performing reload and returning to County Civil form..."
                )
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=self.timeout_ms)
                    await page.wait_for_timeout(getattr(self, "reload_backoff_seconds", 2) * 1000)
                    await self._navigate_to_county_civil(page)
                    await self.check_and_handle_search_criteria_popup(page)
                except Exception as e_rel:
                    logger.warning(f"[{self.county_name}] Page reload note: {e_rel}")

            # Step D: Fill search inputs (Exact Objects from prompt: Last Name, First Name, File Date From txtFrom2)
            t_fill_start = datetime.now()
            last_input = page.locator(
                "input#ctl00_ContentPlaceHolder1_txtLastName[name='ctl00$ContentPlaceHolder1$txtLastName'], "
                "input#ctl00_ContentPlaceHolder1_txtLastName, "
                "input[name='ctl00$ContentPlaceHolder1$txtLastName'], "
                "input[name*='txtLastName'], "
                "input[id*='txtLastName']"
            )
            first_input = page.locator(
                "input#ctl00_ContentPlaceHolder1_txtFirstName[name='ctl00$ContentPlaceHolder1$txtFirstName'], "
                "input#ctl00_ContentPlaceHolder1_txtFirstName, "
                "input[name='ctl00$ContentPlaceHolder1$txtFirstName'], "
                "input[name*='txtFirstName'], "
                "input[id*='txtFirstName']"
            )
            dol_input = page.locator(
                "input#ctl00_ContentPlaceHolder1_txtFrom2[name='ctl00$ContentPlaceHolder1$txtFrom2'], "
                "input#ctl00_ContentPlaceHolder1_txtFrom2, "
                "input[name='ctl00$ContentPlaceHolder1$txtFrom2'], "
                "input[placeholder*='File Date from'], "
                "#ctl00_ContentPlaceHolder1_txtDateFrom, "
                "input[name*='DateFrom'], "
                "input[id*='DateFrom'], "
                "#ctl00_ContentPlaceHolder1_txtDateFrom2"
            )

            if await _safe_count(last_input) > 0:
                wait_fn = getattr(last_input.first, "wait_for", None)
                if callable(wait_fn):
                    res = wait_fn(state="visible", timeout=15000)
                    if inspect.isawaitable(res):
                        await res
                await self.biometric_fill(last_input.first, l_name)

            if f_name and await _safe_count(first_input) > 0:
                await self.biometric_fill(first_input.first, f_name)

            if date_of_loss and await _safe_count(dol_input) > 0:
                clean_dol = _normalize_court_date(date_of_loss.strip()) or date_of_loss.strip()
                await self.biometric_fill(dol_input.first, clean_dol)
                logger.info(f"[{self.county_name}] Step D: Filled File Date from with DOL: {clean_dol}")

            await page.wait_for_timeout(500)
            t_fill_end = datetime.now()
            self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=f"{f_name} {l_name}", dol=date_of_loss)

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

        # Step E: Submit search via button click (Object: <input type="submit" name="ctl00$ContentPlaceHolder1$btnSearch" value="Search" id="ctl00_ContentPlaceHolder1_btnSearch" ...>)
        t_sub_start = datetime.now()
        # Select the party-submit object by exact ID. A CSS selector union
        # returns document order, which otherwise selects btnSearchCase (the
        # Case Number search) before the Party search on the live form.
        search_btn = None
        for selector in (
            "input#ctl00_ContentPlaceHolder1_btnSearch[value='Search']",
            "input#ctl00_ContentPlaceHolder1_btnSearch",
            "input[name='ctl00$ContentPlaceHolder1$btnSearch']",
            "input#ctl00_ContentPlaceHolder1_btnParty",
            "input[name='ctl00$ContentPlaceHolder1$btnParty']",
        ):
            candidate = page.locator(selector)
            if await _safe_count(candidate) > 0 and await _safe_is_visible(candidate.first):
                search_btn = candidate.first
                break
        if search_btn is not None:
            logger.info(f"[{self.county_name}] Step E: Clicking 'Search' button...")
            await self.biometric_click(page, search_btn)
        else:
            raise RuntimeError(f"[{self.county_name}] V4 btnParty search control was not found")
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        if isinstance(page, Page):
            # The ASP.NET result postback can show an empty body briefly.
            # V4 ExtractData waits for the result document before reading rows.
            await page.wait_for_function(
                """() => document.readyState === 'complete'
                    && document.body?.innerText.trim().length > 50
                    && /CourtSearch_R\\.aspx/i.test(location.pathname)""",
                timeout=self.timeout_ms,
            )

        # Step F & I: Check for "YOUR SEARCH CRITERIA" popup
        await self.check_and_handle_search_criteria_popup(page)

        # Step G & H: Extract table rows matching V4 with pagination
        # td:eq(0) > a -> CaseNumber
        # td:eq(1) -> CaseStatus
        # td:eq(2) -> FilingDate
        # td:eq(5) -> CaseStyle
        # STRICT SCHEMA: Output dictionary does NOT contain CaseType!
        t_ext_start = datetime.now()
        page_num = 1
        seen_page_signatures: set[tuple[tuple[str, ...], ...]] = set()

        while True:
            page_start_count = len(results)
            page_cases: list[dict[str, Any]] = []
            page_signature: list[tuple[str, ...]] = []
            # Re-check popup on each page
            await self.check_and_handle_search_criteria_popup(page)

            rows = page.locator("table[id*='grd'] tbody tr, table.grid tbody tr, table tbody tr")
            row_count = await _safe_count(rows)
            logger.info(f"[{self.county_name}] Page {page_num}: Found {row_count} potential result rows")

            for i in range(row_count):
                row = rows.nth(i)
                cells = []
                tds = row.locator("td")
                td_count = await _safe_count(tds)
                # V4 extracts td[0] > a plus td[1], td[2], and td[5].
                # The page also contains a three-cell Party/Attorney/Company
                # radio table, which must never become a case record.
                if td_count >= 6 and (not isinstance(page, Page) or await _safe_count(tds.nth(0).locator("a")) > 0):
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

                if len(cells) >= 3:
                    case_num = cells[0].strip()
                    case_status = cells[1].strip() if len(cells) > 1 else ""
                    filing_date = cells[2].strip() if len(cells) > 2 else ""
                    case_style = cells[5].strip() if len(cells) > 5 else ""

                    _HEADER_LABELS = {"CASE NUMBER", "CASE NO.", "CASE NO", "CASE #", ""}
                    if case_num and case_num.upper() not in _HEADER_LABELS:
                        page_signature.append((*[str(cell).strip() for cell in cells], case_num, case_style, filing_date, case_status))
                        # Strict schema: NO CaseType!
                        page_cases.append({
                            "CaseNumber": case_num,
                            "FilingDate": filing_date,
                            "CaseStyle": case_style,
                            "CaseStatus": case_status,
                        })

            signature = tuple(page_signature)
            if page_num > 1 and signature in seen_page_signatures:
                raise RuntimeError(f"[{self.county_name}] Pagination did not advance to new case results (repeated page)")
            seen_page_signatures.add(signature)
            results.extend(page_cases)

            # Step H: Check next page link (ASP.NET WebSearch pagination)
            next_link = page.locator(
                "table[id*='grd'] tr.pager a:has-text('Next'), "
                "table[id*='grd'] tr.pager a:has-text('>'), "
                "a[id*='Next'], a[href*='__doPostBack'][title*='next' i], "
                "a[href*='__doPostBack']:has-text('Next')"
            )
            if await _safe_count(next_link) > 0 and await _safe_is_visible(next_link.first):
                if page_num > 1 and len(results) == page_start_count:
                    raise RuntimeError(f"[{self.county_name}] Pagination did not advance to new case results")
                try:
                    await self.biometric_click(page, next_link.first)
                    await page.wait_for_timeout(1500)
                    page_num += 1
                except Exception:
                    break
            else:
                break

        if not results:
            body_text = (await _get_page_text(page)).lower()
            if not any(message in body_text for message in ("no records found", "no cases found", "no cases matched", "no data available", "no data found")):
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
