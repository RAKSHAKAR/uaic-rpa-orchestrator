# UAIC Claim & RPA Orchestrator — Power Automate V4 Exact Parity Plan (Broward & Florida Portals)

> **Implementation ID:** `IMP-2026-0930-004`  
> **Topic:** 100% Exact Behavioral, URL & Object Parity with Power Automate Desktop V4 for Broward County & Florida Portals  
> **Source Reference:** Microsoft Power Automate Desktop V4 Flow (`scripts/extracted_v4_flow.robin`, lines 33, 87–161; `v4_subflows/Subflow_Broward.robin`; V4 ControlRepository `ControlRepository_7bdb415f-2aae-45a6-96a0-7ad7cf77de42.json`)  
> **Document Type:** Implementation Plan  
> **Date:** 2026-09-30  
> **Status:** Approved & Executed  
> **Implementation Record:** [`2026-09-30_uaic_power_automate_v4_broward_and_florida_exact_parity_implementation-record_v1.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-30_uaic_power_automate_v4_broward_and_florida_exact_parity_implementation-record_v1.md)  
> **Target Files:**  
> - `backend/app/automation/florida/broward.py`  
> - `backend/app/core/config.py`  
> - `backend/app/schemas/settings.py`  
> - `backend/app/services/settings_service.py`  
> - `backend/app/automation/session_runner.py`  
> - `backend/app/automation/florida/hillsborough.py`  
> - `backend/app/automation/florida/miami.py`  

---

## 1. Root Cause Analysis: Why it was going to PremiumServices and Glossary

Direct inspection of `Subflow_Broward.robin`, `extracted_v4_flow.robin`, and the live HTML of `https://www.browardclerk.org/Web2` revealed the exact chain of causes:

### A. Wrong Base URL Configuration:
1. In Power Automate V4, the portal URL is:
   `https://www.browardclerk.org/Web2`
   (V4 `LaunchChrome` line 33: `Url: 'https://www.browardclerk.org/Web2'`).
2. In the Python codebase (`config.py`, `settings.py`, `settings_service.py`, and `broward.py`), the URL was configured as `https://www.browardclerk.org/` (the county homepage).
3. On `https://www.browardclerk.org/`, the case search form does NOT exist. Instead, the page contains county service links including "Premium Services" (`/Web2/Services/PremiumServices`).

### B. Spurious Button Clicking in `navigate_to_search`:
1. When opening `https://www.browardclerk.org/Web2`, the browser lands directly on **"Case Search - Public"**, which ALREADY has:
   - `#nameSearch` ("Party Name" search pane)
   - `#firstName`
   - `#lastName`
   - `#filingDateOnOrAfterP`
   - `#PersonSearchResults` (the submit button)
2. In `broward.py`, lines 108–125 had:
   ```python
   curr_after = getattr(page, "url", "") or ""
   if "/CaseSearchECA" not in curr_after:
       case_search_btn = page.locator(...)
       await resilient_click(case_search_btn)
   ```
3. Because `https://www.browardclerk.org/Web2` does not contain `"/CaseSearchECA"` in the URL bar, the scraper tried to find and click a button labeled "Case Search".
4. On `https://www.browardclerk.org/Web2`, the navigation bar contains:
   - `li#mnuPremiumServicves > a` (links to `/Web2/Services/PremiumServices`)
   - `a` with text "GLOSSARY OF TERMS" (links to `/Web2/CaseSearchECA/Glossary/`)
5. The loose locators clicked those header/dropdown links, which navigated the browser to **Premium Services** and **Glossary**!

### C. Power Automate V4 Exact Behavior:
1. In Power Automate V4 (`Subflow_Broward.robin` lines 1–6):
   - **V4 does NOT click any "Case Search" button on startup!**
   - It directly clicks `appmask['Broward']['Anchor \'Party Name\'']` (`a[href="#nameSearch"]`).
   - It fills `#firstName`, `#lastName`, `#filingDateOnOrAfterP`.
   - It solves CAPTCHA.
   - It clicks `document.getElementById("PersonSearchResults").click()`.
   - It extracts table rows (`table tbody tr`).
   - After extraction, it resets by simply navigating back to `https://www.browardclerk.org/Web2`.

---

## 2. Proposed Exact Parity Changes

### 2.1 Broward County Scraper (`backend/app/automation/florida/broward.py`)
1. **Canonical URL Constant:**
   ```python
   BROWARD_PORTAL_URL = "https://www.browardclerk.org/Web2"
   ```
2. **Update Constructor:**
   `base_url = base_url or BROWARD_PORTAL_URL`
3. **Rewrite `navigate_to_search(page)` to 1:1 V4 Parity:**
   - Navigate directly to `BROWARD_PORTAL_URL` (`https://www.browardclerk.org/Web2`).
   - **Completely remove all clicking of "Case Search" buttons or header links.**
   - Verify page loaded by checking `#nameSearch` or `#lastName` is present in DOM.
4. **Step C (`select_party_name_tab`):**
   - Click exact V4 object: `#myTabStandard a[href="#nameSearch"], a[href="#nameSearch"]`.
5. **Step D (`fill_search_fields`):**
   - Fill exact V4 IDs:
     - `document.getElementById("firstName").value`
     - `document.getElementById("lastName").value`
     - `document.getElementById("filingDateOnOrAfterP").value`
6. **Step G (Submit):**
   - Click exact V4 ID: `button#PersonSearchResults` / `document.getElementById("PersonSearchResults").click()`.
7. **Step J (`return_to_search_state`):**
   - Re-navigate to `https://www.browardclerk.org/Web2` (exact V4 line 143: `WebAutomation.GoToWebPage Url: 'https://www.browardclerk.org/Web2'`).
   - Re-select `#myTabStandard a[href="#nameSearch"]`. Zero stray button clicks.

### 2.2 System Settings & Migration (`settings_service.py`, `settings.py`, `config.py`)
1. Update default `broward_url` across Pydantic schemas, Config, and DB migration to `https://www.browardclerk.org/Web2`.
2. In `settings_service.py`, update `_normalize_portals_data` so that any existing stored `"https://www.browardclerk.org/"` is migrated immediately to `"https://www.browardclerk.org/Web2"`.

### 2.3 Verification of Hillsborough & Miami Scrapers Against V4
1. **Hillsborough County (`hillsborough.py`):**
   - Verify launch URL: `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` (V4 line 54).
   - Inputs: `#spFirstName`, `#spLastName`, `#spDateFiledAfter` (V4 lines 21, 29, 37).
   - Submit: `#btnSubmitPartySearch` (V4 line 51).
   - Dialog close: `#messageClose` (V4 line 133).
   - Reset: Re-navigate to `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` (V4 line 169).
2. **Miami-Dade County (`miami.py`):**
   - Login Gateway URL: `https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`.
   - OCS URL: `https://www2.miamidadeclerk.gov/ocs`.
   - Inputs: `#partyFirstName`, `#partyLastName`, `#filingDateFrom` (format `MM-dd-yyyy`).
   - Submit: `button.button-green:has-text('Search')`.
   - Reset: Click `Span 'OCS Home'` and `Button 'Refresh'`.

---

## 3. Verification & Acceptance Criteria
1. Live headless/attended browser execution of Broward County scraper must:
   - Open `https://www.browardclerk.org/Web2`.
   - Never visit `/Web2/Services/PremiumServices`.
   - Never visit `/Web2/CaseSearchECA/Glossary/`.
   - Directly populate `#firstName`, `#lastName`, `#filingDateOnOrAfterP` and click `#PersonSearchResults`.
2. All 39 Florida unit tests pass (`100%`).
3. Full backend test suite (554 tests) passes (`100%`).
4. `ruff check app tests` passes (0 errors).
5. Frontend TypeScript (`tsc`) passes (0 errors).
6. PowerShell script check passes (0 errors).
