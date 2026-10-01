import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.automation.browser_manager import ChromeSession
import subprocess

async def test():
    s = ChromeSession(headless=False)
    ctx = await s.start()
    ps_cmd = 'Get-CimInstance Win32_Process -Filter "name=\'chrome.exe\'" | Select-Object -Property ProcessId, CommandLine | Format-List'
    res = subprocess.run(['powershell', '-NoProfile', '-Command', ps_cmd], capture_output=True, text=True)
    print("--- CHROME PROCESSES COMMAND LINE ---")
    print(res.stdout)
    await ctx.close()

if __name__ == '__main__':
    asyncio.run(test())
