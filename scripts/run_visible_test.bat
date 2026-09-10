@echo off
title UAIC Visible Browser Test
echo ========================================================
echo Launching Playwright Chrome in Visible GUI Attended Mode...
echo ========================================================
cd /d "%~dp0"
if exist "%~dp0..\backend\.venv\Scripts\python.exe" (
    "%~dp0..\backend\.venv\Scripts\python.exe" "%~dp0live_visible_scrape.py"
) else if exist "%~dp0..\backend\venv\Scripts\python.exe" (
    "%~dp0..\backend\venv\Scripts\python.exe" "%~dp0live_visible_scrape.py"
) else (
    python "%~dp0live_visible_scrape.py"
)
pause
