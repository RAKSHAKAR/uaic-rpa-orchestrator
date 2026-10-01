import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def test_solve():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    backend_dir = repo_root / "backend"
    ext_path = str(repo_root / "anticaptcha-plugin_v0.83")
    profile_path = str(backend_dir / "data" / "browser_profile" / "chromium")
    
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
            ],
            ignore_default_args=["--disable-extensions"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        print("Navigating to Cloudflare Turnstile demo page...")
        await page.goto("https://2captcha.com/demo/cloudflare-turnstile", wait_until="domcontentloaded")
        
        for i in range(25):
            await asyncio.sleep(1)
            status = await page.evaluate("""() => {
                const el = document.querySelector('.antigate_solver, .antigate_solver_solved');
                const token = document.querySelector('input[name="cf-turnstile-response"]');
                return {
                    text: el ? el.innerText.trim() : 'none',
                    solved: el ? el.classList.contains('antigate_solver_solved') : false,
                    hasToken: token ? token.value.length > 20 : false
                };
            }""")
            print(f"Second {i+1}: {status}")
            if status.get("solved") or status.get("hasToken"):
                print("CAPTCHA Solved successfully! Capturing screenshot...")
                target_img = repo_root / "implementation_plan" / "Images" / "anticaptcha_turnstile_solved.png"
                await page.screenshot(path=str(target_img))
                print(f"Saved: {target_img}")
                break
        await ctx.close()


if __name__ == "__main__":
    asyncio.run(test_solve())
