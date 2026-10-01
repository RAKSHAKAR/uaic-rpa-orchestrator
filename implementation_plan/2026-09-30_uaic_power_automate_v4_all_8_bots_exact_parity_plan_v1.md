# UAIC Claim & RPA Orchestrator — Power Automate V4 Exact Parity Plan (All 8 Bots)

> **Implementation ID:** `IMP-2026-0930-005`  
> **Topic:** 100% Exact Behavioral, Object, URL & Workflow Parity across all 8 Court Bots with Microsoft Power Automate Desktop V4  
> **Source Reference:** Microsoft Power Automate Desktop V4 Flow (`scripts/extracted_v4_flow.robin` lines 33–61, 87–161; `ExtractDataFlow.robin`; `Subflow_Broward.robin`; `Subflow_Dallas.robin`; `Subflow_Travis.robin`; `Subflow_Harris.robin`; `Subflow_Miami.robin`; `Subflow_Cclerk.robin`; `Subflow_Hillsborough.robin`; `Subflow_HarrisDistrict.robin`; V4 Control Repositories)  
> **Document Type:** Implementation Plan  
> **Date:** 2026-09-30  
> **Status:** Approved & Executed  
> **Implementation Record:** [`2026-09-30_uaic_power_automate_v4_all_8_bots_exact_parity_implementation-record_v1.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-30_uaic_power_automate_v4_all_8_bots_exact_parity_implementation-record_v1.md)  
> **Target Files:**  
> - `backend/app/automation/florida/broward.py`  
> - `backend/app/automation/florida/hillsborough.py`  
> - `backend/app/automation/florida/miami.py`  
> - `backend/app/automation/texas/dallas.py`  
> - `backend/app/automation/texas/travis.py`  
> - `backend/app/automation/texas/harris_jp.py`  
> - `backend/app/automation/texas/harris_cclerk.py`  
> - `backend/app/automation/texas/harris_district.py`  
> - `backend/app/automation/session_runner.py`  
> - `backend/app/tasks/scraper_tasks.py`  
> - `backend/app/services/settings_service.py`  
> - `backend/app/schemas/settings.py`  
> - `backend/app/core/config.py`  

---

## 1. Executive Summary & Objective

The user has explicitly mandated:
> *"pls make sure all the 8 bots must be exactly same as we have in power automate solution v4. Note: I don't want a single or small gap in between powerautomate v4 and this solution. i need exact same solution as we have in power automate solution v4"*

To achieve **zero gaps** between the Python RPA solution and Microsoft Power Automate Desktop V4, we conducted an exhaustive extraction and line-by-line audit of all 8 subflows, the `ExtractDataFlow.robin` main loop, and all 3 V4 Control Repository databases (`ControlRepository_5afd2566-e252-4f66-a3a6-1e9e9270b55c.json`, `ControlRepository_104c291e-5233-425c-bde4-e4db1c27a012.json`, `ControlRepository_7bdb415f-2aae-45a6-96a0-7ad7cf77de42.json`).

This plan aligns:
1. **Exact Canonical Launch & Search URLs for all 8 portals.**
2. **Exact DOM Selectors & JavaScript Execution matching V4.**
3. **Exact V4 Field Extraction Schemas** (Strict 4 fields for Harris JP and Harris Clerk; 5 fields for the remaining 6).
4. **Exact V4 Reset Actions** between unique party search iterations.
5. **Exact V4 Execution Sequence** (Broward -> Dallas -> Travis -> Harris JP -> Miami -> Harris CClerk -> Hillsborough -> Harris District).

---

## 2. Comprehensive 8-Bot V4 Parity Matrix

| # | County & State | V4 Exact Canonical URL | V4 Search Form Controls | V4 Submit Action | Output Schema | V4 Clean State Reset |
|---|---|---|---|---|---|---|
| 1 | **Broward (FL)** | `https://www.browardclerk.org/Web2` | `#myTabStandard a[href="#nameSearch"]`<br>`#firstName`, `#lastName`, `#filingDateOnOrAfterP` | `#PersonSearchResults` (JS click) | **5 fields:**<br>CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType | `GoToWebPage https://www.browardclerk.org/Web2` |
| 2 | **Dallas (TX)** | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` | `#tcControllerLink_0`<br>`#caseCriteria_SearchCriteria` (`LastName,FirstName`) | `input[type="submit"][value="Submit"]` | **5 fields:**<br>CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType (with detail tab CaseStyle parsing) | `GoToWebPage .../Dashboard/29`<br>`#tcControllerLink_0.click()` |
| 3 | **Travis (TX)** | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` | `#caseCriteria_SearchCriteria` (`LastName,FirstName`) | `#btnSSSubmit` (JS click) | **5 fields:**<br>CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType (with detail tab style/date parsing) | `Clear input`<br>`p.step-label:has-text('Smart Search').click()` |
| 4 | **Harris JP (TX)** | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` | Click Smart Search<br>`#caseCriteria_SearchCriteria` (`LastName,FirstName`) | `input[type="submit"][value="Submit"]` | **4 fields (NO CaseType):**<br>CaseNumber, CaseStyle, FilingDate, CaseStatus (with detail tab status parsing) | `GoToWebPage .../Dashboard/29` |
| 5 | **Miami-Dade (FL)** | `https://www2.miamidadeclerk.gov/ocs`<br>Login: `.../usermanagementservices/?hs=OCSB` | Auth: `#userName`, `#password`, Login button.<br>Search: `#partyFirstName`, `#partyLastName`, `#filingDateFrom` (`MM-dd-yyyy`) | `Button 'Search'` | **5 fields:**<br>CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType | Click `Span 'OCS Home'` & `Button 'Refresh'` |
| 6 | **Harris County Clerk (TX)** | `https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx` | `#ctl00_ContentPlaceHolder1_txtFirstName`<br>`#ctl00_ContentPlaceHolder1_txtLastName`<br>`#ctl00_ContentPlaceHolder1_txtFrom2` | `Input submit 'Search'` | **4 fields (NO CaseType):**<br>CaseNumber, CaseStyle, FilingDate, CaseStatus | Click `Input submit 'Clear'` (`#ctl00_ContentPlaceHolder1_btnClear`) |
| 7 | **Hillsborough (FL)** | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` | `Button 'Search by Party or Business Name'`<br>`#spFirstName`, `#spLastName`, `#spDateFiledAfter` | `#btnSearchPartyName` | **5 fields:**<br>CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType | Dismiss `#messageClose`<br>`GoToWebPage ...caseSearch.html#nav-Party-tab` |
| 8 | **Harris District (TX)** | `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` | `Span 'Search Our Records'`, `Input button 'Party Inquiry'`<br>`#txtPartyName` (`LastName, FirstName`)<br>`Edit 'Filed Date Range: (mm/dd/yyyy)'` | `#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch` | **5 fields:**<br>CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType | Click `btnSearchAgain` (`#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnSearchAgain`) |

---

## 3. Specific Gaps Identified & Detailed Resolution Plan

### Gap 1: URL Normalization & Scraper Default Parity
- **Issue:** Several scrapers (`hillsborough.py`, `dallas.py`, `travis.py`, `harris_jp.py`, `harris_cclerk.py`, `harris_district.py`) currently default `base_url` to domain roots (e.g. `https://courtsportal.dallascounty.org/DALLASPROD/Home/` or `https://www.hcdistrictclerk.com/`), requiring preliminary clicks or multi-step redirects on initial page load.
- **Fix:** Update all 8 scraper constructors and URL resolvers in `session_runner.py` so they default to the exact V4 canonical URLs above.
- **Database & Settings Parity:** Update `_normalize_portals_data` in `backend/app/services/settings_service.py` and `PortalsSettings` in `backend/app/schemas/settings.py` to auto-migrate any saved records to these canonical URLs.

### Gap 2: SingleSessionBrowserRunner Tab Initialization Parity
- **Issue:** In `backend/app/automation/session_runner.py` line 579, `execute_portal_searches` only had explicit canonical URL overrides for `broward` and `miami`.
- **Fix:** Expand `session_runner.py` to verify and enforce canonical V4 URLs across all 8 portals whenever initializing or switching tabs.

### Gap 3: Execution Order Parity in Celery Scraper Dispatch
- **Issue:** In `backend/app/tasks/scraper_tasks.py` lines 300–314, `scrapers_to_run` was ordered by state (Broward -> Hillsborough -> Miami -> Dallas -> Travis -> Harris JP -> Harris CClerk -> Harris District).
- **V4 Reality:** In Power Automate Desktop V4 `ExtractDataFlow.robin`, the execution sequence is explicitly:
  1. `broward`
  2. `dallas`
  3. `travis`
  4. `harris_jp`
  5. `miami`
  6. `harris_cclerk`
  7. `hillsborough`
  8. `harris_district`
- **Fix:** Reorder `scrapers_to_run` in `scraper_tasks.py` to match the exact V4 sequence.

### Gap 4: Object & Action Verification for Each Scraper
- **Travis:** Ensure `#btnSSSubmit` is the primary click target matching V4 line 37.
- **Harris District:** Confirm date entry uses format `MM/dd/yyyy` and reset clicks `#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnSearchAgain` (V4 line 93).
- **Harris County Clerk:** Confirm `#ctl00_ContentPlaceHolder1_btnClear` is clicked for reset (V4 line 65) and output strictly omits `CaseType`.
- **Harris JP:** Confirm reset navigates to `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` (V4 line 480) and output strictly omits `CaseType`.
- **Dallas:** Confirm `#tcControllerLink_0` is clicked on reset (V4 line 139).
- **Hillsborough:** Confirm `#messageClose` is clicked if no records, and reset re-selects `#nav-Party-tab` (V4 lines 133, 169).

---

## 4. Verification & Testing Strategy

1. **Unit & Scraper Tests:**
   - Execute all portal test suites:
     `pytest tests/test_broward_portal.py tests/test_miami_portal.py tests/test_hillsborough_portal.py tests/test_dallas_portal.py tests/test_travis_portal.py tests/test_harris_jp_portal.py tests/test_harris_cclerk_portal.py tests/test_harris_district_portal.py -q`
2. **Full Backend Test Suite:**
   - Run complete suite: `pytest --tb=short -q` (ensure 100% pass rate across all 554 tests).
3. **Linting & Code Quality:**
   - `ruff check app tests` (0 errors).
   - `npx tsc --noEmit` (0 errors).
   - `powershell scripts\check_ps1_syntax.ps1` (0 errors).
4. **Live Browser Verification Script:**
   - Run live navigation verification across all 8 portals in `scripts/test_all_8_portals_v4_nav.py` to confirm direct URL load and object readiness without extraneous redirects.
5. **Configuration File Integrity:**
   - Verify `setup_local.ps1` and `docker-compose.yml` remain clean and untouched.

---

## 5. User Confirmation Protocol

In adherence with `AGENTS.md` and `diagnose-plan-confirm-execute`, no code will be modified until explicit user approval of this plan is granted.
