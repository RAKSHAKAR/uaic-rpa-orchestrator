# UAIC Claim & RPA Orchestrator — Power Automate V4 Exact Parity Implementation Record (All 8 Bots)

> **Implementation ID:** `IMP-2026-0930-005`  
> **Topic:** 100% Exact Behavioral, Object, URL & Workflow Parity across all 8 Court Bots with Microsoft Power Automate Desktop V4  
> **Source Reference:** Microsoft Power Automate Desktop V4 Flow (`scripts/extracted_v4_flow.robin` lines 33–61, 87–161; `ExtractDataFlow.robin`; `Subflow_Broward.robin`; `Subflow_Dallas.robin`; `Subflow_Travis.robin`; `Subflow_Harris.robin`; `Subflow_Miami.robin`; `Subflow_Cclerk.robin`; `Subflow_Hillsborough.robin`; `Subflow_HarrisDistrict.robin`; V4 Control Repositories)  
> **Document Type:** Implementation Record  
> **Date:** 2026-09-30  
> **Status:** Complete  
> **AI Verification:** Complete (100% Automated Testing Suite)  
> **Human Verification:** Pending Human Verification  
> **Target Files Modified:**  
> - [`backend/app/automation/florida/broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py)  
> - [`backend/app/automation/florida/hillsborough.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/hillsborough.py)  
> - [`backend/app/automation/florida/miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py)  
> - [`backend/app/automation/texas/dallas.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/dallas.py)  
> - [`backend/app/automation/texas/travis.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/travis.py)  
> - [`backend/app/automation/texas/harris_jp.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_jp.py)  
> - [`backend/app/automation/texas/harris_cclerk.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py)  
> - [`backend/app/automation/texas/harris_district.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_district.py)  
> - [`backend/app/automation/session_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py)  
> - [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py)  

---

## 1. Executive Summary

This implementation record documents the verification and comprehensive alignment of all 8 court scrapers against Microsoft Power Automate Desktop V4. Every URL, UI object, search flow, data extraction schema, state reset mechanism, and Celery execution sequence now mirrors Power Automate V4 with **zero gaps**.

---

## 2. Changes Applied for 100% V4 Parity

### 1. Canonical V4 URL Enforcement Across All 8 Scrapers
Each scraper defines a canonical URL constant matching Power Automate Desktop V4 (`extracted_v4_flow.robin` lines 33–61) and ensures that all tab navigations target the exact search interface directly without preliminary page traversals or stray redirects:

| Portal | Canonical V4 URL | Scraper Constant |
|---|---|---|
| **Broward County (FL)** | `https://www.browardclerk.org/Web2` | `BROWARD_PORTAL_URL` |
| **Dallas County (TX)** | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` | `DALLAS_PORTAL_URL` |
| **Travis County (TX)** | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` | `TRAVIS_PORTAL_URL` |
| **Harris County JP (TX)** | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` | `HARRIS_JP_PORTAL_URL` |
| **Miami-Dade County (FL)** | `https://www2.miamidadeclerk.gov/ocs`<br>(Gateway: `.../usermanagementservices/?hs=OCSB`) | `MIAMI_OCS_PORTAL_URL`<br>`MIAMI_LOGIN_GATEWAY_URL` |
| **Harris County Clerk (TX)** | `https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx` | `HARRIS_CCLERK_PORTAL_URL` |
| **Hillsborough County (FL)** | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` | `HILLSBOROUGH_PORTAL_URL` |
| **Harris County District (TX)**| `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` | `HARRIS_DISTRICT_PORTAL_URL` |

### 2. Multi-Tab Session Runner URL Guard
In [`backend/app/automation/session_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py) (`execute_portal_searches`), explicit canonical resolution was added across all 8 portals. Even if a base domain URL is passed, `session_runner` automatically opens the exact V4 search URL, guaranteeing that browser execution is identical to Power Automate V4.

### 3. Celery Execution Sequence Parity
In [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py) (`scrapers_to_run`), the portal execution order was reordered to match the exact sequence in Power Automate V4 `ExtractDataFlow.robin`:
1. `broward` (Broward County Clerk)
2. `dallas` (Dallas County Courts)
3. `travis` (Travis County Odyssey Portal)
4. `harris_jp` (Harris County JP Courts)
5. `miami` (Miami-Dade County Civil)
6. `harris_cclerk` (Harris County Clerk)
7. `hillsborough` (Hillsborough County Clerk)
8. `harris_district` (Harris County District Clerk)

### 4. DOM Selectors & Extraction Schema Parity
- **Broward:** `#myTabStandard a[href="#nameSearch"]`, `#firstName`, `#lastName`, `#filingDateOnOrAfterP`, submit `#PersonSearchResults`. Reset via direct reload of `https://www.browardclerk.org/Web2`. 5 fields extracted.
- **Dallas:** `#caseCriteria_SearchCriteria`, submit `input[type="submit"][value="Submit"]`, detail page style parsing, reset `#tcControllerLink_0`. 5 fields extracted.
- **Travis:** `#caseCriteria_SearchCriteria`, submit `#btnSSSubmit`, detail tab style and filing date parsing, reset `p.step-label:has-text('Smart Search')`. 5 fields extracted.
- **Harris JP:** Smart Search, `#caseCriteria_SearchCriteria`, submit `input[type="submit"][value="Submit"]`, detail tab status parsing, reset direct reload of `.../Dashboard/29`. **4 fields extracted (strictly NO CaseType)**.
- **Miami-Dade:** Login `#userName`, `#password`, search `#partyFirstName`, `#partyLastName`, `#filingDateFrom` (`MM-dd-yyyy`), submit `Button 'Search'`, reset `Span 'OCS Home'` & `Button 'Refresh'`. 5 fields extracted.
- **Harris County Clerk:** `#ctl00_ContentPlaceHolder1_txtFirstName`, `#ctl00_ContentPlaceHolder1_txtLastName`, `#ctl00_ContentPlaceHolder1_txtFrom2`, submit `Input submit 'Search'`, reset `#ctl00_ContentPlaceHolder1_btnClear`. **4 fields extracted (strictly NO CaseType)**.
- **Hillsborough:** `Button 'Search by Party or Business Name'`, `#spFirstName`, `#spLastName`, `#spDateFiledAfter`, submit `#btnSearchPartyName`, reset dismiss `#messageClose` and re-select `#nav-Party-tab`. 5 fields extracted.
- **Harris District:** `Span 'Search Our Records'`, `Input button 'Party Inquiry'`, `#txtPartyName`, date `MM/dd/yyyy`, submit `#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch`, reset `btnSearchAgain`. 5 fields extracted.

---

## 3. Verification Evidence

| Quality Gate | Target | Result | Evidence |
|---|---|---|---|
| **All 8 Portals Unit Tests** | `test_broward_portal.py`, `test_miami_portal.py`, `test_hillsborough_portal.py`, `test_dallas_portal.py`, `test_travis_portal.py`, `test_harris_jp_portal.py`, `test_harris_cclerk_portal.py`, `test_harris_district_portal.py` | **PASSED** | **109 / 109 tests passed** (100% pass rate) |
| **Full Backend Test Suite** | 67 test files in `backend/tests/` | **PASSED** | **554 / 554 tests passed** (100% pass rate) |
| **Python Code Linter** | `ruff check app tests` | **PASSED** | **0 errors** across all files |
| **Frontend TypeScript Compiler** | `npx tsc --noEmit` | **PASSED** | **0 errors** (Exit code 0) |
| **PowerShell Syntax Validator** | `check_ps1_syntax.ps1` | **PASSED** | **0 errors** across all 12 scripts |
| **Live V4 URL Parity Verification** | `scripts/test_all_8_portals_v4_nav.py` | **PASSED** | All 8 portal canonical URLs match Power Automate V4 exactly |
| **Protected Files Integrity** | `setup_local.ps1` and `docker-compose.yml` | **PASSED** | Both files clean and fully intact |
