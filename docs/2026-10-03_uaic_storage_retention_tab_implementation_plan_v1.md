# Implementation Plan: Storage & Retention Tab Functionality Verification & Hardening

**Implementation ID:** `IMP-2026-1003-005`  
**Date:** October 3, 2026  
**Document Type:** Implementation Plan (`v1`) — ✅ Verified October 4, 2026  
**Status:** ✅ Complete — AI Verification: Complete (100% Automated Testing Suite)  
**Component:** Frontend (`/settings` Storage & Retention Tab) + Backend (`StorageService`, `CleanupService`, Settings Endpoints)

---

## 1. Executive Summary & Objective

The user requested that the **"Storage & Retention"** tab functionality in the UAIC Orchestrator Settings (`http://localhost:3000/settings`) be fully working, verified, and tested across all operational layers:
1. **Multi-Provider Storage Configuration:** Error screenshot capture toggle, destination provider selection (`local`, `s3`, `azure_blob`, `gcs`), bucket/credentials inputs, and password reveal controls.
2. **Interactive Live Storage Verification Sandbox:** Testing read/write/bucket reachability via `POST /api/v1/settings/test-storage`.
3. **Data Retention & Automated Purge Policy:** Setting artifact retention windows (1–365 days), auto-cleanup toggles, and on-demand purge via `POST /api/v1/settings/storage/cleanup`.
4. **Enterprise Storage Cleanup & Impact Preview:** Category selection (`ERROR_SCREENSHOTS`, `SCRAPER_PAGE_CACHE`, `EXPORT_GENERATIONS`), time scope (`OLDER_THAN_30_DAYS`, `OLDER_THAN_14_DAYS`, etc.), preview impact via `POST /api/v1/cleanup/preview`, and safe execution via `POST /api/v1/cleanup/execute`.

---

## 2. Root Cause & Gap Analysis

Comprehensive inspection of the backend schemas, services, and frontend JSX revealed four concrete gaps:

### Gap 1: Storage Purge Contract Discrepancy (`StorageCleanupResponse`)
- **Backend Schema:** `StorageCleanupResponse` in `backend/app/schemas/settings.py` defines `files_purged`, `bytes_freed`, `retention_days`, `message`. It lacks `files_deleted` and `storage_provider`.
- **Frontend Expectation:** In `frontend/src/types/index.ts` and `frontend/src/app/settings/page.tsx` line 473 & line 7278, the UI expects `res.files_deleted` and `res.storage_provider`.
- **Symptom:** After running "Purge Expired Storage Now", the toast displays `Storage purge completed: undefined files removed (0.00 MB freed) across undefined storage.` and the card text displays `files / 0.00 MB freed`.

### Gap 2: Cleanup Preview Stats UI Field Mismatches
- **Backend Schema:** `CleanupPreviewResponse` in `backend/app/schemas/cleanup.py` returns `time_scope`, `categories`, `record_counts`, `file_counts`, `total_database_records`, `total_files`, `can_proceed`.
- **Frontend JSX:** In `frontend/src/app/settings/page.tsx` lines 7345–7366, the UI expects `cleanupPreview.scope`, `cleanupPreview.total_records_to_delete`, `cleanupPreview.total_files_to_delete`, and `cleanupPreview.db_records_to_delete`.
- **Symptom:** When clicking "Preview Cleanup Impact", the calculated stat blocks render blank or `0` for records, files, and time scope header displays `undefined`.

### Gap 3: Category Key Aliases in `expand_categories()`
- **Frontend Categories:** The checkboxes in the UI send `["ERROR_SCREENSHOTS", "SCRAPER_PAGE_CACHE", "EXPORT_GENERATIONS"]`.
- **Backend Categories:** `backend/app/services/cleanup_service.py` defines `bot_history`, `scraper_logs`, `generated_exports`. It only mapped `error_screenshots` -> `bot_history`, but ignored `scraper_page_cache` and `export_generations`.
- **Symptom:** In cleanup preview, unmapped categories are silently omitted, and if none match, it defaulted to `["claims"]` (a safety hazard).

### Gap 4: Defensive Fallbacks & Status Display in Storage Sandbox
- Ensure `handlePurgeExpiredStorage` and `handleCalculateCleanupPreview` have robust defensive normalization (`res.files_deleted ?? res.files_purged ?? 0`, `res.storage_provider || "local"`), and the storage test sandbox displays high-contrast dark/light theme badges with exact millisecond timings and directory/bucket details.

---

## 3. Scope of Implementation

### Backend Changes:
1. **`backend/app/schemas/settings.py`**:
   - Update `StorageCleanupResponse` to include `files_deleted: int = 0`, `files_purged: int = 0`, and `storage_provider: str = "local"`.
2. **`backend/app/services/storage_service.py`**:
   - In `cleanup_expired_storage()`, populate `files_deleted=purged_count`, `files_purged=purged_count`, and `storage_provider=provider`.
3. **`backend/app/schemas/cleanup.py`**:
   - In `CleanupPreviewResponse`, add compatibility fields/aliases: `scope: str | None = None`, `total_records_to_delete: int = 0`, `total_files_to_delete: int = 0`, `db_records_to_delete: int = 0`.
4. **`backend/app/services/cleanup_service.py`**:
   - In `expand_categories()`, add complete alias mappings:
     - `error_screenshots`, `screenshots` -> `bot_history`
     - `scraper_page_cache`, `scraper_cache`, `scraper_logs` -> `scraper_logs`
     - `export_generations`, `generated_exports`, `exports` -> `generated_exports`
   - In `calculate_cleanup_preview()`, populate the compatibility fields (`total_records_to_delete`, `total_files_to_delete`, `db_records_to_delete`, `scope`).

### Frontend Changes:
1. **`frontend/src/app/settings/page.tsx`**:
   - Fix `cleanupPreview` field bindings: `cleanupPreview.time_scope || cleanupPreview.scope`, `cleanupPreview.total_database_records`, `cleanupPreview.total_files`.
   - Fix `storagePurgeResult` text formatting: `(storagePurgeResult.files_deleted ?? storagePurgeResult.files_purged ?? 0)` and `storagePurgeResult.storage_provider || "local"`.
   - Ensure the category checkboxes and scope dropdown update state reactively and trigger preview recalculation smoothly.
2. **`frontend/src/types/index.ts`**:
   - Ensure `StorageCleanupResponse` and `CleanupPreviewResponse` TypeScript interfaces reflect the dual-compatible schema.

---

## 4. Verification & Testing Strategy

### Step 1: Automated Integration Test Script (`scripts/verify_storage_retention_tab.py`)
Run automated python verification script testing:
1. `GET /api/v1/settings` (retrieves `storage` settings).
2. `POST /api/v1/settings/test-storage` for `local` provider (verifies 200 OK, `success: True`, directory check, latency).
3. `POST /api/v1/settings` (updates `storage.retention_days = 45`, `auto_cleanup_enabled = True`).
4. `POST /api/v1/settings/storage/cleanup` (asserts `files_deleted`, `files_purged`, `storage_provider`, `bytes_freed`).
5. `GET /api/v1/cleanup/categories` (asserts categories metadata).
6. `POST /api/v1/cleanup/preview` with `ERROR_SCREENSHOTS`, `SCRAPER_PAGE_CACHE`, `EXPORT_GENERATIONS` across `OLDER_THAN_30_DAYS` (asserts stats populated, not 0/undefined).
7. `POST /api/v1/cleanup/execute` with `dry_run=True` (asserts simulation passes safely).

### Step 2: Playwright Headless/GUI Browser Verification
Run a Playwright browser script navigating to `http://localhost:3000/settings`:
1. Click **"Storage & Retention"** tab.
2. Verify Master Capture Toggle switch works.
3. Switch storage providers between Local, S3, Azure, GCS and verify dynamic field visibility.
4. Click **"Test Storage Connection"** -> verify live success toast and result banner.
5. Click **"Preview Cleanup Impact"** -> verify 4 stat cards render non-zero or valid numbers without `undefined`.
6. Click **"Purge Expired Storage Now"** -> verify toast and purge summary badge render correctly.
7. Click **"Execute Cleanup Now"** -> open confirm modal, verify scope description, cancel modal.
8. Capture visual screenshot saved to `docs/storage_retention_verified.png`.

### Step 3: Lint & Build Health Checks
- `pytest` on existing cleanup tests (`tests/test_enterprise_cleanup.py`).
- `ruff check app tests` (0 errors).
- `tsc --noEmit` in frontend (0 errors).
- `powershell check_ps1_syntax.ps1` (0 errors).

---

## 5. Risk Assessment & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Accidental deletion of live claim records | High | Safety lock: `cleanup_service.py` requires explicit `confirmed=True` and defaults to `dry_run=True` in simulations. Claims table is never purged during storage artifact cleanup. |
| Schema breaking changes | Medium | Dual-attribute backward compatibility: support both `files_purged` and `files_deleted` in response schemas. |
| Cloud provider test timeouts | Low | Fast socket timeouts (2.0s) and fallback to local disk. |

---

## 6. Definition of Done
- All 4 gaps resolved and tested across backend and frontend.
- Automated verification script passes 100%.
- Playwright E2E browser verification passes with visual evidence saved in `docs/`.
- Ruff, TypeScript, Pytest, and PowerShell syntax checks pass with 0 errors.
- Verified record saved to `docs/`.
