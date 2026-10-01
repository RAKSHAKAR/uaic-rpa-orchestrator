"""Florida Manual Walkthrough Browser Daemon.

Launches Google Chrome in Attended GUI mode with all three Florida portals
opened one-by-one in tabs, keeping the browser permanently open and exposing
a lightweight local inspector server on http://127.0.0.1:9333.
"""

import asyncio
import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import threading
import urllib.parse

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.automation.browser_manager import ChromeSession, ExtensionManager
from app.services.settings_service import get_system_settings_sync
from playwright.async_api import async_playwright, BrowserContext, Page

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("walkthrough_daemon")

app_state = {
    "context": None,
    "playwright": None,
    "pages": [],
    "ready": False,
    "loop": None,
}


class InspectorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress routine HTTP log messages
        pass

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/status":
            ctx = app_state["context"]
            if not ctx or not app_state["ready"]:
                self._send_json({"ready": False, "pages": []})
                return
            
            pages_info = []
            for idx, p in enumerate(ctx.pages):
                try:
                    pages_info.append({
                        "tab_index": idx + 1,
                        "url": p.url,
                    })
                except Exception:
                    pass
            self._send_json({"ready": True, "pages": pages_info})
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        tab_idx = int(params.get("tab", [1])[0]) - 1

        ctx = app_state["context"]
        loop = app_state["loop"]
        if not ctx or not loop:
            self._send_json({"error": "Browser not initialized"}, 500)
            return

        if tab_idx < 0 or tab_idx >= len(ctx.pages):
            self._send_json({"error": f"Tab index {tab_idx+1} out of range (total: {len(ctx.pages)})"}, 400)
            return

        target_page = ctx.pages[tab_idx]

        if parsed.path == "/screenshot":
            filename = params.get("filename", [f"tab_{tab_idx+1}_inspection.png"])[0]
            img_dir = Path(__file__).resolve().parent.parent / "implementation_plan" / "Images"
            img_dir.mkdir(parents=True, exist_ok=True)
            save_path = img_dir / filename

            async def _take():
                await target_page.screenshot(path=str(save_path), full_page=False)
                return str(save_path)

            fut = asyncio.run_coroutine_threadsafe(_take(), loop)
            try:
                res = fut.result(timeout=10)
                self._send_json({"success": True, "path": res, "url": target_page.url})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif parsed.path == "/inspect":
            async def _inspect():
                title = await target_page.title()
                url = target_page.url
                # Extract summary of form fields, tables, pagination, and frames
                dom_summary = await target_page.evaluate("""() => {
                    const inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(el => ({
                        tag: el.tagName.toLowerCase(),
                        id: el.id,
                        name: el.name,
                        type: el.type,
                        value: el.value,
                        placeholder: el.placeholder,
                        text: el.innerText ? el.innerText.trim().slice(0, 50) : '',
                        visible: el.offsetParent !== null
                    })).filter(x => x.visible || x.id || x.name);

                    const tables = Array.from(document.querySelectorAll('table')).map((t, idx) => {
                        const headers = Array.from(t.querySelectorAll('th')).map(th => th.innerText.trim());
                        const rowCount = t.querySelectorAll('tr').length;
                        return {
                            table_index: idx,
                            id: t.id,
                            className: t.className,
                            headers: headers,
                            rowCount: rowCount
                        };
                    });

                    const pagination = Array.from(document.querySelectorAll('.pagination, [class*="paginate"], [class*="page"], nav[aria-label*="page" i], [id*="page" i]')).map(p => ({
                        id: p.id,
                        className: p.className,
                        text: p.innerText.trim().slice(0, 100)
                    }));

                    return {
                        title: document.title,
                        inputsCount: inputs.length,
                        inputs: inputs.slice(0, 30),
                        tables: tables,
                        pagination: pagination
                    };
                }""")
                return {
                    "url": url,
                    "title": title,
                    "summary": dom_summary
                }

            fut = asyncio.run_coroutine_threadsafe(_inspect(), loop)
            try:
                res = fut.result(timeout=10)
                self._send_json(res)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif parsed.path == "/focus":
            async def _focus():
                await target_page.bring_to_front()
                return {"url": target_page.url}

            fut = asyncio.run_coroutine_threadsafe(_focus(), loop)
            try:
                res = fut.result(timeout=10)
                self._send_json({"success": True, "url": res["url"]})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
        else:
            self._send_json({"error": "Unknown POST endpoint"}, 404)


def start_http_server():
    server = HTTPServer(("127.0.0.1", 9333), InspectorHandler)
    logger.info("Inspector HTTP server listening on http://127.0.0.1:9333")
    server.serve_forever()


async def main():
    settings = get_system_settings_sync()
    broward_url = settings.portals.broward_url or "https://www.browardclerk.org/"
    hillsborough_url = settings.portals.hillsborough_url or "https://hover.hillsclerk.com/"
    miami_url = settings.portals.miami_url or "https://www2.miamidadeclerk.gov/ocs"

    chrome_exe = ChromeSession.find_chrome_executable()
    ext_path = ExtensionManager.resolve_extension_path()
    profile_dir = ChromeSession.get_persistent_profile_dir("chrome")

    logger.info("================================================================")
    logger.info("  MANUAL PORTAL WALKTHROUGH — FLORIDA PORTAL DAEMON")
    logger.info("================================================================")
    logger.info(f"Chrome Executable: {chrome_exe}")
    logger.info(f"Profile Dir:       {profile_dir}")
    logger.info(f"Extension Path:    {ext_path}")
    logger.info("----------------------------------------------------------------")
    logger.info(f"Tab 1 (Broward):      {broward_url}")
    logger.info(f"Tab 2 (Hillsborough): {hillsborough_url}")
    logger.info(f"Tab 3 (Miami-Dade):   {miami_url}")
    logger.info("================================================================")

    # Sync extension API key & pin preferences
    if ext_path and settings.automation.anticaptcha_api_key:
        ExtensionManager.sync_api_key(ext_path, settings.automation.anticaptcha_api_key, settings.automation)
    ChromeSession.configure_and_pin_profile(api_key=settings.automation.anticaptcha_api_key, extension_path=ext_path)
    ChromeSession.clean_profile_locks_and_orphans(profile_dir)

    app_state["loop"] = asyncio.get_running_loop()

    # Start inspector server in daemon thread
    t = threading.Thread(target=start_http_server, daemon=True)
    t.start()

    pw = await async_playwright().start()
    app_state["playwright"] = pw

    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized",
    ]
    if ext_path and ext_path.is_dir():
        launch_args.extend([
            f"--load-extension={ext_path}",
            f"--disable-extensions-except={ext_path}",
        ])

    logger.info("Launching Chrome persistent context...")
    context = await pw.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        executable_path=str(chrome_exe) if chrome_exe else None,
        headless=False,
        args=launch_args,
        viewport=None,  # Real window size
        no_viewport=True,
    )
    app_state["context"] = context

    # 1. Open Tab 1: Broward
    logger.info(f"Navigating Tab 1 to Broward: {broward_url} ...")
    if len(context.pages) > 0:
        tab1 = context.pages[0]
    else:
        tab1 = await context.new_page()
    try:
        await tab1.goto(broward_url, wait_until="domcontentloaded", timeout=45000)
    except Exception as e:
        logger.warning(f"Tab 1 navigation note: {e}")
    logger.info(f"[OK] Tab 1: Broward opened ({tab1.url})")

    # 2. Open Tab 2: Hillsborough
    logger.info(f"Opening Tab 2 to Hillsborough: {hillsborough_url} ...")
    await asyncio.sleep(2)
    tab2 = await context.new_page()
    try:
        await tab2.goto(hillsborough_url, wait_until="domcontentloaded", timeout=45000)
    except Exception as e:
        logger.warning(f"Tab 2 navigation note: {e}")
    logger.info(f"[OK] Tab 2: Hillsborough opened ({tab2.url})")

    # 3. Open Tab 3: Miami-Dade
    logger.info(f"Opening Tab 3 to Miami-Dade: {miami_url} ...")
    await asyncio.sleep(2)
    tab3 = await context.new_page()
    try:
        await tab3.goto(miami_url, wait_until="domcontentloaded", timeout=45000)
    except Exception as e:
        logger.warning(f"Tab 3 navigation note: {e}")
    logger.info(f"[OK] Tab 3: Miami-Dade opened ({tab3.url})")

    await asyncio.sleep(1)
    logger.info("Bringing Tab 1 (Broward) to front...")
    try:
        await tab1.bring_to_front()
    except Exception:
        pass

    app_state["ready"] = True
    logger.info("================================================================")
    logger.info("  ALL THREE FLORIDA TABS ARE OPEN AND READY ON SCREEN.")
    logger.info("  Chrome will remain open permanently for manual walkthrough.")
    logger.info("  Inspector active on http://127.0.0.1:9333")
    logger.info("================================================================")

    # Keep running indefinitely
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
