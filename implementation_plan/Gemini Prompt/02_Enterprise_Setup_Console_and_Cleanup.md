# 02 - ENTERPRISE SETUP CONSOLE (OPTIONS 1-9) & DATA CLEANUP

## 1. CONSOLE ARCHITECTURE
Audit and finalize the existing PowerShell/Python setup console scripts to ensure all options operate on real process management (e.g., `setup-local.ps1`) to reliably support Options 1 through 9 and [M], not blind executions.
- **[1] Start All Services:** Support Interactive Launch (Attended GUI vs Unattended Headless). Check port conflicts before starting.
- **[2] Stop All Services:** Safely terminate Ports 3000, 8000, 5555, 6379, 5432, Celery, and MUST explicitly stop MailDev (Ports 1080, 1025).
- **[4] Install Dependencies:** Support Python 3.14.7, Node, and Playwright. **CRITICAL:** DO NOT install bundled Chromium if the system Google Chrome is selected for RPA. Support Chromium, Google Chrome, and Edge dynamically.
- **[5] Purge Folders:** Delete `.venv`, `node_modules`, `.next` safely without touching source code or credentials. Add if any unused file/folder not listed.
- **[6] RPA Mode:** Toggle Attended (GUI) vs Unattended (Headless). Ensure the backend honors this setting.
- **[7] Diagnostics:** Run Pytest, Ruff, TypeScript checks. Do not hide `PytestUnraisableExceptionWarnings`. Fix underlying issues causing `PytestUnraisableExceptionWarning`.
- **[8] Docker:** Start/stop containerized stack safely.
- **[9] Live Monitor:** Show real health checks (not just open ports) for Frontend, Backend, Redis, Celery, Flower, and MailDev.
- **[M] MailDev:** Open localhost:1080 and verify SMTP/HTTP health.

## 2. OPTION [3] - ENTERPRISE DATA CLEANUP
Transform Option 3 into a time-based, multi-select cleanup engine.
- **Categories:** Must support multi-select for Claims, Queue Data, Scraped Cases, Fuzzy Matches, Guidewire Data, Notifications, Telemetry, Logs, and Caches.
- **Time Scope:** Must support **Current Month** (dynamically calculated), Days, Weeks, Months, Years, and Custom Date Ranges.
- **Safety:** Require a Dry-Run preview. Require explicit confirmation. Implement transactional rollback.
- **Reconciliation:** The cleanup MUST be relationship-aware. If parent records are deleted, child records (e.g., Notification Delivery History) must be cascade-deleted to prevent orphans. Invalidate Dashboard and Redis caches post-cleanup.


Supporting Docs you can ref:
    1) UAIC_Enterprise_Setup_Console_Master_Prompt.md
    2) Complete Validation of Setup Console Actions 1–9 + Enterprise Time-Based Data Cleanup.md
    3) Enterprise Setup Console — Complete Options 1–9 + MailDev Validation, Repair & Productionization Prompt.md
    4) UAIC Claim & RPA Orchestrator — Corrected and Ordered Requirements.md

**Note:**

1. Most of the requirements are already implemented. **Test and verify the existing functionality before making any changes.**
2. Always focus on **upgrading, enhancing, and fixing** the existing implementation. **Do not delete or remove any existing functionality** if it is already working. If any existing functionality is not working correctly, **fix it and make it fully functional** rather than removing or replacing it unnecessarily.
