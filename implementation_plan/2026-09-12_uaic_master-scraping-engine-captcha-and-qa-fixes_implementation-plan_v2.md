# Implementation Plan — Master Scraping Engine, CAPTCHA Compliance & QA Fixes

**Implementation ID:** `IMP-2026-0912-004`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Web Automation, Multi-Tab Scraping Engine, CAPTCHA Compliance, and Operational QA  
**Document Type:** Implementation Plan  
**Version:** v2  
**Status:** Ready for Review  
**Created:** 2026-09-12  
**AI Agent:** Antigravity  
**Approval Status:** Pending User Review  

---

## 1. Executive Summary & Objective

The **UAIC Claim & RPA Orchestrator** automates court-case discovery across 8 Florida and Texas county court portals, replacing legacy Power Automate Desktop RPA bots. 

This implementation plan addresses **Prompt 04 — Master Scraping Engine, CAPTCHA Compliance & QA Fixes**, focusing on:
1. **Strict Unique-Name Orchestration (Mandatory):**
   - Execute the Fuzzy Match API to derive deduplicated unique search names (Insured, Driver, Claimant).
   - Launch System Google Chrome with the Anti-Captcha extension and pre-open tabs for all applicable portals in parallel.
   - Strictly process **one unique name at a time** across all open portal tabs sequentially (Name A: Tab 1 → Extract → Match → Store, then Tab 2 → Extract → Match → Store, ..., across all tabs) before moving to Name B.
   - After all unique names are fully processed across all tabs, execute the legacy Power Automate Fuzzy Match cascade and Guidewire integration.
2. **CAPTCHA Compliance & Non-Blocking Architecture:**
   - 100% adherence to zero-spoofing and zero-circumvention policy (no CAPTCHA token forgery or evasion).
   - If blocked (IP/MAC rate limit, HTTP 429, WAF challenge), instantly mark the portal as `BLOCKED`/`FAILED`, capture a **full-page screenshot** to `.\backend\screenshots`, log details to `.\backend\logs\security_blocks.log`, and **seamlessly continue processing remaining sites**.
   - Implement portal-specific cooldown tracking in Redis and automated retry logic respecting cooldowns or `Retry-After` headers.
3. **Specific QA Fixes & Form Adjustments:**
   - Verify permanent removal of `Loss Location City`, `Loss Location County`, `Garaging City`, and `Garaging State` from New Form, Edit Form, and Ingestion Column Mapping.
   - Verify the exact 8 default portal URLs:
     - Broward: `https://www.browardclerk.org/`
     - Hillsborough: `https://hover.hillsclerk.com/`
     - Miami-Dade: `https://www2.miamidadeclerk.gov/ocs`
     - Travis: `https://odysseyweb.traviscountytx.gov/Portal/`
     - Dallas: `https://courtsportal.dallascounty.org/DALLASPROD/Home/`
     - Harris JP: `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`
     - CClerk: `https://www.cclerk.hctx.net/Applications/WebSearch/`
     - HCDistrict: `https://www.hcdistrictclerk.com/`
   - Ensure Auto Queue is enabled by default (`True`).
   - Investigate and harden `Filing Date` extraction, persistence, and display across all 8 scrapers, backend serialization, and frontend UI.
   - Verify the dedicated Anti-Captcha Extension UI tab in Automation Settings (`activeTab === "extension"`) covering the 5-step configuration workflow.

---

## 2. Baseline Audit & Diagnostic Findings

Before planning modifications, a full audit of existing implementations and automated test suites was performed:

| Component | Status | Findings |
|---|---|---|
| **Python Linter (`ruff check`)** | ✅ PASSED (0 errors) | All backend files clean. |
| **Frontend TypeScript (`tsc --noEmit`)** | ✅ PASSED (0 errors) | Zero compilation errors across all App Router components. |
| **PowerShell Syntax (`check_ps1_syntax.ps1`)** | ✅ PASSED (0 errors) | Zero AST errors across all 6 scripts. |
| **Backend Test Suite (`pytest`)** | ⚠️ 1 Failure in 282 tests | 281 tests passed; exactly 1 failed: `test_queue_runner_progression_and_recovery` in `tests/test_plan_verification.py`. Root cause: Test database had 3 lingering `SCRAPING_IN_PROGRESS` claims from prior test runs, exhausting the `max_concurrency=3` slots and preventing the test from advancing. Test harness needs to ensure clean worker slot state. |
| **Unique-Name Orchestration** | ✅ Implemented | `generate_unique_names_for_claim()` in `fuzzy_engine.py` generates deduplicated unique names. Outer loop iterates over names, inner loop over portal tabs in `scraper_tasks.py`. Can be enhanced to persist cases immediately per tab per name. |
| **CAPTCHA Compliance & Block Handling** | ✅ Implemented | `detect_security_block()` in `base.py` catches 429, WAF, Cloudflare. `scraper_tasks.py` catches `SecurityBlockException`, sets `BLOCKED`, logs to `backend/logs/security_blocks.log`, and continues to next portal. Screenshot needs `full_page=True` enhancement. |
| **Deprecated Fields Removal** | ✅ Implemented | `Loss Location City`, `Loss Location County`, `Garaging City`, and `Garaging State` are absent from `TARGET_CLAIM_FIELDS` and frontend forms. |
| **Default URLs** | ✅ Implemented | All 8 URLs in `PortalsSettings` (`schemas/settings.py`) match the required endpoints character-for-character. |
| **Auto Queue Default** | ✅ Implemented | `is_auto_queue_enabled()` returns `True` and initializes Redis key `uaic:queue:auto_mode` to `"true"`. |
| **Filing Date Display** | ✅ Implemented | All 8 scrapers extract `FilingDate`; `ScrapedCourtCase` persists `filing_date`; frontend displays via multi-key fallback cascade without `"Invalid Date"` bugs. |
| **Anti-Captcha Extension UI Tab** | ✅ Implemented | `activeTab === "extension"` in `settings/page.tsx` provides the 5-step workflow (Path, API Key, Test Balance, Verify Health, Browser Test). |

---

## 3. Proposed Enhancements & Targeted Fixes

### 3.1 Strict Unique-Name Orchestration (`scraper_tasks.py`)
- **Incremental Real-Time Case Persistence:**
  - After searching Name A on Portal Tab 1, immediately persist extracted `ScrapedCourtCase` records to the database and commit, updating the portal's progress and UI state in real time.
  - Then move to Tab 2 for Name A, search, extract, persist.
  - Continue across all open tabs for Name A.
  - Advance to Name B once all tabs are completed for Name A.
  - After all names are completed, dispatch `evaluate_fuzzy_matches_task` to run the legacy Power Automate fuzzy match cascade and Guidewire integration.

### 3.2 CAPTCHA & Security Block Handling (`base.py`)
- **Full-Page Screenshot Capture:**
  - In `BaseCourtScraper.capture_screenshot_on_error()`, configure `full_page=True` with a 5000ms timeout, falling back gracefully to viewport screenshot if page height computation fails.
  - Ensure screenshots are saved to `.\backend\screenshots` via `StorageService`.
- **Security Block Logging:**
  - Verify that `log_security_block_event()` accurately records timestamp, portal name, page URL, reason, and cooldown period in `.\backend\logs\security_blocks.log`.

### 3.3 Test Harness Hardening (`test_plan_verification.py`)
- Fix `test_queue_runner_progression_and_recovery`:
  - Reset any lingering in-progress claims in the test database before testing queue progression so that available worker slots are guaranteed.
  - Ensure 100% pass rate (282/282 tests) across the entire backend test suite.

### 3.4 Verification of QA Fixes
- Validate that all 8 default portal URLs remain strictly untouched and matching specification.
- Validate that the 4 deprecated fields (`Loss Location City`, `Loss Location County`, `Garaging City`, `Garaging State`) remain absent across all schemas, parsers, and frontend components.
- Validate that `Filing Date` is populated for court cases and renders formatted dates properly.
- Validate that the Anti-Captcha Extension UI tab in Settings displays all 5 steps and functions interactively.

---

## 4. Verification & Validation Plan

### Automated Tests
1. **Full Pytest Suite:**
   ```bash
   cd backend
   .venv\Scripts\pytest --tb=short -q
   ```
   *Target: 282 passed, 0 failed.*
2. **IMP-2026-0912-001 / Prompt 04 Test Suite:**
   ```bash
   cd backend
   .venv\Scripts\pytest tests/test_imp_2026_0912_001.py -v
   ```
   *Target: 14/14 tests passed.*
3. **Backend Linter:**
   ```bash
   cd backend
   .venv\Scripts\ruff check app tests
   ```
   *Target: 0 errors.*
4. **Frontend TypeScript:**
   ```bash
   cd frontend
   npx tsc --noEmit
   ```
   *Target: 0 errors.*
5. **PowerShell AST Syntax:**
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```
   *Target: 0 syntax errors across all scripts.*

### Browser & UI Verification
- Use `browser_subagent` to navigate to `http://localhost:3000/settings`, open the **AntiCaptcha Chrome Extension** tab, inspect all 5 workflow steps, capture a verification screenshot to `implementation_plan/Images/`, and save session recording to `implementation_plan/Recording/`.
- Navigate to `http://localhost:3000/claims/[id]`, inspect the **Scraped Cases** table, verify the `Filing Date` and other columns are properly aligned and displayed.

---

## 5. User Review & Approval Request

> [!IMPORTANT]
> In accordance with the **Universal Engineering Governance Skill (`diagnose-plan-confirm-execute`)**, no source code modifications will take place until you have reviewed and approved this implementation plan.
>
> Please confirm if you approve proceeding with the execution of this plan.
