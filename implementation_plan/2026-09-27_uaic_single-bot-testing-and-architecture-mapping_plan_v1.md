# UAIC Claim & RPA Orchestrator — Single Bot Testing Harness & Architecture Mapping Plan

> **Implementation ID:** `IMP-2026-0927-001`  
> **Status:** Operational & Verified  
> **Topic:** Individual 8-Bot Testing Workflow & End-to-End Architectural File Mapping  
> **Author:** Antigravity AI Pair Programmer

---

## 1. Objective

Provide a comprehensive architectural mapping and a dedicated testing harness so the user can test each of the 8 county court portal bots individually in Attended Mode (Visible Google Chrome GUI) with Anti-Captcha solving, and understand precisely which files feed input data, fill the web forms, extract court cases, and persist results.

---

## 2. Complete Architectural File Mapping

### A. Input Data Sources (Where Data Comes From)
| Purpose | File Path | Code Symbols / Logic |
|---|---|---|
| **Excel / CSV Ingestion** | [backend/app/services/excel_parser.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/excel_parser.py) | `parse_claim_file()`, `resolve_county_bot_targets()`. Converts Excel serial dates (`1899-12-30` base) to `MM/dd/yyyy`. Splits Insured, Driver, Claimant into first/last. |
| **Claim Ingestion API** | [backend/app/api/v1/endpoints/ingest.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/ingest.py) | `POST /api/v1/ingest/upload` saves rows to `ClaimRecord`. |
| **Claim Database Model** | [backend/app/models/claim.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/models/claim.py) | `ClaimRecord` ORM model. Stores `insured_first_name`, `insured_last_name`, `driver_first_name`, `driver_last_name`, `claimant_first_name`, `claimant_last_name`, `date_of_loss`, `policy_state`, `loss_location_state`. |
| **Party Deduplication** | [backend/app/services/fuzzy_engine.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/fuzzy_engine.py) | `generate_unique_names_for_claim()`. RapidFuzz 60% partial ratio deduplication yielding unique search party tuples. |
| **Search Count Derivation** | [backend/app/automation/session_runner.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py) | `derive_search_counts()` & `get_search_party_pairs()`. Calculates `DualSearch` & `TripleSearch` (1, 2, or 3 searches). |

---

### B. The 8 Court Portal Scrapers (Form Filling & Data Extraction)

| # | County Court Portal | State | Scraper Implementation File | Scraper Class | Input Form Filling Selectors | Extracted Fields & Schema Parity |
|---|---|:---:|---|---|---|---|
| **1** | **Broward County Clerk** | FL | [backend/app/automation/florida/broward.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py) | `BrowardScraper` | `input#lastName`, `input#firstName`, `input#filingDateOnOrAfterP` | **5 Fields:** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **2** | **Dallas County Odyssey** | TX | [backend/app/automation/texas/dallas.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/dallas.py) | `DallasScraper` | `#caseCriteria_SearchCriteria` (`"LastName, FirstName"`), date filter inputs | **5 Fields:** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **3** | **Travis County Odyssey** | TX | [backend/app/automation/texas/travis.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/travis.py) | `TravisScraper` | `#caseCriteria_SearchCriteria` (`"LastName, FirstName"`), date filter inputs | **5 Fields:** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **4** | **Harris County JP** | TX | [backend/app/automation/texas/harris_jp.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_jp.py) | `HarrisJPScraper` | `#caseCriteria_SearchCriteria` (`"LastName, FirstName"`), Smart Search | **4 Fields (NO CaseType):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` |
| **5** | **Miami-Dade County Clerk**| FL | [backend/app/automation/florida/miami.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py) | `MiamiDadeScraper` | `#txtLastName`, `#txtFirstName`, `#txtDateFrom` (optional login) | **5 Fields:** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **6** | **Harris County Clerk** | TX | [backend/app/automation/texas/harris_cclerk.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py) | `HarrisCountyClerkScraper` | `#ctl00_ContentPlaceHolder1_txtLastName`, `...txtFirstName`, `...txtDateFrom` | **4 Fields (NO CaseType):** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` |
| **7** | **Hillsborough County Clerk**| FL| [backend/app/automation/florida/hillsborough.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/hillsborough.py) | `HillsboroughScraper` | `#partySearch input[name='lastName']`, `...input[name='firstName']`, `...input[name='fileDateFrom']` | **5 Fields:** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **8** | **Harris District Clerk** | TX | [backend/app/automation/texas/harris_district.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_district.py) | `HarrisDistrictClerkScraper` | `#ctl00_ContentPlaceHolder1_txtPartyName` or first/last inputs | **5 Fields:** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |

---

### C. Base Automation & Browser Infrastructure
| Component | File Path | Key Roles |
|---|---|---|
| **Base Court Scraper** | [backend/app/automation/base.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/base.py) | `BaseCourtScraper`: Inherited by all 8 scrapers. Implements `biometric_fill()` (Turbo/Human typing), `detect_and_handle_captcha()` (reCAPTCHA, Turnstile, hCaptcha solving via AntiCaptcha extension), `record_stage()` (telemetry), `run_search()`. |
| **Single-Session Runner** | [backend/app/automation/session_runner.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py) | `SingleSessionBrowserRunner`: Orchestrates multi-tab Chrome session, resolves `anticaptcha-plugin_v0.83`, enforces Attended Mode (`headless=False`), and dispatches sequential searches. |
| **Browser Manager** | [backend/app/automation/browser_manager.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py) | `ChromeSession`, `TabManager`, `ExtensionManager`: Manages persistent user profiles, cleans profile lock files, and pins AntiCaptcha to Chrome toolbar. |
| **Celery Tasks** | [backend/app/tasks/scraper_tasks.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py) | Background task `run_court_scraper_task()` and `execute_court_scrapers()`. Manages distributed concurrency and portal retry logic. |

---

### D. Output Storage Destinations (Where Extracted Data Goes)
| Destination | File Path | Storage Details |
|---|---|---|
| **Raw Portal JSON Columns** | [backend/app/models/claim.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/models/claim.py) | Stored as JSON strings on `ClaimRecord`: `fl_jsonbody_broward`, `te_jsonbody_dallas`, `te_jsonbody_travis`, `te_jsonbody_harris`, `fl_jsonbody_miami`, `te_jsonbody_cclerk`, `fl_jsonbody_hillsborough`, `te_jsonbody_hcdistrict`. |
| **Portal Status Columns** | [backend/app/models/claim.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/models/claim.py) | Enum statuses: `fl_botstatus_broward`, etc. (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `BLOCKED`, `NO_RECORDS`). |
| **Normalized Court Cases Table** | [backend/app/models/court_case.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/models/court_case.py) | `ScrapedCourtCase` table: each row has `claim_id`, `portal_name`, `case_number`, `case_style`, `county_website`, `filing_date`, `case_status`, `case_type`. |
| **Fuzzy Match Engine** | [backend/app/services/fuzzy_engine.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/fuzzy_engine.py) | `match_court_cases_for_claim()` matches scraped `case_style` against Claimant ➔ Insured ➔ Driver (threshold >= 0.60, filing date >= 2010-01-01). Stored in `FuzzyMatchResult` ([backend/app/models/match_result.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/models/match_result.py)). |
| **Guidewire Cloud Payload** | [backend/app/services/guidewire_client.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/guidewire_client.py) | Formats final JSON with zero-padded 10-digit ClaimNumber and matched CaseItems for Guidewire API push. |

---

## 3. Single Bot Testing Capabilities

To test all 8 bots one by one, three methods are provided:
1. **Interactive CLI Test Harness:** `scripts/test_court_bot.py`
   - Test any of the 8 bots individually in Attended Google Chrome GUI (`headless=False`).
   - Injects custom or claim-derived party names and Date of Loss.
   - Solves live CAPTCHAs via AntiCaptcha plugin.
   - Validates extracted record counts and schema compliance (4-field vs 5-field).
2. **REST API Endpoint:**
   - `POST /api/v1/claims/{id}/run-bot/{bot_key}`
3. **Frontend Claim Detail UI:**
   - Click individual bot buttons on `http://localhost:3000/claims/:id`.
