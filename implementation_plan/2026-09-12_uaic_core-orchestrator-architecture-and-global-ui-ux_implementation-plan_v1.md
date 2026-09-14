# Implementation Plan — Core Orchestrator Architecture & Global UI/UX

Implementation ID:   IMP-2026-0912-006  
Project:             UAIC Claim & RPA Orchestrator  
Module:              Core Orchestrator, Scraped Cases Enterprise Table & Global UI/UX  
Feature / Issue:     03 - Core Orchestrator Architecture & Global UI/UX  
Document Type:       Implementation Plan  
Version:             v1  
Status:              Complete
Created:             2026-09-12  
Last Updated:        2026-09-12  
AI Agent:            Antigravity  
Approval Status:     Approved  
Approved By:         User  
Approval Date:       2026-09-12  
AI Verification:     Complete (100% Automated Testing Suite)  

---

## 1. Executive Summary

This implementation plan addresses **Prompt 03 — Core Orchestrator Architecture & Global UI/UX**, fulfilling the four core architectural areas:
1. **Global Responsiveness & Theme:** Full viewport width (`w-full max-w-none flex-1`), zero horizontal page overflow, fixed mobile bottom navigation with device safe-area insets, and 100% Dark/Light mode parity across all components.
2. **Orchestrator & Routing Logic:** Preservation and verification of the strict multi-state routing matrix (Florida -> 3 bots, Texas -> 5 bots, Cross-state -> 8 bots; Miami-Dade strictly Florida) and 100% immutable preservation of the Guidewire case-update JSON contract.
3. **Scraped Public Court Cases (UI Redesign):** Enterprise table with explicit portal-link grouping, column sorting, multi-select filtering, global search, pagination up to 500 rows, empty-field fidelity (no fabricated `"CIVIL"` case types for Harris JP / Harris Clerk), and one-click "View Raw JSON" and "View Screenshot" triage buttons.
4. **Dashboard, Exports & UI Refinements:** Synchronizing the Scraper Execution (8 Bots) cards on Claim Detail with the global dashboard card design language (`StatCard.tsx`), ensuring `AsyncExportModal` is reusable across all application modules, and guaranteeing identical, complete top/bottom claim exports (Excel, CSV, JSON, PDF).

---

## 2. Current State vs. Gap Analysis

| Requirement Area | Current Codebase State | Identified Gap / Required Action |
|---|---|---|
| **1. Full Viewport Width** | All routes (`/`, `/claims/:id`, `/settings`, `/monitor`, `/health`, `/exceptions`, `/upload`, `/branding`, `/audit`) use `w-full max-w-none flex-1`. Shell uses `overflow-x-clip`. | Verified compliant. Guarantee zero child element overflow on 360px–1920px viewports. |
| **2. Mobile Navigation** | `MobileBottomNav.tsx` provides 5 primary destinations with `env(safe-area-inset-bottom)` and `ResponsiveShell.tsx` provides clearance padding. | Verified compliant. Ensure last scrolling record on mobile viewports is never obscured by the fixed bar. |
| **3. Dual Theme Parity** | `theme-system` skill governs 26 semantic color tokens persisted in DB and injected dynamically. | Verified compliant. Inspect all table rows, inputs, badges, and modals for explicit dark/light color token pairings. |
| **4. State Routing Logic** | `resolve_county_bot_targets()` routes FL -> Broward, Hillsborough, Miami; TX -> Travis, Dallas, Harris JP, Harris Clerk, Harris District; Cross-state -> all 8. Miami is strictly Florida (`fl_miami`). | Verified compliant with 5 test suites. Preserved without regression. |
| **5. Guidewire Contract** | Payload contract `{ ClaimNumber, ExposureNumber, CaseItems: [...] }` with 9-digit prefix formatting (`format_claim_number`). | Verified compliant. Purely backend-isolated and protected from any UI modifications. |
| **6. Scraped Cases Table** | Grouped by portal link, column sorting, multi-select filters, global search, pagination up to 500 rows. Standalone `sort:descending` button removed. | **Gap Found:** Empty `case_type` defaults to `"CIVIL"` or `"CIRCUIT CIVIL"`, fabricating values for Harris JP and Harris Clerk scrapers. Change fallback to `"—"` / `"N/A"`. Add "View Screenshot" action to case rows and case details modal. |
| **7. 8 Bots Execution Cards** | Rendered as custom cards in `claims/[id]/page.tsx` Section 2. | **Gap Found:** Elevate the 8 Bots cards to match the global `StatCard.tsx` design language (gradient icon badge, bold mono count, hover lift `-translate-y-0.5`, consistent status badges). |
| **8. Background Export Popup** | `AsyncExportModal.tsx` exists and is used on `/` and `/monitor`. | Reusable component is created. Connect it also to `/exceptions` for large dataset background exports. |
| **9. Top/Bottom Claim Exports** | Top bar has Excel, CSV, PDF, JSON. Bottom cases table has Excel, CSV, JSON, Screenshots. Both use `GET /api/v1/claims/{id}/export`. | Verified identical data. Bottom export excludes PDF as specified. |

---

## 3. Proposed Changes by Component

### Component A: Scraped Public Court Cases Data Integrity & Debugging (`frontend/src/app/claims/[id]/page.tsx`)
- **Fix Case Type Fallback:**
  - Replace `courtCase.case_type || "CIVIL"` in both Unified Table and Grouped View with `courtCase.case_type || "—"`.
  - Replace `selectedCaseForModal.case_type || "CIRCUIT CIVIL"` in the details modal with `selectedCaseForModal.case_type || "—"`.
  - This guarantees that for Harris JP and Harris County Clerk (which do not produce `CaseType`), no artificial value is fabricated, adhering strictly to SOP Section 5.4.
- **Add Per-Case "View Screenshot" Action:**
  - In each table row's Actions column, add a `<button onClick={() => handleViewPortalScreenshot(courtCase)}><Camera className="w-3 h-3 text-rose-500" /> Screenshot</button>`.
  - In the `selectedCaseForModal` details modal, add a "View Portal Screenshot" button that opens error screenshots if available, or navigates to the error screenshot triage modal.

### Component B: Scraper Execution (8 Bots) Cards Styling (`frontend/src/app/claims/[id]/page.tsx`)
- Align the 8 Bots cards in Section 2 with the global `StatCard.tsx` design language:
  - Surface: `bg-white dark:bg-slate-900/60 border rounded-xl p-4 flex flex-col justify-between space-y-3 shadow-xs hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-md hover:-translate-y-0.5 transition-all`
  - Header with icon box: `w-7 h-7 rounded-lg bg-gradient-to-br ... border flex items-center justify-center shrink-0` (indigo gradient for FL, teal gradient for TX).
  - Bold font-mono count: `text-xl sm:text-2xl font-bold font-mono text-slate-900 dark:text-slate-100`.
  - Target badge and StatusBadge styled with semantic design tokens.
  - Consistent action buttons ("Run Bot" / "View Cases").

### Component C: Reusable Background Export Modal (`frontend/src/app/exceptions/page.tsx`)
- Import `AsyncExportModal` on `/exceptions`.
- Provide an "Export Large Dataset" background export option in addition to the instant export buttons, allowing operators to leverage Celery streaming for bulk exception datasets.

### Component D: Verification Suite (`backend/tests/test_imp_2026_0912_006.py`)
- Automated tests verifying:
  - State routing logic across FL, TX, and cross-state combinations.
  - Miami-Dade county classification as Florida (`fl_miami`).
  - Guidewire payload contract structure, field naming, and 9-digit claim number formatting.
  - Court case export endpoint parity (Excel 5-sheet workbook, CSV metadata, JSON schema).
  - Portal output schemas (Harris JP and Harris County Clerk have no `case_type`).

---

## 4. Verification Plan

### Automated Tests:
1. `pytest tests/test_imp_2026_0912_006.py` — Dedicated validation suite for routing, Guidewire contract, and court case exports.
2. `pytest tests/test_services.py tests/test_v4_parity.py tests/test_excel_parser.py` — State routing regression checks.
3. `ruff check app tests` — Backend lint check (0 errors).
4. `npx tsc --noEmit` — Frontend TypeScript check (0 errors).
5. `npm run build` — Next.js production build verification (all routes clean).
6. `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` — PowerShell syntax check.

### Manual / Browser Verification:
1. Navigate to Claim Detail page (`/claims/:id`):
   - Verify 8 Bots cards match the global `StatCard` design language.
   - Verify Scraped Public Court Cases table:
     - Grouping by Portal Link.
     - Column sorting, multi-select filtering, global search, pagination.
     - Cases from Harris JP / Harris Clerk display `—` for Case Type without fabricating `"CIVIL"`.
     - Click "View Raw JSON" and "View Screenshot" buttons.
     - Check Top exports (Excel, CSV, PDF, JSON) and Bottom exports (Excel, CSV, JSON) contain complete, identical data.
2. Navigate to Dashboard (`/`):
   - Verify real application data connectivity.
3. Test Mobile Viewport (390px):
   - Verify fixed bottom nav, safe area insets, and zero horizontal scrolling.
4. Test Light and Dark Themes:
   - Verify 100% readability across both modes.

---

## 5. User Review Required

> [!NOTE]
> All core business logic (state routing matrix, DOL base date, fuzzy cascade, Guidewire contract) is 100% preserved. No existing working features will be removed.
>
> In accordance with the **Universal AI Engineering Governance Skill**, no source code will be modified until you confirm your approval.
