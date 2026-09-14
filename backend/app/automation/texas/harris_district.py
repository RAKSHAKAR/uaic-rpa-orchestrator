"""Harris County District Clerk eDocs Portal Scraper (Power Automate V4 Parity)."""

import logging
import re
from datetime import datetime
from typing import Any

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper

logger = logging.getLogger("uaic_orchestrator.automation.harris_district")


class HarrisDistrictClerkScraper(BaseCourtScraper):
    """Scraper for Harris County District Clerk eDocs Public Search."""

    def __init__(self, base_url: str | None = None, **kwargs):
        super().__init__(
            county_name="Harris District Clerk (TX)",
            base_url=base_url or "https://www.hcdistrictclerk.com/",
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
        # Navigate from configured base URL to the eDocs Party Search page
        nav_url = self.base_url.rstrip("/")
        if "eDocs" not in nav_url and "Search.aspx" not in nav_url:
            nav_url = f"{nav_url.rstrip('/')}/eDocs/Public/Search.aspx"
        await page.goto(nav_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)
        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=nav_url)

        # 1. Navigate to Party Inquiry if needed
        t_fill_start = datetime.now()
        party_inquiry_link = page.locator("a:has-text('Party Inquiry'), #btnPartyInquiry, a[href*='Party']")
        if await party_inquiry_link.count() > 0:
            try:
                await party_inquiry_link.first.click()
                await page.wait_for_timeout(1000)
            except Exception:
                pass

        # 2. Fill Party Name & Date Range matching V4
        # In V4: document.getElementById("txtPartyName").value = "LastName, FirstName"
        party_input = page.locator("#txtPartyName, input[id*='txtPartyName'], input[name*='txtPartyName'], #txtPartyLastName")
        await party_input.first.wait_for(state="visible", timeout=15000)

        query = f"{l_name}, {f_name}".strip(", ")
        await self.biometric_fill(party_input.first, query)
        logger.info(f"[{self.county_name}] Filled Party Name: {query}")

        dol_input = page.locator("input[id*='txtFiledDateFrom'], input[name*='txtFiledDateFrom'], input[id*='txtDateFrom']")
        if date_of_loss and await dol_input.count() > 0:
            clean_dol = date_of_loss.strip()
            await self.biometric_fill(dol_input.first, clean_dol)
            logger.info(f"[{self.county_name}] Filled Filed Date Range with DOL: {clean_dol}")

        await page.wait_for_timeout(500)
        t_fill_end = datetime.now()
        self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=query, dol=date_of_loss)

        # 3. CAPTCHA verification if any
        t_cap_start = datetime.now()
        await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
        t_cap_end = datetime.now()
        self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end)

        # 4. Click Search Button
        t_sub_start = datetime.now()
        search_btn = page.locator("input[id*='btnPartySearch'], input[id*='btnSearch'], input[value*='Search' i], button:has-text('Search')")
        if await search_btn.count() > 0:
            await search_btn.first.click()
            await page.wait_for_timeout(3500)
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # 5. Extract table rows matching V4:
        # td:eq(0) -> CaseNumber
        # td:eq(1) > a > strong -> CaseStyle
        # td:eq(5) -> FilingDate
        # td:eq(6) -> CaseType
        t_ext_start = datetime.now()
        rows = page.locator("table[id*='dgSearchResults'] tbody tr, .grid-results tr, table.grid tbody tr, table tbody tr")
        row_count = await rows.count()
        logger.info(f"[{self.county_name}] Found {row_count} potential result rows")

        for i in range(row_count):
            row = rows.nth(i)
            cells = await row.locator("td").all_inner_texts()
            if len(cells) >= 3:
                case_num = cells[0].strip()
                case_style = cells[1].strip() if len(cells) > 1 else ""
                filing_date = cells[5].strip() if len(cells) > 5 else (cells[2].strip() if len(cells) > 2 else "")
                case_type = cells[6].strip() if len(cells) > 6 else (cells[4].strip() if len(cells) > 4 else "DISTRICT COURTS – CIVIL")

                # Derive status from case number or status cell matching V4
                raw_status = cells[3].strip() if len(cells) > 3 else "ACTIVE"
                case_status = re.sub(r"(?i)^status\s*[:\s]*", "", raw_status).strip() or "ACTIVE"

                if case_num and case_num.upper() != "CASE NUMBER":
                    results.append({
                        "CaseNumber": case_num,
                        "CaseStyle": case_style or f"{l_name}, {f_name}",
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
