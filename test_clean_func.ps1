function Invoke-CleanRunHistory {
    param([switch]$Interactive)
    $pyExe = Get-PythonExecutable
    if ($Interactive -and $pyExe) {
        Push-Location $backendDir
        try { 
            # Rebuild native PowerShell UI
            Write-Host "=======================================================================" -ForegroundColor Cyan
            Write-Host "                  ENTERPRISE DATA CLEANUP" -ForegroundColor Cyan
            Write-Host "=======================================================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Select Data Categories (comma-separated, e.g., 1,3,6,7 or 'A' for All):"
            Write-Host " [1] Claim / Claim Automation Data"
            Write-Host " [2] Work Queue Data"
            Write-Host " [3] Scraped Court Case Data"
            Write-Host " [4] Fuzzy Match Data"
            Write-Host " [5] Guidewire Activity Data"
            Write-Host " [6] Outbound Notification Data"
            Write-Host " [7] Notification Delivery History"
            Write-Host " [8] Stage Execution Telemetry"
            Write-Host " [9] Bot / Scraper Execution History"
            Write-Host "[10] Dashboard / Analytics Data"
            Write-Host "[11] Application Run History"
            Write-Host "[12] Application Logs"
            Write-Host "[13] Scraper Logs"
            Write-Host "[14] Temporary Files / Caches"
            Write-Host "[15] Generated Export Files"
            Write-Host "[16] Redis Runtime Data"
            Write-Host "[17] All Operational Data"
            Write-Host ""
            $catChoice = Read-Host "Enter selection(s)"
            
            Write-Host ""
            Write-Host "Select Time Scope:"
            Write-Host " [1] Current Month"
            Write-Host " [2] Previous Month"
            Write-Host " [3] Last N Days"
            Write-Host " [4] Last N Weeks"
            Write-Host " [5] Last N Months"
            Write-Host " [6] Last N Years"
            Write-Host " [7] Custom Date Range"
            Write-Host " [8] Before Specific Date"
            Write-Host ""
            $timeChoice = Read-Host "Enter selection (Default: 1)"
            if (-not $timeChoice) { $timeChoice = "1" }
            
            $catArgs = ""
            if ($catChoice -match '^[aA]') {
                $catArgs = "all_operational"
            } else {
                $catMap = @{
                    "1"="claims"; "2"="queue"; "3"="court_cases"; "4"="fuzzy_matches";
                    "5"="guidewire_activities"; "6"="notifications"; "7"="notification_deliveries";
                    "8"="telemetry"; "9"="bot_history"; "10"="dashboard_metrics";
                    "11"="run_history"; "12"="app_logs"; "13"="scraper_logs";
                    "14"="temp_caches"; "15"="generated_exports"; "16"="redis_runtime";
                    "17"="all_operational"
                }
                $selectedCats = @()
                foreach ($c in $catChoice.Split(',')) {
                    $c = $c.Trim()
                    if ($catMap.ContainsKey($c)) {
                        $selectedCats += $catMap[$c]
                    }
                }
                $catArgs = $selectedCats -join ","
            }
            
            $timeArg = "current_month"
            $extraArgs = ""
            switch ($timeChoice) {
                "2" { $timeArg = "previous_month" }
                "3" { 
                    $timeArg = "last_n_days" 
                    $n = Read-Host "Enter number of days"
                    $extraArgs = "--n-units $n"
                }
                "4" {
                    $timeArg = "last_n_weeks"
                    $n = Read-Host "Enter number of weeks"
                    $extraArgs = "--n-units $n"
                }
                "5" {
                    $timeArg = "last_n_months"
                    $n = Read-Host "Enter number of months"
                    $extraArgs = "--n-units $n"
                }
                "6" {
                    $timeArg = "last_n_years"
                    $n = Read-Host "Enter number of years"
                    $extraArgs = "--n-units $n"
                }
                "7" {
                    $timeArg = "custom_range"
                    $start = Read-Host "Enter start date (YYYY-MM-DD)"
                    $end = Read-Host "Enter end date (YYYY-MM-DD)"
                    $extraArgs = "--start-date $start --end-date $end"
                }
                "8" {
                    $timeArg = "before_date"
                    $before = Read-Host "Enter cutoff date (YYYY-MM-DD)"
                    $extraArgs = "--before-date $before"
                }
                default { $timeArg = "current_month" }
            }
            
            Write-Host ""
            Write-Host "=======================================================================" -ForegroundColor Cyan
            Write-Host "                    CLEANUP PREVIEW" -ForegroundColor Cyan
            Write-Host "=======================================================================" -ForegroundColor Cyan
            & $pyExe -m app.scripts.clean_history --dry-run --categories $catArgs --time-scope $timeArg $extraArgs
            
            Write-Host ""
            Write-Host "WARNING: This operation will permanently delete the selected data." -ForegroundColor Yellow
            $confirm = Read-Host "Continue? [Y/N]"
            if ($confirm -match '^[yY]') {
                Write-Host ""
                & $pyExe -m app.scripts.clean_history --categories $catArgs --time-scope $timeArg $extraArgs --confirm
            } else {
                Write-Host "Operation cancelled." -ForegroundColor Yellow
            }
        } catch {} finally { Pop-Location }
        return
    }
    $logDir = Join-Path $rootDir "logs"
    if (Test-Path $logDir) {
        Get-ChildItem -Path $logDir -Filter "*.log" -File -ErrorAction Ignore | Remove-Item -Force -ErrorAction Ignore
    }
    Write-LogMessage "Run history cleaned." "SUCCESS"
}
