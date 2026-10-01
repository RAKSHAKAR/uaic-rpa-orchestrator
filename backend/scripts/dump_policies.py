import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        chrome_path = None
        for p_path in [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ]:
            if os.path.exists(p_path):
                chrome_path = p_path
                break
                
        context = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.abspath("test_chrome_profile_policy"),
            executable_path=chrome_path,
            headless=False,
            args=["--test-type"]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("chrome://policy", wait_until="networkidle")
        
        # Get the policy data
        policies = await page.evaluate('''() => {
            const policies = {};
            document.querySelectorAll('.policy-table .policy-row').forEach(row => {
                const name = row.querySelector('.name-column')?.innerText;
                const value = row.querySelector('.value-column')?.innerText;
                if (name && value) policies[name.trim()] = value.trim();
            });
            return policies;
        }''')
        print("POLICIES FOUND:", policies)
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
