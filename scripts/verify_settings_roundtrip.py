"""Exercise the live CAPTCHA wait Settings control and restore its original value."""

import json

import httpx
from playwright.sync_api import sync_playwright


API = "http://localhost:8000/api/v1/settings"
PAGE = "http://localhost:3000/settings"


def current(client: httpx.Client) -> dict:
    response = client.get(API)
    response.raise_for_status()
    return response.json()


def set_in_browser(page, value: int) -> None:
    page.locator("#captcha-resolution-wait").fill(str(value))
    page.get_by_role("button", name="Save Configuration").click()
    page.get_by_text("Settings saved as revision", exact=False).wait_for(timeout=20000)


def main() -> None:
    with httpx.Client(timeout=30) as client:
        original = current(client)
        original_wait = original["automation"]["captcha_wait_seconds"]
        alternate = original_wait + 1 if original_wait < 300 else original_wait - 1
        changed = False
        result = {"original_wait": original_wait, "alternate_wait": alternate}
        console_errors = []
        failed_responses = []
        failed_requests = []
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
                try:
                    page = browser.new_page()
                    page.on("pageerror", lambda error: console_errors.append(str(error)))
                    page.on(
                        "console",
                        lambda message: console_errors.append(message.text)
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
                    page.goto(PAGE, wait_until="domcontentloaded", timeout=30000)
                    page.get_by_text("Loading dynamic system settings...").wait_for(state="hidden", timeout=30000)
                    page.get_by_text("Browser Automation & Fleet", exact=True).click()
                    page.locator("#captcha-resolution-wait").wait_for(timeout=10000)
                    assert int(page.locator("#captcha-resolution-wait").input_value()) == original_wait
                    changed = True
                    set_in_browser(page, alternate)
                    after_save = current(client)
                    assert after_save["automation"]["captcha_wait_seconds"] == alternate
                    page.reload(wait_until="domcontentloaded")
                    page.get_by_text("Loading dynamic system settings...").wait_for(state="hidden", timeout=30000)
                    page.get_by_text("Browser Automation & Fleet", exact=True).click()
                    assert int(page.locator("#captcha-resolution-wait").input_value()) == alternate
                    result["browser_reload_reflected_saved_value"] = True
                    set_in_browser(page, original_wait)
                    changed = False
                    restored = current(client)
                    assert restored["automation"]["captcha_wait_seconds"] == original_wait
                    result["restored_wait"] = original_wait
                    result["revision_delta"] = restored["version"] - original["version"]
                    result["console_errors"] = console_errors
                    result["failed_responses"] = failed_responses
                    result["failed_requests"] = failed_requests
                    assert not console_errors and not failed_responses and not failed_requests, result
                finally:
                    browser.close()
        finally:
            if changed:
                latest = current(client)
                latest["automation"]["captcha_wait_seconds"] = original_wait
                latest.pop("configured_secrets", None)
                restored_response = client.post(API, json=latest)
                restored_response.raise_for_status()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
