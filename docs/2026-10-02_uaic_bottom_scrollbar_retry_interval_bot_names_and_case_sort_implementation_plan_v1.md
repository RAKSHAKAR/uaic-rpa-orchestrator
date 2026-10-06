# Implementation Plan: Viewport Bottom Scrollbar Elimination, Failed Claims Interval Retrigger, Full Florida Bot Badges, and "Cases Extracted" Table Sorting

**Document ID:** `docs/2026-10-02_uaic_bottom_scrollbar_retry_interval_bot_names_and_case_sort_implementation_plan_v1.md`  
**Implementation ID:** `IMP-2026-1002-003`  
**Status:** Awaiting Human Approval  
**AI Verification:** Pending Confirmation & Execution  
**Date:** 2026-10-02  
**Author:** AI Agent (Antigravity)  
**Governance:** `diagnose-plan-confirm-execute` skill (`AGENTS.md`)

---

## 1. Problem Diagnosis & Evidence Analysis

Based on user requests and uploaded screenshot artifacts, four specific items have been analyzed:

### Issue 1: Unwanted Horizontal Scrollbar at Bottom of Viewport (Image 1)
- **Observed Behavior:** In the claim detail page (`/claims/:id`), a horizontal scrollbar track and thumb appears along the bottom of the viewport.
- **Root Cause:**
  1. In `frontend/src/app/claims/[id]/page.tsx` line 948:
     ```tsx
     <main id="claim-detail-container" className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none transition-colors">
     ```
     Under standard CSS specifications, `overflow-y: auto` without an explicit `overflow-x: hidden` causes `overflow-x` to default to `auto`.
  2. In the telemetry section (line 1392), the stepper flow specifies a fixed min-width (`min-w-[760px]`). On viewports where `available_width < 760px + 256px (sidebar) + 64px (padding)`, the content overflows horizontally. Because `<main>` allows `overflow-x: auto`, the browser attaches a horizontal scrollbar to the entire page.
- **Remediation:**
  1. Add `overflow-x-hidden` explicitly to `<main id="claim-detail-container">` in `frontend/src/app/claims/[id]/page.tsx`.
  2. Audit and apply `overflow-x-hidden overflow-y-auto` across all page `<main>` tags (`page.tsx`, `monitor/page.tsx`, `health/page.tsx`, `settings/page.tsx`, etc.).
  3. Ensure inner wide components (tables, steppers) are wrapped in localized `overflow-x-auto w-full max-w-full` containers so scrolling is contained within the element itself, never affecting the window.

---

### Issue 2: Automated Retrigger of Failed Cases on Set Time Interval & Settings UI
- **Observed Behavior:** Users require failed court portal scrapers and claims to be automatically retriggered on a configurable time interval (e.g., every 15 minutes, 30 minutes, etc.), managed directly from the Settings page.
- **Root Cause:**
  1. `_async_retrigger_failed_cases()` in `backend/app/tasks/retry_tasks.py` exists, but its retry threshold is tied to `task_retry_delay_seconds` (intended for brief task failure backoff, 30s) rather than an operator-configurable interval.
  2. `TaskQueueSettings` in `backend/app/schemas/settings.py` lacks a dedicated `failed_claims_retry_interval_minutes: int` setting.
  3. `frontend/src/app/settings/page.tsx` does not display an auto-retrigger toggle or interval selector.
- **Remediation:**
  1. Add `failed_claims_retry_interval_minutes: int = Field(default=15, ge=1, le=1440)` to `TaskQueueSettings` in `backend/app/schemas/settings.py`.
  2. Update `frontend/src/types/index.ts` to include `failed_claims_retry_interval_minutes?: number`.
  3. Update `backend/app/tasks/retry_tasks.py` to use `failed_claims_retry_interval_minutes * 60` for `retry_threshold`.
  4. Build a dedicated UI block in `frontend/src/app/settings/page.tsx` under the Queue/Celery section featuring:
     - Master Toggle: **Auto-Retrigger Failed Claims** (`auto_retry_failed_scrapes`).
     - Interval Selector: **Failed Claims Retrigger Interval** (Presets: 5m, 10m, 15m, 30m, 60m, plus custom minute input).
     - Max Retries Limit (`max_task_retries`: 1–10).

---

### Issue 3: Truncated Florida Bot Badges (`Bro`, `Hil`, `Mia`) (Image 2)
- **Observed Behavior:** In the Queue Monitor table (`/monitor`), Texas bots are shown with clear names (`Travis`, `Dallas`, `Harris JP`, `CClerk`, `HCDistrict`), while Florida bots are truncated to `Bro`, `Hil`, `Mia`.
- **Root Cause:**
  In `frontend/src/app/monitor/page.tsx` lines 390–395:
  ```typescript
  const getBotBadgeLabel = (name: string): string => {
    const n = name.toLowerCase();
    if (n.includes("broward")) return "Bro";
    if (n.includes("hillsborough")) return "Hil";
    if (n.includes("miami")) return "Mia";
  ```
- **Remediation:**
  Update `getBotBadgeLabel` in `frontend/src/app/monitor/page.tsx`:
  - `broward` → **`Broward`**
  - `hillsborough` → **`Hillsborough`**
  - `miami` → **`Miami-Dade`**

---

### Issue 4: Sorting by "Cases Extracted" Column in Queue Monitor
- **Observed Behavior:** The "Cases Extracted" column header in `/monitor` is static text and cannot be clicked to sort claims by the number of extracted court cases.
- **Root Cause:**
  1. In `frontend/src/app/monitor/page.tsx` line 843, `<th className="py-3 px-3 text-center">Cases Extracted</th>` lacks sort handlers and icons.
  2. In `backend/app/api/v1/endpoints/claims.py` line 522, `sort_attr_map` does not support `cases_extracted`.
- **Remediation:**
  1. In `backend/app/api/v1/endpoints/claims.py`, add a correlated scalar subquery for `func.count(ScrapedCourtCase.id)`. When `sort_by == "cases_extracted"`, sort by the subquery count ascending or descending.
  2. In `frontend/src/app/monitor/page.tsx`, add `onClick={() => handleSort("cases_extracted")}` and `renderSortIcon("cases_extracted")` to the `Cases Extracted` header.

---

## 2. Proposed Changes & File Modifications

| Component | Target File | Nature of Change |
| :--- | :--- | :--- |
| **CSS / Viewport** | `frontend/src/app/claims/[id]/page.tsx` | Add `overflow-x-hidden` to `<main>` to eliminate bottom horizontal scrollbar. |
| **CSS / Viewport** | `frontend/src/app/page.tsx`, `monitor/page.tsx`, etc. | Ensure all `<main>` containers enforce `overflow-x-hidden overflow-y-auto`. |
| **Settings Schema** | `backend/app/schemas/settings.py` | Add `failed_claims_retry_interval_minutes: int` to `TaskQueueSettings`. |
| **TypeScript Types**| `frontend/src/types/index.ts` | Add `failed_claims_retry_interval_minutes?: number` to `TaskQueueSettings`. |
| **Celery Retry Task**| `backend/app/tasks/retry_tasks.py` | Use configured interval minutes for automatic retry threshold. |
| **Settings UI** | `frontend/src/app/settings/page.tsx` | Add toggle, presets (5m, 10m, 15m, 30m, 60m), and input for failed claims retrigger. |
| **Bot Badge Names** | `frontend/src/app/monitor/page.tsx` | Update `getBotBadgeLabel` to return `Broward`, `Hillsborough`, `Miami-Dade`. |
| **Sorting API** | `backend/app/api/v1/endpoints/claims.py`| Add correlated count subquery to support `sort_by=cases_extracted`. |
| **Sorting UI** | `frontend/src/app/monitor/page.tsx` | Make `Cases Extracted` table header clickable with sort direction indicator. |

---

## 3. Verification & Validation Plan

1. **Automated Testing**:
   - Run backend tests: `.venv\Scripts\pytest tests/test_api.py tests/test_retry_failed_portals.py -q`.
   - Run linter: `.venv\Scripts\ruff check app tests`.
   - Run TypeScript check: `npx tsc --noEmit`.
   - Run PowerShell check: `powershell -File scripts\check_ps1_syntax.ps1`.
2. **Visual & Interactive Verification**:
   - Verify Claim detail page `/claims/81231115-de71-4ea4-a018-ba5b794df682` has zero bottom horizontal scrollbar.
   - Verify `/monitor` displays Florida bots as `Broward`, `Hillsborough`, `Miami-Dade`.
   - Verify clicking "Cases Extracted" column in `/monitor` sorts claims ascending and descending.
   - Verify `/settings` allows setting failed cases retry interval, saves to database, and persists on page reload.

---

*Plan formulated and saved to `docs/` in accordance with Universal AI Engineering Governance.*
