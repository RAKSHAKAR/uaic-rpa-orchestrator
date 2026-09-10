# IMPLEMENTATION PLAN — POWER PLATFORM EMAIL PARITY + ENTERPRISE NOTIFICATION ENGINE

**Implementation ID:** `IMP-2026-0905-004`  
**Target Specification:** [`implementation_plan/ChatGPT_Prompt/Complete Power Platform Email & Notification Implementation Prompt.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/ChatGPT_Prompt/Complete%20Power%20Platform%20Email%20&%20Notification%20Implementation%20Prompt.md) & [`Exact Acceptance Evidence — Email & Notification Implementation.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/ChatGPT_Prompt/Exact%20Acceptance%20Evidence%20%E2%80%94%20Email%20&%20Notification%20Implementation.md)  
**Governance Framework:** Universal AI Engineering Governance Skill (`.agents/skills/diagnose-plan-confirm-execute/SKILL.md`)  
**Status:** PROPOSED — PENDING HUMAN APPROVAL (NO APPROVAL = NO IMPLEMENTATION)

---

## 1. Executive Summary & Objective

The objective of this task is to upgrade the existing rudimentary `notification_email` string field in `SystemSettings` into an **enterprise-grade, dynamic, multi-provider email and notification engine**.

### Mandatory Core Controls (Per User Requirement):
1. **Master ON / OFF Toggle & Granular Rule Toggles**:
   * The administrator can completely disable the Notification Engine with a single master toggle (`email_notifications_enabled: false`).
   * When turned **OFF**, all automated notification dispatches during claim processing, scraping, and Guidewire sync are completely bypassed, introducing zero latency or Celery task overhead.
   * Granular toggles allow enabling/disabling specific events individually (e.g. disable success emails while keeping failure alerts enabled).
2. **Comprehensive Test Functionality**:
   * **Live Test Email Dispatch**: A dedicated test console to input any destination email address and send a test message with real-time feedback (`Queued` $\rightarrow$ `Sent` / `Failed`) and instant delivery log recording.
   * **Provider Connection Handshake Test**: A 1-click **"Test Connection"** button validating SMTP server reachability, port connection, authentication, and TLS handshake without sending an email.
   * **Local Dev / Mock Provider**: A built-in zero-dependency testing provider that logs full HTML/plain-text emails to disk and memory for safe local development and verification.
3. **Full Functional Parity with Power Platform V4 Cloud Flow**: Trace and support legacy `notification_email` alerting behavior on Guidewire case creation, scraper failures, and operational exceptions.
4. **Dynamic Template & Variable Engine**: Reusable, HTML/plain-text templates supporting safe dynamic variables (`{{claim_number}}`, `{{exposure_number}}`, `{{activity_id}}`, `{{case_number}}`, `{{case_style}}`, `{{county}}`, `{{suit_filed_date}}`, `{{timestamp}}`, `{{error_message}}`, etc.).
5. **Transactional Safety & Idempotency**: Guidewire transactions never fail if an email provider is down; unique idempotency keys prevent duplicate email dispatches.
6. **Persistent Delivery Logs & Audit Trail**: Real-time tracking of notification delivery (`QUEUED`, `SENDING`, `SENT`, `FAILED`, `RETRYING`) with error diagnostics.

---

## 2. Power Platform V4 Source Audit & Legacy Trace (AE-001 to AE-003)

### Findings from `PowerAutomateSolutions/BotCreation_1_0_0_7/`
* **Inspection of Desktop Flow Binaries & XML Definitions**:
  * Scanned `customizations.xml`, `solution.xml`, and control repositories.
  * The desktop RPA robot does not contain native desktop email actions (`SendEmail`, `SendExchangeEmail`).
  * **Source Origin**: `notification_email` was an environment variable / parameter passed to the Cloud Flow (`UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A`).
  * **Classification**: `LEGACY CONFIRMED` (Power Platform Cloud Orchestration layer variable passed to Guidewire and alerting).

### Parity Mapping Matrix
| Legacy Power Platform Behavior | Existing Bot_UAIC Implementation | Gap / Required Upgrade |
|---|---|---|
| Master Email Toggle | Missing | Master ON/OFF toggle (`email_notifications_enabled`) in UI and API |
| Alert Recipient (`notification_email`) | Single string in `IntegrationSettings` (`test@test.com`) | Multi-recipient list (To, CC, BCC) with dynamic recipient tags |
| Email Provider | None (placeholder log only) | Pluggable providers: SMTP, Graph, SendGrid, SES, Local Mock |
| Test Functionality | None | Test Connection button + Send Test Email console with live feedback |
| Guidewire Activity Alert | Timings dictionary metadata only | Dedicated `GUIDEWIRE_ACTIVITY_CREATED` event & async dispatch |
| Guidewire Failure Alert | None | Dedicated `GUIDEWIRE_ACTIVITY_FAILED` event & alert |
| Scraper Failure Alert | None | Dedicated `SCRAPER_FAILED` event & alert |
| Template Customization | Hardcoded log format | Dynamic HTML/Plain-text templates with variable substitution |
| Delivery Status & Retry | None | Persistent `Notification` log table + Celery retry with backoff |
| Idempotency | None | Key format: `{event_type}:{claim_id}:{activity_id or hash}` |

---

## 3. Architecture & Technical Design

### A. Master Toggle & Operational Bypass Logic
```text
Application Event (e.g. Guidewire Case Created)
       │
       ▼
Is Master Notification Engine Enabled? (email_notifications_enabled == true)
       ├── NO  ──► Skip dispatch immediately (Zero Celery tasks, Zero DB overhead)
       │
       └── YES ──► Is specific event rule enabled? (e.g. rule.guidewire_activity_created == true)
                     ├── NO  ──► Skip dispatch
                     └── YES ──► Enqueue to Celery 'notifications' Queue
```

### B. Comprehensive Test Architecture
1. **Provider Connection Handshake (`POST /api/v1/settings/email/test-connection`)**:
   * Opens socket to SMTP server / API endpoint.
   * Performs TLS handshake and authentication.
   * Measures latency in milliseconds.
   * Returns: `{ "success": true, "latency_ms": 142, "message": "SMTP handshake & authentication successful" }`.
2. **Live Test Email Dispatch (`POST /api/v1/settings/email/test-send`)**:
   * Sends actual formatted email message to the specified recipient.
   * Creates a `Notification` database record with `event_type="TEST_EMAIL"`.
   * Displays immediately in the Notification Delivery Log.
3. **Local Dev / Mock Mode (`provider="local_mock"`)**:
   * Saves email payload to `logs/emails/email_<timestamp>.html` and memory.
   * Allows full verification of template variable substitution without external SMTP access.

---

### C. Data Layer (New Database Models & Schemas)
1. **`Notification` Model** (`backend/app/models/notification.py`):
   * `id` (Integer / UUID, Primary Key, Indexed)
   * `event_type` (Enum: `GUIDEWIRE_ACTIVITY_CREATED`, `GUIDEWIRE_ACTIVITY_FAILED`, `SCRAPER_FAILED`, `CLAIM_PROCESSING_FAILED`, `TEST_EMAIL`)
   * `claim_id` (ForeignKey to `claim_records.id`, nullable for test emails)
   * `recipient` (String, comma-separated or primary To address)
   * `cc` (String, nullable)
   * `bcc` (String, nullable)
   * `subject` (String, 255 chars)
   * `body_html` (Text)
   * `body_text` (Text)
   * `provider` (String: `smtp`, `sendgrid`, `local_mock`, etc.)
   * `status` (Enum: `PENDING`, `QUEUED`, `SENDING`, `SENT`, `FAILED`, `RETRYING`, `SKIPPED`)
   * `idempotency_key` (String, unique index)
   * `error_message` (Text, nullable)
   * `retry_count` (Integer, default 0)
   * `queued_at`, `sent_at`, `failed_at`, `created_at` (DateTime with UTC)

2. **`NotificationTemplate` Model** (`backend/app/models/notification.py`):
   * `id`, `name`, `event_type`, `subject_template`, `body_template_html`, `body_template_text`, `is_active`, `created_at`, `updated_at`

3. **`NotificationRule` Model** (`backend/app/models/notification.py`):
   * `id`, `event_type`, `is_enabled`, `channels` (JSON list), `recipient_override` (String, nullable), `updated_at`

4. **Expanded `SystemSettings` Schema** (`backend/app/schemas/settings.py`):
   * `EmailSettings`:
     * `email_notifications_enabled`: bool (Master ON/OFF switch, default `True`)
     * `provider`: Literal["smtp", "graph", "sendgrid", "ses", "local_mock"] (default `local_mock` for safe local dev)
     * `smtp_host`: str
     * `smtp_port`: int
     * `smtp_username`: str
     * `smtp_password`: str (masked in responses)
     * `smtp_encryption`: Literal["tls", "ssl", "none"]
     * `from_name`: str
     * `from_email`: str
     * `reply_to`: str
     * `to_recipients`: list[str]
     * `cc_recipients`: list[str]
     * `bcc_recipients`: list[str]
     * `timeout_seconds`: int
     * `retry_count`: int
     * `retry_delay_seconds`: int
   * Auto-syncs legacy `notification_email` to maintain 100% backward compatibility.

---

### D. Service & Worker Layer
1. **`EmailService` & Provider Abstractions** (`backend/app/services/email_service.py`):
   * `BaseEmailProvider`: Abstract contract (`send_email(to, cc, bcc, subject, body_html, body_text) -> EmailDeliveryResult`, `test_connection() -> ConnectionTestResult`).
   * `SmtpEmailProvider`: Async/threaded SMTP with STARTTLS/SSL, authentication, timeout.
   * `MockEmailProvider`: High-fidelity in-memory/file delivery provider for local dev and unit testing (logs email to `logs/emails/` or memory).
   * `TemplateRenderer`: Safe regex/Mustache variable substitution (`{{var}}`), escaping HTML where appropriate, providing sample previews.
   * `IdempotencyManager`: Verifies if an event with `idempotency_key` was already sent before queueing.

2. **`NotificationService`** (`backend/app/services/notification_service.py`):
   * Checks `email_notifications_enabled`: if `False`, exits immediately.
   * Resolves active rules and recipients.
   * Renders templates with dynamic payload variables.
   * Enqueues async Celery task.

3. **Celery Tasks** (`backend/app/tasks/notification_tasks.py`):
   * `send_notification_email_task`:
     * Explicitly bound to `queue="notifications"`.
     * Reads database settings dynamically via `get_system_settings_async()`.
     * Invokes the configured provider.
     * Updates `Notification` record status and logs duration.
     * Supports automatic retries with exponential backoff on transient socket/connection errors.

---

### E. API Endpoints (`backend/app/api/v1/endpoints/notifications.py` & `settings.py`)
* `GET /api/v1/settings/email` $\rightarrow$ Fetch current email provider and recipient settings (secrets masked).
* `POST /api/v1/settings/email` $\rightarrow$ Update email settings (including master ON/OFF toggle) and persist to database.
* `POST /api/v1/settings/email/test-connection` $\rightarrow$ 1-click test of provider reachability and credentials without sending an email.
* `POST /api/v1/settings/email/test-send` $\rightarrow$ Dispatch a live test email to specified recipient; records in notification log.
* `GET /api/v1/notifications` $\rightarrow$ Paginated notification delivery history (filterable by event, status, search).
* `GET /api/v1/notifications/{id}` $\rightarrow$ Detail breakdown for a specific notification.
* `GET /api/v1/notifications/templates` $\rightarrow$ List all notification templates with default variables.
* `PUT /api/v1/notifications/templates/{id}` $\rightarrow$ Update template subject/body.
* `POST /api/v1/notifications/templates/preview` $\rightarrow$ Render template with sample mock data for instant preview.
* `GET /api/v1/notifications/rules` $\rightarrow$ List event notification rules.
* `PUT /api/v1/notifications/rules` $\rightarrow$ Toggle events on/off.

---

### F. Frontend UI: Settings "Email & Notifications" Console
In [`frontend/src/app/settings/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx):
1. **New Tab in Settings Navigation Bar**:
   * Add **"Email & Notifications"** tab with mail icon.
2. **Master Control Banner**:
   * Prominent **Master Toggle**: "Enable Email Notification Engine" with visual status badge (`ACTIVE` in emerald vs. `DISABLED` in slate).
   * Status alert explaining behavior when disabled.
3. **Sub-Panels**:
   * **Email Service & Provider**:
     * Provider Selector: `Local Dev / Mock`, `SMTP`, `Microsoft 365 (Graph)`, `SendGrid`, `AWS SES`.
     * Host, Port, Encryption (TLS/SSL/None), Username.
     * Masked Password input with eye toggle (Show/Hide).
     * **"Test Connection"** button with latency badge and diagnostic result.
   * **Sender & Multi-Recipient Management**:
     * From Name, From Email, Reply-To.
     * Tag input chip controls for `To Recipients`, `CC Recipients`, and `BCC Recipients`.
   * **Notification Rules**:
     * Event grid with individual toggles:
       * `Guidewire Activity Created` (Default: ON)
       * `Guidewire Activity Failed` (Default: ON)
       * `County Scraper Bot Failed` (Default: ON)
       * `Claim Processing Failed` (Default: ON)
   * **Template Manager & Live Preview**:
     * Template selector dropdown.
     * Subject and Body editor with dynamic variable tokens (`{{claim_number}}`, `{{activity_id}}`, etc.).
     * Live Preview box rendering sample data.
   * **Live Test Email Console**:
     * Recipient input with **"Send Test Email"** button.
     * Real-time status feedback badge (`Testing...` $\rightarrow$ `Queued` $\rightarrow$ `Sent` / `Failed`).
   * **Notification Delivery History Table**:
     * Responsive table showing recent notifications: Timestamp, Event Type, Recipient, Subject, Provider, Status badge (`SENT`, `FAILED`, `QUEUED`), duration, and Details drawer.

---

## 4. Proposed File Changes Breakdown

### Backend Files
* **[NEW]** [`backend/app/models/notification.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/models/notification.py): ORM models for `Notification`, `NotificationTemplate`, `NotificationRule`.
* **[MODIFY]** [`backend/app/models/__init__.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/models/__init__.py): Register new models.
* **[MODIFY]** [`backend/app/schemas/settings.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/settings.py): Add `EmailSettings` (with master `email_notifications_enabled`), `NotificationTemplateSchema`, `NotificationRuleSchema`.
* **[NEW]** [`backend/app/services/email_service.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/email_service.py): Core provider abstractions, SMTP client, mock provider, template renderer, and connection test logic.
* **[NEW]** [`backend/app/services/notification_service.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/notification_service.py): Event router, master switch check, idempotency checker, and Celery enqueuer.
* **[NEW]** [`backend/app/tasks/notification_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/notification_tasks.py): Celery async worker task on `notifications` queue.
* **[MODIFY]** [`backend/app/core/celery_app.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/core/celery_app.py): Include `app.tasks.notification_tasks` and route `app.tasks.notification_tasks.*` to queue `notifications`.
* **[NEW]** [`backend/app/api/v1/endpoints/notifications.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/notifications.py): Notification, template, and test REST endpoints.
* **[MODIFY]** [`backend/app/api/v1/api.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/api.py): Register `/notifications` router.
* **[MODIFY]** [`backend/app/api/v1/endpoints/settings.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/settings.py): Add test connection and test send endpoints.
* **[MODIFY]** [`backend/app/tasks/fuzzy_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/fuzzy_tasks.py): Hook Guidewire dispatch results into `NotificationService`.
* **[NEW]** [`backend/tests/test_email_notifications.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_email_notifications.py): Test suite covering master switch, test connection, test send, templates, idempotency, and API endpoints.

### Frontend Files
* **[MODIFY]** [`frontend/src/types/index.ts`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/types/index.ts): Add TypeScript interfaces for `EmailSettings`, `NotificationItem`, `NotificationTemplate`, `NotificationRule`.
* **[MODIFY]** [`frontend/src/lib/api.ts`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/lib/api.ts): Add notification and test email / connection API client methods.
* **[MODIFY]** [`frontend/src/app/settings/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx): Add comprehensive **"Email & Notifications"** tab, master toggle, provider settings, "Test Connection" button, multi-recipient chips, rules, template preview, "Send Test Email" console, and delivery log table.

---

## 5. Verification & Acceptance Plan (Addressing All AE Items)

### Automated Test Matrix
1. **Unit & Service Tests (`pytest backend/tests/test_email_notifications.py`)**:
   * Verify Master Switch: when disabled, no notifications are queued.
   * Verify Test Connection: returns success/error with latency.
   * Verify `MockEmailProvider` delivers and records emails.
   * Verify `SmtpEmailProvider` connection formatting, auth, and error handling.
   * Verify dynamic template variable substitution and escaping.
   * Verify idempotency key prevents duplicate notification creation.
   * Verify Celery task runs on `notifications` queue.
   * Verify secret masking in API responses (passwords never returned).
2. **Regression Test Suite**:
   * Run all 158 existing backend tests: ensure 100% pass.
   * Run `ruff check app tests`: 0 errors.
   * Run `tsc --noEmit`: 0 errors.
   * Run `npm run lint`: 0 errors.
   * Run `scripts\check_ps1_syntax.ps1`: 0 errors.

### Manual & UI Evidence (Matching AE-001 to AE-024)
1. **Master Toggle Verification**: Toggle ON/OFF in Settings UI, verify status persisted in DB and observed by backend.
2. **AE-005**: Verify "Email & Notifications" tab rendered in Settings with all controls.
3. **AE-006 & AE-007**: Verify multiple recipients (`To`, `CC`, `BCC`) save and persist across page refresh.
4. **AE-008 & AE-009**: Verify provider settings persist and passwords remain masked in API and UI.
5. **Test Functionality**: Click **"Test Connection"**, verify instant latency and success feedback. Click **"Send Test Email"**, verify queued Celery task, verify delivery log created in database with `SENT` status.
6. **AE-012 to AE-014**: Verify Guidewire activity created event sends email; verify Guidewire failure sends alert email.
7. **AE-018**: Verify email provider failure does not mark Guidewire transaction failed.
8. **AE-020**: Verify template variables substitution with mock preview.

---

## 6. Open Questions & Confirmation Request

> [!IMPORTANT]
> **Action Required**: In accordance with rule **"NO APPROVAL = NO IMPLEMENTATION"**, no source code has been altered yet.
> Please review this updated implementation plan and confirm whether to proceed with building the full enterprise Power Platform Email & Notification Engine with master ON/OFF toggle and comprehensive test consoles.
