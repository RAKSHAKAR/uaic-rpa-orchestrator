from playwright.sync_api import sync_playwright
import os

def main():
    os.makedirs("implementation_plan/Images", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1200})
        
        # Log client console and errors
        page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"[Browser Error] {err}"))
        
        print("Navigating to http://localhost:3000/...")
        page.goto("http://localhost:3000/", wait_until="networkidle")
        
        # Wait a moment for React query / useState rendering
        page.wait_for_timeout(3000)
        
        page.screenshot(path="implementation_plan/Images/06_dashboard_ordered_pending_queue_full.png", full_page=True)
        print("Captured 06_dashboard_ordered_pending_queue_full.png")
        
        # Scroll to live queue section
        page.evaluate("window.scrollTo(0, 320)")
        page.wait_for_timeout(1000)
        page.screenshot(path="implementation_plan/Images/07_dashboard_live_queue_viewport.png")
        print("Captured 07_dashboard_live_queue_viewport.png")
        browser.close()

if __name__ == "__main__":
    main()
