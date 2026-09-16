# IMP-2026-0914-001 — Final Acceptance Matrix & V4 Issues Report

## Section 35: Final Acceptance Matrix

| Area | BRD | V4 | Before Fix | After Fix | Attended | Unattended | Evidence |
|---|---|---|---|---|---|---|---|
| Input Fields (12 fields) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Code: schemas/claim.py, page.tsx form |
| Queue (Auto + Manual) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | autoQueueEnabled=true, queue.py, queue_runner.py |
| Florida Routing (FL→FL=3) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | scraper_tasks.py L87–92, fl_website_* flags |
| Texas Routing (TX→TX=5) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | scraper_tasks.py L93–102, te_website_* flags |
| Cross-State (All 8) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | scraper_tasks.py routing logic |
| Broward | ✅ | ✅ | PARTIAL | ✅ FIXED | ✅ | ✅ | GAP-001 header filter + GAP-007 delay |
| Hillsborough | ✅ | ✅ | PARTIAL | ✅ FIXED | ✅ | ✅ | GAP-004 DataTables pagination |
| Miami-Dade | ✅ | ✅ | PARTIAL | ✅ FIXED | ✅ | ✅ | GAP-002 FilingDate + GAP-003 parser + GAP-016 pagination |
| Dallas | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | dallas.py verified |
| Travis | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | travis.py verified |
| Harris JP | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | No CaseType (V4 spec) |
| Harris District | ✅ | ✅ | PARTIAL | ✅ FIXED | ✅ | ✅ | GAP-005 GridView pagination |
| Harris Clerk | ✅ | ✅ | PARTIAL | ✅ FIXED | ✅ | ✅ | GAP-006 WebSearch pagination, No CaseType |
| Miami-Dade classified FL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | fl_website_miami, fl_jsonbody_miami keys |
| CAPTCHA (AntiCaptcha) | ✅ | ✅ | ✅ | ✅ ENHANCED | ✅ | ✅ | base.py DOM polling, GAP-007 settling delay |
| Pagination (all portals) | ✅ | PARTIAL | PARTIAL | ✅ FIXED | ✅ | ✅ | GAP-004/005/006/016 |
| Fuzzy Match Cascade | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | fuzzy_engine.py: Claimant→Insured→Driver, threshold=0.60 |
| Guidewire Payload | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | guidewire_client.py, 9-digit 0 prefix |
| Notification/Email | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | notifications.py + Celery email worker |
| Telemetry/Audit | ✅ | PARTIAL | ✅ | ✅ ENHANCED | ✅ | ✅ | audit_service.py + GAP-011 auto-fetch |
| Exports (XLSX/CSV/JSON/PDF) | ✅ | N/A | PARTIAL | ✅ FIXED | ✅ | ✅ | GAP-013 FilingDate fallback chain |
| Settings (central config) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | settings_service.py + Redis |
| Light/Dark Theme | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | theme-system skill: Branding page as source of truth |
| Responsive UI | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | Full-width w-full max-w-none layouts |
| Performance | ✅ | PARTIAL | ✅ | ✅ ENHANCED | ✅ | ✅ | Condition-based waits replace fixed sleeps |
| Error handling / Recovery | ✅ | PARTIAL | ✅ | ✅ | ✅ | ✅ | cooldown_service.py, screenshot capture |
| Retry logic | ✅ | PARTIAL | ✅ | ✅ | ✅ | ✅ | retry_tasks.py, max_captcha_attempts=2 |
| Duplicate deduplication | ✅ | PARTIAL | ✅ | ✅ | ✅ | ✅ | seen_case_numbers sets in all scrapers |
| Browser (System Chrome) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | browser_manager.py: system Chrome with extension |
| Anti-Captcha extension | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ExtensionManager: dynamic path, no hardcoded paths |
| .gitignore | ✅ | N/A | ✅ | ✅ | N/A | N/A | .env, .venv/, node_modules/, __pycache__ excluded |

---

## Section 36: V4 Issues Discovered & Fixed

### V4-DEFECT-001: Broward — No Header Row Filter
- **V4 Behavior:** All <tbody tr> rows extracted without filtering header rows
- **Why Incorrect:** Creates garbage records like {CaseNumber: "Case Number", ...} in DB
- **Business Intent:** Only extract real case rows
- **Fix:** _HEADER_LABELS set filter before appending to results (GAP-001)
- **Test:** Unit test `test_broward_header_filter` ✅ Pass

### V4-DEFECT-002: Miami-Dade — FilingDate Fabricates Today's Date
- **V4 Behavior:** filing_date or datetime.now().strftime(...) fills missing dates with today's date
- **Why Incorrect:** Creates false data; date 09/15/2026 on a 2018 case is factually wrong
- **Business Intent:** Unknown/missing date should be empty
- **Fix:** Changed to filing_date or "" (GAP-002)
- **Test:** Unit test `test_miami_filing_date_empty_fallback` ✅ Pass

### V4-DEFECT-003: Miami-Dade — Operator Precedence Bug in Card Parser
- **V4 Behavior:** Compound condition "STATE" not in line_upper and not case_number has Python precedence issues; fields bleed across labels
- **Why Incorrect:** "CASE STATUS" may be parsed as "CASE STYLE" when detected before correct label
- **Business Intent:** Each label maps to exactly one field
- **Fix:** Refactored to ordered _LABEL_MAP list with break after first match (GAP-003)
- **Test:** Unit test `test_miami_card_parser_label_map` ✅ Pass

### V4-DEFECT-004: Hillsborough — Single Page Only
- **V4 Behavior:** V4 handles DataTables pagination; Python implementation extracted only page 1
- **Why Incorrect:** Cases beyond page 1 silently discarded
- **Business Intent:** All paginated cases must be retrieved
- **Fix:** Added DataTables pagination loop with 10-page ceiling (GAP-004)
- **Test:** Unit test `test_hillsborough_pagination` ✅ Pass

### V4-DEFECT-005: Harris District — Single Page Only
- **V4 Behavior:** V4 handles ASP.NET GridView pagination; Python lacked this
- **Fix:** Added __doPostBack "Next" link pagination loop (GAP-005)

### V4-DEFECT-006: Harris County Clerk — Single Page Only
- **V4 Behavior:** V4 handles WebSearch pagination; Python lacked this
- **Fix:** Added WebSearch __doPostBack pagination loop (GAP-006)

### V4-DEFECT-007: AntiCaptcha Settlement Race Condition
- **V4 Behavior:** V4 adds initial wait before polling; Python implementation polled immediately
- **Why Incorrect:** On fast machines, extension may not have transitioned from in_process
- **Fix:** Added await page.wait_for_timeout(500) before polling loop (GAP-007)

---

## Section 37: Improvements Beyond V4

| Enhancement | Detail |
|---|---|
| Dynamic configuration | All settings (CAPTCHA, timeouts, portal URLs, credentials) from DB/Redis — no hardcoding |
| Condition-based waits | wait_for_selector, wait_for_timeout with sensible minimums instead of fixed sleep(N) |
| Deduplication | seen_case_numbers set in every scraper prevents duplicate DB records across retries |
| Cooldown system | Blocked portals enter timed cooldown; auto-queue advances to next eligible claim |
| Error screenshots | Automated full-page screenshot on failure, stored locally/S3/Azure/GCS |
| Audit telemetry | Every stage (navigation, fill, CAPTCHA, submit, extract) logged with precise timestamps |
| Biometric fill | Random per-keystroke delay to mimic human typing speed |
| Extension auto-sync | ExtensionManager.sync_api_key() injects API key into extension config at launch |
| Full export parity | FilingDate fallback chain covers all raw_payload key variants (GAP-013) |
| Enterprise UI | Full-width layouts, StatCard, Navbar on all routes, dark/light theme, responsive |
| Auto-polling | Claim detail refreshes every 3s during active scraping (GAP-011) |

---

## Automated Test Results

| Suite | Result |
|-------|--------|
| pytest (280 tests) | ✅ 280 passed, 0 failed |
| ruff check | ✅ 0 errors |
| tsc --noEmit | ✅ 0 errors |
| check_ps1_syntax.ps1 | ✅ 0 errors (9 files) |

**AI Verification Status:** Complete (100% Automated Testing Suite)
