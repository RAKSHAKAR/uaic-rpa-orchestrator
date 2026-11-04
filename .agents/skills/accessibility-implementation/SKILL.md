---
name: accessibility-implementation
description: >-
  Implement WCAG 2.1 AA accessibility compliance, semantic HTML landmarks, ARIA attributes, and full keyboard navigation.
---

# Accessibility Implementation

## 1. Purpose & Overview
Ensures the application is fully accessible to users with disabilities, screen-reader assistive technology, and keyboard-only navigation.

---

## 2. When to Use & When NOT to Use

### When to Use
- Authoring or auditing any user-facing frontend component, modal, or page.
- Pre-release compliance audits against ADA and WCAG 2.1 standards.

### When NOT to Use
- Backend server logic or database scripts.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Frontend component source code and color palette token definitions.

### Prerequisites
- Knowledge of WCAG 2.1 Level AA criteria and ARIA 1.2 authoring practices.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Semantic Landmark Architecture
Structure pages with `<header>`, `<nav>`, `<main>`, `<section>`, and `<footer>` landmarks. Provide skip-to-content links.

### Step 2: Keyboard Navigation & Focus Management
Ensure all interactive elements are focusable via Tab. Implement visible focus rings (`focus-visible:ring-2`). Manage focus traps in modal dialogs.

### Step 3: Color Contrast & Typography Verification
Verify text contrast ratio $\ge 4.5:1$ against background in both Light Mode and Dark Mode ($3:1$ for large text).

### Step 4: ARIA Roles & Labels
Apply `aria-label`, `aria-describedby`, `aria-expanded`, and `aria-live` for dynamic updates (e.g. live queue counts).

### Step 5: Form Accessibility
Ensure all `<input>` elements have associated `<label>` tags with matching `htmlFor`/`id` bindings.

### Step 6: Screen Reader & Axe-Core Audit
Audit pages using automated `axe-core` checks and manual keyboard navigation walkthrough.


---

## 5. Safety Considerations & Guardrails
- Never remove outline rings with `outline: none` without providing an accessible alternative focus indicator.
- Do not convey information using color alone (pair colors with text badges or icons).

---

## 6. Expected Deliverables & Artifacts
- Accessibility-compliant Next.js pages and components.
- Axe-core accessibility audit report with 0 critical/serious violations.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 100% of interactive controls are operable via keyboard alone.
- [ ] Color contrast meets or exceeds WCAG AA (4.5:1) in both Light and Dark modes.
- [ ] Automated accessibility scans report zero critical violations.

---

## 8. Error Recovery & Troubleshooting
- If modal dialogs fail to trap focus, wrap modal contents in a focus-trap container component.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/accessibility-implementation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@accessibility-implementation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `accessibility-implementation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `accessibility-implementation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run accessibility-implementation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt accessibility-implementation`. | `PROMPT FILE` |
| **Windsurf** | Activate `accessibility-implementation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.agents/skills/theme-system/SKILL.md` - Section 2
- `frontend/src/components/Navbar.tsx`
