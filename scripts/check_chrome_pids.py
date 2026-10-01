import subprocess
import json

ps = "Get-CimInstance Win32_Process -Filter \"name = 'chrome.exe'\" | Select-Object ProcessId, CommandLine | ConvertTo-Json"
res = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
try:
    data = json.loads(res.stdout) if res.stdout else []
    if isinstance(data, dict):
        data = [data]
    for d in data:
        cmd = d.get("CommandLine") or ""
        print(f"PID {d.get('ProcessId')}: {cmd[:180]}")
except Exception as e:
    print(f"Error: {e}, raw stdout: {res.stdout[:200]}")
