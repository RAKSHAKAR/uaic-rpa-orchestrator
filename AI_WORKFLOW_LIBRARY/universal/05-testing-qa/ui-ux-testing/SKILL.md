---
name: ui-ux-testing
description: >-
  Validate visual consistency, dual-theme rendering, component states, and responsive interactions.
---

# Ui Ux Testing

## 1. Purpose & Overview
Conducts detailed visual and experiential testing across all frontend pages, checking typography alignment, color token fidelity, loading spinners, and empty states.

---

## 2. When to Use & When NOT to Use

### When to Use
- Verifying new frontend features or design system token updates.
- Pre-release visual quality passes.

### When NOT to Use
- Backend server testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Frontend application running locally on port 3000.
- Dual-theme color specifications.

### Prerequisites
- Next.js frontend running and reachable.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Light Mode Visual Walkthrough
Inspect every page under Light Mode. Verify high-contrast readable text, clean borders, and clear card backgrounds.

### Step 2: Dark Mode Visual Walkthrough
Toggle theme to Dark Mode. Confirm zero black-on-black text, readable input fields, and consistent slate/gray elevation.

### Step 3: State Transitions Inspection
Trigger loading states (skeleton loaders), empty states (zero search matches), and error banners. Verify visual polish.

### Step 4: Interactive Controls & Hover Effects
Test button hover/active states, dropdown menus, modal overlays, and toast notifications.

### Step 5: Screenshot Evidence Archival
Capture side-by-side screenshots of key views in both themes and save to `docs/`.


---

## 5. Safety Considerations & Guardrails
- Never allow un-themed rogue CSS styles to pass UI verification.
- Ensure modal dialogs maintain high-contrast backdrops.

---

## 6. Expected Deliverables & Artifacts
- UI/UX Visual Inspection Report.
- Dual-theme screenshot comparison artifacts in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 100% of pages render flawlessly in both Light Mode and Dark Mode.
- [ ] Zero white-on-white or black-on-black contrast violations exist.
- [ ] All state transitions (loading, empty, error) display appropriate visual feedback.

---

## 8. Error Recovery & Troubleshooting
- If an element displays poor contrast in Dark Mode, adjust Tailwind tokens to use explicit `dark:` modifiers.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/ui-ux-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@ui-ux-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `ui-ux-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `ui-ux-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run ui-ux-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt ui-ux-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `ui-ux-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.agents/skills/theme-system/SKILL.md`
- `frontend/src/app/branding/page.tsx`
