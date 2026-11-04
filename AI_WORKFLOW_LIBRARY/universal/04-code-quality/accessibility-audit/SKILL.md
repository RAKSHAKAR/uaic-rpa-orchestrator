---
name: accessibility-audit
description: >-
  Evaluate frontend accessibility against WCAG 2.1 AA standards, color contrast, focus rings, and screen-reader semantics.
---

# Accessibility Audit

## 1. Purpose & Overview
Audits rendered HTML, CSS stylesheets, and interactive React components against international accessibility standards to guarantee usability for all operators.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pre-release quality gates for user interfaces.
- Following significant redesigns of pages, stat cards, or form controls.

### When NOT to Use
- Backend server code or database testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Frontend application running locally on port 3000.
- Playwright browser automation or axe-core testing scripts.

### Prerequisites
- Next.js frontend running and reachable.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Automated Axe-Core Scan
Run automated accessibility scan across all primary routes (`/`, `/health`, `/monitor`, `/settings`, `/branding`). Log all violations.

### Step 2: Color Contrast Ratio Calculation
Measure contrast of all text elements against backgrounds in both Light Mode and Dark Mode. Confirm $\ge 4.5:1$ ratio.

### Step 3: Keyboard Navigation Walkthrough
Traverse entire application using keyboard alone (`Tab`, `Shift+Tab`, `Enter`, `Escape`). Verify visible focus rings and zero focus traps.

### Step 4: Screen Reader Semantic Verification
Verify ARIA roles, form labels, and live region announcements for dynamic updates.

### Step 5: Remediation Roadmap
Document specific CSS and JSX fixes for all identified contrast or markup issues.


---

## 5. Safety Considerations & Guardrails
- Never compromise accessible contrast to satisfy purely subjective aesthetic preferences.
- Ensure both Light Mode and Dark Mode are audited equally.

---

## 6. Expected Deliverables & Artifacts
- WCAG 2.1 AA Accessibility Audit Report.
- Annotated violation list with file locations and recommended JSX fixes.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero Critical or Serious violations reported by automated accessibility audits.
- [ ] 100% of text elements satisfy 4.5:1 contrast in both Light and Dark themes.
- [ ] All interactive elements support full keyboard navigation.

---

## 8. Error Recovery & Troubleshooting
- If automated axe-core scans fail on dynamic modals, test modal rendering in isolated test fixtures.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/accessibility-audit`. | `CUSTOM SKILL` |
| **Cursor** | Select `@accessibility-audit` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `accessibility-audit`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `accessibility-audit` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run accessibility-audit`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt accessibility-audit`. | `PROMPT FILE` |
| **Windsurf** | Activate `accessibility-audit` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.agents/skills/theme-system/SKILL.md` - Section 2
- `frontend/src/app/branding/page.tsx`
