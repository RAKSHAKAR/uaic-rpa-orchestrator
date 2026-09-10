# Implementation Record

Implementation ID:   IMP-2026-0909-003
Project:             UAIC Claim & RPA Orchestrator
Module:              Frontend (Next.js 14) + Backend (FastAPI + Celery)
Feature / Issue:     Prompt 03 — Responsive UI/UX, Data Formats, Orchestrator & Scraped Cases Fixes
Document Type:       Implementation Plan
Version:             v1
Status:              Awaiting Approval
Created:             2026-09-09
Last Updated:        2026-09-09
AI Agent:            Antigravity (Claude Sonnet 4.6 Thinking)
Approval Status:     Pending
Approved By:         Pending
Approval Date:       Pending
Verification Status: AI Generated — Awaiting Human Verification

---

## Revision History

| Version | Date       | Change           | Reason           |
|---------|------------|------------------|------------------|
| v1      | 2026-09-09 | Initial plan     | User request 03  |

---

## 1. Problem / Request Summary

User request 03 specifies 6 categories of fixes across the full stack:

1. **Global Responsive Design & Theme** — Full viewport width, mobile footer nav, dark/light parity
2. **Page-Specific Fixes** — Dashboard, Audit/Exceptions, Monitor, Claim Detail
3. **Orchestrator & Routing Logic** — State routing validation, Guidewire payload protection
4. **Scraped Public Court Cases UI Redesign** — Portal grouping, sorting, filtering, search, pagination, View Raw JSON
5. **Form & API Adjustments** — Remove 4 fields from forms/ingestion; create fuzzy name extraction API; Anti-Captcha settings UI
6. **Dashboard, Exports & UI Refinements** — Dashboard real data, export popup as reusable component, claim detail export parity

---

## 2. Current State Diagnosis (from code inspection)

### 2a. Already Working (VERIFIED)
- `MobileBottomNav` exists, is rendered in `ResponsiveShell`, and has safe-area-inset support
- `AsyncExportModal` component exists and is imported in both Dashboard and Monitor — already a reusable component
- `MultiSelectDropdown` component exists and is used in Audit and Exceptions pages
- Audit page has Excel/CSV/JSON export handlers (handleExport) — fully implemented
- Exceptions page has column sorting and multi-select filters — already implemented
- State routing logic in `backend/app/services/excel_parser.py::resolve_county_bot_targets` correctly routes FL->3 bots, TX->5 bots, cross-state->all 8. Miami-Dade is correctly in FL group.
- Dashboard already loads real API data via `api.getClaimStats()`, `api.getClaims()`, `api.getLiveQueue()`
- Auto Queue default is `true` in monitor page (line 62: `useState(true)`)
- View Stages button EXISTS at line 1441 in claim detail
- Filing date is captured by all 8 scrapers in the automation layer

### 2b. Issues Found / Gaps

**CLAIM DETAIL (`/claims/[id]`):**
- The `inspectedStage` state is SET by the "View Stages" button but there is NO modal or panel that READS and RENDERS it. The variable `inspectedStage` is set via `setInspectedStage(...)` but is never consumed in JSX — this is the root cause of the broken "View Stages" button.
- Top export toolbar (lines 766-820) includes PDF button — this is CORRECT (keep at top).
- The bottom floating export group (if it exists) needs PDF removed.
- `formData` state includes `loss_location_city` (line 181, 205) and `loss_location_county` — form fields present in Edit modal at lines ~3022-3023.
- Garaging fields are NOT present in claim detail form (already cleaned) — only need removal from Monitor page forms.

**FORM FIELDS TO REMOVE FROM UI:**
Fields to remove from form UI only (NOT from DB model):
- `loss_location_city` — present in Claim Detail Edit form + Monitor Create/Edit form
- `loss_location_county` — present in Monitor Create/Edit form  
- `garaging_city` — present in Monitor Create/Edit form
- `garaging_state` — present in Monitor Create/Edit form

**SCRAPED COURT CASES (CLAIM DETAIL):**
- "View Raw JSON" button does not exist — only the case detail modal exists
- A standalone sort dropdown button exists that needs removal in favor of column header sorting
- The grouped view exists but needs a portal name/link badge in the table view

**FUZZY MATCH APIS:**
- No `/api/v1/matches/extract-names` endpoint exists
- No legacy Power Automate fuzzy match search endpoint exists
- Only `/pending` and `/{id}/review` routes exist in matches.py

**ANTI-CAPTCHA EXTENSION:**
- No UI section exists in Settings > Automation tab for anti-captcha extension
- `anticaptcha-plugin_v0.83` folder exists in project root (reference implementation)
- No backend endpoint for anti-captcha configuration or test exists

**MONITOR PAGE EXPORTS:**
- AsyncExportModal is already used — no change needed here

---

## 3. Gap Analysis

| Gap | Impact | Action |
|-----|--------|--------|
| `inspectedStage` state set but no modal renders it | "View Stages" button broken — clicks produce no output | **FIX: Add modal** |
| `loss_location_city/county`, `garaging_city/state` in Create/Edit forms | UI shows unwanted fields per requirement | **FIX: Remove from form UI** |
| View Raw JSON missing on scraped cases | Debugging/verification blocked | **FIX: Add JSON modal button** |
| No `/api/v1/matches/extract-names` endpoint | Feature not implemented | **FIX: Add endpoint** |
| No legacy PA fuzzy match API | Power Automate compatibility gap | **FIX: Add endpoint** |
| Anti-Captcha extension UI in Settings missing | Extension not configurable from UI | **FIX: Add Automation sub-section** |
| PDF in bottom export group on Claim Detail | User requirement: PDF only at top | **FIX: Remove from bottom** |
| Ingestion mapping shows 4 deprecated fields | Mapping UI noise | **FIX: Remove from TARGET_CLAIM_FIELDS** |

---

## 4. Scope

### IN SCOPE

#### Backend Changes
1. **[MODIFY] `backend/app/api/v1/endpoints/matches.py`**
   - Add `GET /extract-names` — Extract unique party names (Insured, Driver, Claimant) from ClaimRecord table
   - Add `POST /fuzzy-search` — Legacy Power Automate fuzzy match: search name against all ScrapedCourtCase.case_style fields using RapidFuzz partial_ratio >= threshold (default 0.60)

2. **[MODIFY] `backend/app/api/v1/endpoints/settings.py`**
   - Add `POST /test-anticaptcha` — Validate AntiCaptcha API key by calling getBalance endpoint; return balance + latency

3. **[MODIFY] `backend/app/services/excel_parser.py`**
   - Remove the 4 field entries from `TARGET_CLAIM_FIELDS`: `loss_location_city`, `loss_location_county`, `garaging_city`, `garaging_state`

#### Frontend Changes
4. **[MODIFY] `frontend/src/app/claims/[id]/page.tsx`**
   - Add InspectedStage modal JSX: renders when `inspectedStage !== null`; displays portal name, status, duration, start/end time, and stage breakdown list; close button calls `setInspectedStage(null)`
   - Remove `loss_location_city` and `loss_location_county` from `formData` initial state and Edit Form JSX fields
   - Remove PDF button from the bottom export button group (top export toolbar keeps PDF as-is)
   - Add "View Raw JSON" button to each scraped case row — opens `rawJsonCaseForModal` (already exists) with the full case object
   - Remove the standalone sort dropdown button if found; rely on column-header sorting only

5. **[MODIFY] `frontend/src/app/monitor/page.tsx`**
   - Remove `loss_location_city`, `loss_location_county`, `garaging_city`, `garaging_state` from:
     - `formData` initial state (lines ~97, 247, 483)
     - Create modal form JSX
     - Edit modal form JSX (lines ~1558-1559, ~1745-1746)

6. **[MODIFY] `frontend/src/app/settings/page.tsx`**
   - Add "Anti-Captcha Extension" card inside the "Automation" settings tab
   - UI: API Key input (masked), Test Connection button, extension status badge, install instructions
   - Wire to new `POST /api/v1/settings/test-anticaptcha`

7. **[MODIFY] `frontend/src/lib/api.ts`**
   - Add `extractUniquePartyNames(partyType?)` call
   - Add `fuzzySearchCases(body)` call
   - Add `testAntiCaptchaKey(apiKey)` call

8. **[MODIFY] `frontend/src/types/index.ts`**
   - Add `ExtractNamesResponse`, `FuzzySearchRequest`, `FuzzySearchResponse`, `AntiCaptchaTestResponse` types

### OUT OF SCOPE (No Change)
- Database model changes — 4 fields stay in DB schema
- State routing logic — already correct, confirmed
- Guidewire payload assembly — confirmed unmodified by UI
- Celery task signatures
- Scraper automation logic
- AsyncExportModal on Monitor (already reusable and used)
- Dashboard data loading (already connects to real data)
- Audit page exports (already implemented with Excel/CSV/JSON)
- Exceptions page sorting and filtering (already implemented)

---

## 5. Files Expected to Change

### Backend (4 files)
| File | Action | Change |
|------|--------|--------|
| `backend/app/api/v1/endpoints/matches.py` | MODIFY | Add 2 new routes |
| `backend/app/api/v1/endpoints/settings.py` | MODIFY | Add 1 new route |
| `backend/app/services/excel_parser.py` | MODIFY | Remove 4 fields from TARGET_CLAIM_FIELDS |
| `backend/app/schemas/match.py` | MODIFY | Add request/response schemas |

### Frontend (5 files)
| File | Action | Change |
|------|--------|--------|
| `frontend/src/app/claims/[id]/page.tsx` | MODIFY | View Stages modal, form field removal, PDF removal from bottom, View Raw JSON |
| `frontend/src/app/monitor/page.tsx` | MODIFY | Remove 4 form fields from Create/Edit modals |
| `frontend/src/app/settings/page.tsx` | MODIFY | Add Anti-Captcha section in Automation tab |
| `frontend/src/lib/api.ts` | MODIFY | Add 3 new API calls |
| `frontend/src/types/index.ts` | MODIFY | Add 4 new TypeScript types |

---

## 6. Implementation Detail Per File

### Backend: matches.py — New Routes

```python
@router.get("/extract-names")
async def extract_unique_party_names(
    party_type: str = Query("all", regex="^(all|insured|driver|claimant)$"),
    db: AsyncSession = Depends(get_db),
):
    """Extract unique party names from all claim records."""
    result = await db.execute(select(
        ClaimRecord.insured_first_name, ClaimRecord.insured_last_name,
        ClaimRecord.driver_first_name, ClaimRecord.driver_last_name,
        ClaimRecord.claimant_first_name, ClaimRecord.claimant_last_name,
    ))
    rows = result.all()
    # Build unique name sets per party type
    # Return { insured: [], driver: [], claimant: [], total: N }

@router.post("/fuzzy-search")
async def legacy_fuzzy_search(
    payload: FuzzySearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Legacy Power Automate fuzzy match: search name against all scraped case styles."""
    # Load ScrapedCourtCase records (optionally filtered by filing_date >= 2010-01-01)
    # Apply RapidFuzz partial_ratio(search_name, case_style) >= payload.threshold (default 0.60)
    # Return matching cases sorted by similarity_score desc
    # Return { matches: [...], total: N }
```

### Backend: settings.py — New Route

```python
@router.post("/test-anticaptcha")
async def test_anticaptcha_api_key(payload: AntiCaptchaTestRequest):
    """Validate AntiCaptcha API key by checking balance."""
    # POST to https://api.anti-captcha.com/getBalance
    # Return { status, balance, message, latency_ms }
```

### Frontend: claims/[id]/page.tsx — View Stages Modal

The modal will render immediately after `inspectedStage` is set (non-null). JSX pattern:
```tsx
{inspectedStage && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 max-w-lg w-full mx-4 shadow-2xl">
      <h3>Stage Breakdown — {inspectedStage.key}</h3>
      {/* Portal metadata: status, duration, start/end time */}
      {/* Stage list: navigate, search, parse stages from inspectedStage.data.stages */}
      <button onClick={() => setInspectedStage(null)}>Close</button>
    </div>
  </div>
)}
```

### Frontend: settings.tsx — Anti-Captcha Card

Location: inside the "automation" tab section, after existing browser test section.
```tsx
{/* Anti-Captcha Extension */}
<div className="bg-white dark:bg-slate-900 border rounded-2xl p-6">
  <h4>Anti-Captcha Extension Configuration</h4>
  <input type="password" placeholder="API Key" ... />
  <button onClick={handleTestAntiCaptcha}>Test Connection</button>
  {testResult && <div>{testResult.balance ? `Balance: $${testResult.balance}` : testResult.message}</div>}
</div>
```

---

## 7. Testing Plan

### Automated Tests
```bash
cd backend && .venv\Scripts\pytest --tb=short -q
.venv\Scripts\ruff check app tests
cd frontend && npx tsc --noEmit
npm run build
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```

### Manual Verification Checklist
- [ ] "View Stages" button on Claim Detail opens a modal with portal stage data
- [ ] Edit form on Claim Detail does NOT show loss_location_city or loss_location_county
- [ ] Create/Edit modals on Monitor do NOT show any of the 4 deprecated fields
- [ ] `GET /api/v1/matches/extract-names` returns `{insured:[...], driver:[...], claimant:[...], total:N}`
- [ ] `POST /api/v1/matches/fuzzy-search` with `{"search_name":"Smith"}` returns matches
- [ ] Settings > Automation tab shows Anti-Captcha card with API key input and test button
- [ ] `POST /api/v1/settings/test-anticaptcha` returns status response
- [ ] Claim Detail BOTTOM export (if present) does NOT have PDF button
- [ ] Claim Detail TOP export toolbar STILL has PDF button
- [ ] "View Raw JSON" button on scraped case rows opens JSON viewer modal
- [ ] All pages use full viewport width (no max-w-6xl or max-w-4xl outer constraints)
- [ ] Dark mode: all new UI elements render correctly in both light and dark themes
- [ ] State routing: confirm FL+FL → 3 bots, TX+TX → 5 bots (no change needed, just verify)

---

## 8. Acceptance Criteria (Measurable)

1. "View Stages" button → modal opens with at least portal_name, status, duration_seconds fields visible
2. Create/Edit forms on Monitor → 0 input fields for the 4 deprecated fields
3. Edit form on Claim Detail → 0 input fields for loss_location_city and loss_location_county
4. `GET /api/v1/matches/extract-names` → HTTP 200, JSON body with `insured`, `driver`, `claimant` arrays
5. `POST /api/v1/matches/fuzzy-search` → HTTP 200, JSON body with `matches` array and `total` count
6. `POST /api/v1/settings/test-anticaptcha` → HTTP 200, JSON with `status` field
7. Settings Automation tab has Anti-Captcha section with API key input visible
8. Claim detail top toolbar: Excel | CSV | PDF | JSON (4 buttons)
9. No `max-w-6xl` or `max-w-4xl` on top-level `<main>` wrappers across all pages
10. `pytest` 100% pass | `ruff check` 0 errors | `tsc --noEmit` 0 errors | `npm run build` exits 0

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Removing fields from ingestion mapping may break preview UI if FileUploader expects those fields | FileUploader renders whatever TARGET_CLAIM_FIELDS returns — removing entries removes them from UI cleanly |
| Anti-Captcha API connectivity may fail in offline dev environments | Test connection errors handled gracefully with clear error message; no effect on scraping |
| `inspectedStage.data.stages` may be `{}` (empty) for claims that haven't run | Modal renders gracefully with "No stage data available" message |
| Large datasets in fuzzy-search endpoint may be slow | Add limit param (default 100, max 500) with informative response |

---

**No application code has been modified yet.**
**Plan saved to:** `implementation_plan/2026-09-09_uaic_responsive-ux-orchestrator-scraped-cases-form-fixes_implementation-plan_v1.md`
Please confirm if you approve this plan so I may begin execution.
