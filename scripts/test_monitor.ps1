. .\setup_local.ps1 -NoPrompt -ErrorAction SilentlyContinue
Invoke-CheckServiceHealth "Frontend Web Application" 3000 "http://localhost:3000"
Invoke-CheckServiceHealth "FastAPI Backend & API" 8000 "http://localhost:8000/api/v1/health"
Invoke-CheckServiceHealth "Celery Flower Monitor" 5555
Invoke-CheckServiceHealth "MailDev Web Inspector" 1080 "http://localhost:1080"
Invoke-CheckServiceHealth "MailDev SMTP Server" 1025
Invoke-CheckServiceHealth "Redis Queue Broker" 6379
Invoke-CheckServiceHealth "PostgreSQL Database" 5432
