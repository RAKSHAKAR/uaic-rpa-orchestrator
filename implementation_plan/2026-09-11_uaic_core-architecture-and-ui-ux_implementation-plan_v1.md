# Implementation Plan

**Implementation ID:**   IMP-2026-0911-007  
**Project:**             UAIC Claim & RPA Orchestrator  
**Module:**              Core Orchestrator Architecture & Global UI/UX  
**Feature / Issue:**     Prompt 03 — Core Orchestrator Architecture & Global UI/UX Redesign  
**Document Type:**       Implementation Plan  
**Version:**             v1  
**Status:**              Approved by User (Prompt Pipeline Execution)  
**Created:**             2026-09-11  
**AI Agent:**            Antigravity (Advanced Agentic Coding)  
**Approval Status:**     Approved  
**Approved By:**         User  
**Approval Date:**       2026-09-11  
**AI Verification:**     Complete (100% Automated Testing Suite)  

---

## 1. Problem & Executive Summary

Following the execution sequence from `Prompt Processning.txt`, milestone **03 - CORE ORCHESTRATOR ARCHITECTURE & GLOBAL UI/UX** (`03_Core_Architecture_and_UI_UX.md`) focuses on:
1. **Global Responsiveness & Mobile Shell**: Full viewport width, bottom navigation bar on mobile with safe-area insets, dark/light theme parity.
2. **Orchestrator Routing Logic**: Ensuring strict Florida vs. Texas state routing (Miami-Dade is Florida, never Texas) and Guidewire contract preservation.
3. **Scraped Public Court Cases UI Redesign**: Grouping by portal link, column sorting, multi-select filtering, global search, pagination max 500, View Raw JSON modal, and View Screenshot modal.
4. **Dashboard & Exports**: Connecting the 8 Scraper Execution bot throughput cards to real claims data and the 8 official portals, ensuring top/bottom exports contain complete data with PDF only shown on supported routes.

### Gap Analysis:
- In `frontend/src/app/page.tsx`, `portalBreakdown` used static mock numbers and incorrect county names (`Orange (FL)` and `Tarrant (TX)`). It must be connected to real application claims data across the exact 8 portals (Miami-Dade, Broward, Hillsborough, Harris County Clerk, Dallas, Harris JP, Harris District Clerk, Travis).
- In `frontend/src/types/index.ts` and `frontend/src/lib/api.ts`, `getClaimScreenshots` was missing from the API client, preventing the UI from querying captured error screenshots.
- In `frontend/src/app/claims/[id]/page.tsx`, the Scraped Cases section had "View Raw JSON", but lacked the "View Screenshot" button and image inspection modal for operators to inspect bot captures when a portal fails or triggers CAPTCHA.

---

## 2. Proposed Changes

### Component 1: Frontend Type & API Client
#### [MODIFY] [types/index.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/types/index.ts)
- Extend `ErrorScreenshot` interface with optional `portal`, `county`, `error_message`, `error_stage`, `file_size_bytes`, `content_type`.

#### [MODIFY] [lib/api.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/lib/api.ts)
- Add `getClaimScreenshots: (claimId: string) => Promise<{ total: number; screenshots: ErrorScreenshot[] }>` method targeting `/claims/{claim_id}/screenshots`.

### Component 2: Dashboard Real Portal Data Integration
#### [MODIFY] [app/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/page.tsx)
- Dynamically compute `portalBreakdown` from `claims` array across the 8 real portals:
  - Florida: Miami-Dade, Broward, Hillsborough
  - Texas: Harris County Clerk, Dallas, Harris JP, Harris District Clerk, Travis
- Calculate actual extracted case counts per portal dynamically.

### Component 3: Scraped Cases Screenshot Modal
#### [MODIFY] [app/claims/[id]/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/claims/[id]/page.tsx)
- Load error screenshots for the active claim on mount.
- Add "View Screenshots" action button with camera icon in Scraped Cases toolbar.
- Implement rich Screenshot Inspection Modal with portal badge, capture timestamp, error message, image viewer, and download action.

---

## 3. Verification Plan

### Automated Tests:
1. `cd frontend; npx tsc --noEmit` (0 type errors).
2. `cd frontend; npm run lint` (0 lint errors).
3. `cd backend; .venv\Scripts\pytest tests/test_v4_parity.py tests/test_api.py -v`.
4. `cd backend; .venv\Scripts\ruff check app tests`.
5. `powershell -File scripts\check_ps1_syntax.ps1`.
