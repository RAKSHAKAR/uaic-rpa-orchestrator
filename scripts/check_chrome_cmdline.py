import asyncio
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    ext_path = Path("anticaptcha-plugin_v0.83").resolve()
    user_data_dir = Path("backend/data/test_profile_diag").resolve()
    chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            executable_path=chrome_exe,
            headless=False,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
            ],
            ignore_default_args=[
                "--disable-extensions",
                "--disable-component-extensions-with-background-pages"
            ],
            no_viewport=True
        )
        ps_script = """Get-CimInstance Win32_Process -Filter "name='chrome.exe'" | Select-Object -ExpandProperty CommandLine"""
        res = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_script], text=True)
        for line in res.splitlines():
            if "--type=" not in line and "chrome.exe" in line:
                print("MAIN CHROME CMDLINE:")
                for part in line.split(" --"):
                    print("  --" + part if not part.startswith('"') else part)
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
