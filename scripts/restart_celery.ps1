$backendDir = "D:\scratch\Bot_UAIC\backend"
$pyExe = "D:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe"

Write-Host "Finding and terminating stale Celery processes..." -ForegroundColor Yellow
$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*celery*" -and $_.Name -like "*python*" }
foreach ($p in $procs) {
    Write-Host "Killing PID $($p.ProcessId)..."
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1

Write-Host "Starting fresh Celery Worker window..." -ForegroundColor Green
$titleCmd = "`$host.UI.RawUI.WindowTitle = 'Celery Worker [Attended GUI RPA]'"
$fullScript = "$titleCmd`nSet-Location '$backendDir'`n& '$pyExe' -m celery -A app.core.celery_app.celery_app worker -E --loglevel=info -Q ingest,scrapers,matcher,notifications,default --pool=threads --concurrency=10"
$bytes = [System.Text.Encoding]::Unicode.GetBytes($fullScript)
$encoded = [Convert]::ToBase64String($bytes)
Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encoded -WindowStyle Normal

Write-Host "Celery worker launched in interactive window." -ForegroundColor Green
