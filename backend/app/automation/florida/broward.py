import inspect
import logging
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

from playwright.async_api import Page

from app.automation.base import (
    BaseCourtScraper,
    CaptchaResolutionError,
    _safe_eval,
    resilient_click,
)

logger = logging.getLogger("uaic_orchestrator.automation.broward")


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


async def _safe_inner_text(loc: Any) -> str:
    try:
        first_loc = getattr(loc, "first", loc)
        fn = getattr(first_loc, "inner_text", None)
        if callable(fn):
            res = fn()
            if inspect.isawaitable(res):
                res = await res
            if isinstance(res, MagicMock):
                return ""
            return str(res) if res is not None else ""
    except Exception:
        pass
    return ""


def _normalize_date_to_mm_dd_yyyy(raw_date: str) -> str:
    """Normalize dates in any common format (M/D/YYYY, MM/DD/YYYY, YYYY-MM-DD) to strict MM/DD/YYYY required by Broward FormValidation."""
    clean = (raw_date or "").strip()
    if not clean:
        return clean
    if "/" in clean:
        parts = clean.split("/")
        if len(parts) == 3:
            try:
                m = int(parts[0])
                d = int(parts[1])
                y = int(parts[2])
                return f"{m:02d}/{d:02d}/{y:04d}"
            except Exception:
                pass
    elif "-" in clean:
        parts = clean.split("-")
        if len(parts) == 3:
            try:
                if len(parts[0]) == 4:
                    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"{m:02d}/{d:02d}/{y:04d}"
                else:
                    m, d, y = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"{m:02d}/{d:02d}/{y:04d}"
            except Exception:
                pass
    return clean


BROWARD_PORTAL_URL = "https://www.browardclerk.org/Web2"


class BrowardScraper(BaseCourtScraper):
    """Scraper for Broward County Clerk of Courts (100% Power Automate V4 Parity)."""

    def __init__(self, base_url: str | None = None, **kwargs):
        super().__init__(
            county_name="Broward County (FL)",
            base_url=base_url or BROWARD_PORTAL_URL,
            **kwargs,
        )
        if not self.base_url or self.base_url.rstrip("/") == "https://www.browardclerk.org":
            self.base_url = BROWARD_PORTAL_URL

    async def navigate_to_search(self, page: Page) -> str:
        """
        Step A: Open Broward portal URL (https://www.browardclerk.org/Web2).
        V4 Parity: https://www.browardclerk.org/Web2 IS the Case Search page.
        NEVER click header navigation links or loose 'Case Search' buttons which veer into Premium Services or Glossary.
        """
        t_nav_start = datetime.now()
        current_url = getattr(page, "url", "") or ""

        search_url = self.base_url.rstrip("/")
        if not search_url.endswith("/Web2") and "/CaseSearch" not in search_url:
            search_url = f"{search_url}/Web2"

        # Direct navigation to portal URL if not already on the portal
        if not current_url or current_url == "about:blank" or search_url not in current_url:
            logger.info(f"[{self.county_name}] Step A: Opening Broward portal URL: {search_url}")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
            await page.wait_for_timeout(1000)

        # Step A verification: Verify page loaded; reload if empty
        try:
            body_txt = await page.inner_text("body")
            if not body_txt or len(body_txt.strip()) < 5:
                logger.warning(f"[{self.county_name}] Step A: Page appeared empty. Refreshing...")
                await page.reload(wait_until="domcontentloaded", timeout=self.timeout_ms)
                await page.wait_for_timeout(1000)
        except Exception as e_load:
            logger.debug(f"[{self.county_name}] Step A page load check note: {e_load}")

        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=search_url)
        return search_url

    async def select_party_name_tab(self, page: Page) -> None:
        """Step C: Verify Party Name tab is active; select if not (V4: Anchor 'Party Name' -> #myTabStandard a[href="#nameSearch"])."""
        try:
            # Check if Party Name tab pane is active
            is_active = await page.evaluate('''() => {
                const pane = document.querySelector('#nameSearch, div#nameSearch');
                if (!pane) return false;
                const cls = (pane.className || '').toLowerCase();
                return cls.includes('active') || cls.includes('in') || pane.offsetParent !== null;
            }''')

            if not is_active:
                logger.info(f"[{self.county_name}] Step C: Party Name tab not active. Selecting tab...")
                # V4 Exact Object: Anchor 'Party Name' in ControlRepository: a[href="#nameSearch"] under #myTabStandard
                tab_link = page.locator("#myTabStandard a[href='#nameSearch'], a[href='#nameSearch']")
                if await _safe_count(tab_link) > 0:
                    await resilient_click(tab_link, page=page, timeout_ms=3000)
                    await page.wait_for_timeout(500)
            else:
                logger.info(f"[{self.county_name}] Step C: Party Name tab is verified active.")
        except Exception as e_tab:
            logger.debug(f"[{self.county_name}] Party Name tab verification note: {e_tab}")

    async def fill_search_fields(
        self,
        page: Page,
        l_name: str,
        f_name: str | None,
        date_of_loss: str | None = None,
    ) -> None:
        """Step D: Enter Search Data (Last Name, First Name, Date From) using exact object selectors."""
        t_fill_start = datetime.now()
        last_input = page.locator("input#lastName, input[name='lastName'], input[data-fv-field='lastName'], input[name*='LastName']")
        first_input = page.locator("input#firstName, input[name='firstName'], input[data-fv-field='firstName'], input[name*='FirstName']")
        dol_input = page.locator("input#filingDateOnOrAfterP, input[name='filingDateOnOrAfterP'], input[data-fv-field='filingDateOnOrAfterP']")

        if await _safe_count(last_input) > 0:
            try:
                wait_fn = getattr(last_input.first, "wait_for", None)
                if callable(wait_fn):
                    res_w = wait_fn(state="visible", timeout=15000)
                    if inspect.isawaitable(res_w):
                        await res_w
            except Exception:
                pass
            await self.biometric_fill(last_input.first, l_name)

        if f_name and await _safe_count(first_input) > 0:
            await self.biometric_fill(first_input.first, f_name)

        formatted_dol = ""
        if date_of_loss and await _safe_count(dol_input) > 0:
            formatted_dol = _normalize_date_to_mm_dd_yyyy(date_of_loss)
            await self.biometric_fill(dol_input.first, formatted_dol)
            logger.info(f"[{self.county_name}] Step D: Filled filingDateOnOrAfterP with DOL: {formatted_dol}")

        # Ensure KendoDatePicker internal widget and FormValidation are synchronized
        escaped_dol = formatted_dol.replace("'", "\\'")
        await _safe_eval(page, f"""() => {{
            const dol = '{escaped_dol}';
            if (dol) {{
                const el = document.getElementById('filingDateOnOrAfterP') || document.querySelector('input[name="filingDateOnOrAfterP"]');
                if (el) {{
                    el.value = dol;
                    if (window.$ && $(el).data('kendoDatePicker')) {{
                        try {{
                            const kw = $(el).data('kendoDatePicker');
                            kw.value(dol);
                            kw.trigger('change');
                        }} catch(e) {{}}
                    }}
                }}
            }}
            if (window.$ && $('#personSearchForm').data('formValidation')) {{
                try {{
                    const fv = $('#personSearchForm').data('formValidation');
                    fv.revalidateField('lastName');
                    fv.revalidateField('firstName');
                    if (dol) fv.revalidateField('filingDateOnOrAfterP');
                }} catch(e) {{}}
            }}
        }}""")

        await page.wait_for_timeout(500)
        t_fill_end = datetime.now()
        self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=f"{f_name} {l_name}", dol=date_of_loss)

    async def check_and_handle_session_timeout(
        self,
        page: Page,
        l_name: str,
        f_name: str | None,
        date_of_loss: str | None,
    ) -> bool:
        """Exception 2: Check for 'Session timeout warning' or home page redirect, click 'Continue session', or restart from Step B."""
        try:
            # Check if session expired and automatically navigated to homepage
            curr_url = getattr(page, "url", "") or ""
            if curr_url and curr_url != "about:blank" and "/CaseSearchECA" not in curr_url and "/Web2" not in curr_url:
                logger.info(f"[{self.county_name}] Exception 2: Session timeout redirected to home page ({curr_url}). Restarting from Step B (Case Search)...")
                await self.navigate_to_search(page)
                await self.select_party_name_tab(page)
                await self.fill_search_fields(page, l_name, f_name, date_of_loss)
                return True

            timeout_btn = page.locator(
                "button:has-text('Continue session'), a:has-text('Continue session'), "
                "button:has-text('Continue Session'), button:has-text('Continue'), "
                "input[value*='Continue' i], [aria-label*='Continue' i]"
            )
            if await _safe_count(timeout_btn) > 0 and await _safe_is_visible(timeout_btn):
                logger.info(f"[{self.county_name}] Exception 2: 'Session timeout warning' detected. Clicking 'Continue session'...")
                await resilient_click(timeout_btn, page=page, timeout_ms=3000)
                await page.wait_for_timeout(800)

                # Ensure party name tab and search data are retained
                await self.select_party_name_tab(page)
                await self.fill_search_fields(page, l_name, f_name, date_of_loss)
                return True
        except Exception as e_timeout:
            logger.debug(f"[{self.county_name}] Session timeout check note: {e_timeout}")
        return False

    async def return_to_search_state(self, page: Page) -> None:
        """Step J: Reset Broward tab to clean search form and keep tab open (V4 Parity: GoToWebPage https://www.browardclerk.org/Web2)."""
        try:
            logger.info(f"[{self.county_name}] Step J: Resetting to clean search state on {self.base_url}...")
            reset_url = self.base_url.rstrip("/")
            if not reset_url.endswith("/Web2") and "/CaseSearch" not in reset_url:
                reset_url = f"{reset_url}/Web2"

            await page.goto(reset_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
            await page.wait_for_timeout(800)
            await self.select_party_name_tab(page)
        except Exception as e_reset:
            logger.debug(f"[{self.county_name}] Step J return to search state note: {e_reset}")

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

        # Step A & B: Open Broward & navigate to Case Search
        await self.navigate_to_search(page)

        # Step C: Verify & select Party Name tab
        await self.select_party_name_tab(page)

        # Exception 3: CAPTCHA Retry & Refresh Loop adhering to dynamically configured Max Attempts (default: 2) and CAPTCHA Wait (default: 120s)
        max_attempts = max(1, getattr(self, "max_attempts", 2))
        captcha_solved = False

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                logger.info(
                    f"[{self.county_name}] Exception 1 & 3: CAPTCHA Retry attempt {attempt}/{max_attempts}. "
                    f"Performing hard refresh and repeating from Step C (Party Name tab)..."
                )
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=self.timeout_ms)
                    await page.wait_for_timeout(getattr(self, "reload_backoff_seconds", 2) * 1000)
                    # Step C: Select Party Name tab upon reload
                    await self.select_party_name_tab(page)
                except Exception as e_rel:
                    logger.warning(f"[{self.county_name}] Page reload note: {e_rel}")

            # Exception 2: Check session timeout popup before entering data
            await self.check_and_handle_session_timeout(page, l_name, f_name, date_of_loss)

            # Step D: Enter Search Data for CURRENT unique name
            await self.fill_search_fields(page, l_name, f_name, date_of_loss)

            # Step E & F: CAPTCHA verification (reCAPTCHA / Turnstile / AntiCaptcha)
            t_cap_start = datetime.now()
            captcha_ok = await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
            t_cap_end = datetime.now()
            self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end, status="SUCCESS" if captcha_ok else "TIMEOUT")

            if captcha_ok:
                captcha_solved = True
                logger.info(f"[{self.county_name}] Step E & F: CAPTCHA solved! Waiting 2s for Turnstile token to settle...")
                await page.wait_for_timeout(2000)
                break
            else:
                logger.warning(
                    f"[{self.county_name}] Exception 3: CAPTCHA challenge unsolved after {self.captcha_wait_seconds}s "
                    f"(attempt {attempt}/{max_attempts})"
                )

        if not captcha_solved:
            # Resilient speculative submit attempt: Click Search and check if navigation proceeds to Results
            try:
                logger.info(f"[{self.county_name}] Attempting speculative submit of #PersonSearchResults...")
                submit_res = await page.evaluate("""() => {
                    const btn = document.getElementById('PersonSearchResults');
                    if (btn) { btn.click(); return true; }
                    return false;
                }""")
                if submit_res:
                    try:
                        await page.wait_for_url("**/CaseSearchECA/*Results*", timeout=8000)
                        logger.info(f"[{self.county_name}] Speculative submit succeeded! Navigated to Results.")
                        captcha_solved = True
                    except Exception:
                        pass
            except Exception as e_spec:
                logger.debug(f"Speculative submit note: {e_spec}")

        if not captcha_solved:
            logger.error(
                f"[{self.county_name}] Exception 3: CAPTCHA verification failed after {max_attempts} attempts "
                f"for party '{f_name} {l_name}'."
            )
            raise CaptchaResolutionError(f"[{self.county_name}] CAPTCHA was not resolved after {max_attempts} attempts")

        # Step G: Immediately click "Search" upon successful CAPTCHA verification
        t_sub_start = datetime.now()
        # Pre-validate fields right before submission so FormValidation does not block
        await _safe_eval(page, """() => {
            if (window.$ && $('#personSearchForm').data('formValidation')) {
                try {
                    const fv = $('#personSearchForm').data('formValidation');
                    fv.revalidateField('lastName');
                    fv.revalidateField('firstName');
                    const dolInput = document.getElementById('filingDateOnOrAfterP');
                    if (dolInput && dolInput.value) {
                        fv.revalidateField('filingDateOnOrAfterP');
                    }
                } catch(e) {}
            }
        }""")

        # V4 uses ExecuteJavascript on this exact element immediately after
        # its solved-image check. A physical mouse route can wait for scrolling
        # or actionability even while the CAPTCHA token is already valid.
        logger.info(f"[{self.county_name}] Step G: Clicking V4 #PersonSearchResults directly...")
        try:
            submitted = await page.evaluate("""() => {
                const button = document.getElementById('PersonSearchResults');
                if (!button) return false;
                button.click();
                return true;
            }""")
        except Exception as click_error:
            # A synchronous navigation can destroy the old execution context
            # after the click has fired. The results wait below verifies it.
            if "execution context was destroyed" not in str(click_error).lower():
                raise
            submitted = True
        if not submitted:
            search_btn = page.locator(
                "#personSearchForm button#PersonSearchResults, "
                "#nameSearch button#PersonSearchResults, "
                "button#PersonSearchResults, "
                "#personSearchForm button[type='submit']"
            )
            if await _safe_count(search_btn) == 0:
                raise RuntimeError(f"[{self.county_name}] V4 PersonSearchResults control was not found")
            await self.biometric_click(page, search_btn.first)
            submitted = True
        else:
            await self.pace_action(page)

        # Check immediately if red error banner appeared ("Your request could not be completed. Please try again.")
        try:
            err_banner = page.locator(".alert-danger, .alert:has-text('could not be completed'), .alert:has-text('try again')")
            if await _safe_count(err_banner) > 0 and await _safe_is_visible(err_banner):
                banner_text = await _safe_inner_text(err_banner.first)
                logger.warning(f"[{self.county_name}] Broward Turnstile submission note ({banner_text}). Attempting fast recovery...")
                await page.reload(wait_until="domcontentloaded", timeout=self.timeout_ms)
                await page.wait_for_timeout(1000)
                await self.select_party_name_tab(page)
                await self.fill_search_fields(page, l_name, f_name, date_of_loss)
                if await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds):
                    await page.wait_for_timeout(2000)
                    await page.evaluate("""() => {
                        const btn = document.getElementById('PersonSearchResults');
                        if (btn) btn.click();
                    }""")
        except Exception as e_chk_banner:
            logger.debug(f"[{self.county_name}] Banner check note: {e_chk_banner}")

        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # Step H: Wait for results page to fully load (detect navigation away from search form, results container, or empty message)
        try:
            # We MUST wait for the navigation to the Results page
            await page.wait_for_url("**/CaseSearchECA/*Results*", timeout=self.timeout_ms)

            # Wait for loading mask to disappear
            for _ in range(60):
                loading_mask = page.locator(".k-loading-mask, .k-loading-image")
                count = await _safe_count(loading_mask)
                any_visible = False
                for i in range(count):
                    try:
                        if await loading_mask.nth(i).is_visible():
                            any_visible = True
                            break
                    except Exception:
                        pass
                if not any_visible:
                    break
                await page.wait_for_timeout(500)

            # Wait for actual case result rows or an empty results message
            await page.wait_for_selector(
                "table tbody tr td button, table.table tbody tr:has(td), "
                ".alert:has-text('No records found'), :text-is('No items to display')",
                timeout=self.timeout_ms,
            )
        except Exception as e:
            logger.warning(f"[{self.county_name}] Step H Results Wait Timeout: {e}")
        await self.pace_action(page)

        # Step I: Check whether data is available
        body_text = await page.inner_text("body")
        no_match_markers = (
            "no records found", "no cases found", "no items to display",
            "no data found", "no data available", "0 records found",
            "0 items found", "0 results returned", "no results found",
            "no matching records found", "showing 0 to 0 of 0",
            "no cases matched", "no records", "0 records",
        )
        if any(marker in body_text.lower() for marker in no_match_markers):
            logger.info(f"[{self.county_name}] Step I: Search for '{l_name}, {f_name}': No records found.")
            await self.return_to_search_state(page)
            return []

        # Step J & K: Extract ALL available columns across ALL pages
        t_ext_start = datetime.now()
        has_next_page = True
        page_num = 1
        seen_page_signatures: set[tuple[tuple[str, ...], ...]] = set()

        # Step J: Discover all table headers from true results table (excluding glossary/prefix tables)
        header_names: list[str] = []
        try:
            th_loc = page.locator("table thead th, table.table th, table tr th")
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
                logger.info(f"[{self.county_name}] Step J: Discovered table headers: {header_names}")
        except Exception as e_th:
            logger.debug(f"[{self.county_name}] Header discovery note: {e_th}")

        # Known glossary labels to strictly ignore
        _GLOSSARY_PREFIXES = {
            "CACE", "COCE", "CONO", "COSO", "COWE", "CF", "CO", "CT", "MM",
            "MO", "NI", "TC", "TI", "CASE PREFIX", "COURT TYPE", "LOCATION",
            "DIVISION IDENTIFIERS", "CASE NUMBER", "CASE NO.", "CASE NO", "CASE #", "",
        }

        while has_next_page:
            page_start_count = len(results)
            page_signature: list[tuple[str, ...]] = []
            rows = page.locator("table.table tbody tr, table tbody tr, .search-result-row")
            row_count = await _safe_count(rows)
            logger.info(f"[{self.county_name}] Step K: Page {page_num}: Found {row_count} table rows")

            page_cases: list[dict[str, Any]] = []
            for i in range(row_count):
                row = rows.nth(i)
                cells: list[str] = []
                try:
                    cells_raw = row.locator("td").all_inner_texts()
                    if inspect.isawaitable(cells_raw):
                        cells = await cells_raw
                    elif isinstance(cells_raw, list):
                        cells = cells_raw
                except Exception:
                    cells = []
                if cells:
                    page_signature.append(tuple(str(cell).strip() for cell in cells))
                if len(cells) >= 3:
                    case_num = cells[0].strip()

                    # Filter out empty, header, or static glossary prefix table rows
                    if not case_num or case_num.upper() in _GLOSSARY_PREFIXES:
                        continue

                    # Static glossary prefix trap prevention: Real court case numbers always contain digits!
                    # E.g., 'CACE-22-012345', '062022CA012345', 'CACE23012345'. A pure alphabetic code like 'CACE' is a glossary entry.
                    if not any(ch.isdigit() for ch in case_num):
                        continue

                    # Also check if style looks like a glossary description
                    case_style = cells[1].strip() if len(cells) > 1 else ""
                    if case_style.lower() in ("civil action central", "county civil central", "felony"):
                        continue

                    # Dynamically map table cells using discovered headers if present
                    col_map: dict[str, int] = {}
                    for h_idx, h in enumerate(header_names):
                        h_lower = h.lower()
                        if "case" in h_lower and ("number" in h_lower or "no" in h_lower or "#" in h_lower):
                            col_map["case_num"] = h_idx
                        elif "style" in h_lower or "party" in h_lower or "title" in h_lower or "desc" in h_lower:
                            col_map["case_style"] = h_idx
                        elif "type" in h_lower:
                            col_map["case_type"] = h_idx
                        elif "date" in h_lower or "filing" in h_lower:
                            col_map["filing_date"] = h_idx
                        elif "status" in h_lower:
                            col_map["case_status"] = h_idx

                    idx_num = col_map.get("case_num", 0)
                    idx_style = col_map.get("case_style", 1)
                    idx_type = col_map.get("case_type", 2)
                    idx_date = col_map.get("filing_date", 3)
                    idx_status = col_map.get("case_status", 4)

                    case_num = cells[idx_num].strip() if len(cells) > idx_num else cells[0].strip()
                    case_style = cells[idx_style].strip() if len(cells) > idx_style else (cells[1].strip() if len(cells) > 1 else "")
                    case_type = cells[idx_type].strip() if len(cells) > idx_type else (cells[2].strip() if len(cells) > 2 else "")
                    filing_date = cells[idx_date].strip() if len(cells) > idx_date else (cells[3].strip() if len(cells) > 3 else "")
                    case_status = cells[idx_status].strip() if len(cells) > idx_status else (cells[4].strip() if len(cells) > 4 else "")

                    # Normalize filing date using regex (handling ISO YYYY-MM-DD or US MM/DD/YYYY)
                    import re
                    m_iso = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", filing_date)
                    if m_iso:
                        y, m, d = m_iso.groups()
                        filing_date = f"{int(m):02d}/{int(d):02d}/{y}"
                    else:
                        m_us = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", filing_date)
                        if m_us:
                            m, d, y = m_us.groups()
                            if len(y) == 2:
                                y = f"20{y}" if int(y) < 50 else f"19{y}"
                            filing_date = f"{int(m):02d}/{int(d):02d}/{y}"
                        else:
                            # Search across all cells for a valid date if designated column had none
                            filing_date = ""
                            for c_val in cells:
                                d_match = re.search(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b", c_val)
                                if d_match:
                                    raw_d = d_match.group(1)
                                    m, d, y = raw_d.split("/")
                                    if len(y) == 2:
                                        y = f"20{y}" if int(y) < 50 else f"19{y}"
                                    filing_date = f"{int(m):02d}/{int(d):02d}/{y}"
                                    break
                                d_iso = re.search(r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b", c_val)
                                if d_iso:
                                    raw_d = d_iso.group(1)
                                    y, m, d = re.split(r"[/-]", raw_d)
                                    filing_date = f"{int(m):02d}/{int(d):02d}/{y}"
                                    break

                    # If no valid filing date was found anywhere in the row, skip row as non-case
                    if not filing_date:
                        logger.warning(f"[{self.county_name}] Skipping row without a valid filing date: case_num={case_num}, cells={cells}")
                        continue

                    # Preserve the five-field V4 Broward JSON contract.
                    case_payload: dict[str, Any] = {
                        "CaseNumber": case_num,
                        "CaseStyle": case_style,
                        "FilingDate": filing_date,
                        "CaseStatus": case_status,
                        "CaseType": case_type,
                    }

                    page_cases.append(case_payload)

            signature = tuple(page_signature)
            if page_num > 1 and signature in seen_page_signatures:
                raise RuntimeError(f"[{self.county_name}] Pagination did not advance to new case results")
            seen_page_signatures.add(signature)
            results.extend(page_cases)

            # Step K: Pagination traversal
            next_btn = page.locator("a[title*='next' i], a:has-text('Go to the next page'), a:has-text('Next'), .pagination .next:not(.disabled) a")
            if await _safe_count(next_btn) > 0 and await _safe_is_visible(next_btn):
                is_disabled = (await _safe_get_attribute(next_btn, "disabled")) or (await _safe_get_attribute(next_btn, "aria-disabled"))
                cls_attr = (await _safe_get_attribute(next_btn, "class")) or ""
                if is_disabled == "true" or "disabled" in cls_attr.lower():
                    has_next_page = False
                else:
                    if page_num > 1 and len(results) == page_start_count:
                        logger.warning(f"[{self.county_name}] Pagination did not advance to new case results; ending pagination.")
                        has_next_page = False
                        break
                    try:
                        logger.info(f"[{self.county_name}] Step K: Advancing to page {page_num + 1}...")
                        await self.biometric_click(page, next_btn.first)
                        await page.wait_for_timeout(1500)
                        page_num += 1
                    except Exception:
                        has_next_page = False
            else:
                has_next_page = False

        if not results:
            body_text = (await page.inner_text("body")).lower()
            if any(marker in body_text for marker in no_match_markers):
                logger.info(f"[{self.county_name}] No matching records found after parsing.")
                await self.return_to_search_state(page)
                return []
            dt_empty = page.locator(".dataTables_empty, td:has-text('No data'), td:has-text('No records')")
            if await _safe_count(dt_empty) > 0:
                logger.info(f"[{self.county_name}] Empty results indicator detected; returning 0 results.")
                await self.return_to_search_state(page)
                return []
            is_search_form = await _safe_eval(page, "() => !!document.getElementById('personSearchForm') || !!document.getElementById('nameSearch')")
            if is_search_form:
                logger.info(f"[{self.county_name}] Remained on search form with 0 records; returning empty result.")
                await self.return_to_search_state(page)
                return []
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

        # Section 4: Return Broward tab to search state for next unique name
        await self.return_to_search_state(page)

        return results
