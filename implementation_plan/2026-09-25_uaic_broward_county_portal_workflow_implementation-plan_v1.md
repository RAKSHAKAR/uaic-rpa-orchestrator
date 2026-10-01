# Implementation Plan — Broward County Court Portal Workflow

**Implementation ID:** IMP-2026-0925-001  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Broward County Clerk (FL)  
**Feature / Issue:** Prompt 1 — Broward County Portal Workflow Implementation & Fixes  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Completed  
**Created:** 2026-09-25  
**Last Updated:** 2026-09-25  
**AI Agent:** Antigravity  
**Approval Status:** Approved  
**Approved By:** User  
**Approval Date:** 2026-09-25  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Problem Statement & Objective

The objective is to implement and fix the Broward County court portal workflow in the existing application without rebuilding the scraper, without creating a new application, and without breaking any existing functionality.

The Broward workflow must:
1. Obtain all settings dynamically from the existing Settings page (`http://localhost:3000/settings` / DB).
2. For each queue record, retrieve all unique names upfront from the Unique Names API.
3. Launch the browser once, open the Broward portal tab, and process unique names strictly one-by-one sequentially (Name 1 -> Complete Broward -> Name 2 -> Complete Broward -> Name 3 -> Complete Broward).
4. Strictly execute steps A through L:
   - **Step A — Open Broward:** Navigate to configured Broward URL, wait for DOM load, refresh if unusable.
   - **Step B — Case Search:** Click "Case Search".
   - **Step C — Party Name:** Verify Case Search page loads; verify "Party Name" tab is selected (select if not).
   - **Step D — Enter Search Data:** Fill Last Name, First Name, Date From using CURRENT unique name only.
   - **Step E — CAPTCHA:** Detect & solve CAPTCHA using configured integration (AntiCaptcha / tokens).
   - **Step F — CAPTCHA Failure:** Refresh, re-navigate to search state, re-enter data, retry up to configured Max Retry & Refresh Attempts.
   - **Step G — Session Timeout:** Detect "Session timeout warning", click "Continue session", verify fields, re-enter if lost without switching unique names.
   - **Step H — Search:** Immediately click "Search" upon CAPTCHA verification.
   - **Step I — Results:** Wait for result page to fully load and verify.
   - **Step J — Extract Results:** Extract ALL available columns (Case Number, Case Style, Case Type, Filing Date, Case Status, Access Level, and any additional columns).
   - **Step K — Pagination:** Process ALL pages, rows, and available results.
   - **Step L — Database:** Persist to existing database format (`fl_jsonbody_broward` and `ScrapedCourtCase`).
5. Return tab to search state between unique names, keep browser open, process next unique name.
6. After all unique names finish, close tab, close browser, update queue record, advance to next queue record.
7. Capture correlated screenshots and execution logs under `backend/screenshots` and `backend/logs` respecting storage provider settings.

---

## 2. Current State vs. Gap Analysis

| Area | Current State | Required State | Gap |
|---|---|---|---|
| **Base URL Navigation** | Directly jumps to `/Web2/CaseSearchECA/Index/` | Navigates from configured base URL (default: `https://www.browardclerk.org/`), waits for load, refreshes if failed, clicks "Case Search" | Missing home-to-case-search navigation flow & reload retry |
| **Tab Verification** | Assumes Party Name tab is already selected | Verifies Party Name tab is active, clicks tab if not active | Need explicit verification & click for Party Name tab |
| **Unique Name Execution Order** | `for party in party_pairs: for portal in scrapers:` (searches each name across all portals) | For Broward: Broward tab opened, Unique Name 1 processed to completion, then Unique Name 2 processed to completion, etc. | Must execute unique names sequentially on Broward tab |
| **All-Column Extraction** | Extracts only 5 fixed columns (`CaseNumber`, `CaseStyle`, `CaseType`, `FilingDate`, `CaseStatus`) | Extracts ALL available columns including `AccessLevel`, `CourtType`, and any dynamic table headers | Missing `AccessLevel` and dynamic column mapping |
| **Session Timeout Warning** | Only checks generic Odyssey timeout in base class | Explicitly handles "Session timeout warning", clicks "Continue session", verifies whether input fields were retained, and re-enters if lost | Needs dedicated session timeout recovery loop in Broward workflow |
| **Reset Between Names** | Relies on page reload or re-navigation | Provides clean `return_to_search_state()` to reset inputs/tabs for next unique name while keeping browser and tab open | Needs robust in-tab search reset for sequential processing |

---

## 3. Scope of Changes

### In Scope
1. **`backend/app/automation/florida/broward.py`**:
   - Dynamic navigation: open configured base URL, check usable, click "Case Search" if on home page.
   - Party Name tab verification and selection.
   - Biometric data filling for current unique name (Last Name, First Name, Date From).
   - CAPTCHA detection and retry loop adhering to dynamic settings (`max_captcha_attempts`, `captcha_wait_seconds`).
   - Session timeout detection, "Continue session" click, and data re-entry if lost.
   - Immediate search trigger upon CAPTCHA solve token verification.
   - All-column table extraction (mapping all available `th` / `td` columns including `AccessLevel`).
   - Complete multi-page pagination.
   - Clean state return for next sequential unique name.
2. **`backend/app/tasks/scraper_tasks.py`**:
   - Ensure for Broward (and county portals), unique names are processed strictly sequentially on the open portal tab (Name 1 -> Complete -> Name 2 -> Complete -> Name 3 -> Complete).
   - Upfront retrieval of all unique names for the queue record before portal processing.
   - Browser kept open across all unique names, closed once all names complete.
   - Correlated error screenshot and log saving under `backend/screenshots/{claim_id}/{portal_key}/` and `backend/logs/{claim_id}/{portal_key}/`.
3. **`backend/tests/test_broward_portal.py`**:
   - Comprehensive test suite testing all 20+ required scenarios.

### Out of Scope
- Modifying other portal scrapers (Miami, Hillsborough, Dallas, etc.).
- Changing database schema or ORM models.
- Changing Guidewire payload contract.
- Changing frontend UI layout or route structure.

---

## 4. Detailed Implementation Steps

### Step 1: Broward Scraper Refinement (`backend/app/automation/florida/broward.py`)
1. **Dynamic URL & Initial Load (Step A):**
   - Use `self.base_url` obtained dynamically from `SystemSettings.portals.broward_url`.
   - Navigate to `self.base_url`. Wait for `domcontentloaded`.
   - Validate page usability (check body non-empty, status 200). If not usable, reload once and wait.
2. **Case Search Navigation (Step B):**
   - Check current URL: if already on `/Web2` or `/CaseSearchECA`, proceed.
   - Otherwise, click "Case Search" link/button (`a:has-text("Case Search"), a[href*="CaseSearch"], a[href*="/Web2"]`).
   - Wait for Case Search ECA form to be present.
3. **Party Name Tab Verification (Step C):**
   - Check if `#nameSearch` tab-pane is active or if `a[href*='#nameSearch']` parent has class `active`.
   - If not selected, click `a[href*='#nameSearch']` or `a:has-text('Party Name')` and wait for `#nameSearch` to become visible.
4. **Data Entry (Step D):**
   - Check session timeout popup before entering data.
   - Locate `input#lastName`, `input#firstName`, `input#filingDateOnOrAfterP`.
   - Enter current unique name values using `self.biometric_fill()` respecting `typing_speed_mode` and `typing_delay_ms`.
5. **CAPTCHA Solving & Failure Handling (Steps E & F):**
   - Engage `detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)`.
   - Poll for solve tokens (`g-recaptcha-response` > 25 chars, Turnstile token > 20 chars).
   - If failed after wait, refresh page, return to search state, re-enter data, and retry up to `self.max_attempts`.
6. **Session Timeout Warning (Step G):**
   - Check for modal/dialog containing "Session timeout warning" or "Session Timeout".
   - Click "Continue session" button.
   - Verify if `input#lastName` still contains the current unique name's last name.
   - If lost, re-enter Last Name, First Name, Date From.
7. **Submit & Results (Steps H & I):**
   - Click `#PersonSearchResults` immediately upon CAPTCHA verification.
   - Wait for results page (`table tbody tr`, `#resultsTable`, or "No records found").
8. **Extraction & Dynamic Columns (Step J):**
   - Read all table header labels (`th`) to build dynamic column map.
   - Extract `CaseNumber`, `CaseStyle`, `CaseType`, `FilingDate`, `CaseStatus`, `AccessLevel`, and any additional columns into case payload.
   - Normalize dates and ensure backward compatibility.
9. **Pagination (Step K):**
   - Loop while next-page control is active, extracting all rows on every page.
10. **State Reset for Next Name (Section 4):**
    - Provide `return_to_search_state(page)` to navigate back or click "New Search" / "Back to Search" so the Broward tab is immediately ready for Unique Name 2.

### Step 2: Sequential Orchestration & Queue Runner (`backend/app/tasks/scraper_tasks.py`)
1. Before starting portal processing, call `generate_unique_names_for_claim(claim)` to retrieve ALL unique names.
2. Launch configured browser once.
3. Open Broward tab once.
4. For Broward (and county portals):
   - Sequentially iterate through each unique name:
     - Name 1: execute search on Broward tab to completion -> accumulate results.
     - Reset tab to search state.
     - Name 2: execute search on Broward tab to completion -> accumulate results.
     - Reset tab to search state.
     - Name 3: execute search on Broward tab to completion -> accumulate results.
5. All unique names completed for Broward:
   - Persist accumulated cases to `fl_jsonbody_broward` and `ScrapedCourtCase`.
   - Close Broward tab.
   - Close browser session.
6. Record status updated, audit event logged, queue runner advances to next queue record.

### Step 3: Error Handling & Diagnostics
1. If any exception occurs during Broward processing:
   - Check `storage_cfg.capture_error_screenshots`.
   - Capture full/viewport screenshot.
   - Save to `backend/screenshots/{claim_id}/broward/{claim_id}_broward_{timestamp}.png`.
   - Log execution entry to `backend/logs/{claim_id}/broward/execution.log`.
   - Store error screenshot record in DB with correlation.
   - Do not leak passwords/API keys in screenshots or logs.

---

## 5. Testing & Verification Plan

### Test Scenarios to Verify:
1. **Dynamic Settings:** Scraper reads URL, timeouts, retry limits, CAPTCHA wait, and browser engine from `SystemSettings`.
2. **Unique Names Retrieval:** Upfront API call extracts all unique names for the claim.
3. **Sequential Processing:** Unique Name 1 finishes before Unique Name 2 begins.
4. **Browser & Tab Reuse:** Browser and Broward tab remain open across unique names and are not closed/reopened.
5. **Step A (Open):** Navigates to Broward URL; reloads if unusable.
6. **Step B (Case Search):** Clicks "Case Search" from home page.
7. **Step C (Party Name):** Checks tab and selects "Party Name" tab if not active.
8. **Step D (Data Entry):** Last Name, First Name, Date From filled correctly for each unique name.
9. **Step E (CAPTCHA):** Handles CAPTCHA challenge and detects verification.
10. **Step F (CAPTCHA Failure):** Reloads and retries up to configured max attempts.
11. **Step G (Session Timeout):** Clicks "Continue session", verifies input fields, re-enters if lost.
12. **Step H (Search):** Submits search immediately upon CAPTCHA verification.
13. **Step I & J (Extraction):** Extracts all columns (Case Number, Case Style, Case Type, Filing Date, Case Status, Access Level, and dynamic columns).
14. **Step K (Pagination):** Navigates through all result pages.
15. **Step L (Database):** Saves to `fl_jsonbody_broward` and `ScrapedCourtCase` without breaking existing schemas.
16. **Browser Close:** Closes tab and browser only after all unique names finish.
17. **Error Screenshot & Logs:** Saves correlated screenshot and log files in `backend/screenshots/` and `backend/logs/`.

---

## 6. Verification Commands

```bash
# Backend pytest suite (must pass 100%)
cd backend && .venv\Scripts\pytest -q

# Dedicated Broward test suite
cd backend && .venv\Scripts\pytest tests/test_broward_portal.py -v

# Backend linter (0 errors)
cd backend && .venv\Scripts\ruff check app tests

# Frontend TypeScript (0 errors)
cd frontend && npx tsc --noEmit

# PowerShell syntax check (0 errors)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```

---

## 7. Risks & Rollback Plan

- **Risk:** Existing tests expecting the previous iteration order in `scraper_tasks.py`.
  - **Mitigation:** Maintain full backward compatibility for `execute_portal_searches` and all test fixtures. Run the complete 475-test suite to guarantee zero regressions.
- **Rollback:** Revert git changes to `broward.py` and `scraper_tasks.py` if unexpected issues arise.
