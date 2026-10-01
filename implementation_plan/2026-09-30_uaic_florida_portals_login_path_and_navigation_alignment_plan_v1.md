# UAIC Claim & RPA Orchestrator — Florida Portals Alignment Plan (Miami Login Path & Broward/Hillsborough Navigation)

> **Implementation ID:** `IMP-2026-0930-003`  
> **Topic:** Exact Florida Court Scraper Navigation & Authentication Alignment (`broward.py`, `hillsborough.py`, `miami.py`)  
> **Date:** 2026-09-30  
> **Status:** Approved & Executed  
> **Implementation Record:** [`2026-09-30_uaic_florida_portals_login_path_and_navigation_alignment_implementation-record_v1.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-30_uaic_florida_portals_login_path_and_navigation_alignment_implementation-record_v1.md)  
> **Target Files:**  
> - `backend/app/automation/florida/miami.py`  
> - `backend/app/automation/florida/broward.py`  
> - `backend/app/automation/florida/hillsborough.py`  
> - `backend/app/automation/session_runner.py`  

---

## 1. Problem Statement & Root Cause Analysis

### A. Miami-Dade County (`miami.py`) — Incorrect Navigation & Aborted Login
* **User Feedback:**
  > `login_url = "https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`  
  > `this is also not going to correct path as given above is the correct path`  
  > `Note: i have noticed that you are not following up py files whcih curently i reviewed for all florida sites`
* **Root Causes:**
  1. `SingleSessionBrowserRunner` and `MiamiDadeScraper.navigate_to_search` opened `https://www2.miamidadeclerk.gov/ocs/`.
  2. Live DOM inspection confirms `https://www2.miamidadeclerk.gov/ocs/` contains **zero** `Register/Login` links or login controls (`count=0`).
  3. While `miami.py` line 217 defined `login_url = "https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB"`, line 319 and `verify_portal_url` (line 337) checked `if "usermanagementservices" in curr_url:` and **prematurely forced navigation back to OCS** before the login form could be submitted and authenticated!
  4. The scraper never reached or stayed on the exact login gateway path specified by the user and Power Automate V4:
     `https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`.

### B. Broward County (`broward.py`) — Loose Selectors Causing Stray Clicks
* **User Feedback:**
  > `system is not responding as design, why it is going to https://www.browardclerk.org/Web2/Services/PremiumServices and https://www.browardclerk.org//Web2/CaseSearchECA/Glossary/ i have not told to do this?`
* **Root Causes:**
  1. In `broward.py`, lines 110–120 in `navigate_to_search` and lines 241–250 in `return_to_search_state` used overly broad locators:
     - `".btn-bc-ql-text"` (matches every quick link on Broward home page; the first button in the DOM is **"Premium Services"** (`/Web2/Services/PremiumServices`))
     - `"a:has(div.btn-bc-ql-text)"`
     - `"a[href*='/Web2']"` (matches **"Glossary"** (`/Web2/CaseSearchECA/Glossary/`) in ECA navigation)
  2. These loose selectors caused the bot to veer into Premium Services and Glossary instead of the Case Search interface.

### C. Hillsborough County (`hillsborough.py`) — Verification
* **Current Status:**
  - Direct navigation configured to `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab`.
  - Targets exact `#nav-Party-tab` and pane submit button `#btnSubmitPartySearch`.
  - Needs verification to ensure zero unapproved clicks or stray links exist.

---

## 2. Technical Proposed Changes

### 2.1 Miami-Dade County Scraper (`backend/app/automation/florida/miami.py`)
1. **Explicit Login Navigation Protocol:**
   - Define canonical login URL constant:
     ```python
     MIAMI_LOGIN_GATEWAY_URL = "https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB"
     MIAMI_OCS_PORTAL_URL = "https://www2.miamidadeclerk.gov/ocs"
     ```
   - In `navigate_to_search(page)` / `ensure_authenticated(page)`:
     - Check if the session is already authenticated (look for `<a title*="View account information">Welcome, ...</a>` or logout link).
     - If NOT authenticated and `requires_login` is True:
       - Directly navigate page to `MIAMI_LOGIN_GATEWAY_URL`.
       - Wait for `#userName` and `#password` input fields to become visible.
       - Fill `#userName` with configured `self.username` (`apoorvnigam07@gmail.com`).
       - Fill `#password` with configured `self.password` (`Apoorv@12345`).
       - Click Submit: `input.btn.coc-button--primary[name='btnCall'][value='Login']` (or `input[name='btnCall']` / `#btnLogin`).
       - Wait for navigation/redirection after login: wait until URL changes away from `usermanagementservices` or wait for `Welcome,` greeting.
       - Dismiss browser password prompt with `Escape`.
     - Confirm active page is at `MIAMI_OCS_PORTAL_URL`. If not redirected automatically, navigate to `MIAMI_OCS_PORTAL_URL`.
2. **Fix Premature Redirection Logic:**
   - Remove lines 318–326 and update `verify_portal_url`: do NOT redirect away while authentication is actively underway on `MIAMI_LOGIN_GATEWAY_URL`. Only verify portal URL after `ensure_authenticated` has completed.
3. **Strict Step Execution Order:**
   - **Step a:** Navigation & Authentication (Gateway `https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB` → OCS `https://www2.miamidadeclerk.gov/ocs`).
   - **Step b:** Verify Welcome greeting / session active.
   - **Step c:** Dismiss password prompt (`Escape`).
   - **Step d:** Confirm on `https://www2.miamidadeclerk.gov/ocs`.
   - **Step e:** Click "Party Name" span (`span.cursorPointer:has-text('Party Name')` / `span.subitem-color:has-text('Party Name')`), click "Refresh" (`button.btn.button-blue:has-text('Refresh')`).
   - **Step f:** Fill First Name, Last Name, Filing Date From (DOL), Filing Date To (today's date).
   - **Step g:** Click "Search" button (`button.button-green:has-text('Search')`).
   - **Step h:** Wait for results to load (Table / Cards).
   - **Step i:** Enable Table View if not active.
   - **Step j:** Extract all case columns across pagination; dismiss search criteria popup if present.
   - **Step k:** Reset form / return to search state for next name.

---

### 2.2 Broward County Scraper (`backend/app/automation/florida/broward.py`)
1. **Purge Unbounded Selectors:**
   - Remove `.btn-bc-ql-text`, `a:has(div.btn-bc-ql-text)`, `a[href*='/Web2']` entirely from `navigate_to_search` and `return_to_search_state`.
2. **Direct Entry to ECA Search:**
   - Always navigate directly to `https://www.browardclerk.org/Web2/CaseSearchECA/Index/`.
   - If landing on `https://www.browardclerk.org/`, strictly click `a:has-text('Case Search')` with exact text matching, never broad class matching.
3. **Clean Search Reset:**
   - In `return_to_search_state`, navigate directly to `https://www.browardclerk.org/Web2/CaseSearchECA/Index/` or click `#btnReset` / exact `a:has-text('Case Search')`.

---

### 2.3 Hillsborough County Scraper (`backend/app/automation/florida/hillsborough.py`)
1. Verify direct navigation to `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab`.
2. Ensure `#nav-Party-tab` selection and submit button `#btnSubmitPartySearch` targeting has no loose fallbacks.

---

### 2.4 Browser Session Runner (`backend/app/automation/session_runner.py`)
1. In `get_or_create_tab` for `portal_key="miami"`:
   - When `scraper.requires_login` is True, initialize the tab directly at `MIAMI_LOGIN_GATEWAY_URL` (`https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`) so the visible Attended browser immediately shows the exact login gateway!
2. Ensure Windows profile directory isolation to `data/browser_profile/chromium` when `has_extension=True` to avoid `exitCode=33`.

---

## 3. Verification & Validation Protocol

1. **Automated Unit & Workflow Tests:**
   ```bash
   cd backend
   .venv\Scripts\pytest tests/test_miami_portal.py tests/test_broward_portal.py tests/test_hillsborough_portal.py -v
   .venv\Scripts\pytest --tb=short -q
   .venv\Scripts\ruff check app tests
   ```
2. **Live Interactive Attended GUI Verification:**
   - Launch real browser in Attended GUI mode on Miami portal (`https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`).
   - Verify visible entry to login page, credentials entry, login submission, and transition to `/ocs`.
   - Launch real browser on Broward portal and verify zero visits to PremiumServices or Glossary.
   - Capture screenshot and video recording to `implementation_plan/Images/` and `implementation_plan/Recording/`.

---

## 4. Governance Compliance

- **Rule:** NO APPROVAL = NO IMPLEMENTATION.
- Source code will only be modified after user confirms this plan.
