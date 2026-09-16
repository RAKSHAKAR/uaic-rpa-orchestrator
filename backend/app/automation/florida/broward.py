"""Broward County Clerk Portal Automation Scraper (Power Automate V4 Parity)."""

import logging
from datetime import datetime
from typing import Any

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper

logger = logging.getLogger("uaic_orchestrator.automation.broward")


class BrowardScraper(BaseCourtScraper):
    """Scraper for Broward County Clerk of Courts."""

    def __init__(self, base_url: str | None = None, **kwargs):
        super().__init__(
            county_name="Broward County (FL)",
            base_url=base_url or "https://www.browardclerk.org/",
            **kwargs,
        )

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

        t_nav_start = datetime.now()
        # Navigate from configured base URL to the Case Search ECA page
        search_url = self.base_url.rstrip("/")
        if not search_url.endswith("/Web2") and "/CaseSearch" not in search_url:
            search_url = f"{search_url.rstrip('/')}/Web2/CaseSearchECA/Index/"
        await page.goto(search_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)
        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=search_url)

        # 1. Fill search inputs mirroring V4
        t_fill_start = datetime.now()
        last_input = page.locator("input#lastName, input[name='lastName'], input[name*='LastName']")
        first_input = page.locator("input#firstName, input[name='firstName'], input[name*='FirstName']")
        dol_input = page.locator("input#filingDateOnOrAfterP, input[name='filingDateOnOrAfterP']")

        await last_input.first.wait_for(state="visible", timeout=15000)
        await self.biometric_fill(last_input.first, l_name)
        if f_name and await first_input.count() > 0:
            await self.biometric_fill(first_input.first, f_name)

        if date_of_loss and await dol_input.count() > 0:
            clean_dol = date_of_loss.strip()
            await self.biometric_fill(dol_input.first, clean_dol)
            logger.info(f"[{self.county_name}] Filled filingDateOnOrAfterP with DOL: {clean_dol}")

        await page.wait_for_timeout(500)
        t_fill_end = datetime.now()
        self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=f"{f_name} {l_name}", dol=date_of_loss)

        # 2. CAPTCHA verification (Google reCAPTCHA v2 / AntiCaptcha)
        t_cap_start = datetime.now()
        captcha_ok = await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
        t_cap_end = datetime.now()
        self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end, status="SUCCESS" if captcha_ok else "TIMEOUT")
        if not captcha_ok:
            logger.warning(f"CAPTCHA challenge unsolved on Broward County portal after {self.captcha_wait_seconds}s")
            return []

        # Double check that AntiCaptcha extension is not in the middle of injecting
        # GAP-007: Initial 500ms settling delay before polling to avoid false-negative on fast machines
        await page.wait_for_timeout(500)
        for _ in range(10):
            still_solving = await page.evaluate('''() => {
                const s = document.querySelector('.antigate_solver, [class*="antigate"]');
                return s && (s.className.toLowerCase().includes("in_process") || (s.getAttribute("data-status") || "").toLowerCase().includes("in_process"));
            }''')
            if not still_solving:
                break
            logger.info(f"[{self.county_name}] Waiting for final AntiCaptcha token settlement before submit...")
            await page.wait_for_timeout(1000)

        # 3. Submit search via #PersonSearchResults click
        t_sub_start = datetime.now()
        search_btn = page.locator("#PersonSearchResults, button#PersonSearchResults")
        if await search_btn.count() > 0:
            logger.info(f"[{self.county_name}] Clicking #PersonSearchResults...")
            try:
                await search_btn.first.click(timeout=5000)
            except Exception:
                await page.evaluate("() => document.getElementById('PersonSearchResults') && document.getElementById('PersonSearchResults').click()")
        else:
            await page.evaluate("() => document.querySelector('#personSearchForm') && document.querySelector('#personSearchForm').submit()")
        
        await page.wait_for_timeout(3000)
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # 4. Check for 'No records found'
        body_text = await page.inner_text("body")
        if "no records found" in body_text.lower() or "no cases found" in body_text.lower():
            logger.info(f"[{self.county_name}] Search for '{l_name}, {f_name}': No records found.")
            return []

        # 5. Extraction & Pagination loop mirroring V4
        t_ext_start = datetime.now()
        has_next_page = True
        page_num = 1
        seen_case_numbers = set()

        while has_next_page:
            rows = page.locator("table.table tbody tr, table tbody tr, .search-result-row")
            row_count = await rows.count()
            logger.info(f"[{self.county_name}] Page {page_num}: Found {row_count} table rows")

            for i in range(row_count):
                row = rows.nth(i)
                cells = await row.locator("td").all_inner_texts()
                if len(cells) >= 3:
                    case_num = cells[0].strip()
                    # Column layout matching V4:
                    # td:eq(0) -> CaseNumber
                    # td:eq(1) -> CaseStyle
                    # td:eq(2) -> CaseType
                    # td:eq(3) -> FilingDate
                    # td:eq(4) -> CaseStatus
                    case_style = cells[1].strip() if len(cells) > 1 else ""
                    case_type = cells[2].strip() if len(cells) > 2 else "CIRCUIT CIVIL"
                    filing_date = cells[3].strip() if len(cells) > 3 else ""
                    case_status = cells[4].strip() if len(cells) > 4 else "OPEN"

                    # GAP-001: Skip header rows that got included in tbody
                    _HEADER_LABELS = {"CASE NUMBER", "CASE NO.", "CASE NO", "CASE #", ""}
                    if case_num and case_num.upper() not in _HEADER_LABELS and case_num not in seen_case_numbers:
                        seen_case_numbers.add(case_num)
                        results.append({
                            "CaseNumber": case_num,
                            "CaseStyle": case_style,
                            "CountyWebsite": self.base_url,
                            "FilingDate": filing_date,
                            "CaseStatus": case_status,
                            "CaseType": case_type,
                        })

            # Check next page button
            next_btn = page.locator("a[title*='next' i], a:has-text('Go to the next page'), a:has-text('Next'), .pagination .next:not(.disabled) a")
            if await next_btn.count() > 0 and await next_btn.first.is_visible():
                is_disabled = await next_btn.first.get_attribute("disabled") or await next_btn.first.get_attribute("aria-disabled")
                if is_disabled == "true":
                    has_next_page = False
                else:
                    try:
                        logger.info(f"[{self.county_name}] Advancing to page {page_num + 1}...")
                        await next_btn.first.click()
                        await page.wait_for_timeout(2500)
                        page_num += 1
                        if page_num > 10:  # Safety ceiling
                            break
                    except Exception:
                        has_next_page = False
            else:
                has_next_page = False

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
