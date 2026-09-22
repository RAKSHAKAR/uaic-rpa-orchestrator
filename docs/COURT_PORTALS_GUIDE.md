# Public County Court Portals Operator & Architectural Manual

> **Authoritative Technical Guide for UAIC Court-Case Discovery RPA Automation**  
> Covers all 8 Florida and Texas County Court Scrapers, Playwright Browser Orchestration, Anti-Bot & AntiCaptcha Bypass, and Strict Output Schema Compliance.

---

## 1. Executive Summary & Architectural Overview

The UAIC Claim & RPA Orchestrator automates court-case discovery across **8 county court portals** spanning Florida and Texas. This subsystem is a 100% production-grade replacement for legacy Microsoft Power Automate Desktop (PAD) V4 Robin flows, eliminating fragile Windows UI desktop automation in favor of robust, asynchronous Playwright browser orchestration.

```
+-------------------------------------------------------------------------------+
|                             Celery Scraper Worker                             |
|                                                                               |
|   +-------------------+     +--------------------+     +------------------+   |
|   |   Claim Record    | --> | BaseCourtScraper   | --> | ChromeSession    |   |
|   |  (State Routing)  |     | (Biometric Input)  |     | (TabManager)     |   |
|   +-------------------+     +--------------------+     +------------------+   |
|                                       |                          |            |
|                                       v                          v            |
|                            +---------------------+     +------------------+   |
|                            | AntiCaptcha Plugin  |     | Real Chrome /    |   |
|                            | (LevelDB Synced)    |     | Headless New     |   |
|                            +---------------------+     +------------------+   |
+---------------------------------------|---------------------------------------+
                                        | (Encrypted TLS / Proxy Tunnel)
                                        v
+-------------------------------------------------------------------------------+
|                       8 Public County Court Portals                           |
|                                                                               |
|   [Florida (3 Portals)]                    [Texas (5 Portals)]                |
|   * Broward County Clerk                   * Dallas County Odyssey Portal     |
|   * Hillsborough County Clerk (Hover)      * Travis County Odyssey Portal     |
|   * Miami-Dade County Civil (OCS)          * Harris County JP (No CaseType)   |
|                                            * Harris District Clerk (eDocs)    |
|                                            * Harris County Clerk (No CaseType)|
+-------------------------------------------------------------------------------+
```

---

## 2. The 8 County Court Portals Matrix

| County Portal | State | Scraper Class | Default Base URL | Search Strategy | Output Schema Fields |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Broward County Clerk** | **FL** | `BrowardScraper` | `https://www.browardclerk.org/` | Party Name + DOL cutoff | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Hillsborough County Clerk** | **FL** | `HillsboroughScraper` | `https://hover.hillsclerk.com/` | Party Name + Hover Navigation | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Miami-Dade County Civil** | **FL** | `MiamiDadeScraper` | `https://www2.miamidadeclerk.gov/ocs/` | OCS Portal + Party Name | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Dallas County Courts** | **TX** | `DallasScraper` | `https://courtsportal.dallascounty.org/` | Odyssey Smart Search | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Travis County Courts** | **TX** | `TravisScraper` | `https://odysseyweb.traviscountytx.gov/` | Odyssey Smart Search | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Harris County JP** | **TX** | `HarrisJPScraper` | `https://jpodysseyportal.harriscountytx.gov/` | Odyssey JP Smart Search | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO `CaseType`**) |
| **Harris District Clerk** | **TX** | `HarrisDistrictScraper` | `https://www.hcdistrictclerk.com/` | eDocs Search Interface | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Harris County Clerk** | **TX** | `HarrisCClerkScraper` | `https://www.cclerk.hctx.net/` | County Civil Search | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO `CaseType`**) |

---

## 3. Base Scraper Framework (`BaseCourtScraper`)

All 8 court scrapers inherit from `BaseCourtScraper` defined in [`backend/app/automation/base.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/base.py).

### Core Responsibilities
1. **Biometric Human-Like Typing**:
   ```python
   await self.biometric_fill(locator, text, delay_range=(40, 90))
   ```
   Simulates variable keystroke latency and natural mouse movements to defeat client-side behavioral bot detection.
2. **Standardized Execution Telemetry**:
   Records high-resolution timestamps, request durations, and stage metrics (`website_navigation`, `form_population`, `captcha_resolution`, `result_retrieval`).
3. **Automated Error Screenshots**:
   Captures viewport screenshots upon any navigation failure, element timeout, or CAPTCHA block, immediately uploading the frame via `StorageService` and attaching it to the `ErrorScreenshot` database model.
4. **Security Block Detection**:
   Monitors HTTP status codes and DOM HTML for Cloudflare challenges, 429 rate limits, and WAF blocks, raising `SecurityBlockException` with configurable cooldown periods.

---

## 4. Anti-Bot Detection & AntiCaptcha Extension Integration

Court websites employ diverse bot mitigation mechanisms (Cloudflare Turnstile, Google reCAPTCHA v2/v3, and hCaptcha). The orchestrator handles these with a dual defense:

### A. Manifest v3 AntiCaptcha Extension Loading
- **Extension Path**: `anticaptcha-plugin_v0.83/` (Protected repository directory).
- **Automated LevelDB & Preferences Key Injection**:
  During Chrome profile initialization (`browser_manager.py`), the system dynamically writes the configured AntiCaptcha API key into Chrome's `Preferences` JSON:
  ```json
  {
    "extensions": {
      "settings": {
        "gcpdbjbmekkdlkpldjgffhmapgpdlcpj": {
          "account_key": "YOUR_ANTICAPTCHA_API_KEY",
          "auto_submit": true
        }
      }
    }
  }
  ```
- **Toolbar Pinning**: Automatically registers `kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj` inside Chrome's `pinned_actions` array to ensure active background worker execution.

### B. 5-Attempt Resilient CAPTCHA Retry Loop
When a CAPTCHA challenge is detected:
1. Locates `g-recaptcha-response` or `h-captcha-response` textarea elements.
2. Waits up to 120 seconds per attempt for the extension solver to inject the token.
3. If unsolved, triggers page refresh or re-solves up to 5 attempts before raising a controlled error.

---

## 5. Florida Court Portals Deep-Dive

### 1. Broward County Clerk of Courts (`florida/broward.py`)
- **Portal URL**: `https://www.browardclerk.org/Web2/CaseSearchECA/Index/`
- **Search Strategy**: Populates `lastName`, `firstName`, and optional `filingDateOnOrAfterP` (Date of Loss).
- **Result Parsing**: Scrapes the responsive results table, extracting:
  - `CaseNumber`: Uniform Case Number (e.g., `COCE-22-014522`).
  - `CaseStyle`: Litigation title (e.g., `MARIA MARTINEZ VS PROGRESSIVE AMERICAN INSURANCE COMPANY`).
  - `FilingDate`: Formatted as `MM/dd/yyyy`.
  - `CaseStatus`: Disposed, Pending, or Closed.
  - `CaseType`: County Civil, Circuit Civil, Small Claims.

### 2. Hillsborough County Clerk (Hover Portal) (`florida/hillsborough.py`)
- **Portal URL**: `https://hover.hillsclerk.com/`
- **Dynamic Optimization**: Intercepts and serves cached JavaScript bundles (`hillsborough_bundle.js`) when local caches exist, reducing initial portal load times from 15s to <2s.
- **Hover Dropdown Navigation**: Simulates mouse hover over `#nav-records` and clicks `Case Search`.
- **Result Schema**: Full 5-field schema including `CaseType`.

### 3. Miami-Dade County Civil (OCS Portal) (`florida/miami.py`)
- **Portal URL**: `https://www2.miamidadeclerk.gov/ocs/`
- **Authentication**: Supports both public guest sessions and authenticated staff logins (`requires_login=True`).
- **Date Range Windowing**: Computes filing search windows matching Power Automate V4 logic (Date of Loss to current date).
- **Result Schema**: Full 5-field schema including `CaseType`.

---

## 6. Texas Court Portals Deep-Dive

### 1. Dallas County Odyssey Portal (`texas/dallas.py`)
- **Portal URL**: `https://courtsportal.dallascounty.org/DALLASPROD/Dashboard/29`
- **Interface**: Tyler Technologies Odyssey Smart Search.
- **Query Format**: `LastName, FirstName` formatted string in `#caseCriteria_SearchCriteria`.
- **Result Schema**: Full 5-field schema (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).

### 2. Travis County Odyssey Portal (`texas/travis.py`)
- **Portal URL**: `https://odysseyweb.traviscountytx.gov/OdysseyPortal/Home/Dashboard/29`
- **Interface**: Odyssey Smart Search.
- **Query Format**: `LastName, FirstName` search with automated modal popup handling.
- **Result Schema**: Full 5-field schema (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).

### 3. Harris County Justice of the Peace (JP) (`texas/harris_jp.py`)
- **Portal URL**: `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29`
- **Critical Schema Rule**: **DO NOT INCLUDE `CaseType`**.
- **Schema Output**:
  ```json
  {
    "CaseNumber": "221100123456",
    "CaseStyle": "JOHN DOE VS JANE SMITH",
    "FilingDate": "04/12/2022",
    "CaseStatus": "Civil - Filed"
  }
  ```
- **Rationale**: Harris JP courts do not categorize cases by distinct CaseType strings. Adding `CaseType: null` or `"N/A"` violates the Guidewire ingest contract and breaks legacy Power Automate downstream compatibility.

### 4. Harris County District Clerk (eDocs) (`texas/harris_district.py`)
- **Portal URL**: `https://www.hcdistrictclerk.com/edocs/public/CaseDetails.aspx`
- **Interface**: Custom Harris County eDocs ASP.NET WebForms portal.
- **Result Schema**: Full 5-field schema including `CaseType` (e.g., `Civil - Injury or Damage`).

### 5. Harris County Clerk (Civil Records) (`texas/harris_cclerk.py`)
- **Portal URL**: `https://www.cclerk.hctx.net/applications/websearch/CourtSearch.aspx`
- **Critical Schema Rule**: **DO NOT INCLUDE `CaseType`**.
- **Schema Output**:
  ```json
  {
    "CaseNumber": "1198765",
    "CaseStyle": "ACME INS CO VS DOE",
    "FilingDate": "08/19/2021",
    "CaseStatus": "Disposed"
  }
  ```

---

## 7. Attended GUI vs. Unattended Headless 1:1 Parity

The system guarantees **100% identical scraping results** regardless of execution mode:

| Operational Dimension | Attended GUI Mode | Unattended Headless Mode |
| :--- | :--- | :--- |
| **Launch Command** | `headless=False` (Visible Chrome Window) | `--headless=new`, `context_headless=False` |
| **Extension Loading** | Native Chrome toolbar extension | Manifest v3 active service worker verified |
| **CAPTCHA Resolution** | Visual AntiCaptcha solving badge | Automated LevelDB-backed background solving |
| **Target Environment** | Developer desktop, local operator | Docker containers, CI/CD runners, Windows Service |
| **Parity Verification** | `scripts/verify_attended_unattended_parity_e2e.py` | 100% identical docket rows across all 8 portals |

---

## 8. Selective Error Recovery (S66)

If 1 or 2 county portals fail (due to temporary portal maintenance, network blips, or CAPTCHA timeouts):
1. The operator triggers `POST /api/v1/claims/{id}/retry-failed`.
2. The orchestrator inspects the claim's execution history and re-runs **only the failed portals**.
3. **Deduplication Safeguard**: Before saving retried cases, the system purges existing rows for that specific portal, guaranteeing zero duplicated court cases in the database.
4. **Auto-Cascade Trigger**: Successfully extracted cases automatically feed into the RapidFuzz cascade engine.

---

## 9. Operator Diagnostics & Reachability Testing

1. **Ping Single Portal**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/settings/test-portal" \
     -H "Content-Type: application/json" \
     -d '{"portal_key": "hillsborough"}'
   ```
2. **Launch Live Browser Test (GUI or Headless)**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/settings/test-browser" \
     -H "Content-Type: application/json" \
     -d '{"headless": false, "portal_key": "broward"}'
   ```
3. **Run 8-Portal Health Probes**:
   Visit `/health` on the web console to view real-time HTTP latency and availability for all 8 court portals.
