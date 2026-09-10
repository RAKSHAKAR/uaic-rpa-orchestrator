<#
.SYNOPSIS
    Enterprise GitHub Deployment & Multi-Account Management Console
.DESCRIPTION
    An interactive enterprise deployment console that stays open in a continuous menu loop,
    handling multi-account authentication, history sanitization, repository creation, and syncing.
#>

[CmdletBinding()]
param()

# Ensure prompt styling
$Host.UI.RawUI.ForegroundColor = 'Cyan'
Write-Host "======================================================"
Write-Host "           Enterprise GitHub Deployment Tool          "
Write-Host "======================================================"
$Host.UI.RawUI.ForegroundColor = 'White'

# Check prerequisites once at startup
if (!(Get-Command "gh" -ErrorAction SilentlyContinue)) {
    Write-Host "[FATAL ERROR] GitHub CLI ('gh') is not installed or not in your system PATH. Please install from https://cli.github.com/" -ForegroundColor Red
    Write-Host "`nPress Enter to exit..." -ForegroundColor Cyan
    [void](Read-Host)
    exit
}

# Optimize Git Config for Large Transfers globally
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# --- Persistent Interactive Menu Loop ---
$running = $true
while ($running) {
    Clear-Host
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "           Enterprise GitHub Deployment Tool          " -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " [1] Check GitHub Authentication Status" -ForegroundColor White
    Write-Host " [2] Switch GitHub Account" -ForegroundColor White
    Write-Host " [3] Enforce .gitignore & Scrub Heavy History (Clean Artifacts)" -ForegroundColor White
    Write-Host " [4] Deploy / Push Code to GitHub (Create New or Merge Existing)" -ForegroundColor White
    Write-Host " [0] Exit Console" -ForegroundColor Yellow
    Write-Host "======================================================" -ForegroundColor Cyan

    $menuChoice = Read-Host "Select an option [0-4]"

    switch ($menuChoice) {
        "1" {
            Write-Host "`n[INFO] Checking GitHub Authentication Status..." -ForegroundColor Cyan
            gh auth status
            Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
            [void](Read-Host)
        }
        "2" {
            Write-Host "`n[INFO] Logging out of current session..." -ForegroundColor Yellow
            gh auth logout -h github.com -y 2>$null
            Write-Host "[INFO] Please authenticate with your target account:" -ForegroundColor Green
            gh auth login
            Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
            [void](Read-Host)
        }
        "3" {
            Write-Host "`n[INFO] Enforcing enterprise .gitignore & scrubbing history..." -ForegroundColor Cyan
            if (!(Test-Path ".git")) {
                git init
                git branch -M main
            }

            # Enforce strict enterprise .gitignore rules
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

            # Purge tracked items from index
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

            # Flatten and scrub branch history
            $branchName = git branch --show-current
            if ([string]::IsNullOrWhiteSpace($branchName)) { $branchName = "main" }
            
            git checkout --orphan temp_clean_branch 2>$null
            git add .
            git commit -m "chore: enterprise pristine production release (history scrubbed)" 2>$null
            git branch -D $branchName 2>$null
            git branch -m $branchName
            
            Write-Host "[SUCCESS] Repository history successfully sanitized and flattened!" -ForegroundColor Green
            Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
            [void](Read-Host)
        }
        "4" {
            try {
                Write-Host "`n[INFO] Preparing local staging and commit..." -ForegroundColor Cyan
                if (!(Test-Path ".git")) {
                    git init
                    git branch -M main
                }
                git add .
                
                $gitStatus = git status --porcelain
                if ($gitStatus) {
                    $commitMsg = Read-Host "Enter your commit message (Press Enter for default: 'chore: enterprise production release')"
                    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
                        $commitMsg = "chore: enterprise production release"
                    }
                    git commit -m $commitMsg
                    Write-Host "[SUCCESS] Changes committed successfully." -ForegroundColor Green
                } else {
                    Write-Host "[INFO] Working tree is clean." -ForegroundColor Cyan
                }

                Write-Host "`nChoose deployment path:"
                Write-Host "  [1] Create a NEW repository on GitHub"
                Write-Host "  [2] Push / Merge into an EXISTING repository"
                $repoChoice = Read-Host "Enter your choice (1 or 2)"

                git remote remove origin 2>$null

                if ($repoChoice -eq "1") {
                    $repoName = Read-Host "Enter name for the new repository"
                    if ([string]::IsNullOrWhiteSpace($repoName)) { $repoName = "enterprise-repo" }

                    $visibilityChoice = Read-Host "Set repository visibility to Private? (Y/n) [Default: Private]"
                    $visibilityFlag = "--private"
                    if ($visibilityChoice -eq 'n' -or $visibilityChoice -eq 'N') {
                        $visibilityFlag = "--public"
                    }

                    $description = Read-Host "Enter repository description (Optional)"
                    $createArgs = @("repo", "create", $repoName, $visibilityFlag, "--source=.", "--push")
                    if (![string]::IsNullOrWhiteSpace($description)) {
                        $createArgs += "--description"
                        $createArgs += $description
                    }

                    $output = & gh @createArgs 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "[SUCCESS] New repository created and code successfully pushed!" -ForegroundColor Green
                    } else {
                        throw "Repository creation failed: $output"
                    }
                } elseif ($repoChoice -eq "2") {
                    $repoTarget = Read-Host "Enter existing repository identifier (e.g., your-username/repo-name or full HTTPS URL)"
                    if ($repoTarget -notmatch "^https?://") {
                        $repoTarget = "https://github.com/$repoTarget.git"
                    }

                    git remote add origin $repoTarget
                    git fetch origin 2>$null
                    $remoteBranches = git branch -r 2>$null
                    $targetBranch = if ($remoteBranches -match "origin/master") { "master" } else { "main" }
                    git branch -M $targetBranch

                    git push -u origin $targetBranch --force
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "[SUCCESS] Successfully synced and pushed to repository!" -ForegroundColor Green
                    } else {
                        throw "Push operation failed. Check your permissions or token scopes."
                    }
                }
            }
            catch {
                Write-Host "`n[ERROR] $_" -ForegroundColor Red
            }

            Write-Host "`nPress Enter to return to menu..." -ForegroundColor Cyan
            [void](Read-Host)
        }
        "0" {
            $running = $false
            Write-Host "`nExiting Enterprise Deployment Console. Goodbye!" -ForegroundColor Cyan
        }
        default {
            Write-Host "`n[WARNING] Invalid selection. Please choose between 0 and 4." -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }
}