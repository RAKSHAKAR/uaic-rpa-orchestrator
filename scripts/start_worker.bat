@echo off
title UAIC Celery Worker (Attended Mode)
echo ===================================================
echo Starting UAIC Celery Worker in Attended GUI Mode...
echo ===================================================
cd /d "%~dp0..\backend"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
celery -A app.core.celery_app.celery_app worker -E --loglevel=info -Q ingest,scrapers,matcher,notifications,default --pool=threads --concurrency=10
pause
