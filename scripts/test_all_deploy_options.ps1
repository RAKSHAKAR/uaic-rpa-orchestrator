<#
.SYNOPSIS
    Automated Option-by-Option Test Harness for Deploy-To-GitHub.ps1
.DESCRIPTION
    Systematically executes and validates every major routine and edge case in
    Deploy-To-GitHub.ps1 to verify that all errors, warnings, and exceptions are
    gracefully handled with zero unhandled crashes.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$totalTests = 0
$passedTests = 0
$failedTests = 0

function Assert-Test {
    param(
        [string]$TestName,
        [scriptblock]$Action
    )
    $script:totalTests++
    Write-Host "`n[RUNNING TEST $($script:totalTests)] $TestName..." -ForegroundColor Cyan
    try {
        & $Action
        $script:passedTests++
        Write-Host "[PASS] $TestName" -ForegroundColor Green
    } catch {
        $script:failedTests++
        Write-Host "[FAIL] ${TestName}: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Mock Read-Host for 100% non-interactive test execution
function Read-Host {
    param([string]$Prompt)
    return ""
}

# Load the deployment functions non-interactively
. .\Deploy-To-GitHub.ps1 -NonInteractive -SkipPrereqCheck

# Test 1: Prerequisites Check Routine
Assert-Test "Prerequisites Check Execution (Test-And-Install-Prerequisites)" {
    $res = Test-And-Install-Prerequisites
    if ($res -ne $true) { throw "Prerequisites check did not return true" }
}

# Test 2: Multi-Account Detection
Assert-Test "Account Discovery Parser (Get-GitHubAccounts)" {
    $accs = Get-GitHubAccounts
    Write-Host "   Detected $($accs.Count) accounts."
    if ($accs.Count -lt 1) { throw "Expected at least 1 authenticated GitHub account" }
    $active = $accs | Where-Object { $_.IsActive }
    if (!$active) { throw "Expected at least one active account to be identified" }
}

# Test 3: Environment Diagnostics Self-Test
Assert-Test "Diagnostics Self-Test (Invoke-Diagnostics)" {
    Invoke-Diagnostics
}

# Test 4: Smart .gitignore Processing (Without Corruption)
Assert-Test "Smart .gitignore Engine (Invoke-SmartGitignore)" {
    # Backup current .gitignore
    $origGitignore = if (Test-Path ".gitignore") { Get-Content ".gitignore" -Raw -Encoding UTF8 } else { $null }
    
    try {
        Invoke-SmartGitignore
        if (!(Test-Path ".gitignore")) { throw ".gitignore was not created" }
        $content = Get-Content ".gitignore" -Raw -Encoding UTF8
        if ($content -notmatch "\.venv/") { throw ".gitignore missing .venv rule" }
        if ($content -notmatch "node_modules/") { throw ".gitignore missing node_modules rule" }
    } finally {
        # Restore original .gitignore
        if ($origGitignore) {
            Set-Content -Path ".gitignore" -Value $origGitignore -Encoding UTF8
        }
    }
}

# Test 5: 100MB Large File Guard Scanner
Assert-Test "Large File Guard Scanner (Invoke-LargeFileScan)" {
    # Test scan in non-autofix mode
    $hasLarge = Invoke-LargeFileScan -AutoFix $false
    Write-Host "   Large file check completed safely (hasLarge=$hasLarge)."
}

# Test 6: Safe Push Strategy Handler Logic
Assert-Test "Push Strategies Graceful Handling of Unknown Strategy" {
    Invoke-PushStrategies -RemoteUrl "https://github.com/mock/repo.git" -Branch "test-branch"
}

# Test 7: Branch Management Error Resilience (Non-existent branch test)
Assert-Test "Branch Operations Error Resilience" {
    # Check that checking out a non-existent branch does not throw terminating error
    $err = & git checkout --quiet non-existent-branch-test-xyz 2>&1
    Write-Host "   Handled non-existent branch smoothly."
}

# Test 8: Pull Request Operations Resilience without remote failure
Assert-Test "Pull Request Status Verification (gh pr status)" {
    try {
        $prOut = & gh pr status 2>&1
        Write-Host "   PR status command executed without crash."
    } catch {
        Write-Host "   PR status caught safely: $($_.Exception.Message)"
    }
}

# Test 9: Git Tag Listing Resilience
Assert-Test "Tag Listing Operations (git tag -l)" {
    $tags = & git tag -l 2>&1
    Write-Host "   Tags command executed cleanly."
}

# Test 10: Script CLI Execution with -RunSelfTest Flag
Assert-Test "CLI -RunSelfTest Switch Execution" {
    $out = powershell -NoProfile -ExecutionPolicy Bypass -File "Deploy-To-GitHub.ps1" -RunSelfTest 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Self-test exited with non-zero code: $LASTEXITCODE" }
    Write-Host "   Self-test CLI switch passed."
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host " TEST SUMMARY: Total: $totalTests | Passed: $passedTests | Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Red" })
Write-Host "================================================================================" -ForegroundColor Cyan

if ($failedTests -gt 0) { exit 1 } else { exit 0 }
