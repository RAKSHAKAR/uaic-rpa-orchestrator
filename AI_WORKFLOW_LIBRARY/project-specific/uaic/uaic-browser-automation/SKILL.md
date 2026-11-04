---
name: uaic-browser-automation
description: >-
  Develop and maintain Playwright Chromium scrapers with anti-detection flags, shadow DOM traversal, and extension integration.
---

# Uaic Browser Automation

## 1. Purpose & Overview
Governs the development of robust web scrapers using Playwright Python, configuring anti-bot evasion arguments, handling dynamic shadow DOM elements, and managing browser contexts.

---

## 2. When to Use & When NOT to Use

### When to Use
- Writing a new portal scraper or updating existing portal locators.
- Debugging AntiCaptcha extension toolbar integration or Chrome options.

### When NOT to Use
- Headless direct HTTP API clients.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target portal URL, search form DOM structure, and Playwright Chromium driver.

### Prerequisites
- Synchronous Playwright API in Python 3.14.7.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Anti-Detection Flag Configuration
Configure Chrome launch arguments: `--disable-blink-features=AutomationControlled`, `--load-extension`, `--disable-infobars`, `--no-sandbox`.

### Step 2: Extension Integration
Load unpacked `anticaptcha-plugin_v0.83/`. Inject API key into extension preferences and pin toolbar.

### Step 3: Robust Locator Strategy
Use resilient CSS and text locators (`#PersonSearchResults`, `a:has-text('Party Name')`). Avoid fragile full XPath.

### Step 4: Explicit Waiting & DOM Polling
Wait for network idle or selector presence (`page.wait_for_selector()`) with explicit timeouts. Avoid arbitrary sleep calls.

### Step 5: Table Parsing & Pagination
Parse table rows (`tbody tr`), clean whitespace, normalize dates, and iterate through pagination controls (`a.next`).

### Step 6: Exception Capture & Screenshots
Wrap critical interactions in try/except blocks; capture full-page screenshot on error to `backend/screenshots/`.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Keep browser automation strictly synchronous for AntiCaptcha extension stability.
- Never bypass or disable CAPTCHA wait loops.

---

## 6. Expected Deliverables & Artifacts
- Robust Playwright scraper class inheriting from `BasePortalScraper`.
- Automated scraper unit and integration tests.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Scraper navigates, searches, and extracts cases deterministically.
- [ ] AntiCaptcha extension resolves challenges seamlessly.
- [ ] Errors capture diagnostic full-page screenshots.

---

## 8. Error Recovery & Troubleshooting
- If locator breaks due to portal redesign, inspect live DOM snapshot and update selector.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-browser-automation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-browser-automation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-browser-automation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-browser-automation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-browser-automation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-browser-automation`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-browser-automation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/base.py`
- `backend/app/automation/browser_manager.py`
