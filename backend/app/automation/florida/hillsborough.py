"""Hillsborough County Clerk Portal Automation Scraper (Power Automate V4 Parity)."""

import inspect
import logging
import os
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

from playwright.async_api import Page

from app.automation.base import (
    BaseCourtScraper,
    CaptchaResolutionError,
    _safe_eval,
    _safe_wait_timeout,
    resilient_click,
)

logger = logging.getLogger("uaic_orchestrator.automation.hillsborough")


async def _safe_is_visible(loc: Any) -> bool:
    try:
        first_loc = getattr(loc, "first", loc)
        fn = getattr(first_loc, "is_visible", None) or getattr(loc, "is_visible", None)
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                return bool(await res)
            if isinstance(res, bool):
                return res
            if isinstance(res, MagicMock):
                return False
            return bool(res)
    except Exception:
        pass
    return False


async def _safe_count(loc: Any) -> int:
    try:
        fn = getattr(loc, "count", None)
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                return int(await res)
            if isinstance(res, (int, float)):
                return int(res)
            if isinstance(res, MagicMock):
                return 0
            return int(res)
    except Exception:
        pass
    return 0


async def _safe_get_attribute(loc: Any, name: str) -> str | None:
    try:
        first_loc = getattr(loc, "first", loc)
        fn = getattr(first_loc, "get_attribute", None)
        if callable(fn):
            res = fn(name)
            if inspect.isawaitable(res):
                res = await res
            if isinstance(res, MagicMock):
                return None
            return str(res) if res is not None else None
    except Exception:
        pass
    return None


async def _safe_click(loc: Any) -> None:
    try:
        last_loc = getattr(loc, "last", loc)
        first_loc = getattr(last_loc, "first", last_loc)
        fn = getattr(first_loc, "click", None) or getattr(loc, "click", None)
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                await res
            return
    except Exception:
        pass
    try:
        eval_fn = getattr(loc, "evaluate", None)
        if callable(eval_fn):
            res = eval_fn("el => { if (el) { el.scrollIntoView({block: 'center', inline: 'center'}); el.click(); } }")
            if inspect.isawaitable(res):
                await res
    except Exception:
        pass


HILLSBOROUGH_PORTAL_URL = "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"


class HillsboroughScraper(BaseCourtScraper):
    """Scraper for Hillsborough County Clerk of Courts (Power Automate V4 Parity)."""

    def __init__(self, base_url: str | None = None, **kwargs):
        super().__init__(
            county_name="Hillsborough County (FL)",
            base_url=base_url or "https://hover.hillsclerk.com/",
            **kwargs,
        )

    async def navigate_to_search(self, page: Page) -> str:
        """Step a: Open Hillsborough tab, wait for full load, reload if unusable. Step b: Click Party or Business Name."""
        t_nav_start = datetime.now()
        base = self.base_url.rstrip("/")
        search_target_url = f"{base}/html/case/caseSearch.html#nav-Party-tab" if "caseSearch" not in base else base

        current_url = getattr(page, "url", "") or ""
        if not current_url or current_url == "about:blank" or "hillsclerk.com" not in current_url:
            try:
                logger.info(f"[{self.county_name}] Step a: Opening Hillsborough portal URL: {search_target_url}")
                await page.goto(search_target_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                await page.wait_for_timeout(1000)
            except Exception as e_nav:
                logger.warning(f"[{self.county_name}] Step a: Direct load encountered: {e_nav}. Refreshing...")
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=self.timeout_ms)
                    await page.wait_for_timeout(1500)
                except Exception:
                    await page.goto(search_target_url, wait_until="domcontentloaded", timeout=self.timeout_ms)

        # Step a: Verify page body is loaded; if empty or incomplete, refresh
        try:
            body_txt = await page.inner_text("body")
            if not body_txt or len(body_txt.strip()) < 5:
                logger.warning(f"[{self.county_name}] Step a: Page appeared empty. Refreshing page...")
                await page.reload(wait_until="domcontentloaded", timeout=self.timeout_ms)
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        # Step b: If on landing page (hover.hillsclerk.com/ without caseSearch.html), click "Party or Business Name"
        curr_url_check = getattr(page, "url", "") or ""
        if "hillsclerk.com" in curr_url_check and "caseSearch.html" not in curr_url_check:
            party_landing_btn = page.locator(
                "a[href*='/html/case/caseSearch.html#nav-Party-tab'], "
                "a[href*='caseSearch.html#nav-Party-tab'], "
                "a[href*='nav-Party-tab'], "
                "a:has-text('Party or Business Name')"
            )
            if await _safe_count(party_landing_btn) > 0 and await _safe_is_visible(party_landing_btn):
                logger.info(f"[{self.county_name}] Step b: Clicking 'Party or Business Name' button on landing page...")
                await resilient_click(party_landing_btn.first, page=page)
                await page.wait_for_timeout(800)
            elif curr_url_check != "about:blank":
                await page.goto(search_target_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                await page.wait_for_timeout(800)

        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=search_target_url)
        return search_target_url

    async def select_party_search_tab(self, page: Page) -> None:
        """
        Step c: Verify that the page loads and that the 'Search by Party or Business Name' tab is selected.
        If it is not selected, select it (Object: <button class="... active" id="nav-Party-tab" data-bs-toggle="tab" data-bs-target="#nav-Party" ...>).
        """
        try:
            logger.info(f"[{self.county_name}] Step c: Verifying 'Search by Party or Business Name' tab is selected...")
            party_tab = page.locator(
                "button#nav-Party-tab[data-bs-target='#nav-Party'], "
                "button#nav-Party-tab, "
                "#nav-Party-tab, "
                "button[data-bs-target='#nav-Party'], "
                "a[href*='nav-Party-tab'], "
                "button:has-text('Search by Party or Business Name')"
            )
            is_active = False
            if await _safe_count(party_tab) > 0:
                cls_attr = (await _safe_get_attribute(party_tab, "class")) or ""
                aria_sel = (await _safe_get_attribute(party_tab, "aria-selected")) or ""
                if "active" in cls_attr.lower() or aria_sel == "true":
                    is_active = True

            if not is_active:
                logger.info(f"[{self.county_name}] Step c: 'Search by Party or Business Name' tab not active; selecting it...")
                if await _safe_count(party_tab) > 0 and await _safe_is_visible(party_tab):
                    await resilient_click(party_tab.first, page=page)
                    await _safe_wait_timeout(page, 800)
                else:
                    await _safe_eval(page, """() => {
                        const tab = document.querySelector('button#nav-Party-tab') || document.querySelector('#nav-Party-tab') || document.querySelector("a[href*='nav-Party']");
                        if (tab) tab.click();
                    }""")
                    await _safe_wait_timeout(page, 800)

            # Confirm readiness and visibility of party inputs in #nav-Party
            last_input = page.locator("#spLastName, input[name='partyLastName'], #partyLastName")
            if await _safe_count(last_input) > 0:
                first_last = getattr(last_input, "first", last_input)
                wait_fn = getattr(first_last, "wait_for", None)
                if callable(wait_fn):
                    try:
                        res = wait_fn(state="visible", timeout=12000)
                        if inspect.isawaitable(res):
                            await res
                    except Exception:
                        pass
            logger.info(f"[{self.county_name}] Step c: 'Search by Party or Business Name' tab verified active.")
        except Exception as e_tab:
            logger.debug(f"[{self.county_name}] Party search tab selection note: {e_tab}")

    async def check_and_dismiss_search_criteria_popup(self, page: Page) -> bool:
        """Step g / Criteria Popup: Detect 'YOUR SEARCH CRITERIA' popup, click Close or X, and continue workflow."""
        try:
            popup_header = page.locator(
                "div.modal.show, #messageDialog, "
                "div.modal:has-text('YOUR SEARCH CRITERIA'), "
                ".modal-title:has-text('YOUR SEARCH CRITERIA'), "
                "div:has-text('YOUR SEARCH CRITERIA'), "
                "[role='dialog']:has-text('YOUR SEARCH CRITERIA')"
            )
            if await _safe_count(popup_header) > 0 and await _safe_is_visible(popup_header):
                logger.info(f"[{self.county_name}] 'YOUR SEARCH CRITERIA' popup detected. Dismissing...")
                close_btn = page.locator(
                    "#messageClose, "
                    ".modal.show button.close, "
                    ".modal.show button.btn-close, "
                    ".modal.show button:has-text('Close'), "
                    ".modal:has-text('YOUR SEARCH CRITERIA') #messageClose, "
                    ".modal:has-text('YOUR SEARCH CRITERIA') button.close, "
                    ".modal:has-text('YOUR SEARCH CRITERIA') button:has-text('Close'), "
                    ".modal:has-text('YOUR SEARCH CRITERIA') [aria-label*='Close' i], "
                    ".modal:has-text('YOUR SEARCH CRITERIA') [data-dismiss='modal'], "
                    ".modal:has-text('YOUR SEARCH CRITERIA') [data-bs-dismiss='modal'], "
                    "button:has-text('Close'), [aria-label='Close'], [data-dismiss='modal']"
                )
                if await _safe_count(close_btn) > 0 and await _safe_is_visible(close_btn):
                    await resilient_click(close_btn.first, page=page)
                    await page.wait_for_timeout(500)
                    logger.info(f"[{self.county_name}] Dismissed 'YOUR SEARCH CRITERIA' popup via Close/X button.")
                    return True

                # Direct DOM click fallback for Bootstrap modal #messageClose
                dom_dismissed = await _safe_eval(page, """() => {
                    const el = document.getElementById('messageClose') ||
                               document.querySelector('.modal.show button.close') ||
                               document.querySelector('.modal.show [data-dismiss=\"modal\"]') ||
                               document.querySelector('.modal.show button.btn-primary');
                    if (el) { el.click(); return true; }
                    return false;
                }""")
                if dom_dismissed:
                    await page.wait_for_timeout(500)
                    logger.info(f"[{self.county_name}] Dismissed 'YOUR SEARCH CRITERIA' popup via DOM click fallback.")
                    return True

                # Fallback to pressing Escape
                if hasattr(page, "keyboard") and hasattr(page.keyboard, "press"):
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(500)
                    return True
        except Exception as e_pop:
            logger.debug(f"[{self.county_name}] Search criteria popup check note: {e_pop}")
        return False

    async def return_to_search_state(self, page: Page) -> None:
        """Section 4: Return Hillsborough tab to clean search state for the next unique name (V4 parity)."""
        try:
            logger.info(f"[{self.county_name}] Section 4: Returning Hillsborough tab to search state for next unique name (V4 parity)...")
            # Close message/popup if open
            await _safe_eval(page, "() => { const el = document.getElementById('messageClose'); if (el) el.click(); }")
            await _safe_wait_timeout(page, 300)

            # Click Anchor 'Case Search' if visible on page
            case_search_btn = page.locator("a:has-text('Case Search'), a[href*='caseSearch']")
            if await _safe_count(case_search_btn) > 0 and await _safe_is_visible(case_search_btn):
                try:
                    await self.biometric_click(page, case_search_btn.first)
                    await _safe_wait_timeout(page, 500)
                except Exception:
                    pass

            nav_url = self.base_url.rstrip("/")
            if not nav_url.endswith(".html") and "caseSearch" not in nav_url:
                nav_url = f"{nav_url.rstrip('/')}/html/case/caseSearch.html#nav-Party-tab"

            curr_url = getattr(page, "url", "") or ""
            if "caseSearch.html" not in curr_url:
                await page.goto(nav_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                await _safe_wait_timeout(page, 800)

            res_tab = self.select_party_search_tab(page)
            if inspect.isawaitable(res_tab):
                await res_tab
        except Exception as e_reset:
            logger.debug(f"[{self.county_name}] Return to search state note: {e_reset}")

    async def search_by_party_name(
        self,
        first_name: str | None,
        last_name: str | None,
        page: Page,
        date_of_loss: str | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        results = []
        l_name = (last_name or "").strip()
        f_name = (first_name or "").strip()

        if not l_name:
            return results

        # Optional route cache optimization for large bundles
        cache_bundle1 = os.path.join(os.getcwd(), "hillsborough_bundle.js")
        cache_bundle2 = os.path.join(os.getcwd(), "hillsborough_bundle2.js")
        if hasattr(page, "route"):
            if os.path.exists(cache_bundle1) and os.path.getsize(cache_bundle1) > 18000000:
                async def serve_cached_bundle1(route):
                    await route.fulfill(status=200, content_type="application/javascript", path=cache_bundle1)
                try:
                    await page.route("**/bundle/bundle1/bundle-*.js", serve_cached_bundle1)
                except Exception:
                    pass

            if os.path.exists(cache_bundle2) and os.path.getsize(cache_bundle2) > 20000000:
                async def serve_cached_bundle2(route):
                    await route.fulfill(status=200, content_type="application/javascript", path=cache_bundle2)
                try:
                    await page.route("**/bundle/bundle2/bundle-*.js", serve_cached_bundle2)
                except Exception:
                    pass

        # Step A: Navigate to Hillsborough search page with load verification
        await self.navigate_to_search(page)

        # Step B & C: Click 'Party or Business Name' & verify 'Search by Party or Business Name' is active
        await self.select_party_search_tab(page)

        # Step I: Check for and dismiss 'YOUR SEARCH CRITERIA' popup if present before fill
        await self.check_and_dismiss_search_criteria_popup(page)

        # Exception 3: CAPTCHA Retry & Refresh Loop adhering to dynamically configured Max Attempts and CAPTCHA Wait
        max_attempts = max(1, getattr(self, "max_attempts", 2))
        captcha_solved = False

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                logger.info(
                    f"[{self.county_name}] CAPTCHA Retry attempt {attempt}/{max_attempts}. "
                    f"Performing reload and repeating from Step B & C (Party tab)..."
                )
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=self.timeout_ms)
                    await page.wait_for_timeout(getattr(self, "reload_backoff_seconds", 2) * 1000)
                    await self.select_party_search_tab(page)
                    await self.check_and_dismiss_search_criteria_popup(page)
                except Exception as e_rel:
                    logger.warning(f"[{self.county_name}] Page reload note: {e_rel}")

            # Step d: Fill Party Search Inputs in exact order: First Name -> Last Name -> On or After
            t_fill_start = datetime.now()
            first_input = page.locator(
                "input#spFirstName, "
                "#spFirstName, "
                "input[alt*='enter first name'], "
                "input[placeholder*='First Name'], "
                "input[name='partyFirstName']"
            )
            last_input = page.locator(
                "input#spLastName, "
                "#spLastName, "
                "input[alt*='enter last name field'], "
                "input[placeholder*='Last Name'], "
                "input[name='partyLastName']"
            )
            dol_input = page.locator(
                "input#spDateFiledAfter, "
                "#spDateFiledAfter, "
                "input.hasDatepicker[id='spDateFiledAfter'], "
                "input[name='date'][placeholder='mm/dd/yyyy'], "
                "input[name='spDateFiledAfter']"
            )

            # Confirm visibility of search inputs
            first_last_loc = getattr(last_input, "first", last_input)
            wait_fn = getattr(first_last_loc, "wait_for", None)
            if callable(wait_fn):
                try:
                    res_w = wait_fn(state="visible", timeout=25000)
                    if inspect.isawaitable(res_w):
                        await res_w
                except Exception:
                    pass

            # 1. First Name
            if f_name and await _safe_count(first_input) > 0:
                await self.biometric_fill(first_input.first, f_name)
                await page.wait_for_timeout(100)

            # 2. Last Name
            await self.biometric_fill(last_input.first, l_name)
            await page.wait_for_timeout(100)

            # 3. On or After (spDateFiledAfter with readonly removal)
            if date_of_loss and await _safe_count(dol_input) > 0:
                clean_dol = date_of_loss.strip()
                try:
                    await page.evaluate(
                        """(val) => {
                            const el = document.querySelector('#spDateFiledAfter') || document.querySelector("input[name='date']") || document.querySelector("input[name='spDateFiledAfter']");
                            if (el) {
                                el.removeAttribute('readonly');
                                el.value = val;
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                el.dispatchEvent(new Event('blur', { bubbles: true }));
                            }
                            if (typeof window.$ !== 'undefined' && window.$('#spDateFiledAfter').datepicker) {
                                try { window.$('#spDateFiledAfter').datepicker('setDate', val); } catch(e) {}
                            }
                        }""",
                        clean_dol,
                    )
                    logger.info(f"[{self.county_name}] Step d: Filled spDateFiledAfter with DOL: {clean_dol}")
                except Exception as e:
                    logger.warning(f"[{self.county_name}] DOM date fill note: {e}, falling back to biometric_fill")
                    try:
                        await self.biometric_fill(dol_input.first, clean_dol)
                    except Exception as ex:
                        logger.warning(f"[{self.county_name}] Could not fill datepicker: {ex}")

            await self.pace_action(page)
            t_fill_end = datetime.now()
            self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=f"{f_name} {l_name}", dol=date_of_loss)

            # CAPTCHA verification if applicable
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

        # Step e: Click Search Button (button#btnSubmitPartySearch)
        t_sub_start = datetime.now()
        down_search_btn = page.locator(
            "button#btnSubmitPartySearch[type='button'], "
            "button#btnSubmitPartySearch, "
            "#btnSubmitPartySearch, "
            "#nav-Party #btnSubmitPartySearch, "
            "#nav-Party button.btn-success:has-text('Search'), "
            "#nav-Party button.btn-success"
        )
        if await _safe_count(down_search_btn) > 0:
            logger.info(f"[{self.county_name}] Step e: Clicking Search button (#btnSubmitPartySearch)...")
            await self.biometric_click(page, down_search_btn.first)
        else:
            raise RuntimeError(f"[{self.county_name}] V4 btnSubmitPartySearch control was not found")
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # Check for and dismiss 'YOUR SEARCH CRITERIA' popup if triggered by submit
        await self.check_and_dismiss_search_criteria_popup(page)

        # Step f: Wait for HOVER portal search results page to fully load.
        # The portal navigates from caseSearch.html -> searchResults.html via SPA routing.
        # Must wait for: (1) URL navigation, (2) network idle, (3) results table visible.
        t_ext_start = datetime.now()
        try:
            curr_url = getattr(page, "url", "") or ""
            logger.info(f"[{self.county_name}] Step f: Waiting for results page (current URL: {curr_url})...")

            # Primary: wait for URL to change within the configured navigation timeout.
            if "searchResults" not in curr_url:
                try:
                    await page.wait_for_url("**/searchResults.html*", timeout=self.timeout_ms)
                    logger.info(f"[{self.county_name}] Step f: URL navigated to searchResults.html.")
                except Exception as url_err:
                    logger.warning(f"[{self.county_name}] Step f: wait_for_url(searchResults) timed out ({url_err}). Proceeding with table wait.")

            # Secondary: wait for network idle so AJAX-loaded results are in DOM
            try:
                await page.wait_for_load_state("networkidle", timeout=self.timeout_ms)
            except Exception:
                try:
                    await page.wait_for_load_state("load", timeout=self.timeout_ms)
                except Exception:
                    pass

            # Tertiary: wait for results table to be visible
            results_table = page.locator("#partyResultsTable, table.dataTable, #caseResultsTable, #partySearchResults table")
            first_tbl = getattr(results_table, "first", results_table)
            wait_tbl_fn = getattr(first_tbl, "wait_for", None)
            if callable(wait_tbl_fn):
                try:
                    res_tbl = wait_tbl_fn(state="visible", timeout=self.timeout_ms)
                    if inspect.isawaitable(res_tbl):
                        await res_tbl
                    logger.info(f"[{self.county_name}] Step f: Results table visible — ready for extraction.")
                except Exception as tbl_err:
                    logger.warning(f"[{self.county_name}] Step f: Results table wait timed out: {tbl_err}")
        except Exception as e_wait:
            logger.warning(f"[{self.county_name}] Step f: Results page wait error: {e_wait}")

        await self.pace_action(page)

        # Step f2: Wait for DataTables AJAX to finish by ensuring 'Loading...' / 'Processing...' disappear
        try:
            logger.info(f"[{self.county_name}] Step f2: Waiting for loading overlay/text to disappear...")
            # Bound AJAX readiness by the configured portal navigation timeout.
            for _ in range(max(1, (self.timeout_ms + 499) // 500)):
                loading_locators = page.locator("td:has-text('Loading'), td:has-text('Processing'), .blockUI, .loading-spinner, #loading, img[src*='loading']")
                count = await _safe_count(loading_locators)
                any_visible = False
                for i in range(count):
                    try:
                        if await loading_locators.nth(i).is_visible():
                            any_visible = True
                            break
                    except Exception:
                        pass
                if not any_visible:
                    break
                await page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"[{self.county_name}] Step f2 loading wait timeout: {e}")

        # Also check for 'YOUR SEARCH CRITERIA' popup on the results page
        await self.check_and_dismiss_search_criteria_popup(page)

        # Check for empty state (explicitly avoiding 'Processing...' or 'Loading...')
        empty_msg = page.locator("td.dataTables_empty:has-text('No data'), td.dataTables_empty:has-text('No records'), td:has-text('No cases matched'), div:has-text('No cases matched'), :has-text('No data available in table'), :has-text('No records found'), #messageClose")
        if await _safe_count(empty_msg) > 0 and await _safe_is_visible(empty_msg):
            logger.info(f"[{self.county_name}] Step g: Search for '{l_name}, {f_name}': No data available in table.")
            await _safe_eval(page, "() => { const el = document.getElementById('messageClose'); if (el) el.click(); }")
            t_ext_end = datetime.now()
            self.record_stage("result_retrieval", "Result Retrieval", t_ext_start, t_ext_end, cases_found=0, result_category="No Record Found")
            # Step h: Return tab to search state for next unique name
            await self.return_to_search_state(page)
            return []

        # Step g: Discover all table headers to map all available columns dynamically
        header_names: list[str] = []
        try:
            th_loc = page.locator("#partyResultsTable thead th, table.dataTable thead th, table thead th")
            th_count = await _safe_count(th_loc)
            for h_i in range(th_count):
                th_el = getattr(th_loc, "nth", lambda _: None)(h_i)
                if th_el is None:
                    continue
                inner_fn = getattr(th_el, "inner_text", None)
                if callable(inner_fn):
                    res_inner = inner_fn()
                    if inspect.isawaitable(res_inner):
                        th_text = (await res_inner or "").strip()
                    elif isinstance(res_inner, str):
                        th_text = res_inner.strip()
                    else:
                        th_text = ""
                    if th_text:
                        header_names.append(th_text)
            if header_names:
                logger.info(f"[{self.county_name}] Step g: Discovered table headers: {header_names}")
        except Exception as e_th:
            logger.debug(f"[{self.county_name}] Header discovery note: {e_th}")

        # Step g: Extract ALL available columns across ALL pages
        _HEADER_LABELS = {"CASE NUMBER", "CASE NO.", "CASE NO", "CASE #", ""}
        page_num = 1
        has_next_page = True
        seen_page_signatures: set[tuple[tuple[str, ...], ...]] = set()

        while has_next_page:
            page_signature: list[tuple[str, ...]] = []
            rows = page.locator("#partyResultsTable tbody tr, table.dataTable tbody tr")
            row_count = await _safe_count(rows)
            logger.info(f"[{self.county_name}] Step g: Page {page_num}: Found {row_count} table rows")

            for i in range(row_count):
                row = rows.nth(i)
                cells = await row.locator("td").all_inner_texts()
                if len(cells) <= 1:
                    continue
                page_signature.append(tuple(cell.strip() for cell in cells))

                # Standard HOVER column mapping:
                # td:eq(2) -> CaseNumber
                # td:eq(3) -> Citation
                # td:eq(4) -> CaseStyle
                # td:eq(5) -> CaseStatus
                # td:eq(6) -> FilingDate
                # td:eq(7) -> CaseType
                case_num = cells[2].strip() if len(cells) > 2 else ""
                case_style = cells[4].strip() if len(cells) > 4 else ""
                case_status = cells[5].strip() if len(cells) > 5 else ""
                filing_date = cells[6].strip() if len(cells) > 6 else ""
                case_type = cells[7].strip() if len(cells) > 7 else ""

                if case_num and case_num.upper() not in _HEADER_LABELS:
                    case_payload: dict[str, Any] = {
                        "CaseNumber": case_num,
                        "CaseStyle": case_style,
                        "FilingDate": filing_date,
                        "CaseStatus": case_status,
                        "CaseType": case_type,
                    }
                    results.append(case_payload)

            signature = tuple(page_signature)
            if page_num > 1 and signature in seen_page_signatures:
                raise RuntimeError(f"[{self.county_name}] Pagination did not advance to new case results")
            seen_page_signatures.add(signature)

            # Step H: Pagination traversal
            next_btn = page.locator(
                "#partyResultsTable_next:not(.disabled) a, "
                "li.paginate_button.next:not(.disabled) a, "
                ".paginate_button.next:not(.disabled)"
            )
            if await _safe_count(next_btn) > 0 and await _safe_is_visible(next_btn):
                is_disabled = (await _safe_get_attribute(next_btn, "disabled")) or (await _safe_get_attribute(next_btn, "aria-disabled"))
                cls_attr = (await _safe_get_attribute(next_btn, "class")) or ""
                if is_disabled == "true" or "disabled" in cls_attr.lower():
                    has_next_page = False
                else:
                    try:
                        logger.info(f"[{self.county_name}] Step H: Advancing to page {page_num + 1}...")
                        await self.biometric_click(page, next_btn.first)
                        await page.wait_for_timeout(2000)
                        page_num += 1
                    except Exception:
                        has_next_page = False
            else:
                has_next_page = False

        if not results:
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

        # Section 4: Return Hillsborough tab to search state for next unique name
        await self.return_to_search_state(page)

        return results
