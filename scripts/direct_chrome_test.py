import subprocess
import time
from pathlib import Path

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ext_dir = str(Path("anticaptcha-plugin_v0.83").resolve())
profile_dir = str(Path("backend/data/browser_profile/chrome_direct_test").resolve())

cmd = [
    chrome_exe,
    f"--user-data-dir={profile_dir}",
    f"--disable-extensions-except={ext_dir}",
    f"--load-extension={ext_dir}",
    "--no-first-run",
    "--no-default-browser-check",
    "https://antcpt.com/blank.html"
]

print("Launching:", cmd)
proc = subprocess.Popen(cmd)
time.sleep(8)
proc.terminate()
print("Terminated.")
