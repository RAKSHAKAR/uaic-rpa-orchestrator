import json
import subprocess

ps_cmd = """
Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match 'python|celery|msedge|chrome'
} | Select-Object ProcessId, Name, CommandLine | ConvertTo-Json -Depth 2
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
try:
    data = json.loads(res.stdout)
    if isinstance(data, dict):
        data = [data]
    print(f"{'PID':<8} {'Name':<15} {'CommandLine'}")
    print("=" * 80)
    for p in data:
        pid = p.get("ProcessId", "")
        name = p.get("Name", "")
        cmd = p.get("CommandLine") or ""
        print(f"{pid:<8} {name:<15} {cmd[:140]}")
except Exception as e:
    print("Error parsing json:", e)
    print("Stdout was:", res.stdout[:500])
