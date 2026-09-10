# Walkthrough — Dynamic Template Studio, CAPTCHA Wait & Dispatch Mode

Implementation ID:   IMP-2026-0905-003
Project:             UAIC Claim & RPA Orchestrator
Module:              backend / frontend / automation / settings / notifications
Feature / Issue:     Dynamic Email Template Studio, CAPTCHA Solving Wait & Match Notification Dispatch Mode
Document Type:       Walkthrough
Version:             v1
Status:              Completed
Created:             2026-09-05
Last Updated:        2026-09-05
AI Agent:            Antigravity
Approval Status:     Approved
Approved By:         User
Approval Date:       2026-09-05
Human Verified:      Pending User Verification
Verified By:         Pending
Verification Date:   Pending

---

## 1. Overview of Delivered Features

In response to direct operational testing feedback, this engineering iteration resolved three critical capabilities across the platform:

1. **AntiCaptcha Solving Wait & Timeout Resiliency**:
   - Resolved the race condition on `https://www.browardclerk.org/Web2` (and all other portals) where search submission was clicked while token solving was still in progress.
   - Built a pre-submission solver blocker in `backend/app/automation/base.py` that waits up to `captcha_wait_seconds` for `.antigate_solver.in_process` to clear and for valid token strings to be populated (`g-recaptcha-response > 25`, `cf-turnstile-response > 20`, or `h-captcha > 20`).
   - Increased the system default `captcha_wait_seconds` from 15s to **60s** (configurable in Settings across the 5s–300s range).
   - In `backend/app/automation/florida/broward.py`, added an explicit pre-submission solver settlement check right before clicking the search button.

2. **Match Notification Dispatch Mode Strategy**:
   - Introduced a 3-way selectable dispatch strategy in Automation & Robot Settings:
     - `both` (Default): Pushes court match details to Guidewire and dispatches direct system emails immediately.
     - `direct_system`: Dispatches rich HTML emails directly from the UAIC Orchestrator to notify adjusters and marks the claim completed, without requiring a Guidewire activity call.
     - `guidewire_activity`: Pushes to Guidewire and relies solely on Guidewire activity creation triggers.
   - Integrated `court_case_matched` into the notification rule matrix with full recipient configuration.
   - Added automatic styled HTML table generation (`matched_cases_table`) formatted with dark/light themes for all court matches.

3. **Full Dynamic Email Template Studio & Designer**:
   - Upgraded the Settings page notification previewer into a full-featured visual **Template Studio**.
   - Enables real-time editing and customization of email templates in both **HTML View** and **Plain Text View**.
   - Added an editable **Subject Line** input.
   - Implemented an interactive **Dynamic Parameter Palette** organizing all variables into categories (Claim Details, Claimant & Driver, Matched Court Data, Guidewire & System) with 1-click cursor insertion.
   - Added live synchronized preview with HTML/Plain text view switcher and dark/light preview iframe.
   - Provided persistent database storage for customized templates and a **"Reset to Default"** action that cleanly restores factory system templates.

---

## 2. File Changes & Architecture

### Backend
- `backend/app/schemas/settings.py`:
  - Increased `captcha_wait_seconds` default from 15 to `60` (`ge=5, le=300`).
  - Added `notification_dispatch_mode: str = Field(default="both")` to `IntegrationSettings`.
  - Added `"court_case_matched": True` to default `EmailSettings.rules`.
- `backend/app/automation/base.py`:
  - Added defensive async evaluation helpers `_safe_eval` and `_safe_wait_timeout`.
  - Implemented initial 5s scan for solver initialization.
  - Implemented blocking loop awaiting `.antigate_solver.in_process` to disappear or clear.
  - Verified DOM response token lengths for reCAPTCHA, Turnstile, and hCaptcha.
- `backend/app/automation/florida/broward.py`:
  - Added explicit pre-submit solver settlement check in `search_by_name`.
- `backend/app/services/email_service.py`:
  - Added default system template for `COURT_CASE_MATCHED` with inline styling and placeholder tokens.
- `backend/app/tasks/fuzzy_tasks.py`:
  - Wired `notification_dispatch_mode` (`both`, `direct_system`, `guidewire_activity`) into match processing.
  - Generates HTML `matched_cases_table` dynamically for match notifications.
- `backend/app/services/notification_service.py`:
  - Enhanced template lookup: queries `NotificationTemplate` in DB for customized user templates before falling back to `DEFAULT_TEMPLATES`.
- `backend/app/api/v1/endpoints/notifications.py`:
  - `GET /templates/tokens`: Returns the comprehensive dynamic parameter catalog with descriptions and sample values.
  - `PUT /templates/{event_type}`: Updates and persists custom template HTML, text, and subject in the database.
  - `POST /templates/{event_type}/reset`: Clears custom overrides and reverts to system factory defaults.
  - `POST /templates/preview`: Renders live HTML/text drafts with sample test payloads.
- `backend/tests/test_email_notifications.py`:
  - Added `test_template_studio_crud_and_preview` covering template CRUD, parameter catalogs, draft rendering, and reset.

### Frontend
- `frontend/src/types/index.ts`:
  - Added `TemplateParameter`, `TemplateUpdateRequest`, `TemplatePreviewRequest`.
  - Updated `NotificationTemplate` with optional text body and custom status.
  - Added `notification_dispatch_mode` to `IntegrationSettings`.
- `frontend/src/lib/api.ts`:
  - Added `updateNotificationTemplate`, `resetNotificationTemplate`, `getTemplateTokens`.
  - Upgraded `previewNotificationTemplate` to accept custom draft subject, HTML, and text.
- `frontend/src/app/settings/page.tsx`:
  - Added `court_case_matched` event rule row in Notifications tab.
  - Added Match Notification Strategy radio selector cards (`both`, `direct_system`, `guidewire_activity`).
  - Added Dynamic Email Template Studio with:
    - Subject input
    - Format toggle (HTML View vs. Plain Text View)
    - Code editor textareas with monospace font
    - Categorized token chips with 1-click insertion
    - Live synchronized preview pane (Subject, HTML view, Plain text view)
    - "Save Custom Template" and "Reset to System Default" buttons

---

## 3. Verification Results

| Quality Gate | Command | Result | Notes |
|---|---|---|---|
| **Backend Test Suite** | `pytest --tb=short -q` | **100% PASS** | 173 passed (including scraper and template studio tests) |
| **Backend Lint** | `ruff check app tests` | **0 ERRORS** | Zero lint or formatting warnings |
| **Frontend TypeScript** | `npx tsc --noEmit` | **0 ERRORS** | Zero type errors across all routes and components |
| **Frontend Next.js Build** | `npm run build` | **0 ERRORS** | All 11 App Router routes compiled cleanly |
| **PowerShell Scripts** | `scripts\check_ps1_syntax.ps1` | **0 ERRORS** | All `.ps1` scripts validated without syntax errors |
| **Email Address Safety** | `python scripts\find_uaic_emails.py` | **0 MATCHES** | 0 occurrences in source code, documentation, and SQLite DB |

---

## 4. Human Verification Instructions

1. **Verify Template Studio**:
   - Navigate to `/settings` -> **Email & Notifications** tab.
   - Select any template from the dropdown (e.g. `Court Case Match Detected`).
   - Notice the editable Subject line and HTML / Plain Text view switcher.
   - Click on any token chip in the Dynamic Parameter Palette to insert `{{parameter}}` at the cursor.
   - Click **Save Custom Template** and observe instant live preview update.
   - Click **Reset to Default** to verify factory template restoration.
2. **Verify Dispatch Strategy**:
   - In Settings, locate the **Match Notification Strategy** section.
   - Toggle between `Direct System Email Only`, `Guidewire Activity Only`, and `Both`.
   - Save settings and verify persistence.
3. **Verify CAPTCHA Wait Time**:
   - In the Automation & Scraping tab, observe `Default CAPTCHA Wait Time` defaults to `60` seconds.
