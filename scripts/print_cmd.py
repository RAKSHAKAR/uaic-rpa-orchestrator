import subprocess
import json

ps_cmd = """
Get-CimInstance Win32_Process -Filter "ProcessId = 12096" | 
    Select-Object CommandLine | 
    ConvertTo-Json
"""
res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
data = json.loads(res.stdout)
print("FULL COMMAND LINE:")
print(data.get("CommandLine"))
