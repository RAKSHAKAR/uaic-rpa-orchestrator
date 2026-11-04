"""Add universal check_and_handle_session_timeout to BaseCourtScraper."""

from pathlib import Path

base_path = Path("backend/app/automation/base.py")
text = base_path.read_text(encoding="utf-8")

target = """    async def _dismiss_session_timeout_popup(self, page: Page) -> None:
        \"\"\"Dismiss Odyssey/Smart Search session-timeout warning by clicking Continue (V4 Global Standard §5).\"\"\"
        try:
            continue_btn = page.locator(
                "button:has-text('Continue session'), button:has-text('Continue Session'), "
                "button:has-text('Continue'), a:has-text('Continue session'), "
                "a:has-text('Continue'), input[value*='Continue' i], [aria-label*='Continue' i]"
            )
            if await continue_btn.count() > 0 and await continue_btn.first.is_visible():
                await continue_btn.first.click()
                await page.wait_for_timeout(500)
                logger.info(f"[{self.county_name}] Dismissed session timeout popup.")
        except Exception as e:
            logger.debug(f"[{self.county_name}] Session timeout popup check: {e}")"""

replacement = """    async def _dismiss_session_timeout_popup(self, page: Page) -> None:
        \"\"\"Dismiss Odyssey/Smart Search session-timeout warning by clicking Continue (V4 Global Standard §5).\"\"\"
        await self.check_and_handle_session_timeout(page)

    async def check_and_handle_session_timeout(self, page: Page, *args: Any, **kwargs: Any) -> bool:
        \"\"\"Universal session-timeout detection and recovery for all 8 portal scrapers.\"\"\"
        try:
            continue_btn = page.locator(
                "button:has-text('Continue session'), button:has-text('Continue Session'), "
                "button:has-text('Continue'), a:has-text('Continue session'), "
                "a:has-text('Continue'), input[value*='Continue' i], [aria-label*='Continue' i]"
            )
            if await continue_btn.count() > 0 and await continue_btn.first.is_visible():
                logger.info(f"[{self.county_name}] Session timeout popup detected. Clicking 'Continue session'...")
                await continue_btn.first.click()
                await page.wait_for_timeout(800)
                return True
        except Exception as e:
            logger.debug(f"[{self.county_name}] Session timeout check note: {e}")
        return False"""

if target in text:
    text = text.replace(target, replacement, 1)
    base_path.write_text(text, encoding="utf-8")
    print("SUCCESS: Added check_and_handle_session_timeout to BaseCourtScraper.")
else:
    print("ERROR: Target block not found in base.py")

