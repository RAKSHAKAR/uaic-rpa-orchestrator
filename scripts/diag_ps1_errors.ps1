$errors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path 'setup_local.ps1').Path,
    [ref]$null,
    [ref]$errors
)
Write-Host ("Total syntax errors: " + $errors.Count)
if ($errors.Count -gt 0) {
    $errors | Select-Object @{N='Line';E={$_.Extent.StartLineNumber}}, Message | Format-Table -AutoSize
}
