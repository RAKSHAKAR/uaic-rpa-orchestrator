$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*celery*" }
foreach ($p in $procs) {
    [PSCustomObject]@{
        ProcessId = $p.ProcessId
        Name = $p.Name
        CommandLine = $p.CommandLine
    }
}
