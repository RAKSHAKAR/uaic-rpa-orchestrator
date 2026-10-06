# Implementation Plan: Full Audit Summary, Count Accuracy Alignment, & Missing Items Execution

**Implementation ID:** `IMP-2026-1002-008`  
**Date:** 2026-10-02  
**Author:** AI Agent (Antigravity)  
**Status:** Pending User Confirmation  
**Document Version:** v1  
**Governance:** Adheres to `.agents/skills/diagnose-plan-confirm-execute/SKILL.md` (Understand → Inspect → Plan → Confirm → Execute)

---

## 1. Executive Summary & Root Cause Analysis of Count Inaccuracies

### User Feedback
> *"still numbers are not correct, you have not worked lots of things from this conversations. pls summerise all the things and make note missing things which you have not done and then start working on them"*

### Root Cause Analysis of "Numbers Not Correct"
1. **Pushed Claims Zeroing Out "Matches Confirmed":**
   - In `backend/app/api/v1/endpoints/claims.py` (`/api/v1/claims/stats`), `match_found` count is computed using `where(ClaimRecord.record_status == RecordStatusEnum.MATCH_FOUND)`.
   - When a claim with confirmed fuzzy matches is dispatched to Guidewire, its `record_status` transitions to `COMPLETED`.
   - Consequently, claims that found positive matches and successfully pushed are subtracted from `match_found`, reducing "Matches Confirmed" to **0 (0%)** on the Dashboard even though positive matches were discovered and pushed.
2. **"Review Exceptions (0)" Disconnected from Pending Match Reviews:**
   - In `match_pairs`, there are active pairs with `review_status = 'PENDING_REVIEW'`. However, the top navbar/header badge queries `claims.manual_review` count (which only looks for `record_status == MANUAL_REVIEW`).
   - If a claim has borderline cases needing operator review in `match_pairs`, but the claim status is not explicitly set to `MANUAL_REVIEW`, the badge displays `Review Exceptions (0)` while records exist in `/exceptions`.
3. **Dashboard "In Progress / Queue: 477" Confusion:**
   - The top StatCard displays `477` by combining `in_progress` (8) + `new` (469).
   - However, the Quick Filter Tab below displays:
     - `Active / Running: 8`
     - `Queue Pending (FIFO): 469`
     - `Completed: 2` (whereas the top StatCard displays `Completed Scrapes: 22`!)
   - The tab badge for "Completed" was using `stats?.completed ?? 0` (which is only 2), whereas the top card and the actual table results show 22 (20 clean `NO_MATCH_FOUND` + 2 `COMPLETED`).
4. **Combobox Filter Options Missing Count Badges:**
   - On the Dashboard, the `Status`, `State`, and `Match Status` comboboxes were passing static lists without computing option counts (`opt.count`), making them feel static rather than data-driven.

---

## 2. Comprehensive Inventory of All Conversation Requirements

Below is the complete itemization of everything requested across all screens during this session, mapped to its exact implementation status:

| # | Screen / Area | User Requirement | Current Status | Detailed Notes |
|---|---|---|---|---|
| **D1** | **Dashboard (`/`)** | Improve dashboard and connect with real database statistics | ⚠️ Partially Complete | Stats endpoint connected, but pushed claims zero out `match_found` (shows 0), and tab counts diverge from card counts. |
| **D2** | **Dashboard (`/`)** | Tab count parity with StatCards and table rows | ❌ Missing | Tab "Completed" says `(2)` while card says `22`. Tab "Active" says `(8)` while card says `477`. |
| **D3** | **Dashboard (`/`)** | MultiSelect Combobox options must show dynamic record counts | ❌ Missing | `DASHBOARD_STATUS_OPTIONS` has no `count` properties; needs live counts from claims array. |
| **D4** | **Dashboard (`/`)** | 500 records pagination | ✅ Complete | `<option value={500}>` is present in dropdown. |
| **D5** | **Dashboard (`/`)** | Responsiveness & Dark/Light mode tokens | ✅ Complete | Full-width container and semantic CSS variables applied. |
| **A1** | **Audit Logs (`/audit`)** | Table column header sorting (clickable headers with ↑/↓) | ✅ Complete | Clickable sort on Timestamp, Action, Entity, Operator, Status. |
| **A2** | **Audit Logs (`/audit`)** | Card-click quick filtering without 0-row collision | ✅ Complete | All 6 StatCards reset conflicting filters and isolate records. |
| **A3** | **Audit Logs (`/audit`)** | Top Export toolbar (Excel, CSV, PDF, Background) | ✅ Complete | `ExportActionToolbar` mounted in page header. |
| **A4** | **Audit Logs (`/audit`)** | Multi-select combobox dropdowns with counts | ✅ Complete | Multi-select for Entities, Statuses, Actions. |
| **M1** | **Queue Monitor (`/monitor`)** | Universal `StatCard` visual consistency matching Dashboard | ✅ Complete | Replaced ad-hoc cards with `StatCard` with gradient icons and active rings. |
| **M2** | **Queue Monitor (`/monitor`)** | Top `ExportActionToolbar` (Excel, CSV, JSON, Background) | ✅ Complete | Mounted in header. |
| **M3** | **Queue Monitor (`/monitor`)** | Interactive StatCard filtering on click | ✅ Complete | Ingest, Scraper, Matcher, Guidewire, Active cards wired up. |
| **M4** | **Queue Monitor (`/monitor`)** | Auto Queue enabled by default on load | ⚠️ Needs Verification | Defaults in UI state, but must persist in backend settings `auto_mode=true`. |
| **C1** | **Claim Detail (`/claims/[id]`)** | Telemetry Audit popup for all 9 operational stages with screenshot download | ⚠️ Partially Complete | `inspectedStage` popup exists, but needs full 9-stage telemetry and direct screenshot download button. |
| **C2** | **Claim Detail (`/claims/[id]`)** | "View Stages" button click handling | ⚠️ Needs Fix | Exists on lines 1944 and 2211, but requires foolproof parameter handling so it never silently fails. |
| **C3** | **Claim Detail (`/claims/[id]`)** | Single-claim Excel and CSV export capturing all data like JSON | ❌ Missing | Backend `export_single_claim` only checks `scraped_cases` table and omits portal JSON bodies; writes empty cases. |
| **C4** | **Claim Detail (`/claims/[id]`)** | Responsive Multi-Portal Scraping Timeline (fix overlap) | ⚠️ Needs Fix | Timeline needs responsive horizontal scroll container on mobile/tablet. |
| **C5** | **Claim Detail (`/claims/[id]`)** | Bot Execution Status KPI cards matching Dashboard design | ❌ Missing | Bot status section uses ad-hoc inline badges rather than unified `StatCard`. |
| **C6** | **Claim Detail (`/claims/[id]`)** | Capture & display `Filing Date` across all scraped public cases | ⚠️ Needs Fix | Backend `_map_claim_to_response` needs fuzzy date field inspection (`FilingDate`, `SuitFiledDate`, `DateFiled`, `Date`). |
| **C7** | **Claim Detail (`/claims/[id]`)** | Scraped Cases table column header sorting | ✅ Complete | Column headers have clickable `onClick` sorting. |
| **C8** | **Claim Detail (`/claims/[id]`)** | Multi-select filters for County, Status, Case Type | ✅ Complete | `MultiSelectDropdown` wired up on lines 2725-2761. |
| **C9** | **Claim Detail (`/claims/[id]`)** | Provenance audit logs ("No audit events recorded yet") | ❌ Missing | Processing history is not auto-synthesized when claims lack explicit rows in `audit_logs`. |
| **C10**| **Claim Detail (`/claims/[id]`)** | Bottom Scraped Cases export: remove PDF, match top Excel/CSV, add Background Export | ❌ Missing | Bottom section still contains redundant PDF and lacks the background export toolbar. |
| **H1** | **System Health (`/health`)** | Auto-Refresh enabled by default (`15s`) | ⚠️ Needs Fix | Toggle default state in `frontend/src/app/health/page.tsx` must be `true`. |
| **E1** | **Exception Review (`/exceptions`)** | Top `ExportActionToolbar` (Excel, CSV, JSON, PDF, Background) | ✅ Complete | Mounted in page header. |
| **E2** | **Exception Review (`/exceptions`)** | Multi-select filters for County, Party, Score Tier | ✅ Complete | `MultiSelectDropdown` wired up on lines 591-625. |
| **E3** | **Exception Review (`/exceptions`)** | StatCard tier filtering on click | ✅ Complete | High, Borderline, Low cards isolate records. |
| **S1** | **Settings (`/settings`)** | Operational defaults: CAPTCHA 120s, Max Retries 2, Timeout 60s, Backoff 5s, Concurrency 10x | ❌ Missing | Backend defaults and UI initial state still hold older values. |
| **S2** | **Settings (`/settings`)** | Email tab: clean CC/BCC display, remove redundant "Render Preview", toggleable Live Preview | ❌ Missing | Empty brackets displayed; "Render Preview" button is still present. |
| **S3** | **Settings (`/settings`)** | Storage cleanup policy (7, 14, 30 days) & manual purge button | ❌ Missing | Missing `retention_days` and `POST /api/v1/settings/storage/cleanup` endpoint. |
| **S4** | **Settings (`/settings`)** | Celery Worker visualizer and queue explanations | ⚠️ Needs Enhancement | Basic queues listed, needs clear enterprise telemetry visualizer. |
| **B1** | **Branding (`/branding`)** | Full verification of all tabs and presets in light/dark | ✅ Complete | Semantic color tokens verified across themes. |
| **X1** | **Cross-Cutting** | Guidewire auto-push triggers clarification & documentation | ❌ Missing | Must be documented in `README.md` and UI tooltips. |
| **X2** | **Cross-Cutting** | Attended vs Unattended mode support in Docker/VPS | ✅ Complete | Xvfb display :99 configured in Docker; local attended GUI supported. |
| **X3** | **Cross-Cutting** | Page refresh performance & query optimization | ⚠️ In Progress | In-memory settings cache and composite DB indexes. |

---

## 3. Targeted Implementation Steps

### Step 1: Fix Count Inaccuracies & Synchronize Dashboard Numbers
1. **Backend Stats Calculation (`backend/app/api/v1/endpoints/claims.py`):**
   - Update `match_found` query to count claims where:
     `record_status == MATCH_FOUND OR (record_status == COMPLETED AND activity_id IS NOT NULL)` OR `fuzzy_match_status.in_([MATCH_FOUND, COMPLETED])`.
   - Update `manual_review` query to count claims with pending match reviews or `record_status == MANUAL_REVIEW`.
   - Ensure `in_progress` strictly counts `SCRAPING_IN_PROGRESS`.
   - Ensure `new` strictly counts `NEW`.
2. **Dashboard UI Numbers & Tab Parity (`frontend/src/app/page.tsx`):**
   - Separate StatCard: Make "In Progress" reflect active scraping (8) with subtitle `${stats?.new} pending in queue`, OR clarify card title and metrics.
   - Quick Filter Tabs: Fix `Completed` tab count to show `finishedCount` (22) instead of `stats?.completed` (2), matching the card badge and table rows.
   - Add dynamic counts to combobox options (`DASHBOARD_STATUS_OPTIONS`, `DASHBOARD_STATE_OPTIONS`, `DASHBOARD_MATCH_OPTIONS`).
   - Fix header `Review Exceptions (${count})` to accurately query pending match review pairs.

### Step 2: Claim Detail Page Enhancements (`frontend/src/app/claims/[id]/page.tsx`)
1. **View Stages & 9-Stage Telemetry Modal:**
   - Ensure `handleOpenBotStages` safely parses all bot names and keys without throwing or silently returning.
   - Include direct download link/button for screenshot artifacts for any stage with an error or capture.
2. **Filing Date Extraction:**
   - In `backend/app/api/v1/endpoints/claims.py`, enhance `_map_claim_to_response` to inspect `FilingDate`, `filing_date`, `Filing Date`, `SuitFiledDate`, `DateFiled`, `Date`, `FileDate`.
3. **Lossless Single-Claim Export:**
   - In `export_single_claim`, extract court cases from both `scraped_cases` table and portal JSON bodies (`fl_jsonbody_*`, `te_jsonbody_*`) so Excel and CSV never write `NO_CASES_FOUND` when cases exist in JSON.
4. **Scraper Execution Status StatCards:**
   - Replace inline bot cards with unified `StatCard` components.
5. **Claim Audit Provenance:**
   - Synthesize chronological audit timeline from claim creation, bot timings, and match pairs when no explicit rows exist in `audit_logs`.
6. **Bottom Scraped Cases Export:**
   - Remove PDF button from bottom section; mount unified `ExportActionToolbar` (Excel, CSV, JSON, Background Export).

### Step 3: Automation Settings Defaults & UI Enhancements (`frontend/src/app/settings/page.tsx` & Backend)
1. **Update Operational Defaults:**
   - `captcha_wait_seconds`: 120
   - `max_captcha_attempts`: 2
   - `page_timeout_seconds`: 60
   - `reload_backoff_seconds`: 5 (with informative tooltip)
   - `max_concurrent_claims`: 10
2. **Email Tab Cleanup:**
   - Remove redundant "Render Preview" button.
   - Toggle "Live Synchronized Render Preview" with "Live Preview" button.
   - Hide raw empty brackets for CC/BCC.
3. **Storage Retention Policy:**
   - Add `retention_days` (default: 30) and "Purge Expired Storage" endpoint `POST /api/v1/settings/storage/cleanup`.

### Step 4: System Health & Queue Monitor Defaults
1. **System Health (`frontend/src/app/health/page.tsx`):**
   - Default `autoRefresh` state to `true` (15s interval).
2. **Queue Monitor (`frontend/src/app/monitor/page.tsx`):**
   - Ensure Auto Queue defaults to `true`.

### Step 5: Guidewire Auto-Push Clarification & Documentation
1. Document the exact auto-push condition in `README.md` and UI tooltips:
   - Condition: `integration.auto_push_on_match == true` AND `similarity_score >= threshold` (positive match).
   - Clarify why `NO_MATCH_FOUND` claims do NOT push (Guidewire requires `CaseItems: [...]` payload).

---

## 4. Verification & Quality Gates

1. **Database Counts Verification:** Run SQL verification queries on Postgres to confirm 100% parity between DB metrics, API stats, StatCards, and table tabs.
2. **Unit & Integration Tests:** Run `pytest` across all 556 tests.
3. **Frontend Compilation:** Run `npx tsc --noEmit` and `npm run build`.
4. **Code Quality:** Run `ruff check app tests` and `check_ps1_syntax.ps1`.
5. **Docker Container Deployment:** Rebuild and redeploy `uaic_frontend` and `uaic_fastapi`.
6. **Visual E2E Verification:** Automated Playwright browser script verifying every screen.

