# Launch Chrome in Attended GUI mode with AntiCaptcha loaded and Florida portals open

$repoRoot = "C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC"
$chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$extPath = "$repoRoot\anticaptcha-plugin_v0.83"
$profileDir = "$repoRoot\backend\data\browser_profile\chrome"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  LAUNCHING CHROME WITH ANTICAPTCHA IN ATTENDED GUI MODE" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Clean existing process tree locking this profile if any
$pSearch = $profileDir.ToLower()
Get-CimInstance Win32_Process -Filter "name = 'chrome.exe'" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -and $_.CommandLine.ToLower().Contains($pSearch) } | 
    ForEach-Object {
        Write-Host "Stopping orphan chrome PID: $($_.ProcessId)" -ForegroundColor Yellow
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

Start-Sleep -Milliseconds 500

# 2. Remove lock files
if (Test-Path $profileDir) {
    Get-ChildItem -Path $profileDir -Filter "Singleton*" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path $profileDir -Filter "lockfile" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
}

# 3. Launch Chrome with AntiCaptcha extension and the 3 Florida portals
$urls = @(
    "https://www.browardclerk.org/",
    "https://hover.hillsclerk.com/",
    "https://www2.miamidadeclerk.gov/ocs"
)

$argList = @(
    "--user-data-dir=$profileDir",
    "--load-extension=$extPath",
    "--disable-extensions-except=$extPath",
    "--remote-debugging-port=9222",
    "--no-first-run",
    "--no-default-browser-check",
    "--start-maximized"
) + $urls

Write-Host "Executable: $chromeExe" -ForegroundColor Green
Write-Host "Extension:  $extPath" -ForegroundColor Green
Write-Host "Profile:    $profileDir" -ForegroundColor Green
Write-Host "Opening Portals:" -ForegroundColor Green
Write-Host "  Tab 1: https://www.browardclerk.org/" -ForegroundColor White
Write-Host "  Tab 2: https://hover.hillsclerk.com/" -ForegroundColor White
Write-Host "  Tab 3: https://www2.miamidadeclerk.gov/ocs" -ForegroundColor White

Start-Process -FilePath $chromeExe -ArgumentList $argList

Write-Host "Waiting for Chrome window initialization..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Verify port 9222 is listening
$portCheck = Get-NetTCPConnection -LocalPort 9222 -State Listen -ErrorAction SilentlyContinue
if ($portCheck) {
    Write-Host "[SUCCESS] Chrome is running on screen with AntiCaptcha loaded and remote debugging on port 9222!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Port 9222 not yet detected, checking process..." -ForegroundColor Yellow
}
