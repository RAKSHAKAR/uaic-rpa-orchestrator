import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir="backend/data/browser_profile/policy_dump",
            headless=True,
            channel="chrome",
        )
        page = await ctx.new_page()
        await page.goto("chrome://policy", wait_until="networkidle")
        
        # Get all policy elements
        policies = await page.evaluate('''() => {
            const res = [];
            document.querySelectorAll('fieldset').forEach(fs => {
                const legend = fs.querySelector('legend')?.innerText;
                const rows = [];
                fs.querySelectorAll('.policy-table tbody tr').forEach(tr => {
                    const name = tr.querySelector('.name')?.innerText;
                    const value = tr.querySelector('.value')?.innerText;
                    const status = tr.querySelector('.status')?.innerText;
                    if (name) rows.push({name, value, status});
                });
                res.push({section: legend, rows});
            });
            return res;
        }''')
        import pprint
        pprint.pprint(policies)
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
