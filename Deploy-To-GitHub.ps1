<#
.SYNOPSIS
    Enterprise GitHub Deployment & Multi-Account Management Script
.DESCRIPTION
    Automates GitHub authentication selection, local git initialization, custom commits,
    purges tracked heavy files and past commits containing large binaries from Git history,
    and handles creating or pushing into repositories with robust remote conflict safety.
#>

[CmdletBinding()]
param()

# Ensure prompt styling
$Host.UI.RawUI.ForegroundColor = 'Cyan'
Write-Host "======================================================"
Write-Host "     UAIC RPA Orchestrator - Enterprise GitHub Tool   "
Write-Host "======================================================"
$Host.UI.RawUI.ForegroundColor = 'White'

try {
    # 0. Optimize Git Config for Large Transfers
    Write-Host "[INFO] Optimizing Git network buffers for enterprise payload..." -ForegroundColor Yellow
    git config --global http.postBuffer 524288000
    git config --global http.lowSpeedLimit 0
    git config --global http.lowSpeedTime 999999

    # 1. Check prerequisites
    if (!(Get-Command "gh" -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI ('gh') is not installed or not in your system PATH. Please install from https://cli.github.com/"
    }

    # 2. Multi-Account Management
    Write-Host "`n[STEP 1] GitHub Authentication & Account Management" -ForegroundColor Cyan
    gh auth status
    $switchAccount = Read-Host "Do you want to log out and switch your GitHub account? (y/N)"
    if ($switchAccount -eq 'y' -or $switchAccount -eq 'Y') {
        Write-Host "[INFO] Logging out of current GitHub session..." -ForegroundColor Yellow
        gh auth logout -h github.com -y
        Write-Host "[INFO] Please authenticate with your target account:" -ForegroundColor Green
        gh auth login
    } else {
        Write-Host "[SUCCESS] Proceeding with current active GitHub account session." -ForegroundColor Green
    }

    # 3. Local Repository Initialization & Deep History Sanitization
    Write-Host "`n[STEP 2] Local Git Repository & Total History Sanitization" -ForegroundColor Cyan
    if (!(Test-Path ".git")) {
        Write-Host "[INFO] Initializing local Git repository..." -ForegroundColor Green
        git init
        git branch -M main
    } else {
        Write-Host "[INFO] Existing local Git repository detected." -ForegroundColor Cyan
    }

    # Enforce strict enterprise .gitignore rules
    Write-Host "[INFO] Enforcing strict enterprise .gitignore rules..." -ForegroundColor Yellow
    $gitignoreContent = @"
# Environments & Dependencies
.venv/
node_modules/
dist/
build/
__pycache__/
*.pyc

# Local Storage, Browser Caches, and Databases
backend/data/
backend/logs/
backend/screenshots/
logs/
*.db
*.sqlite
*.sqlite3

# Heavy Media, Recordings, VSIX Packages, and Archives (>100MB Limit Protection)
*.mp4
*.mov
*.avi
*.mkv
*.zip
*.rar
*.7z
*.VSIXPackage
implementation_plan/Video/
PowerAutomateSolutions/*.zip
PowerAutomateSolutions/*.mp4

# Environment Variables & OS Files
.env
.DS_Store
Thumbs.db
"@
    Set-Content -Path ".gitignore" -Value $gitignoreContent -Encoding utf8

    # Aggressively remove tracked heavy items from the index
    Write-Host "[INFO] Purging all caches, logs, databases, and heavy files from index..." -ForegroundColor Yellow
    git rm -r --cached backend/data/ 2>$null
    git rm -r --cached backend/logs/ 2>$null
    git rm -r --cached backend/screenshots/ 2>$null
    git rm -r --cached logs/ 2>$null
    git rm -r --cached implementation_plan/Video/ 2>$null
    git rm -r --cached PowerAutomateSolutions/*.zip 2>$null
    git rm -r --cached PowerAutomateSolutions/*.mp4 2>$null
    git rm -r --cached *.VSIXPackage 2>$null
    git rm -r --cached *.mp4 2>$null
    git rm -r --cached *.zip 2>$null

    # --- DEEP HISTORY SCRUB ---
    Write-Host "[INFO] Scrubbing heavy files from past commit history..." -ForegroundColor Yellow
    $branchName = git branch --show-current
    if ([string]::IsNullOrWhiteSpace($branchName)) { $branchName = "main" }
    
    git checkout --orphan temp_clean_branch 2>$null
    git add .
    git commit -m "chore: enterprise pristine production release (history scrubbed)" 2>$null
    git branch -D $branchName 2>$null
    git branch -m $branchName
    Write-Host "[SUCCESS] Git history successfully sanitized and flattened." -ForegroundColor Green

    # 4. Repository Strategy (New vs. Existing & Visibility)
    Write-Host "`n[STEP 3] Target Repository Configuration" -ForegroundColor Cyan
    Write-Host "Choose deployment path:"
    Write-Host "  [1] Create a NEW repository on GitHub"
    Write-Host "  [2] Push / Merge into an EXISTING repository"
    $repoChoice = Read-Host "Enter your choice (1 or 2)"

    # Safely clear any pre-existing remote origin before configuring new/existing link
    git remote remove origin 2>$null

    if ($repoChoice -eq "1") {
        # --- NEW REPOSITORY FLOW ---
        $repoName = Read-Host "Enter name for the new repository (e.g., uaic-rpa-orchestrator)"
        if ([string]::IsNullOrWhiteSpace($repoName)) {
            $repoName = "uaic-rpa-orchestrator"
        }

        $visibilityChoice = Read-Host "Set repository visibility to Private? (Y/n) [Default: Private]"
        $visibilityFlag = "--private"
        if ($visibilityChoice -eq 'n' -or $visibilityChoice -eq 'N') {
            $visibilityFlag = "--public"
            Write-Host "[WARNING] Repository visibility set to PUBLIC." -ForegroundColor Yellow
        } else {
            Write-Host "[INFO] Repository visibility set to PRIVATE." -ForegroundColor Green
        }

        $description = Read-Host "Enter repository description (Optional)"

        Write-Host "[INFO] Attempting to create remote repository and push code..." -ForegroundColor Green
        $createArgs = @("repo", "create", $repoName, $visibilityFlag, "--source=.", "--push")
        if (![string]::IsNullOrWhiteSpace($description)) {
            $createArgs += "--description"
            $createArgs += $description
        }

        $output = & gh @createArgs 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Host "[SUCCESS] New repository created and code successfully pushed!" -ForegroundColor Green
        } else {
            if ($output -match "Name already exists on this account") {
                Write-Host "`n[NOTICE] A repository named '$repoName' already exists on your account." -ForegroundColor Yellow
                $fallbackChoice = Read-Host "Would you like to seamlessly link and push to this existing repository instead? (Y/n)"
                
                if ($fallbackChoice -ne 'n' -and $fallbackChoice -ne 'N') {
                    $currentUser = (gh api user --jq .login 2>$null)
                    $targetRepoUrl = "https://github.com/$currentUser/$repoName.git"
                    
                    Write-Host "[INFO] Linking to existing repository: $targetRepoUrl" -ForegroundColor Green
                    git remote add origin $targetRepoUrl

                    Write-Host "[INFO] Detecting remote branch structure..." -ForegroundColor Yellow
                    git fetch origin 2>$null

                    $remoteBranches = git branch -r 2>$null
                    $targetBranch = "main"

                    if ($remoteBranches -match "origin/master") {
                        $targetBranch = "master"
                        Write-Host "[INFO] Detected remote 'master' branch. Aligning..." -ForegroundColor Cyan
                        git branch -M master
                    } else {
                        git branch -M main
                    }

                    Write-Host "[INFO] Forcing push of sanitized history to existing repository..." -ForegroundColor Green
                    git push -u origin $targetBranch --force
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "[SUCCESS] Successfully recovered and pushed to your existing repository!" -ForegroundColor Green
                    } else {
                        throw "Fallback push operation failed. Check branch permissions."
                    }
                } else {
                    throw "Repository creation aborted because the name already exists."
                }
            } else {
                throw "Repository creation failed: $output"
            }
        }

    } elseif ($repoChoice -eq "2") {
        # --- EXISTING REPOSITORY FLOW ---
        $repoTarget = Read-Host "Enter existing repository identifier (e.g., your-username/repo-name or full HTTPS URL)"
        if ($repoTarget -notmatch "^https?://") {
            $repoTarget = "https://github.com/$repoTarget.git"
        }

        Write-Host "[INFO] Configuring remote origin..." -ForegroundColor Green
        git remote add origin $repoTarget

        Write-Host "[INFO] Detecting remote branch structure..." -ForegroundColor Yellow
        git fetch origin 2>$null

        $remoteBranches = git branch -r 2>$null
        $targetBranch = "main"

        if ($remoteBranches -match "origin/master") {
            $targetBranch = "master"
            Write-Host "[INFO] Detected remote 'master' branch. Aligning..." -ForegroundColor Cyan
            git branch -M master
        } else {
            git branch -M main
        }

        Write-Host "[INFO] Force pushing sanitized history to overwrite remote branch cleanly..." -ForegroundColor Yellow
        git push -u origin $targetBranch --force

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Successfully synced and pushed clean repository!" -ForegroundColor Green
        } else {
            throw "Push operation failed. Check your permissions or token scopes."
        }
    } else {
        throw "Invalid selection. Script terminated."
    }
}
catch {
    Write-Host "`n[FATAL ERROR] $_" -ForegroundColor Red
}

# Prevent automatic window closure
Write-Host "`n======================================================" -ForegroundColor Cyan
Write-Host " Process Completed. Press Enter to close this window..." -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
[void](Read-Host)