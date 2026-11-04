"""Capture screenshot of the Ordered Pending Queue component on http://localhost:3000."""
import os

from playwright.sync_api import sync_playwright


def main():
    os.makedirs("docs/images", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        print("Navigating to http://localhost:3000...")
        page.goto("http://localhost:3000", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(4000)
        
        # Locate the Ordered Pending Queue card
        queue_header = page.get_by_text("Ordered Pending Queue (FIFO Priority)")
        if queue_header.count() > 0:
            print("Found Ordered Pending Queue section!")
            # Take screenshot of the entire fleet & queue grid area
            card = page.locator("div.lg\\:col-span-7").first
            screenshot_path = "docs/images/pending_queue_top_aligned.png"
            card.screenshot(path=screenshot_path)
            print(f"Saved card screenshot to {screenshot_path}")
            
            # Also save to docs/ directly for reference
            card.screenshot(path="docs/pending_queue_top_aligned.png")
            print("Saved card screenshot to docs/pending_queue_top_aligned.png")
        else:
            print("Warning: Could not locate Ordered Pending Queue text, taking full page screenshot")
            page.screenshot(path="docs/images/dashboard_full.png")
            
        browser.close()

if __name__ == "__main__":
    main()
