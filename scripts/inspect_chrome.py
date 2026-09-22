import subprocess

cmd = [
    "powershell",
    "-NoProfile",
    "-Command",
    "Get-CimInstance Win32_Process -Filter \"name = 'chrome.exe'\" | Select-Object ProcessId, CommandLine | Format-Table -Wrap"
]
p = subprocess.run(cmd, capture_output=True, text=True)
print(p.stdout)
