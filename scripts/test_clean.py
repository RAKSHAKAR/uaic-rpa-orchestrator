import subprocess
import os
import time

lockfile = r"C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend\data\browser_profile\chrome\lockfile"

# Check if locked
try:
    with open(lockfile, "a") as f:
        print("Initial lockfile state: UNLOCKED")
except Exception as e:
    print(f"Initial lockfile state: LOCKED ({e})")

# Try killing PID 10656 and children
print("Killing PID 10656 with taskkill /F /T /PID 10656...")
res = subprocess.run(["taskkill", "/F", "/T", "/PID", "10656"], capture_output=True, text=True)
print("TASKKILL OUT:", res.stdout)
print("TASKKILL ERR:", res.stderr)

time.sleep(1)

# Check if lockfile can now be deleted/opened
try:
    if os.path.exists(lockfile):
        os.remove(lockfile)
        print("SUCCESS: lockfile successfully removed!")
    else:
        print("SUCCESS: lockfile no longer exists!")
except Exception as e:
    print(f"FAILED to remove lockfile: {e}")
