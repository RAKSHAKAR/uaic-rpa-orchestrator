<#
.SYNOPSIS
    Root Operations & Setup Entrypoint for UAIC Orchestrator
#>

param(
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

$scriptPath = Join-Path $PSScriptRoot "setup_local.ps1"
if (Test-Path $scriptPath) {
    & $scriptPath @PSBoundParameters
} else {
    Write-Error "setup_local.ps1 not found in $PSScriptRoot"
}