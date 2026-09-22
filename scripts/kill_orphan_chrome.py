import subprocess
import json

ps_script = """
Get-CimInstance Win32_Process -Filter "name = 'chrome.exe'" | 
  Select-Object ProcessId, CommandLine | 
  ConvertTo-Json -Compress
"""
res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
try:
    data = json.loads(res.stdout)
    if isinstance(data, dict):
        data = [data]
    print(f"Total Chrome processes found: {len(data)}")
    killed = 0
    for item in data:
        cmd = item.get("CommandLine") or ""
        pid = item.get("ProcessId")
        if "browser_profile" in cmd or "Bot_UAIC" in cmd or "anticaptcha" in cmd:
            print(f"Killing Chrome process {pid}: {cmd[:100]}...")
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
            killed += 1
    print(f"Successfully killed {killed} orphan Chrome processes.")
except Exception as e:
    print("Error parsing json:", e, res.stdout[:200])
