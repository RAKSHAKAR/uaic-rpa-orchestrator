"""Inspect the live Hillsborough V4 search button and result transition."""

import asyncio
import json
import shutil
import tempfile
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = (ROOT / "backend" / "data").resolve()
SEARCH_URL = "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"


async def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="hills_submit_diag_", dir=DATA_DIR)).resolve()
    if not profile.is_relative_to(DATA_DIR):
        raise RuntimeError("Diagnostic profile is outside backend/data")
    observations: dict = {"url": SEARCH_URL, "requests": [], "page_errors": []}
    try:
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile), headless=True, viewport={"width": 1440, "height": 900}
            )
            try:
                page = await context.new_page()
                page.on("request", lambda req: observations["requests"].append(
                    {"method": req.method, "url": req.url[:200]}
                ) if "hillsclerk.com" in req.url and len(observations["requests"]) < 150 else None)
                page.on("pageerror", lambda error: observations["page_errors"].append(str(error)[:300]))
                await page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=45000)
                tab = page.locator("#nav-Party-tab")
                await tab.click(timeout=12000)
                await page.locator("#spFirstName").fill("Audit")
                await page.locator("#spLastName").fill("Zyxqtest")
                await page.locator("#spDateFiledAfter").evaluate("""element => {
                    element.removeAttribute('readonly');
                    element.value = '01/01/2020';
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new Event('blur', { bubbles: true }));
                }""")
                buttons = page.locator("#btnSubmitPartySearch")
                observations["button_count"] = await buttons.count()
                observations["buttons"] = []
                for index in range(await buttons.count()):
                    button = buttons.nth(index)
                    observations["buttons"].append({
                        "visible": await button.is_visible(),
                        "enabled": await button.is_enabled(),
                        "html": (await button.evaluate("el => el.outerHTML"))[:500],
                    })
                observations["before"] = await page.evaluate("""() => ({
                    url: location.href,
                    formValid: document.querySelector('#spFirstName')?.form?.checkValidity?.(),
                    dialog: document.querySelector('#messageDialog')?.innerText?.slice(0, 500) || '',
                    buttonDisabled: document.querySelector('#btnSubmitPartySearch')?.disabled,
                })""")
                button_box = await buttons.first.bounding_box()
                observations["button_box"] = button_box
                click_x = button_box["x"] + button_box["width"] / 2
                click_y = button_box["y"] + button_box["height"] / 2
                observations["hit_target"] = await page.evaluate(
                    "([x,y]) => document.elementFromPoint(x,y)?.outerHTML?.slice(0,500)",
                    [click_x, click_y],
                )
                request_count = len(observations["requests"])
                await buttons.first.click(timeout=15000)
                await page.wait_for_timeout(15000)
                observations["submit_requests"] = observations["requests"][request_count:]
                observations["after"] = await page.evaluate("""() => ({
                    url: location.href,
                    dialog: document.querySelector('#messageDialog')?.innerText?.slice(0, 500) || '',
                    bodyTail: document.body?.innerText?.slice(-600) || '',
                    noData: Boolean(document.querySelector('td.dataTables_empty')),
                    resultRows: document.querySelectorAll('table.dataTable tbody tr').length,
                    tableText: [...document.querySelectorAll('table.dataTable')].map(el => el.innerText?.slice(0,600)),
                    tableInfo: [...document.querySelectorAll('[id$="_info"]')].map(el => el.innerText?.slice(0,200)),
                    messageCloseVisible: Boolean(document.querySelector('#messageClose')?.getClientRects().length),
                })""")
                screenshot = ROOT / "implementation_plan" / "Images" / "IMP-2026-1001-002_hillsborough_submit_diagnostic.png"
                await page.screenshot(path=str(screenshot), full_page=True)
                observations["screenshot"] = str(screenshot.relative_to(ROOT))
            finally:
                await context.close()
    finally:
        if profile.is_relative_to(DATA_DIR) and profile.exists():
            shutil.rmtree(profile)
    print(json.dumps(observations, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
