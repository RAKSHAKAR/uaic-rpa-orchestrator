# Implementation Plan: Settings Database Save Resiliency & Scraper DB Lock Decoupling

**Document ID:** `IMP-2026-1005-001`  
**Date:** 2026-10-05  
**Version:** v1  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Problem Diagnosis & Root Cause Analysis

### User Symptom
When navigating to `http://localhost:3000/settings` and clicking **Save Configuration** (e.g. on the *Task Queue & Telemetry* tab), a red alert appeared:
```
Settings database save failed
```

### Root Cause
1. **Long-Running DB Session in Scraper Tasks:**
   In [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py), `_async_orchestrate_scrapers` opened a SQLAlchemy `TaskAsyncSessionLocal()` context at line 217 and kept it open across the **entire multi-tab Playwright browser automation run** (averaging ~218 seconds per claim).
   This violated a critical rule in [`AGENTS.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/AGENTS.md) Section 8:
   `"- ❌ Do not hold DB transactions open during browser automation"`
2. **SQLite Write Lock Contention:**
   With 10 Celery worker threads running concurrent browser discovery tasks, SQLite on Windows experienced persistent transaction lock contention. When Uvicorn attempted an atomic `session.commit()` on the `AutomationSetting` row inside `save_system_settings_async()`, SQLite waited up to its 60-second `busy_timeout` before failing with `sqlite3.OperationalError: database is locked`.
3. **Missing Retry Loop in Settings Service:**
   Previously, `save_system_settings_async()` caught `Exception`, immediately logged `"Durable settings save failed"`, and raised `SettingsUnavailableError("Settings database save failed")`, returning HTTP 503 to the frontend without any retry backoff.
4. **Frontend Lack of Transient Recovery:**
   Previously, the settings page only caught HTTP 409 (Conflict), while HTTP 503 immediately surfaced as an error alert to the operator.

---

## 2. Solution Architecture & Changes

### 2.1 Backend: Decouple DB Sessions from Browser Automation
Refactor `_async_orchestrate_scrapers` in [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py) into 3 isolated phases:
1. **Phase 1 (DB Read & Mark In-Progress):**
   - Open short-lived session, fetch claim, validate status, set `record_status = SCRAPING_IN_PROGRESS`, extract unique names, log audit event, and commit.
   - **Immediately close the session.** DB session duration: < 10ms.
2. **Phase 2 (Browser Automation):**
   - Acquire browser concurrency slot.
   - Run `SingleSessionBrowserRunner` across active county portals for all party targets.
   - **Zero active DB transactions held.**
   - If an error screenshot or audit event must be persisted during this phase, use dedicated short-lived helper sessions (< 5ms).
3. **Phase 3 (DB Write & Finalize):**
   - Open short-lived session, re-fetch claim, persist `ScrapedCourtCase` rows, update portal statuses and timings, log `SCRAPING_COMPLETED` or `SCRAPING_FAILED`, commit, and close. DB session duration: < 15ms.

### 2.2 Backend: Concurrency Retry Loop in Settings Service
In [`backend/app/services/settings_service.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/settings_service.py):
- Implement a 5-attempt retry loop with exponential backoff (`0.2s * 2^attempt`) specifically targeting SQLite lock/busy contention.
- Log detailed exception info so underlying database errors are transparent.

### 2.3 Frontend: Transient Lock & Revision Auto-Recovery
In [`frontend/src/app/settings/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx):
- Auto-recover on both HTTP 409 and HTTP 503 by re-fetching the authoritative settings document from `/settings` to obtain the latest revision, pausing 600ms, and re-attempting save transparently before reporting any failure.

---

## 3. Verification Plan
1. Run backend unit & contract tests (`test_settings_durable_contract.py`, `test_settings_alignment.py`).
2. Run backend linter (`ruff check`).
3. Run frontend TypeScript compiler (`npx tsc --noEmit`).
4. Restart background Uvicorn and Celery worker processes.
5. Verify live settings roundtrip save via API endpoint test.
6. Verify live settings save via frontend web browser.
