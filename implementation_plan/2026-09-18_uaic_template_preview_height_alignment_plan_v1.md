# UAIC Claim & RPA Orchestrator — Implementation Plan
## Equal-Height Layout Synchronization for Email Template Editor & Live Synchronized Render Preview

**Implementation ID:** `IMP-2026-0918-010`  
**Date:** September 18, 2026  
**Status:** 🟡 **Awaiting User Approval (Governance Phase: Plan Review)**  
**Target Area:** `frontend/src/app/settings/page.tsx` — Email & Notification Template Studio (Split-View Mode)  

---

## 1. Executive Summary & Root Cause Diagnosis

### A. Root Cause Analysis
In the Email & Notification Template Studio (`settings/page.tsx`):
1. **Grid Row Alignment Constraint (`items-start`):**
   In line 5921, the split-view parent container was defined as:
   ```tsx
   <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 items-start w-full">
   ```
   `items-start` forces both columns to shrink-wrap to their individual internal contents instead of matching heights across the row.
2. **Left vs Right Content Height Asymmetry:**
   - **Left Column (`renderEditor`):** Contains the Subject input (~70px), Body Format switcher (~40px), Dynamic Parameter Palette (~160px), Template Label (~25px), and a `<textarea rows={18}>` (~380px), totaling **~675px**.
   - **Right Column (`renderPreview`):** Contains the Live Preview header (~35px), Subject banner (~40px), and Rendered Viewport Frame constrained with a hard `max-h-[520px]`. Because the sample email template content is only ~350px tall, the preview container only expanded to ~480px.
3. **Result:** As shown in the user's screenshot, the right preview card ended ~200px above the bottom of the left column's dark code editor, leaving an uneven, unbalanced layout with awkward empty space below the preview card.

---

## 2. Proposed Architectural & UI/UX Solution

We will refactor the Split-View Editor layout using an enterprise flexbox/grid stretch architecture:

### 1. Symmetrical Grid Alignment (`items-stretch`)
In `activeEditorTab === "split"`:
```tsx
<div className="grid grid-cols-1 xl:grid-cols-2 gap-6 items-stretch w-full">
  {renderEditor()}
  {renderPreview()}
</div>
```
`items-stretch` guarantees that both columns in the grid row have the exact same pixel height on large/xl displays.

### 2. Left Column Editor Expansion (`flex flex-col h-full`)
In `renderEditor()`:
- Set outer container to `space-y-4 flex flex-col h-full`.
- Set code editor textarea wrapper to `space-y-1.5 flex-1 flex flex-col min-h-0`.
- Update `<textarea>` to `flex-1 min-h-[340px] resize-y`, allowing it to naturally expand and fill available height smoothly.

### 3. Right Column Preview Expansion (`flex flex-col h-full flex-1`)
In `renderPreview()`:
- Set outer container to `space-y-3 flex flex-col h-full`.
- Set header to `shrink-0`.
- Set the preview card container to `border ... flex-1 flex flex-col min-h-0`.
- Inside the preview card:
  - Subject banner: `shrink-0`.
  - Rendered Viewport Frame: `p-4 sm:p-6 bg-slate-100 dark:bg-slate-950 overflow-y-auto flex-1 min-h-[340px]`.
    By using `flex-1` with `overflow-y-auto` instead of hardcoded `max-h-[520px]`, the viewport frame expands dynamically to fill the exact height of the left column.
  - Context Tokens mock footer: `shrink-0`.
  - Paused State container: `flex-1 flex flex-col items-center justify-center`.

### 4. Visual Result
The bottom edge of the left editor card and the bottom edge of the right preview card (with its Context Tokens bar) will line up on the exact same horizontal baseline across all screen resolutions and dark/light themes.

---

## 3. Verification Plan

### Automated Quality Gates
1. `frontend/npx tsc --noEmit` (0 errors)
2. `frontend/npm run lint` (0 errors)
3. `frontend/npm run build` (11/11 routes compile cleanly)
4. `backend/.venv/Scripts/pytest --tb=short -q` (All 453 tests pass)
5. `backend/.venv/Scripts/ruff check app tests` (0 errors)
6. `powershell scripts\check_ps1_syntax.ps1` (0 errors)

### Visual & Interactive Browser Verification
- Launch `browser_subagent` to navigate to `http://localhost:3000/settings` Tab 4 (Notification & Email Studio).
- Inspect the Template Studio in Split-View mode.
- Verify that the bottom border of the left editor column and the right preview column are identical in vertical height.
- Toggle between token categories, switch between HTML and Plain Text view, and verify that height synchronization remains 1:1.
- Capture visual verification screenshot saved to `implementation_plan/Images/template_preview_height_aligned.png` and interaction recording to `implementation_plan/Recording/template_preview_height_aligned.webp`.

---

## 4. Governance & Human Confirmation

In strict compliance with `.agents/skills/diagnose-plan-confirm-execute/SKILL.md`:
- **NO APPROVAL = NO IMPLEMENTATION.**
- No source code changes will be made until explicit user approval is granted.
