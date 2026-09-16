"""Harris County Clerk WebSearch Portal Scraper (Power Automate V4 Parity)."""

import logging
from datetime import datetime
from typing import Any

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper

logger = logging.getLogger("uaic_orchestrator.automation.harris_cclerk")


class HarrisCountyClerkScraper(BaseCourtScraper):
    """
    Scraper for Harris County Clerk WebSearch.
    Strict Schema: Output does NOT contain CaseType.
    """

    def __init__(self, base_url: str | None = None, **kwargs):
        super().__init__(
            county_name="Harris County Clerk (TX)",
            base_url=base_url or "https://www.cclerk.hctx.net/Applications/WebSearch/",
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
        await self._navigate_to_county_civil(page)
        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=self.base_url)

        # 1. Fill search inputs matching V4
        t_fill_start = datetime.now()
        last_input = page.locator("#ctl00_ContentPlaceHolder1_txtLastName, input[name*='txtLastName'], input[id*='txtLastName'], input[name*='LastName']")
        first_input = page.locator("#ctl00_ContentPlaceHolder1_txtFirstName, input[name*='txtFirstName'], input[id*='txtFirstName'], input[name*='FirstName']")
        dol_input = page.locator("#ctl00_ContentPlaceHolder1_txtDateFrom, input[name*='DateFrom'], input[id*='DateFrom'], input[placeholder*='File Date from']")

        await last_input.first.wait_for(state="visible", timeout=15000)
        await self.biometric_fill(last_input.first, l_name)
        if f_name and await first_input.count() > 0:
            await self.biometric_fill(first_input.first, f_name)

        if date_of_loss and await dol_input.count() > 0:
            clean_dol = date_of_loss.strip()
            await self.biometric_fill(dol_input.first, clean_dol)
            logger.info(f"[{self.county_name}] Filled File Date from with DOL: {clean_dol}")

        await page.wait_for_timeout(500)
        t_fill_end = datetime.now()
        self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=f"{f_name} {l_name}", dol=date_of_loss)

        # 2. CAPTCHA verification if any
        t_cap_start = datetime.now()
        await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
        t_cap_end = datetime.now()
        self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end)

        # 3. Submit search via button click
        t_sub_start = datetime.now()
        search_btn = page.locator("#ctl00_ContentPlaceHolder1_btnSearch, input[type='submit'][value*='SEARCH' i], button:has-text('Search'), input[value='Search']")
        if await search_btn.count() > 0:
            await search_btn.first.click()
            await page.wait_for_timeout(3000)
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # 4. Extract table rows matching V4 — with WebSearch pagination (GAP-006)
        # td:eq(0) > a -> CaseNumberC
        # td:eq(2) -> FilingDateC
        # td:eq(5) > span -> CaseStyleC
        # td:eq(1) -> CaseStatusC
        t_ext_start = datetime.now()
        seen_case_numbers: set = set()
        page_num = 1

        while True:
            rows = page.locator("table[id*='grd'] tbody tr, table.grid tbody tr, table tbody tr")
            row_count = await rows.count()
            logger.info(f"[{self.county_name}] Page {page_num}: Found {row_count} potential result rows")

            for i in range(row_count):
                row = rows.nth(i)
                cells = await row.locator("td").all_inner_texts()
                if len(cells) >= 3:
                    case_num = cells[0].strip()
                    case_status = cells[1].strip() if len(cells) > 1 else "ACTIVE"
                    filing_date = cells[2].strip() if len(cells) > 2 else ""
                    case_style = cells[5].strip() if len(cells) > 5 else (cells[1].strip() if len(cells) > 1 else "")

                    _HEADER_LABELS = {"CASE NUMBER", "CASE NO.", "CASE NO", "CASE #", ""}
                    if case_num and case_num.upper() not in _HEADER_LABELS and case_num not in seen_case_numbers:
                        seen_case_numbers.add(case_num)
                        # Strict schema: NO CaseType!
                        results.append({
                            "CaseNumber": case_num,
                            "FilingDate": filing_date,
                            "CaseStyle": case_style or f"{l_name}, {f_name}",
                            "CaseStatus": case_status,
                            "CountyWebsite": self.base_url,
                        })

            # Check next page link (ASP.NET WebSearch pagination)
            next_link = page.locator(
                "table[id*='grd'] tr.pager a:has-text('Next'), "
                "table[id*='grd'] tr.pager a:has-text('>'), "
                "a[id*='Next'], a[href*='__doPostBack'][title*='next' i], "
                "a[href*='__doPostBack']:has-text('Next')"
            )
            if await next_link.count() > 0 and await next_link.first.is_visible():
                try:
                    await next_link.first.click()
                    await page.wait_for_timeout(2500)
                    page_num += 1
                    if page_num > 10:
                        break
                except Exception:
                    break
            else:
                break

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

    async def _navigate_to_county_civil(self, page) -> None:
        """Navigate to County Civil if not already on the form."""
        await page.goto(self.base_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)
        
        form = page.locator("#ctl00_ContentPlaceHolder1_txtLastName, input[name*='txtLastName']")
        if not await form.count() > 0 or not await form.first.is_visible():
            courts_menu = page.locator("a:has-text('COURTS')")
            if await courts_menu.count() > 0:
                await courts_menu.first.hover()
                await page.wait_for_timeout(500)
            civil_link = page.locator("a:has-text('County Civil')")
            if await civil_link.count() > 0:
                await civil_link.first.click()
                await page.wait_for_timeout(1500)
            if await form.count() > 0:
                await form.first.wait_for(state="visible", timeout=15000)
