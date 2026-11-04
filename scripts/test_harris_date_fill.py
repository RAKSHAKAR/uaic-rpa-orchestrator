import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.automation.browser_manager import ChromeSession
from app.automation.texas.harris_district import HarrisDistrictClerkScraper, _date_for_input


async def main():
    s = ChromeSession(browser_engine="chromium", headless=True)
    scraper = HarrisDistrictClerkScraper()
    try:
        ctx = await s.start()
        p = await ctx.new_page()
        await p.goto("https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3)
        
        # Click Party Inquiry tab
        party_tab = p.locator("input#tabParty, input[value*='Party Inquiry'], #tabParty")
        if await party_tab.count() > 0 and await party_tab.first.is_visible():
            await party_tab.first.click()
            await asyncio.sleep(1)

        start_input = p.locator("#txtPartyStartDate")
        end_input = p.locator("#txtPartyEndDate")
        await start_input.wait_for(state="visible", timeout=10000)

        # Fill start date with DOL
        clean_dol = "02/03/2022"
        dol_type = await start_input.get_attribute("type")
        formatted_dol = _date_for_input(clean_dol, dol_type)
        print(f"formatted_dol for type={dol_type}: {formatted_dol}")
        await scraper.biometric_fill(start_input, formatted_dol)
        
        # Fill end date with Today
        today_str = datetime.now().strftime("%m/%d/%Y")
        end_type = await end_input.get_attribute("type")
        formatted_end = _date_for_input(today_str, end_type)
        print(f"formatted_end for type={end_type}: {formatted_end}")
        await scraper.biometric_fill(end_input, formatted_end)

        val_start = await start_input.input_value()
        val_end = await end_input.input_value()
        print(f"Resulting start input value: {val_start}")
        print(f"Resulting end input value: {val_end}")

    finally:
        await s.close()

if __name__ == "__main__":
    asyncio.run(main())
