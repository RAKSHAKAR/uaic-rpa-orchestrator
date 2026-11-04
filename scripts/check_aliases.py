import re

common_aliases = {
    'ps': 'Get-Process',
    'kill': 'Stop-Process',
    'dir': 'Get-ChildItem',
    'ls': 'Get-ChildItem',
    'gci': 'Get-ChildItem',
    'cat': 'Get-Content',
    'gc': 'Get-Content',
    'sc': 'Set-Content',
    'ac': 'Add-Content',
    'cls': 'Clear-Host',
    'clear': 'Clear-Host',
    'rm': 'Remove-Item',
    'ri': 'Remove-Item',
    'cp': 'Copy-Item',
    'cpi': 'Copy-Item',
    'mv': 'Move-Item',
    'mi': 'Move-Item',
    'del': 'Remove-Item',
    'erase': 'Remove-Item',
    'rd': 'Remove-Item',
    'rdir': 'Remove-Item',
    'md': 'mkdir',
    'ni': 'New-Item',
    'sl': 'Set-Location',
    'cd': 'Set-Location',
    'gl': 'Get-Location',
    'pwd': 'Get-Location',
    'select': 'Select-Object',
    'where': 'Where-Object',
    'foreach': 'ForEach-Object',
    'sleep': 'Start-Sleep',
    'write': 'Write-Output',
    'echo': 'Write-Output',
    'type': 'Get-Content',
}

with open('setup_local.ps1', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    # strip comments
    l = line.split('#')[0].strip()
    tokens = re.split(r'[\s|;()]+', l)
    for t in tokens:
        if t.lower() in common_aliases:
            # check if it's used as a command
            print(f'Line {idx+1}: Alias "{t}" -> {common_aliases[t.lower()]} in: {line.strip()[:80]}')
