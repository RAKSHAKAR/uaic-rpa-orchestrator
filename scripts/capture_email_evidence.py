import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "implementation_plan", "Images"))
    os.makedirs(images_dir, exist_ok=True)
    
    print(f"Target Images Directory: {images_dir}")
    
    with sync_playwright() as p:
        # Launch Chromium
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        print("Navigating to http://localhost:3000/settings...")
        page.goto("http://localhost:3000/settings", wait_until="networkidle", timeout=30000)
        time.sleep(2)
        
        # Click on "Email & Notifications" tab
        print("Switching to 'Email & Notifications' tab...")
        email_tab = page.locator("button:has-text('Email & Notifications')")
        if email_tab.count() > 0:
            email_tab.first.click()
        else:
            print("Warning: Email & Notifications tab button not found directly, checking sidebar...")
            page.click("text=Email & Notifications")
            
        time.sleep(2)
        
        # 1. AE-005: Switch to Authenticated SMTP Relay and toggle eye icon
        print("Capturing AE-005: Eye icon toggling in Email Settings...")
        # Click on Authenticated SMTP Relay card
        smtp_relay_card = page.locator("text=Authenticated SMTP Relay")
        if smtp_relay_card.count() > 0:
            print("Selecting Authenticated SMTP Relay...")
            smtp_relay_card.first.scroll_into_view_if_needed()
            smtp_relay_card.first.click()
            time.sleep(1)

        # Locate SMTP password input
        pwd_input = page.locator("input[placeholder='••••••••••••']")
        if pwd_input.count() > 0:
            pwd_input.first.fill("SecretAppPassword2026!")
            time.sleep(0.5)

        # Find eye button inside password container
        eye_buttons = page.locator("button:has(svg.lucide-eye, svg.lucide-eye-off)")
        if eye_buttons.count() > 0:
            print("Found eye toggle button, clicking to reveal password...")
            eye_buttons.first.scroll_into_view_if_needed()
            eye_buttons.first.click()
            time.sleep(1)
            
        ae005_path = os.path.join(images_dir, "AE-005_email_settings_eye_icon.png")
        page.screenshot(path=ae005_path, full_page=False)
        print(f"Saved AE-005 screenshot: {ae005_path}")
        
        # 2. AE-010: Test Connection and Send Live Test Email
        print("Triggering Test Connection & Test Send for AE-010...")
        test_conn_btn = page.locator("button:has-text('Test Connection')")
        if test_conn_btn.count() > 0:
            test_conn_btn.first.click()
            time.sleep(2)
            
        test_send_btn = page.locator("button:has-text('Send Test Email')")
        if test_send_btn.count() > 0:
            test_send_btn.first.click()
            time.sleep(1)
            # Check if modal opened
            modal_send_btn = page.locator("div[role='dialog'] button:has-text('Send Live Test Email'), button:has-text('Send Live Test Email')")
            if modal_send_btn.count() > 0:
                modal_send_btn.first.click()
                time.sleep(3)
                
        ae010_path = os.path.join(images_dir, "AE-010_test_email_delivery.png")
        page.screenshot(path=ae010_path, full_page=False)
        print(f"Saved AE-010 screenshot: {ae010_path}")
        
        # Close modal if open
        close_btn = page.locator("button:has-text('Cancel'), button:has-text('Close')")
        if close_btn.count() > 0:
            close_btn.first.click()
            time.sleep(1)
            
        # 3. AE-024: Outbound Notification Delivery History & Receipt
        print("Capturing AE-024: Outbound Notification Delivery History...")
        # Refresh history
        refresh_btn = page.locator("button:has-text('Refresh History')")
        if refresh_btn.count() > 0:
            refresh_btn.first.click()
            time.sleep(2)
            
        # Scroll down to table
        history_heading = page.locator("text=Outbound Notification Delivery History")
        if history_heading.count() > 0:
            history_heading.first.scroll_into_view_if_needed()
            time.sleep(1)
            
        # Click "View Receipt" on the first row
        view_receipt_btn = page.locator("button:has-text('View Receipt')")
        if view_receipt_btn.count() > 0:
            print("Opening delivery receipt modal...")
            view_receipt_btn.first.click()
            time.sleep(1)
            
        ae024_path = os.path.join(images_dir, "AE-024_outbound_delivery_history.png")
        page.screenshot(path=ae024_path, full_page=False)
        print(f"Saved AE-024 screenshot: {ae024_path}")
        
        browser.close()
        print("All screenshots captured successfully!")

if __name__ == "__main__":
    main()
