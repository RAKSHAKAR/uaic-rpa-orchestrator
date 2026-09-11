# Walkthrough: Universal Enterprise GitHub Deployment Tool (Deploy-To-GitHub.ps1)

**Implementation ID:** `IMP-2026-0911-007`  
**Target Files:**
- [Deploy-To-GitHub.ps1](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/Deploy-To-GitHub.ps1) (Master root console)
- [scripts/Deploy-To-GitHub.ps1](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/scripts/Deploy-To-GitHub.ps1) (Utility mirror)
- [DEPLOYMENT.md](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/DEPLOYMENT.md) (Documentation update)

---

## 1. Overview of Changes

The legacy `Deploy-To-GitHub.ps1` was heavily tied to the `Bot_UAIC` project structure, containing hardcoded paths, risky blind remote deletion, unconditional history flattening, missing credential binding, and no protection against GitHub's 100MB file limit.

The updated `Deploy-To-GitHub.ps1` is a **100% universal, cross-stack enterprise console** that can be dropped into **any project** (Node.js, Python, .NET, Java, Go, Rust, React, Flutter, PHP, etc.) to manage GitHub deployment and operations.

---

## 2. Interactive Console Menu Structure

```
================================================================================
           Enterprise GitHub Deployment and Operations Console                 
================================================================================
  Project: <DynamicFolderName>  |  Branch: <DynamicBranch>  |  Active GitHub: <ActiveAccount>
================================================================================
  ACCOUNT AND AUTHENTICATION:
    [1] View GitHub Auth and Account Status
    [2] Switch / Select Active GitHub Account (Multi-Account Manager)
    [3] Login to New GitHub Account (gh auth login)

  REPOSITORY HYGIENE AND PROTECTION:
    [4] Smart Universal .gitignore Enforcer and Index Untracker
    [5] Scan for Large Files (100MB GitHub Hard Limit Guard)
    [6] Flatten / Squash Commit History (Pristine Release)

  DEPLOYMENT AND SYNC:
    [7] Deploy / Push Code to GitHub (Create New or Sync/Merge Existing)
    [8] Branch Management and Sync (List, Create, Switch, Pull)
    [9] Pull Request Operations (Status, List, Create)
   [10] GitHub Releases and Tagging Management

  SYSTEM AND DIAGNOSTICS:
   [11] Prerequisites Diagnostic and Self-Test
    [0] Exit Console
================================================================================
```

---

## 3. Key Features Demonstrated

### A. Automated Prerequisites Diagnostic & Winget Installer
- Checks `git` and `gh` binaries and versions on startup.
- If missing, presents a formatted diagnostic banner and offers automatic one-click installation via `winget`.
- Automatically refreshes the session `$env:Path` from registry without requiring a terminal restart.
- Verifies Git user identity (`user.name`, `user.email`), auto-populating from active GitHub profile if missing.

### B. Multi-Account Manager & Credential Binding
- Scans all logged-in accounts on `github.com` or GitHub Enterprise Server.
- Clearly displays the active account badge: `[ACTIVE]`.
- Binds Git Credential Manager to GitHub CLI via `gh auth setup-git`, preventing 403 Forbidden errors.

### C. 100MB Large File Guard
- Scans working tree for files $\ge 95\text{MB}$.
- Outputs formatted table of oversized files:
```
--------------------------------------------------------------------------------
File Name                              Size (MB)  Relative Path
--------------------------------------------------------------------------------
Microsoft.VisualStudio.Services.VSIXPackage       179 MB  .\Microsoft.VisualStudio.Services.VSIXPackage
Recording 2026-09-07 161459.mp4        127.54 MB  .\implementation_plan\Video\Recording 2026-09-07 161459.mp4
...
--------------------------------------------------------------------------------
```
- Provides one-click automated `.gitignore` exclusion and Git cache untracking.

### D. Smart Universal `.gitignore` Engine
- Multi-stack rules covering Python, Node.js, .NET, Java, Go, Rust, databases (`*.db`, `*.sqlite*`), secrets (`.env*`), and OS files.
- Preserves existing custom `.gitignore` files; only missing enterprise rules are appended.
- Uses universal unindexing: `git rm -r --cached .` followed by `git add .`.

### E. Safe Multi-Mode Deployment
- Detects existing `origin` remote:
  - Option to push directly to current remote.
  - Option to create new repository via `gh repo create` (default name derived dynamically from folder name, default Private).
  - Option to change remote URL.
- Push strategies:
  1. Standard fast-forward push
  2. Pull & merge remote changes (`git pull --allow-unrelated-histories --no-rebase`)
  3. Force push (with confirmation prompt)

---

## 4. Verification Evidence

### PowerShell Syntax Check
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```
**Output:**
```
Deploy-To-GitHub.ps1 syntax errors: 0
setup.ps1 syntax errors: 0
setup_local.ps1 syntax errors: 0
check_ps1_syntax.ps1 syntax errors: 0
Deploy-To-GitHub.ps1 syntax errors: 0
diag_ps1_errors.ps1 syntax errors: 0
test_setup_console.ps1 syntax errors: 0
```

### Self-Test Diagnostic (`Deploy-To-GitHub.ps1 -RunSelfTest`)
```
================================================================================
  Enterprise Prerequisites and Health Check
================================================================================
  [OK] Git: Installed (git version 2.54.0.windows.1)
  [OK] GitHub CLI (gh): Installed (gh version 2.93.0 (2026-05-27))
  [OK] Git User Identity: Priye Rakshakar (priye_rakshakar@rediffmail.com)

[SUCCESS] All enterprise prerequisites are verified and ready!

================================================================================
  Comprehensive Environment Diagnostic and Self-Test
================================================================================
System Environment:
  OS Version:         Microsoft Windows NT 10.0.26200.0
  PowerShell Version: 5.1.26100.9278
  Working Directory:  C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC

Git Diagnostic:
  [OK] Git Binary:     C:\Program Files\Git\cmd\git.exe
  [OK] Git Version:    git version 2.54.0.windows.1
  [OK] Git User Name:  Priye Rakshakar
  [OK] Git User Email: priye_rakshakar@rediffmail.com
  [OK] postBuffer:     524288000 bytes

GitHub CLI Diagnostic:
  [OK] gh Binary:      C:\Program Files\GitHub CLI\gh.exe
  [OK] gh Version:     gh version 2.93.0 (2026-05-27)

GitHub Authentication Status:
github.com
  ✓ Logged in to github.com account RAKSHAKAR (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'

  ✓ Logged in to github.com account priyer-damco (keyring)
  - Active account: false
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'

Repository Diagnostic:
  [OK] Git Repo:       Initialized
  [OK] Current Branch: main
  [OK] Remotes:
origin	https://github.com/RAKSHAKAR/uaic-rpa-orchestrator.git (fetch)
origin	https://github.com/RAKSHAKAR/uaic-rpa-orchestrator.git (push)
```
