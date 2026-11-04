---
name: theme-system
description: >-
  Global Light and Dark mode theme governance: strictly enforce dual modes, prohibit OS auto-detection, and unify Branding tokens.
---

# Theme System

## 1. Purpose & Overview
Governs the application's Light and Dark theme architecture. Strictly prohibits system/OS automatic detection and mandates the `/branding` page as the single authoritative source of truth for 26 semantic color tokens.

---

## 2. When to Use & When NOT to Use

### When to Use
- Authoring or revising ANY UI component, modal, form, page, or table.
- Auditing theme contrast, readability, and dynamic palette synchronization.

### When NOT to Use
- Backend headless scripts or Celery workers with no UI output.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `frontend/src/context/BrandingContext.tsx`, `app/branding/page.tsx`, and Tailwind CSS configuration.

### Prerequisites
- Knowledge of CSS variable dynamic injection in `:root` and `.dark`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Enforce Exactly Two Theme Modes
Support strictly `Light` (`[data-theme='light']`) and `Dark` (`[data-theme='dark']`). Prohibit OS auto-detection (`prefers-color-scheme`).

### Step 2: Branding Page Authority
Ensure `/branding` controls both Light Mode and Dark Mode palettes, persisted in database settings (`BrandingSettings`).

### Step 3: Dual-Token Pairing
Pair every background utility with a corresponding text color (`bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100`).

### Step 4: Dynamic Injection Verification
Verify that `BrandingContext.tsx` updates active CSS variables in `:root` and `.dark` in real time without page reloads.

### Step 5: Dual-Mode Visual Verification
Inspect all pages in both Light Mode and Dark Mode. Confirm zero white-on-white or black-on-black defects.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: NEVER implement `window.matchMedia('(prefers-color-scheme: ...)')` or auto-detection toggles.
- Never allow white text on white background or black text on black background under either mode.

---

## 6. Expected Deliverables & Artifacts
- Theme-compliant React components and layouts.
- Dual-theme screenshot verification artifacts in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Application toggles cleanly between Light and Dark modes via the header selector.
- [ ] All inputs, cards, borders, and modals are clearly readable under both themes.
- [ ] Zero OS auto-detection logic exists in codebase.

---

## 8. Error Recovery & Troubleshooting
- If text is unreadable in Dark Mode, replace hardcoded slate classes with semantic token classes or explicit `dark:text-slate-100` variants.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/theme-system` or follow `.agents/skills/theme-system/SKILL.md`. | `CUSTOM SKILL` |
| **Cursor** | Select `@theme-system` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `theme-system`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `theme-system` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run theme-system`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt theme-system`. | `PROMPT FILE` |
| **Windsurf** | Activate `theme-system` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.agents/skills/theme-system/SKILL.md` (Authoritative Theme Governance Skill)
- `frontend/src/app/branding/page.tsx`
