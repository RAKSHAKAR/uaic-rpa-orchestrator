---
name: uaic-unattended-mode
description: >-
  Run background headless browser automation with robust timeout handling, headless Chrome, and error screenshots.
---

# Uaic Unattended Mode

## 1. Purpose & Overview
Executes high-throughput, unattended court portal scraping in the background (`headless=True` or xvfb), handling unexpected dialogs and capturing error screenshots upon failure.

---

## 2. When to Use & When NOT to Use

### When to Use
- Production batch queue processing of high-volume claims.
- Automated overnight queue runs.

### When NOT to Use
- Visual client demonstrations.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `headless=True` in `SystemSettings`, Celery worker daemon, and background display.

### Prerequisites
- Running Celery worker on `scrapers` queue.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Headless Browser Launch
Launch Playwright with `--headless=new` and anti-detection arguments.

### Step 2: Background Extension Execution
Verify AntiCaptcha extension operates headless with injected API key.

### Step 3: Strict Timeout Enforcement
Enforce explicit page navigation timeouts (30s) and CAPTCHA resolution timeouts (60s) to prevent hanging workers.

### Step 4: Error Screenshot & Trace Capture
Upon any navigation or extraction failure, capture full-page screenshot to `backend/screenshots/` and log traceback.

### Step 5: Automatic Worker Recycling
Recycle browser context after task completion to maintain zero memory leakage.

### Step 6: Status Update & Queue Drain
Update claim record in database and pull next available claim from Celery queue.


---

## 5. Safety Considerations & Guardrails
- Never allow an unattended scraper to hang indefinitely; enforce hard timeouts.
- Capture screenshots on all failures for post-mortem operator review.

---

## 6. Expected Deliverables & Artifacts
- Unattended batch claim processing.
- Diagnostic error screenshots in `backend/screenshots/` for any failed portal.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Scrapers run headless in background without desktop popups.
- [ ] Timeout limits terminate hanging pages cleanly.
- [ ] Claim status transitions reliably to `SCRAPED` or `FAILED`.

---

## 8. Error Recovery & Troubleshooting
- If headless mode triggers Cloudflare bot blocks, switch to attended mode or enable residential proxy rotation.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-unattended-mode`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-unattended-mode` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-unattended-mode`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-unattended-mode` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-unattended-mode`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-unattended-mode`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-unattended-mode` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/tests/e2e/test_e2e_unattended_scraping.py`
- `backend/app/tasks/scraper_tasks.py`
