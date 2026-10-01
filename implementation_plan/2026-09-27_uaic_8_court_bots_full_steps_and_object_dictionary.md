# UAIC Claim & RPA Orchestrator — Complete 8-Bot Automation Steps & Object Dictionary

> **Document ID:** `IMP-2026-0927-002`  
> **Topic:** Exhaustive Step-by-Step UI Automation Steps & Exact Object / Selector Dictionary for All 8 County Court Bots  
> **Source Reference:** Microsoft Power Automate Desktop V4 (`ExtractDataFlow.robin`, lines 173–1390) & Active Playwright Engine  
> **Purpose:** User review, validation, and correction of all DOM elements, input fields, navigation tabs, and submit buttons (specifically resolving multi-button ambiguity).

---

## 1. Executive Summary: The "Two-Button" Ambiguity Problem

Across several county court portals, web pages contain **multiple buttons** labeled "Search" or "Submit":
1. **Header / Global Search Button vs. In-Page Form Submit Button:** Clicking the global header search instead of the party form submit button causes page navigation away from the search form.
2. **Tab Expansion Button vs. Query Execution Button (e.g., Miami-Dade OCS):** One button is used to expand or select the "Search" tab/view, and a second button inside the form executes the query.
3. **Multi-Tab Search Portals (e.g., Hillsborough, Harris District Clerk):** Pages with tabs for "Case Number Search", "Party Search", and "Attorney Search" render multiple submit buttons on the same page (e.g., `#btnSubmitCaseSearch` vs. `#btnSubmitPartySearch`). A generic selector like `button:has-text('Search')` hits the wrong, hidden button.

This document details the **exact steps and UI object selectors** for all 8 bots so you can verify each object ID, name, and sequence.

---

## 2. Summary Comparison of the 8 Submit Buttons & Confusion Points

| # | Court Portal | State | Primary Correct Submit Button (V4 Reference) | Ambiguous / Wrong Button on Same Page | Risk if Wrong Button Clicked |
|:---:|---|:---:|---|---|---|
| **1** | **Broward County Clerk** | FL | `document.getElementById("PersonSearchResults")` or `button#btnSearch` inside `#personSearchForm` | Global Header Search `input#txtSearch` / `button#btnGlobalSearch` | Navigates to general clerk search; clears entered party name. |
| **2** | **Dallas County Odyssey** | TX | `input[type="submit"][value="Submit"]` inside `#frmSS` or `document.getElementById("btnSSSubmit")` | Top navigation menu search icon / Smart Search navigation link | Reloads blank search dashboard instead of submitting form. |
| **3** | **Travis County Odyssey** | TX | `document.getElementById("btnSSSubmit")` (ID: `btnSSSubmit`) | Header portal search input / quick search bar | Navigates to general record lookup without date filters. |
| **4** | **Harris County JP** | TX | `input[type="submit"][value="Submit"]` inside `form#frmSS` | Navigation heading / breadcrumb link `#headingSmartSearch` | Collapses search panel; does not submit. |
| **5** | **Miami-Dade County Clerk** | FL | In-form query button `button#btnSearch` / `main#content button` | Tab selection button `Button 'Search' 2` (top navigation) | Re-selects / collapses tab instead of executing search query. |
| **6** | **Harris County Clerk** | TX | `input#ctl00_ContentPlaceHolder1_btnSearch` (Value: `"SEARCH"`) | `input#ctl00_ContentPlaceHolder1_btnClear` (Value: `"CLEAR"`) right next to it | Completely wipes out all entered search criteria! |
| **7** | **Hillsborough County Clerk**| FL | `button#btnSubmitPartySearch` (under `#nav-Party`) | `button#btnSubmitCaseSearch` (under `#nav-Case`) | Clicks hidden case-number submit; returns empty or error. |
| **8** | **Harris District Clerk** | TX | `input#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch` | `input#btnCaseSearch` (Search by Case Number on adjacent tab) | Submits empty case number search; returns no results. |

---

## 3. Exhaustive Step-by-Step & Object Dictionary for Each Bot

```
PORTAL INDEX:
[1] Broward County Clerk (FL)
[2] Dallas County Odyssey (TX)
[3] Travis County Odyssey (TX)
[4] Harris County JP (TX)
[5] Miami-Dade County Clerk (FL)
[6] Harris County Clerk (TX)
[7] Hillsborough County Clerk (FL)
[8] Harris District Clerk (TX)
```

---

### [1] Broward County Clerk of Courts (FL)

* **Base URL:** `https://www.browardclerk.org/Web2`
* **Source Code:** [backend/app/automation/florida/broward.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py)
* **Robin Reference:** `Subflow_Broward` (Lines 173–334)
* **Output Schema:** 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`)

#### Detailed Steps & UI Objects:
| Step # | Action | UI Object Description | PAD V4 / Playwright Selector | Notes / Confusion Avoidance |
|:---:|---|---|---|---|
| **1.1** | Navigate | Portal Entry Point | `https://www.browardclerk.org/Web2` | Initial load of case search web application. |
| **1.2** | Click Tab | Select "Party Name" Search Mode | `div#myTabStandard > a[Text='Party Name']` or `a#partyName-tab` | Must select Party Name tab; default may be Case Number. |
| **1.3** | Populate | Enter Last Name | `input#lastName` (or `input[name='lastName']`) | Form ID: `form#personSearchForm`. |
| **1.4** | Populate | Enter First Name | `input#firstName` (or `input[name='firstName']`) | Filled if First Name is present. |
| **1.5** | Populate | Enter Date of Loss (Filing Date) | `input#filingDateOnOrAfterP` | V4 Robin line 191: `document.getElementById("filingDateOnOrAfterP").value = "${VarDOL}"`. |
| **1.6** | CAPTCHA | Anti-Captcha / Turnstile Verification | Iframe container `#dvMainBody` / Cloudflare Turnstile | Solved via AntiCaptcha extension before clicking Submit. |
| **1.7** | **SUBMIT** | **Execute Party Search** | **PAD V4:** `document.getElementById("PersonSearchResults").click();`<br>**Playwright Fallback:** `button#btnSearch`, `input[type='submit'][value*='Search']` inside `form#personSearchForm` | **DO NOT CLICK:** Global header search `input#txtSearch` / `button#btnGlobalSearch`. Must click `#PersonSearchResults`. |
| **1.8** | Extract | Parse Results Table | `table.table tbody tr` or `div#SearchResultsGrid table tbody tr` | td:0 CaseNumber, td:1 CaseStyle, td:2 CaseType, td:3 FilingDate, td:4 CaseStatus. |
| **1.9** | Pagination | Advance Pages | `a[title*='next' i]`, `a:has-text('Go to the next page')` | Traverses until disabled or max 20 pages. |
| **1.10** | Reset | Return to Clean State | `a#btnNewSearch`, `button#btnNewSearch`, or re-click `#myTabStandard a[Text='Party Name']` | Resets form inputs cleanly for the next party search iteration. |

---

### [2] Dallas County Odyssey Portal (TX)

* **Base URL:** `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29`
* **Source Code:** [backend/app/automation/texas/dallas.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/dallas.py)
* **Robin Reference:** `Subflow_Dallas` (Lines 335–476)
* **Output Schema:** 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`)

#### Detailed Steps & UI Objects:
| Step # | Action | UI Object Description | PAD V4 / Playwright Selector | Notes / Confusion Avoidance |
|:---:|---|---|---|---|
| **2.1** | Navigate | Open Dallas Dashboard | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` | Odyssey portal dashboard. |
| **2.2** | Click | Activate Smart Search | `a:has-text('Smart Search')`, `h1:has-text('Smart Search')`, or `#SearchCriteriaContainer` | Opens the Smart Search input container. |
| **2.3** | Populate | Enter Party Name | `input#caseCriteria_SearchCriteria` | **Format:** `"LastName, FirstName"` (comma separated). |
| **2.4** | CAPTCHA | reCAPTCHA v2 Checkbox | `iframe[title='reCAPTCHA'] > div#rc-anchor-container` | AntiCaptcha plugin verifies checkbox. |
| **2.5** | **SUBMIT** | **Submit Search Query** | **PAD V4 line 389:** `[...document.querySelectorAll('input[type="submit"]')].forEach(el => { if (el.value === "Submit") { el.click(); } });`<br>**Playwright:** `input[type="submit"][value="Submit"]`, `button#btnSSSubmit` inside `form#frmSS` | **DO NOT CLICK:** Magnifying glass icon in top navigation header. |
| **2.6** | Extract | Parse Kendo UI Result Grid | `.k-grid-content tbody tr`, `table.k-selectable tbody tr` | Extracts case number link, case style, filing date, status, and case type. |
| **2.7** | Pagination | Advance Result Grid | `a.k-link[title*='next' i]`, `.k-pager-nav[title='Go to the next page']` | Traverses Kendo paginator. |
| **2.8** | Reset | Return to Clean State | Click `p.step-label` ("Search") or re-navigate to `Dashboard/29` | Re-initializes Smart Search form for the next party name. |

---

### [3] Travis County Odyssey Portal (TX)

* **Base URL:** `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29`
* **Source Code:** [backend/app/automation/texas/travis.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/travis.py)
* **Robin Reference:** `Subflow_Travis` (Lines 477–616)
* **Output Schema:** 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`)

#### Detailed Steps & UI Objects:
| Step # | Action | UI Object Description | PAD V4 / Playwright Selector | Notes / Confusion Avoidance |
|:---:|---|---|---|---|
| **3.1** | Navigate | Open Travis Dashboard | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` | Travis Odyssey portal. |
| **3.2** | Click | Open Smart Search | `a:has-text('Smart Search')`, `h1:has-text('Smart Search')` | Activates search view. |
| **3.3** | Populate | Enter Party Name | `input#caseCriteria_SearchCriteria` | **Format:** `"LastName, FirstName"`. |
| **3.4** | CAPTCHA | reCAPTCHA v2 Checkbox | `iframe[title='reCAPTCHA'] > div#rc-anchor-container` | Solved via AntiCaptcha extension. |
| **3.5** | **SUBMIT** | **Submit Search Query** | **PAD V4 line 513:** `document.getElementById("btnSSSubmit").click();`<br>**Playwright:** `button#btnSSSubmit`, `input[type="submit"][value="Submit"]` | **CRITICAL ID:** `btnSSSubmit`. Explicit submit button for Smart Search. |
| **3.6** | Extract | Parse Kendo Grid Results | `.k-grid-content tbody tr` | Extracts CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType. |
| **3.7** | Pagination | Next Page Navigation | `.k-pager-nav[title='Go to the next page']` | Kendo UI pagination traversal. |
| **3.8** | Reset | Return to Clean State | `[...document.querySelectorAll("p.step-label")].forEach(...)` or re-click Smart Search | Clears search input and returns to initial state. |

---

### [4] Harris County Justice of the Peace (TX)

* **Base URL:** `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29`
* **Source Code:** [backend/app/automation/texas/harris_jp.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_jp.py)
* **Robin Reference:** `Subflow_Harris` (Lines 617–832)
* **Output Schema:** **4 Fields (Strictly NO CaseType):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`

#### Detailed Steps & UI Objects:
| Step # | Action | UI Object Description | PAD V4 / Playwright Selector | Notes / Confusion Avoidance |
|:---:|---|---|---|---|
| **4.1** | Navigate | Open Harris JP Dashboard | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` | JP Odyssey portal entry point. |
| **4.2** | Click | Open Smart Search | `h1:has-text('Smart Search')`, `a[href*='SearchCriteria']` | Selects Smart Search. |
| **4.3** | Populate | Enter Party Name | `document.getElementById("caseCriteria_SearchCriteria").value = "${VarLastName},${VarFirstName}";` | **Format:** `"LastName,FirstName"` (no space after comma in V4). |
| **4.4** | CAPTCHA | reCAPTCHA Checkbox | `div#main > form#frmSS > div#SSColumn > iframe` | Solved via AntiCaptcha extension. |
| **4.5** | **SUBMIT** | **Execute Search Query** | **PAD V4 line 657:** `[...document.querySelectorAll('input[type="submit"]')].forEach(el => { if (el.value === "Submit") el.click(); });`<br>**Playwright:** `form#frmSS input[type="submit"][value="Submit"]` | **DO NOT CLICK:** Smart Search header link or general search bar. |
| **4.6** | Extract | Parse Result Rows | `.k-grid-content tbody tr, table.k-selectable tbody tr` | **STRICT SCHEMA:** Extracts `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`. **`CaseType` IS OMITTED.** |
| **4.7** | Pagination | Advance Results | `a.k-link[title*='next' i]` | Advances through result pages. |
| **4.8** | Reset | Return to Search State | Re-click Smart Search heading or clear `caseCriteria_SearchCriteria` | Clears criteria for subsequent party search iterations. |

---

### [5] Miami-Dade County Clerk of Courts (FL)

* **Base URL:** `https://www2.miamidadeclerk.gov/ocs`
* **Source Code:** [backend/app/automation/florida/miami.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py)
* **Robin Reference:** `Subflow_Miami` (Lines 901–1108)
* **Output Schema:** 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`)

#### Detailed Steps & UI Objects (THE 2-BUTTON TRAP RESOLVED):
| Step # | Action | UI Object Description | PAD V4 / Playwright Selector | Notes / Confusion Avoidance |
|:---:|---|---|---|---|
| **5.1** | Navigate | Open OCS Portal | `https://www2.miamidadeclerk.gov/ocs` | Miami-Dade Online Court Services (OCS). |
| **5.2** | Optional Auth | User Login (if configured) | `input#userName`, `input#password`, `button:has-text('Login')` | Executed only if credentials are configured in Settings. |
| **5.3** | **Click Tab** | **Button 'Search' 2 (Tab Selection)** | **PAD V4 line 957:** `Button 'Search' 2`<br>**Playwright:** `div#root > main#content > button`, `nav a:has-text('Search')` | **BUTTON 1 OF 2:** This button ONLY expands/opens the search panel! It does NOT execute the query! |
| **5.4** | Populate | Enter Last Name | `input#partyLastName` | Input field for Party Last Name. |
| **5.5** | Populate | Enter First Name | `input#partyFirstName` | Input field for Party First Name. |
| **5.6** | Populate | Enter Date of Loss (Filing Date) | `input#filingDateFrom` | Date filter: `MM/dd/yyyy`. |
| **5.7** | CAPTCHA | reCAPTCHA Container | `div#ctl00_ContentPlaceHolder1_CaptchaContainer` | Solved via AntiCaptcha extension. |
| **5.8** | **SUBMIT** | **Button 'Search' (Execute Query)** | **PAD V4 line 1003:** `Button 'Search'`<br>**Playwright:** `main#content form button#btnSearch`, `button[type='submit']`, `button:has-text('Search')` inside party search form | **BUTTON 2 OF 2 (CRITICAL):** This is the ACTUAL form submission button. Must be clicked AFTER entering data. |
| **5.9** | Extract | Parse Results Grid | `table#tblSearchResults tbody tr`, `table.table tbody tr` | Extracts CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType. |
| **5.10** | Pagination | Advance Pages | `a[title*='next' i]`, `.pagination li.next a` | Traverses pagination. |
| **5.11** | Reset | Return to Clean State | `button#btnNameReset` (Button 'Reset') or `a#ctl00_ContentPlaceHolder1_lnk` ('Back to Search') | Resets inputs for next party search. |

---

### [6] Harris County Clerk (TX)

* **Base URL:** `https://www.cclerk.hctx.net/Applications/WebSearch/`
* **Source Code:** [backend/app/automation/texas/harris_cclerk.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py)
* **Robin Reference:** `Subflow_Cclerk` (Lines 833–900)
* **Output Schema:** **4 Fields (Strictly NO CaseType):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`

#### Detailed Steps & UI Objects:
| Step # | Action | UI Object Description | PAD V4 / Playwright Selector | Notes / Confusion Avoidance |
|:---:|---|---|---|---|
| **6.1** | Navigate | Open WebSearch Portal | `https://www.cclerk.hctx.net/Applications/WebSearch/` | ASP.NET WebSearch application. |
| **6.2** | Click Link | Select "County Civil" Category | `a:has-text('County Civil')` | Directs to County Civil court records. |
| **6.3** | Populate | Enter Last Name | `input#ctl00_ContentPlaceHolder1_txtLastName` | PAD V4 line 835: `document.getElementById("txtLastName")`. |
| **6.4** | Populate | Enter First Name | `input#ctl00_ContentPlaceHolder1_txtFirstName` | PAD V4 line 837: `document.getElementById("txtFirstName")`. |
| **6.5** | Populate | Enter Date of Loss (Filing Date) | `input#ctl00_ContentPlaceHolder1_txtDateFrom` | PAD V4 line 839: `Input text 'File Date from' 4`. |
| **6.6** | **SUBMIT** | **Click "SEARCH" Submit Button** | **PAD V4 line 841:** `input#ctl00_ContentPlaceHolder1_btnSearch`<br>**Playwright:** `input#ctl00_ContentPlaceHolder1_btnSearch, input[value='SEARCH' i]` | **DO NOT CLICK:** `input#ctl00_ContentPlaceHolder1_btnClear` ("CLEAR" button sits immediately next to Search!). |
| **6.7** | Extract | Parse ASP.NET Grid Rows | `table[id*='grd'] tbody tr, table.grid tbody tr` | td:0 CaseNumber, td:1 CaseStatus, td:2 FilingDate, td:5 CaseStyle.<br>**STRICT SCHEMA: NO CaseType.** |
| **6.8** | Pagination | Advance Pages | `table.grid tr.pager a, a:has-text('Next')` | Traverses ASP.NET table pagination. |
| **6.9** | Reset | Return to Clean State | **PAD V4 line 897:** `input#ctl00_ContentPlaceHolder1_btnClear` | Clicks CLEAR button to reset inputs for next party search. |

---

### [7] Hillsborough County Clerk of Courts (FL)

* **Base URL:** `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab`
* **Source Code:** [backend/app/automation/florida/hillsborough.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/hillsborough.py)
* **Robin Reference:** `Subflow_Hillsborough` (Lines 1205–1390)
* **Output Schema:** 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`)

#### Detailed Steps & UI Objects:
| Step # | Action | UI Object Description | PAD V4 / Playwright Selector | Notes / Confusion Avoidance |
|:---:|---|---|---|---|
| **7.1** | Navigate | Open HOVER Portal | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` | HOVER case search web portal. |
| **7.2** | Click Tab | Select "Search by Party" Tab | **PAD V4 line 1207:** `button#nav-Party-tab`<br>**Selector:** `div#nav-tab > button#nav-Party-tab` | Activates Party Name search form. |
| **7.3** | Populate | Enter First Name | **PAD V4 line 1225:** `document.getElementById("spFirstName").value = "${VarFirstName}";`<br>**Selector:** `input#spFirstName` or `input[name='firstName']` | First Name input field. |
| **7.4** | Populate | Enter Last Name | **PAD V4 line 1233:** `document.getElementById("spLastName").value = "${VarLastName}";`<br>**Selector:** `input#spLastName` or `input[name='lastName']` | Last Name input field. |
| **7.5** | Populate | Enter Date of Loss (Filing Date) | **PAD V4 line 1241:** `document.getElementById('spDateFiledAfter').value = "${VarDOL}";`<br>**Selector:** `input#spDateFiledAfter` or `input[name='fileDateFrom']` | Filing Date filter. |
| **7.6** | **SUBMIT** | **Click Party Search Button** | **PAD V4 line 1255:** `button#btnSubmitPartySearch`<br>**Selector:** `div#nav-Party button#btnSubmitPartySearch` | **CRITICAL ID:** Must click `#btnSubmitPartySearch`.<br>**DO NOT CLICK:** `#btnSubmitCaseSearch` (Case Search tab) or `#btnSubmitAttorneySearch`! |
| **7.7** | Popup Check | Handle "No Cases Found" Dialog | **PAD V4 lines 1337/1357:** `document.getElementById("messageClose").click();` | Closes message dialog if no matches found. |
| **7.8** | Extract | Parse Results Table | `table#mycasesdata tbody tr` or `main table tbody tr` | Extracts CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType. |
| **7.9** | Reset | Return to Clean State | **PAD V4 line 1373/1381:** Navigate `#nav-Party-tab` and click `button#nav-Party-tab` | Re-opens clean Party tab for next party search. |

---

### [8] Harris County District Clerk (TX)

* **Base URL:** `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx`
* **Source Code:** [backend/app/automation/texas/harris_district.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_district.py)
* **Robin Reference:** `Subflow_HarrisDistrict` (Lines 1109–1204)
* **Output Schema:** 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`)

#### Detailed Steps & UI Objects:
| Step # | Action | UI Object Description | PAD V4 / Playwright Selector | Notes / Confusion Avoidance |
|:---:|---|---|---|---|
| **8.1** | Navigate | Open District Clerk Search | `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` | Marilyn Burgess District Clerk portal. |
| **8.2** | Click Tab | Select "Party Inquiry" Tab | **PAD V4 line 1117:** `input#tabParty`<br>**Selector:** `nav#tabs > input#tabParty` | Must select Party Inquiry tab; default is Case Inquiry. |
| **8.3** | Populate | Enter Party Name | **PAD V4 line 1119:** `document.getElementById("txtPartyName").value = "${VarLastName}, ${VarFirstName}";`<br>**Selector:** `input#txtPartyName` | **Format:** `"LastName, FirstName"`. |
| **8.4** | Populate | Enter Filed Date Range From | **PAD V4 line 1127:** `input#txtPartyStartDate` (SendKeys `FormattedDateHc`)<br>**Selector:** `section#secParty input#txtPartyStartDate` | Date filter: `MM/dd/yyyy`. |
| **8.5** | **SUBMIT** | **Click "Party Search" Button** | **PAD V4 line 1129:** `document.getElementById("ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch").click();`<br>**Playwright:** `input#ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnPartySearch` | **CRITICAL ID:** `#...btnPartySearch`.<br>**DO NOT CLICK:** `input#btnCaseSearch` or adjacent tab search buttons! |
| **8.6** | Extract | Parse Results Table | `html > body > form > ... > table > tbody > tr` or `table#tblResults tbody tr` | td:0 CaseNumber, td:1 CaseStyle (`a > strong`), td:5 FilingDate, td:6 CaseType. |
| **8.7** | Reset | Return to Clean State | **PAD V4 line 1201:** `document.getElementById("ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_ContentPlaceHolder2_btnSearchAgain").click();` | Clicks "Search Again" button to return to clean form. |

---

## 4. User Verification & Correction Form

If you observe any discrepancy during your individual testing of the 8 bots, please specify the portal and the corrected object ID below:

| Portal Name | Current Object / Step | Your Corrected Object ID / Name / Selector | Desired Behavior / Action |
|---|---|---|---|
| **Broward County (FL)** | Submit Button (`PersonSearchResults`) | | |
| **Dallas County (TX)** | Submit Button (`input[value='Submit']`) | | |
| **Travis County (TX)** | Submit Button (`btnSSSubmit`) | | |
| **Harris County JP (TX)** | Submit Button (`input[value='Submit']`) | | |
| **Miami-Dade County (FL)** | Tab Button vs. Submit Button (`btnSearch`) | | |
| **Harris County Clerk (TX)**| Submit Button (`btnSearch` vs. `btnClear`)| | |
| **Hillsborough County (FL)**| Submit Button (`btnSubmitPartySearch`) | | |
| **Harris District Clerk (TX)**| Submit Button (`btnPartySearch`) | | |

---

## 5. Live Single-Bot Verification Command Reference

To test any bot with visible Google Chrome right now:
```powershell
# 1. Broward
python scripts/test_court_bot.py --bot broward --party "DOE, JOHN"

# 2. Dallas
python scripts/test_court_bot.py --bot dallas --party "SMITH, ROBERT"

# 3. Travis
python scripts/test_court_bot.py --bot travis --party "JOHNSON, MICHAEL"

# 4. Harris JP
python scripts/test_court_bot.py --bot harris_jp --party "WILLIAMS, DAVID"

# 5. Miami-Dade
python scripts/test_court_bot.py --bot miami --party "GARCIA, MARIA"

# 6. Harris County Clerk
python scripts/test_court_bot.py --bot harris_cclerk --party "MARTINEZ, JOSE"

# 7. Hillsborough
python scripts/test_court_bot.py --bot hillsborough --party "DOE, JOHN" --dol "01/15/2023"

# 8. Harris District Clerk
python scripts/test_court_bot.py --bot harris_district --party "RODRIGUEZ, CARLOS"
```
