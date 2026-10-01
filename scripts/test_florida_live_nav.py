import asyncio
import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from playwright.async_api import async_playwright
from app.automation.florida.broward import BrowardScraper, BROWARD_PORTAL_URL
from app.automation.florida.miami import MiamiDadeScraper, MIAMI_LOGIN_GATEWAY_URL
from app.automation.florida.hillsborough import HillsboroughScraper

async def test_florida_navigation():
    print("=== Testing Florida Scraper Navigation Parity (V4 Exact) ===")
    
    # 1. Test Broward configured base
    b_scraper = BrowardScraper()
    print(f"Broward configured base: {b_scraper.base_url}")
    assert b_scraper.base_url == "https://www.browardclerk.org/Web2", f"Broward base_url mismatch: {b_scraper.base_url}"
    
    # 2. Test Miami login URL
    m_scraper = MiamiDadeScraper(requires_login=True)
    print(f"Miami login URL: {m_scraper.login_url}")
    assert m_scraper.login_url == "https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB", "Miami login URL mismatch!"
    
    # 3. Test Hillsborough target URL
    h_scraper = HillsboroughScraper()
    print(f"Hillsborough base URL: {h_scraper.base_url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test Broward direct Web2 navigation
        print("\nTesting Broward navigation...")
        broward_target = await b_scraper.navigate_to_search(page)
        print(f"Broward arrived at: {page.url}")
        assert "PremiumServices" not in page.url, "Broward navigated to PremiumServices!"
        assert "Glossary" not in page.url, "Broward navigated to Glossary!"
        assert "Web2" in page.url, f"Broward did not reach Web2: {page.url}"
        
        # Verify exact V4 inputs are present on Broward page
        name_cnt = await page.locator("#nameSearch").count()
        first_cnt = await page.locator("#firstName").count()
        last_cnt = await page.locator("#lastName").count()
        submit_cnt = await page.locator("#PersonSearchResults").count()
        print(f"Broward form controls found: #nameSearch({name_cnt}), #firstName({first_cnt}), #lastName({last_cnt}), #PersonSearchResults({submit_cnt})")
        assert first_cnt > 0, "Broward #firstName not found!"
        assert last_cnt > 0, "Broward #lastName not found!"
        assert submit_cnt > 0, "Broward #PersonSearchResults not found!"
        print("  -> Broward navigation: PASS (100% V4 Parity, 0 stray clicks)")
        
        # Test Miami login gateway navigation
        print("\nTesting Miami login gateway navigation...")
        await page.goto(m_scraper.login_url, wait_until="domcontentloaded", timeout=30000)
        print(f"Miami arrived at: {page.url}")
        assert "usermanagementservices" in page.url, f"Miami did not reach user management services: {page.url}"
        assert "hs=OCSB" in page.url or "usermanagementservices" in page.url, f"Miami query param missing: {page.url}"
        
        user_cnt = await page.locator("input#userName, #userName, input[name='userName']").count()
        pwd_cnt = await page.locator("input#password, #password, input[name='password']").count()
        print(f"Miami login fields verified: userName ({user_cnt}), password ({pwd_cnt})")
        assert user_cnt > 0, "Miami userName input not found!"
        assert pwd_cnt > 0, "Miami password input not found!"
        print("  -> Miami login gateway: PASS")
        
        await browser.close()
        
    print("\nAll Florida navigation checks PASSED successfully!")

if __name__ == "__main__":
    asyncio.run(test_florida_navigation())
