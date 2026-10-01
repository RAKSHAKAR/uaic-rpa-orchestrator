import subprocess
import time
import json
from pathlib import Path

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ext_dir = str(Path("anticaptcha-plugin_v0.83").resolve())
profile_dir = str(Path("backend/data/browser_profile/test_direct").resolve())

cmd = [
    chrome_exe,
    f"--user-data-dir={profile_dir}",
    f"--load-extension={ext_dir}",
    f"--disable-extensions-except={ext_dir}",
    "--no-first-run",
    "https://antcpt.com/blank.html"
]

print("Launching:", cmd)
proc = subprocess.Popen(cmd)
time.sleep(5)

# Now inspect profile_dir/Default/Preferences
pref = Path(profile_dir) / "Default" / "Preferences"
sec_pref = Path(profile_dir) / "Default" / "Secure Preferences"
print("Preferences exists:", pref.exists())
if pref.exists():
    try:
        d = json.loads(pref.read_text(encoding="utf-8"))
        print("Extensions in Pref:", list(d.get("extensions", {}).get("settings", {}).keys()))
    except Exception as e:
        print("Pref read error:", e)

if sec_pref.exists():
    try:
        d = json.loads(sec_pref.read_text(encoding="utf-8"))
        print("Extensions in Secure Pref:", list(d.get("extensions", {}).get("settings", {}).keys()))
        for k, v in d.get("extensions", {}).get("settings", {}).items():
            print(f"  {k}: {v.get('manifest', {}).get('name')}")
    except Exception as e:
        print("Secure Pref read error:", e)

proc.terminate()
print("Terminated.")
