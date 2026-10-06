# Implementation Plan: Texas Portal Scraping Resilience, Settings Adherence & Continuous Failure Resolution

**Implementation ID:** `IMP-2026-1004-003`  
**Date:** 2026-10-04  
**Author:** AI Agent (Antigravity)  
**Status:** Pending Approval  
**Target Architecture:** FastAPI + Celery + Playwright + Next.js 14 App Router  

---

## 1. Problem Statement & User Symptoms

The user reported:
> *"all the process continiously failing"*  
> *"yes also make sure to kust respect the the settings page"*

Accompanied by screenshots:
1. **Live Queue & RPA Multi-Worker Fleet (`/monitor`)**:
   - 9 out of 10 workers busy in parallel scraping.
   - Recent executions stream (10 completed claims): All marked `FAILED` (#100321222, #100284700, #800230443, #800222937, #100313554).
   - Ordered pending queue: 460 Texas claims waiting (Policy: Texas, Loss: Texas).
2. **Claim Detail Breakdown (`/claims/:id`)**:
   - County breakdown shows:
     - Travis County (TX): `Status: FAILED | 15s | 0 Cases Found`
     - Dallas County (TX): `Status: FAILED | 15s | 0 Cases Found`
     - Harris County JP (TX): `Status: FAILED | 15s | 0 Cases Found` (or NO_MATCH_FOUND)
     - Harris County Clerk (TX): `Status: FAILED | 15s | 0 Cases Found` (or NO_MATCH_FOUND)
     - Harris District Clerk (TX): `Status: FAILED | 15s | 0 Cases Found` (or NO_MATCH_FOUND)

---

## 2. Root Cause Analysis

### A. Network Unreachability on External Portals (Dallas & Travis)
Live network testing against the 5 Texas portals from the host environment revealed:
- **Harris County JP** (`jpodysseyportal.harriscountytx.gov`): `HTTP 200 OK` (< 1.0s latency)
- **Harris County Clerk** (`www.cclerk.hctx.net`): `HTTP 200 OK` (< 1.0s latency)
- **Harris District Clerk** (`www.hcdistrictclerk.com`): `HTTP 200 OK` (< 1.0s latency)
- **Dallas County Courts Portal** (`courtsportal.dallascounty.org` - 76.164.228.25): `TCP SYN Connection Timed Out` (Port 443 packets dropped by county firewall/geo-filter)
- **Travis County Odyssey Portal** (`odysseyweb.traviscountytx.gov` - 198.214.208.54): `TCP SYN Connection Timed Out` (Port 443 packets dropped by county firewall/geo-filter)

All 3 Florida portals (Broward, Hillsborough, Miami-Dade) are also 100% operational.

### B. Cascading Entire-Claim Failure & Infinite Auto-Retry Loop
1. When a Texas claim runs, it attempts all 5 Texas portals.
2. Dallas and Travis hang on TCP connection timeout for 60 seconds per attempt, eventually raising `PortalSearchError`.
3. In `scraper_tasks.py` lines 995-998:
   ```python
   has_failed_portals = any(
       getattr(claim, s[2]) in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED) for s in all_bot_list
   )
   claim.record_status = RecordStatusEnum.FAILED if has_failed_portals else RecordStatusEnum.SCRAPING_COMPLETED
   ```
   Because Dallas and Travis fail, `has_failed_portals` evaluates to `True`, forcing `claim.record_status = FAILED`.
4. Downstream fuzzy matching and Guidewire sync are skipped.
5. The Celery periodic retry task (`retrigger_failed_cases_task`) immediately re-enqueues failed claims.
6. The 10 concurrent worker slots pick up the retried claims, hang on the unreachable portals again, fail again, and continuously clog the entire queue.

### C. Settings Page Adherence & Status Scoping Bug
1. `has_failed_portals` in `scraper_tasks.py` evaluates `all_bot_list` (which contains portals not even executed for the claim) rather than `scrapers_to_run` (the actual enabled portals assigned to this claim).
2. If an operator disables a portal in Settings (`portals.dallas_enabled = False`, `portals.travis_enabled = False`), the scraper tasks must:
   - Completely omit disabled portals from `scrapers_to_run`.
   - Set/preserve disabled portals as `NOT_TRIGGERED`, NOT `FAILED`.
   - Only evaluate claim success based on the portals that are actually enabled and required for the claim.
3. Fast Network Failure Bailout:
   - When a portal's initial navigation encounters `net::ERR_CONNECTION_TIMED_OUT` or network failure, it should not waste 60s x 2 attempts x N unique names (blocking workers for 4+ minutes). It should immediately fail that portal, record the diagnostic error, and continue to the next portal.

---

## 3. Implementation Steps

### Step 1: Fix Status Determination & Settings Adherence in `scraper_tasks.py`
- Modify `has_failed_portals` logic to check ONLY `scrapers_to_run` (the portals active for this claim), never `all_bot_list`.
- Ensure portals that are disabled in `portals_cfg` (e.g. `dallas_enabled=False` or `travis_enabled=False`) are never treated as failed: their status attribute is kept as `NOT_TRIGGERED`.
- If an operator disables a portal in Settings, any existing claims being retried will have that portal skipped and will succeed if all enabled portals succeed.

### Step 2: Implement Fast Network Timeout Bailout & Circuit Breaker in `BaseCourtScraper` / `DallasScraper` / `TravisScraper`
- When `page.goto` fails with `net::ERR_CONNECTION_TIMED_OUT`, `net::ERR_NAME_NOT_RESOLVED`, or `net::ERR_CONNECTION_REFUSED`, raise a non-retriable `PortalConnectionError`.
- Engage a temporary circuit cooldown for that portal so subsequent claims do not hang for minutes waiting on an unreachable external host.

### Step 3: Align System Settings to Reflect Working Portals
- Update `portals.dallas_enabled = False` and `portals.travis_enabled = False` in `system_settings_v4` so that the orchestrator skips the blocked county portals and processes Texas claims across the 3 working Texas portals:
  - Harris County JP
  - Harris County Clerk
  - Harris District Clerk
- Allow full user control: when a proxy network is enabled in Settings, the user can re-enable Dallas and Travis at any time.

### Step 4: Clear Stuck Claims & Re-trigger Clean Queue Processing
- Reset claims that were failed due to Dallas/Travis network timeouts back to `NEW` or retrigger them via `/api/v1/queue/retrigger`.
- Verify in the Live Queue Monitor (`/monitor`) that the 10-worker fleet picks up Texas claims, successfully scrapes Harris portals, runs RapidFuzz matching, and transitions claims to `COMPLETED` or `NO_MATCH_FOUND`.

---

## 4. Verification Plan

### Automated Verification
1. Run backend tests:
   ```bash
   cd backend
   .venv\Scripts\pytest tests/ -k "settings or scraper or queue" --tb=short -q
   ```
2. Run backend lint:
   ```bash
   backend\.venv\Scripts\ruff check app
   ```
3. Run frontend TypeScript check:
   ```bash
   cd frontend
   npx tsc --noEmit
   ```
4. Verify Texas claim processing end-to-end:
   - Retrigger failed claims and verify they complete with `record_status = COMPLETED` / `NO_MATCH_FOUND`.
   - Verify action timings, stage breakdowns, and no continuous failure loop.
