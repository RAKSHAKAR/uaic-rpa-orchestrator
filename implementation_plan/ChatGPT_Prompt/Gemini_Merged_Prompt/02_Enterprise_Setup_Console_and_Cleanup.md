# 02 - ENTERPRISE SETUP CONSOLE (OPTIONS 1-9) & DATA CLEANUP

## 1. CONSOLE ARCHITECTURE & OPTIONS 1-9
Audit and finalize the existing PowerShell/Python setup console scripts to ensure all options operate on real process management, not blind executions.
- **[1] Start All Services:** Support Interactive Launch (Attended GUI vs Unattended Headless). Check for port conflicts before starting.
- **[2] Stop / Kill All Services:** Safely terminate Ports 3000, 8000, 5555, 6379, 5432, Celery, and MUST explicitly stop MailDev (Ports 1080, 1025).
- **[4] Install Dependencies:** Support Python 3.14.7, Node, and Playwright. **CRITICAL:** Do NOT install bundled Playwright Chromium if the system Google Chrome is selected for RPA execution. If system Chromiumm is selected then it must check that bundled is insatlled or not, show the proper information with full instructions. So that if user want to test in Chromiumm then he must have all the information.
- **[5] Purge Folders:** Delete `.venv`, `node_modules`, `.next` safely without touching source code or credentials.
- **[6] RPA Mode:** Toggle Attended (GUI) vs Unattended (Headless). Ensure the backend honors this setting.
- **[7] Diagnostics:** Run Pytest, Ruff, and TypeScript. Fix underlying issues causing `PytestUnraisableExceptionWarning`.
- **[8] Docker:** Manage the containerized stack safely.
- **[9] Live Monitor:** Show real health checks (not just open ports) for Frontend, Backend, Redis, Celery, Flower, and MailDev.
- **[M] MailDev:** Open localhost:1080 and verify SMTP/HTTP health.

## 2. OPTION [3] - ENTERPRISE DATA CLEANUP
Transform Option 3 into a complete enterprise data-retention engine.
- **Categories:** Support multi-select for Claims, Queue Data, Scraped Cases, Fuzzy Matches, Guidewire Data, Notifications, Telemetry, Logs, and Caches.
- **Time Scope:** Support Days, Weeks, Months, Years, Custom Range, and dynamically calculated **Current Month**.
- **Safety:** Require a Dry-Run preview. Require explicit confirmation. Implement transactional rollback.
- **Reconciliation:** The cleanup MUST be relationship-aware. If parent records are deleted, child records (e.g., Notification Delivery History) must be cascade-deleted to prevent orphans. Invalidate Dashboard and Redis caches post-cleanup.



Suporting Docs you can ref:
1) UAIC_Enterprise_Setup_Console_Master_Prompt.md  
2) Complete Validation of Setup Console Actions 1–9 + Enterprise Time-Based Data Cleanup.md  
3) Enterprise Setup Console — Complete Options 1–9 + MailDev Validation, Repair & Productionization Prompt.md  

Note: Most of them are already implemented, test before making any changes.



