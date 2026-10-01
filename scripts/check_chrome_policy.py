import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(Path("backend/data/browser_profile/policy_test").resolve()),
            headless=False,
            channel="chrome",
        )
        page = await ctx.new_page()
        await page.goto("chrome://policy")
        await asyncio.sleep(2)
        
        # Extract policies using document evaluate or text
        content = await page.evaluate("""
        () => {
            const res = {};
            const rows = document.querySelectorAll('.policy-table tr');
            rows.forEach(r => {
                const name = r.querySelector('.name');
                const val = r.querySelector('.value');
                if (name && val) {
                    res[name.innerText.trim()] = val.innerText.trim();
                }
            });
            return res;
        }
        """)
        print("POLICIES FOUND IN CHROME:")
        for k, v in content.items():
            print(f" - {k}: {v}")

        await page.screenshot(path="implementation_plan/Images/chrome_policy_screenshot.png")
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
