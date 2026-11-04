---
name: browser-testing
description: >-
  Automate and record real browser execution in genuine Google Chrome with AntiCaptcha extensions.
---

# Browser Testing

## 1. Purpose & Overview
Exercises court portal automation in genuine attended Chrome instances, verifying extension loading, CAPTCHA token injection, party name search, and row extraction with video evidence.

---

## 2. When to Use & When NOT to Use

### When to Use
- Testing court scraper implementations against Florida and Texas portals.
- Validating AntiCaptcha Manifest V3 extension solving and DOM token injection.
- Capturing video recordings for client demonstrations.

### When NOT to Use
- Headless API unit testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Installed Google Chrome, unpacked `anticaptcha-plugin_v0.83/`, portal URLs, and test party names.

### Prerequisites
- Synchronous Playwright with `ChromeSession` architecture.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Browser Manager Launch
Launch Chrome using `SingleSessionBrowserRunner` or `Launch_Attended_Browser.bat` with `--load-extension` flags pointing to `anticaptcha-plugin_v0.83`.

### Step 2: Extension Readiness Check
Verify AntiCaptcha extension loads, pinned status, and API key presence via `chrome://extensions` or DOM flags.

### Step 3: Portal Navigation & Tab Management
Navigate to portal URL. Switch to target search tab (Party Name) using reliable CSS locators.

### Step 4: Search Form Interaction
Fill party Last Name, First Name, and DOL normalized to `MM/dd/yyyy` format.

### Step 5: CAPTCHA Handling & Token Verification
Wait for solve tokens (`g-recaptcha-response`, `cf-turnstile-response`). Verify resolution before search submission.

### Step 6: Result Table Extraction & Verification
Extract table rows, parse columns matching portal schema, and verify zero glossary rows (`CACE`, `COCE`) are included.

### Step 7: Video & Screenshot Evidence Capture
Record browser session into WebP or MP4 artifact and save to `docs/`.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never use aggressive Chrome process termination (`taskkill /f /im chrome.exe`) while an attended user session is running.
- Block speculative form submits when an active, unsolved CAPTCHA challenge is present.

---

## 6. Expected Deliverables & Artifacts
- Verified scraper execution logs with extracted case count.
- Playwright browser video recording (.webp) in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Chrome launches with AntiCaptcha extension active and functional.
- [ ] Portal search executes and parses matching cases into the exact 5-field schema.
- [ ] Video recording confirms smooth, human-paced browser interaction.

---

## 8. Error Recovery & Troubleshooting
- If portal returns a transient Cloudflare block, implement retry with exponential backoff or proxy rotation.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/browser-testing` or slash command `/browser`. | `CUSTOM SKILL` |
| **Cursor** | Select `@browser-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `browser-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `browser-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run browser-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt browser-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `browser-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/base.py`
- `backend/app/automation/browser_manager.py`
