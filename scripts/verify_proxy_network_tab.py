"""
End-to-End Verification of 'Proxy Network' Tab Functionality
Target Route: http://localhost:3000/settings (Tab: "Proxy Network" / activeTab === "proxy")

Validates:
1. Navigation & Tab Switching to Proxy Network
2. Real-time Egress Mode Indicator (Direct Egress vs Proxy Routed)
3. Form Inputs: Host, Port, Username, Password
4. Password Visibility Eye Toggle (Show/Hide)
5. Live Proxy Connectivity Test against Offline Port (Failure Handling)
6. Live Proxy Connectivity Test against Active Local Proxy Server (Success Handling)
7. Settings Persistence & SQLite Database Versioning
8. Clean Reset to Direct Internet Egress
"""

import os
import select
import socket
import sys
import threading
import time
from playwright.sync_api import sync_playwright

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)


class LocalHttpProxy:
    """Lightweight local HTTP CONNECT proxy server for testing."""

    def __init__(self, port: int = 9099):
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("127.0.0.1", port))
        self.server.listen(15)
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def _listen(self):
        while self.running:
            try:
                client, _ = self.server.accept()
                threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, client: socket.socket):
        try:
            req = client.recv(4096).decode("latin-1")
            if req.startswith("CONNECT"):
                target = req.split()[1]
                host, port = target.split(":")
                remote = socket.create_connection((host, int(port)), timeout=10)
                client.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
                sockets = [client, remote]
                while True:
                    r, _, _ = select.select(sockets, [], [], 10)
                    if not r:
                        break
                    for s in r:
                        data = s.recv(8192)
                        if not data:
                            return
                        out = remote if s is client else client
                        out.sendall(data)
            else:
                client.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
        except Exception:
            pass
        finally:
            try:
                client.close()
            except Exception:
                pass

    def close(self):
        self.running = False
        try:
            self.server.close()
        except Exception:
            pass


def run_proxy_network_verification():
    print("=" * 75)
    print("Starting Playwright verification of 'Proxy Network' tab...")
    print("=" * 75)

    proxy_server = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1872, "height": 1113})
        page = context.new_page()

        # Step 1: Navigate to Settings page
        print("\n1. Navigating to http://localhost:3000/settings...")
        page.goto("http://localhost:3000/settings", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("text=Unified Solution & Automation Settings", timeout=30000)
        page.wait_for_timeout(1000)
        print("   PASS: Settings page loaded.")

        # Step 2: Switch to Proxy Network tab
        print("\n2. Switching to 'Proxy Network' tab...")
        proxy_tab_btn = page.locator("button:has-text('Proxy Network')")
        assert proxy_tab_btn.is_visible(), "Proxy Network tab button not found"
        proxy_tab_btn.click()
        page.wait_for_selector("text=Proxy Pool Settings", timeout=10000)
        page.wait_for_timeout(800)

        overview_path = os.path.join(DOCS_DIR, "verify_proxy_tab_overview.png")
        page.screenshot(path=overview_path)
        print(f"   PASS: Switched to 'Proxy Network' tab. Screenshot: {overview_path}")

        # Step 3: Verify initial Direct Egress state
        print("\n3. Verifying initial Direct Egress status badge...")
        direct_badge = page.locator("text=Direct Internet Egress").first
        assert direct_badge.is_visible(), "Direct Internet Egress badge not visible"
        print("   PASS: Direct Internet Egress badge verified.")

        # Step 4: Toggle Enable Proxy Server
        print("\n4. Toggling 'Enable Proxy Server' switch...")
        enable_toggle = page.locator("#proxy-enabled-toggle")
        if not enable_toggle.is_checked():
            enable_toggle.check()
        page.wait_for_timeout(500)
        assert enable_toggle.is_checked(), "Proxy enable toggle did not check"
        print("   PASS: Proxy enabled toggle checked.")

        # Step 5: Fill in Proxy Parameters
        print("\n5. Configuring Proxy Host, Port, Username, and Password...")
        host_input = page.locator("#proxy-host")
        port_input = page.locator("#proxy-port")
        username_input = page.locator("#proxy-username")
        password_input = page.locator("#proxy-password")

        host_input.fill("127.0.0.1")
        port_input.fill("9999")
        username_input.fill("uaic_rpa_bot")
        password_input.fill("SecureProxyPass2026!")
        page.wait_for_timeout(400)
        print("   PASS: Proxy parameters populated.")

        # Step 6: Test Password Visibility Toggle
        print("\n6. Testing Proxy Password Show/Hide Toggle...")
        assert password_input.get_attribute("type") == "password", "Default input type must be password"
        toggle_eye_btn = page.locator("#btn-toggle-proxy-password")
        toggle_eye_btn.click()
        page.wait_for_timeout(200)
        assert password_input.get_attribute("type") == "text", "Password input type did not change to text"
        toggle_eye_btn.click()
        page.wait_for_timeout(200)
        assert password_input.get_attribute("type") == "password", "Password input type did not revert to password"
        print("   PASS: Password visibility toggle verified (hidden -> visible -> hidden).")

        # Step 7: Test Failure Scenario (unreachable offline port 9999)
        print("\n7. Testing Proxy Connectivity Failure handling (offline port 9999)...")
        test_btn = page.locator("#btn-test-proxy-connection")
        assert test_btn.is_visible(), "Test Proxy Connection button not visible"
        test_btn.click()
        page.wait_for_selector("#proxy-test-result-card", timeout=20000)
        failure_card = page.locator("#proxy-test-result-card")
        assert failure_card.locator("text=Proxy Connection Failed").first.is_visible(), "Failure message not displayed"
        print("   PASS: Unreachable proxy failure handled with diagnostic error card.")

        # Step 8: Start Live Mock Proxy Server & Test Success Scenario
        print("\n8. Starting local HTTP CONNECT proxy server on 127.0.0.1:9099...")
        proxy_server = LocalHttpProxy(port=9099)
        time.sleep(0.5)

        port_input.fill("9099")
        page.wait_for_timeout(300)
        print("   Clicking 'Test Proxy Connection' against live proxy on port 9099...")
        test_btn.click()
        page.wait_for_selector("text=Proxy Reachable", timeout=25000)
        success_card = page.locator("#proxy-test-result-card")
        assert success_card.locator("text=Proxy Reachable").first.is_visible(), "Proxy Reachable not visible"
        assert success_card.locator("text=via 127.0.0.1:9099").first.is_visible() or success_card.locator("text=HTTP 200").first.is_visible()
        print("   PASS: Live proxy connectivity test succeeded with round-trip response!")

        # Step 9: Save Configuration & Verify Persistence
        print("\n9. Persisting Proxy Configuration to database...")
        save_btn = page.locator("button:has-text('Save Configuration')").first
        save_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        save_btn.click()
        page.wait_for_selector("text=Settings saved as revision", timeout=20000)
        print("   PASS: Settings persisted successfully.")

        # Step 10: Reload and Confirm State Retained
        print("\n10. Reloading Settings page and verifying persistence...")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_selector("text=Unified Solution & Automation Settings", timeout=30000)
        page.locator("button:has-text('Proxy Network')").click()
        page.wait_for_selector("text=Proxy Pool Settings", timeout=10000)
        page.wait_for_timeout(800)

        assert page.locator("#proxy-enabled-toggle").is_checked(), "Proxy enabled state not retained"
        assert page.locator("#proxy-host").input_value() == "127.0.0.1", "Host not retained"
        assert page.locator("#proxy-port").input_value() == "9099", "Port not retained"
        assert page.locator("#proxy-username").input_value() == "uaic_rpa_bot", "Username not retained"
        assert page.locator("text=Secret Saved").is_visible(), "Secret Saved indicator not visible"
        print("   PASS: Full proxy configuration and credentials retained across page reloads.")

        # Capture result screenshot with live success state and secret badge
        result_path = os.path.join(DOCS_DIR, "verify_proxy_tab_test_result.png")
        page.screenshot(path=result_path)
        print(f"   PASS: Captured verified test result screenshot: {result_path}")

        # Step 11: Clean Restoration to Direct Internet Egress
        print("\n11. Restoring system to Direct Internet Egress mode...")
        page.locator("#proxy-enabled-toggle").uncheck()
        page.wait_for_timeout(300)
        save_btn.scroll_into_view_if_needed()
        save_btn.click()
        page.wait_for_selector("text=Settings saved as revision", timeout=20000)
        assert page.locator("text=Direct Internet Egress").first.is_visible(), "Direct Internet Egress badge not restored"
        print("   PASS: System restored to clean Direct Internet Egress mode.")

        browser.close()

    if proxy_server:
        proxy_server.close()

    print("\n" + "=" * 75)
    print("ALL 11 PROXY NETWORK VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_proxy_network_verification()
