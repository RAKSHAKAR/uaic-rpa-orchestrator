# Verify live health probe output directly from setup_local.ps1
$content = Get-Content (Join-Path $PSScriptRoot "..\setup_local.ps1") -Raw
$parsed = [System.Management.Automation.Language.Parser]::ParseInput($content, [ref]$null, [ref]$null)
$healthFuncAst = $parsed.Find({ param($ast) $ast -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $ast.Name -eq 'Invoke-CheckServiceHealth' }, $true)

if ($healthFuncAst) {
    Invoke-Expression $healthFuncAst.Extent.Text
    Write-Host "`n--- Testing Live Health Probes for Offline Services ---" -ForegroundColor Cyan
    Invoke-CheckServiceHealth "Frontend Web Application" 3000 "http://localhost:3000"
    Invoke-CheckServiceHealth "FastAPI Backend & API" 8000 "http://localhost:8000/api/v1/health"
    Invoke-CheckServiceHealth "Celery Flower Monitor" 5555 "http://localhost:5555"
    Invoke-CheckServiceHealth "MailDev Web Inspector" 1080 "http://localhost:1080"
    Invoke-CheckServiceHealth "MailDev SMTP Server" 1025
    Invoke-CheckServiceHealth "Redis Queue Broker" 6379
    Invoke-CheckServiceHealth "PostgreSQL Database" 5432
    Write-Host "--- Test Completed Successfully ---`n" -ForegroundColor Green
} else {
    Write-Error "Could not find Invoke-CheckServiceHealth in setup_local.ps1"
}
