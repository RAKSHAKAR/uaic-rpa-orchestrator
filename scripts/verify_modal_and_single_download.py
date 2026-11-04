"""Playwright script to verify AsyncExportModal single download guard and Unified Master Dossier banner."""

from pathlib import Path

from playwright.sync_api import sync_playwright

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)


def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("Navigating to http://localhost:3000/monitor...")
        page.goto("http://localhost:3000/monitor", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # Locate the Async Export button (it has title or button text with download/cloud)
        export_buttons = page.locator("button:has(svg.lucide-download), button[title*='Background']")
        if export_buttons.count() == 0:
            export_buttons = page.locator("button:has-text('Async')")
        
        print(f"Found {export_buttons.count()} export buttons. Clicking background export modal...")
        export_buttons.first.click()
        page.wait_for_timeout(1000)

        # Verify modal elements
        modal = page.locator("div.fixed.inset-0")
        assert modal.is_visible(), "Async export modal did not open"
        print("Async export modal opened successfully.")

        # Capture screenshot 1: Open modal showing Unified Master Dossier and green banner
        screenshot1_path = DOCS_DIR / "unified_master_dossier_modal.png"
        page.screenshot(path=str(screenshot1_path))
        print(f"Captured screenshot: {screenshot1_path.name}")

        # Assert banner text
        banner = page.locator("text='All Data Combined in One Single File'")
        assert banner.is_visible(), "Banner 'All Data Combined in One Single File' is missing"
        print("PASS: Verified 'All Data Combined in One Single File' banner is visible.")

        # Setup download listener to count downloads
        download_count = 0
        downloaded_files = []

        def on_download(download):
            nonlocal download_count
            download_count += 1
            suggested = download.suggested_filename
            downloaded_files.append(suggested)
            print(f"[DOWNLOAD #{download_count}] Triggered: {suggested}")

        page.on("download", on_download)

        # Click Start Background Export
        start_btn = page.locator("button:has-text('Start Background Export')")
        assert start_btn.is_visible(), "Start Background Export button missing"
        print("Clicking 'Start Background Export'...")
        start_btn.click()

        # Wait for export completion (up to 90 seconds)
        print("Waiting for export to complete...")
        page.wait_for_selector("text='Export Complete! Ready for Download'", timeout=90000)
        print("Export completed! Waiting 5 seconds to verify no loop downloads occur...")
        page.wait_for_timeout(5000)

        # Capture screenshot 2: Completed state
        screenshot2_path = DOCS_DIR / "unified_master_dossier_completed.png"
        page.screenshot(path=str(screenshot2_path))
        print(f"Captured completed screenshot: {screenshot2_path.name}")

        print(f"Total downloads captured: {download_count}")
        print(f"Downloaded files: {downloaded_files}")
        assert download_count == 1, f"Expected exactly 1 download, but got {download_count}!"

        print("\n=======================================================")
        print("SUCCESS: EXACTLY 1 FILE DOWNLOADED! NO LOOPING OCCURRED!")
        print("=======================================================")
        browser.close()


if __name__ == "__main__":
    run_verification()
