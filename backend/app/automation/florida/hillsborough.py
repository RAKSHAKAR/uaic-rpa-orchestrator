"""Hillsborough County Clerk Portal Automation Scraper (Power Automate V4 Parity)."""

import logging
import os
from datetime import datetime
from typing import Any

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper

logger = logging.getLogger("uaic_orchestrator.automation.hillsborough")


class HillsboroughScraper(BaseCourtScraper):
    """Scraper for Hillsborough County Clerk of Courts."""

    def __init__(self, base_url: str | None = None, **kwargs):
        super().__init__(
            county_name="Hillsborough County (FL)",
            base_url=base_url or "https://hover.hillsclerk.com/",
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

        t_nav_start = datetime.now()
        # Navigate from configured base URL to the Party search tab
        nav_url = self.base_url.rstrip("/")
        if not nav_url.endswith(".html") and "caseSearch" not in nav_url:
            nav_url = f"{nav_url.rstrip('/')}/html/case/caseSearch.html#nav-Party-tab"
        await page.goto(nav_url, wait_until="domcontentloaded")
        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=nav_url)

        # 1. Wait for and activate Party Search Tab
        t_fill_start = datetime.now()
        party_tab = page.locator("#nav-Party-tab, button:has-text('Search by Party'), a:has-text('Party')")
        if await party_tab.count() > 0:
            try:
                await party_tab.first.wait_for(state="visible", timeout=25000)
                await party_tab.first.click()
            except Exception:
                pass
            await page.wait_for_timeout(1000)

        # 2. Fill Party Search Inputs (spLastName, spFirstName, spDateFiledAfter)
        last_input = page.locator("#spLastName, input[name='partyLastName'], #partyLastName")
        first_input = page.locator("#spFirstName, input[name='partyFirstName'], #partyFirstName")
        dol_input = page.locator("#spDateFiledAfter, input[name='spDateFiledAfter']")

        await last_input.first.wait_for(state="visible", timeout=25000)
        await self.biometric_fill(last_input.first, l_name)
        if f_name and await first_input.count() > 0:
            await self.biometric_fill(first_input.first, f_name)

        if date_of_loss and await dol_input.count() > 0:
            clean_dol = date_of_loss.strip()
            try:
                await page.evaluate(
                    """(val) => {
                        const el = document.querySelector('#spDateFiledAfter') || document.querySelector("input[name='spDateFiledAfter']");
                        if (el) {
                            el.removeAttribute('readonly');
                            el.value = val;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }""",
                    clean_dol,
                )
                logger.info(f"[{self.county_name}] Filled spDateFiledAfter with DOL via DOM evaluation: {clean_dol}")
            except Exception as e:
                logger.warning(f"[{self.county_name}] DOM date fill note: {e}, falling back to locator.fill")
                try:
                    await self.biometric_fill(dol_input.first, clean_dol)
                except Exception as ex:
                    logger.warning(f"[{self.county_name}] Could not fill datepicker: {ex}")

        await page.wait_for_timeout(500)
        t_fill_end = datetime.now()
        self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=f"{f_name} {l_name}", dol=date_of_loss)

        # 3. Check CAPTCHA if any
        t_cap_start = datetime.now()
        await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
        t_cap_end = datetime.now()
        self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end)

        # 4. Click Submit Button
        t_sub_start = datetime.now()
        search_btn = page.locator("#btnSubmitPartySearch, #partySearchBtn, button:has-text('Search'), input[value='Search']")
        if await search_btn.count() > 0:
            await search_btn.first.click()
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # 5. Wait for results grid with 50s timeout matching V4
        t_ext_start = datetime.now()
        try:
            results_table = page.locator("#partyResultsTable, table.dataTable")
            await results_table.first.wait_for(state="visible", timeout=50000)
        except Exception:
            logger.warning(f"[{self.county_name}] Table wait timed out after 50s")

        await page.wait_for_timeout(1000)

        # Check for empty state
        empty_msg = page.locator(".dataTables_empty, :text('No data available in table')")
        if await empty_msg.count() > 0 and await empty_msg.first.is_visible():
            logger.info(f"[{self.county_name}] Search for '{l_name}, {f_name}': No data available in table.")
            t_ext_end = datetime.now()
            self.record_stage("result_retrieval", "Result Retrieval", t_ext_start, t_ext_end, cases_found=0, result_category="No Record Found")
            return []

        # 6. Extract Table Rows matching V4
        rows = page.locator("#partyResultsTable tbody tr, table.dataTable tbody tr")
        row_count = await rows.count()

        for i in range(row_count):
            row = rows.nth(i)
            cells = await row.locator("td").all_inner_texts()
            if len(cells) <= 1:
                continue

            if len(cells) >= 8:
                # Column mapping matching V4:
                # td:eq(2) -> CaseNumber
                # td:eq(4) -> CaseStyle
                # td:eq(5) -> CaseStatus
                # td:eq(6) -> FilingDate
                # td:eq(7) -> CaseType
                case_num = cells[2].strip()
                case_style = cells[4].strip()
                case_status = cells[5].strip().upper()
                filing_date = cells[6].strip()
                case_type = cells[7].strip()

                if case_num:
                    results.append({
                        "CaseNumber": case_num,
                        "Citation": cells[3].strip() if len(cells) > 3 else "",
                        "CaseStyle": case_style,
                        "CountyWebsite": self.base_url,
                        "FilingDate": filing_date,
                        "CaseStatus": case_status,
                        "CaseType": case_type,
                    })

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
