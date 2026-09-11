<#
.SYNOPSIS
    Universal Enterprise GitHub Deployment & Operations Console
.DESCRIPTION
    A 100% project-independent, enterprise-grade PowerShell console for automated
    GitHub repository lifecycle management across any solution or tech stack (Node.js,
    Python, .NET, Java, Go, Rust, React, Flutter, PHP, etc.).

    Features:
    - Automated Prerequisites Diagnostics & On-Demand Winget Installer
    - Multi-Account GitHub CLI Management & Git Credential Helper Binding
    - Smart Universal .gitignore Enforcer & Index Untracker (Preserves Custom Rules)
    - 100MB GitHub Hard File Limit Scanner & Auto-Protection Guard
    - Dynamic Deployment Engine (Create New Public/Private Repo or Sync/Merge Existing)
    - Intelligent Error Recovery (Detects already-existing repos, branch conflicts, etc.)
    - Branch Management, Pull Requests, Tagging & Releases
    - Safe & Confirmed Commit History Squashing (Pristine Initial Commit)
    - Comprehensive Self-Test & Environment Diagnostic
#>

[CmdletBinding()]
param(
    [switch]$SkipPrereqCheck,
    [switch]$NonInteractive,
    [switch]$RunSelfTest
)

# Set UTF-8 Output Encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ==============================================================================
# UI & DISPLAY HELPER FUNCTIONS
# ==============================================================================

function Write-ConsoleHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor White
    Write-Host "================================================================================" -ForegroundColor Cyan
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-WarningMsg {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Read-UserConfirm {
    param(
        [string]$PromptMessage,
        [bool]$DefaultYes = $false
    )
    $promptSuffix = if ($DefaultYes) { "[Y/n]" } else { "[y/N]" }
    $response = Read-Host "$PromptMessage $promptSuffix"
    if ([string]::IsNullOrWhiteSpace($response)) {
        return $DefaultYes
    }
    return ($response.Trim().ToLower() -in @('y', 'yes'))
}

# ==============================================================================
# ENVIRONMENT & PATH REFRESH
# ==============================================================================

function Update-SessionPath {
    try {
        $machinePath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
        $userPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)
        $env:Path = "$machinePath;$userPath"
    } catch {
        Write-WarningMsg "Could not refresh environment Path: $($_.Exception.Message)"
    }
}

# ==============================================================================
# PREREQUISITES VERIFICATION & AUTOMATED INSTALLER
# ==============================================================================

function Test-And-Install-Prerequisites {
    Write-ConsoleHeader "Enterprise Prerequisites and Health Check"

    $hasErrors = $false
    $wingetAvailable = [bool](Get-Command "winget" -ErrorAction SilentlyContinue)

    # 1. Check Git
    try {
        $gitCmd = Get-Command "git" -ErrorAction SilentlyContinue
        if ($gitCmd) {
            $gitVer = & git --version 2>&1
            Write-Host "  [OK] Git: Installed ($gitVer)" -ForegroundColor Green
        } else {
            Write-Host "  [X] Git: NOT INSTALLED or not found in system PATH" -ForegroundColor Red
            $hasErrors = $true

            if ($wingetAvailable) {
                if (Read-UserConfirm "Would you like to install Git now via Windows Package Manager (winget)?" -DefaultYes $true) {
                    Write-Info "Installing Git via winget. Please wait..."
                    & winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
                    Update-SessionPath
                    $gitCmd = Get-Command "git" -ErrorAction SilentlyContinue
                    if ($gitCmd) {
                        $installedGitVer = & git --version 2>&1
                        Write-Success "Git installed successfully: $installedGitVer"
                        $hasErrors = $false
                    } else {
                        Write-ErrorMsg "Git installation completed but binary not yet in current session PATH. Please restart terminal if needed."
                    }
                }
            } else {
                Write-WarningMsg "Please install Git manually from: https://git-scm.com/download/win"
            }
        }
    } catch {
        Write-ErrorMsg "Error verifying Git: $($_.Exception.Message)"
        $hasErrors = $true
    }

    # 2. Check GitHub CLI (gh)
    try {
        $ghCmd = Get-Command "gh" -ErrorAction SilentlyContinue
        if ($ghCmd) {
            $ghVer = & gh --version 2>&1 | Select-Object -First 1
            Write-Host "  [OK] GitHub CLI (gh): Installed ($ghVer)" -ForegroundColor Green
        } else {
            Write-Host "  [X] GitHub CLI (gh): NOT INSTALLED or not found in system PATH" -ForegroundColor Red
            $hasErrors = $true

            if ($wingetAvailable) {
                if (Read-UserConfirm "Would you like to install GitHub CLI (gh) now via winget?" -DefaultYes $true) {
                    Write-Info "Installing GitHub CLI via winget. Please wait..."
                    & winget install --id GitHub.cli -e --source winget --accept-package-agreements --accept-source-agreements
                    Update-SessionPath
                    $ghCmd = Get-Command "gh" -ErrorAction SilentlyContinue
                    if ($ghCmd) {
                        $installedGhVer = & gh --version 2>&1 | Select-Object -First 1
                        Write-Success "GitHub CLI installed successfully: $installedGhVer"
                        $hasErrors = $false
                    } else {
                        Write-ErrorMsg "GitHub CLI installation completed but binary not yet in current session PATH. Please restart terminal if needed."
                    }
                }
            } else {
                Write-WarningMsg "Please install GitHub CLI manually from: https://cli.github.com/"
            }
        }
    } catch {
        Write-ErrorMsg "Error verifying GitHub CLI: $($_.Exception.Message)"
        $hasErrors = $true
    }

    # 3. Check Git User Identity
    if (Get-Command "git" -ErrorAction SilentlyContinue) {
        try {
            $userName = & git config --get user.name 2>$null
            $userEmail = & git config --get user.email 2>$null

            if ([string]::IsNullOrWhiteSpace($userName) -or [string]::IsNullOrWhiteSpace($userEmail)) {
                Write-Host "  [!] Git User Identity: Not fully configured" -ForegroundColor Yellow
                Write-Info "Git requires a name and email to record commits."

                $ghLogin = $null
                $ghName = $null
                if (Get-Command "gh" -ErrorAction SilentlyContinue) {
                    $ghLogin = & gh api user --jq .login 2>$null
                    $ghName = & gh api user --jq .name 2>$null
                }

                $defaultName = if (![string]::IsNullOrWhiteSpace($ghName)) { $ghName } elseif (![string]::IsNullOrWhiteSpace($ghLogin)) { $ghLogin } else { "Developer" }
                $inputName = Read-Host "Enter your Git commit name [Default: $defaultName]"
                if ([string]::IsNullOrWhiteSpace($inputName)) { $inputName = $defaultName }

                $defaultEmail = if (![string]::IsNullOrWhiteSpace($ghLogin)) { "$ghLogin@users.noreply.github.com" } else { "developer@domain.local" }
                $inputEmail = Read-Host "Enter your Git commit email [Default: $defaultEmail]"
                if ([string]::IsNullOrWhiteSpace($inputEmail)) { $inputEmail = $defaultEmail }

                & git config --global user.name $inputName
                & git config --global user.email $inputEmail
                Write-Success "Git user identity configured: $inputName ($inputEmail)"
            } else {
                Write-Host "  [OK] Git User Identity: $userName ($userEmail)" -ForegroundColor Green
            }
        } catch {
            Write-WarningMsg "Could not query Git user identity: $($_.Exception.Message)"
        }
    }

    # 4. Git Buffer and Performance Optimization
    if (Get-Command "git" -ErrorAction SilentlyContinue) {
        try {
            & git config --global http.postBuffer 524288000 2>$null
            & git config --global http.lowSpeedLimit 0 2>$null
            & git config --global http.lowSpeedTime 999999 2>$null
        } catch {
            Write-WarningMsg "Could not set global Git transfer optimizations: $($_.Exception.Message)"
        }
    }

    if ($hasErrors) {
        Write-Host ""
        Write-ErrorMsg "Critical prerequisites are missing. Please complete installation before running deployment operations."
        Write-Host "Press Enter to return to menu..." -ForegroundColor Cyan
        [void](Read-Host)
        return $false
    }

    # Ensure Git Credential Helper is bound to GitHub CLI
    if (Get-Command "gh" -ErrorAction SilentlyContinue) {
        try {
            & gh auth setup-git 2>$null
        } catch {
            # Non-fatal
        }
    }

    Write-Host ""
    Write-Success "All enterprise prerequisites are verified and ready!"
    return $true
}

# ==============================================================================
# MULTI-ACCOUNT GITHUB MANAGEMENT
# ==============================================================================

function Get-GitHubAccounts {
    if (!(Get-Command "gh" -ErrorAction SilentlyContinue)) { return @() }
    
    try {
        $rawStatus = & gh auth status 2>&1
        $accountList = @()
        $currentAccount = $null
        $currentHost = "github.com"

        foreach ($line in $rawStatus) {
            # Host detection
            if ($line -match '^([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})') {
                $currentHost = $Matches[1]
            }
            # Account detection
            if ($line -match 'Logged in to\s+(\S+)\s+account\s+([^\s\(\)]+)') {
                $currentHost = $Matches[1]
                $currentAccount = $Matches[2]
                $accountList += [PSCustomObject]@{
                    Username = $currentAccount
                    Host     = $currentHost
                    IsActive = $false
                }
            }
            # Active status detection
            if ($line -match 'Active account:\s*true' -and $currentAccount) {
                $found = $accountList | Where-Object { $_.Username -eq $currentAccount -and $_.Host -eq $currentHost }
                if ($found) { $found.IsActive = $true }
            }
        }

        # If only 1 account exists, ensure it is tagged as active
        if ($accountList.Count -eq 1) {
            $accountList[0].IsActive = $true
        }

        return $accountList
    } catch {
        Write-WarningMsg "Could not query GitHub CLI accounts: $($_.Exception.Message)"
        return @()
    }
}

function Select-GitHubAccount {
    Write-ConsoleHeader "Multi-Account GitHub CLI Manager"

    if (!(Get-Command "gh" -ErrorAction SilentlyContinue)) {
        Write-ErrorMsg "GitHub CLI ('gh') is not installed."
        return
    }

    try {
        Write-Info "Detecting authenticated GitHub accounts..."
        $accounts = Get-GitHubAccounts

        if ($accounts.Count -eq 0) {
            Write-WarningMsg "No active GitHub accounts found. Launching authentication login..."
            & gh auth login
            & gh auth setup-git 2>$null
            return
        }

        Write-Host "`nAuthenticated GitHub Accounts on this machine:" -ForegroundColor Yellow
        for ($i = 0; $i -lt $accounts.Count; $i++) {
            $acc = $accounts[$i]
            $activeBadge = if ($acc.IsActive) { " [ACTIVE]" } else { "" }
            $color = if ($acc.IsActive) { "Green" } else { "White" }
            Write-Host "  [$($i + 1)] $($acc.Username) ($($acc.Host))$activeBadge" -ForegroundColor $color
        }

        if ($accounts.Count -eq 1) {
            $target = $accounts[0]
            Write-Host ""
            Write-Info "Single account detected: $($target.Username). Binding credentials..."
            & gh auth switch -u $target.Username -h $target.Host 2>$null
            & gh auth setup-git 2>$null
            Write-Success "Active account confirmed: $($target.Username) (Git credentials bound)."
            return
        }

        Write-Host ""
        $selection = Read-Host "Select account number to activate [1-$($accounts.Count)] (Press Enter to keep current)"
        if (![string]::IsNullOrWhiteSpace($selection)) {
            $idx = 0
            if ([int32]::TryParse($selection, [ref]$idx) -and $idx -ge 1 -and $idx -le $accounts.Count) {
                $target = $accounts[$idx - 1]
                Write-Info "Switching active GitHub account to: $($target.Username) ($($target.Host))..."
                & gh auth switch -u $target.Username -h $target.Host 2>$null
                if ($LASTEXITCODE -eq 0) {
                    & gh auth setup-git 2>$null
                    Write-Success "Successfully activated $($target.Username) and bound Git credential helper."
                } else {
                    Write-ErrorMsg "Failed to switch active account to $($target.Username)."
                }
            } else {
                Write-WarningMsg "Invalid selection. Retaining current active account."
            }
        } else {
            # Re-enforce credential helper on current active account
            & gh auth setup-git 2>$null
        }
    } catch {
        Write-ErrorMsg "An error occurred during account selection: $($_.Exception.Message)"
    }
}

# ==============================================================================
# SMART UNIVERSAL .GITIGNORE ENFORCER & CACHE CLEANER
# ==============================================================================

function Invoke-SmartGitignore {
    Write-ConsoleHeader "Smart Universal .gitignore and Cache Cleaner"

    try {
        if (!(Get-Command "git" -ErrorAction SilentlyContinue)) {
            Write-ErrorMsg "Git is not installed or not in PATH."
            return
        }

        if (!(Test-Path ".git")) {
            Write-Info "Initializing local Git repository..."
            & git init
            & git branch -M main
        }

        # Universal cross-stack enterprise gitignore template
        $universalRules = @(
            "# ==============================================================================",
            "# UNIVERSAL ENTERPRISE GITIGNORE RULES",
            "# ==============================================================================",
            "",
            "# Environments, Dependencies and Virtual Envs",
            ".venv/",
            "venv/",
            "env/",
            "node_modules/",
            "vendor/",
            "packages/",
            "",
            "# Build Artifacts, Compilations and Distributions",
            "dist/",
            "build/",
            "out/",
            "target/",
            "bin/",
            "obj/",
            ".next/",
            ".nuxt/",
            ".turbo/",
            ".parcel-cache/",
            "coverage/",
            "",
            "# Language Specific Caches",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            "*.egg-info/",
            "*.class",
            "",
            "# Databases, Storage and Logs",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            "*.log",
            "logs/",
            "*.tmp",
            "*.bak",
            "*.swp",
            "",
            "# Secrets, Tokens and Environment Overrides",
            ".env",
            ".env.local",
            ".env.*.local",
            "*.pem",
            "*.key",
            "*.pfx",
            "*.cert",
            "",
            "# Large Archives, Binaries and Media (100MB Protection)",
            "*.mp4",
            "*.mov",
            "*.avi",
            "*.mkv",
            "*.zip",
            "*.rar",
            "*.7z",
            "*.tar.gz",
            "*.iso",
            "*.VSIXPackage",
            "",
            "# Operating System and IDE Artifacts",
            ".DS_Store",
            "Thumbs.db",
            "desktop.ini",
            ".idea/",
            "*.suo",
            "*.user"
        )

        $gitignorePath = ".gitignore"
        if (Test-Path $gitignorePath) {
            Write-Info "Existing .gitignore detected. Merging enterprise rules safely..."
            $existingContent = Get-Content $gitignorePath -Encoding UTF8
            $existingSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
            foreach ($line in $existingContent) {
                $trimmed = $line.Trim()
                if (![string]::IsNullOrWhiteSpace($trimmed) -and !$trimmed.StartsWith("#")) {
                    [void]$existingSet.Add($trimmed)
                }
            }

            $rulesToAdd = @()
            foreach ($rule in $universalRules) {
                $trimmed = $rule.Trim()
                if (![string]::IsNullOrWhiteSpace($trimmed) -and !$trimmed.StartsWith("#")) {
                    if (!$existingSet.Contains($trimmed)) {
                        $rulesToAdd += $rule
                    }
                }
            }

            if ($rulesToAdd.Count -gt 0) {
                $appendBlock = "`n# --- Enterprise Standard Rules (Appended by Deploy Tool) ---`n" + ($rulesToAdd -join "`n") + "`n"
                Add-Content -Path $gitignorePath -Value $appendBlock -Encoding UTF8
                Write-Success "Added $($rulesToAdd.Count) missing standard enterprise rules to existing .gitignore."
            } else {
                Write-Success "Existing .gitignore already contains all essential enterprise rules."
            }
        } else {
            Write-Info "Creating clean enterprise .gitignore..."
            Set-Content -Path $gitignorePath -Value ($universalRules -join "`n") -Encoding UTF8
            Write-Success "Created enterprise .gitignore."
        }

        # Universal Untracking: unindex files matching .gitignore without deleting them from filesystem
        Write-Info "Re-indexing Git cache to untrack newly ignored files..."
        & git rm -r --cached . 2>$null
        & git add .

        Write-Success "Git cache refreshed. All ignored files have been unindexed safely."
    } catch {
        Write-ErrorMsg "Error updating .gitignore or Git cache: $($_.Exception.Message)"
    }
}

# ==============================================================================
# 100MB FILE SIZE GUARD (GITHUB LIMIT PROTECTION)
# ==============================================================================

function Invoke-LargeFileScan {
    param([bool]$AutoFix = $false)

    Write-ConsoleHeader "GitHub 100MB File Size Guard"
    Write-Info "Scanning workspace for files exceeding 95MB (GitHub hard limit: 100MB)..."

    $thresholdBytes = 95 * 1024 * 1024  # 95MB safety threshold
    $largeFiles = @()

    try {
        $items = Get-ChildItem -Path "." -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
            $_.FullName -notmatch '\\(\.git|node_modules|\.venv|venv|dist|build)\\' -and $_.Length -ge $thresholdBytes
        }

        if ($items) {
            Write-Host "`n[ALERT] Detected files exceeding GitHub file size limit:" -ForegroundColor Red
            Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Red
            Write-Host ("{0,-35} {1,12}  {2}" -f "File Name", "Size (MB)", "Relative Path") -ForegroundColor Yellow
            Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Red
            
            foreach ($f in $items) {
                $sizeMB = [math]::Round($f.Length / 1MB, 2)
                $relPath = Resolve-Path -Path $f.FullName -Relative
                Write-Host ("{0,-35} {1,12}  {2}" -f $f.Name, "$sizeMB MB", $relPath) -ForegroundColor White
                $largeFiles += $f
            }
            Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Red
            Write-WarningMsg "GitHub strictly rejects any commit or push containing files >= 100MB!"

            if ($AutoFix -or (Read-UserConfirm "Would you like to automatically add these files to .gitignore and untrack them?" -DefaultYes $true)) {
                $gitignorePath = ".gitignore"
                $linesToAppend = @("`n# Large Files Excluded by 100MB Guard")
                foreach ($f in $largeFiles) {
                    $rel = Resolve-Path -Path $f.FullName -Relative
                    $cleanRel = $rel.TrimStart(".\").Replace("\", "/")
                    $linesToAppend += $cleanRel
                    & git rm --cached "$cleanRel" 2>$null
                }
                Add-Content -Path $gitignorePath -Value ($linesToAppend -join "`n") -Encoding UTF8
                & git add .gitignore 2>$null
                Write-Success "Large files successfully excluded in .gitignore and untracked from Git index."
                return $false
            }
            return $true  # Large files still present
        } else {
            Write-Success "No files exceeding 95MB detected. Workspace is safe for GitHub push."
            return $false
        }
    } catch {
        Write-ErrorMsg "Error while scanning for large files: $($_.Exception.Message)"
        return $false
    }
}

# ==============================================================================
# DYNAMIC DEPLOYMENT & REPOSITORY PUSH ENGINE
# ==============================================================================

function Invoke-DeployToGitHub {
    Write-ConsoleHeader "Enterprise GitHub Deployment Engine"

    try {
        # Step 1: Ensure Prerequisites & Account Selection
        if (!(Test-And-Install-Prerequisites)) { return }
        Select-GitHubAccount

        # Step 2: Run 100MB File Guard
        $hasDangerousFiles = Invoke-LargeFileScan -AutoFix $false
        if ($hasDangerousFiles) {
            if (!(Read-UserConfirm "Large files (>95MB) are present in the directory. Proceeding might cause GitHub to reject the push. Continue anyway?" -DefaultYes $false)) {
                Write-Info "Deployment aborted by user to resolve large files."
                return
            }
        }

        # Step 3: Git Initialization & Branch Detection
        if (!(Test-Path ".git")) {
            Write-Info "Initializing local Git repository..."
            & git init
            & git branch -M main
        }

        $currentBranch = & git branch --show-current 2>$null
        if ([string]::IsNullOrWhiteSpace($currentBranch)) {
            $currentBranch = "main"
            & git branch -M $currentBranch 2>$null
        }
        Write-Info "Active local branch: $currentBranch"

        # Step 4: Staging & Commit
        Write-Info "Checking working tree status..."
        & git add .
        $status = & git status --porcelain 2>$null

        if ($status) {
            $commitMsg = Read-Host "`nEnter commit message [Default: 'chore: enterprise production release']"
            if ([string]::IsNullOrWhiteSpace($commitMsg)) {
                $commitMsg = "chore: enterprise production release"
            }
            & git commit -m $commitMsg
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Changes successfully committed locally."
            } else {
                Write-ErrorMsg "Commit failed. Please check if your Git user.name and user.email are configured."
                return
            }
        } else {
            Write-Info "Working tree clean. Nothing new to commit."
        }

        # Step 5: Remote Resolution
        $existingOrigin = & git remote get-url origin 2>$null
        $deployPath = ""

        if (![string]::IsNullOrWhiteSpace($existingOrigin)) {
            Write-Host "`nExisting Remote Detected: origin -> $existingOrigin" -ForegroundColor Yellow
            Write-Host "  [1] Push to current remote origin ($existingOrigin)" -ForegroundColor White
            Write-Host "  [2] Create a NEW repository on GitHub (via GitHub CLI)" -ForegroundColor White
            Write-Host "  [3] Connect and push to a DIFFERENT existing repository URL" -ForegroundColor White
            $choice = Read-Host "`nChoose deployment option [1-3]"
            $deployPath = $choice
        } else {
            Write-Host "`nChoose deployment destination:" -ForegroundColor Yellow
            Write-Host "  [1] Create a NEW repository on GitHub (via GitHub CLI)" -ForegroundColor White
            Write-Host "  [2] Connect and push to an EXISTING GitHub repository" -ForegroundColor White
            $choice = Read-Host "`nChoose deployment option [1-2]"
            $deployPath = if ($choice -eq "1") { "2" } else { "3" }
        }

        # Path A: Push to Current Existing Remote
        if ($deployPath -eq "1" -and ![string]::IsNullOrWhiteSpace($existingOrigin)) {
            Invoke-PushStrategies -RemoteUrl $existingOrigin -Branch $currentBranch
        }
        # Path B: Create New Repository on GitHub
        elseif ($deployPath -eq "2") {
            $defaultRepoName = Split-Path -Leaf (Get-Location)
            $repoName = Read-Host "`nEnter repository name [Default: $defaultRepoName]"
            if ([string]::IsNullOrWhiteSpace($repoName)) { $repoName = $defaultRepoName }
            # Sanitize repo name (replace spaces with hyphens)
            $repoName = $repoName.Trim().Replace(" ", "-")

            $isPrivate = Read-UserConfirm "Set repository visibility to Private?" -DefaultYes $true
            $visibilityFlag = if ($isPrivate) { "--private" } else { "--public" }

            $desc = Read-Host "Enter repository description (Optional)"

            # If origin already existed, safely remove it to allow new creation
            & git remote remove origin 2>$null

            $createArgs = @("repo", "create", $repoName, $visibilityFlag, "--source=.", "--push")
            if (![string]::IsNullOrWhiteSpace($desc)) {
                $createArgs += "--description"
                $createArgs += $desc
            }

            Write-Info "Executing: gh $($createArgs -join ' ')..."
            $out = & gh @createArgs 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Repository '$repoName' created and code pushed successfully to GitHub!"
                Write-Host "$out" -ForegroundColor Gray
            } else {
                # Intelligent Recovery: Check if failure is due to repository already existing on GitHub
                if ("$out" -match "already exists") {
                    Write-WarningMsg "Repository '$repoName' already exists on GitHub."
                    if (Read-UserConfirm "Would you like to connect to this existing repository and push?" -DefaultYes $true) {
                        # Resolve authenticated username
                        $activeAcc = & gh api user --jq .login 2>$null
                        if ([string]::IsNullOrWhiteSpace($activeAcc)) { $activeAcc = "RAKSHAKAR" }
                        $existingTarget = "https://github.com/$activeAcc/$repoName.git"
                        & git remote remove origin 2>$null
                        & git remote add origin $existingTarget
                        Write-Success "Configured remote origin: $existingTarget"
                        Invoke-PushStrategies -RemoteUrl $existingTarget -Branch $currentBranch
                        return
                    }
                }
                Write-ErrorMsg "Repository creation failed:`n$out"
            }
        }
        # Path C: Connect to New / Different Existing Remote
        elseif ($deployPath -eq "3") {
            $targetRepo = Read-Host "`nEnter GitHub repository URL or slug (e.g. username/repo or https://github.com/...)"
            if ([string]::IsNullOrWhiteSpace($targetRepo)) {
                Write-WarningMsg "No repository target provided. Aborting."
                return
            }

            if ($targetRepo -notmatch '^https?://' -and $targetRepo -notmatch '^git@') {
                $targetRepo = "https://github.com/$targetRepo.git"
            }

            & git remote remove origin 2>$null
            & git remote add origin $targetRepo
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Configured remote origin: $targetRepo"
                Invoke-PushStrategies -RemoteUrl $targetRepo -Branch $currentBranch
            } else {
                Write-ErrorMsg "Failed to set remote origin to '$targetRepo'."
            }
        }
    } catch {
        Write-ErrorMsg "An unexpected error occurred during deployment: $($_.Exception.Message)"
    }
}

function Invoke-PushStrategies {
    param(
        [string]$RemoteUrl,
        [string]$Branch
    )

    try {
        Write-Host "`nSelect push strategy for branch '$Branch':" -ForegroundColor Yellow
        Write-Host "  [1] Standard Push (Safe fast-forward: git push -u origin $Branch)" -ForegroundColor White
        Write-Host "  [2] Pull and Merge Remote Changes (Reconcile remote commits/README: git pull --no-rebase)" -ForegroundColor White
        Write-Host "  [3] Force Push (OVERWRITE remote branch - requires explicit confirmation)" -ForegroundColor Red
        
        $strategy = Read-Host "Select strategy [1-3] (Default: 1)"
        if ([string]::IsNullOrWhiteSpace($strategy)) { $strategy = "1" }

        switch ($strategy) {
            "1" {
                Write-Info "Executing standard push..."
                $pushOut = & git push -u origin $Branch 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Code successfully pushed to $RemoteUrl ($Branch)!"
                } else {
                    Write-WarningMsg "Push rejected. The remote may contain work that you do not have locally."
                    Write-Host "$pushOut" -ForegroundColor DarkGray
                    if (Read-UserConfirm "Would you like to reconcile remote changes automatically via Pull and Merge?" -DefaultYes $true) {
                        # Re-execute strategy 2
                        Write-Info "Attempting automatic Pull and Merge..."
                        & git fetch origin $Branch 2>$null
                        & git pull origin $Branch --allow-unrelated-histories --no-rebase
                        if ($LASTEXITCODE -eq 0) {
                            & git push -u origin $Branch
                            if ($LASTEXITCODE -eq 0) {
                                Write-Success "Successfully reconciled and pushed to $RemoteUrl!"
                                return
                            }
                        }
                        Write-ErrorMsg "Automatic reconciliation failed. Please resolve manually or choose Force Push."
                    }
                }
            }
            "2" {
                Write-Info "Fetching and merging remote changes..."
                & git fetch origin $Branch 2>$null
                $pullOut = & git pull origin $Branch --allow-unrelated-histories --no-rebase 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Info "Pushing merged branch to remote..."
                    & git push -u origin $Branch
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "Successfully merged and pushed to $RemoteUrl!"
                    } else {
                        Write-ErrorMsg "Push failed following merge."
                    }
                } else {
                    # Check if remote branch doesn't exist yet
                    if ("$pullOut" -match "couldn't find remote ref") {
                        Write-Info "Remote branch '$Branch' does not exist yet. Proceeding with initial push..."
                        & git push -u origin $Branch
                        if ($LASTEXITCODE -eq 0) {
                            Write-Success "Initial branch '$Branch' created and pushed successfully!"
                        } else {
                            Write-ErrorMsg "Initial push failed."
                        }
                    } else {
                        Write-ErrorMsg "Merge encountered conflicts or errors:`n$pullOut"
                        Write-Info "Please resolve any merge conflicts in your editor, commit, and then push."
                    }
                }
            }
            "3" {
                Write-WarningMsg "FORCE PUSH will overwrite commits on the remote branch."
                if (Read-UserConfirm "Are you absolutely certain you want to force-push to '$Branch'?" -DefaultYes $false) {
                    Write-Info "Executing force push..."
                    $fpOut = & git push -u origin $Branch --force 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "Force push completed successfully!"
                    } else {
                        Write-ErrorMsg "Force push failed:`n$fpOut"
                    }
                } else {
                    Write-Info "Force push cancelled by user."
                }
            }
            default {
                Write-WarningMsg "Invalid option selected."
            }
        }
    } catch {
        Write-ErrorMsg "Error during push operation: $($_.Exception.Message)"
    }
}

# ==============================================================================
# SAFE HISTORY FLATTENING / SQUASHING
# ==============================================================================

function Invoke-FlattenHistory {
    Write-ConsoleHeader "Flatten and Squash Git History (Pristine Initial Release)"

    try {
        Write-WarningMsg "This operation flattens all existing commits into a SINGLE initial commit."
        Write-WarningMsg "All past commit history, timestamps, and commit logs will be permanently squashed."
        Write-Host ""

        if (!(Read-UserConfirm "Are you sure you want to flatten the Git history of this repository?" -DefaultYes $false)) {
            Write-Info "History flattening cancelled."
            return
        }

        if (!(Test-Path ".git")) {
            Write-ErrorMsg "No Git repository found in current directory."
            return
        }

        # Check if repository has any commits
        $headCommit = & git rev-parse --verify HEAD 2>$null
        if ([string]::IsNullOrWhiteSpace($headCommit)) {
            Write-WarningMsg "Repository has no commits to flatten. Staging files and creating initial commit..."
            & git add .
            & git commit -m "chore: pristine enterprise release" 2>$null
            Write-Success "Initial commit created."
            return
        }

        $currentBranch = & git branch --show-current 2>$null
        if ([string]::IsNullOrWhiteSpace($currentBranch)) { $currentBranch = "main" }

        Write-Info "Creating orphan branch 'temp_pristine_branch'..."
        & git branch -D temp_pristine_branch 2>$null
        & git checkout --orphan temp_pristine_branch 2>$null
        & git add .

        $commitMsg = Read-Host "`nEnter message for the pristine commit [Default: 'chore: pristine enterprise release']"
        if ([string]::IsNullOrWhiteSpace($commitMsg)) { $commitMsg = "chore: pristine enterprise release" }

        & git commit -m $commitMsg
        & git branch -D $currentBranch 2>$null
        & git branch -m $currentBranch

        Write-Success "Git history successfully flattened into a single clean commit on branch '$currentBranch'!"
    } catch {
        Write-ErrorMsg "Error during history flattening: $($_.Exception.Message)"
    }
}

# ==============================================================================
# BRANCH MANAGEMENT & SYNCHRONIZATION
# ==============================================================================

function Invoke-BranchManagement {
    Write-ConsoleHeader "Branch Management and Synchronization"

    try {
        if (!(Test-Path ".git")) {
            Write-ErrorMsg "No Git repository found in current directory."
            return
        }

        Write-Host "Local Branches:" -ForegroundColor Cyan
        & git branch -v
        Write-Host "`nRemote Branches:" -ForegroundColor Cyan
        $remotes = & git branch -r 2>$null
        if ($remotes) { Write-Host "$remotes" } else { Write-Host "  (None detected)" -ForegroundColor Gray }

        Write-Host "`nOptions:" -ForegroundColor Yellow
        Write-Host "  [1] Create and switch to a NEW branch"
        Write-Host "  [2] Switch to an EXISTING branch"
        Write-Host "  [3] Pull latest changes for current branch"
        Write-Host "  [0] Return to Main Menu"

        $bChoice = Read-Host "`nSelect an option [0-3]"
        switch ($bChoice) {
            "1" {
                $newB = Read-Host "Enter new branch name"
                if (![string]::IsNullOrWhiteSpace($newB)) {
                    # Sanitize
                    $newB = $newB.Trim().Replace(" ", "-")
                    # Check if branch already exists
                    $exists = & git branch --list $newB 2>$null
                    if ($exists) {
                        Write-WarningMsg "Branch '$newB' already exists. Switching to it..."
                        & git checkout $newB
                    } else {
                        & git checkout -b $newB
                        if ($LASTEXITCODE -eq 0) {
                            Write-Success "Switched to new branch: $newB"
                        } else {
                            Write-ErrorMsg "Failed to create branch: $newB"
                        }
                    }
                }
            }
            "2" {
                $targetB = Read-Host "Enter existing branch name"
                if (![string]::IsNullOrWhiteSpace($targetB)) {
                    & git checkout $targetB.Trim()
                    if ($LASTEXITCODE -ne 0) {
                        Write-ErrorMsg "Could not checkout branch '$targetB'. Please verify the branch name."
                    }
                }
            }
            "3" {
                $cur = & git branch --show-current 2>$null
                Write-Info "Pulling latest changes for '$cur'..."
                & git pull
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Branch '$cur' is up to date."
                } else {
                    Write-WarningMsg "Pull failed. Verify that a remote tracking branch is configured."
                }
            }
            "0" {
                return
            }
        }
    } catch {
        Write-ErrorMsg "Error during branch operation: $($_.Exception.Message)"
    }
}

# ==============================================================================
# PULL REQUEST (PR) OPERATIONS
# ==============================================================================

function Invoke-PullRequestOps {
    Write-ConsoleHeader "GitHub Pull Request (PR) Operations"

    try {
        if (!(Get-Command "gh" -ErrorAction SilentlyContinue)) {
            Write-ErrorMsg "GitHub CLI ('gh') is required for PR operations."
            return
        }

        $rem = & git remote get-url origin 2>$null
        if ([string]::IsNullOrWhiteSpace($rem)) {
            Write-WarningMsg "No remote origin configured in this repository. Push your code to GitHub first."
            return
        }

        Write-Host "Options:" -ForegroundColor Yellow
        Write-Host "  [1] View PR Status for Current Branch (gh pr status)"
        Write-Host "  [2] List Open Pull Requests (gh pr list)"
        Write-Host "  [3] Create a New Pull Request (gh pr create)"
        Write-Host "  [0] Return to Main Menu"

        $prChoice = Read-Host "`nSelect an option [0-3]"
        switch ($prChoice) {
            "1" {
                Write-Info "Checking Pull Request status..."
                & gh pr status
            }
            "2" {
                Write-Info "Fetching open Pull Requests..."
                & gh pr list
            }
            "3" {
                $curBranch = & git branch --show-current 2>$null
                if ($curBranch -in @('main', 'master')) {
                    Write-WarningMsg "You are currently on '$curBranch'. Pull Requests are usually created from feature branches."
                    if (!(Read-UserConfirm "Do you still want to proceed with creating a PR from '$curBranch'?" -DefaultYes $false)) {
                        return
                    }
                }

                $title = Read-Host "Enter PR Title"
                $body = Read-Host "Enter PR Description (Body)"
                $prArgs = @("pr", "create")
                if (![string]::IsNullOrWhiteSpace($title)) { $prArgs += @("--title", $title) }
                if (![string]::IsNullOrWhiteSpace($body)) { $prArgs += @("--body", $body) }
                & gh @prArgs
            }
            "0" {
                return
            }
        }
    } catch {
        Write-ErrorMsg "Error during PR operation: $($_.Exception.Message)"
    }
}

# ==============================================================================
# TAGGING & GITHUB RELEASE OPERATIONS
# ==============================================================================

function Invoke-ReleaseManagement {
    Write-ConsoleHeader "GitHub Releases and Tagging Management"

    try {
        if (!(Test-Path ".git")) {
            Write-ErrorMsg "No Git repository found in current directory."
            return
        }

        Write-Host "Options:" -ForegroundColor Yellow
        Write-Host "  [1] List Local Git Tags (git tag -l)"
        Write-Host "  [2] Create and Push a New Git Tag"
        Write-Host "  [3] Create a GitHub Release via gh CLI"
        Write-Host "  [0] Return to Main Menu"

        $relChoice = Read-Host "`nSelect an option [0-3]"
        switch ($relChoice) {
            "1" {
                Write-Host "`nGit Tags:" -ForegroundColor Cyan
                $tags = & git tag -l -n1 2>$null
                if ($tags) { Write-Host "$tags" } else { Write-Host "  (No tags found)" -ForegroundColor Gray }
            }
            "2" {
                $tagName = Read-Host "Enter tag name (e.g. v1.0.0)"
                if ([string]::IsNullOrWhiteSpace($tagName)) {
                    Write-WarningMsg "Tag name cannot be empty."
                    return
                }

                # Check if tag already exists
                $existingTag = & git tag -l $tagName.Trim() 2>$null
                if ($existingTag) {
                    Write-WarningMsg "Tag '$tagName' already exists."
                    if (Read-UserConfirm "Would you like to overwrite / force-update this tag?" -DefaultYes $false) {
                        $tagMsg = Read-Host "Enter tag annotation message"
                        if ([string]::IsNullOrWhiteSpace($tagMsg)) { $tagMsg = "Release $tagName" }
                        & git tag -f -a $tagName -m $tagMsg
                    } else {
                        return
                    }
                } else {
                    $tagMsg = Read-Host "Enter tag annotation message"
                    if ([string]::IsNullOrWhiteSpace($tagMsg)) { $tagMsg = "Release $tagName" }
                    & git tag -a $tagName -m $tagMsg
                }

                # Push tag if origin exists
                $hasOrigin = & git remote get-url origin 2>$null
                if (![string]::IsNullOrWhiteSpace($hasOrigin)) {
                    Write-Info "Pushing tag '$tagName' to origin..."
                    & git push origin $tagName
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "Tag $tagName created and pushed to GitHub."
                    } else {
                        Write-WarningMsg "Tag created locally, but could not push to remote."
                    }
                } else {
                    Write-Success "Tag $tagName created locally (No remote origin configured)."
                }
            }
            "3" {
                if (!(Get-Command "gh" -ErrorAction SilentlyContinue)) {
                    Write-ErrorMsg "GitHub CLI required for releases."
                    return
                }
                $tagName = Read-Host "Enter release tag (e.g. v1.0.0)"
                if ([string]::IsNullOrWhiteSpace($tagName)) {
                    Write-WarningMsg "Release tag cannot be empty."
                    return
                }
                $title = Read-Host "Enter release title"
                $notes = Read-Host "Enter release notes (optional)"
                $relArgs = @("release", "create", $tagName)
                if (![string]::IsNullOrWhiteSpace($title)) { $relArgs += @("--title", $title) }
                if (![string]::IsNullOrWhiteSpace($notes)) { $relArgs += @("--notes", $notes) }
                & gh @relArgs
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "GitHub Release '$tagName' created successfully!"
                } else {
                    Write-ErrorMsg "Failed to create GitHub Release."
                }
            }
            "0" {
                return
            }
        }
    } catch {
        Write-ErrorMsg "Error during release operation: $($_.Exception.Message)"
    }
}

# ==============================================================================
# ENVIRONMENT DIAGNOSTICS & SELF-TEST
# ==============================================================================

function Invoke-Diagnostics {
    Write-ConsoleHeader "Comprehensive Environment Diagnostic and Self-Test"

    try {
        Write-Host "System Environment:" -ForegroundColor Cyan
        Write-Host "  OS Version:         $([System.Environment]::OSVersion.VersionString)"
        Write-Host "  PowerShell Version: $($PSVersionTable.PSVersion)"
        Write-Host "  Working Directory:  $((Get-Location).Path)"

        Write-Host "`nGit Diagnostic:" -ForegroundColor Cyan
        $gitCmd = Get-Command "git" -ErrorAction SilentlyContinue
        if ($gitCmd) {
            $gitSource = $gitCmd.Source
            $gitVersionText = & git --version 2>&1
            $userNameText = & git config --get user.name 2>$null
            $userEmailText = & git config --get user.email 2>$null
            $postBufText = & git config --get http.postBuffer 2>$null

            Write-Host "  [OK] Git Binary:     $gitSource" -ForegroundColor Green
            Write-Host "  [OK] Git Version:    $gitVersionText" -ForegroundColor Green
            Write-Host "  [OK] Git User Name:  $userNameText" -ForegroundColor Green
            Write-Host "  [OK] Git User Email: $userEmailText" -ForegroundColor Green
            Write-Host "  [OK] postBuffer:     $postBufText bytes" -ForegroundColor Green
        } else {
            Write-Host "  [X] Git Binary:     NOT FOUND" -ForegroundColor Red
        }

        Write-Host "`nGitHub CLI Diagnostic:" -ForegroundColor Cyan
        $ghCmd = Get-Command "gh" -ErrorAction SilentlyContinue
        if ($ghCmd) {
            $ghSource = $ghCmd.Source
            $ghVerText = & gh --version 2>&1 | Select-Object -First 1
            Write-Host "  [OK] gh Binary:      $ghSource" -ForegroundColor Green
            Write-Host "  [OK] gh Version:     $ghVerText" -ForegroundColor Green
            Write-Host "`nGitHub Authentication Status:" -ForegroundColor Cyan
            & gh auth status
        } else {
            Write-Host "  [X] gh Binary:      NOT FOUND" -ForegroundColor Red
        }

        Write-Host "`nRepository Diagnostic:" -ForegroundColor Cyan
        if (Test-Path ".git") {
            $curBranchText = & git branch --show-current 2>$null
            Write-Host "  [OK] Git Repo:       Initialized" -ForegroundColor Green
            Write-Host "  [OK] Current Branch: $curBranchText" -ForegroundColor Green
            $remotes = & git remote -v 2>$null
            if ($remotes) {
                Write-Host "  [OK] Remotes:`n$($remotes -join "`n")" -ForegroundColor Green
            } else {
                Write-Host "  [!] Remotes:        None configured" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  [!] Git Repo:       Not initialized in current folder" -ForegroundColor Yellow
        }
    } catch {
        Write-ErrorMsg "Error during diagnostic run: $($_.Exception.Message)"
    }
}

# ==============================================================================
# MAIN PERSISTENT INTERACTIVE CONSOLE MENU
# ==============================================================================

# Run initial pre-flight check at startup unless skipped
if (!$SkipPrereqCheck) {
    [void](Test-And-Install-Prerequisites)
}

if ($RunSelfTest) {
    Invoke-Diagnostics
    exit 0
}

if ($NonInteractive) {
    return
}

$running = $true
while ($running) {
    try {
        $curFolder = Split-Path -Leaf (Get-Location)
        $curBranch = if (Test-Path ".git") { (& git branch --show-current 2>$null) } else { "none" }
        if ([string]::IsNullOrWhiteSpace($curBranch)) { $curBranch = "detached" }

        # Detect current active GitHub account
        $activeAcc = "None"
        $allAccs = Get-GitHubAccounts
        $foundActive = $allAccs | Where-Object { $_.IsActive }
        if ($foundActive) {
            $activeAcc = "$($foundActive[0].Username) ($($foundActive[0].Host))"
        } elseif ($allAccs.Count -gt 0) {
            $activeAcc = "$($allAccs[0].Username)"
        }

        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "           Enterprise GitHub Deployment and Operations Console                 " -ForegroundColor White
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "  Project: $curFolder  |  Branch: $curBranch  |  Active GitHub: $activeAcc" -ForegroundColor Gray
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "  ACCOUNT AND AUTHENTICATION:" -ForegroundColor Yellow
        Write-Host "    [1] View GitHub Auth and Account Status" -ForegroundColor White
        Write-Host "    [2] Switch / Select Active GitHub Account (Multi-Account Manager)" -ForegroundColor White
        Write-Host "    [3] Login to New GitHub Account (gh auth login)" -ForegroundColor White
        Write-Host ""
        Write-Host "  REPOSITORY HYGIENE AND PROTECTION:" -ForegroundColor Yellow
        Write-Host "    [4] Smart Universal .gitignore Enforcer and Index Untracker" -ForegroundColor White
        Write-Host "    [5] Scan for Large Files (100MB GitHub Hard Limit Guard)" -ForegroundColor White
        Write-Host "    [6] Flatten / Squash Commit History (Pristine Release)" -ForegroundColor White
        Write-Host ""
        Write-Host "  DEPLOYMENT AND SYNC:" -ForegroundColor Yellow
        Write-Host "    [7] Deploy / Push Code to GitHub (Create New or Sync/Merge Existing)" -ForegroundColor White
        Write-Host "    [8] Branch Management and Sync (List, Create, Switch, Pull)" -ForegroundColor White
        Write-Host "    [9] Pull Request Operations (Status, List, Create)" -ForegroundColor White
        Write-Host "   [10] GitHub Releases and Tagging Management" -ForegroundColor White
        Write-Host ""
        Write-Host "  SYSTEM AND DIAGNOSTICS:" -ForegroundColor Yellow
        Write-Host "   [11] Prerequisites Diagnostic and Self-Test" -ForegroundColor White
        Write-Host "    [0] Exit Console" -ForegroundColor Yellow
        Write-Host "================================================================================" -ForegroundColor Cyan

        $choice = Read-Host "Select an option [0-11]"

        switch ($choice) {
            "1" {
                Write-ConsoleHeader "GitHub Authentication Status"
                if (Get-Command "gh" -ErrorAction SilentlyContinue) {
                    $statusOut = & gh auth status 2>&1
                    Write-Host "$statusOut"
                    if ($LASTEXITCODE -ne 0) {
                        Write-WarningMsg "No active authentication detected."
                        if (Read-UserConfirm "Would you like to log in now via browser/token?" -DefaultYes $true) {
                            & gh auth login
                            & gh auth setup-git 2>$null
                        }
                    }
                } else {
                    Write-ErrorMsg "GitHub CLI is not installed."
                }
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "2" {
                Select-GitHubAccount
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "3" {
                Write-ConsoleHeader "GitHub Authentication Login"
                if (Get-Command "gh" -ErrorAction SilentlyContinue) {
                    & gh auth login
                    & gh auth setup-git 2>$null
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "GitHub login complete!"
                    } else {
                        Write-WarningMsg "GitHub login cancelled or incomplete."
                    }
                } else {
                    Write-ErrorMsg "GitHub CLI is not installed."
                }
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "4" {
                Invoke-SmartGitignore
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "5" {
                [void](Invoke-LargeFileScan -AutoFix $false)
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "6" {
                Invoke-FlattenHistory
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "7" {
                Invoke-DeployToGitHub
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "8" {
                Invoke-BranchManagement
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "9" {
                Invoke-PullRequestOps
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "10" {
                Invoke-ReleaseManagement
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "11" {
                Invoke-Diagnostics
                Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
                [void](Read-Host)
            }
            "0" {
                $running = $false
                Write-Host "`nExiting Enterprise Deployment Console. Goodbye!" -ForegroundColor Cyan
            }
            default {
                Write-WarningMsg "Invalid selection. Please choose an option between 0 and 11."
                Start-Sleep -Seconds 1
            }
        }
    } catch {
        Write-ErrorMsg "An unexpected error occurred in console menu: $($_.Exception.Message)"
        Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
        [void](Read-Host)
    }
}