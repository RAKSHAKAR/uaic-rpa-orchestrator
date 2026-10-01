import asyncio
import os
import json
from datetime import datetime
import sys
sys.stdout.reconfigure(line_buffering=True)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.automation.florida.broward import BrowardScraper
from app.automation.florida.hillsborough import HillsboroughScraper
from app.automation.florida.miami import MiamiDadeScraper
from app.automation.texas.dallas import DallasScraper
from app.automation.texas.travis import TravisScraper
from app.automation.texas.harris_jp import HarrisJPScraper
from app.automation.texas.harris_district import HarrisDistrictClerkScraper
from app.automation.texas.harris_cclerk import HarrisCountyClerkScraper
from app.automation.session_runner import SingleSessionBrowserRunner
from app.services.settings_service import get_system_settings_async

class MockClaim:
    def __init__(self):
        self.id = "MOCK-12345"
        self.claim_number = "TEST-12345"
        self.insured_first_name = "JOHN"
        self.insured_last_name = "SMITH"
        self.claimant_first_name = "JOHN"
        self.claimant_last_name = "SMITH"
        self.driver_first_name = "JOHN"
        self.driver_last_name = "SMITH"
        self.date_of_loss = datetime(2020, 1, 1)

async def main():
    sys_settings = await get_system_settings_async()
    auto_cfg = sys_settings.automation
    portals_cfg = sys_settings.portals

    print(f"Loaded AntiCaptcha Key: {'[SET]' if auto_cfg.anticaptcha_api_key else '[NOT SET]'}")
    print(f"Loaded Miami User: {'[SET]' if portals_cfg.miami_username else '[NOT SET]'}")

    scrapers = [
        BrowardScraper(base_url=portals_cfg.broward_url),
        HillsboroughScraper(base_url=portals_cfg.hillsborough_url),
        MiamiDadeScraper(base_url=portals_cfg.miami_url),
        DallasScraper(base_url=portals_cfg.dallas_url),
        TravisScraper(base_url=portals_cfg.travis_url),
        HarrisJPScraper(base_url=portals_cfg.harris_jp_url),
        HarrisDistrictClerkScraper(base_url=portals_cfg.harris_district_url),
        HarrisCountyClerkScraper(base_url=portals_cfg.harris_cclerk_url),
    ]
    
    runner = SingleSessionBrowserRunner(
        headless=True,
        timeout_ms=60000,
        use_chrome=auto_cfg.use_chrome_browser,
        extension_dir=auto_cfg.chrome_extension_dir,
        anticaptcha_api_key=auto_cfg.anticaptcha_api_key,
        anticaptcha_settings=auto_cfg,
        user_data_dir=auto_cfg.chrome_user_data_dir,
        browser_engine="chromium", 
    )
    
    claim = MockClaim()
    results_summary = {}
    
    async with runner as browser_session:
        for scraper in scrapers:
            print(f"\n--- Scraping {scraper.county_name} ---")
            try:
                page = await browser_session.context.new_page()
                
                # Wrap scraper execution with a strict 90 second timeout so it doesn't hang
                results = await asyncio.wait_for(
                    scraper.search_on_page(
                        page=page,
                        first_name="JOHN",
                        last_name="SMITH",
                        date_of_loss="01/01/2020",
                        claim_num="TEST-12345"
                    ),
                    timeout=300.0
                )
                
                results_summary[scraper.county_name] = results
                print(f"Extracted {len(results)} cases for {scraper.county_name}")
                if results:
                    print(json.dumps(results[0], indent=2))
                else:
                    print("No cases found.")
            except asyncio.TimeoutError:
                print(f"Error scraping {scraper.county_name}: Strict 300s Timeout exceeded.")
                results_summary[scraper.county_name] = {"error": "Strict 90s Timeout exceeded"}
            except Exception as e:
                print(f"Error scraping {scraper.county_name}: {e}")
                results_summary[scraper.county_name] = {"error": str(e)}

    print("\n=== FINAL SUMMARY ===")
    for county, res in results_summary.items():
        if isinstance(res, list):
            print(f"{county}: {len(res)} cases found.")
        else:
            print(f"{county}: ERROR - {res}")

if __name__ == "__main__":
    asyncio.run(main())
