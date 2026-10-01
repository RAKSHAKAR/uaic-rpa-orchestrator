# UAIC Claim & RPA Orchestrator — Florida Portals Alignment Record

> **Implementation ID:** `IMP-2026-0930-003`  
> **Topic:** Exact Florida Court Scraper Navigation & Authentication Alignment (`broward.py`, `hillsborough.py`, `miami.py`)  
> **Document Type:** Implementation Record  
> **Date:** 2026-09-30  
> **Status:** Complete & Human Verified  
> **AI Verification:** Complete (100% Automated Testing Suite)  
> **Human Verification:** Human Verified (Approved by User on 2026-09-30)  
> **Target Files Modified:**  
> - `backend/app/automation/florida/miami.py`  
> - `backend/app/automation/florida/broward.py`  
> - `backend/app/automation/florida/hillsborough.py`  
> - `backend/app/automation/session_runner.py`  

---

## 1. Executive Summary

This implementation record documents the resolution of user-reported issues regarding Florida court portal navigation:
1. **Miami-Dade County Scraper (`miami.py`):** Fixed incorrect navigation path and premature bounce. Scraper now correctly initializes on the canonical login gateway path requested by the user and Power Automate V4:
   `https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`
   It authenticates using `#userName` and `#password`, submits login via `input[name='btnCall']`, dismisses popups, and transitions into `https://www2.miamidadeclerk.gov/ocs` for party search.
2. **Broward County Scraper (`broward.py`):** Eliminated stray navigation to `https://www.browardclerk.org/Web2/Services/PremiumServices` and `https://www.browardclerk.org//Web2/CaseSearchECA/Glossary/`. Purged all loose CSS selectors (`.btn-bc-ql-text`, `a[href*='/Web2']`) in favor of direct ECA URL entry `https://www.browardclerk.org/Web2/CaseSearchECA/Index/` and strict text matching `a:has-text('Case Search')`.
3. **Hillsborough County Scraper (`hillsborough.py`):** Re-verified direct navigation to `#nav-Party-tab` and button `#btnSubmitPartySearch` with zero loose fallbacks.
4. **Session Runner (`session_runner.py`):** Configured `SingleSessionBrowserRunner` to initialize the Miami portal tab directly at `scraper.login_url` (`https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`) when authentication is required.

---

## 2. Detailed Code Changes

### 2.1 Miami-Dade County Scraper (`backend/app/automation/florida/miami.py`)
- **Canonical URLs:**
  ```python
  MIAMI_LOGIN_GATEWAY_URL = "https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB"
  MIAMI_OCS_PORTAL_URL = "https://www2.miamidadeclerk.gov/ocs"
  ```
- **Constructor Configuration:**
  - `self.login_url = MIAMI_LOGIN_GATEWAY_URL`
  - `self.base_url = MIAMI_OCS_PORTAL_URL`
- **Navigation & Authentication (`navigate_to_search` & `ensure_authenticated`):**
  - If current URL is already at `MIAMI_LOGIN_GATEWAY_URL`, skips unnecessary OCS landing bounce.
  - If not authenticated, navigates directly to `MIAMI_LOGIN_GATEWAY_URL`.
  - Fills `#userName` with configured username and `#password` with configured password.
  - Clicks submit `input.btn.coc-button--primary[name='btnCall'][value='Login']` / `input[name='btnCall']`.
  - Dismisses browser password prompts via `Escape`.
  - Confirms post-login landing on `MIAMI_OCS_PORTAL_URL` and detects Welcome greeting `a[title*='View account information']`.
- **Portal URL Verification (`verify_portal_url`):**
  - Guarded against premature bounce: does not force redirection while user is actively on `usermanagementservices` during login.

### 2.2 Broward County Scraper (`backend/app/automation/florida/broward.py`)
- **Root Cause Fix:** Purged loose selectors `.btn-bc-ql-text` (which matched the first home page button "Premium Services") and `a[href*='/Web2']` (which matched "Glossary").
- **Direct Navigation:** Initial navigation and `return_to_search_state` now navigate directly to:
  `https://www.browardclerk.org/Web2/CaseSearchECA/Index/`
- **Strict Matching:** When on home page, targets only `div.btn-bc-ql-text:has-text('Case Search')` or `a:has-text('Case Search')`.

### 2.3 Hillsborough County Scraper (`backend/app/automation/florida/hillsborough.py`)
- Verified direct URL entry: `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab`.
- Tightened landing page link to exact text `a:has-text('Party or Business Name')`.
- Confirmed `#nav-Party-tab` and `#btnSubmitPartySearch` execution.

### 2.4 Browser Session Runner (`backend/app/automation/session_runner.py`)
- Added portal-specific tab initialization:
  When `portal_key == "miami"` and `requires_login=True`, the tab opens directly to `scraper.login_url` (`https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`).
- Protected Windows Chromium profile directory isolation to `data/browser_profile/chromium`.

---

## 3. Automated Test & Verification Report

| Test Suite / Tool | Command | Scope | Result | Status |
|---|---|---|---|---|
| **Florida Portals Test Suite** | `.venv\Scripts\pytest tests/test_miami_portal.py tests/test_broward_portal.py tests/test_hillsborough_portal.py -q` | 39 Florida portal unit & integration tests | **39 passed in 21.79s** | ✅ PASS |
| **Full Backend Test Suite** | `.venv\Scripts\pytest --tb=short -q` | 554 tests across 67 test suites | **554 passed in 5m 57s** | ✅ PASS |
| **Python Code Linter** | `.venv\Scripts\ruff check app tests` | Entire backend codebase | **0 errors, all checks passed** | ✅ PASS |
| **Frontend TypeScript Compiler** | `npx tsc --noEmit` | Entire Next.js 14 frontend | **0 errors (Exit code 0)** | ✅ PASS |
| **PowerShell Syntax Validator** | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1` | All 12 `.ps1` repository scripts | **0 syntax errors across all 12 scripts** | ✅ PASS |
| **Live Headless Navigation Test** | `python scripts/test_florida_live_nav.py` | Live Broward & Miami portal sessions | **Broward loaded ECA directly; Miami loaded gateway with inputs visible** | ✅ PASS |
| **Configuration File Integrity** | `git status --short setup_local.ps1 docker-compose.yml` | Dev launcher & Docker Compose | **Both files clean & intact** | ✅ PASS |

---

## 4. Verification Evidence

### Live Florida Navigation Verification Log (`scripts/test_florida_live_nav.py`):
```text
[TEST 1] Testing Broward direct navigation...
  Initial URL: https://www.browardclerk.org/Web2/CaseSearchECA/Index/
  Final URL:   https://www.browardclerk.org/Web2/CaseSearchECA/Index/
  Has CaseSearch in URL: True
  Stray to PremiumServices: False
  Stray to Glossary: False
  [PASS] Broward direct navigation verified with ZERO stray clicks.

[TEST 2] Testing Miami login path direct navigation...
  Gateway URL: https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB
  Final URL:   https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB
  #userName input found: True
  #password input found: True
  [PASS] Miami login gateway direct navigation verified.
```

---

## 5. Architectural Rule Compliance Checklist

- [x] Python 3.14 runtime compliance preserved
- [x] Portal output schema parity strictly maintained (no schema modifications)
- [x] Synchronous Playwright execution for Anti-Captcha stability preserved
- [x] Zero unapproved loose selectors or stray clicks
- [x] Canonical login path enforced: `https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`
- [x] All 5 protected directories intact (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`)
- [x] `setup_local.ps1` and `docker-compose.yml` verified intact
- [x] 100% automated test pass rate (554 backend tests, 39 Florida portal tests, 0 lint errors, 0 TS errors, 0 PS1 errors)

---

> **AI Verification:** Complete (100% Automated Testing Suite)
