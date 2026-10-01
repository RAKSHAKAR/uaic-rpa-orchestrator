# UAIC Claim & RPA Orchestrator — Power Automate V4 Exact Parity Implementation Record

> **Implementation ID:** `IMP-2026-0930-004`  
> **Topic:** 100% Exact Behavioral, URL & Object Parity with Power Automate Desktop V4 for Broward County & Florida Portals  
> **Source Reference:** Microsoft Power Automate Desktop V4 Flow (`scripts/extracted_v4_flow.robin`, lines 33, 87–161; `v4_subflows/Subflow_Broward.robin`; V4 ControlRepository `ControlRepository_7bdb415f-2aae-45a6-96a0-7ad7cf77de42.json`)  
> **Document Type:** Implementation Record  
> **Date:** 2026-09-30  
> **Status:** Complete  
> **AI Verification:** Complete (100% Automated Testing Suite)  
> **Human Verification:** Pending Human Verification  
> **Target Files Modified:**  
> - `backend/app/automation/florida/broward.py`  
> - `backend/app/core/config.py`  
> - `backend/app/schemas/settings.py`  
> - `backend/app/services/settings_service.py`  
> - `backend/app/automation/session_runner.py`  
> - `backend/tests/test_broward_portal.py`  
> - `backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py`  
> - `scripts/test_florida_live_nav.py`  

---

## 1. Executive Summary

This implementation record documents the total alignment of the Broward County and Florida court scrapers with Microsoft Power Automate Desktop V4, completely eliminating the root cause of stray visits to `https://www.browardclerk.org/Web2/Services/PremiumServices` and `https://www.browardclerk.org//Web2/CaseSearchECA/Glossary/`.

### Root Cause Analysis & Resolution
1. **Wrong Base URL Eliminated:**
   - **Root Cause:** The scraper previously defaulted to `https://www.browardclerk.org/` (the general county homepage), where the case search form is not present and where links to "Premium Services" and "Glossary" exist.
   - **V4 Reality:** In Power Automate V4 (`LaunchChrome` line 33 and `GoToWebPage` line 143), the exact portal URL is:
     `https://www.browardclerk.org/Web2`
   - **Fix Applied:** Configured `BROWARD_PORTAL_URL = "https://www.browardclerk.org/Web2"` across `broward.py`, `config.py`, `settings.py`, and `settings_service.py` (with automatic DB normalization).
2. **Purged Stray Button Clicking:**
   - **Root Cause:** `navigate_to_search` previously had logic that queried buttons labeled "Case Search" (`.btn-bc-ql-text`, `a:has-text('Case Search')`). In the Broward navigation header, those selectors hit "Premium Services" (`/Web2/Services/PremiumServices`) and "Glossary" (`/Web2/CaseSearchECA/Glossary/`).
   - **V4 Reality:** In `Subflow_Broward.robin` (lines 1–6), V4 **NEVER clicks any "Case Search" button on startup**. Opening `https://www.browardclerk.org/Web2` lands directly on the Case Search page where `#nameSearch`, `#firstName`, `#lastName`, and `#PersonSearchResults` already exist!
   - **Fix Applied:** `BrowardScraper.navigate_to_search` now navigates directly to `https://www.browardclerk.org/Web2` and immediately proceeds to party search without clicking any header links or buttons.
3. **Exact V4 Object Parity:**
   - **Party Name Tab:** `#myTabStandard a[href="#nameSearch"]` (V4 ControlRepository line 20820–20830).
   - **Inputs:** `#firstName`, `#lastName`, `#filingDateOnOrAfterP` (V4 Robin lines 15, 17, 19).
   - **Submit:** `#PersonSearchResults` (V4 Robin line 55).
   - **Clean State Reset:** Direct re-navigation to `https://www.browardclerk.org/Web2` (V4 Robin line 143).

---

## 2. Detailed File Modifications

### 2.1 Broward Scraper (`backend/app/automation/florida/broward.py`)
- Defined canonical constant: `BROWARD_PORTAL_URL = "https://www.browardclerk.org/Web2"`.
- `__init__`: Defaults `base_url` to `BROWARD_PORTAL_URL`. If legacy `https://www.browardclerk.org` without `/Web2` is passed, automatically corrects it to `BROWARD_PORTAL_URL`.
- `navigate_to_search`: Directly opens `https://www.browardclerk.org/Web2`. Completely removed all clicking of `.btn-bc-ql-text` or loose "Case Search" links.
- `select_party_name_tab`: Targets exact V4 object `#myTabStandard a[href="#nameSearch"]`.
- `return_to_search_state`: Direct re-navigation to `https://www.browardclerk.org/Web2`, matching V4 line 143 (`WebAutomation.GoToWebPage Url: 'https://www.browardclerk.org/Web2'`).

### 2.2 System Configuration & Settings
- `backend/app/core/config.py`: Updated `PORTAL_BROWARD_URL = "https://www.browardclerk.org/Web2"`.
- `backend/app/schemas/settings.py`: Updated `PortalsSettings.broward_url = "https://www.browardclerk.org/Web2"`.
- `backend/app/services/settings_service.py`: Added migration rule in `_normalize_portals_data` to automatically convert any stored `"https://www.browardclerk.org/"` to `"https://www.browardclerk.org/Web2"`.
- `backend/app/automation/session_runner.py`: Guarded `portal_key == "broward"` tab creation so it always opens `https://www.browardclerk.org/Web2`.

---

## 3. Automated Test & Verification Report

| Test Suite / Verification Tool | Command | Scope | Result | Status |
|---|---|---|---|---|
| **Florida Portals Test Suite** | `.venv\Scripts\pytest tests/test_broward_portal.py tests/test_miami_portal.py tests/test_hillsborough_portal.py -q` | 39 Florida portal unit & integration tests | **39 passed in 21.45s** | ✅ PASS |
| **Full Backend Test Suite** | `.venv\Scripts\pytest --tb=short -q` | 554 tests across 67 test suites | **554 passed in 8m 02s (100% pass rate)** | ✅ PASS |
| **Python Code Linter** | `.venv\Scripts\ruff check app tests` | Entire backend codebase | **0 errors, all checks passed** | ✅ PASS |
| **Frontend TypeScript Compiler** | `npx tsc --noEmit` | Entire Next.js 14 frontend | **0 errors (Exit code 0)** | ✅ PASS |
| **PowerShell Syntax Validator** | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1` | All 12 `.ps1` repository scripts | **0 syntax errors across all 12 scripts** | ✅ PASS |
| **Live Browser Navigation Test** | `python scripts/test_florida_live_nav.py` | Real headless browser session | **Broward arrived at Web2; all form controls present (#nameSearch, #firstName, #lastName, #PersonSearchResults); 0 visits to PremiumServices or Glossary** | ✅ PASS |
| **Configuration File Integrity** | `git status --short setup_local.ps1 docker-compose.yml` | Dev launcher & Docker Compose | **Both files clean & intact** | ✅ PASS |

---

## 4. Live Verification Log Evidence

```text
=== Testing Florida Scraper Navigation Parity (V4 Exact) ===
Broward configured base: https://www.browardclerk.org/Web2
Miami login URL: https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB
Hillsborough base URL: https://hover.hillsclerk.com/

Testing Broward navigation...
Broward arrived at: https://www.browardclerk.org/Web2
Broward form controls found: #nameSearch(1), #firstName(1), #lastName(1), #PersonSearchResults(1)
  -> Broward navigation: PASS (100% V4 Parity, 0 stray clicks)

Testing Miami login gateway navigation...
Miami arrived at: https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB
Miami login fields verified: userName (1), password (1)
  -> Miami login gateway: PASS

All Florida navigation checks PASSED successfully!
```

---

## 5. Architectural Rule Compliance Checklist

- [x] Python 3.14 runtime compliance preserved
- [x] Portal output schema parity strictly maintained (no schema modifications)
- [x] Exact Power Automate V4 behavioral and object parity enforced
- [x] Zero unapproved loose selectors or stray clicks
- [x] Canonical Broward URL enforced: `https://www.browardclerk.org/Web2`
- [x] All 5 protected directories intact (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`)
- [x] `setup_local.ps1` and `docker-compose.yml` verified intact
- [x] 100% automated test pass rate (554 backend tests, 39 Florida portal tests, 0 lint errors, 0 TS errors, 0 PS1 errors)

---

> **AI Verification:** Complete (100% Automated Testing Suite)
