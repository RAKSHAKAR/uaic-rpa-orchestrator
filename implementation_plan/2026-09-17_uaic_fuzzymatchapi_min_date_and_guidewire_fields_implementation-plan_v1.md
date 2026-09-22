# Implementation Plan: Minimum Case Filing Date Filtering & Guidewire Schema Alignment for Fuzzy Match API Tester (`/fuzzymatchapi`)

**Implementation ID:** `IMP-2026-0917-005`  
**Date:** 2026-09-17  
**Author:** AI Agent (Antigravity)  
**Status:** Awaiting User Approval  
**Lifecycle Stage:** Plan  

---

## 1. Problem Statement & Background

In the Automation & Robot Settings console (`/settings`), the **Fuzzy Match API Tester** (`/fuzzymatchapi`) allows operators to test the RapidFuzz string comparison and date qualification engine before running production court scrapers and Guidewire dispatches.

Two critical defects and discrepancies were reported:
1. **Minimum Case Filing Date (YYYY-MM-DD) Filter Disconnect:**
   - The date filter input in Settings (`settings.matcher.min_filing_date`) is disconnected from the tester presets, which hardcode `"min_filing_date": "2010-01-01"`.
   - In the backend (`fuzzy_engine.is_case_eligible`), `min_filing_date` parsing strictly assumed `%Y-%m-%d`, failing on any date string variations or timestamps.
   - If omitted from the payload, the backend defaulted to `"2010-01-01"` instead of reading the system's configured `min_filing_date` from the settings database.
2. **Response Field Pollution & Guidewire Schema Incompatibility:**
   - The tester response returned bloated null fields:
     ```json
     "reference_string": null,
     "matches": null,
     "cases": null,
     "cases_results": null,
     "cases_evaluated": null,
     "eligible_for_guidewire": null
     ```
   - In legacy Power Automate solutions (`PA_FuzzyMatch_ActivityCreation_v1_Main`), Guidewire requires an exact, clean payload structure (`ClaimNumber`, `ExposureNumber`, `CaseItems` containing `CaseNumber`, `CaseStyle`, `CountyWebsite`, `SuitFiledDate`). Returning unneeded null fields and conflicting schemas creates data patching issues with Guidewire.

---

## 2. Legacy Power Platform & Guidewire Contract Review

Per inspection of `PowerAutomateSolutions/BotCreation_1_0_0_7/Workflows/PA_FuzzyMatch_ActivityCreation_v1_Main-EBA1AB1C-009D-F011-BBD2-7C1E52172CF3.json`:
- **Filing Date Filter Rule (Lines 586-592):**
  `formatDateTime(FilingDate, 'yyyy-MM-dd') >= '2010-01-01'` (or configured `min_filing_date`).
- **Guidewire Case Item Schema (Lines 480-485):**
  ```json
  {
    "CaseNumber": "@{items('Apply_to_each_2')?['CaseNumber']}",
    "CaseStyle": "@{items('Apply_to_each_2')?['CaseStyle']}",
    "CountyWebsite": "@{items('Apply_to_each')?['CountyWebsite']}",
    "SuitFiledDate": "@{items('Apply_to_each_2')?['FilingDate']}"
  }
  ```
- **Overall Guidewire Payload (Lines 713-718):**
  ```json
  {
    "ClaimNumber": "0123456789",
    "ExposureNumber": "001",
    "CaseItems": [
      {
        "CaseNumber": "COCE-23-019482",
        "CaseStyle": "JOHN DOE VS JANE SMITH",
        "CountyWebsite": "https://www.browardclerk.org/Web2/",
        "SuitFiledDate": "2023-05-14"
      }
    ]
  }
  ```

---

## 3. Detailed Proposed Changes

### Component 1: Core Fuzzy Engine (`backend/app/services/fuzzy_engine.py`)
- **Multi-Format Date Parsing in `is_case_eligible`:**
  - Robustly parse both `filing_date` and `min_filing_date` across `%Y-%m-%d`, `%m/%d/%Y`, `%Y/%m/%d`, `%m-%d-%Y`, and ISO strings.
  - Strip whitespace and handle date edge cases gracefully.
  - Ensure filing date comparison `parsed_dt >= min_dt` strictly evaluates year, month, and day without timezone shifts.

### Component 2: API Endpoints & Schemas (`backend/app/schemas/match.py`, `backend/app/api/v1/endpoints/matches.py`, `backend/app/main.py`)
- **FastAPI Serialization Clean-up:**
  - Add `response_model_exclude_none=True` on `@router.post("/fuzzymatchapi")` and root `@app.post("/fuzzymatchapi")`.
  - Automatically omit all `null` fields from single and batch responses.
- **Dynamic System Settings Fallback:**
  - In `fuzzy_match_direct`, if `payload.min_filing_date` is not provided, fetch the active system setting via `await get_system_settings_async()` (or sync cache fallback) instead of hardcoding `"2010-01-01"`.
- **Exact Guidewire Canonical Format for Batch Cases:**
  - When evaluating `cases`, output each case item with the exact Guidewire keys:
    - `CaseNumber`: court case identifier
    - `CaseStyle`: party caption
    - `CountyWebsite`: county clerk source portal URL
    - `SuitFiledDate`: normalized filing date (mapped from `FilingDate` or `filing_date`)
    - `score`: similarity score percentage
    - `result`: "Match Found" | "Filtered Out (Filing Date < ...)" | "No Match Found"
    - `guidewire_eligible`: boolean
    - `filter_reason`: explanation if ineligible
  - In batch mode, return only:
    `result`, `score`, `text1`, `threshold_applied`, `min_filing_date`, `guidewire_eligible`, `cases_evaluated`, `eligible_for_guidewire`, `cases`.
    Omit redundant `cases_results`, `matches`, `reference_string`, `text2`.
- **Root Parity Parity in `backend/app/main.py`:**
  - Synchronize `@app.post("/fuzzymatchapi")` with `fuzzy_match_direct` so root calls also support batch cases, date filtering, and clean Guidewire schemas.

### Component 3: Frontend Settings Console (`frontend/src/app/settings/page.tsx`, `frontend/src/types/index.ts`)
- **Dynamic Preset Generation:**
  - Update `FUZZY_PRESET_WITH_DATE_FILTER` and `FUZZY_PRESET_COURT_CASES_BATCH` generators to bind dynamically to `settings.matcher.min_filing_date`.
  - When the operator edits `Minimum Case Filing Date (YYYY-MM-DD)` input, automatically synchronize the active preset payload if currently on "With Date Filter" or "Batch Cases Evaluation".
  - Ensure clicking "Exact API Sample", "With Date Filter", and "Batch Cases Evaluation" updates the JSON editor immediately with valid, beautifully formatted payloads.
- **TypeScript Types Alignment:**
  - Update `DirectFuzzyMatchResponse` and `FuzzyMatchCaseResult` in `frontend/src/types/index.ts` to support the canonical Guidewire fields (`CaseNumber`, `CaseStyle`, `CountyWebsite`, `SuitFiledDate`).

---

## 4. Expected Output Samples

### Preset 1: Exact API Sample
```json
{
  "result": "Match Found",
  "score": 100.0,
  "text1": "Miami Dade Police Department",
  "text2": "JASMINE PHILLIPS vs MIAMI DADE POLICE DEPARTMENT et al",
  "threshold_applied": 60.0,
  "guidewire_eligible": true
}
```
*(Zero null fields, clean and minimal)*

### Preset 2: With Date Filter (Eligible)
```json
{
  "result": "Match Found",
  "score": 100.0,
  "text1": "Miami Dade Police Department",
  "text2": "JASMINE PHILLIPS vs MIAMI DADE POLICE DEPARTMENT et al",
  "threshold_applied": 60.0,
  "filing_date": "2023-05-14",
  "min_filing_date": "2010-01-01",
  "guidewire_eligible": true
}
```

### Preset 2: With Date Filter (Filtered Out)
```json
{
  "result": "Filtered Out (Filing Date < 2010-01-01)",
  "score": 100.0,
  "text1": "Miami Dade Police Department",
  "text2": "JASMINE PHILLIPS vs MIAMI DADE POLICE DEPARTMENT et al",
  "threshold_applied": 60.0,
  "filing_date": "2008-05-14",
  "min_filing_date": "2010-01-01",
  "guidewire_eligible": false,
  "filter_reason": "Filing date '2008-05-14' is prior to Minimum Case Filing Date '2010-01-01'"
}
```

### Preset 3: Batch Cases Evaluation (Guidewire Schema Format)
```json
{
  "result": "Match Found",
  "score": 100.0,
  "text1": "JOHN DOE",
  "threshold_applied": 60.0,
  "min_filing_date": "2010-01-01",
  "guidewire_eligible": true,
  "cases_evaluated": 2,
  "eligible_for_guidewire": 1,
  "cases": [
    {
      "CaseNumber": "COCE-23-019482",
      "CaseStyle": "JOHN DOE VS JANE SMITH",
      "CountyWebsite": "https://www.browardclerk.org/Web2/",
      "SuitFiledDate": "2023-05-14",
      "score": 100.0,
      "result": "Match Found",
      "guidewire_eligible": true
    },
    {
      "CaseNumber": "COCE-09-001234",
      "CaseStyle": "JOHN DOE VS ACME CORP",
      "CountyWebsite": "https://www.browardclerk.org/Web2/",
      "SuitFiledDate": "2009-02-10",
      "score": 100.0,
      "result": "Filtered Out (Filing Date < 2010-01-01)",
      "guidewire_eligible": false,
      "filter_reason": "Filing date '2009-02-10' is prior to Minimum Case Filing Date '2010-01-01'"
    }
  ]
}
```

---

## 5. Verification Plan

### Automated Tests
1. **Backend Tests:**
   - Run `pytest tests/test_fuzzymatch_api_parity.py tests/test_entry_gate_and_fuzzymatchapi.py -v`
   - Run full pytest test suite: `.venv\Scripts\pytest --tb=short -q`
2. **Backend Linting:**
   - Run `.venv\Scripts\ruff check app tests` (0 errors)
3. **Frontend Type Check:**
   - Run `npx tsc --noEmit` in `frontend/` (0 errors)
4. **PowerShell Script Syntax:**
   - Run `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (0 errors)

### Visual Verification
- Use `browser_subagent` to open `http://localhost:3000/settings`, navigate to the APIs tab, test all 3 presets ("Exact API Sample", "With Date Filter", "Batch Cases Evaluation"), verify that changing Minimum Case Filing Date updates the filter properly, and capture visual proof into `implementation_plan/Images/`.

---

## 6. Commitment to Governance Rules
- No source code will be modified until explicit user confirmation is received.
- Repository structure, protected directories, and business rules remain strictly intact.
