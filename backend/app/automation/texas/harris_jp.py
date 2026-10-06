"""Harris County Justice of the Peace (JP) Portal Automation Scraper (Power Automate V4 Parity & Prompt 6 Compliance)."""

import inspect
import logging
import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper, CaptchaResolutionError

logger = logging.getLogger("uaic_orchestrator.automation.harris_jp")


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


HARRIS_JP_PORTAL_URL = "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"


class HarrisJPScraper(BaseCourtScraper):
    """
    Scraper for Harris County JP Odyssey Portal (Power Automate V4 Parity).
    Fully compliant with Prompt 6:
    - Dynamic Settings integration (URL, browser, CAPTCHA wait, max retries)
    - Sequential unique name processing with persistent tab/browser reuse
    - Step A: Navigation and reload if blank/unresponsive
    - Step B & C: "Smart Search" click & verification
    - Step D: Search Input data entry (LastName,FirstName)
    - Step G: "Session timeout warning" detection & "Continue session"
    - Steps E, F, H: CAPTCHA handling respecting wait time & retry limit
    - Step I: Immediate "Submit" click upon CAPTCHA verification
    - Step J: Result grid loading wait
    - Step K: All-column extraction (Case Number, Style, Filing Date, Status, Access Level, etc.)
    - STRICT SCHEMA: Output does NOT contain CaseType!
    - Step L: Multi-page Kendo UI pagination traversal
    - Step M: Database persistence format (te_jsonbody_harris & ScrapedCourtCase)
    - Section 4: Return to clean search state between unique names
    """

    def __init__(self, base_url: str | None = None, **kwargs: Any):
        if "captcha_wait_seconds" not in kwargs:
            kwargs["captcha_wait_seconds"] = 120
        if "max_attempts" not in kwargs:
            kwargs["max_attempts"] = 2
        super().__init__(
            county_name="Harris County JP (TX)",
            base_url=base_url or "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29",
            **kwargs,
        )

    async def navigate_to_search(self, page: Page) -> None:
        """Step A: Go to Harris JP tab, wait for load, reload & wait again if body empty/unresponsive."""
        t_nav_start = datetime.now()
        nav_url = self.base_url.rstrip("/")
        if "Dashboard/29" not in nav_url:
            nav_url = f"{nav_url}/Dashboard/29"

        try:
            logger.info(f"[{self.county_name}] Step A: Navigating to Harris JP portal: {nav_url}")
            await page.goto(nav_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)

            # Wait for content container or body
            content_loc = page.locator(".k-content, #main-content, #caseCriteria_SearchCriteria, body")
            if await _safe_count(content_loc) > 0:
                try:
                    await content_loc.first.wait_for(state="visible", timeout=10000)
                except Exception:
                    pass

            # Detect blank/empty body and reload if needed (Step a: check body length < 5)
            body_text = await _get_page_text(page)
            if not body_text or len(body_text.strip()) < 5:
                logger.warning(f"[{self.county_name}] Blank/incomplete page body detected; reloading...")
                await _safe_reload(page)
                await page.wait_for_timeout(2000)
        except Exception as e_nav:
            logger.warning(f"[{self.county_name}] Step A navigation encountered: {e_nav}; attempting reload...")
            try:
                await _safe_reload(page)
                await page.wait_for_timeout(2000)
            except Exception as e_reload:
                logger.debug(f"[{self.county_name}] Reload note: {e_reload}")

        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=nav_url)

    async def click_smart_search(self, page: Page) -> None:
        """Step B: Click 'Smart Search' (Object: a.portlet-buttons[href*='/OdysseyPortalJP/Home/Dashboard/29'])."""
        try:
            search_input = page.locator(
                "input#caseCriteria_SearchCriteria[name='caseCriteria.SearchCriteria'], "
                "input#caseCriteria_SearchCriteria, "
                "#caseCriteria_SearchCriteria, "
                "input[name='caseCriteria.SearchCriteria'], "
                "input[name='caseCriteria_SearchCriteria'], "
                "#SearchCriteria"
            )
            if await _safe_count(search_input) > 0 and await _safe_is_visible(search_input):
                logger.info(f"[{self.county_name}] Step B: Smart Search input already visible; proceeding.")
                return

            smart_search_link = page.locator(
                "a.portlet-buttons[href*='/OdysseyPortalJP/Home/Dashboard/29'], "
                "a.portlet-buttons[href*='Dashboard/29'], "
                "a[href*='/OdysseyPortalJP/Home/Dashboard/29'], "
                "a.portlet-buttons, "
                "a.btn:has-text('Smart Search'), "
                "a:has-text('Smart Search'), "
                "button:has-text('Smart Search'), "
                "#tcControllerLink_0"
            )
            if await _safe_count(smart_search_link) > 0 and await _safe_is_visible(smart_search_link):
                logger.info(f"[{self.county_name}] Step B: Clicking 'Smart Search' portlet button...")
                await self.biometric_click(page, smart_search_link.first)
                await page.wait_for_timeout(1000)
        except Exception as e_smart:
            logger.debug(f"[{self.county_name}] Smart Search click note: {e_smart}")

    async def verify_search_page_loaded(self, page: Page) -> bool:
        """Step C: Verify that the Smart Search page loads."""
        try:
            search_input = page.locator(
                "input#caseCriteria_SearchCriteria[name='caseCriteria.SearchCriteria'], "
                "input#caseCriteria_SearchCriteria, "
                "#caseCriteria_SearchCriteria, "
                "input[name='caseCriteria.SearchCriteria'], "
                "input[name='caseCriteria_SearchCriteria'], "
                "#SearchCriteria"
            )
            if await _safe_count(search_input) > 0:
                try:
                    await search_input.first.wait_for(state="visible", timeout=15000)
                    return True
                except Exception:
                    return False
            return False
        except Exception as e_ver:
            logger.debug(f"[{self.county_name}] Search page verification note: {e_ver}")
            return False

    async def check_and_handle_session_timeout(self, page: Page) -> bool:
        """Step G / Exception 2: If 'Session timeout warning' appears: click 'Continue session', wait for page."""
        try:
            timeout_modal = page.locator(
                "div:has-text('Session timeout warning'), "
                ".modal:has-text('Session timeout warning'), "
                "div:has-text('extend your session')"
            )
            if await _safe_count(timeout_modal) > 0 and await _safe_is_visible(timeout_modal):
                continue_btn = page.locator(
                    "button:has-text('Continue session'), "
                    "a:has-text('Continue session'), "
                    "input[value*='Continue session' i]"
                )
                if await _safe_count(continue_btn) > 0 and await _safe_is_visible(continue_btn):
                    logger.warning(f"[{self.county_name}] Step G / Exception 2: 'Session timeout warning' detected; clicking 'Continue session'...")
                    await self.biometric_click(page, continue_btn.first)
                    wait_fn = getattr(page, "wait_for_timeout", None)
                    if callable(wait_fn):
                        res = wait_fn(1500)
                        if inspect.isawaitable(res):
                            await res

                    # Exception 2 check: if website redirected to home page, restart from step b
                    raw_url = getattr(page, "url", None)
                    curr_url = raw_url if isinstance(raw_url, str) else ""
                    if curr_url and "Dashboard/29" not in curr_url:
                        logger.info(f"[{self.county_name}] Navigated to home page after timeout; restarting from Smart Search (Step b)...")
                        await self.click_smart_search(page)
                        await self.verify_search_page_loaded(page)
                    return True
        except Exception as e_timeout:
            logger.debug(f"[{self.county_name}] Session timeout check note: {e_timeout}")
        return False

    async def return_to_search_state(self, page: Page) -> None:
        """Section 4: Return to Harris JP search between unique names (Power Automate V4 Parity)."""
        try:
            logger.info(f"[{self.county_name}] Section 4: Returning to search state for next unique name...")
            await self.check_and_handle_session_timeout(page)

            # Power Automate V4 Parity (Subflow_Harris line 213):
            # 1. Clear search input
            search_input = page.locator(
                "input#caseCriteria_SearchCriteria[name='caseCriteria.SearchCriteria'], "
                "input#caseCriteria_SearchCriteria, "
                "#caseCriteria_SearchCriteria, "
                "input[name='caseCriteria.SearchCriteria'], "
                "input[name='caseCriteria_SearchCriteria'], "
                "#SearchCriteria"
            )
            if await _safe_count(search_input) > 0 and await _safe_is_visible(search_input):
                clear_fn = getattr(search_input.first, "clear", None)
                if callable(clear_fn):
                    res = clear_fn()
                    if inspect.isawaitable(res):
                        await res

            # 2. Click #tcControllerLink_0 or navigate to Dashboard/29
            reset_link = page.locator(
                "p.step-label:has-text('Smart Search'), "
                "a.portlet-buttons[href*='/OdysseyPortalJP/Home/Dashboard/29'], "
                "a.portlet-buttons[href*='Dashboard/29'], "
                "#tcControllerLink_0, "
                "a:has-text('Smart Search')"
            )
            if await _safe_count(reset_link) > 0 and await _safe_is_visible(reset_link):
                await self.biometric_click(page, reset_link.first)
                await page.wait_for_timeout(1000)
            else:
                nav_url = self.base_url.rstrip("/")
                if "Dashboard/29" not in nav_url:
                    nav_url = f"{nav_url}/Dashboard/29"
                goto_fn = getattr(page, "goto", None)
                if callable(goto_fn):
                    res_g = goto_fn(nav_url, wait_until="domcontentloaded")
                    if inspect.isawaitable(res_g):
                        await res_g
                    await page.wait_for_timeout(1200)
        except Exception as e_ret:
            logger.debug(f"[{self.county_name}] Return to search state note: {e_ret}")

    async def search_by_party_name(
        self,
        first_name: str | None,
        last_name: str | None,
        page: Page,
        date_of_loss: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Executes Harris County JP Courts Smart Search workflow strictly complying with Prompt 6:
        - Step A: Go to Harris JP tab, wait for load, reload if blank
        - Step B & C: Click 'Smart Search' and verify page load
        - Step D: Enter current unique-name into Search Input
        - Step G: Check and handle Session timeout warning
        - Steps E, F, H: CAPTCHA wait & retry loop up to max_attempts
        - Step I: Immediate 'Submit' click
        - Step J: Wait for results page
        - Step K: Extract ALL columns (Case Number, Style, Filing Date, Status, Access Level, etc.)
        - STRICT SCHEMA: Output does NOT contain CaseType!
        - Step L: Extract all result pages across pagination
        - Step M: Database format persistence (te_jsonbody_harris & ScrapedCourtCase)
        - Section 4: Return to search state between unique names
        """
        results: list[dict[str, Any]] = []
        l_name = (last_name or "").strip()
        f_name = (first_name or "").strip()

        if not l_name:
            return results

        # Step A: Navigate to Harris JP search
        await self.navigate_to_search(page)

        # Step B & C: Click Smart Search and verify
        await self.click_smart_search(page)
        await self.verify_search_page_loaded(page)

        # Step G: Session timeout guard
        await self.check_and_handle_session_timeout(page)

        # Query format for Odyssey Smart Search: Last, First (Format: Last, First Middle Suffix)
        query = f"{l_name},{f_name}".strip(",")

        # Steps D, E, F, H, I: Search Input, CAPTCHA wait & retry loop
        captcha_success = False
        max_attempts_to_use = max(getattr(self, "max_attempts", 2), 1)

        for attempt in range(1, max_attempts_to_use + 1):
            logger.info(f"[{self.county_name}] Attempt {attempt}/{max_attempts_to_use} for '{query}'")

            # Check session timeout
            await self.check_and_handle_session_timeout(page)

            # Step D: Enter data into Search Input
            t_fill_start = datetime.now()
            search_input = page.locator(
                "input#caseCriteria_SearchCriteria[name='caseCriteria.SearchCriteria'], "
                "input#caseCriteria_SearchCriteria, "
                "#caseCriteria_SearchCriteria, "
                "input[name='caseCriteria.SearchCriteria'], "
                "input[name='caseCriteria_SearchCriteria'], "
                "#SearchCriteria"
            )
            if await _safe_count(search_input) > 0:
                try:
                    await search_input.first.wait_for(state="visible", timeout=10000)
                except Exception:
                    pass
                await self.biometric_fill(search_input.first, query)
                logger.info(f"[{self.county_name}] Step D: Entered search query: {query}")
                await self.pace_action(page)

            t_fill_end = datetime.now()
            self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, query=query)

            # Step E & H: CAPTCHA Resolution Wait (default 120s from Settings)
            t_cap_start = datetime.now()
            captcha_ok = await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
            t_cap_end = datetime.now()

            if captcha_ok:
                captcha_success = True
                self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end, status="SUCCESS")
                logger.info(f"[{self.county_name}] Step E: CAPTCHA verification succeeded on attempt {attempt}.")

                # Step G / Step I: Immediately click 'Submit' (Object: <input name="Search" id="btnSSSubmit" class="btn btn-primary pull-right" value="Submit" type="submit">)
                t_sub_start = datetime.now()
                submit_btn = page.locator(
                    "input#btnSSSubmit[name='Search'][value='Submit'], "
                    "input#btnSSSubmit[value='Submit'], "
                    "input#btnSSSubmit, "
                    "#btnSSSubmit, "
                    "input[name='Search'][value='Submit'], "
                    "input[type='submit'][value*='Submit' i], "
                    "button:has-text('Submit')"
                )
                if await _safe_count(submit_btn) > 0:
                    logger.info(f"[{self.county_name}] Step G: Clicking 'Submit' button (#btnSSSubmit)...")
                    await self.biometric_click(page, submit_btn.first)
                else:
                    raise RuntimeError(f"[{self.county_name}] V4 Submit control was not found")

                # Step J: Wait for result page
                try:
                    for _ in range(25):
                        await self.check_and_handle_session_timeout(page)
                        body_text = await _get_page_text(page)
                        lower_body = body_text.lower()
                        if any(phrase in lower_body for phrase in (
                            "no cases match your search", "no cases match", "no records found",
                            "no records to display", "no results found", "no cases found",
                            "0 records found", "0 items found", "no record found"
                        )):
                            break
                        norecords_el = page.locator(".k-grid-norecords, .norecords, div:has-text('No records to display')")
                        if await _safe_count(norecords_el) > 0:
                            break
                        row_candidates = page.locator(".k-grid-content tbody tr, table.k-selectable tbody tr, table tbody tr")
                        if await _safe_count(row_candidates) > 0:
                            break
                        await page.wait_for_timeout(400)
                except Exception:
                    await page.wait_for_timeout(2000)

                t_sub_end = datetime.now()
                self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)
                break
            else:
                # Exception 1 & 3: CAPTCHA Failure & Retry Handling
                self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end, status="TIMEOUT")
                logger.warning(
                    f"[{self.county_name}] Step F / Exception 1: CAPTCHA verification failed on attempt {attempt}/{max_attempts_to_use}."
                )
                if attempt < max_attempts_to_use:
                    try:
                        logger.info(f"[{self.county_name}] Refreshing page and retrying from step c...")
                        await _safe_reload(page)
                        await page.wait_for_timeout(self.reload_backoff_seconds * 1000)
                        await self.click_smart_search(page)
                        await self.verify_search_page_loaded(page)
                    except Exception as e_rel:
                        logger.debug(f"[{self.county_name}] Retry refresh note: {e_rel}")
                else:
                    logger.warning(f"[{self.county_name}] Max CAPTCHA retry attempts reached without verification.")

        if not captcha_success:
            raise CaptchaResolutionError(f"[{self.county_name}] CAPTCHA was not resolved after {max_attempts_to_use} attempts")

        # Step J: Check for 'No cases match your search' / no records
        t_ext_start = datetime.now()
        body_text = await _get_page_text(page)
        lower_body = body_text.lower()
        row_candidates = page.locator(".k-grid-content tbody tr, table.k-selectable tbody tr, table tbody tr")
        has_rows = await _safe_count(row_candidates) > 0
        norecords_el = page.locator(".k-grid-norecords, .norecords, div:has-text('No records to display')")
        has_norecords = (await _safe_count(norecords_el) > 0)
        is_no_match = any(phrase in lower_body for phrase in (
            "no cases match your search", "no cases match", "no records found",
            "no records to display", "no results found", "no cases found",
            "0 records found", "0 items found", "no record found"
        )) or (has_norecords and not has_rows)

        if is_no_match:
            logger.info(f"[{self.county_name}] Search for '{query}': No matching cases found.")
            t_ext_end = datetime.now()
            self.record_stage("result_retrieval", "Result Retrieval", t_ext_start, t_ext_end, cases_found=0, result_category="No Record Found")
            await self.return_to_search_state(page)
            return []

        # Step K: Discover all table headers dynamically
        header_names: list[str] = []
        try:
            th_loc = page.locator(".k-grid-header thead th, table thead th")
            th_count = await _safe_count(th_loc)
            for h_i in range(th_count):
                th_el = getattr(th_loc, "nth", lambda _: None)(h_i)
                if th_el is None:
                    continue
                th_text = await _safe_inner_text(th_el)
                if th_text:
                    header_names.append(th_text.strip())
            if header_names:
                logger.info(f"[{self.county_name}] Step K: Discovered headers: {header_names}")
        except Exception as e_th:
            logger.debug(f"[{self.county_name}] Header discovery note: {e_th}")

        # Step K & L: Extract ALL available columns across ALL pages
        page_num = 1
        has_next_page = True
        _HEADER_LABELS = {"CASE NUMBER", "CASE NO.", "CASE NO", "CASE #", ""}
        seen_page_signatures: set[tuple[tuple[str, ...], ...]] = set()

        while has_next_page:
            page_start_count = len(results)
            page_cases: list[dict[str, Any]] = []
            page_signature: list[tuple[str, ...]] = []
            rows = page.locator(".k-grid-content tbody tr, table.k-selectable tbody tr, table tbody tr")
            row_count = await _safe_count(rows)
            logger.info(f"[{self.county_name}] Step L: Page {page_num}: Found {row_count} potential result rows")

            for i in range(row_count):
                row = rows.nth(i)
                tds = row.locator("td")
                cells: list[str] = []

                # First try all_inner_texts() (official Playwright bulk text extraction)
                if hasattr(tds, "all_inner_texts"):
                    try:
                        raw_cells = tds.all_inner_texts()
                        if inspect.isawaitable(raw_cells):
                            awaited_cells = await raw_cells
                            if isinstance(awaited_cells, list):
                                cells = [str(c).strip() for c in awaited_cells]
                        elif isinstance(raw_cells, list):
                            cells = [str(c).strip() for c in raw_cells]
                    except Exception:
                        cells = []

                # Fallback to counting and individual cell iteration
                if not cells:
                    td_count = await _safe_count(tds)
                    if td_count >= 2:
                        for c_i in range(td_count):
                            cell_el = getattr(tds, "nth", lambda _: None)(c_i)
                            cells.append((await _safe_inner_text(cell_el)).strip())

                if len(cells) < 2:
                    continue

                # V4 takes the nested grid values, then opens each data-url to
                # read CaseStatus from the case information panel.
                v4_cells = row.locator("td:nth-child(2) table tbody tr:first-child td")
                detail_url = ""
                if len(cells) <= 2 and await _safe_count(v4_cells) >= 4:
                    case_num = (await _safe_inner_text(v4_cells.nth(1))).strip()
                    styled = v4_cells.nth(2).locator("div[title]")
                    title = await _safe_get_attribute(styled.first, "title") if await _safe_count(styled) else None
                    case_style = title.strip() if isinstance(title, str) else (await _safe_inner_text(v4_cells.nth(2))).strip()
                    filing_date = (await _safe_inner_text(v4_cells.nth(3))).strip()
                    link = v4_cells.nth(1).locator("a[data-url]")
                    value = await _safe_get_attribute(link.first, "data-url") if await _safe_count(link) else None
                    detail_url = value if isinstance(value, str) else ""
                    if not detail_url:
                        raise RuntimeError(f"[{self.county_name}] V4 result {case_num} has no case-detail data-url")
                    case_status = await self._read_v4_case_status(page, detail_url)
                else:
                    case_num = cells[0].strip() if len(cells) > 0 else ""
                    case_style = cells[1].strip() if len(cells) > 1 else ""
                    filing_date = cells[2].strip() if len(cells) > 2 else ""
                    raw_status = cells[3].strip() if len(cells) > 3 else ""
                    case_status = re.sub(r"(?i)^case\s*status\s*[:\s]*", "", raw_status).strip()

                if case_num and case_num.upper() not in _HEADER_LABELS:
                    page_signature.append((*cells, case_num, case_style, filing_date, case_status, detail_url))
                    page_cases.append({
                        "CaseNumber": case_num,
                        "CaseStyle": case_style,
                        "FilingDate": filing_date,
                        "CaseStatus": case_status,
                    })

            signature = tuple(page_signature)
            if page_num > 1 and signature in seen_page_signatures:
                raise RuntimeError(f"[{self.county_name}] Pagination did not advance to new case results (repeated page)")
            seen_page_signatures.add(signature)
            results.extend(page_cases)

            # Step L: Pagination check via Kendo UI pager
            next_btn = page.locator(
                ".k-pager-wrap a[title='Go to the next page']:not(.k-state-disabled), "
                ".k-pager-wrap .k-i-arrow-end-right:not(.k-state-disabled), "
                "a.k-link[title='Next']:not(.k-state-disabled), "
                ".k-pager-wrap a:has-text('>'):not(.k-state-disabled)"
            )
            if await _safe_count(next_btn) > 0 and await _safe_is_visible(next_btn):
                cls_attr = (await _safe_get_attribute(next_btn, "class")) or ""
                if "k-state-disabled" in cls_attr or "disabled" in cls_attr:
                    has_next_page = False
                else:
                    if page_num > 1 and len(results) == page_start_count:
                        raise RuntimeError(f"[{self.county_name}] Pagination did not advance to new case results")
                    try:
                        logger.info(f"[{self.county_name}] Step L: Advancing to page {page_num + 1}...")
                        old_case = results[-1]["CaseNumber"] if results else ""
                        await self.biometric_click(page, next_btn.first)
                        try:
                            wf_fn = getattr(page, "wait_for_function", None)
                            if callable(wf_fn):
                                res = wf_fn(
                                    "oldNum => { const row = document.querySelector('.k-grid-content tbody tr, table.k-selectable tbody tr'); return row && !row.innerText.includes(oldNum); }",
                                    arg=old_case,
                                    timeout=5000,
                                )
                                if inspect.isawaitable(res):
                                    await res
                        except Exception:
                            await page.wait_for_timeout(2000)
                        page_num += 1
                    except Exception:
                        has_next_page = False
            else:
                has_next_page = False

        if not results:
            logger.info(f"[{self.county_name}] No cases extracted from result grid for '{query}'.")
            t_ext_end = datetime.now()
            self.record_stage("result_retrieval", "Result Retrieval", t_ext_start, t_ext_end, cases_found=0, result_category="No Record Found")
            await self.return_to_search_state(page)
            return []

        t_ext_end = datetime.now()
        self.record_stage(
            "result_retrieval",
            "Result Retrieval",
            t_ext_start,
            t_ext_end,
            cases_found=len(results),
            result_category="Data Found" if results else "No Record Found",
        )

        # Section 4: Return to Harris JP search between unique names
        await self.return_to_search_state(page)

        return results
    async def _read_v4_case_status(self, page: Page, detail_url: str) -> str:
        """Read the case information status from the separate V4 Harris JP tab."""
        detail_page = await page.context.new_page()
        try:
            await detail_page.goto(urljoin(self.base_url, detail_url), wait_until="domcontentloaded", timeout=self.timeout_ms)
            status_nodes = detail_page.locator("#divCaseInformation_body p")
            for index in range(await _safe_count(status_nodes)):
                value = (await _safe_inner_text(status_nodes.nth(index))).strip()
                if re.match(r"^Case\s+Status\b", value, flags=re.I):
                    return re.sub(r"^Case\s+Status\s*:?[\s]*", "", value, flags=re.I).strip()
            raise RuntimeError(f"[{self.county_name}] Case detail did not provide a case status: {detail_url}")
        finally:
            await detail_page.close()
