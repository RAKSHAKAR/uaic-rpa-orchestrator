import subprocess
import time
from pathlib import Path

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ext_dir = str(Path("anticaptcha-plugin_v0.83").resolve())
test_profile = str(Path("backend/data/browser_profile/test_ext_diag").resolve())

cmd = [
    chrome_exe,
    f"--user-data-dir={test_profile}",
    f"--load-extension={ext_dir}",
    f"--disable-extensions-except={ext_dir}",
    "--enable-logging=stderr",
    "--v=1",
    "chrome://extensions"
]

print("Running cmd:", " ".join(cmd))
proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
time.sleep(6)
proc.terminate()
try:
    stdout, stderr = proc.communicate(timeout=3)
    print("--- STDOUT ---")
    print(stdout[:2000])
    print("--- STDERR ---")
    print(stderr[:4000])
except Exception as e:
    print("Communicate error:", e)
