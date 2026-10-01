# UAIC Claim & RPA Orchestrator — Complete 8-Bot Step-by-Step Execution & Manual Coding Guide

> **Document ID:** `IMP-2026-0929-001`  
> **Topic:** Exhaustive Step-by-Step UI Automation Steps, Selector Recognition, AntiCaptcha Lifecycle, and Single-Bot Manual Debugging Playbook  
> **Target Audience:** Developers & RPA Engineers performing hands-on manual coding, selector tuning, and step-by-step verification  
> **Runtime Platform:** Python 3.14 + Playwright + Google Chrome / Chromium + AntiCaptcha Plugin v0.83  

---

## Table of Contents

1. [Executive Overview & Purpose](#1-executive-overview--purpose)
2. [Section 1: Configuration Source & Parent Bot URL Pipeline](#2-section-1-configuration-source--parent-bot-url-pipeline)
3. [Section 2: Browser Launch, AntiCaptcha Injection & Extension Lifecycle](#3-section-2-browser-launch-anticaptcha-injection--extension-lifecycle)
4. [Section 3: Detailed Step-by-Step Action & Object Recognition for All 8 Bots](#4-section-3-detailed-step-by-step-action--object-recognition-for-all-8-bots)
   - [Bot 1: Broward County Clerk of Courts (FL)](#bot-1-broward-county-clerk-of-courts-fl)
   - [Bot 2: Hillsborough County Clerk of Courts (FL)](#bot-2-hillsborough-county-clerk-of-courts-fl)
   - [Bot 3: Miami-Dade County Clerk of Courts (FL)](#bot-3-miami-dade-county-clerk-of-courts-fl)
   - [Bot 4: Dallas County Courts Odyssey (TX)](#bot-4-dallas-county-courts-odyssey-tx)
   - [Bot 5: Travis County Odyssey Portal (TX)](#bot-5-travis-county-odyssey-portal-tx)
   - [Bot 6: Harris County Justice of the Peace (TX)](#bot-6-harris-county-justice-of-the-peace-tx)
   - [Bot 7: Harris County District Clerk (TX)](#bot-7-harris-county-district-clerk-tx)
   - [Bot 8: Harris County Clerk WebSearch (TX)](#bot-8-harris-county-clerk-websearch-tx)
5. [Section 4: Developer Playbook — How to Play and Manually Fix Bots One by One](#5-section-4-developer-playbook--how-to-play-and-manually-fix-bots-one-by-one)
6. [Section 5: File Reference Matrix & Automation Architecture](#6-section-5-file-reference-matrix--automation-architecture)

---

## 1. Executive Overview & Purpose

This document provides a single-source guide for understanding, executing, debugging, and manually coding all 8 county court scrapers in the UAIC RPA Orchestrator.

If you have observed missed steps, incorrect button clicks, or workflow stalls, this manual explains:
1. **Exactly where the parent bot URL is sourced** (from Settings UI to Redis to Celery workers).
2. **How the browser launches with AntiCaptcha enabled and pinned**.
3. **What specific actions and DOM selectors each bot executes** at every step.
4. **How to test each bot in isolation in visible Google Chrome (Attended GUI Mode)** so you can observe the browser, inspect the DOM with DevTools, edit the Python scraper code, and verify that the workflow succeeds before moving to the next bot.

---

## 2. Section 1: Configuration Source & Parent Bot URL Pipeline

Every court scraper receives its base target URL dynamically at runtime. The URL is **never hardcoded in production**; it flows through a five-tier hierarchy:

```
[ Frontend Settings Page (/settings) ]
                   │
                   ▼ (HTTP POST /api/v1/settings)
[ FastAPI Settings Endpoint (settings.py) ]
                   │
                   ▼ (JSON Serialization)
[ Redis Database (Key: "uaic:system:settings:v4") ]
                   │
                   ▼ (get_system_settings_async())
[ Celery Task Worker (scraper_tasks.py) ]
                   │
                   ▼ (PortalsSettings instance)
[ Scraper Class Constructor (e.g. BrowardScraper(base_url=...)) ]
```

### 1.1 Where the URL is Edited in the UI
* **Location:** Web application route: `http://localhost:3000/settings`
* **Tab:** **"Portals"** Tab (or "Automation & Robot Configuration").
* **Fields:** Each of the 8 portals has:
  - An **Enabled Toggle** (`broward_enabled`, `hillsborough_enabled`, etc.).
  - A **Target URL Input Field** (`broward_url`, `hillsborough_url`, etc.).
  - For Miami-Dade: **Username**, **Password**, and **Requires Login** toggle.

### 1.2 Database Storage Key & Schema
* **Redis Key:** `uaic:system:settings:v4`
* **Pydantic Model:** `PortalsSettings` in [`backend/app/schemas/settings.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/settings.py#L220-L270)
* **Default Values in Code:** [`backend/app/services/settings_service.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/settings_service.py#L54-L74)

| Portal Identifier | Settings Field | Default URL (Fallback) | Database Target JSON Column | State Routing |
|---|---|---|---|:---:|
| **Broward** | `portals.broward_url` | `https://www.browardclerk.org/` | `fl_jsonbody_broward` | FL / Cross |
| **Hillsborough** | `portals.hillsborough_url` | `https://hover.hillsclerk.com/` | `fl_jsonbody_hillsborough` | FL / Cross |
| **Miami-Dade** | `portals.miami_url` | `https://www2.miamidadeclerk.gov/ocs` | `fl_jsonbody_miami` | FL / Cross |
| **Dallas** | `portals.dallas_url` | `https://courtsportal.dallascounty.org/DALLASPROD/Home/` | `te_jsonbody_dallas` | TX / Cross |
| **Travis** | `portals.travis_url` | `https://odysseyweb.traviscountytx.gov/Portal/` | `te_jsonbody_travis` | TX / Cross |
| **Harris JP** | `portals.harris_jp_url` | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/` | `te_jsonbody_harris` | TX / Cross |
| **Harris Clerk** | `portals.harris_cclerk_url` | `https://www.cclerk.hctx.net/Applications/WebSearch/` | `te_jsonbody_cclerk` | TX / Cross |
| **Harris District**| `portals.harris_district_url`| `https://www.hcdistrictclerk.com/` | `te_jsonbody_hcdistrict` | TX / Cross |

### 1.3 State Routing Logic (Strict Business Rule)
When a claim is processed by the orchestrator:
* If `policy_state == "FL"` and `loss_location_state == "FL"`: Runs **3 Florida Portals** (`broward`, `hillsborough`, `miami`).
* If `policy_state == "TX"` and `loss_location_state == "TX"`: Runs **5 Texas Portals** (`harris_cclerk`, `dallas`, `harris_jp`, `harris_district`, `travis`).
* If cross-state (`policy_state != loss_location_state`): Runs **ALL 8 Portals**.

---

## 3. Section 2: Browser Launch, AntiCaptcha Injection & Extension Lifecycle

A core challenge with browser automation is ensuring that the **Anti-Captcha Chrome Extension** is active, has a valid API key, and appears on the browser toolbar before navigation begins.

### 2.1 Extension Location on Disk
* **Directory:** `anticaptcha-plugin_v0.83/` located directly in the repository root.
* **Resolved By:** `ExtensionManager.resolve_extension_path()` in [`backend/app/automation/browser_manager.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py#L72-L102).

### 2.2 API Key Synchronization
Before launching the browser, the orchestrator syncs the API key into the extension files:
* Target file: `anticaptcha-plugin_v0.83/js/config_ac_api_key.js`
* Function: `ExtensionManager.sync_api_key(extension_dir, api_key, auto_cfg)`
* The script writes:
  ```javascript
  var antiCapApiKey = 'YOUR_API_KEY';
  var antiCapAutoSubmitForm = false; // We click submit manually via Playwright
  chrome.storage.local.set({ account_key: antiCapApiKey, enable: true, ... });
  ```

### 2.3 Browser Engine & Launch Arguments
In [`backend/app/automation/browser_manager.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py#L710-L930), the browser is launched using Playwright's `launch_persistent_context`:

1. **Engine Selection (`browser_engine`):**
   - **Google Chrome (`chrome`):** Searches standard Windows paths (`C:\Program Files\Google\Chrome\Application\chrome.exe`).
   - *Note on Extensions:* Modern Google Chrome Stable on Windows deprecates command-line `--load-extension`. The orchestrator auto-routes extension runs to Playwright's bundled Chromium binary when necessary to guarantee 100% active service workers without exit code 33 crashes.
2. **Launch Flags Injected:**
   ```python
   launch_args = [
       "--disable-blink-features=AutomationControlled", # Prevents bot detection
       "--start-maximized",                            # Opens full screen
       "--disable-background-timer-throttling",        # Prevents background tab freeze
       "--disable-backgrounding-occluded-windows",
       "--disable-renderer-backgrounding",
       f"--disable-extensions-except={ext_norm}",      # Loads ONLY AntiCaptcha
       f"--load-extension={ext_norm}",                 # Unpacked extension path
       "--no-sandbox",
   ]
   ```
3. **Headless vs. Attended Mode:**
   - **Attended (Visible GUI):** `headless = False`. You see real Chrome open on your desktop.
   - **Headless:** `launch_args.append("--headless=new")` while context has `headless = False` so extensions load invisibly.
4. **Toolbar Pinning:**
   - `ChromeSession.pin_extension_in_preferences()` writes the AntiCaptcha ID (`gcpdbjbmekkdlkpldjgffhmapgpdlcpj`) into the Chromium profile `Preferences` file under `extensions.pinned_extensions` and `toolbar.pinned_actions`. This ensures the icon is physically visible on the toolbar.

---

## 4. Section 3: Detailed Step-by-Step Action & Object Recognition for All 8 Bots

Below is the exhaustive, click-by-click breakdown for all 8 scrapers.

---

### Bot 1: Broward County Clerk of Courts (FL)

* **Source File:** [`backend/app/automation/florida/broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py)
* **Base URL:** `https://www.browardclerk.org/`
* **Direct Search URL:** `https://www.browardclerk.org/Web2/CaseSearchECA/Index/`
* **Output Schema (5 Fields):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

#### Step-by-Step Execution:
1. **Step A — Navigation & Readiness Check:**
   - Bot calls `page.goto("https://www.browardclerk.org/")`.
   - Checks `body` text length. If empty (< 5 chars), reloads the page.
2. **Step B — Navigate to Case Search:**
   - Checks if `/CaseSearchECA` is already in the URL.
   - If not, clicks the **Case Search** quick-link button:
     - Selector: `div.btn-bc-ql-text:has-text('Case Search'), a:has(div.btn-bc-ql-text), a[href*='CaseSearch']`
     - If button is missing, direct-navigates to `https://www.browardclerk.org/Web2/CaseSearchECA/Index/`.
3. **Step C — Select "Party Name" Tab:**
   - Evaluates whether `#nameSearch` tab pane has class `active` or `in`.
   - If not active, clicks Party Name tab:
     - Selector: `a[href='#nameSearch'], a#partyName-tab, a:has-text('Party Name')`
4. **Step D — Enter Search Inputs:**
   - **Last Name:** `input#lastName` (or `input[name='lastName']`, `input[data-fv-field='lastName']`).
   - **First Name:** `input#firstName` (or `input[name='firstName']`).
   - **Filing Date (DOL):** `input#filingDateOnOrAfterP` (format: `MM/dd/yyyy`).
   - Uses `biometric_fill()` respecting configured speed mode (turbo instant vs. paced).
5. **Step E — Session Timeout Guard:**
   - Checks for timeout dialog: `button:has-text('Continue session'), a:has-text('Continue session')`.
   - If present, clicks "Continue session" and re-verifies Party Name inputs.
6. **Step F — CAPTCHA Detection & Resolution:**
   - Calls `detect_and_handle_captcha()`.
   - Scans DOM for reCAPTCHA v2/v3, Turnstile, or AntiCaptcha solver status (`.antigate_solver_solved`).
   - Waits up to `captcha_wait_seconds` (default: 120s).
   - Once solved, dismisses any hanging image challenge popup via outside click and Escape key (`dismiss_captcha_challenge_popup()`).
7. **Step G — Submit Search (THE SUBMIT BUTTON):**
   - **Button to Click:** `button#PersonSearchResults`
   - Exact Selectors:
     - `button#PersonSearchResults`
     - `button[name='PersonSearchResults']`
     - `input#PersonSearchResults`
   - *Danger Zone:* **NEVER** click the global header search bar (`input#txtSearch` / `button#btnGlobalSearch`).
8. **Step H — Wait for Results:**
   - Waits for selector: `table.table tbody tr, :has-text('No records found'), :has-text('No cases found')`.
   - Timeout: 15s.
9. **Step I — Extract Results Grid:**
   - Column index mapping:
     - `td:eq(0)` -> `CaseNumber`
     - `td:eq(1)` -> `CaseStyle`
     - `td:eq(2)` -> `CaseType`
     - `td:eq(3)` -> `FilingDate`
     - `td:eq(4)` -> `CaseStatus`
10. **Step J — Pagination Traversal:**
    - Next page button: `a[title*='next' i], a:has-text('Go to the next page'), a:has-text('Next')`.
    - Checks `aria-disabled="true"`. Traverses until last page (safety limit: 20 pages).
11. **Step K — Reset to Clean Search State:**
    - Clicks `div.btn-bc-ql-text:has-text('Case Search')` or `a#btnNewSearch` to prepare tab for next party name.

---

### Bot 2: Hillsborough County Clerk of Courts (FL)

* **Source File:** [`backend/app/automation/florida/hillsborough.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/hillsborough.py)
* **Base URL:** `https://hover.hillsclerk.com/`
* **Direct Search URL:** `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab`
* **Output Schema (5 Fields):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

#### Step-by-Step Execution:
1. **Step A — Navigation & Landing Page:**
   - Bot navigates to `https://hover.hillsclerk.com/`.
   - If landing page displays, clicks: `a[href*='caseSearch.html#nav-Party-tab'], a:has-text('Party or Business Name')`.
2. **Step B — Select "Party or Business Name" Tab:**
   - Verifies if `#nav-Party-tab` is active (`class.includes('active')` or `aria-selected="true"`).
   - If not active, clicks: `button#nav-Party-tab[data-bs-target='#nav-Party'], button#nav-Party-tab`.
3. **Step C — Dismiss "YOUR SEARCH CRITERIA" Modal:**
   - If modal appears: `div.modal:has-text('YOUR SEARCH CRITERIA')`.
   - Clicks: `#messageClose, button.close, button:has-text('Close')`.
4. **Step D — Populate Search Fields (Exact Order: First -> Last -> Date):**
   - **First Name:** `input#spFirstName` (or `input[alt*='enter first name']`).
   - **Last Name:** `input#spLastName` (or `input[alt*='enter last name field']`).
   - **Date Filed After (DOL):** `input#spDateFiledAfter`.
     - *Important DOM Detail:* This field is often marked `readonly` by jQuery UI datepicker. The scraper executes JavaScript to `removeAttribute('readonly')` and dispatches `input`, `change`, and `blur` events.
5. **Step E — CAPTCHA Check:**
   - Scans for reCAPTCHA/Turnstile challenges; waits for AntiCaptcha solve.
6. **Step F — Click Search Button (THE SUBMIT BUTTON):**
   - **Button to Click:** `button#btnSubmitPartySearch`
   - Exact Selectors:
     - `button#btnSubmitPartySearch[type='button']`
     - `#nav-Party #btnSubmitPartySearch`
     - `#nav-Party button.btn-success`
   - *Danger Zone:* **NEVER** click `button#btnSubmitCaseSearch` (under `#nav-Case`) or `button#btnSubmitAttorneySearch`!
7. **Step G — Wait for Results Grid:**
   - Waits for URL `**/searchResults.html*` or table `#partyResultsTable, table.dataTable`.
   - Timeout: 35s.
8. **Step H — Extract Results Columns:**
   - Standard HOVER table columns:
     - `td:eq(2)` -> `CaseNumber`
     - `td:eq(3)` -> `Citation`
     - `td:eq(4)` -> `CaseStyle`
     - `td:eq(5)` -> `CaseStatus`
     - `td:eq(6)` -> `FilingDate`
     - `td:eq(7)` -> `CaseType`
9. **Step I — Pagination Traversal:**
   - Next button: `#partyResultsTable_next:not(.disabled) a, li.paginate_button.next:not(.disabled) a`.
10. **Step J — Reset to Clean Search State:**
    - Clicks `#messageClose` if open, then clicks `a:has-text('Case Search')` or re-navigates to `#nav-Party-tab`.

---

### Bot 3: Miami-Dade County Clerk of Courts (FL)

* **Source File:** [`backend/app/automation/florida/miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py)
* **Base URL:** `https://www2.miamidadeclerk.gov/ocs/`
* **Output Schema (5 Fields):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

#### Step-by-Step Execution:
1. **Step A — Navigation & Gateway Agreement:**
   - Navigates to `https://www2.miamidadeclerk.gov/ocs/`.
   - If disclaimer modal appears, clicks: `button:has-text('I Agree'), button:has-text('Accept'), button:has-text('Continue')`.
2. **Step B — Authentication / Login Workflow:**
   - Checks if user is already logged in (inspects for greeting: `a.header__nav-link:has-text('Welcome')` or `#lnkLogout`).
   - If not logged in and credentials are provided in Settings:
     - Clicks `a:has-text('Register/Login')` (or navigates to `.../Home/LoginOrRegister`).
     - Fills User ID / Email: `input#userName[name='userName']`.
     - Fills Password: `input#password[name='password']`.
     - Clicks **LOGIN**: `input.btn.coc-button--primary[name='btnCall'][value='Login'], input[name='btnCall']`.
     - Dismisses Chrome "Save Password" dialog via Escape key.
     - Confirms redirect back to `https://www2.miamidadeclerk.gov/ocs/`.
3. **Step C — The "Two-Button" Trap: Tab Selection vs. Query Submit:**
   - **Action 1 (Select Tab):** Clicks the navigation tab **"Party Name"**:
     - Selector: `span.subitem-color[role='button']:has-text('Party Name'), span.cursorPointer:has-text('Party Name')`.
     - *Note:* In responsive/small screens, first expands `button.navbar-toggler`.
   - **Action 2 (Refresh):** Clicks `button.btn.button-blue:has-text('Refresh')` to clear stale form cache.
4. **Step D — Populate Search Inputs:**
   - **Last Name:** `input#partyLastName[name='partyLastName']` (or `#txtLastName`).
   - **First Name:** `input#partyFirstName[name='partyFirstName']` (or `#txtFirstName`).
   - **Filing Date Range From:** `input#filingDateFrom` (format: `YYYY-MM-DD`).
   - **Filing Date Range To:** `input#filingDateTo` — **Always filled with Today's Date** (`datetime.now().strftime("%Y-%m-%d")`).
5. **Step E — CAPTCHA Check:**
   - Detects reCAPTCHA/Turnstile; waits for AntiCaptcha token.
6. **Step F — Submit Search (THE SUBMIT BUTTON):**
   - **Button to Click:** `button.btn.button-green[type='submit']:has-text('Search')`
   - Exact Selectors:
     - `button.btn.button-green[type='submit']`
     - `button.button-green:has-text('Search')`
     - `#btnSearch`
   - *Danger Zone:* **NEVER** click the top navigation bar "Party Name" button again, as that only re-toggles the tab.
7. **Step G — Wait for Results & Switch to Table View:**
   - Waits for results: `#tblResults, table.table, table.dataTable`.
   - **Table View Toggle:** If results render as cards, clicks: `button:has-text('Table View'), a:has-text('Table View'), #btnTableView`.
8. **Step H — Extract Columns:**
   - Extracts: `CaseNumber`, `CaseStyle`, `CaseType`, `FilingDate`, `CaseStatus`.
9. **Step I — Reset to Clean State:**
   - Clicks `span:has-text('OCS Home')` and `button:has-text('Refresh')` to reset for next party name.

---

### Bot 4: Dallas County Courts Odyssey (TX)

* **Source File:** [`backend/app/automation/texas/dallas.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/dallas.py)
* **Base URL:** `https://courtsportal.dallascounty.org/DALLASPROD/Home/`
* **Direct Search URL:** `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29`
* **Output Schema (5 Fields):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

#### Step-by-Step Execution:
1. **Step A — Navigation & Load Check:**
   - Navigates to `.../Home/Dashboard/29`.
   - Checks body length; reloads if unrendered.
2. **Step B — Activate Smart Search:**
   - If search input is not visible, clicks Smart Search button:
     - Selector: `a.portlet-buttons[href*='Dashboard/29'], a.btn:has-text('Smart Search')`.
3. **Step C — Handle Session Timeout Warning:**
   - If popup appears: `div:has-text('Session timeout warning')`.
   - Clicks: `button:has-text('Continue session'), a:has-text('Continue session')`.
4. **Step D — Populate Search Input (Formatted Name):**
   - **Field:** `input#caseCriteria_SearchCriteria` (or `input[name='caseCriteria.SearchCriteria']`).
   - **Name Format:** `"LastName, FirstName"` (comma-separated string).
5. **Step E — CAPTCHA Check:**
   - Detects reCAPTCHA v2 iframe (`iframe[title='reCAPTCHA']`); waits for AntiCaptcha solve.
6. **Step F — Submit Search (THE SUBMIT BUTTON):**
   - **Button to Click:** `input#btnSSSubmit[value='Submit']`
   - Exact Selectors:
     - `input#btnSSSubmit[name='Search'][value='Submit']`
     - `input#btnSSSubmit`
     - `form#frmSS input[type='submit'][value='Submit']`
   - *Danger Zone:* **DO NOT** click the magnifying glass in the top header or breadcrumb link `#tcControllerLink_0`.
7. **Step G — Wait for Kendo UI Grid:**
   - Waits for `.k-grid-content tbody tr, table.k-selectable tbody tr` or text `"no cases match your search"`.
8. **Step H — Extract Kendo Grid Columns:**
   - Extracts: Case number link (`a.caseLink`), Case style, Filing date, Case status, Case type.
9. **Step I — Pagination Traversal:**
   - Clicks Kendo next-page arrow: `.k-pager-nav[title='Go to the next page'], a.k-link[title*='next' i]`.
10. **Step J — Reset to Clean State:**
    - Clears `input#caseCriteria_SearchCriteria`, then clicks `#tcControllerLink_0` ("Smart Search").

---

### Bot 5: Travis County Odyssey Portal (TX)

* **Source File:** [`backend/app/automation/texas/travis.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/travis.py)
* **Base URL:** `https://odysseyweb.traviscountytx.gov/Portal/`
* **Direct Search URL:** `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29`
* **Output Schema (5 Fields):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

#### Step-by-Step Execution:
1. **Step A — Navigation & Load Check:**
   - Navigates to `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29`.
2. **Step B — Activate Smart Search:**
   - Clicks Smart Search portlet button: `a.portlet-buttons[href*='Dashboard/29'], a:has-text('Smart Search')`.
3. **Step C — Handle Session Timeout:**
   - Detects `div:has-text('Session timeout warning')`; clicks `button:has-text('Continue session')`.
4. **Step D — Populate Search Input:**
   - **Field:** `input#caseCriteria_SearchCriteria`.
   - **Format:** `"LastName, FirstName"`.
5. **Step E — CAPTCHA Check:**
   - Detects reCAPTCHA; waits for AntiCaptcha solve.
6. **Step F — Submit Search (THE SUBMIT BUTTON):**
   - **Button to Click:** `input#btnSSSubmit` (or `button#btnSSSubmit`).
   - Exact Selectors:
     - `input#btnSSSubmit[value='Submit']`
     - `#btnSSSubmit`
     - `input[name='Search'][value='Submit']`
7. **Step G — Wait for Results Grid:**
   - Waits for `.k-grid-content tbody tr` or `"no cases match your search"`.
8. **Step H — Extract Results:**
   - Extracts: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`.
9. **Step I — Pagination Traversal:**
   - Kendo next button: `.k-pager-nav[title='Go to the next page'], a.k-link[title*='next' i]`.
10. **Step J — Reset to Clean State:**
    - Clears search input, clicks breadcrumb `#tcControllerLink_0`.

---

### Bot 6: Harris County Justice of the Peace (TX)

* **Source File:** [`backend/app/automation/texas/harris_jp.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_jp.py)
* **Base URL:** `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`
* **Direct Search URL:** `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29`
* **STRICT SCHEMA RULE:** **4 Fields ONLY — Strictly NO CaseType!** (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`)

#### Step-by-Step Execution:
1. **Step A — Navigation:**
   - Navigates to `.../OdysseyPortalJP/Home/Dashboard/29`.
2. **Step B — Open Smart Search:**
   - Clicks: `a.portlet-buttons[href*='Dashboard/29'], a:has-text('Smart Search')`.
3. **Step C — Populate Search Input:**
   - **Field:** `input#caseCriteria_SearchCriteria`.
   - **Format:** `"LastName,FirstName"` (no space after comma, matching PAD V4 line 641).
4. **Step D — CAPTCHA Check:**
   - Waits for reCAPTCHA resolution via AntiCaptcha.
5. **Step E — Submit Search (THE SUBMIT BUTTON):**
   - **Button to Click:** `input#btnSSSubmit`
   - Exact Selectors:
     - `form#frmSS input[type='submit'][value='Submit']`
     - `input#btnSSSubmit[value='Submit']`
     - `#btnSSSubmit`
6. **Step F — Extract Results Grid:**
   - Extracts: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`.
   - **CRITICAL:** Do NOT extract or inject `CaseType`. If `CaseType` is present, downstream Guidewire validation fails!
7. **Step G — Pagination:**
   - Kendo paginator: `a.k-link[title*='next' i]`.
8. **Step H — Reset:**
    - Clears input, clicks `#tcControllerLink_0`.

---

### Bot 7: Harris County District Clerk (TX)

* **Source File:** [`backend/app/automation/texas/harris_district.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_district.py)
* **Base URL:** `https://www.hcdistrictclerk.com/`
* **Direct Search URL:** `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx`
* **Output Schema (5 Fields):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

#### Step-by-Step Execution:
1. **Step A — Navigation & Landing Page:**
   - Navigates to `https://www.hcdistrictclerk.com/`.
   - If on landing page, clicks **Search Our Records**:
     - Selector: `div.cardBody:has-text('Search Our Records'), a:has-text('Search Our Records'), img[src*='Icon_Nav_Search']`.
2. **Step B — Select "Party Inquiry" Tab:**
   - Checks if `#tabParty` has class `active`.
   - If not active, clicks: `input#tabParty[name*='tabParty'], #tabParty, input[value*='Party Inquiry' i]`.
   - *Danger Zone:* Default tab is often "Case Inquiry". You must select "Party Inquiry".
3. **Step C — Handle "YOUR SEARCH CRITERIA" Popup:**
   - If popup appears: `div:has-text('YOUR SEARCH CRITERIA')`.
   - Clicks: `a#messageClose, button:has-text('Close'), button:has-text('×')`.
4. **Step D — Populate Search Fields:**
   - **Party Name:** `input#txtPartyName` (or `input[name*='txtPartyName']`).
     - **Format:** `"LastName, FirstName"`.
   - **Filing Date (From):** `input#txtPartyStartDate` (format: `MM/dd/yyyy`).
5. **Step E — Submit Search (THE SUBMIT BUTTON):**
   - **Button to Click:** `ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch`
   - Exact Selectors:
     - `input#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch`
     - `input[name*='btnPartySearch']`
     - `input[value*='Search' i][id*='btnPartySearch']`
   - *Danger Zone:* **NEVER** click `input#btnCaseSearch` (the search button for the adjacent Case Number tab)!
6. **Step F — Extract ASP.NET GridView Rows:**
   - Extracts from `table[id*='grd'] tbody tr, table.grid tbody tr`:
     - `td:eq(0)` -> `CaseNumber`
     - `td:eq(1)` -> `CaseStyle`
     - `td:eq(5)` -> `FilingDate`
     - `td:eq(6)` -> `CaseType`
     - Status -> `CaseStatus` (defaults to "OPEN" if blank)
7. **Step G — Pagination Traversal:**
   - Clicks ASP.NET pagination links: `table[id*='grd'] tr.pager a, a:has-text('Next')`.
8. **Step H — Reset to Clean State:**
   - Clicks **Search Again** button:
     - `input#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnSearchAgain, input[value*='Search Again' i]`.

---

### Bot 8: Harris County Clerk WebSearch (TX)

* **Source File:** [`backend/app/automation/texas/harris_cclerk.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py)
* **Base URL:** `https://www.cclerk.hctx.net/Applications/WebSearch/`
* **Direct Search URL:** `https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil`
* **STRICT SCHEMA RULE:** **4 Fields ONLY — Strictly NO CaseType!** (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`)

#### Step-by-Step Execution:
1. **Step A — Navigation & Menu Hover:**
   - Navigates to `https://www.cclerk.hctx.net/Applications/WebSearch/`.
   - Hovers over top menu: `a:has-text('COURTS'), li.dropdown:has-text('COURTS')`.
   - Clicks submenu item **"County Civil"**:
     - Selector: `a[href*='CourtSearch.aspx?CaseType=Civil'], a:has-text('County Civil')`.
2. **Step B — Verify County Civil Form Loaded:**
   - Waits for input field: `input#ctl00_ContentPlaceHolder1_txtLastName`.
3. **Step C — Populate Search Fields:**
   - **Last Name:** `input#ctl00_ContentPlaceHolder1_txtLastName[name='ctl00$ContentPlaceHolder1$txtLastName']`.
   - **First Name:** `input#ctl00_ContentPlaceHolder1_txtFirstName[name='ctl00$ContentPlaceHolder1$txtFirstName']`.
   - **File Date From:** `input#ctl00_ContentPlaceHolder1_txtFrom2[name='ctl00$ContentPlaceHolder1$txtFrom2']` (or `#ctl00_ContentPlaceHolder1_txtDateFrom`).
4. **Step D — Submit Search (THE SUBMIT BUTTON):**
   - **Button to Click:** `ctl00_ContentPlaceHolder1_btnSearch`
   - Exact Selectors:
     - `input#ctl00_ContentPlaceHolder1_btnSearch[value='Search']`
     - `input[name='ctl00$ContentPlaceHolder1$btnSearch']`
     - `input#ctl00_ContentPlaceHolder1_btnSearch`
   - *Danger Zone:* **DO NOT CLICK `input#ctl00_ContentPlaceHolder1_btnClear`!** The "Clear" button sits directly adjacent to Search and will wipe out all inputs.
5. **Step E — Handle Popup:**
   - Checks for `div:has-text('YOUR SEARCH CRITERIA')`; clicks `a#messageClose, button:has-text('Close')`.
6. **Step F — Extract ASP.NET Grid Rows:**
   - Extracts from `table[id*='grd'] tbody tr, table.grid tbody tr`:
     - `td:eq(0) > a` -> `CaseNumber`
     - `td:eq(1)` -> `CaseStatus`
     - `td:eq(2)` -> `FilingDate`
     - `td:eq(5)` -> `CaseStyle`
   - **CRITICAL:** Do NOT extract or inject `CaseType`. Harris County Clerk strictly omits CaseType.
7. **Step G — Pagination Traversal:**
   - Clicks: `table.grid tr.pager a, a:has-text('Next')`.
8. **Step H — Reset to Clean State:**
   - Clicks `input#ctl00_ContentPlaceHolder1_btnClear` ("Clear") and clears inputs for next party name.

---

## 5. Section 4: Developer Playbook — How to Play and Manually Fix Bots One by One

You can run, pause, inspect, and tune every bot individually **without touching the Celery queue or running a full batch**.

### 5.1 The Single-Bot Test Harness: `scripts/test_court_bot.py`
The project includes a standalone test script located at [`scripts/test_court_bot.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/scripts/test_court_bot.py). It launches real Google Chrome on your screen, loads AntiCaptcha, executes the search, extracts cases, validates the schema contract, and prints timing telemetry.

#### CLI Command Reference:
Open PowerShell in the repository root:

```powershell
# ── 1. Test Broward County (FL) ──
python scripts/test_court_bot.py --bot broward --party "DOE, JOHN"

# ── 2. Test Hillsborough County (FL) ──
python scripts/test_court_bot.py --bot hillsborough --party "SMITH, ROBERT" --dol "01/15/2023"

# ── 3. Test Miami-Dade County (FL) ──
python scripts/test_court_bot.py --bot miami --party "GARCIA, MARIA"

# ── 4. Test Dallas County (TX) ──
python scripts/test_court_bot.py --bot dallas --party "JOHNSON, MICHAEL"

# ── 5. Test Travis County (TX) ──
python scripts/test_court_bot.py --bot travis --party "WILLIAMS, DAVID"

# ── 6. Test Harris County JP (TX) ──
python scripts/test_court_bot.py --bot harris_jp --party "BROWN, JAMES"

# ── 7. Test Harris County District Clerk (TX) ──
python scripts/test_court_bot.py --bot harris_district --party "RODRIGUEZ, CARLOS"

# ── 8. Test Harris County Clerk (TX) ──
python scripts/test_court_bot.py --bot harris_cclerk --party "MARTINEZ, JOSE"
```

#### Interactive Mode:
If you simply run:
```powershell
python scripts/test_court_bot.py
```
The script will prompt you with an interactive menu (1 to 8) to choose which bot to run, and allow you to enter any party name and date of loss interactively.

---

### 5.2 Step-by-Step Workflow for Fixing a Bot

Follow this iterative process to test and fix bots one by one:

```
[ Run Bot with test_court_bot.py ]
               │
               ▼
[ Watch Chrome Window Live on Screen ]
               │
               ├── If Error / Missed Action / Freeze ──┐
               │                                       ▼
               │                        [ Press F12 (DevTools) / Inspect Element ]
               │                                       │
               │                                       ▼
               │                        [ Find Exact ID / Class / Hierarchy ]
               │                                       │
               │                                       ▼
               │                        [ Open Python File for that Bot ]
               │                                       │
               │                                       ▼
               │                        [ Edit Selector or Add Step ]
               │                                       │
               │                                       ▼
               │                        [ Re-run test_court_bot.py ]
               │                                       │
               └── If Success & Valid Schema ◄─────────┘
                               │
                               ▼
               [ Run pytest for that Bot ]
                               │
                               ▼
               [ Proceed to Next Bot ]
```

#### Step 1: Add a Breakpoint or Inspection Pause
If you need Chrome to freeze right before clicking a button or filling an input so you can inspect the DOM:
1. Open the scraper file (e.g. `backend/app/automation/florida/broward.py`).
2. Insert a temporary pause:
   ```python
   # Freeze execution for 30 seconds so you can inspect with DevTools (F12)
   await page.wait_for_timeout(30000)
   ```
   Or use Playwright's built-in interactive inspector:
   ```python
   await page.pause()
   ```
3. Run the CLI command:
   ```powershell
   python scripts/test_court_bot.py --bot broward --party "DOE, JOHN"
   ```
4. The Chrome window will stay open and pause. Press **F12** in Chrome to open Developer Tools, right-click the element that failed to click, and select **Inspect**.

#### Step 2: Test Selectors Directly in Chrome Console
In the Chrome DevTools Console, test your selector before putting it in Python code:
```javascript
// Test standard querySelector
document.querySelector("button#PersonSearchResults")

// Test by text content
$x("//button[contains(text(), 'Search')]")
```

#### Step 3: Edit the Python Scraper File
Once you have the exact selector or missing step:
1. Open the target file (see [Section 5](#6-section-5-file-reference-matrix--automation-architecture) for file paths).
2. Locate the corresponding method:
   - `navigate_to_search(self, page)` — URL loading and tab activation.
   - `fill_search_fields(self, page, ...)` — Input fields population.
   - `search_by_party_name(self, ...)` — Submit button click and results wait.
   - `extract_results(self, ...)` or table parsing loop — Column mappings.
3. Update the selector using `page.locator(...)` or `resilient_click(locator, page=page)`.

#### Step 4: Validate Schema Parity
The test harness automatically validates that the extracted cases conform to the contract:
- If running **Broward, Hillsborough, Miami, Dallas, Travis, or Harris District**:
  - `CaseType` **MUST** be present in each case dictionary.
- If running **Harris JP or Harris County Clerk**:
  - `CaseType` **MUST NOT** be present! (The harness will print a red `[!] SCHEMA VIOLATION` error if present).

#### Step 5: Run Unit Tests for the Scraper
Run the automated pytest suite for that specific scraper:
```powershell
cd backend
.venv\Scripts\pytest tests/test_broward.py -v
.venv\Scripts\pytest tests/test_hillsborough.py -v
.venv\Scripts\pytest tests/test_miami.py -v
.venv\Scripts\pytest tests/test_dallas.py -v
.venv\Scripts\pytest tests/test_travis.py -v
.venv\Scripts\pytest tests/test_harris_jp.py -v
.venv\Scripts\pytest tests/test_harris_district.py -v
.venv\Scripts\pytest tests/test_harris_cclerk.py -v
```

---

## 6. Section 5: File Reference Matrix & Automation Architecture

| Bot # | County Portal | State | Primary Python File to Edit | Unit Test File | DB Column | Schema: CaseType? |
|:---:|---|:---:|---|---|---|:---:|
| **1** | **Broward County Clerk** | FL | [`backend/app/automation/florida/broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py) | `tests/test_broward.py` | `fl_jsonbody_broward` | **YES** |
| **2** | **Hillsborough County Clerk**| FL | [`backend/app/automation/florida/hillsborough.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/hillsborough.py) | `tests/test_hillsborough.py` | `fl_jsonbody_hillsborough` | **YES** |
| **3** | **Miami-Dade County Clerk** | FL | [`backend/app/automation/florida/miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py) | `tests/test_miami.py` | `fl_jsonbody_miami` | **YES** |
| **4** | **Dallas County Odyssey** | TX | [`backend/app/automation/texas/dallas.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/dallas.py) | `tests/test_dallas.py` | `te_jsonbody_dallas` | **YES** |
| **5** | **Travis County Odyssey** | TX | [`backend/app/automation/texas/travis.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/travis.py) | `tests/test_travis.py` | `te_jsonbody_travis` | **YES** |
| **6** | **Harris County JP** | TX | [`backend/app/automation/texas/harris_jp.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_jp.py) | `tests/test_harris_jp.py` | `te_jsonbody_harris` | **NO (STRICT)** |
| **7** | **Harris District Clerk** | TX | [`backend/app/automation/texas/harris_district.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_district.py) | `tests/test_harris_district.py` | `te_jsonbody_hcdistrict` | **YES** |
| **8** | **Harris County Clerk** | TX | [`backend/app/automation/texas/harris_cclerk.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py) | `tests/test_harris_cclerk.py` | `te_jsonbody_cclerk` | **NO (STRICT)** |

### Core Shared Infrastructure Files:
- **Base Scraper Contract & CAPTCHA Polling:** [`backend/app/automation/base.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/base.py)
  - Contains `resilient_click()`, `biometric_fill()`, `detect_and_handle_captcha()`, `dismiss_captcha_challenge_popup()`.
- **Browser Lifecycle & Extension Loader:** [`backend/app/automation/browser_manager.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py)
  - Contains `ChromeSession`, `ExtensionManager`, `TabManager`.
- **Multi-Tab Session Runner:** [`backend/app/automation/session_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py)
  - Reuses a single Chrome window across multiple portal tabs for an entire claim.
- **Settings Service & Redis Sync:** [`backend/app/services/settings_service.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/settings_service.py)
- **Celery Task Worker:** [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py)

---

## 7. Summary & Quick Action Checklist

When starting your manual coding session:
1. **Launch a bot in attended mode:**
   ```powershell
   python scripts/test_court_bot.py --bot broward --party "DOE, JOHN"
   ```
2. **Observe where it clicks:** Watch the screen. If it misclicks, pauses, or misses an action, note the step.
3. **Open the corresponding Python scraper file** in your IDE.
4. **Tune the selector or action** using Playwright's `locator()` or JavaScript evaluation.
5. **Re-run the command** until the bot outputs 100% clean cases with exact schema parity.
6. **Move to the next bot** until all 8 bots execute cleanly.
