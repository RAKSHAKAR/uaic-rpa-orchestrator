---
name: cross-browser-testing
description: >-
  Validate application rendering, layouts, and JavaScript execution across Chromium, Firefox, and WebKit browser engines.
---

# Cross Browser Testing

## 1. Purpose & Overview
Ensures the web application functions identically and consistently across all major web browser engines without engine-specific rendering bugs or CSS breakage.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pre-release testing of the frontend web application.
- Testing advanced CSS layouts, sticky scrollbars, or flexbox containers.

### When NOT to Use
- Court portal automation bots (which are strictly pinned to Google Chrome for AntiCaptcha MV3 stability).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Next.js frontend application running locally on port 3000.
- Playwright browser engines (Chromium, Firefox, WebKit).

### Prerequisites
- Playwright browser binaries installed.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Chromium Engine Pass
Execute Playwright suite against Chromium. Capture baseline rendering and layout measurements.

### Step 2: Firefox Engine Pass
Execute suite against Firefox. Check font rendering, form control styles, and CSS grid alignment.

### Step 3: WebKit Engine Pass
Execute suite against WebKit (Safari engine). Check date inputs, flexbox alignments, and backdrop blur filters.

### Step 4: Discrepancy Cataloguing
Log any layout shifts, font mismatches, or interaction differences between engines.

### Step 5: CSS Prefix & Fallback Remediation
Apply standard CSS vendor fallbacks to eliminate cross-browser inconsistencies.


---

## 5. Safety Considerations & Guardrails
- Remember that court automation scrapers are strictly Chrome-only; cross-browser testing applies exclusively to the Next.js frontend UI.

---

## 6. Expected Deliverables & Artifacts
- Cross-Browser Compatibility Report.
- Comparative screenshots across Chromium, Firefox, and WebKit.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All primary frontend routes render cleanly across Chromium, Firefox, and WebKit.
- [ ] Zero JavaScript console exceptions thrown in any engine.
- [ ] Forms, tables, and buttons function identically across all engines.

---

## 8. Error Recovery & Troubleshooting
- If WebKit exhibits CSS flexbox bugs, apply explicit width constraints or Tailwind vendor prefix utilities.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/cross-browser-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@cross-browser-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `cross-browser-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `cross-browser-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run cross-browser-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt cross-browser-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `cross-browser-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/app/page.tsx`
- `AGENTS.md` - Section 8
