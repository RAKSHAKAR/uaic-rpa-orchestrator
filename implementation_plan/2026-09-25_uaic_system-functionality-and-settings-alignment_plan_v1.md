# Implementation Plan: System Functionality & Settings Alignment

**Implementation ID:** `IMP-2026-0925-003`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** System Settings, County Court Scrapers, Session Runner & Dynamic UI Alignment  
**Date:** 2026-09-25  
**Author:** Antigravity AI Engineering Assistant  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Human Verification:** Pending Human Verification  

---

## 1. Problem Statement & User Request

The user requested:
1. Continue and finish all items from the interrupted execution.
2. Check every functionality in the current system to ensure 100% alignment with the Settings page (`/settings`).
3. Conduct a comprehensive Gap Analysis of missing, broken, or misaligned functionality, UI, or UX across all application routes and RPA scraping workflows.

---

## 2. Proposed Architecture & Scope of Changes

### 2.1 Dynamic Extension Configuration Injection (`session_runner.py`)
- **Diagnosis:** `SingleSessionBrowserRunner` previously used a static JavaScript template in `setup_page.evaluate()` to configure AntiCaptcha, ignoring user-configured toggles (auto-submit, sound, solve-specific widget types, reCAPTCHA v3 score) set in the Settings UI.
- **Solution:** Construct a dynamic configuration payload in Python from `self.anticaptcha_settings` and pass it directly to `setup_page.evaluate((config) => { ... })`.

### 2.2 Celery Worker Fleet Lifecycle Management
- **Diagnosis:** Stale Python bytecode in long-lived Celery worker processes prevented newly defined symbols and settings from taking effect.
- **Solution:** Terminate stale worker processes and launch fresh workers with concurrency 10 across all 5 queues (`ingest`, `scrapers`, `matcher`, `notifications`, `default`).

### 2.3 Settings Propagation Verification
- **Diagnosis:** Ensure runtime modifications via `POST /api/v1/settings` are immediately reflected across Redis and SQLite and received by `get_system_settings_async()` without service restarts.
- **Solution:** Develop automated verification script `test_settings_propagation.py`.

### 2.4 End-to-End System Audit & Gap Analysis
- Document alignment across all 9 Settings tabs, 8 county portal scrapers, fuzzy deduplication cascade, Guidewire integration, and frontend pages.

---

## 3. Implementation Steps

1. **Step 1:** Modify `backend/app/automation/session_runner.py` to dynamically construct and inject the full AntiCaptcha configuration.
2. **Step 2:** Execute pytest on `tests/test_settings_workflow_parity.py` and run full backend tests.
3. **Step 3:** Run `ruff check app tests` to guarantee zero Python lint errors.
4. **Step 4:** Run `npx tsc --noEmit` to verify frontend TypeScript integrity.
5. **Step 5:** Run `powershell -File scripts/check_ps1_syntax.ps1` to ensure all setup and maintenance scripts are valid.
6. **Step 6:** Launch fresh Celery worker fleet and beat daemon.
7. **Step 7:** Execute `test_settings_propagation.py` to confirm dynamic settings updates.
8. **Step 8:** Compile the comprehensive Gap Analysis document into `implementation_plan/`.

---

## 4. Verification & Validation Criteria

- **Pytest:** 100% pass rate.
- **Ruff:** 0 errors.
- **TypeScript:** 0 errors.
- **PowerShell:** 0 errors across 10 scripts.
- **Settings Propagation:** Verified via automated script.
- **Live Queue:** All 10 Florida claims visible in FIFO order in the dashboard queue.
