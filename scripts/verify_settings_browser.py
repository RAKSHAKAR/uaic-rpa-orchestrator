"""Read-only desktop/mobile browser check for the live Settings page."""

import json
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "implementation_plan" / "Images"
URL = "http://localhost:3000/settings"


def inspect_page(browser, *, mobile: bool, theme: str) -> dict:
    label = "mobile" if mobile else "desktop"
    context = browser.new_context(
        viewport={"width": 390 if mobile else 1440, "height": 844 if mobile else 900},
        is_mobile=mobile,
        device_scale_factor=1,
    )
    context.add_init_script(f"localStorage.setItem('uaic_theme', {json.dumps(theme)})")
    page = context.new_page()
    errors = []
    failed_responses = []
    failed_requests = []
    page.on("pageerror", lambda error: errors.append({"error": str(error), "stack": error.stack}))
    page.on(
        "console",
        lambda message: errors.append({"error": message.text, "location": message.location})
        if message.type == "error"
        else None,
    )
    page.on(
        "response",
        lambda response: failed_responses.append({"status": response.status, "url": response.url})
        if response.status >= 400 and ("localhost:3000" in response.url or "localhost:8000" in response.url)
        else None,
    )
    page.on(
        "requestfailed",
        lambda request: failed_requests.append({"url": request.url, "failure": request.failure})
        if not (request.failure == "net::ERR_ABORTED" and "_rsc=" in request.url)
        else None,
    )
    page.goto(URL, wait_until="domcontentloaded", timeout=30000)
    page.locator("body").wait_for(state="attached", timeout=15000)
    try:
        page.get_by_text("Loading dynamic system settings...").wait_for(state="hidden", timeout=30000)
    except PlaywrightTimeout:
        raise RuntimeError(json.dumps({
            "phase": "settings load",
            "theme": theme,
            "viewport": label,
            "console_errors": errors,
            "failed_responses": failed_responses,
            "failed_requests": failed_requests,
            "title": page.title(),
            "body_excerpt": page.locator("body").inner_text()[:500],
            "script_urls": page.locator("script[src]").evaluate_all("nodes => nodes.map(node => node.src)"),
        })) from None
    page.get_by_text("Browser Automation & Fleet", exact=True).click()
    page.get_by_text("CAPTCHA Resolution Wait", exact=False).first.wait_for(timeout=10000)
    captcha_wait = page.get_by_label("CAPTCHA Resolution Wait", exact=True)
    captcha_wait_value = int(captcha_wait.input_value())
    slider_bounds = {}
    for field_id in ("typing-delay-ms", "action-pacing-ms"):
        slider_bounds[field_id] = page.locator(f"#{field_id}").evaluate(
            "node => ({min: node.min, max: node.max, step: node.step})"
        )
    page.get_by_text("APIs & Matching Engine", exact=True).click()
    for field_id in ("auto-match-threshold", "manual-review-threshold"):
        slider_bounds[field_id] = page.locator(f"#{field_id}").evaluate(
            "node => ({min: node.min, max: node.max, step: node.step})"
        )
    page.get_by_text("Browser Automation & Fleet", exact=True).click()
    IMAGES.mkdir(parents=True, exist_ok=True)
    screenshot = IMAGES / f"IMP-2026-1001-002_settings_{label}_{theme}.png"
    page.screenshot(path=str(screenshot))
    captcha_wait.scroll_into_view_if_needed()
    field_screenshot = IMAGES / f"IMP-2026-1001-002_settings_{label}_{theme}_captcha.png"
    page.screenshot(path=str(field_screenshot))
    page.get_by_text("Mouse Simulation", exact=True).scroll_into_view_if_needed()
    mouse_copy_screenshot = IMAGES / f"IMP-2026-1001-002_settings_{label}_{theme}_mouse_copy.png"
    page.screenshot(path=str(mouse_copy_screenshot))
    body_text = page.locator("body").inner_text()
    result = {
        "viewport": label,
        "theme": theme,
        "theme_applied": page.evaluate("document.documentElement.classList.contains(" + json.dumps(theme) + ")"),
        "url": page.url,
        "title": page.title(),
        "headings": page.locator("h1, h2").all_text_contents()[:20],
        "body_has_browser_settings": "Browser Automation" in body_text,
        "body_has_captcha_wait": "CAPTCHA Resolution Wait" in body_text,
        "mouse_simulation_copy": (
            "Mouse Simulation" in body_text
            and "Adds randomized mouse movement and brief pauses before supported portal clicks." in body_text
            and "bezier curves" not in body_text.lower()
            and "Anti-Bot Evasion" not in body_text
        ),
        "captcha_wait_seconds": captcha_wait_value,
        "slider_bounds": slider_bounds,
        "horizontal_overflow_px": page.evaluate("Math.max(0, document.documentElement.scrollWidth - innerWidth)"),
        "console_errors": errors,
        "failed_responses": failed_responses,
        "failed_requests": failed_requests,
        "screenshot": str(screenshot),
        "field_screenshot": str(field_screenshot),
        "mouse_copy_screenshot": str(mouse_copy_screenshot),
    }
    if (
        not result["theme_applied"]
        or not result["body_has_browser_settings"]
        or not result["body_has_captcha_wait"]
        or not result["mouse_simulation_copy"]
        or captcha_wait_value < 5
        or slider_bounds != {
            "typing-delay-ms": {"min": "0", "max": "200", "step": "1"},
            "action-pacing-ms": {"min": "0", "max": "1500", "step": "1"},
            "auto-match-threshold": {"min": "0", "max": "1", "step": "0.01"},
            "manual-review-threshold": {"min": "0", "max": "1", "step": "0.01"},
        }
        or result["horizontal_overflow_px"]
        or errors
        or failed_responses
        or failed_requests
    ):
        raise RuntimeError(json.dumps(result))
    context.close()
    return result


def main() -> None:
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
        except PlaywrightError:
            browser = playwright.chromium.launch(headless=True)
        try:
            results = [
                inspect_page(browser, mobile=mobile, theme=theme)
                for theme in ("light", "dark")
                for mobile in (False, True)
            ]
            print(json.dumps(results, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
