# Implementation Plan: 04 - Master Scraping Engine, CAPTCHA Compliance & QA Fixes

**Implementation ID:** `IMP-2026-0916-004`  
**Date:** September 16, 2026  
**Status:** Ready for Review  
**Lifecycle Step:** Plan → Confirm  

---

## 1. Goal & Requirements Overview

This plan addresses all requirements from **Prompt 04 — Master Scraping Engine, CAPTCHA Compliance & QA Fixes**:
1. **Strict Unique-Name Orchestration (Mandatory):**
   - Step 1: Execute the New Fuzzy Match API (`generate_unique_names_for_claim`) to derive Unique Names from Insured, Driver, and Claimant fields.
   - Step 2: Open System Google Chrome with the Anti-Captcha extension. Open tabs for all applicable county portals in parallel.
   - Step 3: **Process one unique name at a time:** Search Name A in Portal Tab 1 -> Extract -> Match -> Store; switch to Portal Tab 2 -> Search Name A -> Extract -> Match -> Store; continue across ALL open tabs.
   - Step 4: Only after ALL tabs are searched for Name A, move to Name B.
   - Step 5: After ALL unique names are fully processed across all tabs, execute the legacy Power Automate Fuzzy Match logic (`evaluate_fuzzy_matches_task`) and push to Guidewire Cloud.
2. **CAPTCHA Compliance & Non-Blocking Architecture:**
   - The system must NEVER attempt to bypass, defeat, or spoof reCAPTCHA, Cloudflare, or Arkose Labs.
   - Non-blocking error handling: If blocked (IP/MAC/rate limit), instantly mark portal as `BLOCKED`, capture a full-page screenshot to `backend/screenshots/{claim_id}/{portal}/`, log to `backend/logs/{claim_id}/{portal}/execution.log`, and seamlessly continue processing remaining portals.
   - Automated cooldown tracking with `Retry-After` headers and backoff.
3. **Specific QA Fixes & Form Adjustments:**
   - **Deprecated Fields:** Ensure `Loss Location City`, `Loss Location County`, `Garaging City`, and `Garaging State` are completely absent from New Form, Edit Form, and Data Ingestion Column Mapping.
   - **Default Portal URLs:** Verify all 8 default URLs match exact requirement:
     - Broward: `https://www.browardclerk.org/`
     - Hillsborough: `https://hover.hillsclerk.com/`
     - Miami-Dade: `https://www2.miamidadeclerk.gov/ocs`
     - Travis: `https://odysseyweb.traviscountytx.gov/Portal/`
     - Dallas: `https://courtsportal.dallascounty.org/DALLASPROD/Home/`
     - Harris JP: `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`
     - CClerk: `https://www.cclerk.hctx.net/Applications/WebSearch/`
     - HCDistrict: `https://www.hcdistrictclerk.com/`
   - **Auto Queue:** Enabled by default (`True`).
   - **Filing Date Capture:** Fix missing `Filing Date` capture in Scraped Cases section and ensure `SuitFiledDate` in Guidewire payloads correctly maps `case.get("FilingDate")` with fallback to claim's Date of Loss (`claim.dol`).
   - **Anti-Captcha Extension UI:** Enhance dedicated Extension tab in Automation Settings providing an integrated 3-step test and configuration workflow prior to queue launch.

---

## 2. Gap Analysis & Current System State

| Requirement | Current System State | Action Required |
|---|---|---|
| **1. Unique-Name Sequence** | `scraper_tasks.py` derives unique names and runs outer loop over unique names, inner loop over portal tabs. | Verified working; add comprehensive end-to-end unit test in `test_prompt04_scraping_compliance_and_qa_fixes.py`. |
| **2. Non-blocking CAPTCHA** | `SecurityBlockException` catches blocks, marks `BLOCKED`, logs, captures screenshot, sets cooldown, and continues. | Verified working; add automated regression assertion for block isolation. |
| **3. Deprecated Fields** | `loss_location_city`, `loss_location_county`, `garaging_city`, `garaging_state` removed from forms and ingestion mapping. | Verified clean; add unit test asserting absence from `TARGET_CLAIM_FIELDS`. |
| **4. Default Portal URLs** | Configured in `config.py`, `settings.py`, and `settings_service.py`. | Verified exact match across all 8 URLs. |
| **5. Auto Queue Default** | `queue_runner.py` defaults to `True` on uninitialized Redis key. | Verified; add regression test. |
| **6. Filing Date Capture & Columns** | `guidewire_client.py` checked `case.get("SuitFiledDate") or case.get("filing_date")`, omitting PascalCase `case.get("FilingDate")`, leading to empty `SuitFiledDate`. Also UI table had no `Party Searched` column. | **FIX:** In `guidewire_client.py`, check `case.get("FilingDate")`. In `scraper_tasks.py`, ensure fallback to `claim.dol`. In UI table, add `Party Searched` column and robust date fallback. |
| **7. Anti-Captcha Extension Tab** | Extension tab exists (`id: "extension"`) with pinning, profile setup, and health check. | **ENHANCE:** Add clear 3-step operational readiness banner and test suite verification. |

---

## 3. Proposed Code Changes

### Backend Services & Tasks

#### [MODIFY] [`backend/app/services/guidewire_client.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/guidewire_client.py)
- In `send_case_update`, line 88:
  ```python
  "SuitFiledDate": (
      case.get("SuitFiledDate")
      or case.get("FilingDate")
      or case.get("filing_date")
      or ""
  ),
  ```

#### [MODIFY] [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py)
- When persisting `ScrapedCourtCase` in `_async_execute_claim_scrapers`:
  Ensure `f_date = normalize_court_date(raw_f_date) or (claim.dol if claim else "")` so `ScrapedCourtCase.filing_date` is never null or blank.

#### [MODIFY] [`backend/app/api/v1/endpoints/claims.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/claims.py)
- In `_map_claim_to_response`:
  Ensure fallback includes `claim.dol` if `sc.filing_date` and `raw_payload` dates are empty.

### Frontend Scraped Cases Table

#### [MODIFY] [`frontend/src/app/claims/[id]/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/claims/[id]/page.tsx)
- In Scraped Cases table:
  - Add `Party Searched` column to the table header and body.
  - Fall back to `claim?.dol` for `Filing Date` when portal date is unavailable.
  - Ensure all 7 columns (`Case Number`, `Court / Portal`, `Party Searched`, `Case Style`, `Filing Date`, `Status`, `Type`) render cleanly.

### Testing Suite

#### [NEW] [`backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py)
- Comprehensive automated test suite validating all 8 requirements of Prompt 04:
  1. `test_unique_names_generation_and_order`
  2. `test_guidewire_suit_filed_date_mapping_with_filing_date`
  3. `test_deprecated_fields_completely_absent_from_ingestion`
  4. `test_default_portal_urls_exact_match`
  5. `test_auto_queue_enabled_by_default`
  6. `test_security_block_non_blocking_and_cooldown`
  7. `test_anti_captcha_extension_status_and_pinning`
  8. `test_scraped_case_filing_date_fallback`

---

## 4. Verification Plan

### Automated Tests
1. Run new test suite:
   ```bash
   cd backend
   .venv\Scripts\pytest tests/test_prompt04_scraping_compliance_and_qa_fixes.py -v
   ```
2. Run full test suite:
   ```bash
   .venv\Scripts\pytest --tb=short -q
   ```
3. Run Python code quality check:
   ```bash
   .venv\Scripts\ruff check app tests
   ```
4. Run TypeScript compilation check:
   ```bash
   cd ../frontend
   npx tsc --noEmit
   ```
5. Run PowerShell syntax validator:
   ```bash
   cd ..
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```

### Manual & Visual Verification
1. Inspect `http://localhost:3000/claims/4d6e8f53-f6dc-409f-8413-a9add23d70ac` to verify all Scraped Cases columns (`Case Number`, `Court / Portal`, `Party Searched`, `Case Style`, `Filing Date`, `Status`, `Type`).
2. Inspect `http://localhost:3000/settings` -> `AntiCaptcha Extension` tab to verify extension testing workflow.
