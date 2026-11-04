import subprocess

ps_cmd = """
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'celery.*worker'
} | Select-Object ProcessId, CreationDate, CommandLine | ConvertTo-Json
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
print(res.stdout)
