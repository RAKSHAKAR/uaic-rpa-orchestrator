"""Read-only browser QA of every visible Settings tab in two representative views."""

import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "implementation_plan" / "Images"
REPORT = ROOT / "implementation_plan" / "2026-10-01_uaic_settings_all_tabs_browser_qa.json"
URL = "http://localhost:3000/settings"
TABS = (
    ("guidewire", "APIs & Matching Engine"),
    ("portals", "County Court Portals"),
    ("automation", "Browser Automation & Fleet"),
    ("proxy", "Proxy Network"),
    ("email", "Email & Notifications"),
    ("storage", "Storage & Retention"),
    ("queue", "Task Queue & Telemetry"),
)


def inspect_view(browser, *, mobile: bool, theme: str) -> dict:
    viewport = "mobile" if mobile else "desktop"
    context = browser.new_context(
        viewport={"width": 390 if mobile else 1440, "height": 844 if mobile else 900},
        is_mobile=mobile,
        device_scale_factor=1,
    )
    context.add_init_script(f"localStorage.setItem('uaic_theme', {json.dumps(theme)})")
    page = context.new_page()
    errors: list[dict] = []
    failed_local_responses: list[dict] = []
    failed_local_requests: list[dict] = []
    page.on("pageerror", lambda error: errors.append({"type": "pageerror", "message": str(error)}))
    page.on(
        "console",
        lambda message: errors.append({"type": "console", "message": message.text})
        if message.type == "error"
        else None,
    )
    page.on(
        "response",
        lambda response: failed_local_responses.append({"status": response.status, "url": response.url})
        if response.status >= 400 and ("localhost:3000" in response.url or "localhost:8000" in response.url)
        else None,
    )
    page.on(
        "requestfailed",
        lambda request: failed_local_requests.append({"url": request.url, "failure": request.failure})
        if ("localhost:3000" in request.url or "localhost:8000" in request.url)
        and not (request.failure == "net::ERR_ABORTED" and "_rsc=" in request.url)
        else None,
    )
    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=30_000)
        page.get_by_text("Loading dynamic system settings...").wait_for(state="hidden", timeout=30_000)
        view = {
            "viewport": viewport,
            "theme": theme,
            "theme_applied": page.evaluate("document.documentElement.classList.contains(" + json.dumps(theme) + ")"),
            "tabs": [],
        }
        for tab_id, label in TABS:
            button = page.get_by_role("button", name=label, exact=True)
            button.click()
            page.wait_for_timeout(700)
            headings = [heading.strip() for heading in page.locator("main h3").all_text_contents()]
            selected = button.evaluate("node => node.className.includes('border-indigo-600')")
            first_heading = page.locator("main h3").first
            first_heading.scroll_into_view_if_needed()
            heading_unobscured = first_heading.evaluate("""node => {
                const rect = node.getBoundingClientRect();
                const target = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
                return target !== null && (node === target || node.contains(target));
            }""")
            overflow = page.evaluate("Math.max(0, document.documentElement.scrollWidth - innerWidth)")
            screenshot = IMAGES / f"IMP-2026-1001-002_settings_tab_{tab_id}_{viewport}_{theme}.png"
            page.screenshot(path=str(screenshot))
            view["tabs"].append({
                "tab": tab_id,
                "label": label,
                "selected": selected,
                "first_heading_unobscured": heading_unobscured,
                "heading_count": len(headings),
                "headings": headings[:4],
                "content_chars": len(page.locator("main").inner_text()),
                "horizontal_overflow_px": overflow,
                "screenshot": str(screenshot.relative_to(ROOT)),
            })
        view["console_errors"] = errors
        view["failed_local_responses"] = failed_local_responses
        view["failed_local_requests"] = failed_local_requests
        view["passed"] = (
            view["theme_applied"]
            and not errors
            and not failed_local_responses
            and not failed_local_requests
            and all(tab["selected"] and tab["first_heading_unobscured"]
                    and tab["heading_count"] > 0 and tab["content_chars"] > 300
                    and tab["horizontal_overflow_px"] == 0 for tab in view["tabs"])
        )
        return view
    finally:
        context.close()


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
        except PlaywrightError:
            browser = playwright.chromium.launch(headless=True)
        try:
            views = [
                inspect_view(browser, mobile=False, theme="light"),
                inspect_view(browser, mobile=True, theme="dark"),
            ]
        finally:
            browser.close()
    report = {
        "implementation_id": "IMP-2026-1001-002",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "url": URL,
        "read_only": True,
        "views": views,
        "passed": all(view["passed"] for view in views),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": report["passed"],
        "report": str(REPORT.relative_to(ROOT)),
        "views": [{
            "viewport": view["viewport"],
            "theme": view["theme"],
            "tabs_passed": sum(tab["selected"] and tab["horizontal_overflow_px"] == 0 for tab in view["tabs"]),
            "tabs_total": len(view["tabs"]),
            "console_errors": len(view["console_errors"]),
            "failed_local_responses": len(view["failed_local_responses"]),
            "failed_local_requests": len(view["failed_local_requests"]),
        } for view in views],
    }, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
