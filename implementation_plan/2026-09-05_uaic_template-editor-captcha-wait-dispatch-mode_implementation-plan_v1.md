# Implementation Plan: Email Template Studio, Direct System Notification Mode & CAPTCHA Wait Optimization

**Implementation ID:** `IMP-2026-0905-003`  
**Date:** 2026-09-05  
**Author:** AI Agent (Google Antigravity)  
**Status:** `AWAITING_HUMAN_APPROVAL`  
**Related Documents:**
- `implementation_plan/2026-09-05_uaic_maildev-and-email-receipts_implementation-record_v1.md`
- `implementation_plan/2026-09-05_uaic_enterprise-email-service_implementation-plan_v1.md`
- `AGENTS.md`
- `README.md`

---

## 1. Executive Summary & Problem Diagnosis

### 1.1 User Requirements
1. **Direct System Email vs. Guidewire Activity Notification Toggle**:
   - Currently, match notifications only fire under the event `GUIDEWIRE_ACTIVITY_CREATED` after pushing to Guidewire ClaimCenter.
   - The user requested an option (radio/toggle) allowing match notifications to be sent directly from this system (UAIC Orchestrator) without requiring Guidewire, via Guidewire activity, or both.
2. **Customizable Dynamic Email Template Editor (HTML & Plain Text Views + Dynamic Parameters)**:
   - Currently, templates are hardcoded in `DEFAULT_TEMPLATES` and view-only in the UI.
   - The user requires the ability to customize and save template designs in both **HTML View** and **Plain Text View**, including custom **Subject Line**.
   - An interactive **Dynamic Parameter Palette / Token Selector** must display all available placeholders (`{{claim_number}}`, `{{insured_name}}`, `{{claimant_name}}`, `{{matched_count}}`, `{{county_name}}`, `{{portal_name}}`, `{{timestamp}}`, etc.) with one-click insertion at cursor position, plus live preview and "Reset to System Default".
3. **CAPTCHA Solving Wait Logic & Default Timing across 8 Portals**:
   - In live testing on Broward County (`https://www.browardclerk.org/Web2`), the scraper was prematurely clicking the search submit button (`#PersonSearchResults`) while CAPTCHA solving was still in progress by the AntiCaptcha extension.
   - The automation must actively detect solving status (`.antigate_solver.in_process`, `data-status="in_process"`), verify non-empty response tokens (`g-recaptcha-response`, `cf-turnstile-response`), and NEVER submit while solving is in progress.
   - Default CAPTCHA wait timeout must be increased (from 15s to 60s, configurable up to 300s) to accommodate variance across all 8 Florida and Texas court websites.
4. **Diagnostic Verification (`@[current_problems]`)**:
   - Verified that Pyrefly virtual diagnostics were ephemeral in-memory artifacts. Workspace code passes `ruff check` (0 errors) and `tsc --noEmit` (0 errors).

---

## 2. Technical Architecture & Component Design

```
+-----------------------------------------------------------------------------------------------------+
|                                          SETTINGS / UI                                              |
|                                                                                                     |
|  +-------------------------------------+      +--------------------------------------------------+  |
|  |     Match Notification Strategy     |      |          Email Template Studio & Editor          |  |
|  |  ( ) Direct System Email Only       |      |  - Subject Line Input                            |  |
|  |  ( ) Guidewire Activity Push Only   |      |  - [HTML Source] / [Plain Text] Tabs             |  |
|  |  (*) Both (Guidewire + Direct Email)|      |  - Interactive Token Palette (Click to Insert)   |  |
|  +-------------------------------------+      |  - Live Synchronized Preview                     |  |
|                                               |  - [Save Changes]  [Reset to System Default]     |  |
|                                               +--------------------------------------------------+  |
+-----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-----------------------------------------------------------------------------------------------------+
|                                          BACKEND API                                                |
|                                                                                                     |
|  PUT  /api/v1/notifications/templates/{event_type}       -> Save custom template to DB table        |
|  POST /api/v1/notifications/templates/{event_type}/reset -> Reset custom template to default       |
|  GET  /api/v1/notifications/templates                    -> Retrieve templates + token catalog      |
|  POST /api/v1/notifications/templates/preview            -> Live preview with dynamic mock context  |
+-----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-----------------------------------------------------------------------------------------------------+
|                                     MATCH & DISPATCH ENGINE                                         |
|                                                                                                     |
|  fuzzy_tasks.py -> On positive match:                                                               |
|    - If mode in ('direct_system', 'both'): emit COURT_CASE_MATCHED directly via NotificationService |
|    - If mode in ('guidewire_activity', 'both'): enqueue notify_guidewire_task to push to Guidewire  |
+-----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-----------------------------------------------------------------------------------------------------+
|                                    AUTOMATION & CAPTCHA ENGINE                                      |
|                                                                                                     |
|  AutomationSettings.captcha_wait_seconds: default=60s (ge=5, le=300)                                |
|  detect_and_handle_captcha():                                                                       |
|    1. Wait up to 5-8s for CAPTCHA iframe/container (#RecaptchaField1, .cf-turnstile) to mount      |
|    2. Detect AntiCaptcha extension status: poll .antigate_solver.in_process                         |
|    3. Verify non-empty response token (g-recaptcha-response > 25 chars, cf-turnstile > 20 chars)     |
|    4. Never click submit while in_process is active                                                 |
|    5. Fail gracefully on timeout after full wait_seconds                                           |
+-----------------------------------------------------------------------------------------------------+
```

---

## 3. Detailed Proposed Changes

### Phase 1: Automation Settings & CAPTCHA Wait Logic
1. **`backend/app/schemas/settings.py`**:
   - In `AutomationSettings`:
     - Change `captcha_wait_seconds` default from `15` to `60`.
     - Update validation range to `ge=5, le=300` (allowing up to 5 minutes wait).
2. **`backend/app/automation/base.py`**:
   - Enhance `detect_and_handle_captcha()`:
     - Add initial mounting wait (up to 5s) to detect if any CAPTCHA container or iframe is loading (`#RecaptchaField1`, `.g-recaptcha`, `.cf-turnstile`, `.antigate_solver`, etc.).
     - Poll AntiCaptcha extension element: `.antigate_solver`.
     - If `.antigate_solver.in_process` or status contains `in_process` / `Solving`, continue polling without returning `True`.
     - For reCAPTCHA: verify `g-recaptcha-response` has `len(val) > 25` or `anchor[aria-checked='true']`.
     - For Turnstile: verify `cf-turnstile-response` has `len(val) > 20` or frame text contains "Success".
     - Return `False` if `wait_seconds` expires without verification.
     - Only return `True` when tokens are explicitly verified or if no CAPTCHA exists after thorough scan.
3. **`backend/app/automation/florida/broward.py`**:
   - Double-check `#personSearchForm textarea[name='g-recaptcha-response']` before clicking `#PersonSearchResults`.
   - Prevent clicking search submit if AntiCaptcha is still `.in_process`.

### Phase 2: Notification Dispatch Strategy (Direct System vs. Guidewire Activity)
1. **`backend/app/schemas/settings.py`**:
   - In `IntegrationSettings`:
     - Add `notification_dispatch_mode: str = Field(default="both", description="direct_system, guidewire_activity, both")`
   - In `EmailSettings.rules`:
     - Add `"court_case_matched": True` to default rules dictionary.
2. **`backend/app/tasks/fuzzy_tasks.py`**:
   - On confirmed positive matches:
     - Check `runtime_settings.integration.notification_dispatch_mode`:
       - If `"direct_system"` or `"both"`:
         Emit `COURT_CASE_MATCHED` event with claim details, claimant, insured, driver, and table of matched court cases.
       - If `"guidewire_activity"` or `"both"`:
         Enqueue `notify_guidewire_task` to push to Guidewire ClaimCenter (which emits `GUIDEWIRE_ACTIVITY_CREATED` on success).
       - If `"direct_system"`:
         Complete claim status directly without waiting for Guidewire.
3. **`backend/app/services/email_service.py`**:
   - Add default template for `COURT_CASE_MATCHED`:
     - Name: `"Court Case Match Found - Direct Notification"`
     - Subject: `"Court Docket Match Discovered - Claim {{claim_number}} ({{matched_count}} Case(s))"`
     - HTML body featuring clean responsive table with matched court cases, dockets, and county court links.

### Phase 3: Customizable Dynamic Email Template Editor
1. **`backend/app/api/v1/endpoints/notifications.py`**:
   - Add dynamic parameter catalog dictionary:
     - `claim_number`, `exposure_number`, `insured_name`, `claimant_name`, `driver_name`, `party_name`, `activity_id`, `matched_count`, `county_name`, `portal_name`, `error_message`, `http_status`, `attempt_number`, `timestamp`, `environment`, `recipient`, `provider`.
   - Enhance `GET /api/v1/notifications/templates`:
     - Fetch all rows from `NotificationTemplate` table in DB.
     - Merge with `TemplateRenderer.DEFAULT_TEMPLATES` (DB custom overrides take precedence).
     - Include `available_variables` with descriptions and sample values.
   - Add `PUT /api/v1/notifications/templates/{event_type}`:
     - Upsert custom template (`subject_template`, `body_template_html`, `body_template_text`, `is_active=True`) into `NotificationTemplate` table.
   - Add `POST /api/v1/notifications/templates/{event_type}/reset`:
     - Remove custom template row from DB or reset to system default.
   - Enhance `POST /api/v1/notifications/templates/preview`:
     - Support custom `subject_template`, `body_template_html`, `body_template_text` in preview request.
2. **`backend/app/services/email_service.py` & `backend/app/services/notification_service.py`**:
   - Update `TemplateRenderer.get_template()` and `NotificationService.emit_event()`:
     - Query DB `NotificationTemplate` table for custom active template for `event_type`.
     - Fallback to `DEFAULT_TEMPLATES` if not customized in DB.
3. **`frontend/src/lib/api.ts`**:
   - Add API methods:
     - `getNotificationTemplates()`
     - `updateNotificationTemplate(eventType, data)`
     - `resetNotificationTemplate(eventType)`
     - `previewTemplate(payload)`
4. **`frontend/src/app/settings/page.tsx`**:
   - **Match Dispatch Strategy Section**:
     - Radio group: `Direct System Notification Only`, `Guidewire Activity Push Only`, `Both (Guidewire + Direct System Email)`.
   - **Template Studio & Editor**:
     - Toggle: "Live Preview" vs. "Edit Template".
     - Subject Line Editor.
     - HTML Editor & Plain Text Editor tabs.
     - **Dynamic Parameter Palette**:
       - Categorized badges for all tokens.
       - Clicking a token inserts `{{token}}` into the active editor at the cursor position.
     - Real-time synchronized preview.
     - "Save Template" and "Reset to Default" buttons.
     - "Send Test with This Template" button to send live test to `priyer@test.com`.

---

## 4. Verification Plan

### Automated Tests
1. **Backend Pytest**:
   - Run `pytest backend/tests/test_email_notifications.py` to verify:
     - Template persistence, preview rendering, and DB override fallback.
     - Match dispatch mode logic (`direct_system`, `guidewire_activity`, `both`).
     - Event rules filtering.
   - Run full test suite: `pytest` (172+ tests pass).
2. **Backend Lint**:
   - Run `ruff check app tests` (0 errors).
3. **Frontend TypeScript & Build**:
   - Run `npx tsc --noEmit` (0 errors).
   - Run `npm run build` (all routes pass).
4. **Email Address Hygiene**:
   - Run `python scripts/find_uaic_emails.py` (0 occurrences of `[at]uaic.com`).
5. **PowerShell Syntax Check**:
   - Run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1` (0 errors).

### Live Verification
1. **CAPTCHA Waiting Verification**:
   - Run browser launch test in attended mode on Broward County URL to observe AntiCaptcha solving wait behavior.
2. **Template Editor Verification**:
   - Edit a template in `/settings` (e.g. modify Subject and HTML).
   - Click a parameter chip (e.g. `{{insured_name}}`) to verify cursor insertion.
   - Save changes and verify DB persistence.
   - Click "Reset to Default" and verify restoration.
3. **Live Test Dispatch**:
   - Send test email using the customized template to `priyer@test.com` and inspect delivery receipt.
