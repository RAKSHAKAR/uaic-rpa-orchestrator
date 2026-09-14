"""
Browser Smoke Test Script
Validates that the selected browser (Chromium, Chrome, or Edge) can launch,
load the Anti-Captcha extension, and interact with the DOM.
"""
import os
import sys

from playwright.sync_api import sync_playwright


def main():
    channel = os.getenv("PLAYWRIGHT_CHANNEL", "chromium")
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() in ("true", "1")
    extension_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../anticaptcha-plugin_v0.83"))

    if not os.path.exists(extension_path):
        print(f"ERROR: Anti-Captcha extension not found at {extension_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Launching smoke test for browser channel: {channel} (Headless: {headless})")

    # Anti-Captcha requires headed mode (or new headless mode in chromium, but better keep it headed for smoke testing if not explicitly unattended)
    args = [
        f"--disable-extensions-except={extension_path}",
        f"--load-extension={extension_path}"
    ]
    if headless:
        args.append("--headless=new")

    try:
        with sync_playwright() as p:
            browser_context = p.chromium.launch_persistent_context(
                user_data_dir="",
                channel=channel if channel in ("chrome", "msedge") else None,
                headless=headless,
                args=args,
                no_viewport=True,
            )
            
            page = browser_context.pages[0]
            page.goto("https://example.com", timeout=15000)
            
            # Simple DOM validation
            title = page.title()
            if "Example Domain" not in title:
                raise Exception(f"Unexpected page title: {title}")
                
            print("Smoke test passed: Browser launched and DOM loaded successfully.")
            browser_context.close()
            sys.exit(0)
    except Exception as e:
        print(f"Smoke test failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
