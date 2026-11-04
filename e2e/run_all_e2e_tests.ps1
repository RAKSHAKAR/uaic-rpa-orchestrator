<#
.SYNOPSIS
    UAIC RPA Orchestrator - Automated E2E Execution Runner
    Implementation ID: IMP-2026-1031-002

.DESCRIPTION
    Comprehensive PowerShell E2E test execution harness supporting:
    - Environment selection: Local vs Docker
    - Suite selection: All, Portal, Backend, Frontend, Integration
    - Portal filtering: fl_broward, fl_hillsborough, fl_miami, te_travis, te_dallas, te_harris_jp, te_harris_cclerk, te_harris_district
    - Mode selection: Attended (Visible GUI) vs Unattended (Headless)
    - Automated machine-readable JSON results in e2e/results/summary.json
    - Interactive, responsive HTML report in e2e/reports/e2e_test_report.html

.PARAMETER Environment
    Execution environment: Local (default) or Docker

.PARAMETER Suite
    Test suite to execute: All (default), Portal, Backend, Frontend, Integration

.PARAMETER Portal
    Specific portal key for portal-level runs (e.g. fl_broward)

.PARAMETER Mode
    Execution mode: Attended (default) or Unattended

.PARAMETER Headless
    Switch to force headless browser mode

.PARAMETER OpenReport
    Switch to automatically launch the generated HTML report in default browser
#>

[CmdletBinding()]
param(
    [ValidateSet("Local", "Docker")]
    [string]$Environment = "Local",

    [ValidateSet("All", "Portal", "Backend", "Frontend", "Integration")]
    [string]$Suite = "All",

    [string]$Portal = "",

    [ValidateSet("Attended", "Unattended")]
    [string]$Mode = "Attended",

    [switch]$Headless,
    [switch]$OpenReport
)

$ErrorActionPreference = "Continue"
$e2eDir = $PSScriptRoot
$rootDir = (Get-Item $e2eDir).Parent.FullName
$backendDir = Join-Path $rootDir "backend"
$reportsDir = Join-Path $e2eDir "reports"
$resultsDir = Join-Path $e2eDir "results"
$logsDir = Join-Path $e2eDir "logs"
$screenshotsDir = Join-Path $e2eDir "screenshots"

# Ensure output directories exist
foreach ($d in @($reportsDir, $resultsDir, $logsDir, $screenshotsDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

$startTime = Get-Date
$isHeadless = if ($Headless -or ($Mode -eq "Unattended")) { $true } else { $false }
$effectiveMode = if ($isHeadless) { "Unattended (Headless)" } else { "Attended (Visible GUI)" }

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " UAIC RPA Orchestrator - End-to-End Test Runner" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " Environment: $Environment" -ForegroundColor White
Write-Host " Test Suite:  $Suite" -ForegroundColor White
Write-Host " Mode:        $effectiveMode" -ForegroundColor White
if ($Portal) { Write-Host " Portal:      $Portal" -ForegroundColor Yellow }
Write-Host " Start Time:  $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Pre-flight Checks
Write-Host "`n[PHASE 1] Pre-Flight Health & Dependency Verification..." -ForegroundColor Cyan

function Test-PortListening {
    param([int]$Port)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect("127.0.0.1", $Port, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne(800, $false)
        if ($wait) {
            $tcp.EndConnect($iar)
            $tcp.Close()
            return $true
        }
        $tcp.Close()
        return $false
    } catch {
        return $false
    }
}

$backendOnline = Test-PortListening 8000
$frontendOnline = Test-PortListening 3000
$redisOnline = Test-PortListening 6379

Write-Host "  Backend  (port 8000): " -NoNewline
if ($backendOnline) { Write-Host "ONLINE" -ForegroundColor Green } else { Write-Host "OFFLINE (Mock/Unit mode active)" -ForegroundColor Yellow }

Write-Host "  Frontend (port 3000): " -NoNewline
if ($frontendOnline) { Write-Host "ONLINE" -ForegroundColor Green } else { Write-Host "OFFLINE (Skipping UI specs if not running)" -ForegroundColor Yellow }

Write-Host "  Redis    (port 6379): " -NoNewline
if ($redisOnline) { Write-Host "ONLINE" -ForegroundColor Green } else { Write-Host "OFFLINE" -ForegroundColor Yellow }

# 2. Python Environment Resolution
$pyExe = Join-Path $backendDir ".venv\Scripts\python.exe"
if (-not (Test-Path $pyExe)) {
    $pyExe = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $pyExe) {
    Write-Host "[ERROR] Python executable not found!" -ForegroundColor Red
    exit 1
}

$pytestExe = Join-Path $backendDir ".venv\Scripts\pytest.exe"
if (-not (Test-Path $pytestExe)) {
    $pytestExe = "pytest"
}

# 3. Test Execution Array
$testResults = @()
$totalPassed = 0
$totalFailed = 0
$totalSkipped = 0

Write-Host "`n[PHASE 2] Executing E2E Test Suites..." -ForegroundColor Cyan

# Test Item 1: Attended / Unattended Browser Automation Parity
if ($Suite -in @("All", "Backend", "Integration")) {
    Write-Host "  -> Running Backend E2E Suite: Attended & Unattended Scraping..." -ForegroundColor White
    $logFile = Join-Path $logsDir "test_backend_e2e_scraping.log"
    $t0 = [System.Diagnostics.Stopwatch]::StartNew()
    
    $pytestArgs = @(
        "e2e/backend/test_e2e_attended_scraping.py",
        "e2e/backend/test_e2e_unattended_scraping.py",
        "e2e/backend/test_e2e_browser_engine.py",
        "-o", "pythonpath=backend",
        "-q", "--tb=short"
    )
    
    $proc = Start-Process -FilePath $pytestExe -ArgumentList $pytestArgs -WorkingDirectory $rootDir -NoNewWindow -PassThru -Wait -RedirectStandardOutput $logFile
    $t0.Stop()
    $dur = [math]::Round($t0.Elapsed.TotalSeconds, 2)
    $logContent = if (Test-Path $logFile) { Get-Content $logFile -Raw } else { "" }
    
    $passed = 0
    $failed = 0
    $skipped = 0
    if ($logContent -match '(\d+)\s+passed') { $passed = [int]$matches[1] }
    elseif ($proc.ExitCode -eq 0 -and $logContent -match '(\.{3,})') { 
        $passed = ($matches[1] | Select-String -Pattern '\.' -AllMatches).Matches.Count 
    }
    if ($logContent -match '(\d+)\s+failed') { $failed = [int]$matches[1] }
    if ($logContent -match '(\d+)\s+skipped') { $skipped = [int]$matches[1] }
    
    $status = if ($proc.ExitCode -eq 0 -and $failed -eq 0) { "PASSED" } else { "FAILED" }
    if ($status -eq "PASSED") {
        Write-Host "     [PASSED] in ${dur}s ($passed passed, $skipped skipped)" -ForegroundColor Green
        $totalPassed += $passed
        $totalSkipped += $skipped
    } else {
        Write-Host "     [FAILED] in ${dur}s ($failed failed, $passed passed)" -ForegroundColor Red
        $totalFailed += ($failed + 1)
        $totalPassed += $passed
    }
    
    $testResults += [PSCustomObject]@{
        Suite = "Backend Automation & Engine E2E"
        Target = "Attended / Unattended Parity & Browser Channels"
        Status = $status
        Duration = $dur
        Passed = $passed
        Failed = $failed
        Skipped = $skipped
        Log = $logFile
    }
}

# Test Item 2: Portal Health & Reachability Verification
if ($Suite -in @("All", "Backend", "Portal")) {
    Write-Host "  -> Running Portal Ping & Health Detailed E2E..." -ForegroundColor White
    $logFile = Join-Path $logsDir "test_portal_health_e2e.log"
    $t0 = [System.Diagnostics.Stopwatch]::StartNew()
    
    $portalArgs = @(
        "e2e/backend/test_e2e_portal_pings.py",
        "e2e/backend/test_e2e_health_detailed.py",
        "-o", "pythonpath=backend",
        "-q", "--tb=short"
    )
    
    $proc = Start-Process -FilePath $pytestExe -ArgumentList $portalArgs -WorkingDirectory $rootDir -NoNewWindow -PassThru -Wait -RedirectStandardOutput $logFile
    $t0.Stop()
    $dur = [math]::Round($t0.Elapsed.TotalSeconds, 2)
    $logContent = if (Test-Path $logFile) { Get-Content $logFile -Raw } else { "" }
    
    $passed = 0
    $failed = 0
    $skipped = 0
    if ($logContent -match '(\d+)\s+passed') { $passed = [int]$matches[1] }
    elseif ($proc.ExitCode -eq 0 -and $logContent -match '(\.{3,})') { 
        $passed = ($matches[1] | Select-String -Pattern '\.' -AllMatches).Matches.Count 
    }
    if ($logContent -match '(\d+)\s+failed') { $failed = [int]$matches[1] }
    if ($logContent -match '(\d+)\s+skipped') { $skipped = [int]$matches[1] }
    
    $status = if ($proc.ExitCode -eq 0 -and $failed -eq 0) { "PASSED" } else { "FAILED" }
    if ($status -eq "PASSED") {
        Write-Host "     [PASSED] in ${dur}s ($passed passed, $skipped skipped)" -ForegroundColor Green
        $totalPassed += $passed
        $totalSkipped += $skipped
    } else {
        Write-Host "     [FAILED] in ${dur}s ($failed failed, $passed passed)" -ForegroundColor Red
        $totalFailed += ($failed + 1)
        $totalPassed += $passed
    }
    
    $testResults += [PSCustomObject]@{
        Suite = "County Portal Health & Ping Verification"
        Target = "8 Portal Pings & Detailed Diagnostic Compliance"
        Status = $status
        Duration = $dur
        Passed = $passed
        Failed = $failed
        Skipped = $skipped
        Log = $logFile
    }
}

# Test Item 3: Core Scraper Unit & Integration Validation
if ($Suite -in @("All", "Portal", "Integration")) {
    Write-Host "  -> Running 8-Portal Scraper Engine & Schema Tests..." -ForegroundColor White
    $logFile = Join-Path $logsDir "test_scrapers_schema_integration.log"
    $t0 = [System.Diagnostics.Stopwatch]::StartNew()
    
    $scraperFilter = if ($Portal) { "-k", $Portal } else { @() }
    $scraperArgs = @(
        "backend/tests/test_scrapers.py",
        "backend/tests/test_scraper_pagination.py",
        "backend/tests/test_multi_portal_execution_order.py",
        "-q", "--tb=short"
    ) + $scraperFilter
    
    $proc = Start-Process -FilePath $pytestExe -ArgumentList $scraperArgs -WorkingDirectory $rootDir -NoNewWindow -PassThru -Wait -RedirectStandardOutput $logFile
    $t0.Stop()
    $dur = [math]::Round($t0.Elapsed.TotalSeconds, 2)
    $logContent = if (Test-Path $logFile) { Get-Content $logFile -Raw } else { "" }
    
    $passed = 0
    $failed = 0
    $skipped = 0
    if ($logContent -match '(\d+)\s+passed') { $passed = [int]$matches[1] }
    elseif ($proc.ExitCode -eq 0 -and $logContent -match '(\.{3,})') { 
        $passed = ($matches[1] | Select-String -Pattern '\.' -AllMatches).Matches.Count 
    }
    if ($logContent -match '(\d+)\s+failed') { $failed = [int]$matches[1] }
    if ($logContent -match '(\d+)\s+skipped') { $skipped = [int]$matches[1] }
    
    $status = if ($proc.ExitCode -eq 0 -and $failed -eq 0) { "PASSED" } else { "FAILED" }
    if ($status -eq "PASSED") {
        Write-Host "     [PASSED] in ${dur}s ($passed passed, $skipped skipped)" -ForegroundColor Green
        $totalPassed += $passed
        $totalSkipped += $skipped
    } else {
        Write-Host "     [FAILED] in ${dur}s ($failed failed, $passed passed)" -ForegroundColor Red
        $totalFailed += ($failed + 1)
        $totalPassed += $passed
    }
    
    $testResults += [PSCustomObject]@{
        Suite = "8-Portal Scraper Schemas & Execution Order"
        Target = if ($Portal) { "Portal: $Portal" } else { "All 8 Portals (FL & TX)" }
        Status = $status
        Duration = $dur
        Passed = $passed
        Failed = $failed
        Skipped = $skipped
        Log = $logFile
    }
}

# Test Item 4: Fuzzy Matching & Unique Names Extraction
if ($Suite -in @("All", "Backend", "Integration")) {
    Write-Host "  -> Running RapidFuzz Cascade & Unique Names Extraction Tests..." -ForegroundColor White
    $logFile = Join-Path $logsDir "test_fuzzy_and_unique_names.log"
    $t0 = [System.Diagnostics.Stopwatch]::StartNew()
    
    $fuzzyArgs = @(
        "backend/tests/test_fuzzy_engine.py",
        "backend/tests/test_unique_names_spreadsheet_matrix.py",
        "backend/tests/test_guidewire_client.py",
        "backend/tests/test_guidewire_pipeline.py",
        "-q", "--tb=short"
    )
    
    $proc = Start-Process -FilePath $pytestExe -ArgumentList $fuzzyArgs -WorkingDirectory $rootDir -NoNewWindow -PassThru -Wait -RedirectStandardOutput $logFile
    $t0.Stop()
    $dur = [math]::Round($t0.Elapsed.TotalSeconds, 2)
    $logContent = if (Test-Path $logFile) { Get-Content $logFile -Raw } else { "" }
    
    $passed = 0
    $failed = 0
    $skipped = 0
    if ($logContent -match '(\d+)\s+passed') { $passed = [int]$matches[1] }
    elseif ($proc.ExitCode -eq 0 -and $logContent -match '(\.{3,})') { 
        $passed = ($matches[1] | Select-String -Pattern '\.' -AllMatches).Matches.Count 
    }
    if ($logContent -match '(\d+)\s+failed') { $failed = [int]$matches[1] }
    if ($logContent -match '(\d+)\s+skipped') { $skipped = [int]$matches[1] }
    
    $status = if ($proc.ExitCode -eq 0 -and $failed -eq 0) { "PASSED" } else { "FAILED" }
    if ($status -eq "PASSED") {
        Write-Host "     [PASSED] in ${dur}s ($passed passed, $skipped skipped)" -ForegroundColor Green
        $totalPassed += $passed
        $totalSkipped += $skipped
    } else {
        Write-Host "     [FAILED] in ${dur}s ($failed failed, $passed passed)" -ForegroundColor Red
        $totalFailed += ($failed + 1)
        $totalPassed += $passed
    }
    
    $testResults += [PSCustomObject]@{
        Suite = "Fuzzy Matching & Guidewire Cloud Integration"
        Target = "Cascade (Claimant -> Insured -> Driver) & 9-digit '0' prefix"
        Status = $status
        Duration = $dur
        Passed = $passed
        Failed = $failed
        Skipped = $skipped
        Log = $logFile
    }
}

# Test Item 5: Frontend E2E Specs (if Frontend is online)
if ($Suite -in @("All", "Frontend") -and $frontendOnline) {
    Write-Host "  -> Running Playwright Frontend E2E Specs..." -ForegroundColor White
    $logFile = Join-Path $logsDir "test_frontend_playwright.log"
    $t0 = [System.Diagnostics.Stopwatch]::StartNew()
    
    $npxCmd = "npx.cmd"
    $pwArgs = @("playwright", "test", "--reporter=list")
    
    $proc = Start-Process -FilePath $npxCmd -ArgumentList $pwArgs -WorkingDirectory (Join-Path $e2eDir "frontend") -NoNewWindow -PassThru -Wait -RedirectStandardOutput $logFile
    $t0.Stop()
    $dur = [math]::Round($t0.Elapsed.TotalSeconds, 2)
    $logContent = if (Test-Path $logFile) { Get-Content $logFile -Raw } else { "" }
    
    $passed = 0
    $failed = 0
    $skipped = 0
    if ($logContent -match '(\d+)\s+passed') { $passed = [int]$matches[1] }
    elseif ($proc.ExitCode -eq 0 -and $logContent -match '(\.{3,})') { 
        $passed = ($matches[1] | Select-String -Pattern '\.' -AllMatches).Matches.Count 
    }
    if ($logContent -match '(\d+)\s+failed') { $failed = [int]$matches[1] }
    
    $status = if ($proc.ExitCode -eq 0) { "PASSED" } else { "FAILED" }
    if ($status -eq "PASSED") {
        Write-Host "     [PASSED] in ${dur}s" -ForegroundColor Green
        $totalPassed += $passed
    } else {
        Write-Host "     [FAILED] in ${dur}s" -ForegroundColor Red
        $totalFailed += ($failed + 1)
    }
    
    $testResults += [PSCustomObject]@{
        Suite = "Next.js Frontend End-to-End Suite"
        Target = "Dashboard, Monitor, Settings, Health, Exceptions, Branding"
        Status = $status
        Duration = $dur
        Passed = $passed
        Failed = $failed
        Skipped = $skipped
        Log = $logFile
    }
}

$endTime = Get-Date
$totalDuration = [math]::Round(($endTime - $startTime).TotalSeconds, 2)

# 4. Generate Machine-Readable JSON Output
$summaryJsonPath = Join-Path $resultsDir "summary.json"
$summaryObj = [PSCustomObject]@{
    implementation_id = "IMP-2026-1031-002"
    timestamp = $endTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
    environment = $Environment
    suite = $Suite
    mode = $effectiveMode
    portal = if ($Portal) { $Portal } else { "all" }
    duration_seconds = $totalDuration
    total_passed = $totalPassed
    total_failed = $totalFailed
    total_skipped = $totalSkipped
    overall_status = if ($totalFailed -eq 0) { "PASSED" } else { "FAILED" }
    test_suites = $testResults
}
$summaryObj | ConvertTo-Json -Depth 5 | Set-Content -Path $summaryJsonPath -Encoding UTF8
Write-Host "`n[OUTPUT] Machine-readable summary saved to: $summaryJsonPath" -ForegroundColor DarkGray

# 5. Generate Standalone HTML Report
$htmlReportPath = Join-Path $reportsDir "e2e_test_report.html"

$statusBadgeClass = if ($totalFailed -eq 0) { "badge-success" } else { "badge-failure" }
$statusBadgeText = if ($totalFailed -eq 0) { "ALL TESTS PASSED" } else { "TESTS FAILED" }

$tableRows = ""
foreach ($tr in $testResults) {
    $rowClass = if ($tr.Status -eq "PASSED") { "row-pass" } else { "row-fail" }
    $badgeClass = if ($tr.Status -eq "PASSED") { "badge-pass" } else { "badge-fail" }
    $tableRows += @"
    <tr class="$rowClass">
        <td class="font-bold">$($tr.Suite)</td>
        <td>$($tr.Target)</td>
        <td><span class="badge $badgeClass">$($tr.Status)</span></td>
        <td>$($tr.Duration)s</td>
        <td class="num-pass">$($tr.Passed)</td>
        <td class="num-fail">$($tr.Failed)</td>
        <td class="num-skip">$($tr.Skipped)</td>
    </tr>
"@
}

$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UAIC RPA Orchestrator - E2E Test Execution Report</title>
    <style>
        :root {
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #243447;
            --border: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #6366f1;
            --success: #10b981;
            --fail: #ef4444;
            --warn: #f59e0b;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 32px 24px;
            font-size: 14px;
            line-height: 1.5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 24px 28px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            animation: slideDown 0.5s ease-out;
        }
        h1 { margin: 0 0 6px 0; font-size: 22px; font-weight: 700; color: #fff; letter-spacing: -0.5px; }
        .meta { color: var(--text-muted); font-size: 12px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 22px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            animation: cardFadeIn 0.6s ease-out forwards;
            opacity: 0;
            transform: translateY(12px);
        }
        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .stat-card:nth-child(4) { animation-delay: 0.4s; }
        .stat-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(99, 102, 241, 0.15);
        }
        .stat-label { 
            font-size: 11px; 
            text-transform: uppercase; 
            color: var(--text-muted); 
            font-weight: 700; 
            letter-spacing: 0.5px;
            margin-bottom: 8px; 
        }
        .stat-val { 
            font-size: 32px; 
            font-weight: 800; 
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            display: flex;
            align-items: baseline;
            gap: 4px;
        }
        .stat-val.pass { color: var(--success); }
        .stat-val.fail { color: var(--fail); }
        .stat-val.skip { color: var(--warn); }
        .stat-val.dur { color: #38bdf8; }
        
        .progress-bar-container {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 9999px;
            margin-top: 12px;
            overflow: hidden;
        }
        .progress-bar-fill {
            height: 100%;
            border-radius: 9999px;
            width: 0%;
            transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .fill-pass { background: linear-gradient(90deg, #059669, #10b981); }
        .fill-fail { background: #ef4444; }
        .fill-skip { background: #f59e0b; }
        .fill-dur { background: linear-gradient(90deg, #0284c7, #38bdf8); }

        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 24px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            animation: cardFadeIn 0.7s ease-out 0.4s forwards;
            opacity: 0;
            transform: translateY(12px);
        }
        th, td {
            padding: 14px 18px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        th {
            background: #0b1120;
            font-size: 11px;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        tbody tr:hover { background: var(--surface-hover); }
        tbody tr:last-child td { border-bottom: none; }
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }
        .badge-failure { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }
        .badge-pass { background: #064e3b; color: #6ee7b7; padding: 4px 10px; border-radius: 6px; font-size: 11px; }
        .badge-fail { background: #7f1d1d; color: #fca5a5; padding: 4px 10px; border-radius: 6px; font-size: 11px; }
        .num-pass { color: var(--success); font-weight: 700; }
        .num-fail { color: var(--fail); font-weight: 700; }
        .num-skip { color: var(--warn); font-weight: 700; }
        
        .footer {
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 36px;
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-16px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes cardFadeIn {
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>UAIC RPA Orchestrator - E2E Execution Report</h1>
                <div class="meta">
                    Execution ID: <strong>IMP-2026-1031-002</strong> &bull;
                    Environment: <strong>$Environment</strong> &bull;
                    Mode: <strong>$effectiveMode</strong> &bull;
                    Timestamp: <strong>$($endTime.ToString('yyyy-MM-dd HH:mm:ss'))</strong>
                </div>
            </div>
            <div>
                <span class="badge $statusBadgeClass" style="font-size: 13px; padding: 8px 18px;">$statusBadgeText</span>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Passed Tests</div>
                <div class="stat-val pass" id="valPassed" data-target="$totalPassed">0</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill fill-pass" id="barPassed" data-width="100%"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Failed Tests</div>
                <div class="stat-val fail" id="valFailed" data-target="$totalFailed">0</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill fill-fail" id="barFailed" data-width="$(if ($totalFailed -gt 0) { '100%' } else { '0%' })"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Skipped Tests</div>
                <div class="stat-val skip" id="valSkipped" data-target="$totalSkipped">0</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill fill-skip" id="barSkipped" data-width="$(if ($totalSkipped -gt 0) { '100%' } else { '0%' })"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Duration</div>
                <div class="stat-val dur" id="valDuration" data-target="$totalDuration" data-suffix="s">0s</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill fill-dur" id="barDuration" data-width="100%"></div>
                </div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Test Suite</th>
                    <th>Target Scope</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Skipped</th>
                </tr>
            </thead>
            <tbody>
                $tableRows
            </tbody>
        </table>

        <div class="footer">
            UAIC RPA Orchestrator &bull; Production Court Discovery & Cloud Push &bull; Playwright + Celery + FastAPI + RapidFuzz
        </div>
    </div>

    <script>
        // Smooth animated statistic counters and loading bars
        window.addEventListener('DOMContentLoaded', () => {
            const counters = [
                { id: 'valPassed', bar: 'barPassed', target: $totalPassed, suffix: '' },
                { id: 'valFailed', bar: 'barFailed', target: $totalFailed, suffix: '' },
                { id: 'valSkipped', bar: 'barSkipped', target: $totalSkipped, suffix: '' },
                { id: 'valDuration', bar: 'barDuration', target: $totalDuration, suffix: 's', decimals: 2 }
            ];

            const duration = 1200;
            const startTime = performance.now();

            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeOut = 1 - Math.pow(1 - progress, 3);

                counters.forEach(c => {
                    const el = document.getElementById(c.id);
                    if (!el) return;
                    const val = (c.target * easeOut);
                    el.textContent = (c.decimals ? val.toFixed(c.decimals) : Math.round(val)) + c.suffix;
                });

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    counters.forEach(c => {
                        const el = document.getElementById(c.id);
                        if (el) el.textContent = (c.decimals ? c.target.toFixed(c.decimals) : c.target) + c.suffix;
                    });
                }
            }

            requestAnimationFrame(animate);

            // Animate progress bars
            setTimeout(() => {
                document.querySelectorAll('.progress-bar-fill').forEach(bar => {
                    const targetWidth = bar.getAttribute('data-width');
                    if (targetWidth) bar.style.width = targetWidth;
                });
            }, 150);
        });
    </script>
</body>
</html>
"@

Set-Content -Path $htmlReportPath -Value $htmlContent -Encoding UTF8
Write-Host "[OUTPUT] HTML report successfully generated: $htmlReportPath" -ForegroundColor Green

if ($OpenReport) {
    Start-Process $htmlReportPath
}

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host " E2E Test Execution Complete! (Total Duration: ${totalDuration}s)" -ForegroundColor $(if ($totalFailed -eq 0) { "Green" } else { "Red" })
Write-Host " Passed: $totalPassed | Failed: $totalFailed | Skipped: $totalSkipped" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan

exit $(if ($totalFailed -eq 0) { 0 } else { 1 })
