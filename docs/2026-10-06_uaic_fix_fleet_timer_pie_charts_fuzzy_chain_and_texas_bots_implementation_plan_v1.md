# Implementation Plan: Fleet Timers, Lifecycle Pie Chart, RapidFuzz Chain & Texas 5-Bot Accuracy

**Implementation ID:** `IMP-2026-1006-001`  
**Project:** UAIC Claim & RPA Orchestrator  
**Modules:**  
- Fleet Automation Telemetry (`/` & `/monitor`)
- Lifecycle Distribution & Visual Pie Chart (`frontend/src/app/page.tsx`)
- RapidFuzz Evaluation & Guidewire Automation Chain (`backend/app/tasks/`)
- County Court Scraper Portals Settings (`travis_enabled`, `dallas_enabled`)
- Portal Telemetry Disambiguation & `hh:mm:ss` Duration Formatting  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Created:** 2026-10-06  
**AI Agent:** Antigravity  

---

## 1. Deep Problem Diagnosis & Root Causes

### Problem 1: Identical Execution Times in Active Fleet (`19884s` across workers)
* **Root Cause**:
  * In `backend/app/api/v1/endpoints/queue.py`, `_format_live_queue_item()` sets `created_at` and `updated_at` from the database.
  * In `frontend/src/app/page.tsx`, `getItemElapsedSeconds()` calculates:
    ```typescript
    const startStr = item.updated_at || item.created_at;
    const startTime = new Date(startStr).getTime();
    return Math.floor((nowTimestamp - startTime) / 1000);
    ```
  * When claims are imported in bulk or set to `SCRAPING_IN_PROGRESS` together, their `updated_at` is identical (from hours ago), yielding identical stale values like `19884s` (5.52 hours).
  * Furthermore, durations are displayed as raw seconds (`19884s`) rather than formatted as `hh:mm:ss`.

### Problem 2: Missing "Failed" in Lifecycle Distribution & Need for Pie Chart
* **Root Cause**:
  * The Lifecycle Distribution card in `frontend/src/app/page.tsx` only included:
    * Completed / Clean (`finishedCount`)
    * In Progress / Queue (`stats.in_progress + stats.new`)
    * Exceptions (`stats.manual_review`)
    * Matches Found (`stats.match_found`)
  * `stats.failed` (e.g. ~131 records, 25% of total) was completely omitted from the segmented bar and legend.
  * The segmented bar lacked an interactive, elegant Pie/Donut visualization for visual scanning.

### Problem 3: RapidFuzz & Guidewire Execution Not Done for Claim `870f33f1`
* **Root Cause**:
  * In `ClaimRecord`, Claim `870f33f1-d4e5-49b5-9afd-13521bcf60f9` has `record_status = "SCRAPING_COMPLETED"`, 1,000 extracted cases, but `fuzzy_match_status = "NEW"`.
  * In `backend/app/tasks/scraper_tasks.py`, when scraping finishes, it dispatches:
    `celery_app.send_task("app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task", args=[claim.id], queue="matcher")`.
  * If Celery worker is offline, bypassed, or not listening to the `matcher` queue during local execution, the task is never executed.
  * In addition, there was no auto-recovery in `queue_runner.py` or `/claims/{id}/start` to automatically trigger fuzzy matching when a claim has scraped cases but remains in `fuzzy_match_status == "NEW"`.

### Problem 4: Texas Claim Ran Only 3 Bots Instead of 5 Bots
* **Root Cause**:
  * In database settings (`settings.portals`):
    * `travis_enabled = False`
    * `dallas_enabled = False`
    * `harris_jp_enabled = True`
    * `harris_cclerk_enabled = True`
    * `harris_district_enabled = True`
  * Because `travis_enabled` and `dallas_enabled` were disabled in settings, `scrapers_to_run` for Texas claims only contained the 3 Harris bots.

### Problem 5: Harris County Bots Cross-Contamination (603 Cases and 225.58s Shared Across 3 Bots)
* **Root Cause 1 (Backend)**:
  * In `backend/app/api/v1/endpoints/claims.py`, `_case_count()` fell back to searching `scraped_by_county` by keyword:
    ```python
    cases_found=_case_count(claim.te_jsonbody_harris, ["harris"]),
    cases_found=_case_count(claim.te_jsonbody_cclerk, ["harris"]),
    cases_found=_case_count(claim.te_jsonbody_hcdistrict, ["harris"]),
    ```
  * Because all three passed `["harris"]`, Harris District Clerk's 603 cases matched for all three portals when `te_jsonbody_harris` or `te_jsonbody_cclerk` was empty or zero!
* **Root Cause 2 (Frontend)**:
  * In `frontend/src/app/claims/[id]/page.tsx`, the portal duration was resolved by:
    ```typescript
    const botWord = botName.toLowerCase().split(" ")[0]; // "harris" for all 3!
    const portalKey = Object.keys(claim.action_timings?.portals || {}).find(
      (k) => (claim.action_timings?.portals?.[k]?.portal_name || k || "").toLowerCase().includes(botWord)
    );
    ```
  * Because `botWord` was `"harris"` for all three portals, `find()` returned the exact same portal timing (`duration: 225.58s`) for all three cards!

---

## 2. Proposed Changes & Technical Architecture

### A. Format Durations in `hh:mm:ss` Everywhere & Accurate Fleet Ticking
1. **Utility Function (`formatDurationHms`)**:
   - Create a reusable utility in `frontend/src/lib/utils.ts` and backend:
     - `0` -> `"00:00:00"`
     - `65s` -> `"00:01:05"`
     - `225.58s` -> `"00:03:45"`
     - `19884s` -> `"05:31:24"`
2. **True Fleet Running Timestamps**:
   - In `backend/app/tasks/scraper_tasks.py`: record exact UTC `started_at` in `action_timings["started_at"]` when a worker actually begins executing a claim.
   - In `backend/app/api/v1/endpoints/queue.py`: expose `started_at` in `LiveQueueItemResponse`.
   - In `frontend/src/app/page.tsx`: use `item.started_at` (or `action_timings.started_at`) for active running workers; for completed workers, use `item.total_duration_seconds`. If a claim has been marked `SCRAPING_IN_PROGRESS` for > 30 minutes without heartbeat, treat as orphaned/stale and display real status rather than an ever-inflating fake counter.
   - Format all durations on the fleet cards, table columns, portal badges, and dossier in `hh:mm:ss`.

### B. Lifecycle Distribution: Add Failed Items & Interactive Pie Chart
1. **Include Failed Claims**:
   - Add `stats.failed` with distinct rose/crimson color (`#f43f5e`).
   - Update percentages so Completed (clean + matches), In Progress/Queue, Exceptions, and Failed sum to 100%.
2. **Interactive SVG Pie / Donut Chart**:
   - Build a clean, responsive SVG Donut Chart component in `frontend/src/app/page.tsx` (using modern SVG arcs or Chart tokens without external heavy bundle dependencies).
   - Display:
     - Center text: Total Records (e.g. `539`) with sub-label "Total Claims".
     - Segments:
       - 🟢 Completed / Clean (`#10b981`)
       - 🔵 Matches Found (`#6366f1`)
       - 🟡 In Progress / Queue (`#f59e0b`)
       - 🟣 Exceptions / Manual Review (`#a855f7`)
       - 🔴 Failed (`#ef4444`)
     - Hover tooltips and click-to-filter support to filter the dashboard table to that exact status.

### C. RapidFuzz & Guidewire Automation Chain Execution
1. **Immediate Execution Fallback**:
   - In `scraper_tasks.py`, after scraping finishes:
     - Dispatch `evaluate_fuzzy_matches_task`.
     - In case Celery worker or `matcher` queue is congested or disabled, provide an async direct invocation fallback so claims never get stranded in `SCRAPING_COMPLETED` with `fuzzy_match_status == "NEW"`.
2. **Auto-Recovery in Queue Runner**:
   - In `queue_runner.py` / `advance_auto_queue_task`, add an auto-catch: find any claims with `record_status == "SCRAPING_COMPLETED"` and `fuzzy_match_status == "NEW"` and immediately execute `evaluate_fuzzy_matches_task`.
3. **Run on Claim `870f33f1`**:
   - Execute fuzzy matching on claim `870f33f1-d4e5-49b5-9afd-13521bcf60f9`, evaluate all 1,000 cases, update match status, and dispatch Guidewire activity if matched.

### D. Enable All 8 Portals (Texas 5 Bots) by Default in Settings
1. Update database settings so `travis_enabled = True` and `dallas_enabled = True`.
2. Ensure defaults in `backend/app/services/settings_service.py` have all 8 portals enabled (`True`).
3. Re-run or verify that Texas claims route to all 5 bots: Travis, Dallas, Harris JP, Harris County Clerk, and Harris District Clerk.

### E. Fix Harris Portal Cross-Contamination & Timing Mapping
1. **Backend Disambiguation (`backend/app/api/v1/endpoints/claims.py`)**:
   - In `_build_bot_details`:
     - Distinguish Harris County JP: keywords `["harris jp", "harris county jp", "odyssey jp"]`.
     - Distinguish Harris County Clerk: keywords `["harris county clerk", "harris clerk", "cclerk"]`.
     - Distinguish Harris District Clerk: keywords `["harris district", "hcdistrict", "e-docs"]`.
   - Prevent generic `"harris"` fallback from attributing Harris District's cases to JP and Clerk.
2. **Frontend Portal Key Mapping (`frontend/src/app/claims/[id]/page.tsx`)**:
   - Replace brittle `botName.split(" ")[0]` with exact mapping:
     ```typescript
     const portalKeyMap: Record<string, string> = {
       "Broward County (FL)": "broward",
       "Hillsborough County (FL)": "hillsborough",
       "Miami-Dade County (FL)": "miami",
       "Travis County (TX)": "travis",
       "Dallas County (TX)": "dallas",
       "Harris County JP (TX)": "harris_jp",
       "Harris County Clerk (TX)": "harris_cclerk",
       "Harris District Clerk (TX)": "harris_district",
     };
     ```
   - Each card queries its exact `claim.action_timings.portals[portalKeyMap[bot.name]]`, ensuring Harris JP, Harris Clerk, and Harris District show their own true case count and true duration.

---

## 3. Verification Plan

1. **Unit & Integration Tests**:
   - Add automated test module `backend/tests/test_portal_disambiguation_and_timings.py` testing:
     - Disambiguated case counts for Harris JP, Harris County Clerk, and Harris District Clerk.
     - `travis_enabled` and `dallas_enabled` default behavior for Texas claims.
     - `format_duration_hms` helper.
     - Auto-trigger of fuzzy matching from `SCRAPING_COMPLETED`.
   - Run `pytest backend/tests/test_portal_disambiguation_and_timings.py`.
2. **Linters & Type Checkers**:
   - Run `ruff check app tests ..\e2e\backend` (0 errors).
   - Run `npx tsc --noEmit` in `frontend` (0 errors).
   - Run `scripts/check_ps1_syntax.ps1` (0 errors).
3. **Live Browser Verification**:
   - Inspect `http://localhost:3000/`:
     - Active fleet cards show distinct, realistic execution times in `hh:mm:ss`.
     - Lifecycle Distribution shows all 5 categories (including Failed) with interactive Pie/Donut Chart.
   - Inspect `http://localhost:3000/claims/870f33f1-d4e5-49b5-9afd-13521bcf60f9`:
     - RapidFuzz evaluation completed and Guidewire status updated.
   - Inspect `http://localhost:3000/claims/28eab91e-8491-4923-8709-397ed895feb9`:
     - Harris JP, Harris Clerk, and Harris District show distinct case counts and durations in `hh:mm:ss`.
     - Texas bots show full 5 targeted bots.
   - Capture video/screenshots to `docs/`.
