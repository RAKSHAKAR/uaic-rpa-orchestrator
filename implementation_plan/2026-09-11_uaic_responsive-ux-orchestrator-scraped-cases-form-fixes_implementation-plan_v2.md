# Implementation Plan — Responsive UI/UX, Data Formats & Core Orchestrator Fixes (v2)

**Implementation ID:** `IMP-2026-0911-002`  
**Date:** 2026-09-11  
**Status:** `Complete`  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Reference Prompt:** `# 03 - RESPONSIVE UI/UX, DATA FORMATS, AND CORE ORCHESTRATOR FIXES`  
**Parent Plan:** [`implementation_plan/2026-09-11_uaic_responsive-ux-orchestrator-scraped-cases-form-fixes_implementation-plan_v1.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-11_uaic_responsive-ux-orchestrator-scraped-cases-form-fixes_implementation-plan_v1.md)

---

## 1. Executive Summary & Verification Baseline

A complete diagnostic audit of Prompt 03 requirements was executed across the backend test suite, frontend TypeScript compiler, and PowerShell syntax verifiers:
- **Backend Tests:** 100% passed (exit code 0 across all 27 test suites).
- **Backend Ruff Lint:** 0 errors (all checks passed).
- **Frontend TypeScript (`tsc --noEmit`):** 0 errors.
- **PowerShell Syntax Check (`check_ps1_syntax.ps1`):** 0 errors.

### Existing Functionality Verified As Already Operational:
1. **Full Viewport Width:** All pages (`/`, `/monitor`, `/claims/[id]`, `/exceptions`, `/audit`, `/health`, `/settings`, `/branding`, `/upload`) utilize full active screen real estate (`w-full max-w-none flex-1`).
2. **Mobile Navigation & Clearance:** `MobileBottomNav` with safe-area insets (`env(safe-area-inset-bottom)`) and `ResponsiveShell` mobile bottom padding (`pb-[calc(4.75rem+env(safe-area-inset-bottom,0px))]`) prevent content overlap.
3. **Dark/Light Mode Parity:** 100% theme parity and zero OS auto-preference across all tables, inputs, and modals.
4. **Dashboard Real Data:** Connected to live metrics (`getClaimStats`, `getClaims`, `getLiveQueue`) with dynamic polling.
5. **Monitor Auto-Queue:** Enabled by default in Redis and frontend state (`useState(true)`). Reusable `AsyncExportModal` component is implemented.
6. **Claim Detail View Stages & Telemetry:** Multi-stage telemetry modal with structured stage progression and full JSON diagnostics.
7. **Scraped Court Cases Redesign:** Enterprise table with column sorting, multi-select filtering (Counties, Status, Type), Global Search, pagination (10 to 500 rows), and "View Raw JSON" button. Standalone broken `sort:descending` button removed.
8. **Top/Bottom Export Parity:** Both call `handleExportClaim(format)` hitting the same endpoint. PDF is removed from bottom toolbar and only available in the top toolbar.
9. **Deprecated Field Cleanup:** 'Loss Location City', 'Loss Location County', 'Garaging City', and 'Garaging State' cleanly removed from New Form, Edit Form, and Ingestion Mapping definitions.
10. **Fuzzy Match & Anti-Captcha APIs:** `GET /matches/extract-names`, `POST /matches/fuzzy-search`, `POST /settings/test-anticaptcha`, and `POST /settings/validate-extension` are fully wired.

---

## 2. Gap Analysis & Targeted Fixes

Through granular inspection of the active codebase against Prompt 03 specifications, the following specific gaps were identified for resolution:

| Item | Current State | Target State | Resolution Plan |
|---|---|---|---|
| **Exceptions Excel Export** | `/exceptions` has NO export functionality | Excel (`xlsx`), CSV, and JSON export buttons on `/exceptions` page | Add backend `GET /api/v1/matches/export` endpoint with openpyxl streaming, and export toolbar on `exceptions/page.tsx` |
| **State Routing Normalization** | Mixed string variations (e.g. `policy_state="FL"` and `loss_location_state="Florida"`) trigger cross-state fallback to all 8 portals | Mixed state representations for Florida or Texas correctly resolve to same-state routing | Implement robust `_normalize_state_code()` helper in `excel_parser.py` mapping `FL`/`Florida` -> `FL` and `TX`/`Texas` -> `TX` |
| **Filing Date Fallback Serialization** | `ScrapedCaseResponse` in `claims.py` checks 5 raw keys | Full 10-key fallback matching `scraper_tasks.py` | Add `DateFiled`, `date_filed`, `Filed`, `filed`, `filed_date` keys to `claims.py` serialization |
| **Backend Unit Testing** | Existing 3 tests in `test_imp_2026_0911_001.py` | Full test coverage for new match export formats and state routing normalization | Add test cases for `GET /api/v1/matches/export?format=xlsx|csv|json` and mixed state normalization |

---

## 3. Proposed Modifications

### A. Backend — `backend/app/`

#### 1. `backend/app/api/v1/endpoints/matches.py` [MODIFY]
- Add endpoint `GET /api/v1/matches/export`:
  - Query parameters: `format: "xlsx" | "csv" | "json"`, `review_status: str | None`.
  - Queries `MatchPair` joined with `ScrapedCourtCase` and `ClaimRecord`.
  - Builds structured report with columns:
    * `Match ID`, `Claim Number`, `Court Case Number`, `County Name`, `Party Type`, `Party Name`, `Case Style`, `Similarity Score (%)`, `Filing Date`, `Review Status`, `County Website`.
  - For `xlsx`: Generates formatted Excel workbook via `openpyxl` with header styling, autofit column widths, and proper cell types.
  - For `csv`: Streams UTF-8 encoded CSV.
  - For `json`: Streams formatted JSON array.
  - Returns `StreamingResponse` with appropriate MIME type and `Content-Disposition: attachment; filename="fuzzy_match_exceptions_<date>.<format>"`.

#### 2. `backend/app/services/excel_parser.py` [MODIFY]
- Enhance `resolve_county_bot_targets(policy_state, loss_state)`:
  - Add `_normalize_state(val: str | None) -> str`:
    - `"FL"`, `"FLORIDA"`, `"Fl"`, `"florida"` -> `"FL"`
    - `"TX"`, `"TEXAS"`, `"Tx"`, `"texas"` -> `"TX"`
  - Compare normalized state codes so `policy_state="FL"` and `loss_location_state="Florida"` matches same-state Florida (Broward, Hillsborough, Miami-Dade).
  - Strictly preserve critical business rule: Miami-Dade is Florida (never Texas).

#### 3. `backend/app/api/v1/endpoints/claims.py` [MODIFY]
- In `ClaimResponse` builder (line 151), expand `filing_date` raw payload fallback keys to include:
  `FilingDate`, `filing_date`, `Filing Date`, `SuitFiledDate`, `suit_filed_date`, `DateFiled`, `date_filed`, `Filed`, `filed`, `filed_date`.

---

### B. Frontend — `frontend/src/`

#### 1. `frontend/src/lib/api.ts` [MODIFY]
- Add `exportMatches(params: { format: 'xlsx' | 'csv' | 'json'; status?: string }): Promise<Blob>`:
  - Calls `GET /matches/export` with `responseType: "blob"`.

#### 2. `frontend/src/app/exceptions/page.tsx` [MODIFY]
- Add Export toolbar in page header next to "Refresh":
  - **Export Excel (`.xlsx`)** button with emerald styling and `FileSpreadsheet` icon.
  - **Export CSV (`.csv`)** button with sky styling and `FileText` icon.
  - **Export JSON (`.json`)** button with amber styling and `FileCode` icon.
- Implement `handleExport(format)` downloading formatted file using browser Blob URL with automatic memory cleanup.

---

### C. Testing — `backend/tests/`

#### 1. `backend/tests/test_imp_2026_0911_002.py` [NEW]
- Test `GET /api/v1/matches/export?format=xlsx` (returns 200 OK, valid Excel binary header `PK...`).
- Test `GET /api/v1/matches/export?format=csv` (returns 200 OK, valid CSV with headers).
- Test `GET /api/v1/matches/export?format=json` (returns 200 OK, valid JSON array).
- Test `resolve_county_bot_targets` with mixed inputs:
  - `("FL", "Florida")` -> Florida 3 bots (`Yes`), Texas 5 bots (`No`).
  - `("TX", "Texas")` -> Texas 5 bots (`Yes`), Florida 3 bots (`No`).
  - `("FL", "TX")` -> Cross-state: all 8 bots (`Yes`).
  - Ensure Miami-Dade is Florida.

---

## 4. Verification Plan

### Automated Verification:
```bash
# 1. Backend targeted tests
cd backend
.venv\Scripts\pytest tests/test_imp_2026_0911_002.py -v

# 2. Backend full suite (all 27+ test suites)
.venv\Scripts\pytest --tb=short -q

# 3. Backend lint check
.venv\Scripts\ruff check app tests

# 4. Frontend TypeScript validation
cd ../frontend
npx tsc --noEmit

# 5. Frontend production build
npm run build

# 6. PowerShell syntax validation
cd ..
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```

### Visual Verification:
- Verify `/exceptions` in browser:
  - Header displays "Export Excel", "Export CSV", "Export JSON" buttons.
  - Test clicking "Export Excel" to verify file download.
  - Test Light and Dark mode appearance.
