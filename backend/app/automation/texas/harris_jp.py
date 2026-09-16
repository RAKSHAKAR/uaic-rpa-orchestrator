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
            # Dynamic predicate wait: wait until Kendo grid rows populate or empty banner appears
            try:
                for _ in range(25):
                    body_text = await page.inner_text("body")
                    if "no cases match your search" in body_text.lower():
                        break
                    row_candidates = page.locator(".k-grid-content tbody tr, table.k-selectable tbody tr, table tbody tr")
                    if await row_candidates.count() > 0:
                        break
                    await page.wait_for_timeout(400)
            except Exception:
                await page.wait_for_timeout(2000)
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # 4. Check for 'No cases match your search'
        t_ext_start = datetime.now()
        body_text = await page.inner_text("body")
        if "no cases match your search" in body_text.lower():
            logger.info(f"[{self.county_name}] Search for '{query}': No cases match search.")
            t_ext_end = datetime.now()
            self.record_stage("result_retrieval", "Result Retrieval", t_ext_start, t_ext_end, cases_found=0, result_category="No Record Found")
            return []

        # 5. Extract results from grid with Kendo UI multi-page pagination
        seen_case_numbers: set = set()
        page_num = 1
        _HEADER_LABELS = {"CASE NUMBER", "CASE NO.", "CASE NO", "CASE #", ""}

        while True:
            rows = page.locator(".k-grid-content tbody tr, table.k-selectable tbody tr, table tbody tr")
            row_count = await rows.count()
            logger.info(f"[{self.county_name}] Page {page_num}: Found {row_count} potential result rows")

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

                    # Sanitize CaseStyle matching V4: remove [-\\/|]
                    clean_style = re.sub(r"[-\\/|]", "", case_style).strip()
                    clean_style = re.sub(r"\s+", " ", clean_style)

                    if case_num and case_num.upper() not in _HEADER_LABELS and case_num not in seen_case_numbers:
                        seen_case_numbers.add(case_num)
                        # STRICT SCHEMA: NO CaseType in Harris JP output!
                        results.append({
                            "CaseNumber": case_num,
                            "CaseStyle": clean_style or f"{l_name}, {f_name}",
                            "CountyWebsite": self.base_url,
                            "FilingDate": filing_date,
                            "CaseStatus": case_status,
                        })

            # Check next page link in Kendo UI pager
            next_btn = page.locator(
                ".k-pager-wrap a[title='Go to the next page']:not(.k-state-disabled), "
                ".k-pager-wrap .k-i-arrow-end-right:not(.k-state-disabled), "
                "a.k-link[title='Next']:not(.k-state-disabled), "
                ".k-pager-wrap a:has-text('>'):not(.k-state-disabled)"
            )
            if await next_btn.count() > 0 and await next_btn.first.is_visible():
                classes = await next_btn.first.get_attribute("class") or ""
                if "k-state-disabled" in classes or "disabled" in classes:
                    break
                try:
                    old_case = results[-1]["CaseNumber"] if results else ""
                    await next_btn.first.click()
                    try:
                        await page.wait_for_function(
                            "oldNum => { const row = document.querySelector('.k-grid-content tbody tr, table.k-selectable tbody tr'); return row && !row.innerText.includes(oldNum); }",
                            arg=old_case,
                            timeout=5000,
                        )
                    except Exception:
                        await page.wait_for_timeout(2000)
                    page_num += 1
                    if page_num > 10:  # Safety ceiling
                        break
                except Exception:
                    break
            else:
                break

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

