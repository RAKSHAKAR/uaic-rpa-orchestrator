---
name: accessibility-testing
description: >-
  Execute automated axe-core accessibility checks and verify manual keyboard traversal across all interactive views.
---

# Accessibility Testing

## 1. Purpose & Overview
Verifies that the application adheres to WCAG 2.1 AA criteria, verifying that assistive technology and keyboard-only operators can navigate and use all system features.

---

## 2. When to Use & When NOT to Use

### When to Use
- Quality gates for new UI pages, modals, tables, or form controls.
- Pre-release accessibility compliance sign-off.

### When NOT to Use
- Backend server testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Frontend application running locally on port 3000.
- Axe-core automated testing engine.

### Prerequisites
- Next.js frontend reachable on port 3000.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Automated Axe-Core Test Pass
Run automated axe-core accessibility scan against all active routes. Collect violation counts by impact (Critical, Serious, Moderate, Minor).

### Step 2: Keyboard Tab Order Traversal
Tab through every interactive element on each page. Confirm focus moves in logical reading order without jumping.

### Step 3: Focus Visibility Audit
Confirm every focused element displays a prominent, high-contrast focus ring (`focus-visible:ring-2`).

### Step 4: Modal Dialog Focus Trapping
Open modals. Confirm focus is trapped within modal and returns to triggering button upon closure with Escape.

### Step 5: Form Label Association Check
Verify that every `<input>`, `<select>`, and `<textarea>` has an associated `<label>` with matching ID.

### Step 6: Accessibility Report Synthesis
Document scan results and confirm 0 critical/serious violations.


---

## 5. Safety Considerations & Guardrails
- Never bypass accessibility failures to meet delivery deadlines.
- Ensure color contrast is tested under both Light and Dark themes.

---

## 6. Expected Deliverables & Artifacts
- Automated Accessibility Scan Results.
- Keyboard Navigation Audit Checklist.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero Critical or Serious violations reported by axe-core.
- [ ] 100% of interactive controls are operable via keyboard alone.
- [ ] Visible focus indicators present on all focused elements.

---

## 8. Error Recovery & Troubleshooting
- If an element lacks accessible naming, add `aria-label` or visible `<label>` text.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/accessibility-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@accessibility-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `accessibility-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `accessibility-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run accessibility-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt accessibility-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `accessibility-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.agents/skills/theme-system/SKILL.md`
- `frontend/src/components/Navbar.tsx`
