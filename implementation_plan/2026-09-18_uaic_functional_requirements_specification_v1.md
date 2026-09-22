# Functional Requirements & System Specification — UAIC Claim & RPA Orchestrator

**Implementation ID:** `IMP-2026-0918-005`  
**Document Type:** Functional Requirements Specification (Functional Spec)  
**Version:** `v1.0.0`  
**Status:** Complete (100% Automated Testing Suite)  
**Authority:** Authoritative Functional Baseline  
**Date:** 2026-09-18  

---

## 1. Introduction & Business Context

The **UAIC Claim & RPA Orchestrator** automates court litigation discovery for auto insurance claims across Florida and Texas. It replaces legacy Microsoft Power Automate Desktop (PAD) V4 Robin flows, providing automated court docket retrieval, RapidFuzz string matching against policyholder records, and automated dispatch to Guidewire Insurance Cloud.

This specification documents all **Functional Requirements (FR-1 through FR-12)** and **Non-Functional Requirements (NFR-1 through NFR-6)** governing system behavior.

---

## 2. Functional Requirements Matrix

### FR-1: Spreadsheet File Ingestion & 5-Step Mapping Wizard
- **Input Formats**: Microsoft Excel (`.xlsx`), Comma-Separated Values (`.csv`).
- **5-Step Ingestion Workflow**:
  1. *Upload*: Drag-and-drop file upload with MIME type validation.
  2. *Mapping*: Automatic fuzzy column header detection pairing spreadsheet columns to canonical fields (`ClaimNumber`, `PolicyNumber`, `InsuredName`, `ClaimantName`, `DriverName`, `DateOfLoss`, `PolicyState`, `LossLocationState`).
  3. *Validation & Preview*: Row-level schema validation and sample preview.
  4. *Import*: Batch asynchronous database commit.
  5. *Summary*: Ingestion report displaying total records, imported rows, and invalid rows.
- **Invalid Row Isolation**: Rows with missing or malformed mandatory fields are isolated and exportable as CSV (`GET /api/v1/ingest/batches/{id}/failed-rows`) without halting the import of valid claims.

### FR-2: Dynamic State Routing Logic
Court portal scraping tasks are dynamically assigned based on policy and loss geography:
- **Florida Domestic (`policy_state == loss_location_state == 'FL'`)**: Routes to Florida portals:
  - `broward`, `hillsborough`, `miami`
- **Texas Domestic (`policy_state == loss_location_state == 'TX'`)**: Routes to Texas portals:
  - `harris_cclerk`, `dallas`, `harris_jp`, `harris_district`, `travis`
- **Cross-State (`policy_state != loss_location_state`)**: Routes to **all 8 court portals**.

### FR-3: Date of Loss (DOL) 1899-12-30 Base Conversion
- **Base Epoch**: Excel serial numbers must strictly use the **1899-12-30** base date.
- **Formatting**: Output strings must be formatted as `MM/dd/yyyy` with zero timezone shifting or day truncation.
- **String Formats**: Ingest engine must support standard date strings (`YYYY-MM-DD`, `MM/DD/YYYY`, `M/D/YY`, `YYYY/MM/DD`).

### FR-4: Public County Court Discovery (8 Portals)
The system executes automated browser sessions across 8 public court portals:

| Portal Key | Jurisdiction | Search Method | Mandatory Output Schema |
| :--- | :--- | :--- | :--- |
| `broward` | Broward County Clerk (FL) | Party Name + DOL | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| `hillsborough`| Hillsborough County Clerk (FL) | Party Name (Hover Menu) | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| `miami` | Miami-Dade County Civil (FL) | Party Name + OCS Tab | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| `dallas` | Dallas County Courts (TX) | Odyssey Smart Search | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| `travis` | Travis County Courts (TX) | Odyssey Smart Search | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| `harris_jp` | Harris County JP (TX) | Odyssey JP Smart Search | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO `CaseType`**) |
| `harris_district`| Harris County District Clerk (TX)| eDocs WebForms Search | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| `harris_cclerk` | Harris County Clerk (TX) | County Civil Records | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO `CaseType`**) |

> **Critical Parity Rule**: `harris_jp` and `harris_cclerk` must **never** include `CaseType` in their output dictionaries or database models.

### FR-5: 3-Tier RapidFuzz Deduplication Cascade & Temporal Filter
- **Cascade Priority**:
  1. **Tier 1 (Claimant)**: `rapidfuzz.fuzz.partial_ratio(claimant_full_name, case_style)`
  2. **Tier 2 (Insured)**: Evaluated only if Tier 1 score < `threshold`.
  3. **Tier 3 (Driver)**: Evaluated only if Tiers 1 and 2 scores < `threshold`.
- **Similarity Threshold**: Default `0.6` (60%). Matches `>= threshold` are stored as candidate pairs.
- **Auto-Match Threshold**: Configurable threshold (e.g. `0.85` / 85%). Matches `>= auto_match_threshold` are marked `APPROVED` and queued for Guidewire push.
- **Temporal Cutoff Filter (`min_filing_date`)**: Cases filed prior to `min_filing_date` (default `2010-01-01`) are discarded before matching to eliminate stale historical dockets.

### FR-6: Party Deduplication & Search Count Derivation (DualSearch / TripleSearch)
The system normalizes names across the three party columns (`Claimant`, `Insured`, `Driver`) using RapidFuzz `partial_ratio` at a 60% similarity threshold. This derivation governs the exact number of party searches executed on court portals:

| Party Equality Scenario | DualSearch | TripleSearch | Effective Search Queries |
| :--- | :---: | :---: | :--- |
| **All parties identical** (`Insured == Driver == Claimant`) | 1 | 1 | 1 Search Party (`Insured`) |
| **Insured == Driver**, `Claimant` different | 1 | 3 | 2 Search Parties (`Insured`, `Claimant`) |
| **Insured == Claimant**, `Driver` different | 2 | 1 | 2 Search Parties (`Insured`, `Driver`) |
| **Driver == Claimant**, `Insured` different | 2 | 1 | 2 Search Parties (`Claimant`, `Insured`) |
| **All parties different** (`Insured != Driver != Claimant`) | 2 | 3 | 3 Search Parties (`Claimant`, `Insured`, `Driver`) |

### FR-7: Human Review & Exceptions Console (`/exceptions`)
- Borderline match candidates (`threshold <= score < auto_match_threshold`) are flagged with status `PENDING_REVIEW`.
- The `/exceptions` console allows human claims adjusters to:
  - Inspect party comparison highlights and similarity percentage scores.
  - 1-Click **Approve**: Promotes status to `APPROVED` and triggers automatic Guidewire dispatch.
  - 1-Click **Reject**: Promotes status to `REJECTED` and prevents Guidewire push.

### FR-8: Guidewire Insurance Cloud Dispatch Contract
- **9-Digit Rule**: If `len(claim_number) == 9`, prepend a leading `"0"` (yielding a 10-character string) strictly in the outbound payload.
- **Exposure Number**: Default exposure `"001"`.
- **Outbound JSON Contract**:
  ```json
  {
    "ClaimNumber": "0100290914",
    "ExposureNumber": "001",
    "CaseItems": [
      {
        "CaseNumber": "COCE-22-014522",
        "CaseStyle": "MARIA MARTINEZ VS PROGRESSIVE AMERICAN",
        "CountyWebsite": "https://www.browardclerk.org/",
        "SuitFiledDate": "02/27/2022"
      }
    ]
  }
  ```
- **Supported Auth Protocols**: HTTP Bearer Token, API Key Header, HTTP Basic Auth, and OAuth2 Client Credentials Grant.

### FR-9: Queue Management & Real-Time Monitoring (`/monitor`)
- Real-time queue metrics: Total Claims, In Queue, Active Bots, Processed, Failed.
- **8-Portal Execution Matrix**: Accordion grid displaying scraper status, execution duration, and case count across all 8 court portals.
- **Queue Controls**: Start All, Pause Queue, Retrigger Failed, and Auto-Queue Toggle.

### FR-10: Selective Error Recovery (S66)
- Allows operators to re-run only failed portals for a specific claim (`POST /api/v1/claims/{id}/retry-failed`).
- **Deduplication Safeguard**: Automatically deletes existing case records for the retried portal before inserting new findings, avoiding duplicate database records.
- Automatically re-triggers RapidFuzz match evaluation upon retry completion.

### FR-11: Multi-Provider Notifications & Template Studio (`/notifications`)
- **6 Transport Providers**: Authenticated SMTP, Corporate Direct MX, Microsoft Graph API, Amazon SES API, MailDev, Local Mock.
- **Master Toggle**: `email_notifications_enabled` (immediate zero-overhead mute).
- **5 Granular Event Rules**: `guidewire_activity_created`, `guidewire_activity_failed`, `court_case_matched`, `scraper_failed`, `claim_failed`.
- **Deterministic Idempotency Key**: Prevents duplicate email alerts upon task retry.
- **HTML Template Studio**: Dynamic variable token interpolation (`{{claim_number}}`, `{{county}}`, etc.) with strict syntax validation.

### FR-12: System Settings, Branding & Operations Console (`setup_local.ps1`)
- **Dual Application Themes**: Strictly **Light** and **Dark** only; zero OS automatic detection (`prefers-color-scheme`).
- **26 Semantic Design Tokens**: Centralized Branding console (`/branding`) as the authoritative source of truth.
- **Operations Console (`setup_local.ps1`)**: Windows management launcher providing options 1 through 9 and M for service startup, stopping, cleanup, dependency management, diagnostics, and MailDev inspection.

---

## 3. Non-Functional Requirements (NFRs)

### NFR-1: Attended vs. Unattended RPA 1:1 Parity
Every scraper workflow executing in Attended GUI mode must execute with 100% identical docket extraction in Unattended Headless mode (`--headless=new`).

### NFR-2: Performance & Scalability
- Excel file ingestion: <3.0 seconds for 500 claim records.
- RapidFuzz matching: <50ms per claim docket set (C-accelerated).
- Concurrency: Supports 1 to 10 concurrent headless browser scraper sessions.

### NFR-3: Reliability & Fault Tolerance
- **Automatic Stuck Task Recovery**: Celery beat detects and resets tasks in `PROCESSING` status for >15 minutes.
- **Storage Failover**: Seamless failover to local server disk if cloud storage (S3/Azure/GCS) is unreachable.
- **Isolation**: Email notification failures must never block or abort the underlying claim workflow.

### NFR-4: Security & Zero Credential Leakage
- All sensitive credentials (`password`, `api_key`, `secret`, `token`) are masked in logs, telemetry, and API responses.
- Encrypted password transmission in transit.

### NFR-5: Audit Trail & Provenance
Every claim lifecycle transition, file upload, manual review decision, settings change, and Guidewire dispatch is recorded in `audit_logs` with client IP, operator identity, timestamp, and sanitized payload details.
