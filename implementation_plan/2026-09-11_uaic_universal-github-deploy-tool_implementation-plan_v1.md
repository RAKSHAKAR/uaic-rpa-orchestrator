# Implementation Plan: Universal Enterprise GitHub Deployment & Operations Console (Deploy-To-GitHub.ps1)

**Implementation ID:** `IMP-2026-0911-007`  
**Target:** `Deploy-To-GitHub.ps1` (and `scripts/Deploy-To-GitHub.ps1`)  
**Objective:** Create a 100% universal, solution-agnostic, interactive enterprise PowerShell deployment and GitHub management console. Includes an automated prerequisite installation assistant, multi-account credential management, large file guards, repository health and sanitization, dynamic branch/PR/release operations, and multi-mode deployment.

---

## 1. Architectural Principles & Zero-Dependency Design

1. **Zero Project Hardcoding:**
   - Zero hardcoded folder paths (no `backend/data/`, no `PowerAutomateSolutions/`, no `implementation_plan/Video/`, etc.).
   - Default repository and branch names are dynamically derived at runtime (`Split-Path -Leaf (Get-Location)`, `git branch --show-current`).
2. **Safe Against Data Loss:**
   - Never overwrite or erase existing `.gitignore` files; merge missing rules intelligently.
   - Never wipe out git history silently. History squashing is isolated in a dedicated tool with mandatory `y/N` confirmation.
   - Never delete remote configurations unconditionally.
   - Support safe push (fast-forward), pull & merge remote changes, or confirmed force push.
3. **Automated Prerequisites Verification & On-Demand Installer:**
   - Checks Git installation & version.
   - Checks GitHub CLI (`gh`) installation & version.
   - If missing, displays formatted diagnostic status and prompts: *"Would you like to install <tool> automatically via Windows Package Manager (winget)? (Y/n)"*.
   - If user accepts, executes automated installation, refreshes process `PATH`, verifies installation, and proceeds seamlessly.
   - Verifies Git user identity (`user.name`, `user.email`). If unset, offers to auto-configure using active GitHub CLI profile data.
4. **Multi-Account Credential Helper Binding:**
   - Scans and lists all authenticated GitHub accounts, clearly tagging the `(Currently Active)` account.
   - Supports 1-click switching (`gh auth switch -u <user>`).
   - Automatically executes `gh auth setup-git` on selection to bind Git's credential helper directly to GitHub CLI, preventing Windows Credential Manager 403 authorization failures.
5. **GitHub 100MB Hard File Limit Guard:**
   - Pre-commit & pre-push scanning for files $\ge 95\text{MB}$.
   - Displays file size in MB and gives one-click capability to append them to `.gitignore` and untrack them from Git's index.
6. **Enterprise Git & GitHub Lifecycle Operations Suite:**
   - Authentication & Account Management (status, switch, login)
   - Intelligent `.gitignore` Enforcer & Universal Untracking (`git rm -r --cached . && git add .`)
   - Large File Scanner (100MB Guard)
   - Deployment Engine (Create New Repo Public/Private OR Sync/Merge with Existing Remote)
   - Branch Management & Synchronization (list, create, switch, sync/pull)
   - Pull Request Operations (create PR, view status, list PRs)
   - Tagging & Release Management (create git tag, create GitHub release)
   - Optional History Flattening / Squashing (pristine release with confirmation)
   - Self-Test & Diagnostic Check

---

## 2. Detailed Technical Design

### A. Prerequisites Assistant (`Test-And-Install-Prerequisites`)
- Scans environment:
  - `git` (version check)
  - `gh` (version check)
  - `winget` (for automated installation if needed)
- If missing:
  - Prompt user to install automatically via `winget install --id Git.Git -e --source winget` or `winget install --id GitHub.cli -e --source winget`.
  - Refresh `$env:Path` from registry without requiring terminal restart.
  - Re-verify immediately.
- Git User Configuration Check:
  - Tests `git config --get user.name` and `git config --get user.email`.
  - If missing, queries GitHub CLI (`gh api user`) to get default user name/email or prompts user.

### B. Multi-Account Management (`Select-GitHubAccount`)
- Parses `gh auth status 2>&1`.
- Extracts all logged-in accounts and hostnames.
- Identifies the currently active account.
- If switching accounts: executes `gh auth switch -u $account` followed immediately by `gh auth setup-git` to bind Git's credential manager to the active session.

### C. Universal Smart `.gitignore` Engine (`Invoke-GitignoreEnforce`)
- Standardized cross-stack enterprise template:
  - Python (`.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`)
  - Node.js / Web (`node_modules/`, `dist/`, `build/`, `.next/`, `.nuxt/`, `out/`, `coverage/`, `.turbo/`)
  - .NET / C# (`bin/`, `obj/`, `*.user`, `*.suo`)
  - Java / JVM (`target/`, `.gradle/`, `build/`)
  - Go / Rust (`vendor/`, `target/`)
  - Databases & Storage (`*.db`, `*.sqlite*`, `*.log`, `logs/`, `*.tmp`, `*.bak`)
  - Secrets & Environment (`.env`, `.env.local`, `.env.*.local`, `*.pem`, `*.key`)
  - Heavy Media / Binaries (>100MB protection: `*.mp4`, `*.mov`, `*.zip`, `*.rar`, `*.7z`, `*.tar.gz`, `*.iso`, `*.VSIXPackage`)
  - OS / IDE (`.DS_Store`, `Thumbs.db`, `desktop.ini`, `.idea/`)
- If `.gitignore` already exists:
  - Reads existing lines.
  - Identifies which standard rules are not yet covered.
  - Appends only missing rules under `# --- Enterprise Standard Rules ---`, keeping existing custom rules 100% intact.
- Untracks newly ignored files universally:
  - Executes `git rm -r --cached . 2>$null` followed by `git add .` to remove ignored items from the index without deleting files on disk.

### D. Large File Guard (`Invoke-LargeFileScan`)
- Scans working directory recursively (excluding `.git`, `node_modules`, `.venv`).
- Flags files with `Length -ge 95MB`.
- Warns user with formatted table: Name, Size in MB, Path.
- Offers automatic exclusion into `.gitignore` and untracks from Git index.

### E. Multi-Mode Deployment Engine (`Invoke-DeployToGitHub`)
- Pre-flight checks: working tree dirty check, large file check.
- Commit workflow: default message `chore: enterprise release` or custom user message.
- Target Remote Resolution:
  - Detects existing `origin`:
    - If found: allows pushing directly to current remote, changing remote, or creating a new repo.
    - If not found: offers new repo creation or connecting to existing remote.
- Create New Repository:
  - Auto-suggests repository name based on current directory: `Split-Path -Leaf (Get-Location)`.
  - Prompts for visibility (default: Private).
  - Prompts for description.
  - Executes `gh repo create $repoName $visibilityFlag --source=. --push`.
- Push / Sync to Existing Repository:
  - Detects current branch dynamically (`git branch --show-current`, fallback `main`).
  - Safe push options:
    1. Standard Push (fast-forward)
    2. Pull & Merge Remote Changes (`git pull origin $branch --allow-unrelated-histories --no-rebase` then push)
    3. Force Push (with explicit user confirmation warning)

### F. Additional Dynamic Enterprise Activities
- Branch Management (list, create, switch, sync)
- Pull Request Operations (`gh pr create`, `gh pr list`, `gh pr status`)
- Release & Tag Management (`git tag`, `gh release create`)
- Safe Commit History Squashing (Option with confirmation prompt)
- Diagnostics & Self-Test

---

## 3. Verification Plan

1. **PowerShell Syntax Parsing:**
   - Execute `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"`.
   - Must return 0 errors across all `.ps1` files.
2. **Coupling Audit:**
   - Search `Deploy-To-GitHub.ps1` for any solution keywords (`UAIC`, `PowerAutomate`, `backend/data`, etc.). Zero matches allowed.
3. **Execution & Interactive Flow Verification:**
   - Test non-destructive menu functions (Prerequisites check, Account detection, Auth status, Large file scan).
4. **File Synchronization:**
   - Verify `Deploy-To-GitHub.ps1` in root and `scripts/Deploy-To-GitHub.ps1` are identical.
