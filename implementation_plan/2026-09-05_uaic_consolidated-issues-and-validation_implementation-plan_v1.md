# Implementation Plan — UAIC Claim & RPA Orchestrator Consolidated Issues and Validation Requirements

Implementation ID:   IMP-2026-0905-005  
Project:             UAIC Claim & RPA Orchestrator  
Module:              frontend / backend / automation / tasks / settings / audit / exceptions / monitor / claims  
Feature / Issue:     Consolidated Issues & Validation Across UI/UX, Functionality, Dual-Mode Theme, Responsiveness, Automation, Audit & Safety  
Document Type:       Implementation Plan  
Version:             v1  
Status:              Completed  
Created:             2026-09-05  
Last Updated:        2026-09-05  
AI Agent:            Antigravity  
Approval Status:     Approved  
Approved By:         User  
Approval Date:       2026-09-05  
Verification Status: AI Generated — Awaiting Human Verification  
Primary Reference:   `implementation_plan/ChatGPT_Prompt/UAIC Claim & RPA Orchestrator — Consolidated Issues and Validation Requirements.md`  
Authoritative Architectural Reference: `PowerAutomateSolutions/BotCreation_1_0_0_7/` (V4)  

---

## 1. Executive Summary & Objectives

This implementation plan addresses the complete, consolidated set of 26 requirement domains identified in `UAIC Claim & RPA Orchestrator — Consolidated Issues and Validation Requirements.md`. The goal is to resolve every remaining functional, UI, UX, automation, data integrity, and operational defect across the application to establish a production-grade, fully validated system.

---

## 2. Forensic Gap Analysis & Root Cause Diagnosis

| Section | Feature Area | Current State | Root Cause | Target Solution |
|---|---|---|---|---|
| **§1.2, §3.7, §4.2, §10.3** | **Multi-Select Filters** | Single `<select>` tags or text filters across tables | No reusable multi-select component | Create reusable `<MultiSelectDropdown />` supporting select all, clear, multiple tokens, search, and badges |
| **§1.3, §5.1, §9** | **Reusable Stat Cards** | Dashboard has gradient icon cards; Monitor & Claim Detail have plain text boxes | Divergent design implementations | Create `<StatCard />` component matching Dashboard design language and reuse across Monitor, Audit, and Claim Detail |
| **§3.1, §3.2** | **Audit Page Excel Export** | Audit page only offers CSV and JSON; backend `/api/v1/audit/export` accepts `^(csv\|json)$` | Missing `xlsx` format handling in backend & frontend button | Add openpyxl workbook generator in `audit.py` `/export` and add Excel button to Audit page header |
| **§3.3, §3.4** | **Audit KPI Clickable Filters** | KPI metric cards in Audit page are static `<div>` containers | Missing `onClick` filter handler | Wire up metric cards to filter by action (`CLAIM`, `SETTINGS`, `MATCH`, `FAILED`) and today's activity |
| **§3.5, §3.6** | **Audit Table Sorting** | Column headers are non-clickable plain text | Hardcoded `order_by(AuditLog.timestamp.desc())` in backend `audit.py` | Add `sort_by` and `sort_dir` query parameters to `list_audit_logs` and clickable sorting on table headers |
| **§4.1** | **Exceptions Page Export** | Exceptions page lacks export controls | Missing export toolbar | Add Excel (`.xlsx`), CSV, and JSON export buttons using `AsyncExportModal` / client data |
| **§5.3** | **Auto Queue Default** | `is_auto_queue_enabled()` returns `False` if Redis key is unset; frontend defaults to `false` | Uninitialized Redis key defaults to falsy | Default Redis key to `"true"` on first read; initialize frontend state to `true` |
| **§6.1, §6.2** | **View Stages Button & Popup** | Clicking `View Stages` sets tab above viewport with no scroll or modal; user sees nothing | Missing viewport scroll and modal inspector | Trigger dedicated stage inspector modal or auto-scroll with visual highlight to execution stages card |
| **§7, §12** | **Claim Detail Export Parity** | Top CSV only exports cases; Excel lacks 8-bot sheet; bottom section redundantly has PDF | Asymmetric data mapping | Add complete claim metadata to CSV, add 8 Bots Status sheet to Excel workbook, remove redundant bottom PDF button |
| **§8** | **Concurrent Timeline Overlap** | Width calculation inside narrow percentage bar causes horizontal clipping on mobile/tablet | `w-64 shrink-0` + tight bar width | Responsive stacking on mobile, duration badges outside progress bar, no overlapping labels |
| **§10.1** | **Missing Filing Date** | `ScrapedCaseResponse` in `claim.py` schema omits `case_status` and `case_type`; date formatting mismatches | Schema field omission in `ScrapedCaseResponse` | Add `case_status`, `case_type`, `raw_payload` to `ScrapedCaseResponse` and ensure scrapers format dates consistently |
| **§10.2** | **Standalone Sort Button** | Standalone "Sort: Descending" button is awkward alongside sortable table headers | Leftover prototype control | Remove standalone sort button; upgrade table headers with clean Lucide sort indicators |
| **§11** | **Missing Audit Events on Claim** | Claim detail displays "No audit events recorded" after automation runs | Scraper, matcher, and Guidewire tasks never called `record_audit_event_background` with claim ID | Add audit logging in `scraper_tasks.py`, `fuzzy_tasks.py`, and `notify_guidewire_task`; ensure query checks both `entity_id` and `claim_number` |
| **§14** | **Guidewire Automation Clarity** | Qualification criteria and automatic push behavior unclear to operator | Lack of operational visibility and explicit audit trail | Document and audit the exact trigger: auto-push triggered on `RecordStatusEnum.MATCH_FOUND` (score >= 0.60) or manual approval |
| **§15.1** | **Health Auto-Refresh** | Auto-refresh defaults to `0` (disabled) | `autoRefreshInterval` initial state is `0` | Default to `15` seconds with active status indicator and configurable picker |
| **§16.1** | **Browser & CAPTCHA Defaults** | Defaults: wait 60s, max 5 retries, timeout 30s | Schema defaults need alignment | Update defaults: CAPTCHA wait = **120s**, max retries = **2**, portal timeout = **60s** |
| **§17.1, 17.2, 17.3** | **Email Settings Clutter** | Large empty CC/BCC italic blocks; redundant "Render Preview" button; live preview always visible | Redundant controls and un-collapsed empty states | Collapsible CC/BCC inputs, remove redundant Render Preview button, show Live Preview only when preview tab is active |
| **§18** | **Celery Queue Admin UX** | Queue tab only shows 4 basic text inputs | Missing live queue metrics & worker health | Add live Redis queue depths, active worker count, and worker ping tool to Settings Queue tab |
| **§23** | **Pagination 500 Records** | Backend `audit.py` and `notifications.py` capped at `le=100` | Hardcoded validation limits | Increase `le=500` across backend endpoints and add 250 & 500 options to frontend pagination |

---

## 3. Detailed Proposed Changes by Component

### Component A: Reusable UI Components
1. **[NEW] `frontend/src/components/MultiSelectDropdown.tsx`**:
   - Generic multi-select dropdown supporting:
     - Search filter inside dropdown.
     - "Select All" and "Clear All" actions.
     - Badge/chip counter showing selected items.
     - Light and dark mode compatible.
2. **[NEW] `frontend/src/components/StatCard.tsx`**:
   - Reusable statistic card matching Dashboard design:
     - Title, formatted value, subtitle/trend.
     - Gradient icon container with custom colors.
     - Optional `onClick` callback for filtering, with active highlight state.

### Component B: Backend Endpoints & Schemas
1. **[MODIFY] `backend/app/schemas/settings.py`**:
   - Set `captcha_wait_seconds = 120`.
   - Set `max_captcha_attempts = 2`.
   - Set `page_timeout_seconds = 60`.
   - Document `reload_backoff_seconds` clearly in docstrings and UI descriptions.
2. **[MODIFY] `backend/app/schemas/claim.py`**:
   - Add `case_status: str | None = None` and `case_type: str | None = None` to `ScrapedCaseResponse`.
3. **[MODIFY] `backend/app/api/v1/endpoints/audit.py`**:
   - Increase `page_size` max to `le=500`.
   - Add `sort_by` (`timestamp`, `action`, `entity_type`, `status`) and `sort_dir` (`asc`, `desc`) to `list_audit_logs`.
   - Add `xlsx` format support in `export_audit_logs` using `openpyxl`.
   - Ensure claim audit query checks both `AuditLog.entity_id == claim_id` and `AuditLog.claim_number == claim.claim_number`.
4. **[MODIFY] `backend/app/api/v1/endpoints/notifications.py`**:
   - Increase `page_size` max to `le=500`.
5. **[MODIFY] `backend/app/tasks/queue_runner.py`**:
   - In `is_auto_queue_enabled()`, default to `True` if Redis key does not exist yet.
6. **[MODIFY] `backend/app/tasks/scraper_tasks.py`**:
   - Emit audit logs on scraper completion: `SCRAPER_COMPLETED` with claim ID, county name, and case count.
7. **[MODIFY] `backend/app/tasks/fuzzy_tasks.py`**:
   - Emit audit logs on fuzzy match evaluation: `FUZZY_MATCHING_COMPLETED` with positive and borderline match counts.
   - Emit audit logs on Guidewire dispatch: `GUIDEWIRE_PUSHED` with Activity ID or error.

### Component C: Frontend Pages
1. **[MODIFY] `frontend/src/app/audit/page.tsx`**:
   - Replace static stat cards with `<StatCard />` supporting click-to-filter.
   - Add "Export Excel" button to top export area.
   - Implement sortable column headers with visual sort indicators.
   - Integrate `<MultiSelectDropdown />` for Actions, Entity Types, and Statuses.
   - Add 250 and 500 page size options.
2. **[MODIFY] `frontend/src/app/exceptions/page.tsx`**:
   - Add export controls (Excel, CSV, JSON) via `AsyncExportModal` or client download.
   - Integrate `<MultiSelectDropdown />` for County, Party Type, and Score Range.
   - Add 50, 100, 250 page size options.
3. **[MODIFY] `frontend/src/app/monitor/page.tsx`**:
   - Default `autoQueueEnabled` state to `true`.
   - Replace queue metric boxes with unified `<StatCard />` components.
   - Add 250 and 500 page size options.
4. **[MODIFY] `frontend/src/app/claims/[id]/page.tsx`**:
   - Update `View Stages` button to trigger a focused stage inspector modal.
   - Unify Scraper Status 8 Bots metric cards with `<StatCard />`.
   - Make Concurrent Multi-Portal Timeline fully responsive (no text overlap or horizontal clipping).
   - Remove standalone "Sort: Descending" button above cases table.
   - Remove bottom redundant "PDF" export button.
   - Improve CSV export to include complete claim metadata.
   - Add 8 Bots Status sheet to Excel workbook export.
5. **[MODIFY] `frontend/src/app/health/page.tsx`**:
   - Set `autoRefreshInterval` default to `15` seconds.
6. **[MODIFY] `frontend/src/app/settings/page.tsx`**:
   - Remove redundant "Render Preview" button in Template Studio.
   - Conditionally render Live Synchronized Preview only when preview tab or toggle is active.
   - Streamline CC/BCC inputs to avoid large empty placeholder blocks.
   - Enhance Celery Worker Queues & Failure Alerts tab with live queue depth indicators and worker ping capability.

---

## 4. Verification & Testing Plan

### 4.1 Automated Backend & Quality Tests
```bash
# 1. Backend tests
cd backend
.venv\Scripts\pytest --tb=short -q

# 2. Ruff linter
.venv\Scripts\ruff check app tests

# 3. Frontend TypeScript
cd frontend
npx tsc --noEmit

# 4. Frontend production build
npm run build

# 5. PowerShell syntax check
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"

# 6. Domain safety audit
python scripts\find_uaic_emails.py
```

### 4.2 Browser & End-to-End Validation
1. **Audit Page**:
   - Verify clicking stat cards filters the table by action or status.
   - Verify clicking table headers toggles ASC/DESC sorting.
   - Download Excel export and verify formatting.
2. **Exceptions Page**:
   - Test multi-select filtering across counties and party types.
   - Export exceptions to Excel, CSV, and JSON.
3. **Monitor Page**:
   - Verify Auto Queue displays `ENABLED` on initial load.
   - Verify stat cards match Dashboard design.
4. **Claim Detail Page**:
   - Click `View Stages` and verify stage inspector opens.
   - Verify Concurrent Timeline displays cleanly without text overlap on mobile, tablet, and desktop.
   - Verify audit trail displays scraping, matching, and Guidewire events.
   - Verify bottom cases export has Excel, CSV, JSON (no duplicate PDF).
5. **Health Page**:
   - Verify auto-refresh is active by default (15s).
6. **Settings Page**:
   - Verify CAPTCHA wait default is 120s, retries is 2, navigation timeout is 60s.
   - Verify redundant Render Preview button is removed.
   - Verify Queue tab displays active queue depths.
7. **Pagination**:
   - Verify selecting 500 records renders smoothly across Claims, Audit, and Monitor.

---

## 5. Governance & Constraints Compliance
- **Zero Corporate Domain Emails**: All recipient defaults and test strings strictly use `@test.com` (strictly zero corporate domain violations).
- **Theme Governance**: Strictly Light and Dark modes; zero OS detection.
- **Protected Directories**: Zero modification or deletion of protected user folders.
- **Single Source of Truth**: Update `implementation_plan/README.md` and keep records in `implementation_plan/`.
