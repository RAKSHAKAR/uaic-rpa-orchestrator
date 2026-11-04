import json
import subprocess
import time

ps_cmd = """
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'celery.*(worker|beat)'
} | Select-Object ProcessId, CommandLine | ConvertTo-Json
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
try:
    data = json.loads(res.stdout) if res.stdout.strip() else []
    if isinstance(data, dict):
        data = [data]
    print(f"Found {len(data)} Celery processes to terminate:")
    for p in data:
        pid = str(p.get("ProcessId"))
        cmd = p.get("CommandLine", "")
        print(f"Terminating PID {pid}: {cmd[:80]}...")
        subprocess.run(["taskkill", "/F", "/T", "/PID", pid], capture_output=True)
    time.sleep(2)
    print("All stale Celery workers terminated.")
except Exception as e:
    print("Error:", e)
