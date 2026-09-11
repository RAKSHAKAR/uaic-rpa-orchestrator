$allErrors = 0
$root = Join-Path $PSScriptRoot ".."
Get-ChildItem -Path $root -Filter "*.ps1" -Recurse | Where-Object { $_.FullName -notmatch '\\(\.venv|node_modules|\.git)\\' } | ForEach-Object {
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$null, [ref]$errors) | Out-Null
    Write-Host "$($_.Name) syntax errors: $($errors.Count)"
    if ($errors.Count -gt 0) {
        $errors | ForEach-Object { Write-Host "   Line $($_.Extent.StartLineNumber): $($_.Message)" }
    }
    $allErrors += $errors.Count
}
exit $allErrors
