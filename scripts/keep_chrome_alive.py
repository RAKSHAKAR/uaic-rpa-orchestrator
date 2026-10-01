import subprocess
import time
import sys
from pathlib import Path

repo_root = Path(r"c:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC")
chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ext_dir = str((repo_root / "anticaptcha-plugin_v0.83").resolve())
profile_dir = str((repo_root / "backend" / "data" / "browser_profile" / "chrome_walkthrough").resolve())

# Clean lock files first
p = Path(profile_dir)
if p.exists():
    for f in p.glob("Singleton*"):
        try:
            f.unlink()
        except Exception:
            pass
    lock = p / "lockfile"
    if lock.exists():
        try:
            lock.unlink()
        except Exception:
            pass

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

print("=========================================================")
print("LAUNCHING REAL GOOGLE CHROME ON USER DESKTOP")
print(f"Extension: {ext_dir}")
print(f"Profile:   {profile_dir}")
print("Opening 3 Florida Portals:")
print("  Tab 1: https://www.browardclerk.org/")
print("  Tab 2: https://hover.hillsclerk.com/")
print("  Tab 3: https://www2.miamidadeclerk.gov/ocs")
print("=========================================================")

proc = subprocess.Popen(cmd)
print(f"Chrome active with PID: {proc.pid}")
sys.stdout.flush()

# Keep running so the background task never exits and Chrome stays open
while True:
    time.sleep(2)
    if proc.poll() is not None:
        print(f"Chrome exited with code {proc.returncode}")
        break
