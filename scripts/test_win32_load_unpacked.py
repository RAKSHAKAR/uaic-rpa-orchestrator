import asyncio
import ctypes
import time
from pathlib import Path
from playwright.async_api import async_playwright

ext_dir = str(Path('anticaptcha-plugin_v0.83').resolve())
rpa_profile = Path('backend/data/browser_profile/chrome').resolve()

# Auto-purge _metadata before test
meta_dir = Path('anticaptcha-plugin_v0.83/_metadata')
if meta_dir.exists():
    import shutil
    shutil.rmtree(meta_dir)

WM_SETTEXT = 0x000C
BM_CLICK = 0x00F5

def automate_select_folder():
    user32 = ctypes.windll.user32
    print("[Automate] Waiting for 'Select the extension directory.' dialog...")
    for _ in range(40):
        time.sleep(0.3)
        hwnd = user32.FindWindowW(None, 'Select the extension directory.')
        if hwnd:
            print(f"[Automate] Found dialog HWND: {hwnd}")
            time.sleep(0.3)
            
            # Find Edit control and Select Folder button
            controls = {}
            def enum_child(child, lparam):
                cls_buff = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(child, cls_buff, 256)
                txt_buff = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(child, txt_buff, 256)
                cls_name = cls_buff.value
                txt_val = txt_buff.value
                if cls_name == "Edit":
                    controls["edit"] = child
                elif cls_name == "Button" and "Select Folder" in txt_val:
                    controls["select_btn"] = child
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumChildWindows(hwnd, WNDENUMPROC(enum_child), 0)

            edit_hwnd = controls.get("edit")
            btn_hwnd = controls.get("select_btn")
            print(f"[Automate] Edit HWND: {edit_hwnd}, Select Button HWND: {btn_hwnd}")

            if edit_hwnd and btn_hwnd:
                # Set path in Edit box
                user32.SendMessageW(edit_hwnd, WM_SETTEXT, 0, ext_dir)
                time.sleep(0.3)
                # Click Select Folder
                user32.SendMessageW(btn_hwnd, BM_CLICK, 0, 0)
                print("[Automate] Clicked 'Select Folder'!")
                return True
    return False

import threading

async def main():
    t = threading.Thread(target=automate_select_folder, daemon=True)
    t.start()

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(rpa_profile),
            executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            headless=False,
            args=['--no-sandbox', '--start-maximized']
        )
        page = await ctx.new_page()
        await page.goto('chrome://extensions')
        await asyncio.sleep(2)

        # Turn on Developer Mode
        await page.evaluate('''() => {
            const mgr = document.querySelector('extensions-manager');
            const toolbar = mgr.shadowRoot.querySelector('extensions-toolbar');
            const devToggle = toolbar.shadowRoot.querySelector('#devMode');
            if (devToggle && !devToggle.checked) devToggle.click();
        }''')
        await asyncio.sleep(1)

        print("Clicking Load unpacked...")
        await page.evaluate('''() => {
            const mgr = document.querySelector('extensions-manager');
            const toolbar = mgr.shadowRoot.querySelector('extensions-toolbar');
            const btn = toolbar.shadowRoot.querySelector('#loadUnpacked');
            if (btn) btn.click();
        }''')

        await asyncio.sleep(4)

        # Inspect extensions on page
        js = '''() => {
            const mgr = document.querySelector('extensions-manager');
            if (!mgr) return 'No mgr';
            const list = mgr.shadowRoot.querySelector('extensions-item-list');
            if (!list) return 'No list';
            const items = list.shadowRoot.querySelectorAll('extensions-item');
            return Array.from(items).map(i => ({
                id: i.id,
                name: i.shadowRoot.querySelector('#name')?.innerText,
                description: i.shadowRoot.querySelector('#description')?.innerText,
                version: i.shadowRoot.querySelector('#version')?.innerText
            }));
        }'''
        exts = await page.evaluate(js)
        print("INSTALLED EXTENSIONS AFTER AUTOMATION:")
        print(exts)

        print("Service workers in context:", [sw.url for sw in ctx.service_workers])
        await page.screenshot(path='implementation_plan/Images/chrome_win32_loaded_ext.png')
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
