---
name: uaic-settings-validation
description: >-
  Prove that Settings page configuration (headless mode, timeouts, thresholds, credentials) is strictly respected at runtime.
---

# Uaic Settings Validation

## 1. Purpose & Overview
Verifies that all automation settings configured by operators via the `/settings` UI are persisted in database `SystemSettings` and loaded dynamically by scrapers and workers at runtime.

---

## 2. When to Use & When NOT to Use

### When to Use
- Modifying or adding new settings to `/settings` page.
- Verifying runtime adherence to operator-configured timeouts or headless toggles.

### When NOT to Use
- Hardcoding runtime settings in scraper classes.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `SystemSettings` schema (`app/schemas/settings.py`) and `settings_service.py`.

### Prerequisites
- Running backend with settings endpoints.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Settings Schema Inspection
Review `SystemSettings` schema. Verify fields: `headless`, `captcha_wait_seconds`, `match_threshold`, `min_filing_date`, `auto_queue_enabled`, `proxy_enabled`.

### Step 2: Database Persistence Verification
Update setting via `POST /api/v1/settings`. Verify changes persist in `system_settings` table.

### Step 3: Worker Runtime Propagation Audit
Verify that scraper tasks invoke `get_system_settings_async()` to fetch active settings before launching Chrome.

### Step 4: Headless Toggle Verification
Toggle `headless: true/false`. Verify Chrome launches in corresponding headless or GUI mode.

### Step 5: Timeout Adherence Verification
Set `captcha_wait_seconds: 15`. Verify scraper CAPTCHA loop terminates at exactly 15 seconds.

### Step 6: Settings Test Suite Pass
Run `pytest tests/test_automation_runtime_settings.py -q`.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Workers MUST read dynamic settings via `get_system_settings_async()`; never rely solely on static `.env` defaults.
- Mask all credentials (AntiCaptcha key, SMTP password, Guidewire token) in settings API responses.

---

## 6. Expected Deliverables & Artifacts
- Verified settings persistence and runtime propagation.
- Automated test report confirming settings adherence.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Settings persist across backend restarts.
- [ ] Scrapers and workers dynamically adapt to updated settings.
- [ ] Sensitive credentials remain masked.

---

## 8. Error Recovery & Troubleshooting
- If settings fail to propagate to workers, verify workers are querying `get_system_settings_async()` on each task execution.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-settings-validation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-settings-validation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-settings-validation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-settings-validation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-settings-validation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-settings-validation`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-settings-validation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/schemas/settings.py`
- `backend/app/services/settings_service.py`
