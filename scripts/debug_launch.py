import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.on("console", lambda msg: print("BROWSER CONSOLE:", msg.type, msg.text, flush=True))
    page.on("request", lambda req: print("REQ:", req.method, req.url, flush=True) if "api/v1" in req.url else None)
    page.on("response", lambda res: print("RES:", res.status, res.url, flush=True) if "api/v1" in res.url else None)
    
    print("Navigating to http://localhost:3000/settings...", flush=True)
    page.goto("http://localhost:3000/settings")
    tab_btn = page.locator("button:has-text('Browser Automation')").first
    tab_btn.wait_for(timeout=10000)
    tab_btn.click()
    page.wait_for_timeout(1000)
    
    print("Finding Launch button...", flush=True)
    btn = page.locator("button.bg-purple-600:has-text('Launch')").first
    print("Button text:", btn.text_content().strip(), flush=True)
    btn.click()
    print("Clicked! Waiting up to 60s...", flush=True)
    found = False
    for i in range(60):
        time.sleep(1)
        res_elem = page.locator("text=Live Launch Verified Successfully")
        if res_elem.is_visible():
            print("Found success result banner!", res_elem.text_content(), flush=True)
            found = True
            break
        fail_elem = page.locator("text=Live Launch Verification Failed")
        if fail_elem.is_visible():
            print("Found failure result banner!", fail_elem.text_content(), flush=True)
            found = True
            break
        if i % 5 == 0:
            print(f"Waiting... {i}s", flush=True)
            
    if not found:
        print("Timeout reached without result banner.", flush=True)
    browser.close()
