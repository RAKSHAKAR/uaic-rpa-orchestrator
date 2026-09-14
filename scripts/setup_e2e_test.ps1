# Automated E2E Validation for Enterprise Setup Console
$ErrorActionPreference = "Stop"

$rootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$setupScript = Join-Path $rootDir "setup_local.ps1"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " Running E2E Automated Tests on Enterprise Setup Console" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

Write-Host "`n[Test 1] Starting All Services (Option 1 equivalent)..." -ForegroundColor Yellow
$global:LASTEXITCODE = 0
& powershell -NoProfile -ExecutionPolicy Bypass -File $setupScript -StartAll -NoPrompt -Mode "Unattended"
if ($LASTEXITCODE -eq 0) {
    Write-Host "PASS: Services started successfully." -ForegroundColor Green
} else {
    Write-Host "FAIL: Failed to start services with exit code $LASTEXITCODE." -ForegroundColor Red
    exit 1
}

Write-Host "`nWaiting 15 seconds for Celery workers to initialize..." -ForegroundColor DarkGray
Start-Sleep -Seconds 15

Write-Host "`n[Test 2] Running Diagnostics & Test Suite (Option 7 equivalent)..." -ForegroundColor Yellow
$global:LASTEXITCODE = 0
& powershell -NoProfile -ExecutionPolicy Bypass -File $setupScript -RunTests
if ($LASTEXITCODE -eq 0) {
    Write-Host "PASS: Diagnostics & Test Suite ran successfully." -ForegroundColor Green
} else {
    Write-Host "FAIL: Diagnostics & Test Suite failed with exit code $LASTEXITCODE." -ForegroundColor Red
    exit 1
}

Write-Host "`n[Test 3] Stopping All Services (Option 2 equivalent)..." -ForegroundColor Yellow
$global:LASTEXITCODE = 0
& powershell -NoProfile -ExecutionPolicy Bypass -File $setupScript -StopAll
if ($LASTEXITCODE -eq 0) {
    Write-Host "PASS: Services stopped successfully." -ForegroundColor Green
} else {
    Write-Host "FAIL: Failed to stop services with exit code $LASTEXITCODE." -ForegroundColor Red
    exit 1
}

Write-Host "`n======================================================" -ForegroundColor Cyan
Write-Host " All E2E Automated Tests Passed Successfully." -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Cyan
