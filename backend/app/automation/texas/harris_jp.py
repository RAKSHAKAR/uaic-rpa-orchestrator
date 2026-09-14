"""Harris County Justice of the Peace (JP) Portal Automation Scraper (Power Automate V4 Parity)."""

import logging
import re
from datetime import datetime
from typing import Any

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper

logger = logging.getLogger("uaic_orchestrator.automation.harris_jp")


class HarrisJPScraper(BaseCourtScraper):
    """
    Scraper for Harris County JP Odyssey Portal.
    Strict Schema: Output does NOT contain CaseType.
    """

    def __init__(self, base_url: str | None = None, **kwargs):
        super().__init__(
            county_name="Harris County JP (TX)",
            base_url=base_url or "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/",
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
        # Navigate to Odyssey Smart Search (Dashboard/29). If base_url is root/Home, append the dashboard path.
        nav_url = self.base_url.rstrip("/")
        if "Dashboard/29" not in nav_url:
            nav_url = f"{nav_url.rstrip('/')}/Dashboard/29"
        await page.goto(nav_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)
        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=nav_url)

        # 1. Fill Smart Search criteria: LastName,FirstName (Harris JP does NOT use DOL)
        t_fill_start = datetime.now()
        search_input = page.locator("#caseCriteria_SearchCriteria, #SearchCriteria, input[name='caseCriteria_SearchCriteria']")
        await search_input.first.wait_for(state="visible", timeout=15000)

        query = f"{l_name},{f_name}".strip(", ")
        await self.biometric_fill(search_input.first, query)
        logger.info(f"[{self.county_name}] Filled Smart Search query: {query}")
        await page.wait_for_timeout(500)
        t_fill_end = datetime.now()
        self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, query=query)

        # 2. Detect and solve reCAPTCHA (with 4x8s wait policy matching V4)
        t_cap_start = datetime.now()
        captcha_ok = await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
        t_cap_end = datetime.now()
        self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end, status="SUCCESS" if captcha_ok else "TIMEOUT")
        if not captcha_ok:
            logger.warning("CAPTCHA challenge unsolved on Harris County JP portal")
            return []

        # 3. Submit search via #btnSSSubmit
        t_sub_start = datetime.now()
        submit_btn = page.locator("#btnSSSubmit, input#btnSSSubmit, input[type='submit'][value*='Submit' i]")
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_timeout(3000)
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # 4. Check for 'No cases match your search'
        body_text = await page.inner_text("body")
        if "no cases match your search" in body_text.lower():
            logger.info(f"[{self.county_name}] Search for '{query}': No cases match search.")
            return []

        # 5. Extract results from grid and pagination
        t_ext_start = datetime.now()
        rows = page.locator(".k-grid-content tbody tr, table.k-selectable tbody tr, table tbody tr")
        row_count = await rows.count()
        logger.info(f"[{self.county_name}] Found {row_count} potential result rows")

        for i in range(row_count):
            row = rows.nth(i)
            cells = await row.locator("td").all_inner_texts()
            if len(cells) >= 3:
                case_num = cells[0].strip()
                case_style = cells[1].strip() if len(cells) > 1 else ""
                filing_date = cells[2].strip() if len(cells) > 2 else ""
                raw_status = cells[3].strip() if len(cells) > 3 else "ACTIVE"
                # Strip "Case Status" prefix if present matching V4
                case_status = re.sub(r"(?i)^case\s*status\s*[:\s]*", "", raw_status).strip() or "ACTIVE"

                if case_num:
                    # Note: Strict schema: NO CaseType in Harris JP output!
                    results.append({
                        "CaseNumber": case_num,
                        "CaseStyle": case_style or f"{l_name}, {f_name}",
                        "CountyWebsite": self.base_url,
                        "FilingDate": filing_date,
                        "CaseStatus": case_status,
                    })

        # Reset search screen if available
        try:
            reset_link = page.locator("#tcControllerLink_0, a:has-text('Smart Search')")
            if await reset_link.count() > 0:
                await reset_link.first.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass

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
