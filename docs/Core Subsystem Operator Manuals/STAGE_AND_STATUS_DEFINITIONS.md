# UAIC Claim & RPA Orchestrator — Stages, Statuses & Operational Telemetry Manual

> **Authoritative Technical & Operational Reference for Claim Lifecycle, Automation Stages, and Diagnostic Telemetry**  
> **Document Reference:** `docs/STAGE_AND_STATUS_DEFINITIONS.md`  
> **Applicable Version:** UAIC Orchestrator v4.2+ (Python 3.14 + FastAPI + Celery + Playwright + Next.js 14)

---

## 1. Executive Summary & Purpose

The **UAIC Claim & RPA Orchestrator** automates court-case discovery across 8 Florida and Texas county court portals, performs a 3-tier RapidFuzz deduplication cascade, and synchronizes validated legal dossiers with Guidewire Insurance Cloud.

Because each claim progresses through multiple distributed components (file ingestion, Celery queues, Playwright browser workers, fuzzy matching engine, and external REST APIs), the system maintains a **three-tier status architecture**:
1. **Overall Claim Record Status (`RecordStatusEnum`)**: The macro lifecycle state of the insurance claim dossier.
2. **Fuzzy Matching Status (`FuzzyMatchStatusEnum`)**: The state of the name-matching and case-style comparison pipeline.
3. **Individual Portal Bot Status (`BotStatusEnum`)**: The micro execution state of each specific county court scraper.

In addition, each scraper execution tracks **9 granular operational stages** with millisecond-precision execution telemetry.

This document serves as the definitive reference manual for system operators, claims adjusters, and AI engineering agents.

---

## 2. Claim Lifecycle Architecture & State Machine

### 2.1 State Transition Diagram

```mermaid
flowchart TD
    classDef default fill:#1e293b,stroke:#475569,stroke-width:1.5px,color:#f8fafc;
    A["Excel / CSV File Upload"] -->|"Ingestion and Validation"| B["NEW"]
    B -->|"Celery Queue Dispatch"| C["SCRAPING_IN_PROGRESS"]
    
    subgraph Browser_Automation ["8 County Court Portals Automation"]
        C --> D1["Stage 1: Browser Launch"]
        D1 --> D2["Stage 2: Portal Navigation"]
        D2 --> D3["Stage 3: Data Entry"]
        D3 --> D4["Stage 4: CAPTCHA Resolution"]
        D4 --> D5["Stage 5: Search Submit"]
        D5 --> D6["Stage 6: Docket Extraction"]
        D6 --> D7["Stage 7: Database Commit"]
    end

    D7 --> E{"Cases Extracted?"}
    E -->|"0 Cases from all Portals"| F["NO_MATCH_FOUND"]
    E -->|">= 1 Cases Extracted"| G["SCRAPING_COMPLETED"]

    subgraph Deduplication_Cascade ["RapidFuzz Matching Cascade"]
        G --> H["Stage 8: Fuzzy Matching"]
        H --> I{"Match Decision"}
        I -->|"Score >= 60% and Date >= 2010"| J["MATCH_FOUND"]
        I -->|"Borderline Score"| K["MANUAL_REVIEW"]
        I -->|"No Party Exceeds Threshold"| F
    end

    K -->|"Operator Approved in /exceptions"| J
    K -->|"Operator Rejected in /exceptions"| F

    subgraph Downstream_Sync ["Guidewire Cloud REST Dispatch"]
        J --> L["Stage 9: Guidewire Trigger"]
        L -->|"REST HTTP 200/201 Sync"| M["COMPLETED"]
        L -->|"REST HTTP 4xx/5xx Failure"| N["FAILED"]
    end

    Browser_Automation -->|"Unrecoverable Error / SLA Timeout"| N


    style Browser_Automation fill:#0f172a,stroke:#3b82f6,stroke-width:1.5px,color:#93c5fd
    style Deduplication_Cascade fill:#022c22,stroke:#10b981,stroke-width:1.5px,color:#6ee7b7
    style Downstream_Sync fill:#1e1b4b,stroke:#6366f1,stroke-width:1.5px,color:#a5b4fc```

---

## 3. Claim Record Statuses (`RecordStatusEnum`)

The `record_status` field on `claim_records` mirrors the legacy Dataverse `uaic_recordstatus` optionset and defines the macro status of a claim.

| Status Key | Legacy Dataverse Code | UI Display Label | Badge Color | Category | Detailed Definition & Trigger Condition |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `NEW` | `870300000` | **New Record Added** | Blue (`#3B82F6`) | Queued | Claim ingested from Excel/CSV or REST API. Validated and queued in Redis/PostgreSQL; awaiting worker pickup. |
| `SCRAPING_IN_PROGRESS` | `870300001` | **Scraping In Progress** | Amber (`#F59E0B`) | Active | Playwright browser worker has claimed the task and is actively launching Chrome, navigating portals, and executing searches. |
| `SCRAPING_COMPLETED` | `870300002` | **Scraping Completed** | Cyan (`#06B6D4`) | Intermediate | All routed county court scrapers have finished execution and extracted dockets. The claim is queued for the fuzzy matching cascade. |
| `MATCH_FOUND` | `870300003` | **Positive Match Found** | Emerald (`#10B981`) | Success | RapidFuzz cascade found at least 1 scraped case matching Claimant, Insured, or Driver with similarity $\ge 60\%$ and filing date $\ge 2010-01-01$. |
| `NO_MATCH_FOUND` | `870300004` | **No Match Found** | Slate (`#64748B`) | Clean Complete | All targeted portals were searched successfully, but zero court cases were filed or matched the party names. **This is a successful business outcome** (no legal exposure). |
| `MANUAL_REVIEW` | — | **Manual Review** | Purple (`#8B5CF6`) | Attention | Borderline fuzzy match detected (score between review thresholds) or ambiguous party resolution requiring operator sign-off at `/exceptions`. |
| `FAILED` | — | **Failed** | Rose (`#F43F5E`) | Exception | Fatal unrecoverable scraping exception, persistent anti-bot lockout across all retry attempts, or invalid claim structure. |
| `COMPLETED` | `870300005` | **Completed / Guidewire Updated** | Green (`#059669`) | Terminal Success | Matching court cases successfully packaged and delivered to Guidewire ClaimCenter Cloud REST API (`activity_id` generated). |

---

## 4. Fuzzy Match Statuses (`FuzzyMatchStatusEnum`)

The `fuzzy_match_status` field tracks the state of the 3-tier RapidFuzz deduplication cascade.

| Status Key | Legacy Dataverse Code | UI Display Label | Definition & Workflow Role |
| :--- | :---: | :--- | :--- |
| `NEW` | `870300000` | **Fuzzy Match New** | Initial state upon ingestion. Matching cascade has not yet evaluated any scraped cases. |
| `IN_PROGRESS` | `870300001` | **Fuzzy Match In Progress** | RapidFuzz engine is actively evaluating scraped `CaseStyle` strings against Claimant, Insured, and Driver names. |
| `COMPLETED` | `870300002` | **Fuzzy Match Completed** | Cascade completed and successfully confirmed at least one positive match ($\ge 60\%$). |
| `NO_MATCH_FOUND` | `870300003` | **No Positive Match Found** | Cascade completed; all scraped dockets fell below threshold or were filtered by the 2010-01-01 filing cutoff. |
| `PENDING_REVIEW` | — | **Pending Review** | One or more comparisons scored within the human review window and are awaiting operator adjudication on `/exceptions`. |

---

## 5. Individual County Court Bot Statuses (`BotStatusEnum`)

Each claim tracks the independent execution state of all 8 county court portals:
- **Florida**: `fl_botstatus_broward`, `fl_botstatus_hillsborough`, `fl_botstatus_miami`
- **Texas**: `te_botstatus_dallas`, `te_botstatus_travis`, `te_botstatus_harris`, `te_botstatus_cclerk`, `te_botstatus_hcdistrict`

| Status Key | UI Display Label | Badge Color | Definition & Technical Meaning |
| :--- | :--- | :--- | :--- |
| `NOT_TRIGGERED` | **Not Triggered** | Zinc (`#71717A`) | Portal was **not selected** for execution based on state routing rules (e.g., Texas portals on a Florida-only claim where Policy State = FL and Loss Location State = FL). |
| `IN_PROGRESS` | **In Progress** | Amber (`#F59E0B`) | The Playwright browser tab is currently navigating, entering party names, solving CAPTCHA, or parsing results for this specific court. |
| `COMPLETED` | **Completed** | Emerald (`#10B981`) | Scraper successfully executed the search and extracted court records ($\ge 1$ docket found). Stored in `fl_jsonbody_*` or `te_jsonbody_*`. |
| `NO_MATCH_FOUND` | **No Records Found** | Blue (`#3B82F6`) | Search submitted successfully, and the court clerk system explicitly returned **zero search results** ("No cases found matching criteria"). |
| `FAILED` | **Failed** | Rose (`#F43F5E`) | Unhandled runtime exception, missing page selector, DOM navigation crash, or page load timeout after maximum retry attempts. |
| `BLOCKED` | **Blocked / WAF** | Red (`#DC2626`) | Web Application Firewall (WAF), bot challenge (e.g., PerimeterX HUMAN Security, Cloudflare Turnstile), or IP rate limit prevented automated access. |

---

## 6. The 9 Canonical Operational Stages

During automation, the orchestrator records timestamped latency and execution status across **9 distinct operational stages** stored in `claim_records.action_timings.stages`:

| Stage # | Canonical Key | Display Name | Subsystem / Engine | Purpose & Operations Performed |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `browser_launch` | **Browser Launch** | Playwright / ChromeSession | Launches Google Chrome with isolated user profile directory, AntiCaptcha extension injection, and proxy tunneling configuration. |
| **2** | `website_navigation` | **Portal Navigation** | Playwright TabManager | Navigates to the county court base URL or deep-search endpoint; waits for network idle and DOM hydration. |
| **3** | `data_filling` | **Data Entry** | BaseCourtScraper | Types party search names (Claimant, Insured, Driver) with randomized biometric delays (50–150ms keystroke pacing) and sets search dropdowns. |
| **4** | `captcha` | **CAPTCHA Solving** | AntiCaptcha / ExtensionManager | Detects reCAPTCHA v2/v3, Turnstile, or hCaptcha widgets; monitors monotonic deadline while AntiCaptcha extension resolves challenge. |
| **5** | `submit` | **Search Submit** | BaseCourtScraper | Executes form submission click, handles confirmation modals, and waits for server-side query processing and AJAX response. |
| **6** | `result_retrieval` | **Docket Extraction** | Scraper DOM Parser | Extracts tabular rows or card dockets; parses Case Number, Case Style, Filing Date, Case Status, and Case Type; captures discovery proof screenshot. |
| **7** | `database_save` | **Database Save** | SQLAlchemy Async | Commits extracted court cases to `scraped_court_cases` table and updates raw JSON payloads (`fl_jsonbody_*` / `te_jsonbody_*`) on `claim_records`. |
| **8** | `fuzzy_matching` | **Fuzzy Matching** | RapidFuzz Engine | Executes 3-tier cascade (`Claimant > Insured > Driver`) against docket `CaseStyle` using `partial_ratio` algorithm ($\ge 60\%$ cutoff). |
| **9** | `guidewire_trigger` | **Guidewire Trigger** | GuidewireClient REST | Formats validated claim dossier into Guidewire ClaimCenter Cloud REST payload (applying 9-digit zero-prefixing) and dispatches via authenticated REST. |

### 6.1 Telemetry JSON Schema (`action_timings`)

```json
{
  "total_scraping_seconds": 42.85,
  "stages": {
    "browser_launch": {
      "name": "Browser Launch",
      "duration_seconds": 2.15,
      "status": "SUCCESS",
      "detail": "Attended Google Chrome with AntiCaptcha Extension"
    },
    "website_navigation": {
      "name": "Portal Navigation",
      "duration_seconds": 4.30,
      "status": "SUCCESS"
    },
    "data_filling": {
      "name": "Data Entry",
      "duration_seconds": 3.12,
      "status": "SUCCESS"
    },
    "captcha": {
      "name": "CAPTCHA Solving",
      "duration_seconds": 12.40,
      "status": "SUCCESS"
    },
    "submit": {
      "name": "Search Submit",
      "duration_seconds": 2.80,
      "status": "SUCCESS"
    },
    "result_retrieval": {
      "name": "Docket Extraction",
      "duration_seconds": 15.60,
      "status": "SUCCESS"
    },
    "database_save": {
      "name": "Database Save",
      "duration_seconds": 0.48,
      "status": "SUCCESS"
    },
    "fuzzy_matching": {
      "name": "Fuzzy Matching",
      "duration_seconds": 1.20,
      "status": "SUCCESS"
    },
    "guidewire_trigger": {
      "name": "Guidewire Trigger",
      "duration_seconds": 0.80,
      "status": "SUCCESS"
    }
  },
  "portals": {
    "broward": { "status": "NO_MATCH_FOUND", "cases_found": 0, "duration_seconds": 8.5 },
    "hillsborough": { "status": "BLOCKED", "cases_found": 0, "duration_seconds": 15.2 },
    "harris_district": { "status": "COMPLETED", "cases_found": 27, "duration_seconds": 19.15 }
  }
}
```

---

## 7. Screenshot Classifications: Discovery Proofs vs. Scraping Failures

The orchestrator automatically captures high-resolution full-page screenshots during browser execution. These screenshots fall into **two distinct business categories**:

```
                                Screenshot Capture
                                        |
            +---------------------------+---------------------------+
            |                                                       |
            v                                                       v
   [DISCOVERY AUDIT PROOF]                                 [SCRAPING EXCEPTION]
   * Trigger: Cases Found > 0                              * Trigger: WAF Block, Timeout, Error
   * Badge: EMERALD (Green)                                * Badge: ROSE (Red)
   * Example: Harris District Clerk (27 cases)             * Example: Hillsborough PerimeterX Block
   * Purpose: Proof of court docket discovery              * Purpose: Forensic debugging & remediation
```

### 7.1 Discovery Audit Proofs (Success)
- **When Captured**: Automatically triggered when a court scraper extracts **$\ge 1$ court cases** (`cases_count > 0`).
- **Exception Message Field**: Prefixed with `Discovery: <N> court cases found across party searches`.
- **UI Treatment**: Highlighted with an **Emerald Green Badge** labeled `DISCOVERY PROOF (SUCCESS)`.
- **Business Value**: Provides undeniable visual proof that court dockets existed on the county clerk's live website at the exact time of automation.

### 7.2 Scraping Failures & WAF Blocks (Exception)
- **When Captured**: Triggered when a scraper encounters an unhandled exception, DOM timeout, missing selector, or anti-bot security challenge.
- **Exception Message Field**: Contains the root cause error (e.g., `SecurityBlockException: Access to this page has been denied... PerimeterX`).
- **UI Treatment**: Highlighted with a **Rose Red Badge** labeled `SCRAPING FAILURE (EXCEPTION)`.
- **Business Value**: Enables operators and AI agents to instantly inspect what the browser saw (e.g., PerimeterX block, Cloudflare challenge, or clerk maintenance screen) without guessing.

---

## 8. State Routing Logic & Canonical V4 Sequential Order

### 8.1 State Routing Rules (DO NOT CHANGE)

The orchestrator routes claims based on the policy and loss location states:

```python
if policy_state == loss_location_state:
    if policy_state == "FL":
        portals = [broward, hillsborough, miami]
    elif policy_state == "TX":
        portals = [harris_cclerk, dallas, harris_jp, harris_district, travis]
else:
    # Cross-State Claim (Policy State != Loss Location State):
    # Enforces comprehensive legal discovery across ALL 8 portals
    portals = [broward, hillsborough, miami, harris_cclerk, dallas, harris_jp, harris_district, travis]
```

### 8.2 Canonical Power Automate V4 Sequential Execution Order

When multiple portals are executed, the orchestrator strictly enforces the **canonical Power Automate V4 sequential portal execution sequence** to maintain 100% parity with legacy Robin flows:

```
1. Broward County Clerk (FL)
   └── 2. Dallas County Courts (TX)
       └── 3. Travis County Courts (TX)
           └── 4. Harris County JP (TX)
               └── 5. Miami-Dade County Civil (FL)
                   └── 6. Harris County Clerk (TX)
                       └── 7. Hillsborough County Clerk (FL)
                           └── 8. Harris District Clerk (TX)
```

---

## 9. Output Schema Compliance Across Portals

Each court scraper produces docket dictionaries adhering strictly to the required schema:

| County Portal | CaseNumber | CaseStyle | FilingDate | CaseStatus | CaseType | Schema Note |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Broward County Clerk** | Yes | Yes | Yes | Yes | **Yes** | Standard 5-Field Schema |
| **Hillsborough County Clerk** | Yes | Yes | Yes | Yes | **Yes** | Standard 5-Field Schema |
| **Miami-Dade County Civil** | Yes | Yes | Yes | Yes | **Yes** | Standard 5-Field Schema |
| **Dallas County Courts** | Yes | Yes | Yes | Yes | **Yes** | Standard 5-Field Schema |
| **Travis County Courts** | Yes | Yes | Yes | Yes | **Yes** | Standard 5-Field Schema |
| **Harris District Clerk** | Yes | Yes | Yes | Yes | **Yes** | Standard 5-Field Schema |
| **Harris County JP** | Yes | Yes | Yes | Yes | **NO** | **Strictly NO CaseType (4 fields only)** |
| **Harris County Clerk** | Yes | Yes | Yes | Yes | **NO** | **Strictly NO CaseType (4 fields only)** |

> [!CAUTION]
> **Strict Contract Enforcement**: Never add `CaseType` to **Harris County JP** or **Harris County Clerk**. Adding `CaseType` to these two scrapers breaks backward compatibility with downstream Guidewire payload transforms and violates legacy Robin flow specifications.

---

## 10. Operator Diagnostic & Troubleshooting Cheat Sheet

| Symptom / Observation | Root Cause | Operator Action / Recommended Resolution |
| :--- | :--- | :--- |
| **Hillsborough Bot Status = BLOCKED** | `hover.hillsclerk.com` threw PerimeterX (HUMAN Security) bot detection screen (`Access to this page has been denied`). | Verify residential proxy pool is enabled in **Settings > Proxy Network** or switch to Attended GUI mode (`-P solo`). |
| **Screenshot cards show solid black background** | Frontend requested relative screenshot URL via port 3000 proxy rewrite that failed to resolve internal container port. | System now uses `getFullScreenshotUrl()` pointing directly to FastAPI port 8000. Hard-refresh browser (`Ctrl+F5`). |
| **Screenshot has green badge but shows under screenshots** | This is a **Discovery Audit Proof** confirming that $\ge 1$ cases were found, not a failure. | Review extracted court cases in the Court Cases docket table below. |
| **Claim Status = NO_MATCH_FOUND** | Automation completed successfully across all portals; 0 dockets filed or matched. | Normal business outcome. No adjuster action required. |
| **Claim Status = MANUAL_REVIEW** | Fuzzy match similarity score fell between 60% and 75% or party name was ambiguous. | Navigate to `/exceptions` to inspect docket details and click **Approve Match** or **Reject Match**. |
| **Claim Status = FAILED** | All portal retries exhausted or catastrophic worker crash. | Inspect **Audit Log** on `/audit` or click **Retry Claim** on `/claims/[id]`. |
