# UAIC Orchestrator Full Parity, Scraper Navigation & UI/UX Remediation Plan

**Implementation ID:** `IMP-2026-0916-002`  
**Date:** 2026-09-16  
**Status:** Approved - In Execution  
**AI Verification:** In Progress (100% Automated Testing Suite)  
**Lifecycle Phase:** Execute & Verify  

---

## 1. Executive Summary & Root-Cause Analysis

This implementation addresses all user-reported issues across all 7 frontend pages, 8 portal scrapers, backend APIs, settings, and workflows:

### A. Audit Page (`/audit`)
1. **Sorting**: Column sorting headers with active sort indicators (`asc`/`desc`).
2. **StatCard Filter Click**: Mismatch between UI queries (`MATCH_PAIR`, `SYSTEM`) and database enum/string values (`MATCH`, `SETTINGS`, `SYSTEM`). Normalize query parameters so clicking cards filters the audit table accurately.
3. **Export**: Universal `ExportActionToolbar` (Excel, CSV, JSON, PDF) and background export modal.
4. **Pagination**: Max records option up to 500.

### B. Dashboard (`/`)
1. **Live Data Connection**: Connect all cards (queue, throughput, bot breakdown) directly to live API endpoints (`/claims/stats`, `/queue/status`).
2. **Universal Export & Pagination**: Embed `ExportActionToolbar`, support up to 500 rows.

### C. Queue Monitor (`/monitor`)
1. **StatCard Design Harmony**: Synchronize card layout and visual styling with the main Dashboard cards.
2. **Universal Export**: Embed `ExportActionToolbar` with instant JSON, Excel, and CSV download, plus `AsyncExportModal`.
3. **Default Auto-Queue**: Ensure Auto-Queue defaults to `true` (Enabled).

### D. Claim Detail (`/claims/:id`)
1. **"View Stages" Telemetry Modal**: Fix the missing modal JSX for `inspectedStage` to show all bot execution stages, durations, and download links for captured screenshots.
2. **Storage Cleanup Policy**: Add local and remote screenshot/log cleanup configuration inside Settings under Storage & Error Screenshots tab.
3. **Export Rectification**:
   - Comprehensive single-sheet CSV export containing full claim metadata headers + court case docket fields in a lossless tabular representation.
   - Multi-tab Excel export matching the full JSON data structure.
   - Remove bottom redundant PDF button from Scraped Cases section.
4. **Scraped Cases Table**:
   - Fix Filing Date parsing and display (`FilingDate` / `SuitFiledDate` / `Filled`).
   - Remove `sort:descending` button and implement sortable column headers.
   - All filter dropdowns support multi-select.
5. **Timeline Responsiveness**: Fix visual overlap in Concurrent Multi-Portal Scraping Timeline.
6. **Audit Logs for Scraped Cases**: Ensure `AuditLog` entries are generated upon portal start, completion, and docket extraction so the Claim Audit Trail is populated.

### E. System Health (`/health`)
1. **Auto Refresh**: Default Auto Refresh to ON (15s interval) with a clear visual status badge.

### F. Exceptions Review (`/exceptions`)
1. **Universal Export**: Embed `ExportActionToolbar` with JSON, Excel, CSV, PDF, and `AsyncExportModal`.
2. **Multi-Select Filters**: Multi-select dropdown filtering on match status and confidence bands.
3. **Pagination**: Max records up to 500.

### G. Settings (`/settings`)
1. **Default Settings Calibration**:
   - `captcha_wait_seconds`: 120
   - `max_captcha_attempts`: 2
   - `page_timeout_seconds`: 60
   - `reload_backoff_seconds`: 2 (clarified as delay before reloading on transient network/bot challenge failures)
   - `max_concurrent_claims`: 10 (10x concurrency)
2. **Email & Notification Tab**:
   - Collapse CC/BCC into an optional clean accordion to eliminate empty state confusion.
   - Remove redundant "Render Preview" button.
   - Gate "Live Synchronized Render Preview" behind the "Live Preview" button toggle.
   - Ensure outbound notification delivery history records and renders.
3. **Fuzzy Match & Unique Name APIs**:
   - `POST /api/v1/matches/unique-names`: Extract unique non-empty party names.
   - `POST /fuzzymatchapi` and `POST /api/v1/matches/fuzzymatchapi`: Legacy Power Automate RapidFuzz `partial_ratio` API.
   - Provide interactive testing consoles with real positive/negative match test scenarios.

### H. Form & Ingestion Simplification
- Remove `"Loss Location City"`, `"Loss Location County"`, `"Garaging City"`, and `"Garaging State"` from New Claim Form, Edit Claim Form, and Excel/CSV ingestion mapping.

### I. Scraper Human Navigation Flows (All 8 Portals)
- Update default portal URLs and navigation flow to start from root portal homepages and interactively click through navigation menus before reaching search forms to evade bot detection.
- Hierarchical screenshot and log storage under `backend/screenshots/{claim_id}/{portal}/` and `backend/logs/{claim_id}/{portal}/`.

---

## 2. Implementation Steps

1. **Frontend Global Reusable Component:**
   - Create `ExportActionToolbar.tsx`.
2. **Page Updates:**
   - Update `/audit/page.tsx`, `/page.tsx`, `/monitor/page.tsx`, `/claims/[id]/page.tsx`, `/health/page.tsx`, `/exceptions/page.tsx`, `/settings/page.tsx`, `/upload/page.tsx`.
3. **Backend Endpoints & Scrapers:**
   - Update `claims.py` (comprehensive CSV/Excel, remove deprecated fields).
   - Update `audit.py` (filter normalization, PDF export).
   - Update `matches.py` (`/matches/unique-names`, `/fuzzymatchapi`).
   - Update `scraper_tasks.py` (audit logs, screenshots/logs hierarchy).
   - Update `backend/app/automation/` portal scrapers for homepage navigation.
4. **Automated Testing Suite:**
   - Add new tests in `backend/tests/`: `test_unique_names_and_legacy_fuzzy_api.py`, `test_single_claim_comprehensive_export.py`, `test_scraper_human_navigation.py`.
   - Run full regression suite (`pytest`, `ruff`, `tsc`, `ps1`).
5. **Documentation & Validation Walkthrough:**
   - Update `README.md` and generate `walkthrough.md`.
