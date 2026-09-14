import re
import os

with open("setup_local.ps1", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Modify Invoke-KillPort to be graceful
new_kill_port = """function Invoke-KillPort {
    param([int]$Port)
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connections) {
            $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($procId in $pids) {
                if ($procId -and $procId -gt 4) {
                    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
                    if ($proc -and ($proc.ProcessName -match "^(wsl|wslhost|wslrelay|docker|com\\.docker)" -or $proc.Name -match "^(wsl|wslhost|wslrelay|docker|com\\.docker)")) {
                        continue
                    }
                    Write-LogMessage "Attempting graceful shutdown for PID $procId on Port $Port..." "INFO" "DarkGray"
                    try { cmd.exe /c "taskkill /T /PID $procId" 2>$null | Out-Null } catch {}
                    Start-Sleep -Seconds 2
                    $procCheck = Get-Process -Id $procId -ErrorAction SilentlyContinue
                    if ($procCheck) {
                        Write-LogMessage "Graceful shutdown failed for PID $procId. Force terminating..." "WARNING" "Yellow"
                        try { cmd.exe /c "taskkill /F /T /PID $procId" 2>$null | Out-Null } catch {}
                        try { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } catch {}
                    }
                    Start-Sleep -Seconds 1
                    $procCheck = Get-Process -Id $procId -ErrorAction SilentlyContinue
                    if ($procCheck) {
                        Write-LogMessage "CRITICAL: Failed to terminate PID $procId!" "ERROR" "Red"
                    } else {
                        Write-LogMessage "PID $procId successfully terminated." "SUCCESS" "Green"
                    }
                }
            }
        }
        $netstatLines = netstat -ano 2>$null | Where-Object { $_ -match ":$Port\\s+" -and $_ -match "LISTENING" }
        foreach ($line in $netstatLines) {
            if ($line -match "\\s+(\\d+)$") {
                $netPid = [int]$matches[1]
                if ($netPid -gt 4) {
                    $proc = Get-Process -Id $netPid -ErrorAction SilentlyContinue
                    if ($proc -and ($proc.ProcessName -match "^(wsl|wslhost|wslrelay|docker|com\\.docker)" -or $proc.Name -match "^(wsl|wslhost|wslrelay|docker|com\\.docker)")) {
                        continue
                    }
                    Write-LogMessage "Attempting graceful shutdown for PID $netPid on Port $Port..." "INFO" "DarkGray"
                    try { cmd.exe /c "taskkill /T /PID $netPid" 2>$null | Out-Null } catch {}
                    Start-Sleep -Seconds 2
                    $procCheck = Get-Process -Id $netPid -ErrorAction SilentlyContinue
                    if ($procCheck) {
                        try { cmd.exe /c "taskkill /F /T /PID $netPid" 2>$null | Out-Null } catch {}
                        try { Stop-Process -Id $netPid -Force -ErrorAction SilentlyContinue } catch {}
                    }
                }
            }
        }
    } catch {}
}"""

# Escape backslashes for re.sub
content = re.sub(r'function Invoke-KillPort \{.*?^\}\n', new_kill_port.replace('\\', '\\\\') + '\n', content, flags=re.MULTILINE | re.DOTALL)

# 2. Modify Invoke-InstallDependencies to run the smoke test
smoke_test_code = """
        Set-PlaywrightChannel "chromium"
        }
        Write-LogMessage "Executing Real-World Browser Smoke Test ($($browsers.CurrentChannel))..." "INFO" "Cyan"
        $smokeTest = Join-Path $backendDir "app\\scripts\\browser_smoke_test.py"
        & $pyExe $smokeTest
        if ($LASTEXITCODE -ne 0) {
            Write-LogMessage "Browser smoke test failed! Check extension paths and browser installation." "ERROR" "Red"
        } else {
            Write-LogMessage "Browser smoke test passed. Anti-Captcha extension loaded successfully." "SUCCESS" "Green"
        }
        Write-LogMessage "Backend dependencies and browser engine verified successfully." "SUCCESS"
"""
content = re.sub(
    r'Set-PlaywrightChannel "chromium"\r?\n\s+\}\r?\n\s+Write-LogMessage "Backend dependencies and browser engine verified successfully." "SUCCESS"',
    smoke_test_code.replace('\\', '\\\\'),
    content
)

with open("setup_local.ps1", "w", encoding="utf-8") as f:
    f.write(content)

print("setup_local.ps1 rewritten")
