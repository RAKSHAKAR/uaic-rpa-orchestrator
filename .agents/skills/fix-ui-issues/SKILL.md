---
name: fix-ui-issues
description: >-
  Resolve layout shifts, z-index bugs, modal backdrop traps, contrast defects, and broken responsive viewports.
---

# Fix Ui Issues

## 1. Purpose & Overview
Diagnoses and patches CSS layout defects, broken flex/grid alignments, missing theme tokens, and modal stacking context bugs across Next.js components.

---

## 2. When to Use & When NOT to Use

### When to Use
- UI components clip or overflow unexpectedly on smaller screens.
- Modals render behind other elements or block page interactions.
- Text is unreadable due to missing dark/light theme token pairing.

### When NOT to Use
- Backend API logic.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Affected component file path, visual defect description, and viewport resolution.

### Prerequisites
- Tailwind CSS configuration and running frontend application.

---

## 4. Step-by-Step Execution Procedure

### Step 1: DOM & CSS Inspection
Inspect affected element in browser DevTools. Check computed box-sizing, display mode, padding, margin, and z-index values.

### Step 2: Theme Token Pairing Check
Verify background and text color utility classes are paired correctly (`bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100`).

### Step 3: Z-Index & Stacking Context Fix
Assign explicit, standardized z-index levels (`z-10` for dropdowns, `z-50` for modals, `z-60` for toasts). Ensure backdrop overlays have `fixed inset-0`.

### Step 4: Overflow & Responsive Fix
Replace rigid pixel widths with responsive utilities (`w-full`, `max-w-none`, `overflow-x-auto`).

### Step 5: Dual-Mode Visual Verification
Inspect fix under both Light Mode and Dark Mode across 375px, 768px, and 1920px viewports.

### Step 6: TypeScript Compile Pass
Run `cd frontend && npx tsc --noEmit`.


---

## 5. Safety Considerations & Guardrails
- Do NOT use arbitrary high z-indexes (e.g. `z-[999999]`); use established design system elevation scales.
- Ensure UI fixes do not introduce horizontal scrollbars.

---

## 6. Expected Deliverables & Artifacts
- Patched React component JSX/CSS.
- Dual-theme screenshot verifying defect resolution.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Visual defect is completely resolved across desktop, tablet, and mobile.
- [ ] Renders cleanly with high contrast in both Light Mode and Dark Mode.
- [ ] `npx tsc --noEmit` passes with 0 errors.

---

## 8. Error Recovery & Troubleshooting
- If Tailwind classes fail to apply, check for specificity collisions with custom CSS.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fix-ui-issues`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fix-ui-issues` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fix-ui-issues`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fix-ui-issues` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fix-ui-issues`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fix-ui-issues`. | `PROMPT FILE` |
| **Windsurf** | Activate `fix-ui-issues` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.agents/skills/theme-system/SKILL.md`
- `frontend/src/app/branding/page.tsx`
