import subprocess
import json

ps_cmd = """
Get-CimInstance Win32_Process -Filter "name = 'chrome.exe' or name = 'msedge.exe'" | 
    Select-Object ProcessId, CommandLine | 
    ConvertTo-Json -Depth 2
"""
res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
print("STDOUT:")
try:
    data = json.loads(res.stdout)
    if isinstance(data, dict):
        data = [data]
    for p in data:
        cmd = p.get("CommandLine") or ""
        print(f"PID: {p.get('ProcessId')}, Has 'browser_profile': {'browser_profile' in cmd}")
        if "browser_profile" in cmd or "bot_uaic" in cmd.lower() or "anticaptcha" in cmd.lower():
            print(f"   FULL CMD: {cmd[:200]}")
except Exception as e:
    print(f"Parse error: {e}")
    print(res.stdout[:500])
