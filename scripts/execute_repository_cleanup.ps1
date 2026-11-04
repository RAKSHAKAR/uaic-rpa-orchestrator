<#
.SYNOPSIS
    UAIC RPA Orchestrator - Canonical Directory Restructuring and Duplicate Cleanup
    Implementation ID: IMP-2026-1031-002
#>

$ErrorActionPreference = "Stop"
$rootDir = (Get-Item $PSScriptRoot).Parent.FullName

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " UAIC RPA Orchestrator - Repository Restructuring" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Root Directory Cleanup
# Remove 0-byte orphan orchestrator.db in root (active is in backend/orchestrator.db)
$rootDb = Join-Path $rootDir "orchestrator.db"
if (Test-Path $rootDb) {
    $item = Get-Item $rootDb
    if ($item.Length -eq 0) {
        Remove-Item -Path $rootDb -Force
        Write-Host "[CLEANUP] Removed 0-byte orphan root orchestrator.db" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] root orchestrator.db is not 0 bytes; skipping removal" -ForegroundColor Yellow
    }
}

# Move root scripts into scripts/
$filesToMoveToScripts = @("Launch_Attended_Browser.bat", "Deploy-To-GitHub.ps1")
foreach ($f in $filesToMoveToScripts) {
    $src = Join-Path $rootDir $f
    $dst = Join-Path $rootDir ("scripts\" + $f)
    if (Test-Path $src) {
        Move-Item -Path $src -Destination $dst -Force
        Write-Host "[MOVED] $f -> scripts/$f" -ForegroundColor Green
    }
}

# Move root docs into docs/
$filesToMoveToDocs = @(
    "CLIENT_DEMO_VERIFICATION_WALKTHROUGH.md",
    "DEPLOYMENT.md",
    "DEPLOYMENT_AND_HOSTING_GUIDE.md"
)
foreach ($f in $filesToMoveToDocs) {
    $src = Join-Path $rootDir $f
    $dst = Join-Path $rootDir ("docs\" + $f)
    if (Test-Path $src) {
        Move-Item -Path $src -Destination $dst -Force
        Write-Host "[MOVED] $f -> docs/$f" -ForegroundColor Green
    }
}

# Move ProdRecords8Bots.xlsx into e2e/fixtures/
$e2eFixtures = Join-Path $rootDir "e2e\fixtures"
if (-not (Test-Path $e2eFixtures)) {
    New-Item -ItemType Directory -Path $e2eFixtures -Force | Out-Null
    Write-Host "[CREATED] e2e/fixtures directory" -ForegroundColor Green
}
$prodRecords = Join-Path $rootDir "ProdRecords8Bots.xlsx"
if (Test-Path $prodRecords) {
    Move-Item -Path $prodRecords -Destination (Join-Path $e2eFixtures "ProdRecords8Bots.xlsx") -Force
    Write-Host "[MOVED] ProdRecords8Bots.xlsx -> e2e/fixtures/ProdRecords8Bots.xlsx" -ForegroundColor Green
}

# 2. Cleanup stale temporary test dumps in scripts/
$staleDirs = Get-ChildItem -Path (Join-Path $rootDir "scripts") -Directory -Filter "pytest_runtime_tmp_*"
foreach ($d in $staleDirs) {
    Remove-Item -Path $d.FullName -Recurse -Force
    Write-Host "[CLEANUP] Removed stale directory: $($d.Name)" -ForegroundColor Green
}
$testDownloads = Join-Path $rootDir "scripts\test_downloads"
if (Test-Path $testDownloads) {
    Remove-Item -Path $testDownloads -Recurse -Force
    Write-Host "[CLEANUP] Removed temporary test_downloads" -ForegroundColor Green
}

# 3. Canonical Visual Directory Restructuring
# Create canonical directories: docs/frames, docs/images, docs/recordings
$docsDir = Join-Path $rootDir "docs"
$framesDir = Join-Path $docsDir "frames"
$imagesDir = Join-Path $docsDir "images"
$recordingsDir = Join-Path $docsDir "recordings"

if (-not (Test-Path $framesDir)) {
    New-Item -ItemType Directory -Path $framesDir -Force | Out-Null
}
if (-not (Test-Path $imagesDir)) {
    New-Item -ItemType Directory -Path $imagesDir -Force | Out-Null
}
if (-not (Test-Path $recordingsDir)) {
    New-Item -ItemType Directory -Path $recordingsDir -Force | Out-Null
}

# Move frames from docs/recordings/frames to docs/frames
$misplacedFrames = Join-Path $recordingsDir "frames"
if (Test-Path $misplacedFrames) {
    Get-ChildItem -Path $misplacedFrames | ForEach-Object {
        $dest = Join-Path $framesDir $_.Name
        if (-not (Test-Path $dest)) {
            Move-Item -Path $_.FullName -Destination $dest -Force
        } else {
            Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
            Remove-Item -Path $_.FullName -Recurse -Force
        }
    }
    Remove-Item -Path $misplacedFrames -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "[MOVED] docs/recordings/frames -> docs/frames" -ForegroundColor Green
}

# Move loose .png files in docs/ to docs/images/
$loosePngs = Get-ChildItem -Path $docsDir -File -Filter "*.png"
$movedPngCount = 0
foreach ($png in $loosePngs) {
    $dest = Join-Path $imagesDir $png.Name
    Move-Item -Path $png.FullName -Destination $dest -Force
    $movedPngCount++
}
Write-Host "[MOVED] $movedPngCount loose .png files from docs/ -> docs/images/" -ForegroundColor Green

# Remove duplicate .webp files from docs/ (where identical file exists in docs/recordings/)
$looseWebps = Get-ChildItem -Path $docsDir -File -Filter "*.webp"
$removedDuplicateWebp = 0
$movedWebp = 0

foreach ($webp in $looseWebps) {
    $canonPath = Join-Path $recordingsDir $webp.Name
    if (Test-Path $canonPath) {
        $hashLoose = (Get-FileHash -Algorithm SHA256 $webp.FullName).Hash
        $hashCanon = (Get-FileHash -Algorithm SHA256 $canonPath).Hash
        if ($hashLoose -eq $hashCanon) {
            Remove-Item -Path $webp.FullName -Force
            $removedDuplicateWebp++
            Write-Host "[DEDUP] Removed duplicate: docs/$($webp.Name)" -ForegroundColor DarkGray
        } else {
            Write-Host "[CONFLICT] Hash mismatch for $($webp.Name) - preserved" -ForegroundColor Yellow
        }
    } else {
        # Move non-duplicate webp recordings into docs/recordings/
        Move-Item -Path $webp.FullName -Destination $canonPath -Force
        $movedWebp++
        Write-Host "[MOVED] Moved non-duplicate recording docs/$($webp.Name) -> docs/recordings/" -ForegroundColor Green
    }
}
Write-Host "[DEDUP] Removed $removedDuplicateWebp duplicate recordings from docs/" -ForegroundColor Green
Write-Host "[MOVED] Relocated $movedWebp recordings into docs/recordings/" -ForegroundColor Green

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " Directory Restructuring and Cleanup Complete!" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
