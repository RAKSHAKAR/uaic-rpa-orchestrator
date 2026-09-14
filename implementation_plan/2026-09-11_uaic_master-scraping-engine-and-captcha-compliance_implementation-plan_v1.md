# Implementation Plan — IMP-2026-0911-002

**Implementation ID:** IMP-2026-0911-002  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Scraping Engine, Human-Like Navigation, CAPTCHA Compliance, Settings & QA Adjustments  
**Feature / Issue:** Master Scraping Engine, CAPTCHA Compliance & Form Adjustments (Prompt 04)  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**Created:** 2026-09-11  
**AI Agent:** Antigravity  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Problem / Request Summary

The user provided prompt `# 04 - MASTER SCRAPING ENGINE, HUMAN-LIKE NAVIGATION & CAPTCHA COMPLIANCE` with 3 core pillars:
1. **Strict Unique-Name Orchestration (Mandatory Sequence):**
   - Generate unique names from Insured, Driver, Claimant fields.
   - Open default browser (Chrome/Edge/Chromium) with Anti-Captcha extension loaded and open tabs for all applicable portals based on routing rules (FL: Broward, Hillsborough, Miami; TX: Travis, Dallas, Harris JP, CClerk, HCDistrict; Cross-State: All 8).
   - Process ONE unique name at a time sequentially across all open tabs: fill fields, detect/wait for CAPTCHA resolution, click search only after verification, wait for results, extract all cases (pagination), match against original claim data, store results.
   - Only after all tabs searched for Name A, proceed to Name B.
   - After all names are processed, execute legacy Power Automate fuzzy match logic.
   - Send result to Guidewire integration payload.
   - Maintain detailed audit logs, correlation IDs, and telemetry.
2. **CAPTCHA Compliance, Security Handling & Non-Blocking Architecture:**
   - Zero circumvention / spoofing of reCAPTCHA, Cloudflare, Arkose.
   - Pause in attended mode or allow authorized human solving.
   - Non-blocking error handling: if blocked, mark "Failed/Blocked", screenshot to `backend/screenshots`, log, and continue remaining portals/claims.
   - Cooldown and automated retries.
3. **Specific QA Fixes & Form Adjustments:**
   - Remove fields `Loss Location City`, `Loss Location County`, `Garaging City`, `Garaging State` from New Form, Edit Form, and Data Ingestion Column Mapping.
   - Default Portal URLs: Broward (`https://www.browardclerk.org/`), Hillsborough (`https://hover.hillsclerk.com/`), Miami-Dade (`https://www2.miamidadeclerk.gov/ocs`), Travis (`https://odysseyweb.traviscountytx.gov/Portal/`), Dallas (`https://courtsportal.dallascounty.org/DALLASPROD/Home/`), Harris JP (`https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`), CClerk (`https://www.cclerk.hctx.net/Applications/WebSearch/`), HCDistrict (`https://www.hcdistrictclerk.com/`).
   - Auto Queue enabled by default.
   - Filing Date capture in Scraped Cases section.
   - Anti-Captcha Extension UI tab in Automation Settings.

---

## 2. Existing State & Gap Analysis

A comprehensive automated audit (214 backend tests, TypeScript verification, and code inspection) was conducted:

| Item | Expected State | Current State | Status / Gap |
|------|---------------|---------------|--------------|
| **Unique Name Derivation** | Deduplicated names from Insured, Driver, Claimant | `derive_search_counts()` + `get_search_party_pairs()` in `session_runner.py` | ✅ Fully Implemented |
| **Name-First Loop Order** | Outer = Unique Names, Inner = Applicable Portals | `scraper_tasks.py` lines 189–260 runs `for party in party_pairs:` -> `for scraper in scrapers_to_run:` | ✅ Fully Implemented |
| **Browser Pre-Opening** | Tabs pre-opened in single browser session | `SingleSessionBrowserRunner` pre-opens tabs with Anti-Captcha | ✅ Fully Implemented |
| **Non-Circumvention CAPTCHA** | Extension-based solving, token verification, human fallback | `BaseCourtScraper.detect_and_handle_captcha()` verifies tokens and avoids premature clicks | ✅ Fully Implemented |
| **Non-Blocking On Block** | Screenshot on error, log, proceed to remaining | `scraper_tasks.py` catches portal exceptions, takes full-page screenshot into `backend/screenshots`, records to `ErrorScreenshot` model | ✅ Fully Implemented |
| **Auto Queue Default** | Enabled by default (`True`) | `queue_runner.py` line 34: `AUTO_QUEUE_ENABLED_DEFAULT = True` | ✅ Fully Implemented |
| **Anti-Captcha Extension UI** | Dedicated tab in Automation Settings | Tab `extension` with 5-step workflow in `settings/page.tsx` | ✅ Fully Implemented |
| **Deprecated Field Removal** | Removed from forms & column mapping | Removed from frontend forms, `TARGET_CLAIM_FIELDS`, and `ClaimRowSchema` | ⚠️ Minor: Remove unused types in `LiveQueueItem` (`index.ts`) |
| **Default Portal URLs** | 8 exact home URLs | Updated in `settings_service.py`, but **`schemas/settings.py` still has legacy URLs** in `PortalsSettings` | ❌ **GAP:** Align `schemas/settings.py` defaults |
| **Filing Date Display** | Visible in Scraped Cases table & modal | Captured in scrapers and table; **modal view lacks fallback cascade, `formatDate` has potential timezone shift** | ❌ **GAP:** Harden `formatDate` & modal fallback in `claims/[id]/page.tsx` |

---

## 3. Scope of Changes

### Backend — `backend/app/`
- **`schemas/settings.py` [MODIFY]:** Update default field values in `PortalsSettings` to the exact 8 URLs specified in Prompt 04.
- **`tasks/scraper_tasks.py` [MODIFY]:** Harden `f_date` key resolution in `_async_orchestrate_scrapers` to cover all field variations (`FilingDate`, `filing_date`, `Filing Date`, `SuitFiledDate`, `suit_filed_date`, `filed_date`, `DateFiled`, `date_filed`).

### Frontend — `frontend/src/`
- **`types/index.ts` [MODIFY]:** Remove obsolete `loss_location_city?: string;` and `loss_location_county?: string;` from `LiveQueueItem`.
- **`app/claims/[id]/page.tsx` [MODIFY]:** 
  - Harden `formatDate` to avoid UTC timezone shifts and safely handle non-standard date formats without outputting `"Invalid Date"`.
  - Add fallback cascade to the Case Details Modal for `Filing Date`: `courtCase.filing_date || courtCase.raw_payload?.FilingDate || courtCase.raw_payload?.filing_date || courtCase.raw_payload?.SuitFiledDate`.

### Tests — `backend/tests/`
- **`tests/test_imp_2026_0911_002.py` [NEW]:** Comprehensive automated regression test suite covering:
  - Exact 8 Portal URLs in `PortalsSettings` defaults and `reset_system_settings_async()`.
  - Name-first unique party derivation across all 5 Dual/Triple search scenarios.
  - Filing date fallback cascade logic.
  - Non-blocking error handling and screenshot capture verification.
  - Absence of deprecated fields from active schemas.

---

## 4. Verification Plan

1. **Backend Tests:** Run `pytest tests/test_imp_2026_0911_002.py` and verify all tests pass.
2. **Full Test Suite:** Run `pytest --tb=short -q` (zero failures).
3. **Backend Lint:** Run `ruff check app tests` (zero errors).
4. **Frontend Type Check:** Run `npx tsc --noEmit` (zero errors).
5. **PowerShell Syntax:** Run `scripts\check_ps1_syntax.ps1` (zero errors).
6. **Documentation:** Update README and generate Walkthrough and Implementation Record.
