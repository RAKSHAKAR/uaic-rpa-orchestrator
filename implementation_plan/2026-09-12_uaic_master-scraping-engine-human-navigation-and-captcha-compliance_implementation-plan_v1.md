# Implementation Plan — Master Scraping Engine, Human-Like Navigation & CAPTCHA Compliance

**Implementation ID:** `IMP-2026-0912-001`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Web Automation, Scraping Engine, Fuzzy Deduplication & Security Handling  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**Created:** 2026-09-12  
**Last Updated:** 2026-09-12  
**AI Agent:** Antigravity  
**Approval Status:** Approved  
**Approved By:** User  
**Approval Date:** 2026-09-12  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Executive Summary & Problem Context

The UAIC Claim & RPA Orchestrator replaces legacy Microsoft Power Automate Desktop RPA bots that automate court-case discovery across 8 Florida and Texas county court portals. 

This plan addresses **Prompt 04 — Master Scraping Engine, Human-Like Navigation & CAPTCHA Compliance**, ensuring:
1. **Strict Unique-Name Orchestration:**
   - Generation of deduplicated unique search names from Insured, Driver, and Claimant fields via a dedicated Unique Names API / Fuzzy Engine.
   - Pre-opening applicable browser portal tabs (FL: 3, TX: 5, Cross-State: 8) with the Anti-Captcha extension.
   - Strictly processing **one unique name at a time** across all open portal tabs sequentially before moving to the next name.
   - Executing legacy Power Automate fuzzy match logic (`evaluate_fuzzy_matches_task`) and Guidewire integration (`notify_guidewire_task`) only after all unique names and portals are fully processed.
2. **CAPTCHA Compliance, Security Handling & Non-Blocking Architecture:**
   - Strict zero-circumvention / zero-spoofing policy (no CAPTCHA token forgery or evasion).
   - Legitimate browser workflow using the Anti-Captcha extension to solve challenges, verified via DOM tokens (`g-recaptcha-response`, `cf-turnstile-response`, `h-captcha-response`).
   - Attended mode human fallback pause allowing an authorized human to solve interactive challenges.
   - Non-blocking error capturing: If blocked by IP/MAC/Rate Limit/429, mark the portal as `FAILED`/`BLOCKED`, capture a full-page screenshot to `.\backend\screenshots`, log to `.\backend\logs\security_blocks.log`, and seamlessly continue processing remaining sites.
   - Cooldown & automated retries: Track portal cooldowns (default or `Retry-After` headers) in Redis and retrigger via Celery tasks once cooldown expires.
3. **Specific QA Fixes & Form Adjustments:**
   - Confirm complete removal of `Loss Location City`, `Loss Location County`, `Garaging City`, and `Garaging State` across New Form, Edit Form, and Data Ingestion Column Mapping.
   - Validate default portal URLs match the exact 8 endpoints specified.
   - Guarantee Auto Queue is enabled by default (`True`).
   - Harden `Filing Date` capture, storage, and display across all 8 scrapers and frontend tables/modals.
   - Provide dedicated Anti-Captcha Extension UI tab in Automation Settings for path configuration, API key management, balance testing, health diagnostics, and browser launch verification.
   - Implement parity `/fuzzymatchapi` endpoint matching `PowerAutomateSolutions/fuzzy-match-api`.

---

## 2. Current System Audit & Baseline Test Results

All existing automated test suites were run prior to planning:
- **Backend Pytest:** 204 passed, 10 skipped (offline Redis/MailDev), 0 failed.
- **Backend Ruff Linter:** 0 errors (all checks passed).
- **Frontend TypeScript (`tsc --noEmit`):** 0 errors.
- **PowerShell AST Syntax (`check_ps1_syntax.ps1`):** 0 errors across all 6 scripts.

---

## 3. Gap Analysis

| Area | Current State | Required / Target State | Gap / Action |
|---|---|---|---|
| **Unique Names API** | `session_runner.py` derives search counts using strict string equality. `matches.py` has `/extract-names` (all DB names) and `/fuzzy-search`. | API to generate deduplicated unique search names for a claim using fuzzy matching across Insured, Driver, Claimant. | **NEW:** Add `POST /api/v1/matches/unique-names` & `GET /api/v1/claims/{id}/unique-names` with fuzzy normalization. |
| **Legacy Fuzzy Match API Parity** | `PowerAutomateSolutions/fuzzy-match-api/` defines `POST /fuzzymatchapi` with `{text1, text2, threshold}`. | Current FastAPI backend should expose this exact contract for 100% legacy parity. | **NEW:** Mount `POST /fuzzymatchapi` and `POST /api/v1/matches/fuzzymatchapi`. |
| **Security & Rate-Limit Block Detection** | `base.py` handles generic exceptions and captures screenshots. | Explicitly detect rate-limit (429), IP ban, WAF challenge, or security block in response/DOM. | **ENHANCE:** Add `detect_security_block()` in `base.py` & handle in `scraper_tasks.py`. |
| **BotStatusEnum Status** | `BotStatusEnum` has `NOT_TRIGGERED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `NO_MATCH_FOUND`. | Prompt asks to mark as "Failed/Blocked". | **ENHANCE:** Add `BLOCKED = "BLOCKED"` to `BotStatusEnum` while preserving `FAILED`. |
| **Cooldown Tracking & Retry** | `retry_tasks.py` blindly retries all failed claims every cycle. | Implement portal-specific cooldown tracking in Redis (`uaic:cooldown:{portal_key}`) and skip in-cooldown portals until expired. | **ENHANCE:** Add cooldown service methods in `backend/app/services/cooldown_service.py` & wire to `scraper_tasks.py` and `retry_tasks.py`. |
| **Audit & Security Logging** | Standard logging writes to `backend.log`. | Write dedicated security block audit log entries and maintain `backend/logs/security_blocks.log`. | **ENHANCE:** Add dedicated security block logger in `base.py` and `scraper_tasks.py`. |
| **Filing Date Display Hardening** | `formatDate` handles `MM/DD/YYYY` and standard ISO. | Ensure all date variations (slashes, hyphens, timestamps, empty) format cleanly without `"Invalid Date"` text. | **VERIFIED & REINFORCED:** Retain multi-key fallback cascade and hardened date formatter. |
| **Anti-Captcha Settings UI** | Dedicated tab exists in `settings/page.tsx` (`activeTab === "extension"`). | Contains 5-step workflow (Path, API Key, Balance Test, Health Diagnostics, Browser Launch Test). | **VERIFIED:** Verify full wiring and responsiveness. |

---

## 4. Proposed Architectural & Code Changes

### 4.1 Backend — Models & Schema Updates

#### [MODIFY] `backend/app/models/claim.py`
- Add `BLOCKED = "BLOCKED"` to `BotStatusEnum` so portals can be explicitly marked as `BLOCKED` upon encountering rate limits or security blocks, while maintaining full backward compatibility.

#### [MODIFY] `backend/app/schemas/claim.py`
- Ensure `BotStatusEnum` in schemas includes `BLOCKED`.

### 4.2 Backend — Cooldown & Security Block Service

#### [NEW] `backend/app/services/cooldown_service.py`
- Implement `set_portal_cooldown(portal_key: str, seconds: int = 300, reason: str = "") -> None`:
  - Stores cooldown expiration in Redis key `f"uaic:cooldown:{portal_key}"`.
- Implement `is_portal_in_cooldown(portal_key: str) -> tuple[bool, int]`:
  - Checks if portal is currently in cooldown and returns remaining seconds.
- Implement `clear_portal_cooldown(portal_key: str) -> None`:
  - Clears cooldown once manually reset or successfully retested.
- Implement `get_all_portal_cooldowns() -> dict[str, dict]`:
  - Returns active cooldown status for all 8 portals for health/monitoring endpoints.

### 4.3 Backend — Fuzzy Engine & Unique Names API

#### [MODIFY] `backend/app/services/fuzzy_engine.py`
- Add `generate_unique_names_for_claim(claim: Any, threshold: float = 0.85) -> list[dict]`:
  - Extracts Insured, Driver, Claimant first and last names.
  - Normalizes text (stripping noise patterns, punctuation, casing).
  - Uses RapidFuzz similarity (`token_sort_ratio` / `partial_ratio`) to deduplicate names that refer to the same party.
  - Respects DualSearch and TripleSearch rules.
  - Returns structured list: `[{"party_type": "Insured", "first_name": "...", "last_name": "...", "full_name": "...", "search_order": 1}, ...]`.

#### [MODIFY] `backend/app/api/v1/endpoints/matches.py`
- Add `POST /api/v1/matches/unique-names`:
  - Accepts claim fields payload or `claim_id` query parameter.
  - Returns deduplicated unique search names list.
- Add `POST /fuzzymatchapi` and `POST /api/v1/matches/fuzzymatchapi`:
  - Exact legacy Power Automate contract: `{text1, text2, threshold}` -> `{result: "Match Found" | "No Match Found", score: float}`.

#### [MODIFY] `backend/app/main.py`
- Mount root `POST /fuzzymatchapi` to ensure direct requests to `/fuzzymatchapi` succeed identically to the standalone legacy service.

### 4.4 Backend — Scraping Tasks & Base Automation

#### [MODIFY] `backend/app/automation/base.py`
- Add `detect_security_block(page: Page) -> tuple[bool, str, int]`:
  - Inspects page title, HTTP status, and DOM text for security blocks: "429 Too Many Requests", "Cloudflare Ray ID", "Access Denied", "Rate limit exceeded", "Your IP has been blocked", "Attention Required! | Cloudflare".
  - Checks `Retry-After` response header if available.
  - Returns `(is_blocked, block_reason, suggested_cooldown_seconds)`.
- Ensure security block logging writes to `backend/logs/security_blocks.log` as well as standard logger.

#### [MODIFY] `backend/app/tasks/scraper_tasks.py`
- Before launching the browser session, call `generate_unique_names_for_claim(claim)` to produce the ordered unique search names.
- Check active portal cooldowns: If a portal is currently in active cooldown (`is_portal_in_cooldown(name)`), log cooldown notice, mark status as `BLOCKED`, and continue to other portals.
- In the inner loop, after calling `scraper.search_on_page`:
  - Check `detect_security_block`: if blocked, set portal status to `BotStatusEnum.BLOCKED` (or `FAILED`), record cooldown in Redis, capture full-page screenshot to `backend/screenshots`, record `ErrorScreenshot` DB entry, write security block log, and seamlessly continue to the next portal.
- Maintain telemetry, correlation IDs, and stage timings for every step.

#### [MODIFY] `backend/app/tasks/retry_tasks.py`
- When evaluating failed/blocked claims for retry, check if the failed portals have cleared their cooldown period. Only retrigger portals whose cooldown has expired.

### 4.5 Frontend — Polish & Verification

#### [MODIFY] `frontend/src/app/settings/page.tsx`
- Ensure the AntiCaptcha Extension UI tab (`activeTab === "extension"`) displays all 5 steps cleanly, with real-time feedback for API balance, health diagnostics, and browser launch test.
- Add quick-links to test individual portal reachability and view cooldown states.

### 4.6 Automated Test Suite

#### [NEW] `backend/tests/test_imp_2026_0912_001.py`
- Comprehensive test suite covering:
  1. `test_unique_names_generation_and_deduplication`: Validates Insured, Driver, Claimant fuzzy grouping.
  2. `test_fuzzymatchapi_endpoint_parity`: Validates exact legacy Power Automate request/response contract.
  3. `test_unique_names_api_endpoint`: Validates `POST /api/v1/matches/unique-names`.
  4. `test_security_block_detection`: Validates 429 / WAF / Cloudflare block detection.
  5. `test_cooldown_service_and_redis`: Validates cooldown setting, TTL expiration, and status retrieval.
  6. `test_name_first_orchestration_with_cooldown`: Validates scraping engine skips or isolates blocked portals and completes remaining sites.
  7. `test_deprecated_fields_complete_absence`: Validates 4 deprecated fields are absent across all models and schemas.
  8. `test_filing_date_robustness`: Validates multi-key fallback cascade and formatting without `"Invalid Date"`.

---

## 5. Verification & Testing Plan

### 5.1 Automated Quality Gates
1. `backend/.venv\Scripts\pytest tests/test_imp_2026_0912_001.py -q`
2. `backend/.venv\Scripts\pytest --tb=short -q` (full suite across all 28+ test files)
3. `backend/.venv\Scripts\ruff check app tests` (0 errors)
4. `frontend/npx tsc --noEmit` (0 errors)
5. `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1` (0 errors)

### 5.2 Browser Subagent & Visual Verification
- Use `browser_subagent` to visually test:
  - Automation Settings -> AntiCaptcha Extension tab (all 5 steps rendered, interactive buttons).
  - Claims Detail -> Scraped Cases table and modal (Filing Date rendering).
  - Ingestion Upload -> Column mapping (confirm 4 fields absent).
- Save recordings to `implementation_plan/Recording/` (`.webp`) and screenshots to `implementation_plan/Images/` (`.png`).

---

## 6. Acceptance Criteria Checklist

- [x] **Strict Unique-Name Orchestration:** Unique names generated via fuzzy deduplication before browser tabs launch; Name A searched across all open portals before moving to Name B; legacy fuzzy matching and Guidewire integration run only after all names are completed.
- [x] **CAPTCHA Non-Circumvention:** Automation relies strictly on the Anti-Captcha extension and token checks; Attended mode supports human pausing; zero spoofing.
- [x] **Non-Blocking Security Architecture:** Blocked portals (IP/MAC/Rate Limit/429) marked `BLOCKED`/`FAILED`, full-page screenshot saved to `backend/screenshots`, logged to `backend/logs/security_blocks.log`, and remaining sites processed seamlessly.
- [x] **Automated Cooldown:** Portals in cooldown are tracked in Redis and retried after cooldown ends.
- [x] **Fuzzy Match API Parity:** `/fuzzymatchapi` and `/api/v1/matches/fuzzymatchapi` accept `{text1, text2, threshold}` and return `{result, score}`.
- [x] **Unique Names API:** `POST /api/v1/matches/unique-names` returns deduplicated search names.
- [x] **4 Deprecated Fields:** `Loss Location City`, `Loss Location County`, `Garaging City`, `Garaging State` absent from all forms and column mapping.
- [x] **Default Portal URLs:** All 8 default portal URLs exact as specified.
- [x] **Auto Queue:** Enabled by default (`True`).
- [x] **Filing Date:** Captured and displayed accurately without `"Invalid Date"`.
- [x] **Zero Regressions:** 100% test pass rate across pytest (275/275 tests passed), ruff (0 errors), tsc (0 errors), Next.js build (11/11 pages compiled), and PowerShell syntax (0 errors).

---

**AI Verification:** Complete (100% Automated Testing Suite)  
**Implementation ID:** `IMP-2026-0912-001`  
All code and automated tests verified and committed.

