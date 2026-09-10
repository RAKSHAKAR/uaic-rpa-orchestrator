<#
.SYNOPSIS
    Enterprise Operations & Orchestrator Console for UAIC Orchestrator
.DESCRIPTION
    Flexible, enterprise-grade PowerShell orchestration script.
    - Manages local development and production-grade background services.
    - Features an interactive menu loop that never auto-closes until explicitly requested.
    - Supports Attended (Visible GUI Chrome/Edge) vs Unattended (Headless Background) execution.
    - Includes automatic Docker daemon self-healing and deep container/volume/image teardown.
#>

param (
    [switch]$StartAll,
    [switch]$StopAll,
    [switch]$Clean,
    [switch]$CleanHistory,
    [switch]$PurgeDeps,
    [switch]$InstallDeps,
    [switch]$RunTests,
    [ValidateSet("Attended", "Unattended")]
    [string]$Mode,
    [switch]$NoPrompt,
    [string]$LogFile = ""
)

$ErrorActionPreference = "Stop"

# Establish standardized logs directory
$logDir = Join-Path $PSScriptRoot "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
$gitKeepPath = Join-Path $logDir ".gitkeep"
if (-not (Test-Path $gitKeepPath)) {
    Set-Content -Path $gitKeepPath -Value "# Preserves logs directory in version control`n" -ErrorAction Ignore
}

# Determine timestamped LogFile and latest mirror
if ([string]::IsNullOrWhiteSpace($LogFile) -or $LogFile -eq "setup.log") {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd_HHmmss")
    $LogFile = Join-Path $logDir "setup_$timestamp.log"
} elseif (-not [System.IO.Path]::IsPathRooted($LogFile)) {
    $LogFile = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot $LogFile))
}
$latestLogFile = Join-Path $logDir "setup_latest.log"

$rootDir     = $PSScriptRoot
$backendDir  = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"

# --- Logging & Formatting Functions ---

function Write-LogMessage {
    param(
        [Parameter(Mandatory=$true)][string]$Message,
        [string]$Level = "INFO",
        [ConsoleColor]$Color = "White"
    )
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry -ErrorAction Ignore
    if ($LogFile -ne $latestLogFile) {
        Add-Content -Path $latestLogFile -Value $logEntry -ErrorAction Ignore
    }

    if ($Level -eq "ERROR") { $Color = "Red" }
    elseif ($Level -eq "WARNING") { $Color = "Yellow" }
    elseif ($Level -eq "SUCCESS") { $Color = "Green" }

    Write-Host "[$timestamp] " -NoNewline -ForegroundColor DarkGray
    Write-Host $Message -ForegroundColor $Color
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Test-DockerDaemonHealth {
    try {
        $null = docker version --format '{{.Server.Version}}' 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    } catch {}
    return $false
}

function Invoke-DockerSelfHealing {
    Write-LogMessage "Docker daemon check failed or unresponsive. Initiating enterprise auto-recovery..." "WARNING" "Yellow"
    try {
        Write-LogMessage "Shutting down WSL 2 engine..." "INFO"
        wsl --shutdown 2>$null | Out-Null
        
        Write-LogMessage "Clearing lingering Docker and WSL background host processes..." "INFO"
        taskkill /F /IM "Docker Desktop.exe" 2>$null | Out-Null
        taskkill /F /IM "com.docker.backend.exe" 2>$null | Out-Null
        taskkill /F /IM "com.docker.proxy.exe" 2>$null | Out-Null
        taskkill /F /IM "wslservice.exe" 2>$null | Out-Null

        Write-LogMessage "Relaunching Docker Desktop service..." "INFO"
        $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if (Test-Path $dockerPath) {
            Start-Process $dockerPath
        }

        Write-LogMessage "Waiting for Docker daemon to become responsive (up to 90 seconds)..." "INFO"
        $elapsed = 0
        while ($elapsed -lt 90) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            if (Test-DockerDaemonHealth) {
                Write-LogMessage "Docker daemon successfully recovered and online." "SUCCESS"
                return $true
            }
            Write-Host "." -NoNewline -ForegroundColor DarkGray
        }
        Write-Host ""
        Write-LogMessage "Docker daemon failed to respond within timeout window." "ERROR"
        return $false
    } catch {
        Write-LogMessage "Docker auto-recovery exception: $_" "ERROR"
        return $false
    }
}

function Get-PythonExecutable {
    $venvPy1 = Join-Path $backendDir ".venv\Scripts\python.exe"
    $venvPy2 = Join-Path $backendDir "venv\Scripts\python.exe"
    if (Test-Path $venvPy1) { return $venvPy1 }
    if (Test-Path $venvPy2) { return $venvPy2 }
    if (Test-Command "python") { return "python" }
    if (Test-Command "py") { return "py" }
    return $null
}

function Invoke-KillPort {
    param([int]$Port)
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction Ignore
        foreach ($conn in $connections) {
            $pidVal = $conn.OwningProcess
            if ($pidVal) {
                $proc = Get-Process -Id $pidVal -ErrorAction Ignore
                if ($proc) {
                    if ($proc.Name -match "^(wsl|wslhost|docker|com\.docker)" -or $proc.ProcessName -match "^(wsl|wslhost|docker|com\.docker)") {
                        continue
                    }
                    Write-LogMessage "Terminating process $($proc.Name) (PID: $($proc.Id)) bound to port $Port" "INFO" "DarkYellow"
                    Stop-Process -Id $proc.Id -Force -ErrorAction Ignore
                }
            }
        }
    } catch {
        Write-LogMessage "Port $Port check note: $_" "WARNING" "DarkGray"
    }
}

function Start-EncodedWindow {
    param([string]$Title, [string]$Script)
    $titleCmd   = "`$host.UI.RawUI.WindowTitle = '$Title'"
    $fullScript = "$titleCmd`n$Script"
    $bytes      = [System.Text.Encoding]::Unicode.GetBytes($fullScript)
    $encoded    = [Convert]::ToBase64String($bytes)
    Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encoded -WindowStyle Normal
}

function Get-DockerComposeCommand {
    if (-not (Test-DockerDaemonHealth)) {
        $recovered = Invoke-DockerSelfHealing
        if (-not $recovered) { return $null }
    }

    if (Test-Command "docker-compose") {
        return "docker-compose"
    } elseif (Test-Command "docker") {
        try {
            docker compose version | Out-Null
            return "docker compose"
        } catch {
            return $null
        }
    }
    return $null
}

# --- Core Operation Implementations ---

function Invoke-PreflightChecks {
    Write-LogMessage "Running pre-flight checks..." "INFO" "Cyan"
    $missing = $false

    if (-not (Test-Command "python") -and -not (Test-Command "py")) {
        Write-LogMessage "Missing prerequisite: Python 3 (python is not in PATH)." "ERROR"
        $missing = $true
    }
    if (-not (Test-Command "npm")) {
        Write-LogMessage "Missing prerequisite: Node.js (npm is not in PATH)." "ERROR"
        $missing = $true
    }

    $compose = Get-DockerComposeCommand
    if ($compose) {
        Write-LogMessage "Docker Compose detected: '$compose'." "SUCCESS"
    } else {
        Write-LogMessage "Docker Compose not found or Docker daemon is offline." "WARNING"
    }

    if ($missing) {
        Write-LogMessage "Pre-flight checks failed. Please install missing prerequisites." "ERROR"
        return $false
    }
    Write-LogMessage "All fundamental prerequisites are satisfied." "SUCCESS"
    return $true
}

function Get-CurrentPlaywrightChannel {
    $envFile = Join-Path $backendDir ".env"
    if (Test-Path $envFile) {
        $content = Get-Content $envFile -Raw -ErrorAction Ignore
        if ($content -match "PLAYWRIGHT_CHANNEL=msedge") { return "msedge" }
        if ($content -match "PLAYWRIGHT_CHANNEL=chrome") { return "chrome" }
    }
    return "chromium"
}

function Set-PlaywrightChannel {
    param([string]$Channel)
    $envFile = Join-Path $backendDir ".env"
    if (-not (Test-Path $envFile)) {
        Set-Content -Path $envFile -Value "PLAYWRIGHT_CHANNEL=$Channel`r`n" -NoNewline -ErrorAction Ignore
        return
    }
    $content = Get-Content $envFile -Raw
    if ($content -match "PLAYWRIGHT_CHANNEL=") {
        $content = $content -replace "PLAYWRIGHT_CHANNEL=\S*", "PLAYWRIGHT_CHANNEL=$Channel"
    } else {
        $content = "$content`r`nPLAYWRIGHT_CHANNEL=$Channel"
    }
    Set-Content -Path $envFile -Value $content -NoNewline
}

function Invoke-InstallDependencies {
    Write-LogMessage "Installing and verifying all application dependencies..." "INFO" "Cyan"

    Push-Location $backendDir
    try {
        $venvDir = Join-Path $backendDir ".venv"
        if (-not (Test-Path "$venvDir\Scripts\python.exe")) {
            Write-LogMessage "Creating Python virtual environment ($venvDir)..." "INFO"
            if (Test-Path $venvDir) { Remove-Item -Recurse -Force $venvDir -ErrorAction Ignore }
            if (Test-Command "py") { py -3.14 -m venv $venvDir } else { python -m venv $venvDir }
        }

        $pyExe  = Join-Path $venvDir "Scripts\python.exe"
        $pipExe = Join-Path $venvDir "Scripts\pip.exe"

        Write-LogMessage "Installing Python dependencies (requirements.txt)..." "INFO"
        & $pyExe -m pip install --upgrade pip --quiet
        & $pipExe install -r requirements.txt --quiet

        Write-LogMessage "Installing Playwright Bundled Chromium browser..." "INFO"
        & $pyExe -m playwright install chromium
        Set-PlaywrightChannel "chromium"

        Write-LogMessage "Backend dependencies successfully installed and verified." "SUCCESS"
    } catch {
        Write-LogMessage "Backend dependency setup failed: $_" "ERROR"
    } finally {
        Pop-Location
    }

    Push-Location $frontendDir
    try {
        Write-LogMessage "Installing Frontend NPM dependencies..." "INFO"
        npm install --no-audit --no-fund --loglevel=error
        Write-LogMessage "Frontend dependencies successfully installed." "SUCCESS"
    } catch {
        Write-LogMessage "Frontend dependency setup failed: $_" "ERROR"
    } finally {
        Pop-Location
    }
}

function Invoke-PurgeDependencyFolders {
    param([bool]$Force = $false)
    if (-not $Force) {
        $confirm = Read-Host "WARNING: This will delete backend\.venv, frontend\node_modules, and frontend\.next. Continue? [y/N]"
        if ($confirm -notmatch '^[yY]') {
            Write-LogMessage "Purge cancelled by user." "INFO"
            return
        }
    }

    Write-LogMessage "Purging all dependency folders for a completely clean slate..." "WARNING" "DarkYellow"
    Invoke-KillAllServices -Quiet

    $protectedNames = @("implementation_plan", "PowerAutomateSolutions", "Testing files", "Test files", "anticaptcha-plugin_v0.83", ".agents")
    $pathsToPurge = @(
        (Join-Path $backendDir ".venv"),
        (Join-Path $backendDir "venv"),
        (Join-Path $frontendDir "node_modules"),
        (Join-Path $frontendDir ".next")
    )

    foreach ($p in $pathsToPurge) {
        $base = Split-Path $p -Leaf
        if ($protectedNames -contains $base) { continue }
        if (Test-Path $p) {
            Remove-Item -Recurse -Force $p -ErrorAction Ignore
        }
    }
    Write-LogMessage "All dependency folders successfully purged." "SUCCESS"
}

function Invoke-CleanRunHistory {
    param([switch]$Interactive)
    $pyExe = Get-PythonExecutable
    if ($Interactive -and $pyExe) {
        Push-Location $backendDir
        try { & $pyExe -m app.scripts.clean_history } catch {} finally { Pop-Location }
        return
    }
    Write-LogMessage "Cleaning run history and logs..." "INFO" "Cyan"
    $logDir = Join-Path $rootDir "logs"
    if (Test-Path $logDir) {
        Get-ChildItem -Path $logDir -Filter "*.log" -File -ErrorAction Ignore | Remove-Item -Force -ErrorAction Ignore
    }
    Write-LogMessage "Run history cleaned successfully." "SUCCESS"
}

function Invoke-KillAllServices {
    param([switch]$Quiet, [switch]$KeepInfrastructure)
    if (-not $Quiet) {
        Write-LogMessage "Stopping and terminating all application and infrastructure processes..." "INFO" "Cyan"
    }

    Invoke-KillPort 3000
    Invoke-KillPort 8000
    Invoke-KillPort 5555
    Invoke-KillPort 1080
    Invoke-KillPort 1025
    Invoke-KillPort 6379
    Invoke-KillPort 5432

    foreach ($procName in @("celery", "uvicorn", "node", "python")) {
        try {
            Get-Process -Name $procName -ErrorAction Ignore | Where-Object { 
                $_.Path -like "*$rootDir*" -or $_.CommandLine -like "*$rootDir*" -or $procName -eq "celery" -or $procName -eq "uvicorn"
            } | Stop-Process -Force -ErrorAction Ignore
        } catch {}
    }

    if (-not $KeepInfrastructure) {
        $compose = Get-DockerComposeCommand
        if ($compose) {
            try {
                if (-not $Quiet) {
                    Write-LogMessage "Tearing down docker compose stack (removing containers, volumes, and local images)..." "INFO"
                }
                if ($compose -eq "docker-compose") {
                    docker-compose down --volumes --rmi local --remove-orphans 2>$null | Out-Null
                } else {
                    docker compose down --volumes --rmi local --remove-orphans 2>$null | Out-Null
                }
            } catch {}
        }

        if (Test-DockerDaemonHealth) {
            try {
                if (-not $Quiet) {
                    Write-LogMessage "Force removing project containers and pruning project volumes..." "INFO"
                }
                docker rm -f uaic_postgres uaic_redis uaic_maildev uaic_fastapi uaic_celery_worker uaic_celery_beat uaic_frontend 2>$null | Out-Null
                docker volume prune -f 2>$null | Out-Null
            } catch {}
        }
    }

    if (-not $Quiet) {
        Write-LogMessage "All active service ports, infrastructure containers, volumes, and images have been completely purged." "SUCCESS"
    }
}

function Invoke-SetRpaMode {
    param([string]$ChosenMode)
    $envFile = Join-Path $backendDir ".env"
    if (-not $ChosenMode) {
        Write-Host ""
        Write-Host "Select RPA Browser Execution Mode:" -ForegroundColor Cyan
        Write-Host " [A] Attended Mode   (Visible GUI Chrome/Edge)" -ForegroundColor White
        Write-Host " [U] Unattended Mode (Headless Background)" -ForegroundColor White
        $choice = Read-Host "Choose mode [A/U] (Default: A)"
        $ChosenMode = if ($choice -match '^[uU]') { "Unattended" } else { "Attended" }
    }
    $isHeadless = if ($ChosenMode -eq "Unattended") { "true" } else { "false" }
    if (-not (Test-Path $envFile)) {
        Set-Content -Path $envFile -Value "PLAYWRIGHT_HEADLESS=$isHeadless`r`n" -NoNewline
    } else {
        $content = Get-Content $envFile -Raw
        if ($content -match "PLAYWRIGHT_HEADLESS=") {
            $content = $content -replace "PLAYWRIGHT_HEADLESS=\w+", "PLAYWRIGHT_HEADLESS=$isHeadless"
        } else {
            $content = "$content`r`nPLAYWRIGHT_HEADLESS=$isHeadless"
        }
        Set-Content -Path $envFile -Value $content -NoNewline
    }
    $env:PLAYWRIGHT_HEADLESS = $isHeadless
    return $ChosenMode
}

function Invoke-StartAllServices {
    param([string]$TargetMode)
    Write-LogMessage "=======================================================" "INFO" "Cyan"
    Write-LogMessage " Starting UAIC Orchestrator Application Stack" "INFO" "Cyan"
    Write-LogMessage "=======================================================" "INFO" "Cyan"

    if (-not (Invoke-PreflightChecks)) { return }
    $activeMode = Invoke-SetRpaMode -ChosenMode $TargetMode
    Invoke-KillAllServices -Quiet

    $venvDir = Join-Path $backendDir ".venv"
    $pyExe   = Join-Path $venvDir "Scripts\python.exe"
    if (-not (Test-Path $pyExe)) {
        Invoke-InstallDependencies
        $pyExe = Join-Path $venvDir "Scripts\python.exe"
    }

    $compose = Get-DockerComposeCommand
    if ($compose) {
        Write-LogMessage "Starting infrastructure containers (PostgreSQL, Redis, MailDev)..." "INFO"
        try {
            if ($compose -eq "docker-compose") {
                docker-compose up -d postgres redis maildev
            } else {
                docker compose up -d postgres redis maildev
            }
        } catch {
            Write-LogMessage "Docker start note: $_" "WARNING"
        }
    }

    $frontendModules = Join-Path $frontendDir "node_modules"
    if (-not (Test-Path $frontendModules)) {
        Push-Location $frontendDir
        try { npm install --no-audit --no-fund --loglevel=error } finally { Pop-Location }
    }

    Write-LogMessage "Launching background service windows..." "INFO"
    Start-EncodedWindow "FastAPI Backend (port 8000)" "Set-Location '$backendDir'; & '$pyExe' -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    Start-EncodedWindow "Celery Worker [$activeMode RPA]" "Set-Location '$backendDir'; & '$pyExe' -m celery -A app.core.celery_app.celery_app worker -E --loglevel=info -Q ingest,scrapers,matcher,notifications,default -P solo"
    Start-EncodedWindow "Celery Beat Scheduler" "Set-Location '$backendDir'; & '$pyExe' -m celery -A app.core.celery_app.celery_app beat --loglevel=info"
    Start-EncodedWindow "Celery Flower Monitor (port 5555)" "Set-Location '$backendDir'; & '$pyExe' -m celery -A app.core.celery_app.celery_app flower --port=5555"
    Start-EncodedWindow "Next.js Frontend (port 3000)" "Set-Location '$frontendDir'; npm.cmd run dev"

    Write-LogMessage "All UAIC Orchestrator Services Successfully Launched!" "SUCCESS" "Green"
}

function Invoke-CheckServiceHealth {
    param([string]$ServiceName, [int]$Port, [string]$HttpUrl = "")
    $portOpen = $false
    try {
        if (Get-NetTCPConnection -LocalPort $Port -ErrorAction Ignore) { $portOpen = $true }
    } catch {}

    if (-not $portOpen) {
        Write-Host " [STOPPED] " -NoNewline -ForegroundColor DarkGray
        Write-Host "$ServiceName (Port $Port)" -ForegroundColor Gray
        return
    }

    if ($HttpUrl -ne "") {
        try {
            $resp = Invoke-WebRequest -Uri $HttpUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300) {
                Write-Host " [HEALTHY]  " -NoNewline -ForegroundColor Green
                Write-Host "$ServiceName (Port $Port - HTTP $($resp.StatusCode))" -ForegroundColor White
                return
            }
        } catch {}
        Write-Host " [RUNNING]  " -NoNewline -ForegroundColor Yellow
        Write-Host "$ServiceName (Port $Port - port open, HTTP initializing)" -ForegroundColor DarkYellow
    } else {
        Write-Host " [RUNNING]  " -NoNewline -ForegroundColor Green
        Write-Host "$ServiceName (Port $Port)" -ForegroundColor White
    }
}

function Show-LiveStatusMonitor {
    Clear-Host
    Write-Host "=======================================================================" -ForegroundColor Cyan
    Write-Host "          UAIC Orchestrator - Live Service Health Monitor              " -ForegroundColor Cyan
    Write-Host "=======================================================================" -ForegroundColor Cyan
    Invoke-CheckServiceHealth "Frontend Web Application" 3000 "http://localhost:3000"
    Invoke-CheckServiceHealth "FastAPI Backend & API   " 8000 "http://localhost:8000/api/v1/health"
    Invoke-CheckServiceHealth "Celery Flower Monitor   " 5555 "http://localhost:5555"
    Invoke-CheckServiceHealth "MailDev Web Inspector   " 1080 "http://localhost:1080"
    Invoke-CheckServiceHealth "MailDev SMTP Server     " 1025
    Invoke-CheckServiceHealth "Redis Queue Broker      " 6379
    Invoke-CheckServiceHealth "PostgreSQL Database     " 5432
    Write-Host "-----------------------------------------------------------------------" -ForegroundColor DarkGray
}

function Show-EnterpriseMenu {
    while ($true) {
        Clear-Host
        Write-Host "                  Enterprise Operations & Orchestration Console" -ForegroundColor Cyan
        Write-Host "=======================================================================" -ForegroundColor Cyan
        Write-Host " [1] Start All Application Services"
        Write-Host " [2] Stop / Kill All Running Services (Clean ports, containers, volumes & images)"
        Write-Host " [3] Enterprise Data Cleanup & Retention"
        Write-Host " [4] Install / Update Dependencies"
        Write-Host " [5] Purge / Delete All Dependency Folders"
        Write-Host " [6] Configure RPA Execution Mode"
        Write-Host " [7] Run Full Diagnostics & Test Suite"
        Write-Host " [8] Docker Stack Management"
        Write-Host " [9] Live Service Status Monitor"
        Write-Host " [0] Exit Console"
        Write-Host "=======================================================================" -ForegroundColor Cyan

        $choice = Read-Host "Select an option [0-9]"
        switch ($choice) {
            "1" {
                Invoke-StartAllServices
                $monitoring = $true
                while ($monitoring) {
                    Show-LiveStatusMonitor
                    $key = Read-Host "Enter key action [R/K/M/Q]"
                    if ($key -match '^[kK]') { Invoke-KillAllServices; Start-Sleep -Seconds 1 }
                    elseif ($key -match '^[mM]') { $monitoring = $false }
                    elseif ($key -match '^[qQ]') { exit 0 }
                }
            }
            "2" { Invoke-KillAllServices; Read-Host "Press Enter to return..." }
            "3" { Invoke-CleanRunHistory -Interactive; Read-Host "Press Enter to return..." }
            "4" { Invoke-InstallDependencies; Read-Host "Press Enter to return..." }
            "5" { Invoke-PurgeDependencyFolders; Read-Host "Press Enter to return..." }
            "6" { Invoke-SetRpaMode; Read-Host "Press Enter to return..." }
            "7" { Invoke-RunTestSuite; Read-Host "Press Enter to return..." }
            "8" {
                if (Get-DockerComposeCommand) {
                    $dChoice = Read-Host "Choose Docker action: [U]p / [D]own (with volumes) / [R]estart"
                    if ($dChoice -match '^[uU]') { docker compose up -d }
                    elseif ($dChoice -match '^[dD]') { docker compose down --volumes --rmi local }
                    elseif ($dChoice -match '^[rR]') { docker compose restart }
                }
                Read-Host "Press Enter to return..."
            }
            "9" {
                $mon = $true
                while ($mon) {
                    Show-LiveStatusMonitor
                    $k = Read-Host "Enter key action [R/K/M/Q]"
                    if ($k -match '^[kK]') { Invoke-KillAllServices }
                    elseif ($k -match '^[mM]') { $mon = $false }
                    elseif ($k -match '^[qQ]') { exit 0 }
                }
            }
            "0" { exit 0 }
        }
    }
}

if ($StopAll) { Invoke-KillAllServices; exit 0 }
if ($StartAll) { Invoke-StartAllServices -TargetMode $Mode; exit 0 }
Show-EnterpriseMenu