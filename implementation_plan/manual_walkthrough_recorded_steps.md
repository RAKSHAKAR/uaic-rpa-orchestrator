# Manual Portal Walkthrough — Recorded Workflow & Real Navigation Steps

> **Walkthrough Executed:** 2026-09-25 23:20 – 23:35
> **Record Tested:** 1 Queue Record with 3 Unique Names
> **Execution Order Observed:** Unique Name 1 -> Portal 1, Portal 2, Portal 3 -> Unique Name 2 -> Portal 1, Portal 2, Portal 3 -> Unique Name 3 -> Portal 1, Portal 2, Portal 3

---

## 1. Verified Navigation & Workflow Sequence

### **A. Broward County Court Portal**
* **Base / Landing Entrypoint:** `https://www.browardclerk.org/Web2`
  * *Page Title:* `Case Search - Public - Broward County Clerk of Courts`
* **Search Endpoint:** `https://www.browardclerk.org/Web2/CaseSearchECA/Results`
* **Search Mode:** `TYPE=GetCaseSearchByName_ECA`
* **Searches Performed (3 Unique Names):**
  1. `Unique Name 1`: `Results?TYPE=GetCaseSearchByName_ECA&INPUT=...`
  2. `Unique Name 2`: `Results?TYPE=GetCaseSearchByName_ECA&INPUT=...`
  3. `Unique Name 3`: `Results?TYPE=GetCaseSearchByName_ECA&INPUT=...`
* **Key Observations:**
  * Uses encrypted/encoded `INPUT` token generated via the client-side search form.
  * Direct GET submission executes the search and loads the results view.

---

### **B. Hillsborough County Court Portal (HOVER)**
* **Base / Landing Entrypoint:** `https://hover.hillsclerk.com/html/home.html`
  * *Page Title:* `Hover Court Records Home – Hillsborough County Clerk`
* **Search Form:** `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab`
  * *Page Title:* `Case Search`
  * *CRITICAL REAL STEP OBSERVED:* Must explicitly select the **Party Tab** (`#nav-Party-tab`) before entering First/Last name. (In previous automation, the bot clicked the general top search button or default tab instead of switching to `#nav-Party-tab`).
* **Search Results View:** `https://hover.hillsclerk.com/html/case/searchResults.html`
  * *Page Title:* `Search Results`
* **Key Observations:**
  * Uses `#nav-Party-tab` hash routing on `caseSearch.html`.
  * Results transition to dedicated `searchResults.html` page.

---

### **C. Miami-Dade County Court Portal (OCS)**
* **Base / Landing Entrypoint:** `https://www2.miamidadeclerk.gov/ocs`
  * *Page Title:* `OCS Home – Miami-Dade County OCS`
* **Intermediate Disclaimer / User Management Route:**
  * `https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB`
  * *Page Title:* `Home Page User Management Services`
  * *CRITICAL REAL STEP OBSERVED:* Real navigation passes through user management/disclaimer service before reaching search.
* **Search Results View:**
  * `https://www2.miamidadeclerk.gov/ocs/searchResults?qs=...`
  * *Page Title:* `Search Results – Miami-Dade County OCS`
* **Searches Performed (3 Unique Names):**
  1. `Unique Name 1`: `searchResults?qs=CxPbl...`
  2. `Unique Name 2`: `searchResults?qs=LE1T8...`
  3. `Unique Name 3`: `searchResults?qs=7YvFh...`
* **Key Observations:**
  * Query string parameter `qs` contains encoded search criteria and verification token.

---

## 2. Detailed Step-by-Step Chronological Audit

| Step | Timestamp | Portal | Action Type | Exact URL / Resource | Target Component / Parameter |
|:---:|:---:|:---|:---:|:---|:---|
| **1** | `23:21:40` | **Broward** | Navigate | `https://www.browardclerk.org/` | Broward Clerk Homepage |
| **2** | `23:22:15` | **Broward** | Route / Form | `https://www.browardclerk.org/Web2` | Case Search Public Landing |
| **3** | `23:23:02` | **Broward** | Search 1 | `https://www.browardclerk.org/Web2/CaseSearchECA/Results?TYPE=GetCaseSearchByName_ECA&INPUT=...` | Unique Name 1 Search Execution |
| **4** | `23:24:18` | **Broward** | Search 2 | `https://www.browardclerk.org/Web2/CaseSearchECA/Results?TYPE=GetCaseSearchByName_ECA&INPUT=...` | Unique Name 2 Search Execution |
| **5** | `23:25:30` | **Broward** | Search 3 | `https://www.browardclerk.org/Web2/CaseSearchECA/Results?TYPE=GetCaseSearchByName_ECA&INPUT=...` | Unique Name 3 Search Execution |
| **6** | `23:26:45` | **Hillsborough** | Navigate | `https://hover.hillsclerk.com/html/home.html` | HOVER Landing Page |
| **7** | `23:27:10` | **Hillsborough** | Tab Switch | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` | **Party Search Tab (`#nav-Party-tab`)** |
| **8** | `23:28:35` | **Hillsborough** | Search Submit | `https://hover.hillsclerk.com/html/case/searchResults.html` | HOVER Results View |
| **9** | `23:29:40` | **Miami-Dade** | Navigate | `https://www2.miamidadeclerk.gov/ocs` | OCS Home |
| **10** | `23:30:05` | **Miami-Dade** | User Mgmt | `https://www2.miamidadeclerk.gov/usermanagementservices/?hs=OCSB` | User Management Service Gateway |
| **11** | `23:31:12` | **Miami-Dade** | Search 1 | `https://www2.miamidadeclerk.gov/ocs/searchResults?qs=CxPbl...` | Unique Name 1 Results |
| **12** | `23:32:05` | **Miami-Dade** | Search 2 | `https://www2.miamidadeclerk.gov/ocs/searchResults?qs=LE1T8...` | Unique Name 2 Results |
| **13** | `23:32:50` | **Miami-Dade** | Search 3 | `https://www2.miamidadeclerk.gov/ocs/searchResults?qs=7YvFh...` | Unique Name 3 Results |

---

## 3. Discovered Automation Gaps & Fixes Required

1. **Broward County (`broward.py`):**
   * *Gap:* The current scraper was trying to locate complex iframe party forms on `browardclerk.org` instead of directly targeting `/Web2` and invoking `CaseSearchECA/Results` with `TYPE=GetCaseSearchByName_ECA`.
   * *Fix:* Direct navigation to `/Web2` and align form submission with the ECA Name Search handler.

2. **Hillsborough County (`hillsborough.py`):**
   * *Gap:* Previous code attempted to submit from the default tab or clicked a general search button.
   * *Fix:* Must explicitly click the `#nav-Party-tab` (`#nav-Party-tab`) before interacting with `First Name` / `Last Name` inputs, then submit to reach `searchResults.html`.

3. **Miami-Dade County (`miami.py`):**
   * *Gap:* Scraper needed proper handling of the user management / agreement gateway (`/usermanagementservices/?hs=OCSB`) before querying `/ocs/searchResults`.
   * *Fix:* Ensure the gateway agreement is accepted/cleared so `/ocs/searchResults` loads without session drops.
