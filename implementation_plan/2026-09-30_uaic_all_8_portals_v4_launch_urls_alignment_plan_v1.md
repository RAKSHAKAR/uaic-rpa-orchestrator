# Implementation Plan: All 8 Court Scraper Bots — Power Automate V4 Launch URLs Alignment

Implementation ID:   IMP-2026-0930-003  
Project:             UAIC Claim & RPA Orchestrator  
Module:              Court Portal Automation Engine & Settings (`backend/app/automation/`, `backend/app/core/`, `backend/app/schemas/`, `backend/app/services/`)  
Feature / Issue:     Match Exact Power Automate V4 Start and Launch URLs Across All 8 Scraper Bots  
Document Type:       Implementation Plan  
Version:             v1  
Status:              Pending Approval  
Created:             2026-09-30  
Last Updated:        2026-09-30  
AI Agent:            Antigravity  
Approval Status:     Pending  
Approved By:         User  
Approval Date:       Pending  
AI Verification:     Pending  

---

## 1. Executive Summary & Objective

The user requested:
> *"all urls must be same as power platform v4 to start and loanuch all 8 bots, pls correct if url is mistmatched"*

In Microsoft Power Automate Desktop V4, the robot opens Google Chrome and prepares all court portal search tabs upfront with specific deep-link search endpoints. A forensic audit of the repository reveals that while some scrapers and `session_runner.py` contain internal redirections, the central system configuration (`backend/app/core/config.py`), settings schema (`backend/app/schemas/settings.py`), database normalization (`backend/app/services/settings_service.py`), and default scraper initializations in `backend/app/automation/` were defaulting to root generic domain paths (e.g. `/Home/` or root `/`) rather than the exact V4 start and launch URLs.

This plan aligns **all 8 court bots** with the authoritative Power Automate Desktop V4 start and launch URLs across configuration, schema, database persistence, session runner tab pre-loading, and individual scraper classes.

---

## 2. Power Automate Desktop V4 Authoritative Baseline

From the extracted Power Automate V4 Desktop Flow (`scripts/extracted_v4_flow.robin`, lines 33–58):

```robin
0033: WebAutomation.LaunchChrome.LaunchChrome Url: $fx'https://www.browardclerk.org/Web2' WindowState: WebAutomation.BrowserWindowState.Maximized ClearCache: False ClearCookies: False WaitForPageToLoadTimeout: $fx'60' Timeout: $fx'60' PiPUserDataFolderMode: WebAutomation.PiPUserDataFolderModeEnum.DefaultProfile TargetDesktop: $fx'{"DisplayName":"Local computer","Route":{"ServerType":"Local","ServerAddress":""},"DesktopType":"local"}' BrowserInstance=> BrowserBroward
0034: WebAutomation.CreateNewTab.CreateNewTab BrowserInstance: $fx'=BrowserBroward' Url: $fx'https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29' WaitForPageToLoadTimeout: $fx'=60' NewBrowserInstance=> BrowserDallas
0038: WebAutomation.CreateNewTab.CreateNewTab BrowserInstance: $fx'=BrowserBroward' Url: $fx'https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29' WaitForPageToLoadTimeout: $fx'=60' NewBrowserInstance=> BrowserTravis
0042: WebAutomation.CreateNewTab.CreateNewTab BrowserInstance: $fx'=BrowserBroward' Url: $fx'https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29' WaitForPageToLoadTimeout: $fx'=60' NewBrowserInstance=> BrowserHarris
0046: WebAutomation.CreateNewTab.CreateNewTab BrowserInstance: $fx'=BrowserBroward' Url: $fx'https://www2.miamidadeclerk.gov/ocs' WaitForPageToLoadTimeout: $fx'=60' NewBrowserInstance=> MiamiBrowser
0050: WebAutomation.CreateNewTab.CreateNewTab BrowserInstance: $fx'=BrowserBroward' Url: $fx'https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx?ID=...' WaitForPageToLoadTimeout: $fx'=60' NewBrowserInstance=> BrowserCclerk
0054: WebAutomation.CreateNewTab.CreateNewTab BrowserInstance: $fx'=BrowserBroward' Url: $fx'https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab' WaitForPageToLoadTimeout: $fx'=60' NewBrowserInstance=> HillsboroughBrowser
0058: WebAutomation.CreateNewTab.CreateNewTab BrowserInstance: $fx'=BrowserBroward' Url: $fx'https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx' WaitForPageToLoadTimeout: $fx'=60' NewBrowserInstance=> HcDistrictBrowser
```

---

## 3. Comprehensive URL Mismatch Audit & Gap Analysis

| Portal Key | Portal Name | Current Default URL in Config / Settings | Exact Power Automate V4 Start & Launch URL | Status | Required Correction |
|---|---|---|---|---|---|
| `broward` | Broward County Clerk (FL) | `https://www.browardclerk.org/Web2` | `https://www.browardclerk.org/Web2` | **Match** | Preserve `https://www.browardclerk.org/Web2`. Normalize any bare `https://www.browardclerk.org/`. |
| `hillsborough` | Hillsborough County Clerk (FL) | `https://hover.hillsclerk.com/` | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` | **MISMATCH** | Update to `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` (matching V4 line 54 and line 169). |
| `miami` | Miami-Dade County Clerk (FL) | `https://www2.miamidadeclerk.gov/ocs` | `https://www2.miamidadeclerk.gov/ocs` | **Match** | Preserve `https://www2.miamidadeclerk.gov/ocs` (with standard login redirection when auth is required). |
| `dallas` | Dallas County Courts (TX) | `https://courtsportal.dallascounty.org/DALLASPROD/Home/` | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` | **MISMATCH** | Update to `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` (matching V4 line 34 and line 471). |
| `travis` | Travis County Odyssey (TX) | `https://odysseyweb.traviscountytx.gov/Portal/` | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` | **MISMATCH** | Update to `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` (matching V4 line 38). |
| `harris_jp` | Harris County JP Courts (TX) | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/` | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` | **MISMATCH** | Update to `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` (matching V4 line 42 and line 829). |
| `harris_cclerk` | Harris County Clerk (TX) | `https://www.cclerk.hctx.net/Applications/WebSearch/` | `https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx` | **MISMATCH** | Update to `https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx` (matching V4 line 50 and canonical `CourtSearch_R.aspx`). |
| `harris_district` | Harris District Clerk (TX) | `https://www.hcdistrictclerk.com/` | `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` | **MISMATCH** | Update to `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` (matching V4 line 58 and `Subflow_HarrisDistrict.robin`). |

---

## 4. Proposed Changes by File

### 1. `backend/app/core/config.py`
Update environment variable defaults:
- `PORTAL_HILLSBOROUGH_URL: str = "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"`
- `PORTAL_TRAVIS_URL: str = "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29"`
- `PORTAL_DALLAS_URL: str = "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"`
- `PORTAL_HARRIS_JP_URL: str = "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"`
- `PORTAL_HARRIS_CCLERK_URL: str = "https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx"`
- `PORTAL_HARRIS_DISTRICT_URL: str = "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"`

### 2. `backend/app/schemas/settings.py`
Update `PortalsSettings` pydantic model defaults:
- `hillsborough_url: str = Field(default="https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab", ...)`
- `travis_url: str = Field(default="https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29", ...)`
- `dallas_url: str = Field(default="https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29", ...)`
- `harris_jp_url: str = Field(default="https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29", ...)`
- `harris_cclerk_url: str = Field(default="https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx", ...)`
- `harris_district_url: str = Field(default="https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx", ...)`

### 3. `backend/app/services/settings_service.py`
- Update `_normalize_portals_data`: Auto-migrate any existing records in SQLite/Postgres from old generic URLs (e.g. `https://hover.hillsclerk.com/`, `https://courtsportal.dallascounty.org/DALLASPROD/Home/`, `https://odysseyweb.traviscountytx.gov/Portal/`, `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`, `https://www.cclerk.hctx.net/Applications/WebSearch/`, `https://www.hcdistrictclerk.com/`) to their exact V4 start and launch targets.
- Update default settings factory `get_default_settings()`.

### 4. Scraper Automation Classes (`backend/app/automation/`)
Update default `base_url` values in class `__init__`:
- `florida/hillsborough.py`: `base_url=base_url or "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"`
- `texas/dallas.py`: `base_url=base_url or "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"`
- `texas/travis.py`: `base_url=base_url or "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29"`
- `texas/harris_jp.py`: `base_url=base_url or "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"`
- `texas/harris_cclerk.py`: `base_url=base_url or "https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx"`
- `texas/harris_district.py`: `base_url=base_url or "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"`

### 5. `backend/app/automation/session_runner.py`
Verify that `get_or_create_tab` and `execute_portal_searches` dispatch exact V4 URLs when opening or resetting tabs.

### 6. Test Suite Updates
- `backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py`: Update `test_p4_004_exact_default_portal_urls` to assert the authoritative V4 launch URLs.
- `backend/tests/test_plan_verification.py`: Update `test_hillsborough_scraper_initialization_and_selectors` line 783 to assert `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab`.

---

## 5. Verification Strategy & Acceptance Criteria

1. **Automated Unit & Portal Testing**:
   - `pytest tests/test_*_portal.py tests/test_scraper_captcha_behavior.py` (120/120 passing).
   - Full test suite: `pytest --tb=short -q` (554/554 passing, 100%).
2. **Static Quality Gates**:
   - `ruff check app tests` (0 errors).
   - `cd frontend && npx tsc --noEmit` (0 errors).
   - `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/check_ps1_syntax.ps1"` (0 errors).
   - `docker compose config --quiet` (valid syntax).
3. **Execution Verification**:
   - Verify all 8 bots launch and start on the exact Power Automate V4 URLs.
