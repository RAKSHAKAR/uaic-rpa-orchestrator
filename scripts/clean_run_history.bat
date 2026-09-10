@echo off
title UAIC Orchestrator - Clean Run & Queue History
color 0b

echo ======================================================================
echo           UAIC Orchestrator - Clean Run and Queue History
echo ======================================================================
echo.
echo This script will completely clear:
echo   1. All Celery Redis queues (scrapers, ingest, matcher, notifications)
echo   2. All SQLite claim records, batch logs, and scraped court cases
echo   3. Backup orchestrator.db to orchestrator.db.bak
echo   4. Reset system settings to clean defaults (blank Chrome profile)
echo.
set /p CONFIRM="Are you sure you want to clean all history? (Y/N): "
if /I NOT "%CONFIRM%"=="Y" (
    echo [INFO] Operation cancelled by user.
    pause
    exit /b 0
)

echo.
echo [1/2] Locating Python environment...
set PYTHON_EXE=
if exist "%~dp0..\backend\.venv\Scripts\python.exe" (
    set PYTHON_EXE="%~dp0..\backend\.venv\Scripts\python.exe"
) else if exist "%~dp0..\backend\venv\Scripts\python.exe" (
    set PYTHON_EXE="%~dp0..\backend\venv\Scripts\python.exe"
) else (
    set PYTHON_EXE=python
)

echo Using Python: %PYTHON_EXE%
echo.
echo [2/2] Running cleanup script...
cd /d "%~dp0..\backend"
%PYTHON_EXE% -m app.scripts.clean_history
if errorlevel 1 (
    echo.
    echo [ERROR] Cleanup encountered an error.
) else (
    echo.
    echo [SUCCESS] All run history, Redis queues, and worker records cleared cleanly!
)

echo.
pause
