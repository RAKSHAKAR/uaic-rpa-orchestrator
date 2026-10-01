import asyncio
import ctypes
import time
import threading
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

ext_dir = str(Path('anticaptcha-plugin_v0.83').resolve())
meta_dir = Path('anticaptcha-plugin_v0.83/_metadata')
if meta_dir.exists():
    shutil.rmtree(meta_dir)

rpa_profile = Path('backend/data/browser_profile/chrome').resolve()

user32 = ctypes.windll.user32
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
BM_CLICK = 0x00F5
WM_COMMAND = 0x0111
VK_RETURN = 0x0D

def get_text(hwnd):
    buf = ctypes.create_unicode_buffer(512)
    user32.SendMessageW(hwnd, WM_GETTEXT, 512, buf)
    return buf.value

def set_text_via_clipboard(hwnd, edit_hwnd, text):
    import subprocess
    subprocess.run(['powershell', '-NoProfile', '-Command', f'Set-Clipboard -Value "{text}"'], check=True)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    user32.SetFocus(edit_hwnd)
    time.sleep(0.2)
    
    # Send WM_PASTE (0x0302) to edit
    WM_PASTE = 0x0302
    user32.SendMessageW(edit_hwnd, WM_PASTE, 0, 0)
    time.sleep(0.3)

dialog_done = threading.Event()

def test_dialog():
    print('[DialogTest] Waiting for dialog...')
    for _ in range(60):
        time.sleep(0.2)
        hwnd = user32.FindWindowW(None, 'Select the extension directory.')
        if hwnd:
            print(f'[DialogTest] Found dialog HWND: {hwnd}')
            time.sleep(0.5)
            edit = user32.GetDlgItem(hwnd, 1152)
            btn = user32.GetDlgItem(hwnd, 1)
            print(f'[DialogTest] Edit initial text: "{get_text(edit)}"')
            print(f'[DialogTest] Pasting Edit text: "{ext_dir}"')
            set_text_via_clipboard(hwnd, edit, ext_dir)
            print(f'[DialogTest] Edit text after paste: "{get_text(edit)}"')
            
            # Press ENTER in the Edit control to navigate into the directory
            print('[DialogTest] Pressing ENTER in edit control to navigate...')
            user32.SetFocus(edit)
            time.sleep(0.2)
            user32.SendMessageW(edit, 0x0100, 0x0D, 0) # WM_KEYDOWN VK_RETURN
            user32.SendMessageW(edit, 0x0101, 0x0D, 0) # WM_KEYUP VK_RETURN
            time.sleep(1.0)
            
            print(f'[DialogTest] Dialog open after Enter? {bool(user32.IsWindow(hwnd))}')
            print(f'[DialogTest] Edit text after Enter: "{get_text(edit)}"')
            
            # Now click Select Folder
            print('[DialogTest] Clicking Select Folder...')
            user32.SendMessageW(btn, BM_CLICK, 0, 0)
            time.sleep(1.0)
            
            print(f'[DialogTest] Dialog still open? {bool(user32.IsWindow(hwnd))}')
            if user32.IsWindow(hwnd):
                print(f'[DialogTest] Edit text now: "{get_text(edit)}"')
                print('[DialogTest] Clicking Select Folder 2nd time...')
                user32.SendMessageW(btn, BM_CLICK, 0, 0)
                time.sleep(1.0)
                print(f'[DialogTest] Dialog open after 2nd click? {bool(user32.IsWindow(hwnd))}')
            dialog_done.set()
            return True
    dialog_done.set()
    return False

async def main():
    threading.Thread(target=test_dialog, daemon=True).start()
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(rpa_profile),
            executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            headless=False,
            args=['--no-sandbox', '--start-maximized']
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto('chrome://extensions')
        await asyncio.sleep(2)
        
        # Turn dev mode on
        await page.evaluate('''() => {
            const mgr = document.querySelector('extensions-manager');
            const toolbar = mgr.shadowRoot.querySelector('extensions-toolbar');
            const devToggle = toolbar.shadowRoot.querySelector('#devMode');
            if (devToggle && !devToggle.checked) devToggle.click();
        }''')
        await asyncio.sleep(1)
        
        # Click load unpacked
        print('[Playwright] Clicking Load unpacked...')
        await page.evaluate('''() => {
            const mgr = document.querySelector('extensions-manager');
            const toolbar = mgr.shadowRoot.querySelector('extensions-toolbar');
            const btn = toolbar.shadowRoot.querySelector('#loadUnpacked');
            btn.click();
        }''')
        
        print('[Playwright] Waiting for dialog to complete...')
        await asyncio.to_thread(dialog_done.wait, 20)
        print('[Playwright] Dialog finished. Waiting 3 seconds for Chrome to register...')
        await asyncio.sleep(3)
        
        # Type 'anti' into search input
        try:
            await page.evaluate('''() => {
                const mgr = document.querySelector('extensions-manager');
                const toolbar = mgr?.shadowRoot?.querySelector('extensions-toolbar');
                const crToolbar = toolbar?.shadowRoot?.querySelector('cr-toolbar');
                const search = crToolbar?.shadowRoot?.querySelector('cr-toolbar-search-field');
                const input = search?.shadowRoot?.querySelector('#searchInput');
                if (input) {
                    input.value = 'anti';
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }''')
            await asyncio.sleep(2)
        except Exception as e:
            print('[Playwright] Search error:', e)
        
        # Check developerPrivate
        info = await page.evaluate('''() => {
            return new Promise((resolve) => {
                if (window.chrome?.developerPrivate?.getExtensionsInfo) {
                    chrome.developerPrivate.getExtensionsInfo({includeDisabled: true}, (exts) => {
                        resolve(exts.map(e => ({id: e.id, name: e.name, state: e.state})));
                    });
                } else {
                    resolve('developerPrivate not available');
                }
            });
        }''')
        print('[Playwright] developerPrivate.getExtensionsInfo:')
        print(info)
        
        # Check extensions
        js = '''() => {
            const mgr = document.querySelector('extensions-manager');
            const list = mgr?.shadowRoot?.querySelector('extensions-item-list');
            const items = list?.shadowRoot?.querySelectorAll('extensions-item') || [];
            return Array.from(items).map(i => ({
                id: i.id,
                name: i.shadowRoot?.querySelector('#name')?.innerText,
                desc: i.shadowRoot?.querySelector('#description')?.innerText,
            }));
        }'''
        exts = await page.evaluate(js)
        print('[Playwright] Result extensions:', exts)
        print('[Playwright] Service workers:', [sw.url for sw in ctx.service_workers])
        await page.screenshot(path='implementation_plan/Images/chrome_win32_loaded_ext5.png')
        await asyncio.sleep(2)
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
