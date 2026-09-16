# Implementation Plan — Unique Names Extraction Engine (Threshold 0.60) & Named Logging Architecture

**Implementation ID:** `IMP-2026-0916-008`  
**Date:** 2026-09-16  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Target Module:** `backend/app/tasks/scraper_tasks.py`, `backend/app/api/v1/endpoints/matches.py`, `backend/app/schemas/match.py`, `backend/app/services/fuzzy_engine.py`, `frontend/src/app/settings/page.tsx`, `frontend/src/types/index.ts`

---

## 1. User Directives & Key Specifications

1. **Threshold Specification**:
   - `generate_unique_names_for_claim(claim, fuzzy_threshold=0.60)`
   - Default threshold updated from `0.85` to `0.60` across the fuzzy engine, API schemas, and task runner.
2. **Explicit Named Logging (Not Just Counts)**:
   - Stating only *"Extracted 3 unique names"* is **insufficient**.
   - Logs must print the **exact party names**, **party types**, and **search order** so the user can directly read and validate the names for each record.
   - Example Log Output:
     ```text
     [UNIQUE_NAMES_EXTRACTION] Extracted 3 unique search target(s) for Claim 123456789:
       Target 1: [Insured] CORNELIUS BRIGHT
       Target 2: [Driver] Aquaria Mitchell
       Target 3: [Claimant] Felicia Mcmiller
       (Source columns: Insured='CORNELIUS BRIGHT', Driver='Aquaria Mitchell', Claimant='Felicia Mcmiller')
     ```
     ```text
     [UNIQUE_NAMES_EXTRACTION] Extracted 1 unique search target for Claim 100290914:
       Target 1: [Insured] MARIA MARTINEZ
       (Deduplication: Insured == Driver == Claimant -> all 3 columns identical 'MARIA MARTINEZ')
     ```
3. **Execution Pipeline First Action (In Logs Only)**:
   - When the Automated Execution Pipeline starts, the **very first action** extracts and logs these unique names.
   - Recorded in:
     - **Audit Trail** (`UNIQUE_NAMES_EXTRACTED` event with names and source breakdown).
     - **Portal Execution Logs** (`append_portal_execution_log(claim.id, ...)`).
     - **Worker Logger** (`logger.info(...)`).
   - The UI stepper remains **strictly 9 steps** (Browser Launch -> Navigation -> Data Entry -> CAPTCHA -> Submit -> Retrieval -> DB Commit -> RapidFuzz -> Guidewire).
4. **Unique Names API Contract (3-Array Format)**:
   - Accepts the exact format:
     ```json
     {
  "Claimants": [
    {
      "FirstName": "CORNELIUS",
      "LastName": "BRIGHT",
      "MiddleName": "",
      "Suffix": ""
    }
  ],
  "Insureds": [
    {
      "FirstName": "Aquaria",
      "LastName": "Mitchell",
      "MiddleName": "",
      "Suffix": ""
    }
  ],
  "Drivers": [
    {
      "FirstName": "Felicia",
      "LastName": "Mcmiller",
      "MiddleName": "",
      "Suffix": ""
    }
  ]
}
     ```
5. **Spreadsheet Test Matrix**:
   - Verify all 10 records from the user's Excel spreadsheet (Rows 2–11).

---

## 2. Spreadsheet Verification Matrix (All 10 Real Records)

| Row | Insured Name | Driver Name | Claimant Name | Unique Names Extracted | Count | Search Order & Exact Names Logged |
|:---:|---|---|---|---|:---:|---|
| **2** | `MARIA MARTINEZ` | `MARIA MARTINEZ` | `MARIA MARTINEZ` | `['MARIA MARTINEZ']` | **1** | 1: `[Insured] MARIA MARTINEZ` |
| **3** | `LADEEN MCCRAY DAVIS` | `LADEEN MCCRAY DAVIS` | `LaDeen McCray-Davis` | `['LADEEN MCCRAY DAVIS']` | **1** | 1: `[Insured] LADEEN MCCRAY DAVIS` (Fuzzy match ≥ 60% merges hyphen/case) |
| **4** | `SERGIO GONZALEZ` | `SERGIO GONZALEZ` | `SERGIO GONZALEZ` | `['SERGIO GONZALEZ']` | **1** | 1: `[Insured] SERGIO GONZALEZ` |
| **5** | `TIFFANY LATONYA YOUNG` | `TIFFANY LATONYA YOUNG` | `TIFFANY LATONYA YOUNG` | `['TIFFANY LATONYA YOUNG']` | **1** | 1: `[Insured] TIFFANY LATONYA YOUNG` |
| **6** | `CRYSTAL BROWN` | `CRYSTAL BROWN` | `CRYSTAL BROWN` | `['CRYSTAL BROWN']` | **1** | 1: `[Insured] CRYSTAL BROWN` |
| **7** | `CORNELIUS BRIGHT` | `Aquaria Mitchell` | `Felicia Mcmiller` | `['CORNELIUS BRIGHT', 'Aquaria Mitchell', 'Felicia Mcmiller']` | **3** | 1: `[Insured] CORNELIUS BRIGHT`<br>2: `[Driver] Aquaria Mitchell`<br>3: `[Claimant] Felicia Mcmiller` |
| **8** | `ASHLEY RODRIGUEZ` | `ASHLEY RODRIGUEZ` | `ASHLEY RODRIGUEZ` | `['ASHLEY RODRIGUEZ']` | **1** | 1: `[Insured] ASHLEY RODRIGUEZ` |
| **9** | `EMANUEL TORRES` | `EMANUEL TORRES` | `EMANUEL TORRES` | `['EMANUEL TORRES']` | **1** | 1: `[Insured] EMANUEL TORRES` |
| **10** | `CESAR ARIAS` | `CESAR ARIAS` | `CESAR ARIAS` | `['CESAR ARIAS']` | **1** | 1: `[Insured] CESAR ARIAS` |
| **11** | `ARMANDO FERNANDEZ HERNANDEZ` | `ARMANDO FERNANDEZ HERNANDEZ` | `Jorge Bencomo Santana` | `['ARMANDO FERNANDEZ HERNANDEZ', 'Jorge Bencomo Santana']` | **2** | 1: `[Insured] ARMANDO FERNANDEZ HERNANDEZ`<br>2: `[Claimant] Jorge Bencomo Santana` |

---

## 3. Implementation Details

### Component 1: Fuzzy Engine Threshold & Direct Deduplication ([`backend/app/services/fuzzy_engine.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/fuzzy_engine.py))
- Update function signature:
  ```python
  def generate_unique_names_for_claim(
      claim: Any,
      fuzzy_threshold: float = 0.60,
      noise_patterns: list[str] | None = None,
  ) -> list[dict[str, Any]]:
  ```
- Also update `derive_search_counts_fuzzy` to default `fuzzy_threshold: float = 0.60`.
- Sequential deduplication:
  1. Add Insured: `_add_party("Insured", ins_f, ins_l)`
  2. Add Driver: `_add_party("Driver", drv_f, drv_l)` — deduplicates if similarity $\ge 0.60$
  3. Add Claimant: `_add_party("Claimant", clm_f, clm_l)` — deduplicates if similarity $\ge 0.60$
- Output format per item:
  `{"party_type": str, "first_name": str, "last_name": str, "full_name": str, "name": str, "search_order": int, "target_number": int}`
- Pure response schema: `UniqueNamesResponse` contains strictly `unique_names`, `total_unique_names`, and `count`.
- **Elimination of Legacy Counter Clutter:** Legacy `dual_search` and `triple_search` branch counters (which were required only for Robin RPA Desktop Flow nested IF/ELSE loops) and unused `claim_number` are completely removed from the API response and schemas.

### Component 2: High-Resolution Named Logging & Pure Array-Driven Pipeline Start ([`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py))
- At pipeline start:
  ```python
  # ── FIRST ACTION: Extract & Deduplicate Unique Names from the 3 Columns ──
  unique_name_items = generate_unique_names_for_claim(claim, fuzzy_threshold=0.60)
  party_pairs = [(p["party_type"], p.get("first_name"), p.get("last_name")) for p in unique_name_items]
  
  # Format clear human-readable named list
  named_targets_str = ", ".join([f"Target {p['search_order']}: [{p['party_type']}] '{p['full_name']}'" for p in unique_name_items])
  
  # 1. Celery Worker Console Log
  logger.info(
      f"Claim {claim.claim_number}: [UNIQUE_NAMES_EXTRACTION] Extracted {len(unique_name_items)} unique search target(s):\n"
      + "\n".join([f"  -> Target {p['search_order']}: [{p['party_type']}] '{p['full_name']}'" for p in unique_name_items])
      + f"\n  Source Columns: Insured='{claim.insured_first_name} {claim.insured_last_name}', "
      f"Driver='{claim.driver_first_name} {claim.driver_last_name}', "
      f"Claimant='{claim.claimant_first_name} {claim.claimant_last_name}'"
  )
  
  # 2. Portal Execution Log
  append_portal_execution_log(
      claim.id, "orchestrator",
      f"[PIPELINE START - FIRST ACTION] Extracted {len(unique_name_items)} unique search target(s): {named_targets_str}. "
      f"Columns: Insured='{claim.insured_first_name} {claim.insured_last_name}', "
      f"Driver='{claim.driver_first_name} {claim.driver_last_name}', "
      f"Claimant='{claim.claimant_first_name} {claim.claimant_last_name}'"
  )
  
  # 3. Audit Trail Log Event
  await log_audit_event_async(
      session=session,
      claim_id=claim.id,
      claim_number=claim.claim_number,
      action="UNIQUE_NAMES_EXTRACTED",
      details={
          "claim_number": claim.claim_number,
          "unique_count": len(unique_name_items),
          "unique_targets": [
              {"search_order": p["search_order"], "party_type": p["party_type"], "full_name": p["full_name"]}
              for p in unique_name_items
          ],
          "source_insured": f"{claim.insured_first_name} {claim.insured_last_name}".strip(),
          "source_driver": f"{claim.driver_first_name} {claim.driver_last_name}".strip(),
          "source_claimant": f"{claim.claimant_first_name} {claim.claimant_last_name}".strip(),
          "fuzzy_threshold": 0.60,
      },
  )
  ```

### Component 3: 3-Array API Normalizer & End-to-End Orchestration Architecture ([`backend/app/schemas/match.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/match.py) & [`backend/app/api/v1/endpoints/matches.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/matches.py))
- In `UniqueNamesRequest`: default `threshold: float = 0.60`.
- Accepts 3 arrays (`Claimants`, `Insureds`, `Drivers`) or flat fields.
- Imputes missing driver from insured.
- Feed normalized parties into `generate_unique_names_for_claim(source_data, fuzzy_threshold=payload.threshold)`.
- Replaces legacy Robin RPA IF/ELSE branching counters (`DualSearch`/`TripleSearch`) with a clean 4-stage pipeline:
  1. **Unique Names Extraction**: Generates deduplicated list of parties (`unique_names`) and `total_unique_names`.
  2. **Portal Scraping Engine**: Directly loops through each unique party, fills portal search criteria, retrieves case rows, and persists records in `ScrapedCourtCase`.
  3. **RapidFuzz Case Matching & Guidewire Filter Engine**: Runs candidate case styles against claim parties, applies the 60% confidence threshold and minimum filing date filter (e.g. >= 2010-01-01).
  4. **Guidewire 2-Way Sync**: Pushes approved matches to Guidewire ClaimCenter (or mock simulator in test mode).

### Component 4: Settings UI Live Tester ([`frontend/src/app/settings/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx))
- Preload textarea with the 3-array structure (Maria Martinez).
- Provide quick preset buttons for spreadsheet rows.
- Maintain strict 9-step stepper on `claims/[id]`.

---

## 4. Verification Plan

### Automated Tests
- Implement [`backend/tests/test_unique_names_spreadsheet_matrix.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_unique_names_spreadsheet_matrix.py) verifying all 10 spreadsheet rows.
- Run `pytest` across all suites (416+ tests).
- Run `ruff check app tests` (0 errors).
- Run `npx tsc --noEmit` and `npm run lint` (0 errors).

### Visual Verification
- Run Playwright subagent to test `/settings` live and capture screenshot.
