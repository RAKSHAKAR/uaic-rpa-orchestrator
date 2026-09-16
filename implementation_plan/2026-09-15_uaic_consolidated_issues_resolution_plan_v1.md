# IMP-2026-0915-002: Consolidated Issues & Validation Requirements — Full Resolution Plan

**Implementation ID:** IMP-2026-0915-002  
**Date:** 2026-09-15  
**Status:** PLAN — Awaiting User Approval  
**Reference Documents:**
- `ManualPrompt.txt`
- `UAIC Claim & RPA Orchestrator — Consolidated Issues and Validation Requirements.md` (26 sections)

---

## Background

This plan resolves all identified gaps from the Consolidated Issues document and ManualPrompt.txt through a complete line-by-line audit of the codebase. Each item below has been verified against the actual source code with exact file and line references.

---

## Current State Summary

### ✅ Already Implemented (18 Items — No Action Required)

| Item | Status | Evidence |
|------|--------|----------|
| Audit page: Excel/CSV/JSON export buttons | ✅ Done | `audit/page.tsx` lines 344–369 |
| Audit page: Multi-select filters (Action, Entity, Status) | ✅ Done | Uses `MultiSelectDropdown` component |
| Audit page: Column sorting with sort indicators | ✅ Done | `handleSort()`, `renderSortIndicator()` |
| Audit page: Clickable stat cards → filter table | ✅ Done | `onClick` on each `StatCard` |
| Exceptions page: Export (Excel/CSV/JSON) via AsyncExportModal | ✅ Done | `exceptions/page.tsx` line 8 |
| Exceptions page: Multi-select filters | ✅ Done | County, Party Type, Score Tier |
| Exceptions page: Sorting | ✅ Done | `sortField`/`sortOrder` state |
| Monitor page: Auto Queue default `true` | ✅ Done | `useState(true)` on line 62 |
| Monitor page: `StatCard` component used | ✅ Done | Import confirmed |
| Settings: CAPTCHA wait = 120s | ✅ Done | `settings_service.py` line 35 |
| Settings: Max retry = 2 | ✅ Done | `settings_service.py` line 34 |
| Settings: Portal timeout = 60s | ✅ Done | `settings_service.py` line 36 |
| Settings: All 8 portal URLs updated | ✅ Done | `settings_service.py` lines 49–67 |
| Health page: Auto-refresh active by default (interval=15s) | ✅ Done | `useState(15)` — non-zero drives setInterval |
| Claim detail: `handleOpenBotStages` implemented | ✅ Done | Lines 314–366, sets `inspectedStage` |
| Claim detail: `inspectedStage` telemetry modal renders | ✅ Done | Line 3110, Stages/JSON tabs |
| Form fields: `loss_location_city`, `garaging_city` etc. removed | ✅ Done | Not present in any form component |
| Portal home-page default URLs updated | ✅ Done | `settings_service.py` lines 49–67 |

---

## 🔴 Confirmed Gaps — 15 Items Requiring Implementation

### BACKEND GAPS (5)

---

#### BGAP-001 — Missing `/claims/{id}/audit-logs` Endpoint (Root Cause of "No Audit Events")

> [!CAUTION]
> This is the single highest-priority fix. Without it, audit events can never display on Claim Detail.

**Root Cause:** Frontend calls `GET /api/v1/claims/{claimId}/audit-logs` (confirmed at `api.ts` line 524). This route **does not exist** in `claims.py` or `audit.py`. The audit router is mounted at `/audit-logs` (global only).

**Fix — add to `claims.py`:**
```python
@router.get("/{claim_id}/audit-logs", response_model=list[AuditLogResponse])
async def get_claim_audit_logs(claim_id: str, db: AsyncSession = Depends(get_db)):
    """Return all audit log entries for a specific claim (by entity_id)."""
    from app.models.audit_log import AuditLog
    from app.schemas.audit import AuditLogResponse
    stmt = (
        select(AuditLog)
        .where(AuditLog.entity_id == claim_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(200)
    )
    res = await db.execute(stmt)
    items = res.scalars().all()
    return [AuditLogResponse.model_validate(item) for item in items]
```

---

#### BGAP-002 — Missing JSON Quick-Download in Monitor Export Area

**Root Cause:** `AsyncExportModal` on Monitor has Excel and CSV quick-download buttons but no JSON button. Sections 5.2 and ManualPrompt line 23 require JSON export.

**Fix:** Add JSON quick-download button to `AsyncExportModal` component (alongside existing Excel/CSV buttons).

---

#### BGAP-003 — PDF Export Must Be Removed from Bottom Cases Section

**Requirement (Section 12 / ManualPrompt line 48):** PDF is already in the top export options (working). Must be **removed** from the bottom "Export Cases" section under Scraped Public Court Cases.

**Fix:** Remove the PDF export button from the bottom cases export toolbar in `claims/[id]/page.tsx`.

---

#### BGAP-004 — Top Excel & CSV Export Missing Full Court Case Data (Sections 7, 12)

**Root Cause:** Bottom "Export Cases" Excel works well (per user). Top-level single-claim Excel/CSV export (`export_single_claim` in `claims.py`) may not include all scraped court case fields at the same fidelity as JSON.

**Fix:** Audit `export_single_claim` in `claims.py` and align Excel/CSV column output to fully match the JSON payload.

---

#### BGAP-005 — Scraped Cases: Remove Standalone Sort Button, Add Column Sorting (Section 10.2)

**Requirement:** The standalone `Sort: Descending` button is not working correctly. Remove it. Implement ascending/descending sorting directly on table column headers.

**Fix:** Remove the sort direction dropdown/button from the cases section toolbar. Add `onClick` sort handlers to `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` column headers with sort icon indicators.

---

### FRONTEND GAPS (10)

---

#### FGAP-001 — FilingDate Not Displaying in Scraped Cases Table (Section 10.1)

**Root Cause:** The FilingDate field pipeline must be traced end-to-end: scraper → DB → API → frontend render. Cases appear but FilingDate is blank.

**Fix:** Confirm `ScrapedCourtCase.filing_date` is populated in DB, confirmed in API response, and rendered in the cases table. If the frontend uses a different key (e.g., `filing_date` vs `FilingDate`), normalize the mapping.

---

#### FGAP-002 — Scraped Cases: All Filters Must Support Multi-Select (Section 10.3)

**Requirement:** County, Case Status, and Case Type filters on the scraped cases table must all be multi-select.

**Fix:** Replace any single-select dropdowns with `MultiSelectDropdown` component for all three filter dimensions.

---

#### FGAP-003 — Concurrent Scraping Timeline: UI Overlap at Smaller Breakpoints (Section 8)

**Requirement:** The concurrent multi-portal scraping timeline has overlapping UI elements. Must be fully responsive across all breakpoints (desktop → 360px, landscape & portrait).

**Fix:** Apply responsive fixes (`flex-wrap`, `overflow-x-auto`, breakpoint-aware sizing, `min-w-0`) to the timeline component layout.

---

#### FGAP-004 — Bot Status Cards: Design Inconsistent with Dashboard (Section 9)

**Requirement:** The 8 bot stat cards under "County Court Portal Scraper Execution Status" must match the global `StatCard` design system language.

**Fix:** Verify and enforce `StatCard` component usage for the portal bot status summary cards on claim detail.

---

#### FGAP-005 — Pagination Max 500 Records (Section 23 / ManualPrompt line 124)

**Requirement:** All applicable page size selectors must offer up to 500 records. Currently maxed at 100 in UI.

**Fix:** Add `{ value: 500, label: "500" }` to the page size options on Dashboard, Monitor, Audit, Exceptions, and Claim Detail pages.

---

#### FGAP-006 — Settings: CC/BCC Empty State Confusing (Section 17.1)

**Requirement:** "No CC recipients configured / No BCC recipients configured" displays unnecessarily and confuses users.

**Fix:** Remove the empty-state CC/BCC display, or make it a collapsible "Advanced Recipient Options" section that defaults to hidden unless the user toggles it.

---

#### FGAP-007 — Settings: Render Preview Redundancy (Section 17.2)

**Requirement:** If "Render Preview" button is redundant with "Live Preview", remove it.

**Fix:** Inspect what `Render Preview` triggers vs `Live Preview`. If identical, remove the `Render Preview` button entirely.

---

#### FGAP-008 — Settings: Live Render Preview Section Must Be Gated (Section 17.3)

**Requirement:** "Live Synchronized Render Preview" section should only become visible after the user clicks "Live Preview". It should not occupy space by default.

**Fix:** Gate the section with a `showLivePreview` state variable (default: `false`). Set to `true` only when "Live Preview" button is clicked.

---

#### FGAP-009 — Reusable Export Component Coverage (Section 13)

**Requirement:** The `AsyncExportModal` with JSON + Excel + CSV quick-download must be the universal export component on all applicable pages.

**Fix:** Confirm `AsyncExportModal` is present and correctly wired on Audit, Claim Detail, Monitor, and Exceptions. If any page is missing it, add it.

---

#### FGAP-010 — Guidewire Auto-Push: Document & Verify Trigger Condition (Section 14)

**Requirement:** Clearly determine and document when Guidewire push is triggered (automatic vs. manual). Fix root cause if automatic push is not working.

**Finding:** `auto_push_on_match=True` in settings_service.py line 110. `fuzzy_tasks.py` line 460 calls `log_audit_event_async` post-push. The full trigger chain needs tracing and documentation.

**Fix:** Trace `auto_push_on_match` → fuzzy task → `guidewire_client.push()` → audit log. Confirm it fires correctly. Document the exact trigger condition.

---

## Proposed Changes by File

### Backend

#### [MODIFY] [`claims.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/claims.py)
- Add `GET /{claim_id}/audit-logs` endpoint (**BGAP-001**)
- Audit and fix `export_single_claim` Excel/CSV to include all court case fields (**BGAP-004**)

---

### Frontend

#### [MODIFY] [`claims/[id]/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/claims/%5Bid%5D/page.tsx)
- Remove PDF from bottom Export Cases section (**BGAP-003**)
- Fix FilingDate display in scraped cases table (**FGAP-001**)
- Replace standalone sort button with column-header sorting on cases table (**BGAP-005**)
- Add multi-select to all case filters (**FGAP-002**)
- Fix concurrent timeline responsive layout overlap (**FGAP-003**)
- Fix bot status cards to use StatCard design system (**FGAP-004**)
- Add 500 to cases page size options (**FGAP-005**)
- Confirm `AsyncExportModal` is wired on claim detail (**FGAP-009**)

#### [MODIFY] [`monitor/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/monitor/page.tsx)
- Add JSON quick-download button to export area (**BGAP-002**)
- Add 500 to page size options (**FGAP-005**)

#### [MODIFY] [`page.tsx` (Dashboard)](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/page.tsx)
- Add 500 to page size options (**FGAP-005**)

#### [MODIFY] [`audit/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/audit/page.tsx)
- Add 500 to page size options (**FGAP-005**)

#### [MODIFY] [`settings/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)
- Remove/clean CC/BCC empty-state clutter (**FGAP-006**)
- Remove redundant Render Preview button if confirmed duplicate (**FGAP-007**)
- Gate Live Render Preview section behind Live Preview click (**FGAP-008**)

---

## Verification Plan

### Automated Tests
```bash
cd backend
.venv\Scripts\pytest --tb=short -q

.venv\Scripts\ruff check app tests

cd frontend
npx tsc --noEmit

powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```

### Manual Verification Points
1. Claim detail → Audit Events section shows actual events after running automation
2. Claim detail → Bottom export section has **NO** PDF button
3. Claim detail → Scraped Cases table has column-header sort only (no standalone sort button)
4. Claim detail → FilingDate column populated correctly
5. Dashboard / Monitor / Audit / Exceptions → Page size options include **500**
6. Settings → No confusing CC/BCC empty-state messages
7. Settings → Live Preview section hidden until button clicked

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Adding `/claims/{id}/audit-logs` conflicts with existing routes | Low | Route is unique, no conflict |
| Excel/CSV export fix could change existing column order | Low | Add columns; never remove existing ones |
| Removing PDF from bottom export breaks user workflow | Low | PDF remains in top export — Section 12 explicitly requests bottom removal |
| Page size 500 causing slow loads | Medium | Backend audit endpoint already has `le=500`; add backend cap to claims list endpoint |

---

> [!CAUTION]
> **NO IMPLEMENTATION will begin until the user explicitly approves this plan.**
> Per AGENTS.md Rule 8: NO APPROVAL = NO IMPLEMENTATION.

**Implementation ID:** IMP-2026-0914-001  
**Date:** 2026-09-14  
**Status:** PLAN — Awaiting Approval  
**Scope:** Full V4 Parity Audit + Consolidated Issues Resolution + Scraping Engine Validation  

---

## Background

This plan is the result of a deep, comprehensive audit of the UAIC Claim & RPA Orchestrator codebase against:
1. **V4 Power Automate desktop flow reference** (`PowerAutomateSolutions/BotCreation_1_0_0_7/`)
2. **Consolidated Issues and Validation Requirements** (26 sections, all reviewed)
3. **Current codebase state** — all 8 scrapers, orchestration, frontend routes, API endpoints reviewed

---

## Audit Findings — Current State

### ✅ What is Working Correctly

| Area | Status |
|------|--------|
| Ruff lint | ✅ 0 errors |
| TypeScript (`tsc --noEmit`) | ✅ 0 errors |
| Pytest test collection | ✅ 281 tests across 28 suites |
| State routing logic (FL/TX/cross-state) | ✅ Correct in `scraper_tasks.py` |
| Party name cascade (Claimant → Insured → Driver) | ✅ Correct |
| DualSearch / TripleSearch derivation | ✅ Correct |
| DOL 10-year lookback cap enforcement | ✅ Correct (lines 314–323) |
| Claim number 9-digit `"0"` prefix rule | ✅ Correct in `guidewire_client.py` |
| Fuzzy match cascade (RapidFuzz partial_ratio 0.6) | ✅ Correct |
| Portal output schema — Harris JP (no CaseType) | ✅ Correct |
| Portal output schema — Harris Clerk (no CaseType) | ✅ Correct |
| All other portal schemas (CaseType included) | ✅ Correct |
| CAPTCHA detection loop (DOM polling, not blind sleep) | ✅ Correct in `base.py` |
| AntiCaptcha extension loaded via `--load-extension` | ✅ Correct in `browser_manager.py` |
| Security block detection + cooldown system | ✅ Correct |
| Browser test endpoint (`/settings/test-browser`) | ✅ Implemented |
| Extension validation endpoint (`/settings/validate-extension`) | ✅ Implemented |
| Incremental case accumulation + deduplication | ✅ Correct in `scraper_tasks.py` |
| FilingDate alias normalization (multiple key variants) | ✅ Correct |
| Auto-queue advance after portal failures | ✅ Correct |
| Celery task signatures (scraper_tasks, fuzzy_tasks) | ✅ Preserved |
| Biometric-style fill (random delay per key) | ✅ Correct in `base.py` |
| Error screenshot capture (Local/S3/Azure/GCS) | ✅ Implemented |

---

## 🔴 Identified Gaps (16 Total)

### SCRAPING ENGINE GAPS

#### GAP-001 — Broward: No Header Row Filter in Pagination Loop
**File:** [`broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py) (lines 122–147)  
**Issue:** Extracts all `<tbody tr>` rows without skipping header rows. Other scrapers (`harris_district.py` line 117, `harris_cclerk.py` line 101) have this filter; Broward does not.  
**Risk:** Creates garbage records like `{CaseNumber: "Case Number", ...}` in results.  
**Fix:** Add: `if case_num.upper() in ("CASE NUMBER", "CASE NO.", "CASE #", ""): continue`

#### GAP-002 — Miami-Dade: FilingDate Fallback Fabricates Today's Date
**File:** [`miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py) (line 194)  
**Issue:** `"FilingDate": filing_date or datetime.now().strftime("%m/%d/%Y")` — when card-parsing fails to find a FilingDate label, it uses **today's date** as a fabricated value. This is factually wrong.  
**V4 Reference:** V4 uses empty string when not found.  
**Fix:** Change to `"FilingDate": filing_date or ""`

#### GAP-003 — Miami-Dade: Card Parsing Logic Is Fragile
**File:** [`miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py) (lines 165–184)  
**Issue:** The compound condition on line 167 has Python operator precedence issues — `"STATE" not in line_upper and not case_number` binds incorrectly. Also, the "CASE STYLE" detection may match before "CASE STATUS" is parsed, causing values to bleed across fields.  
**Fix:** Refactor to explicit ordered checks using a `label_map` dict approach:
```python
label_map = {
    "LOCAL CASE NUMBER": "case_number",
    "STATE CASE NUMBER": "case_number_alt",
    "CASE STYLE": "case_style",
    "FILING DATE": "filing_date",
    "FILED DATE": "filing_date",
    "CASE STATUS": "case_status",
    "STATUS": "case_status",
    "CASE TYPE": "case_type",
    "TYPE": "case_type",
}
```
Use `case_number_alt` as fallback if `case_number` is empty.

#### GAP-004 — Hillsborough: No Pagination Loop
**File:** [`hillsborough.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/hillsborough.py) (lines 149–192)  
**Issue:** Extracts a single page of results. The DataTables-powered table has built-in pagination (`#partyResultsTable_next`). Results beyond page 1 are silently discarded.  
**V4 Reference:** V4 handles DataTables pagination.  
**Fix:** Add pagination loop after row extraction:
```python
while True:
    next_btn = page.locator("#partyResultsTable_next:not(.disabled) a, li.paginate_button.next:not(.disabled) a")
    if await next_btn.count() == 0 or not await next_btn.first.is_visible():
        break
    await next_btn.first.click()
    await page.wait_for_timeout(2000)
    # extract rows again...
    if page_num > 10: break
    page_num += 1
```

#### GAP-005 — Harris District Clerk: No Pagination Loop
**File:** [`harris_district.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_district.py) (lines 100–125)  
**Issue:** Same problem as GAP-004. The `dgSearchResults` grid on hcdistrictclerk.com is paginated.  
**Fix:** Add ASP.NET GridView pagination: look for `a` with `href` containing `__doPostBack` and label "Next >" or similar.

#### GAP-006 — Harris County Clerk: No Pagination Loop
**File:** [`harris_cclerk.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py) (lines 88–119)  
**Issue:** Same problem. The WebSearch grid paginates via ASP.NET LinkButton postbacks.  
**Fix:** Add pagination: check for `a[href*='__doPostBack'][title*='next' i]` or similar control.

#### GAP-007 — Broward: AntiCaptcha Settlement Loop Lacks Initial Delay
**File:** [`broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py) (lines 79–87)  
**Issue:** The `still_solving` polling loop starts immediately after `detect_and_handle_captcha()` returns. On fast machines, AntiCaptcha may not have fully transitioned from `in_process` yet, causing the loop to incorrectly conclude `still_solving = False` on iteration 0 and proceed too early.  
**Fix:** Add `await page.wait_for_timeout(500)` before the polling loop begins.

### SETTINGS & CONFIGURATION GAPS

#### GAP-008 — Settings Defaults: Wrong Values (CAPTCHA, Retries, Timeout)
**File:** `backend/app/services/settings_service.py`  
**Issue per Section 16.1 of Consolidated Issues:**
- CAPTCHA Resolution Wait: should be **120s** (current default may differ)
- Max Retry & Refresh Attempts: should be **2**
- Portal Navigation Timeout: should be **60s**
**Fix:** Verify and update `AutomationSettings` Pydantic model defaults.

#### GAP-009 — Auto Queue Default Not Verified at Startup
**Issue per Section 5.3:** Auto Queue must be enabled by default.  
**Fix:** Verify that `queue_runner.py` auto-starts when `auto_queue_enabled=True` in settings, and that `monitor/page.tsx` renders enabled state by default.

### FRONTEND GAPS

#### GAP-010 — View Stages Button Non-Functional
**File:** `frontend/src/app/claims/[id]/page.tsx`  
**Issue per Section 6.2:** Clicking "View Stages" does nothing.  
**Fix:** Wire button to open the telemetry/stages drawer or modal with `action_timings` data from the claim detail API response.

#### GAP-011 — Audit Events Not Showing on Claim Detail
**Issue per Section 11:** Claim detail shows "No audit events recorded" even after completed scraping.  
**Fix:** Verify `log_audit_event_async()` calls in `scraper_tasks.py` are being committed, and verify the frontend audit events API call sends the correct `claim_id` filter.

#### GAP-012 — Pagination Limit 100 (Must Support 500)
**Issue per Section 23:** Current max page size is 100; must support 500.  
**Fix:** Update frontend pagination options to include 500. Update backend `GET /api/v1/claims` to accept `limit` up to 500.

#### GAP-013 — FilingDate Lost in Excel/CSV Export
**Issue per Section 10.1 and Section 12:** FilingDate not correctly represented in exports.  
**Fix:** Trace `ScrapedCourtCase.filing_date` through export endpoint and fix column mapping.

#### GAP-014 — Health Page Auto-Refresh Not Default Enabled
**File:** `frontend/src/app/health/page.tsx`  
**Issue per Section 15.1:** Auto-refresh must be enabled by default.  
**Fix:** Initialize `autoRefresh` state to `true` instead of `false`.

#### GAP-015 — Monitor Statistic Cards Inconsistent Design
**Issue per Section 5.1:** Monitor statistic cards don't match Dashboard design.  
**Fix:** Apply the reusable `StatCard` component pattern from Dashboard to Monitor page.

#### GAP-016 — Miami-Dade Missing Pagination for Card Results
**File:** [`miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py)  
**Issue:** The OCS portal may return paginated card results. No pagination loop exists.  
**Fix:** Add a check for "Load More" button or pagination controls after card extraction.

---

## Proposed Changes by File

### Backend — Scraping Engine

---

#### [MODIFY] [`broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py)
- Add 500ms initial delay before AntiCaptcha settlement loop (GAP-007)
- Add header row filter in extraction loop (GAP-001)

#### [MODIFY] [`miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py)
- Fix FilingDate fallback from `today's date` → `""` (GAP-002)
- Refactor card-parsing to explicit label_map dict approach (GAP-003)
- Add pagination handling for card results (GAP-016)

#### [MODIFY] [`hillsborough.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/hillsborough.py)
- Add DataTables pagination loop (GAP-004)

#### [MODIFY] [`harris_district.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_district.py)
- Add ASP.NET GridView pagination loop (GAP-005)

#### [MODIFY] [`harris_cclerk.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py)
- Add WebSearch pagination loop (GAP-006)

---

### Backend — Settings & Services

---

#### [MODIFY] `settings_service.py` / Settings Pydantic schema
- Set `captcha_wait_seconds = 120` (GAP-008)
- Set `max_attempts = 2` (GAP-008)
- Set `page_timeout_seconds = 60` (GAP-008)

---

### Frontend

---

#### [MODIFY] `health/page.tsx`
- Set `autoRefresh` state initial value to `true` (GAP-014)

#### [MODIFY] `claims/[id]/page.tsx`
- Wire "View Stages" button to open telemetry modal (GAP-010)
- Update pagination max size to 500 (GAP-012)

#### [MODIFY] `monitor/page.tsx`
- Verify/enforce Auto Queue enabled by default (GAP-009)
- Apply consistent StatCard component (GAP-015)

#### [MODIFY] `page.tsx` (Dashboard/Claims list)
- Update pagination page size options to include 500 (GAP-012)

---

## Open Questions for User

> [!IMPORTANT]
> **Q1 — Miami-Dade Login:** The `MiamiDadeScraper` accepts `username`/`password` constructor parameters. Where are Miami-Dade portal credentials currently configured in the Settings page? Are they wired to a specific Miami-Dade section, or must this be added?

> [!IMPORTANT]
> **Q2 — Pagination Page Ceiling:** The Broward scraper has a 10-page safety ceiling. Should this be a configurable Settings field (e.g., `max_pagination_pages: int = 10`), or keep it hardcoded?

> [!NOTE]
> **Q3 — Audit Events Gap:** Is the "No audit events" issue on Claim Detail a known bug from a prior session, or should this be root-caused fresh? (I can trace the `log_audit_event_async` call chain completely.)

> [!NOTE]
> **Q4 — Export Fix Scope:** For GAP-013, should the fix scope be limited to FilingDate only (as in Section 10.1), or should the full Excel/CSV parity with JSON be implemented (Section 7 and 12)?

---

## Verification Plan

### Automated Tests
```bash
# All 281 tests must pass after changes
cd backend
.venv\Scripts\pytest --tb=short -q

# Zero lint errors
.venv\Scripts\ruff check app tests

# Zero TypeScript errors
cd frontend
npx tsc --noEmit

# PowerShell syntax
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```

### Manual Verification Points
1. Settings page → CAPTCHA Resolution Wait shows **120s** by default
2. Settings page → Max Retry shows **2** by default
3. Health page → Auto Refresh starts **enabled** without clicking
4. Claim detail → "View Stages" button opens telemetry panel
5. Claims list → Page size options include **500**
6. Monitor → Auto Queue toggle shows **enabled** state on first load

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Pagination loops causing infinite cycles | Medium | 10-page ceiling on all new loops |
| Miami card parser refactor breaks existing tests | Medium | Update mock card HTML in `test_scrapers.py` |
| Settings default change affects running instances | Low | Redis-persisted settings take precedence; only new defaults change |
| FilingDate fix removes today's-date fallback | Low | Correct behavior: empty string is honest; `""` won't break fuzzy matching |
| Header row filter over-excludes valid rows | Low | Filter only exact known header strings |

---

> [!CAUTION]
> **NO IMPLEMENTATION will begin until the user explicitly approves this plan.**
> Per AGENTS.md Rule 8: NO APPROVAL = NO IMPLEMENTATION.
