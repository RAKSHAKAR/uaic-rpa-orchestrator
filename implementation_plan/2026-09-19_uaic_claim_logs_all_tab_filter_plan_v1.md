# Implementation Plan — Claim Logs & Diagnostic Center "All" Unified Timeline Tab

**Implementation ID:** `IMP-2026-0919-002`  
**System Target:** UAIC Claim & RPA Orchestrator — Claim Detail View (`/claims/[id]`)  
**Component:** Claim Logs & Diagnostic Center (`frontend/src/app/claims/[id]/page.tsx`)  
**Date:** 2026-09-19  
**Version:** v1  
**Governing Skill:** `.agents/skills/diagnose-plan-confirm-execute/SKILL.md`

---

## 1. Problem Statement & User Request

The user shared a screenshot of the **Claim Logs & Diagnostic Center** on Claim `#TEST_DATEFILED_001` with the instruction:
> *"i think you have to add All as options also"*

### Current Situation:
1. The header displays: `11 Total Log Entries` (e.g. 4 Audit Trail entries + 7 Processing Log entries + 0 Exceptions).
2. However, the tab navigation only offers 4 isolated category tabs:
   - `Audit Trail (4)`
   - `Processing Logs (7)`
   - `Exceptions & Errors (0)`
   - `Portal Console Terminal (1 Portals)`
3. There is **no "All" tab option**. An adjuster or operator wanting to inspect the complete operational narrative of a claim in real-time must flip back and forth between tabs. They cannot view a single, cohesive, chronological timeline of everything that happened to the claim.

---

## 2. Proposed Changes

### Component: Frontend Claim Detail View (`frontend/src/app/claims/[id]/page.tsx`)

#### 1. Expand `claimLogsTab` State
- Update state type definition to include `"all"`:
  ```typescript
  const [claimLogsTab, setClaimLogsTab] = useState<"all" | "audit" | "processing" | "exceptions" | "terminal">("all");
  ```
- Set default tab to `"all"`, so operators immediately see the full chronological log stream upon opening the diagnostic center.

#### 2. Implement `sortedAllLogs` Unified Memoized Stream
- Combine `audit_logs`, `processing_logs`, and `exception_logs` into a typed unified timeline:
  ```typescript
  interface UnifiedLogItem {
    id: string;
    source: "audit" | "processing" | "exception";
    timestamp: string;
    parsedTime: number;
    data: AuditLogEntry | ProcessingLogEntry | ExceptionLogEntry;
  }
  ```
- Sort all entries by `parsedTime` dynamically honoring `claimLogsSortOrder` (`"desc"` = Latest First, `"asc"` = Oldest First).

#### 3. Update Tab Navigation Bar
- Add **`All`** (or `All Logs`) as the prominent first tab:
  - Icon: `<Layers className="w-3.5 h-3.5" />`
  - Label: `All`
  - Badge: Total count of all entries (e.g. `11`)
  - Active style: `bg-indigo-600 text-white shadow-sm shadow-indigo-600/30`
- Followed by category tabs: `Audit Trail (4)`, `Processing Logs (7)`, `Exceptions & Errors (0)`, `Portal Console Terminal (1 Portals)`.

#### 4. Render Unified Timeline Section
- When `claimLogsTab === "all"`, render the combined timeline:
  - **Audit Trail items:** Indigo source pill `AUDIT TRAIL`, action tag, status badge (`SUCCESS` / `FAILED`), description, user/actor, IP address, and `Inspect` detail button.
  - **Processing Log items:** Sky source pill `PROCESSING`, stage badge (e.g. `1_BROWSER_LAUNCH`), portal badge (e.g. `hillsborough`), level pill (`INFO` / `WARNING` / `ERROR`), message, and actor.
  - **Exception items:** Rose source pill `EXCEPTION`, component badge, error message, and `Inspect Error` modal button.
  - Left timeline connector line matching existing design tokens.
  - Full support for interactive sorting (`Latest First` / `Oldest First`) and `Refresh Logs`.

---

## 3. Verification Plan

### Automated Tests
1. **Frontend TypeScript Check:**
   ```bash
   cd frontend
   npx tsc --noEmit
   ```
2. **Frontend ESLint Check:**
   ```bash
   cd frontend
   npm run lint
   ```
3. **PowerShell Syntax Check:**
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```
4. **Backend Parity / Regression:**
   ```bash
   cd backend
   .venv\Scripts\pytest tests/test_match_inspection.py -q
   ```

### Visual & Browser Verification
1. Run Playwright script against `http://localhost:3000/claims/[id]`:
   - Verify the new `All (11)` tab is rendered as the first tab in the Claim Logs & Diagnostic Center.
   - Verify that clicking `All` displays a chronological feed merging Audit Trail and Processing Logs.
   - Verify that toggling `Latest First` / `Oldest First` correctly reorders the unified timeline.
   - Capture screenshot: `implementation_plan/Images/claim_logs_all_tab_timeline.png`.

---

## 4. Definition of Done Checklist
- [ ] `claimLogsTab` state accepts `"all"` and defaults to `"all"`
- [ ] `All (N)` tab added as the first option in tab bar
- [ ] `sortedAllLogs` accurately merges audit, processing, and exception logs
- [ ] Unified timeline renders distinctive source pills (`AUDIT TRAIL`, `PROCESSING`, `EXCEPTION`)
- [ ] Sorting toggle (`Latest First` / `Oldest First`) sorts all 11+ logs correctly
- [ ] Zero TypeScript (`tsc`) and ESLint errors
- [ ] Screenshot captured and saved to `implementation_plan/Images/`
- [ ] Implementation record finalized
