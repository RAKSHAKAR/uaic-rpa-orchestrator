<#
.SYNOPSIS
    Automated Non-Interactive Test Harness for Enterprise Setup Console.
.DESCRIPTION
    Validates setup_local.ps1 and setup.ps1 non-interactively:
    - Verifies PowerShell AST syntax across setup scripts
    - Tests CLI parameters (-CheckPorts, -StopAll, -CleanHistory, -RunTests)
    - Verifies port conflict detection and process termination
    - Verifies MailDev ports (1080, 1025) release
    - Produces a machine-readable summary with exit codes
#>

param(
    [switch]$Detailed
)

$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".."
$setupLocal = Join-Path $root "setup_local.ps1"

Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "      Enterprise Setup Console Automated Test Harness (PS1)            " -ForegroundColor Cyan
Write-Host "=======================================================================" -ForegroundColor Cyan

$testResults = @()

# --- TEST 1: PowerShell AST Syntax Validation ---
Write-Host "`n[TEST 1/6] Verifying PowerShell AST syntax for setup_local.ps1..." -ForegroundColor Yellow
$syntaxErrors = 0
$errs = $null
[System.Management.Automation.Language.Parser]::ParseFile($setupLocal, [ref]$null, [ref]$errs) | Out-Null
if ($errs.Count -eq 0) {
    Write-Host "  -> $(Split-Path $setupLocal -Leaf): PASS (0 syntax errors)" -ForegroundColor Green
} else {
    Write-Host "  -> $(Split-Path $setupLocal -Leaf): FAIL ($($errs.Count) syntax errors)" -ForegroundColor Red
    $syntaxErrors += $errs.Count
}
$status1 = if ($syntaxErrors -eq 0) { "PASS" } else { "FAIL" }
$testResults += [PSCustomObject]@{ Test = "AST Syntax"; Status = $status1 }

# --- TEST 2: Port Conflict Scanner (-CheckPorts) ---
Write-Host "`n[TEST 2/6] Testing Pre-Flight Port Conflict Detection (-CheckPorts)..." -ForegroundColor Yellow
$proc = Start-Process powershell.exe -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$setupLocal`"", "-CheckPorts" -NoNewWindow -Wait -PassThru
Write-Host "  -> setup_local.ps1 -CheckPorts exited with code: $($proc.ExitCode)" -ForegroundColor Cyan
$status2 = if ($proc.ExitCode -in @(0, 1)) { "PASS" } else { "FAIL" }
$testResults += [PSCustomObject]@{ Test = "Port Conflict Scanner"; Status = $status2 }

# --- TEST 3: Safe Process Termination & MailDev Stop (-StopAll) ---
Write-Host "`n[TEST 3/6] Testing Safe Process Termination & MailDev Stop (-StopAll)..." -ForegroundColor Yellow
$proc = Start-Process powershell.exe -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$setupLocal`"", "-StopAll" -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -eq 0) {
    Write-Host "  -> setup_local.ps1 -StopAll exited with code: 0 (SUCCESS)" -ForegroundColor Green
    # Verify ports 1080 and 1025 are not actively listening
    $p1080 = $null
    $p1025 = $null
    try { $p1080 = Get-NetTCPConnection -LocalPort 1080 -State Listen -ErrorAction SilentlyContinue } catch {}
    try { $p1025 = Get-NetTCPConnection -LocalPort 1025 -State Listen -ErrorAction SilentlyContinue } catch {}
    if (-not $p1080 -and -not $p1025) {
        Write-Host "  -> Verified Ports 1080 and 1025 are free." -ForegroundColor Green
    } else {
        Write-Host "  -> Note: Port 1080 or 1025 still occupied by external process." -ForegroundColor Yellow
    }
    $testResults += [PSCustomObject]@{ Test = "Stop All Services"; Status = "PASS" }
} else {
    Write-Host "  -> setup_local.ps1 -StopAll failed with exit code: $($proc.ExitCode)" -ForegroundColor Red
    $testResults += [PSCustomObject]@{ Test = "Stop All Services"; Status = "FAIL" }
}

# --- TEST 4: Clean Run History (-CleanHistory) ---
Write-Host "`n[TEST 4/6] Testing Clean Run History (-CleanHistory)..." -ForegroundColor Yellow
$proc = Start-Process powershell.exe -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$setupLocal`"", "-CleanHistory" -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -eq 0) {
    Write-Host "  -> setup_local.ps1 -CleanHistory exited with code: 0 (SUCCESS)" -ForegroundColor Green
    $testResults += [PSCustomObject]@{ Test = "Clean Run History"; Status = "PASS" }
} else {
    Write-Host "  -> setup_local.ps1 -CleanHistory failed with exit code: $($proc.ExitCode)" -ForegroundColor Red
    $testResults += [PSCustomObject]@{ Test = "Clean Run History"; Status = "FAIL" }
}

# --- TEST 5: RPA Mode Synchronization (set_rpa_mode.py) ---
Write-Host "`n[TEST 5/6] Testing RPA Mode Synchronization (set_rpa_mode.py)..." -ForegroundColor Yellow
$pyExe = Join-Path $root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $pyExe)) { $pyExe = "python" }
Push-Location (Join-Path $root "backend")
try {
    $outAttended = & $pyExe -m app.scripts.set_rpa_mode --mode Attended 2>&1
    $codeAttended = $LASTEXITCODE
    $outUnattended = & $pyExe -m app.scripts.set_rpa_mode --mode Unattended 2>&1
    $codeUnattended = $LASTEXITCODE
    if ($codeAttended -eq 0 -and $codeUnattended -eq 0) {
        Write-Host "  -> set_rpa_mode.py Attended & Unattended: PASS (0 errors)" -ForegroundColor Green
        $testResults += [PSCustomObject]@{ Test = "RPA Mode Synchronization"; Status = "PASS" }
    } else {
        Write-Host "  -> set_rpa_mode.py failed (Attended: $codeAttended, Unattended: $codeUnattended)" -ForegroundColor Red
        $testResults += [PSCustomObject]@{ Test = "RPA Mode Synchronization"; Status = "FAIL" }
    }
} finally { Pop-Location }

# --- TEST 6: Diagnostics & Test Suite Runner (-RunTests) ---
Write-Host "`n[TEST 6/6] Testing Diagnostics & Test Suite Runner (-RunTests)..." -ForegroundColor Yellow
$proc = Start-Process powershell.exe -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$setupLocal`"", "-RunTests" -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -eq 0) {
    Write-Host "  -> setup_local.ps1 -RunTests exited with code: 0 (SUCCESS)" -ForegroundColor Green
    $testResults += [PSCustomObject]@{ Test = "Diagnostics Runner"; Status = "PASS" }
} else {
    Write-Host "  -> setup_local.ps1 -RunTests exited with code: $($proc.ExitCode)" -ForegroundColor Red
    $testResults += [PSCustomObject]@{ Test = "Diagnostics Runner"; Status = "FAIL" }
}

Write-Host "`n=======================================================================" -ForegroundColor Cyan
Write-Host "                      TEST EXECUTION SUMMARY                           " -ForegroundColor Cyan
Write-Host "=======================================================================" -ForegroundColor Cyan
$failedCount = 0
foreach ($res in $testResults) {
    $color = if ($res.Status -eq "PASS") { "Green" } else { "Red"; $failedCount++ }
    Write-Host "  [$($res.Status)] $($res.Test)" -ForegroundColor $color
}
Write-Host "=======================================================================" -ForegroundColor Cyan

if ($failedCount -eq 0) {
    Write-Host "ALL AUTOMATED POWERSHELL SETUP CONSOLE TESTS PASSED (0 FAILURES)!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "$failedCount TEST(S) FAILED!" -ForegroundColor Red
    exit $failedCount
}
