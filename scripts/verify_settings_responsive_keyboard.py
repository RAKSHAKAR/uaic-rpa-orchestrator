"""Read-only responsive and keyboard-focus check for the local Settings page."""

import json
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "implementation_plan" / "Images"
REPORT = ROOT / "implementation_plan" / "2026-10-01_uaic_settings_responsive_keyboard_qa.json"
URL = "http://localhost:3000/settings"
VIEWS = (
    ("tablet_portrait", 768, 1024, "light"),
    ("tablet_landscape", 1024, 768, "dark"),
    ("mobile_landscape", 844, 390, "dark"),
)


def focus_by_keyboard(page, locator) -> dict:
    """Seed focus, then use the keyboard to leave and return to the control."""
    locator.scroll_into_view_if_needed()
    locator.focus()
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Tab")
    return locator.evaluate(
        """el => {
            const style = getComputedStyle(el);
            const box = el.getBoundingClientRect();
            const center = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
            return {
                active: document.activeElement === el,
                focus_visible: el.matches(':focus-visible'),
                outline_style: style.outlineStyle,
                outline_width: style.outlineWidth,
                box_shadow: style.boxShadow,
                center_unobscured: center === el || el.contains(center),
                box: {left: box.left, top: box.top, right: box.right, bottom: box.bottom},
            };
        }"""
    )


def inspect(browser, name: str, width: int, height: int, theme: str) -> dict:
    context = browser.new_context(
        viewport={"width": width, "height": height},
        is_mobile=True,
        has_touch=True,
        device_scale_factor=1,
    )
    context.add_init_script(f"localStorage.setItem('uaic_theme', {json.dumps(theme)})")
    page = context.new_page()
    errors: list[str] = []
    failed_responses: list[dict] = []
    failed_requests: list[dict] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
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
    page.get_by_text("Loading dynamic system settings...").wait_for(state="hidden", timeout=30000)
    page.get_by_text("Browser Automation & Fleet", exact=True).click()
    captcha = page.get_by_label("CAPTCHA Resolution Wait", exact=True)
    captcha.wait_for(state="visible", timeout=10000)
    save = page.get_by_role("button", name="Save Configuration", exact=True)

    IMAGES.mkdir(parents=True, exist_ok=True)
    initial_path = IMAGES / f"IMP-2026-1001-002_settings_{name}_{theme}.png"
    page.screenshot(path=str(initial_path))
    captcha_focus = focus_by_keyboard(page, captcha)
    captcha_path = IMAGES / f"IMP-2026-1001-002_settings_{name}_{theme}_captcha_focus.png"
    page.screenshot(path=str(captcha_path))
    save_focus = focus_by_keyboard(page, save)
    save_path = IMAGES / f"IMP-2026-1001-002_settings_{name}_{theme}_save_focus.png"
    page.screenshot(path=str(save_path))

    result = {
        "viewport": name,
        "width": width,
        "height": height,
        "theme": theme,
        "theme_applied": page.evaluate("document.documentElement.classList.contains(" + json.dumps(theme) + ")"),
        "captcha_wait_seconds": int(captcha.input_value()),
        "horizontal_overflow_px": page.evaluate("Math.max(0, document.documentElement.scrollWidth - innerWidth)"),
        "captcha_focus": captcha_focus,
        "save_focus": save_focus,
        "console_errors": errors,
        "failed_local_responses": failed_responses,
        "failed_requests": failed_requests,
        "screenshots": [str(initial_path), str(captcha_path), str(save_path)],
    }
    context.close()
    if (
        not result["theme_applied"]
        or result["captcha_wait_seconds"] != 120
        or result["horizontal_overflow_px"]
        or errors
        or failed_responses
        or failed_requests
        or not all(
            focus["active"] and focus["focus_visible"] and focus["center_unobscured"]
            for focus in (captcha_focus, save_focus)
        )
    ):
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def main() -> None:
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
        except PlaywrightError:
            browser = playwright.chromium.launch(headless=True)
        try:
            results = [inspect(browser, *view) for view in VIEWS]
            REPORT.write_text(json.dumps(results, indent=2), encoding="utf-8")
            print(json.dumps({
                "passed": True,
                "report": str(REPORT.relative_to(ROOT)),
                "views": [
                    {
                        "viewport": row["viewport"],
                        "horizontal_overflow_px": row["horizontal_overflow_px"],
                        "captcha_focus_visible": row["captcha_focus"]["focus_visible"],
                        "save_focus_visible": row["save_focus"]["focus_visible"],
                        "console_errors": len(row["console_errors"]),
                        "failed_local_responses": len(row["failed_local_responses"]),
                        "failed_requests": len(row["failed_requests"]),
                    }
                    for row in results
                ],
            }, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
