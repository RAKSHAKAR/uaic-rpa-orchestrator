"""Miami-Dade County Civil Court Automation Scraper (Power Automate V4 Parity)."""

import logging
from datetime import datetime, timedelta
from typing import Any

from playwright.async_api import Page

from app.automation.base import BaseCourtScraper

logger = logging.getLogger("uaic_orchestrator.automation.miami")


class MiamiDadeScraper(BaseCourtScraper):
    """Scraper for Miami-Dade County Civil Court (OCS Portal)."""

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        requires_login: bool = True,
        **kwargs,
    ):
        super().__init__(
            county_name="Miami-Dade County (FL)",
            base_url=base_url or "https://www2.miamidadeclerk.gov/ocs/",
            **kwargs,
        )
        self.username = username
        self.password = password
        self.requires_login = requires_login

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
        await page.goto(self.base_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)
        t_nav_end = datetime.now()
        self.record_stage("website_navigation", "Website Navigation", t_nav_start, t_nav_end, url=self.base_url)

        # 1. Check Login Flow if authentication required
        if self.requires_login and self.username and self.password:
            try:
                page_text = await page.inner_text("body")
                is_logged_in = "welcome," in page_text.lower() or "my desk" in page_text.lower()
            except Exception:
                is_logged_in = False

            if not is_logged_in and ("login" in page.url.lower() or "usermanagementservices" in page.url.lower()):
                logger.info(f"[{self.county_name}] Authenticating user session...")
                email_field = page.locator("input[type='email'], input[name*='Email' i], input#txtUserName, input[name*='UserName' i]")
                pwd_field = page.locator("input[type='password'], input[name*='Password' i], input#txtPassword")

                if await email_field.count() > 0:
                    await self.biometric_fill(email_field.first, self.username)
                if await pwd_field.count() > 0:
                    await self.biometric_fill(pwd_field.first, self.password)

                login_btn = page.locator("#btnLogin, button:has-text('LOGIN'), input[type='submit'][value*='Login' i]")
                if await login_btn.count() > 0:
                    await login_btn.first.click()
                    await page.wait_for_timeout(2500)

                if "usermanagementservices" in page.url:
                    await page.goto(self.base_url, wait_until="domcontentloaded")
                    await page.wait_for_timeout(1500)

        # 2. Select Person's Name Radio
        t_fill_start = datetime.now()
        person_radio = page.locator("input#rdoPerson, input[type='radio'][value='Person'], label:has-text(\"Person's Name\")")
        if await person_radio.count() > 0:
            try:
                await person_radio.first.click(timeout=3000)
            except Exception:
                pass

        # 3. Fill Party Name & Date inputs
        last_input = page.locator("#txtLastName, input[name='txtLastName'], input[name*='LastName']")
        first_input = page.locator("#txtFirstName, input[name='txtFirstName'], input[name*='FirstName']")

        await last_input.first.wait_for(state="visible", timeout=15000)
        await self.biometric_fill(last_input.first, l_name)
        if f_name and await first_input.count() > 0:
            await self.biometric_fill(first_input.first, f_name)

        # Date of Loss conversion to MM-dd-yyyy matching V4
        if date_of_loss:
            try:
                # Convert MM/DD/YYYY to MM-dd-yyyy
                parts = date_of_loss.replace("/", "-").split("-")
                if len(parts) == 3:
                    if len(parts[0]) == 4:  # YYYY-MM-DD
                        dol_clean = f"{parts[1]}-{parts[2]}-{parts[0]}"
                    else:  # MM-DD-YYYY
                        dol_clean = f"{parts[0]}-{parts[1]}-{parts[2]}"
                else:
                    dol_clean = date_of_loss
            except Exception:
                dol_clean = (datetime.now() - timedelta(days=730)).strftime("%m-%d-%Y")
        else:
            dol_clean = (datetime.now() - timedelta(days=730)).strftime("%m-%d-%Y")

        date_from_input = page.locator("#filingDateFrom, input[name='filingDateFrom'], input[placeholder*='MM-DD-YYYY']")
        if await date_from_input.count() > 0:
            await self.biometric_fill(date_from_input.first, dol_clean)
            logger.info(f"[{self.county_name}] Filled filingDateFrom with DOL: {dol_clean}")

        date_to_input = page.locator("#filingDateTo, input[name='filingDateTo']")
        if await date_to_input.count() > 0:
            today_str = datetime.now().strftime("%m-%d-%Y")
            await self.biometric_fill(date_to_input.first, today_str)

        await page.wait_for_timeout(500)
        t_fill_end = datetime.now()
        self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_end, party=f"{f_name} {l_name}", dol=dol_clean)

        # 4. CAPTCHA verification if triggered
        t_cap_start = datetime.now()
        await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
        t_cap_end = datetime.now()
        self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_end)

        # 5. Submit Search (#btnSearch)
        t_sub_start = datetime.now()
        search_btn = page.locator("#btnSearch, input[type='submit'][value*='Search' i], button:has-text('SEARCH')")
        if await search_btn.count() > 0:
            await search_btn.first.click()
            await page.wait_for_timeout(3500)
        t_sub_end = datetime.now()
        self.record_stage("submit", "Search Submit", t_sub_start, t_sub_end)

        # 6. Extract Card View Results matching V4 — with pagination (GAP-016)
        t_ext_start = datetime.now()
        seen_case_numbers_miami: set = set()

        # GAP-003: Explicit ordered label_map to fix Python operator-precedence issues
        _LABEL_MAP = [
            ("LOCAL CASE NUMBER", "case_number"),
            ("STATE CASE NUMBER", "case_number_alt"),
            ("CASE STYLE", "case_style"),
            ("STYLE", "case_style"),
            ("FILING DATE", "filing_date"),
            ("FILED DATE", "filing_date"),
            ("CASE STATUS", "case_status"),
            ("STATUS", "case_status"),
            ("CASE TYPE", "case_type"),
            ("TYPE", "case_type"),
            ("SECTION", "court"),
            ("COURT", "court"),
        ]

        def _parse_card(card_text: str) -> dict:
            lines = [ln.strip() for ln in card_text.split("\n") if ln.strip()]
            parsed: dict = {
                "case_number": "",
                "case_number_alt": "",
                "case_style": "",
                "filing_date": "",
                "case_status": "",
                "case_type": "",
                "court": "",
            }
            for idx, line in enumerate(lines):
                line_upper = line.upper()
                for label_key, field_key in _LABEL_MAP:
                    if label_key in line_upper and not parsed.get(field_key):
                        if idx + 1 < len(lines):
                            parsed[field_key] = lines[idx + 1]
                        break
            # Use STATE CASE NUMBER as fallback if LOCAL CASE NUMBER not found
            if not parsed["case_number"] and parsed["case_number_alt"]:
                parsed["case_number"] = parsed["case_number_alt"]
            if not parsed["case_style"] and lines:
                parsed["case_style"] = lines[0]
            return parsed

        # GAP-016: Paginate via Load More button or Next pagination control
        page_num_miami = 1
        while True:
            cards = page.locator(".card-body, .case-card, div.card, div[class*='result']")
            card_count = await cards.count()
            logger.info(f"[{self.county_name}] Page {page_num_miami}: Found {card_count} result cards")

            for i in range(card_count):
                card = cards.nth(i)
                card_text = await card.inner_text()
                if not card_text.strip():
                    continue
                parsed = _parse_card(card_text)
                case_number = parsed["case_number"]
                if case_number and case_number not in seen_case_numbers_miami:
                    seen_case_numbers_miami.add(case_number)
                    # GAP-002: FilingDate fallback is "" — never fabricate today's date
                    results.append({
                        "CaseNumber": case_number,
                        "CaseStyle": parsed["case_style"] or f"{l_name}, {f_name}",
                        "CountyWebsite": self.base_url,
                        "FilingDate": parsed["filing_date"] or "",
                        "CaseStatus": parsed["case_status"] or "OPEN",
                        "CaseType": parsed["case_type"] or "CIVIL",
                        "Court": parsed["court"],
                    })

            # Check for Load More or Next pagination control
            load_more = page.locator(
                "button:has-text('Load More'), a:has-text('Load More'), "
                "button:has-text('Next'), .pagination a:has-text('Next'):not(.disabled)"
            )
            if await load_more.count() > 0 and await load_more.first.is_visible():
                try:
                    await load_more.first.click()
                    await page.wait_for_timeout(2500)
                    page_num_miami += 1
                    if page_num_miami > 10:
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
