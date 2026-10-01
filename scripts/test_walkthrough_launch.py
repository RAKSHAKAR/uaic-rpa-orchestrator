import subprocess
import time
from pathlib import Path

repo_root = Path(r"c:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC")
chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ext_dir = str((repo_root / "anticaptcha-plugin_v0.83").resolve())
profile_dir = str((repo_root / "backend" / "data" / "browser_profile" / "chrome_walkthrough").resolve())

cmd = [
    chrome_exe,
    f"--user-data-dir={profile_dir}",
    f"--disable-extensions-except={ext_dir}",
    f"--load-extension={ext_dir}",
    "--remote-debugging-port=9222",
    "--no-first-run",
    "--no-default-browser-check",
    "--start-maximized",
    "https://www.browardclerk.org/",
    "https://hover.hillsclerk.com/",
    "https://www2.miamidadeclerk.gov/ocs"
]

print("Launching independent Chrome with AntiCaptcha and 3 portals...")
proc = subprocess.Popen(cmd)
print("PID:", proc.pid)
time.sleep(3)

# Check if port 9222 is alive
import urllib.request
try:
    with urllib.request.urlopen("http://localhost:9222/json/version", timeout=3) as resp:
        print("CDP Version response:", resp.read().decode()[:150])
except Exception as e:
    print("CDP Error:", e)
