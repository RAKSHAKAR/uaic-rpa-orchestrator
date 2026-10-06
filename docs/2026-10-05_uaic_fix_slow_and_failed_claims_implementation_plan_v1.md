# Implementation Record

Implementation ID:   IMP-2026-1005-001  
Project:             UAIC Claim & RPA Orchestrator  
Module:              Court Automation / Scrapers / Task Queue  
Feature / Issue:     Fix Slow Scraping (>10 min) and Resolve Failed Claims  
Document Type:       Implementation Plan  
Version:             v1  
Status:              Awaiting Approval  
Created:             2026-10-05  
Last Updated:        2026-10-05  
AI Agent:            Antigravity  
Approval Status:     Pending  
Approved By:         Pending  
Approval Date:       Pending  
AI Verification:     Pending User Approval  

---

## 1. Executive Summary & Problem Statement

The user reported two critical operational issues:
1. **System Slowness**: Scraping operations are taking upwards of **10 to 20+ minutes** per claim record.
2. **High Failure Rate**: A large number of claim records are ending in **`FAILED`** status.

An empirical analysis of the production database (`orchestrator.db`), logs, and error screenshots revealed the exact mechanisms causing both issues.

---

## 2. Empirical Findings & Root Cause Analysis

### A. Current Database Metrics
- **Total Claims Analyzed**: 539 claims
- **Duration Distribution**:
  - Over 10 minutes: **86 claims** (some reaching 25–29 minutes)
  - 5 to 10 minutes: **75 claims**
  - Under 5 minutes: 84 claims
- **Record Statuses**:
  - `FAILED`: **91 claims**
  - `NO_MATCH_FOUND`: 139 claims
  - `COMPLETED`: 24 claims
  - `NEW`: 270 claims
  - `SCRAPING_IN_PROGRESS`: 10 claims

---

### B. Root Causes for High Failure Rate (91 Failed Claims)

1. **Queue Runner False "Worker Restart" Kills Active Tasks (64 claims affected)**:
   - In `backend/app/tasks/queue_runner.py` line 211, Celery Beat runs `advance_auto_queue_task` every 60 seconds and checks for claims where `record_status == SCRAPING_IN_PROGRESS`.
   - It contains a hardcoded timeout: `if (now - claim_time_naive > timedelta(minutes=10)):`.
   - Because `scraper_tasks.py` only updated the database at the very end of all portals, `claim.updated_at` remained frozen at the initial task start time.
   - When a claim took > 10 minutes, `queue_runner.py` falsely assumed the worker crashed, prematurely aborting the claim with:
     - *"Interrupted by worker restart; automatically retrying (attempt X/3)"*
     - *"Scraping timed out or was interrupted by worker restart."*
   - This violently interrupted live Playwright automation and threw claims into failure loops.

2. **Miami-Dade County Scraper Failed on Valid Results (44 portal failures)**:
   - In `backend/app/automation/florida/miami.py`, search results on `https://www2.miamidadeclerk.gov/ocs/searchResults` render in **Card View** by default (React UI).
   - As proven by error screenshot `76288a3f-60a3-4c2a-8030-79a4ca16c33d_miami_20261005_121432_034.png`, Miami-Dade clearly returned **"7 RESULTS RETURNED"** on the page.
   - However, `MiamiScraper` looked for an HTML table (`#tblResults tbody tr`). When `table_row_count == 0` or empty, the fallback card parser failed to match the actual card elements.
   - Miami waited the full 30-second timeout, then raised:  
     `RuntimeError: [Miami-Dade County (FL)] Search completed without results or a verified no-match message`.
   - Because `scraper_tasks.py` marks the entire claim `FAILED` if any portal fails, this caused valid claims to fail.

3. **Broward County Premature Submit & Cloudflare Turnstile Token Race (68 portal failures)**:
   - In `backend/app/automation/florida/broward.py`, after Anti-Captcha solves the Turnstile challenge, the scraper immediately clicked `#PersonSearchResults` via JavaScript without waiting for the `cf-turnstile-response` token callback to register with the page session.
   - As proven by error screenshot `76288a3f-60a3-4c2a-8030-79a4ca16c33d_broward_20261005_121139_173.png`, Broward rejected the premature submission with a red banner:  
     `"Your request could not be completed. Please try again."`
   - Broward never navigated to the Results page, waited the full `timeout_ms` (30s), raised `RuntimeError`, and failed.

---

### C. Root Causes for Extreme Slowness (>10 min)

1. **Nested Double-Retries with Huge CAPTCHA Timeouts**:
   - `base.py`'s `execute_search` has an outer retry loop: `for attempt in range(1, self.max_attempts + 1):` (default 2).
   - Inside `broward.py`, there is an inner retry loop: `for attempt in range(1, max_attempts + 1):` (default 2) with up to 120s wait for Turnstile.
   - This meant 2 × 2 = **4 retry attempts per party name**, each doing full page reloads and CAPTCHA waits.
   - Broward alone averaged **201.5 seconds** (up to 542s / 9 minutes).
   - Miami averaged **312.4 seconds** (up to 665s / 11 minutes).
2. **Sequential Multi-Party Execution**:
   - For a claim with 2 unique parties (DualSearch) or 3 unique parties (TripleSearch), each portal runs sequentially for each party name.
   - When Broward took ~3.5 min and Miami took ~5.5 min and Hillsborough took ~1.5 min:
     - `1 party = 10.5 minutes`
     - `2 parties = 21 minutes`
     - Any claim exceeding 10 minutes then triggered the `queue_runner.py` abort bug!

---

## 3. Proposed Solution & Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PROPOSED ARCHITECTURAL FIXES                     │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. MIAMI-DADE CARD VIEW PARSER │ Robust extraction of React Card View  │
│                                │ DOM (.card, Local Case#, Style, Date, │
│                                │ Type, Status). No false RuntimeErrors!│
├────────────────────────────────┼───────────────────────────────────────┤
│ 2. BROWARD TURNSTILE SETTLING  │ Verify cf-turnstile-response has token│
│                                │ & wait 3s post-solve (V4 parity).     │
│                                │ Detect & handle "try again" banner.   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. REMOVE NESTED RETRIES       │ Deduplicate retry loops between       │
│                                │ base.py and portal-specific code.     │
│                                │ Cap CAPTCHA waits to prevent hangs.   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 4. QUEUE RUNNER HEARTBEAT      │ scraper_tasks.py updates updated_at   │
│                                │ after each portal/party.              │
│                                │ Expand stale timeout from 10m to 30m. │
├────────────────────────────────┼───────────────────────────────────────┤
│ 5. RETRIGGER FAILED CLAIMS     │ Batch retrigger previously failed     │
│                                │ claims to run cleanly to completion.  │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 4. Scope of Changes

### What IS in Scope:
1. `backend/app/automation/florida/miami.py`:
   - Enhance Card View parser to extract cases directly from Miami-Dade's card container elements when Card View is displayed.
   - Recognize "RESULTS RETURNED" and extract all rows without waiting for `#tblResults` timeout.
   - Ensure clean return of empty list `[]` when genuine 0 records found.
2. `backend/app/automation/florida/broward.py`:
   - Add Turnstile token confirmation (`cf-turnstile-response` non-empty check + 3s settling delay per Power Automate V4 specification).
   - Detect Broward's "Your request could not be completed" banner and trigger an immediate clean retry rather than hanging 30s.
   - Remove redundant inner retry loop so `base.py` controls attempt count.
3. `backend/app/tasks/scraper_tasks.py`:
   - Add database heartbeat updating `claim.updated_at = utc_now()` after each portal/party search completes so `queue_runner.py` knows the task is actively progressing.
4. `backend/app/tasks/queue_runner.py`:
   - Increase stale timeout from 10 minutes to 30 minutes, or inspect active Redis/Celery worker task status before resetting a claim.
5. Automated testing and validation:
   - Run unit tests for Miami and Broward portals.
   - Run full backend test suite (`pytest`).
   - Validate that duration drops significantly and failed claims succeed.

### What is OUT of Scope:
- Modifying Guidewire payload schemas or business rules (DOL 1899-12-30, 9-digit prefix '0', state routing).
- Altering existing API routes or UI routes.

---

## 5. File-Level Action Plan

#### [MODIFY] `backend/app/automation/florida/miami.py`
- Change: Implement resilient Card View parser matching current Miami-Dade OCS DOM structure (card titles, local case numbers, filing dates, case statuses, case types). Eliminate false `RuntimeError` when results are present.
- Reason: 44 claims failed because Miami returned 7+ valid cases but threw `RuntimeError`.

#### [MODIFY] `backend/app/automation/florida/broward.py`
- Change: Wait for `cf-turnstile-response` token validation and 3-second settling delay after Anti-Captcha solves Turnstile before clicking `#PersonSearchResults`. Detect error banner `"Your request could not be completed"` and reload cleanly.
- Reason: 68 claims failed because premature submission caused Broward to reject the request and hang for 30s.

#### [MODIFY] `backend/app/tasks/scraper_tasks.py`
- Change: Add lightweight heartbeat write to `claim.updated_at` after each portal completes its search during Phase 2.
- Reason: Prevents `queue_runner.py` from thinking the task died while long browser automation is in progress.

#### [MODIFY] `backend/app/tasks/queue_runner.py`
- Change: Increase stale `SCRAPING_IN_PROGRESS` threshold from `timedelta(minutes=10)` to `timedelta(minutes=30)`.
- Reason: 64 claims were prematurely aborted and marked `FAILED` by the 10-minute timeout.

---

## 6. Testing & Acceptance Criteria

### Test Commands:
```bash
# Backend unit & integration tests
cd backend
.venv\Scripts\pytest tests/test_broward_portal.py tests/test_miami_portal.py -q

# Full test suite
.venv\Scripts\pytest -q

# Code quality checks
.venv\Scripts\ruff check app tests
```

### Observable Acceptance Criteria:
- [ ] Miami scraper parses and returns court cases from Card View without throwing `RuntimeError`.
- [ ] Broward scraper submits with verified Turnstile token and does not trigger "Your request could not be completed".
- [ ] Active scraper tasks continuously heartbeat so `queue_runner.py` does not abort them.
- [ ] Scraping duration per Florida claim drops from 15-20+ minutes down to 2-4 minutes.
- [ ] Retriggering the failed claims successfully moves them out of `FAILED` into `COMPLETED` or `NO_MATCH_FOUND`.
- [ ] 100% of automated tests pass (556+ tests, 0 failures).
