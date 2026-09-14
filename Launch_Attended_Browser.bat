@echo off
title UAIC Orchestrator - Launch Attended Browser
echo =======================================================================
echo          UAIC Orchestrator - Interactive Attended GUI Launcher
echo =======================================================================
echo.
echo Launching visible browser onto your active Windows desktop...
echo.

cd /d "%~dp0backend"
.\.venv\Scripts\python.exe scripts\launch_attended_gui.py

echo.
pause
