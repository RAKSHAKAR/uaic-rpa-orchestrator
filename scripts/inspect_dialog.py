import asyncio
import ctypes
import time
from pathlib import Path
from playwright.async_api import async_playwright

rpa_profile = Path('backend/data/browser_profile/chrome').resolve()

async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(rpa_profile),
            executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            headless=False,
            args=['--no-sandbox']
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
        
        # Click load unpacked
        await page.evaluate('''() => {
            const mgr = document.querySelector('extensions-manager');
            const toolbar = mgr.shadowRoot.querySelector('extensions-toolbar');
            const btn = toolbar.shadowRoot.querySelector('#loadUnpacked');
            if (btn) btn.click();
        }''')
        
        user32 = ctypes.windll.user32
        hwnd = None
        for _ in range(10):
            time.sleep(0.5)
            hwnd = user32.FindWindowW(None, 'Select the extension directory.')
            if hwnd:
                break
                
        print('Found dialog hwnd:', hwnd)
        if hwnd:
            controls = []
            def enum_child(child, lparam):
                cls_buff = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(child, cls_buff, 256)
                txt_buff = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(child, txt_buff, 256)
                controls.append((child, cls_buff.value, txt_buff.value))
                return True
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumChildWindows(hwnd, WNDENUMPROC(enum_child), 0)
            for c in controls:
                if c[1] in ('Edit', 'Button', 'ComboBox', 'ToolbarWindow32'):
                    print(f'Control: {c[0]}, Class: {c[1]}, Text: "{c[2]}"')
                    
        await asyncio.sleep(2)
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
