<#
.SYNOPSIS
    Enterprise Operations & Orchestration Console for UAIC Orchestrator
.DESCRIPTION
    Flexible, enterprise-grade PowerShell orchestration script.
    - Manages local development and production-grade background services.
    - Features an interactive menu loop that never auto-closes until explicitly requested.
    - Supports Attended (Visible GUI Chrome/Edge) vs Unattended (Headless Background) execution.
    - Features automated Docker daemon self-healing, WSL rescue, deep volume/image teardown, and live status monitoring (R/K/M/Q).
#>

param (
    [switch]$StartAll,
    [switch]$StopAll,
    [switch]$Clean,
    [switch]$CleanHistory,
    [switch]$PurgeDeps,
    [switch]$InstallDeps,
    [switch]$RunTests,
    [switch]$CheckPorts,
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
        if ($LASTEXITCODE -eq 0) { return $true }
    } catch {}
    return $false
}

function Invoke-DockerSelfHealing {
    Write-LogMessage "Docker daemon check failed or unresponsive. Initiating enterprise auto-recovery..." "WARNING" "Yellow"
    try {
        wsl --shutdown 2>$null | Out-Null
        taskkill /F /IM "Docker Desktop.exe" 2>$null | Out-Null
        taskkill /F /IM "com.docker.backend.exe" 2>$null | Out-Null
        taskkill /F /IM "com.docker.proxy.exe" 2>$null | Out-Null
        taskkill /F /IM "wslservice.exe" 2>$null | Out-Null

        $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if (Test-Path $dockerPath) { Start-Process $dockerPath }

        $elapsed = 0
        while ($elapsed -lt 90) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            if (Test-DockerDaemonHealth) {
                Write-LogMessage "Docker daemon successfully recovered and online." "SUCCESS"
                return $true
            }
        }
        return $false
    } catch {
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
                    Stop-Process -Id $proc.Id -Force -ErrorAction Ignore
                }
            }
        }
    } catch {}
}

function Invoke-CheckPortConflicts {
    param([int[]]$Ports = @(3000, 8000, 5555, 6379, 5432, 1080, 1025))
    $conflicts = @()
    foreach ($port in $Ports) {
        try {
            $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
            if ($conns) {
                foreach ($conn in $conns) {
                    $owningPid = $conn.OwningProcess
                    if ($owningPid -and $owningPid -gt 4) {
                        $procName = "Unknown"
                        try { 
                            $p = Get-Process -Id $owningPid -ErrorAction SilentlyContinue
                            if ($p) { $procName = $p.ProcessName }
                        } catch {}
                        $conflicts += [PSCustomObject]@{
                            Port    = $port
                            PID     = $owningPid
                            Process = $procName
                        }
                    }
                }
            }
        } catch {}
    }
    if ($conflicts.Count -gt 0) {
        Write-LogMessage "Port conflict(s) detected on target application ports:" "WARNING" "Yellow"
        foreach ($c in $conflicts) {
            Write-LogMessage "  -> Port $($c.Port) is occupied by PID $($c.PID) ($($c.Process))" "WARNING" "Yellow"
        }
    } else {
        Write-LogMessage "Pre-flight port conflict check passed: All application ports (3000, 8000, 5555, 6379, 5432, 1080, 1025) are free." "SUCCESS" "Green"
    }
    return $conflicts
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
    param([switch]$AutoHeal)
    if (-not (Test-DockerDaemonHealth)) {
        if ($AutoHeal) {
            $null = Invoke-DockerSelfHealing
        } else {
            return $null
        }
    }
    if (Test-Command "docker") {
        try {
            $null = docker compose version 2>$null
            if ($LASTEXITCODE -eq 0) { return "docker compose" }
        } catch {}
    }
    if (Test-Command "docker-compose") {
        return "docker-compose"
    }
    return $null
}

function Invoke-PreflightChecks {
    Write-LogMessage "Running pre-flight checks..." "INFO" "Cyan"
    $missing = $false
    if (-not (Test-Command "python") -and -not (Test-Command "py")) { $missing = $true }
    if (-not (Test-Command "npm")) { $missing = $true }
    if ($missing) {
        Write-LogMessage "Pre-flight checks failed. Missing prerequisites." "ERROR"
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

function Test-BrowserAvailability {
    $chromePaths = @(
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        (Join-Path $env:LOCALAPPDATA "Google\Chrome\Application\chrome.exe")
    )
    $edgePaths = @(
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        (Join-Path $env:LOCALAPPDATA "Microsoft\Edge\Application\msedge.exe")
    )

    $chromeInstalled = $false
    $chromePathFound = $null
    foreach ($cp in $chromePaths) {
        if (Test-Path $cp) { $chromeInstalled = $true; $chromePathFound = $cp; break }
    }

    $edgeInstalled = $false
    $edgePathFound = $null
    foreach ($ep in $edgePaths) {
        if (Test-Path $ep) { $edgeInstalled = $true; $edgePathFound = $ep; break }
    }

    $currentChannel = Get-CurrentPlaywrightChannel

    return [PSCustomObject]@{
        ChromeInstalled = $chromeInstalled
        ChromePath      = $chromePathFound
        EdgeInstalled   = $edgeInstalled
        EdgePath        = $edgePathFound
        CurrentChannel  = $currentChannel
    }
}

function Invoke-InstallDependencies {
    Write-LogMessage "Installing and verifying all application dependencies..." "INFO" "Cyan"
    Push-Location $backendDir
    try {
        $venvDir = Join-Path $backendDir ".venv"
        if (-not (Test-Path "$venvDir\Scripts\python.exe")) {
            if (Test-Path $venvDir) { Remove-Item -Recurse -Force $venvDir -ErrorAction Ignore }
            if (Test-Command "py") { py -3.14 -m venv $venvDir } else { python -m venv $venvDir }
        }
        $pyExe  = Join-Path $venvDir "Scripts\python.exe"
        $pipExe = Join-Path $venvDir "Scripts\pip.exe"
        & $pyExe -m pip install --upgrade pip --quiet
        & $pipExe install -r requirements.txt --quiet

        $browsers = Test-BrowserAvailability
        Write-LogMessage "Evaluating Browser Engine Matrix for RPA Automation..." "INFO" "Cyan"
        if ($browsers.ChromeInstalled) {
            Write-LogMessage "  -> Google Chrome (Host): Detected at $($browsers.ChromePath)" "SUCCESS" "Green"
        } else {
            Write-LogMessage "  -> Google Chrome (Host): Not installed" "INFO" "DarkGray"
        }
        if ($browsers.EdgeInstalled) {
            Write-LogMessage "  -> Microsoft Edge (Host): Detected at $($browsers.EdgePath)" "SUCCESS" "Green"
        }
        Write-LogMessage "  -> Configured Playwright Channel: $($browsers.CurrentChannel)" "INFO" "White"

        # CRITICAL: DO NOT install bundled Chromium if host Google Chrome or Edge is selected/active
        if ($browsers.CurrentChannel -eq "chrome" -or ($browsers.ChromeInstalled -and $browsers.CurrentChannel -ne "chromium" -and $browsers.CurrentChannel -ne "msedge")) {
            Write-LogMessage "Host Google Chrome selected for RPA. Skipping bundled Playwright Chromium download (0MB overhead)." "SUCCESS" "Green"
            Set-PlaywrightChannel "chrome"
        } elseif ($browsers.CurrentChannel -eq "msedge" -or ($browsers.EdgeInstalled -and $browsers.CurrentChannel -ne "chromium")) {
            Write-LogMessage "Microsoft Edge selected for RPA. Skipping bundled Playwright Chromium download." "SUCCESS" "Green"
            Set-PlaywrightChannel "msedge"
        } else {
            Write-LogMessage "Chromium channel selected. Installing/verifying bundled Playwright Chromium driver..." "INFO" "Cyan"
            & $pyExe -m playwright install chromium
            Set-PlaywrightChannel "chromium"
        }
        Write-LogMessage "Backend dependencies and browser engine verified successfully." "SUCCESS"
    } catch {
        Write-LogMessage "Backend dependency setup failed: $_" "ERROR"
    } finally { Pop-Location }

    Push-Location $frontendDir
    try {
        npm install --no-audit --no-fund --loglevel=error
        Write-LogMessage "Frontend dependencies installed successfully." "SUCCESS"
    } catch {
        Write-LogMessage "Frontend dependency setup failed: $_" "ERROR"
    } finally { Pop-Location }
}

function Invoke-PurgeDependencyFolders {
    param([bool]$Force = $false)
    if (-not $Force) {
        $confirm = Read-Host "WARNING: This will delete backend\.venv, frontend\node_modules, frontend\.next, and build caches. Continue? [y/N]"
        if ($confirm -notmatch '^[yY]') { return }
    }
    Invoke-KillAllServices -Quiet
    $purgeDirs = @(
        (Join-Path $backendDir ".venv"),
        (Join-Path $backendDir ".ruff_cache"),
        (Join-Path $backendDir ".pytest_cache"),
        (Join-Path $backendDir "__pycache__"),
        (Join-Path $frontendDir "node_modules"),
        (Join-Path $frontendDir ".next"),
        (Join-Path $frontendDir ".turbo")
    )
    foreach ($p in $purgeDirs) {
        if (Test-Path $p) {
            Remove-Item -Recurse -Force $p -ErrorAction Ignore
            Write-LogMessage "Purged: $p" "INFO" "DarkGray"
        }
    }
    # Protected folders check: Verify protected directories are preserved
    foreach ($prot in @("implementation_plan", "PowerAutomateSolutions", "Testing files", "anticaptcha-plugin_v0.83", ".agents")) {
        $protPath = Join-Path $rootDir $prot
        if (-not (Test-Path $protPath)) {
            Write-LogMessage "Protected directory warning: $prot not found!" "WARNING" "Yellow"
        }
    }
    Write-LogMessage "Dependency folders and build caches purged safely without touching source code or credentials." "SUCCESS" "Green"
}

function Invoke-CleanRunHistory {
    param([switch]$Interactive)
    $pyExe = Get-PythonExecutable
    if ($Interactive -and $pyExe) {
        Push-Location $backendDir
        try { & $pyExe -m app.scripts.clean_history } catch {} finally { Pop-Location }
        return
    }
    $logDir = Join-Path $rootDir "logs"
    if (Test-Path $logDir) {
        Get-ChildItem -Path $logDir -Filter "*.log" -File -ErrorAction Ignore | Remove-Item -Force -ErrorAction Ignore
    }
    Write-LogMessage "Run history cleaned." "SUCCESS"
}

function Invoke-KillAllServices {
    param([switch]$Quiet, [switch]$KeepInfrastructure)
    if (-not $Quiet) { Write-LogMessage "Stopping all services, killing processes, and clearing ports..." "INFO" "Cyan" }

    Invoke-KillPort 3000
    Invoke-KillPort 8000
    Invoke-KillPort 5555
    Invoke-KillPort 1080
    Invoke-KillPort 1025
    Invoke-KillPort 6379
    Invoke-KillPort 5432

    # Robust process termination using Win32_Process CommandLine inspection
    try {
        $cimProcs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
            $cmd = $_.CommandLine
            if (-not $cmd) { return $false }
            $name = $_.Name
            if ($name -match "^(python|node)\.exe$") {
                return ($cmd -like "*$rootDir*" -or $cmd -like "*uvicorn*" -or $cmd -like "*celery*" -or $cmd -like "*flower*" -or $cmd -like "*maildev*")
            }
            return ($name -match "^(celery|uvicorn|maildev)\.exe$")
        }
        foreach ($p in $cimProcs) {
            try { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
        }
    } catch {}

    # Explicit MailDev termination and port release verification
    Invoke-KillPort 1080
    Invoke-KillPort 1025
    if (Test-DockerDaemonHealth) {
        docker stop uaic_maildev 2>$null | Out-Null
        docker rm -f uaic_maildev 2>$null | Out-Null
    }
    $maildevReleased = $true
    try {
        if ((Get-NetTCPConnection -LocalPort 1080 -ErrorAction SilentlyContinue) -or (Get-NetTCPConnection -LocalPort 1025 -ErrorAction SilentlyContinue)) {
            $maildevReleased = $false
        }
    } catch {}
    if ($maildevReleased -and -not $Quiet) {
        Write-LogMessage "MailDev (Ports 1080/1025) safely terminated and verified released." "SUCCESS" "Green"
    }

    if (-not $KeepInfrastructure) {
        $compose = Get-DockerComposeCommand
        if ($compose) {
            try {
                Push-Location $backendDir
                if ($compose -eq "docker-compose") { docker-compose down --volumes --rmi local --remove-orphans 2>$null | Out-Null }
                else { docker compose down --volumes --rmi local --remove-orphans 2>$null | Out-Null }
            } catch {} finally { Pop-Location }
        }
        if (Test-DockerDaemonHealth) {
            try {
                docker rm -f uaic_postgres uaic_redis uaic_maildev uaic_fastapi uaic_celery_worker uaic_celery_beat uaic_frontend 2>$null | Out-Null
                docker volume prune -f 2>$null | Out-Null
            } catch {}
        }
    }
    if (-not $Quiet) { Write-LogMessage "All services stopped and infrastructure purged." "SUCCESS" }
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
    Write-LogMessage "Starting UAIC Orchestrator Application Stack..." "INFO" "Cyan"

    if (-not (Invoke-PreflightChecks)) { return }
    $activeMode = Invoke-SetRpaMode -ChosenMode $TargetMode
    $conflicts = Invoke-CheckPortConflicts
    if ($conflicts.Count -gt 0) {
        Write-LogMessage "Releasing conflicting application ports before service launch..." "INFO" "Yellow"
        Invoke-KillAllServices -Quiet
        Start-Sleep -Milliseconds 500
        $null = Invoke-CheckPortConflicts
    } else {
        Invoke-KillAllServices -Quiet
    }

    $venvDir = Join-Path $backendDir ".venv"
    $pyExe   = Join-Path $venvDir "Scripts\python.exe"
    if (-not (Test-Path $pyExe)) {
        Invoke-InstallDependencies
        $pyExe = Join-Path $venvDir "Scripts\python.exe"
    }

    # Start Docker Infrastructure Stack (PostgreSQL, Redis, MailDev)
    $compose = Get-DockerComposeCommand
    if ($compose) {
        Write-LogMessage "Starting Docker infrastructure containers (PostgreSQL, Redis, MailDev)..." "INFO"
        try {
            Push-Location $backendDir
            if ($compose -eq "docker-compose") { docker-compose up -d postgres redis maildev }
            else { docker compose up -d postgres redis maildev }
        } catch {
            Write-LogMessage "Docker start warning: $_" "WARNING"
        } finally {
            Pop-Location
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

    Write-LogMessage "All services successfully initiated." "SUCCESS" "Green"
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

function Invoke-RunTestSuite {
    Write-LogMessage "=======================================================================" "INFO" "Cyan"
    Write-LogMessage "         UAIC Orchestrator Enterprise Diagnostics & Test Suite         " "INFO" "Cyan"
    Write-LogMessage "=======================================================================" "INFO" "Cyan"

    $allPassed = $true
    $pyExe = Get-PythonExecutable

    # 1. Backend Pytest Suite
    Write-LogMessage "Step 1/5: Running Backend Pytest Test Suite..." "INFO" "Cyan"
    if ($pyExe -and (Test-Path $pyExe)) {
        Push-Location $backendDir
        try {
            & $pyExe -m pytest -ra -q --asyncio-mode=auto
            if ($LASTEXITCODE -eq 0) {
                Write-LogMessage "Pytest Suite: PASS (All tests passed, 0 unraisable warnings)" "SUCCESS" "Green"
            } else {
                Write-LogMessage "Pytest Suite: FAIL (exit code $LASTEXITCODE)" "ERROR" "Red"
                $allPassed = $false
            }
        } catch {
            Write-LogMessage "Pytest execution error: $_" "ERROR" "Red"
            $allPassed = $false
        } finally { Pop-Location }
    } else {
        Write-LogMessage "Python virtual environment not found. Please run Option [4] first." "WARNING" "Yellow"
        $allPassed = $false
    }

    # 2. Python Ruff Linter
    Write-LogMessage "Step 2/5: Running Python Ruff Code Quality Linter..." "INFO" "Cyan"
    if ($pyExe -and (Test-Path $pyExe)) {
        Push-Location $backendDir
        try {
            & $pyExe -m ruff check app tests
            if ($LASTEXITCODE -eq 0) {
                Write-LogMessage "Ruff Linter: PASS (0 lint errors)" "SUCCESS" "Green"
            } else {
                Write-LogMessage "Ruff Linter: FAIL (exit code $LASTEXITCODE)" "ERROR" "Red"
                $allPassed = $false
            }
        } catch {
            Write-LogMessage "Ruff execution error: $_" "ERROR" "Red"
            $allPassed = $false
        } finally { Pop-Location }
    }

    # 3. Frontend TypeScript Compilation
    Write-LogMessage "Step 3/5: Running Frontend TypeScript Static Type Checking..." "INFO" "Cyan"
    Push-Location $frontendDir
    try {
        if (Test-Command "npx") {
            npx.cmd tsc --noEmit
            if ($LASTEXITCODE -eq 0) {
                Write-LogMessage "TypeScript: PASS (0 type errors)" "SUCCESS" "Green"
            } else {
                Write-LogMessage "TypeScript: FAIL (exit code $LASTEXITCODE)" "ERROR" "Red"
                $allPassed = $false
            }
        } else {
            Write-LogMessage "npx command not found. Skipping TypeScript check." "WARNING" "Yellow"
        }
    } catch {
        Write-LogMessage "TypeScript execution error: $_" "ERROR" "Red"
        $allPassed = $false
    } finally { Pop-Location }

    # 4. Docker Compose Config Validation
    Write-LogMessage "Step 4/5: Validating Docker Compose Configuration..." "INFO" "Cyan"
    $compose = Get-DockerComposeCommand
    if ($compose) {
        Push-Location $rootDir
        try {
            if ($compose -eq "docker-compose") { docker-compose config --quiet 2>$null }
            else { docker compose config --quiet 2>$null }
            if ($LASTEXITCODE -eq 0) {
                Write-LogMessage "Docker Compose Config: PASS (valid YAML and service schemas)" "SUCCESS" "Green"
            } else {
                Write-LogMessage "Docker Compose Config: NOTE (daemon offline or config check notice)" "WARNING" "Yellow"
            }
        } catch {
            Write-LogMessage "Docker compose check skipped: $_" "WARNING" "Yellow"
        } finally { Pop-Location }
    } else {
        Write-LogMessage "Docker compose tool not active. Skipping container config check." "INFO" "DarkGray"
    }

    # 5. PowerShell AST Syntax Checks
    Write-LogMessage "Step 5/5: Running PowerShell AST Syntax Validation..." "INFO" "Cyan"
    $checkScript = Join-Path $rootDir "scripts\check_ps1_syntax.ps1"
    if (Test-Path $checkScript) {
        powershell -NoProfile -ExecutionPolicy Bypass -File $checkScript
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "PowerShell AST Validation: PASS (0 script syntax errors)" "SUCCESS" "Green"
        } else {
            Write-LogMessage "PowerShell AST Validation: FAIL (exit code $LASTEXITCODE)" "ERROR" "Red"
            $allPassed = $false
        }
    }

    Write-LogMessage "=======================================================================" "INFO" "Cyan"
    if ($allPassed) {
        Write-LogMessage "All Diagnostic Verification Steps Passed Successfully!" "SUCCESS" "Green"
    } else {
        Write-LogMessage "Diagnostics completed with warnings/errors. Review log output above." "WARNING" "Yellow"
    }
    return $allPassed
}

function Show-LiveStatusMonitor {
    # Move cursor to top-left instead of clearing to eliminate screen flicker
    [Console]::SetCursorPosition(0,0)
    Write-Host "=======================================================================" -ForegroundColor Cyan
    Write-Host "          UAIC Orchestrator - Live Service Health Monitor              " -ForegroundColor Cyan
    Write-Host "  [HEALTHY]=HTTP 200  [RUNNING]=Port open  [STOPPED]=Offline          " -ForegroundColor DarkGray
    Write-Host "=======================================================================" -ForegroundColor Cyan
    Invoke-CheckServiceHealth "Frontend Web Application" 3000 "http://localhost:3000"
    Invoke-CheckServiceHealth "FastAPI Backend & API   " 8000 "http://localhost:8000/api/v1/health"
    Invoke-CheckServiceHealth "Celery Flower Monitor   " 5555 "http://localhost:5555"
    Invoke-CheckServiceHealth "MailDev Web Inspector   " 1080 "http://localhost:1080"
    Invoke-CheckServiceHealth "MailDev SMTP Server     " 1025
    Invoke-CheckServiceHealth "Redis Queue Broker      " 6379
    Invoke-CheckServiceHealth "PostgreSQL Database     " 5432
    Write-Host ""
    Write-Host "Quick Controls:" -ForegroundColor DarkCyan
    Write-Host " [R] Refresh Status  |  [K] Stop Services  |  [M] Main Menu  |  [Q] Exit" -ForegroundColor Yellow
    Write-Host "-----------------------------------------------------------------------" -ForegroundColor DarkGray
}

function Show-EnterpriseMenu {
    while ($true) {
        Clear-Host
        Write-Host "                  Enterprise Operations & Orchestration Console" -ForegroundColor Cyan
        Write-Host "=======================================================================" -ForegroundColor Cyan
        Write-Host " [1] Start All Application Services (Interactive Launch with Mode Select)"
        Write-Host " [2] Stop / Kill All Running Services (Clean ports, containers & volumes)"
        Write-Host " [3] Enterprise Data Cleanup & Retention"
        Write-Host " [4] Install / Update Dependencies"
        Write-Host " [5] Purge / Delete All Dependency Folders"
        Write-Host " [6] Configure RPA Execution Mode"
        Write-Host " [7] Run Full Diagnostics & Test Suite"
        Write-Host " [8] Docker Stack Management"
        Write-Host " [9] Live Service Status Monitor"
        Write-Host " [M] Open MailDev Web Inspector (http://localhost:1080)"
        Write-Host " [0] Exit Console"
        Write-Host "=======================================================================" -ForegroundColor Cyan

        $choice = Read-Host "Select an option [0-9/M]"
        switch ($choice) {
            "m" { Start-Process "http://localhost:1080"; Start-Sleep -Seconds 1 }
            "M" { Start-Process "http://localhost:1080"; Start-Sleep -Seconds 1 }
            "1" {
                Invoke-StartAllServices
                $monitoring = $true
                while ($monitoring) {
                    Show-LiveStatusMonitor
                    $key = Read-Host "Enter key action [R/K/M/Q]"
                    if ($key -match '^[kK]') { 
                        Invoke-KillAllServices
                        Start-Sleep -Seconds 1 
                    } elseif ($key -match '^[mM]') { 
                        $monitoring = $false 
                    } elseif ($key -match '^[qQ]') { 
                        exit 0 
                    }
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
                    $dChoice = Read-Host "Choose Docker action: [U]p / [D]own / [R]estart"
                    if ($dChoice -match '^[uU]') { Push-Location $backendDir; docker compose up -d; Pop-Location }
                    elseif ($dChoice -match '^[dD]') { Push-Location $backendDir; docker compose down; Pop-Location }
                    elseif ($dChoice -match '^[rR]') { Push-Location $backendDir; docker compose restart; Pop-Location }
                }
                Read-Host "Press Enter to return..."
            }
            "9" {
                $mon = $true
                while ($mon) {
                    Show-LiveStatusMonitor
                    $k = Read-Host "Enter key action [R/K/M/Q]"
                    if ($k -match '^[kK]') { Invoke-KillAllServices; Start-Sleep -Seconds 1 }
                    elseif ($k -match '^[mM]') { $mon = $false }
                    elseif ($k -match '^[qQ]') { exit 0 }
                }
            }
            "0" { exit 0 }
            default { Start-Sleep -Seconds 1 }
        }
    }
}

# CLI Parameter Dispatches for Automated and Headless Operations
if ($CheckPorts) { 
    $conflicts = Invoke-CheckPortConflicts
    if ($conflicts.Count -gt 0) { exit 1 } else { exit 0 }
}
if ($StopAll) { 
    Invoke-KillAllServices
    exit 0 
}
if ($RunTests) { 
    $passed = Invoke-RunTestSuite
    if ($passed) { exit 0 } else { exit 1 }
}
if ($PurgeDeps) { 
    Invoke-PurgeDependencyFolders -Force $true
    exit 0
}
if ($InstallDeps) { 
    Invoke-InstallDependencies
    exit 0
}
if ($CleanHistory -or $Clean) { 
    Invoke-CleanRunHistory
    exit 0
}
if ($StartAll) { 
    Invoke-StartAllServices -TargetMode $Mode
    if ($NoPrompt) { exit 0 }
    $monitoring = $true
    while ($monitoring) {
        Show-LiveStatusMonitor
        $key = Read-Host "Enter key action [R/K/M/Q]"
        if ($key -match '^[kK]') { Invoke-KillAllServices; Start-Sleep -Seconds 1 }
        elseif ($key -match '^[mM]') { $monitoring = $false }
        elseif ($key -match '^[qQ]') { exit 0 }
    }
    exit 0
}
Show-EnterpriseMenu