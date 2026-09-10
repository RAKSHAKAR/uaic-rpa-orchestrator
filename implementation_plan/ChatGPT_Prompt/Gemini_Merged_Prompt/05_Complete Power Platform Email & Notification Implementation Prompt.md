# MASTER PROMPT — POWER PLATFORM EMAIL PARITY + DYNAMIC EMAIL/NOTIFICATION ENGINE

You are working on the **existing UAIC Claim & RPA Orchestrator** application.

This is an **existing production-oriented system**. Do NOT treat this as a greenfield development.

Your task is to deeply inspect the existing implementation, the Power Platform source workflows, especially the latest:

**UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A**

and implement/correct the complete email and notification behavior so that this solution has full functional parity with the previous Power Platform system while also providing a more dynamic, configurable, reliable and maintainable architecture.

---

# 1. CRITICAL RULE — INSPECT BEFORE MODIFYING

Before changing any code:

1. Inspect the complete existing repository.
2. Inspect frontend.
3. Inspect backend.
4. Inspect database models/migrations.
5. Inspect settings/configuration.
6. Inspect Celery tasks/workers.
7. Inspect Redis configuration.
8. Inspect notification/email-related code.
9. Inspect Guidewire integration.
10. Inspect all existing logging/audit functionality.
11. Inspect all existing environment variables.
12. Inspect all existing Power Platform exports available in the repository/workspace.
13. Locate and inspect the actual V4 Power Platform export:

`UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A`

14. Inspect every related child flow/subflow involved in:
   - claim processing
   - scraping
   - fuzzy matching
   - Guidewire
   - failure handling
   - status updates
   - notifications
   - email
   - queue processing

Do NOT rely only on filenames.

Search inside JSON/XML/exported workflow definitions for:

```text
email
notification
notification_email
send email
Send an email
mail
recipient
To
CC
BCC
subject
body
HTML
Office 365
Outlook
SMTP
Graph
Exchange
Guidewire
ActivityID
caseupdate
failure
success
completed
failed
alert
```

Also inspect expressions, variables, environment variables, connection references, custom connectors and child flows.

---

# 2. DO NOT ASSUME THAT notification_email IS THE ONLY EMAIL BEHAVIOR

The user has identified that the previous Power Platform/Guidewire system used:

```text
notification_email
```

and that the current application does not expose an equivalent setting.

Do NOT simply add one textbox called `notification_email`.

Determine exactly:

1. Where `notification_email` originated.
2. Whether it was:
   - a workflow variable
   - environment variable
   - Dataverse column
   - Guidewire payload property
   - recipient field
   - configuration value
   - hardcoded value
   - user/business configuration
3. Which workflow populated it.
4. Which workflow consumed it.
5. Which email action sent the message.
6. Which event triggered the message.
7. What subject was used.
8. What body/content was used.
9. What data was inserted dynamically.
10. Whether CC/BCC existed.
11. Whether multiple recipients were supported.
12. Whether the notification was sent before or after Guidewire response.
13. Whether notification failure affected the main workflow.
14. Whether retry behavior existed.
15. Whether notification status was persisted.

Do not invent any of these behaviors.

If V4 contains the information, reproduce it exactly.

If V4 does not contain it, explicitly document that fact and then implement the recommended dynamic architecture described below.

---

# 3. POWER PLATFORM EMAIL PARITY

The new system must preserve every email behavior that actually exists in V4.

For every discovered email operation, create a parity matrix:

| Power Platform Behavior | Existing App | Missing | Required Implementation |
|---|---|---|---|
| Recipient | | | |
| CC | | | |
| BCC | | | |
| Subject | | | |
| Body | | | |
| HTML | | | |
| Dynamic variables | | | |
| Trigger | | | |
| Provider | | | |
| Retry | | | |
| Failure handling | | | |
| Audit | | | |
| Delivery status | | | |

Do not mark a feature as implemented merely because code exists.

Verify actual runtime behavior.

---

# 4. IMPLEMENT A CENTRAL EMAIL SERVICE

Create a reusable backend email service.

Recommended architecture:

```text
Application Event
      ↓
Notification Service
      ↓
Notification Routing
      ↓
Email Template
      ↓
Recipient Resolution
      ↓
Notification Queue
      ↓
Celery Worker
      ↓
Email Provider
      ↓
Delivery Result
      ↓
Notification Log
```

Do NOT send email synchronously from the main scraping or Guidewire request whenever avoidable.

Email delivery should normally be asynchronous.

This prevents:

- Guidewire delays
- scraper delays
- HTTP request blocking
- queue worker blocking
- slow SMTP/API operations
- notification failures from breaking successful claim processing

---

# 5. CENTRAL EMAIL CONFIGURATION

Add a proper Email/Communication section to the existing Settings system.

Do NOT create a separate disconnected configuration mechanism.

The existing application already has centralized settings and communication-provider requirements. Extend the existing architecture.

The Admin/Super Admin should be able to configure:

### Email Provider

```text
Email Enabled
Provider
Provider Status
From Name
From Email
Reply-To
SMTP/API Host
Port
Username
Password/API Key
Encryption
Connection Timeout
Retry Count
Retry Delay
```

Support a provider abstraction rather than hardcoding SMTP.

At minimum design the system so providers can include:

```text
SMTP
Microsoft 365 / Graph
SendGrid
AWS SES
Other API-based provider
```

Only implement providers that are actually required/appropriate for the current environment, but keep the architecture provider-independent.

---

# 6. SECURITY

NEVER expose email passwords, SMTP passwords, API keys or tokens in:

- frontend source
- browser responses
- logs
- audit logs
- exported configuration
- Git
- screenshots
- API responses
- error messages

Secrets must be stored securely.

Sensitive settings should be masked in UI:

```text
********
```

Provide:

```text
Show
Hide
Test Connection
Save
```

where appropriate.

Never store secrets in plaintext if the existing application has a secure secret mechanism available.

---

# 7. EMAIL RECIPIENT CONFIGURATION

Provide a dynamic recipient configuration system.

The administrator should be able to configure:

### Default notification recipients

```text
To
CC
BCC
```

with multiple recipients.

Example:

```text
claims@company.com
admin@company.com
```

Do not restrict the system to a single email address.

Support recipient types such as:

```text
Specific Email
User Email
Role
Team
Business/Organization
Claim Owner
Assigned User
Configured Notification Email
```

Only implement recipient types that are compatible with the current application's data model, but architect the resolver so additional types can be added without rewriting the notification engine.

---

# 8. GUIDEWIRE NOTIFICATION EMAIL

The Guidewire workflow must support the legacy `notification_email` behavior.

After successful Guidewire case/activity creation, determine whether the Power Platform system sends a notification.

If yes, reproduce that behavior.

The event should be something equivalent to:

```text
GUIDEWIRE_ACTIVITY_CREATED
```

Payload should be able to contain:

```text
Claim Number
Exposure Number
Activity ID
Matched Case Number
Case Style
County
County Website
Suit Filed Date
Guidewire Request
Guidewire Response
Execution Time
```

Do not send sensitive internal information unnecessarily.

---

# 9. DYNAMIC EMAIL TEMPLATE ENGINE

Do not hardcode the Guidewire email subject/body inside Python.

Create reusable notification templates.

Example template:

```text
Template Name:
Guidewire Activity Created
```

Subject:

```text
Guidewire Activity Created - {{claim_number}}
```

Body:

```text
Claim Number: {{claim_number}}

Exposure Number: {{exposure_number}}

Activity ID: {{activity_id}}

Matched Case:
{{case_number}}

Case Style:
{{case_style}}

County:
{{county}}

Suit Filed Date:
{{suit_filed_date}}
```

The exact legacy V4 content must be preserved where it exists.

The template system should support dynamic variables.

---

# 10. TEMPLATE VARIABLE SYSTEM

Implement safe variable substitution.

Examples:

```text
{{claim_number}}
{{exposure_number}}
{{activity_id}}
{{case_number}}
{{case_style}}
{{county}}
{{county_website}}
{{suit_filed_date}}
{{claimant_first_name}}
{{claimant_last_name}}
{{insured_first_name}}
{{insured_last_name}}
{{driver_first_name}}
{{driver_last_name}}
{{dol}}
{{timestamp}}
{{environment}}
{{status}}
{{error_message}}
```

The exact variables must be derived from the actual event payload.

Unknown variables must not silently produce broken emails.

Provide validation before saving templates.

---

# 11. ADMIN UI FOR EMAIL

Add email configuration to the existing Admin Settings area.

Do not create an isolated page unless the current architecture requires one.

The UI should include sections such as:

## Email Service

```text
Email Notifications       ON/OFF
Provider                  SMTP / Graph / SES / SendGrid
Provider Status
```

## Sender

```text
From Name
From Email
Reply-To
```

## Default Recipients

```text
To
CC
BCC
```

## Delivery

```text
Retry Count
Retry Delay
Timeout
```

## Testing

```text
Test Email Address
[ Send Test Email ]
```

Show:

```text
Connection successful
Email queued
Email sent
Email failed
```

Never display credentials.

---

# 12. NOTIFICATION RULES

Implement configurable notification rules.

Example:

```text
Event                         Email
---------------------------------------------
Guidewire Activity Created    ON
Guidewire Failed              ON
Claim Processing Failed       ON
Scraper Failed                ON
No Match Found                Optional
Queue Failed                  ON
System Error                  ON
```

The exact default events must be based on the Power Platform behavior plus sensible enterprise defaults.

Do not force every event to generate an email by default.

Allow the administrator to enable/disable notification events.

---

# 13. CLAIM-SPECIFIC NOTIFICATION OVERRIDE

If the existing business requirement requires `notification_email` per claim or per transaction, support it.

Example:

```text
Claim
 └── Notification Email
```

However, define precedence clearly:

```text
Claim-specific recipient
        ↓
Business/tenant recipient
        ↓
Global notification recipient
```

or another precedence discovered from V4.

Do not override legacy behavior without documenting the reason.

---

# 14. NOTIFICATION PREFERENCES

Create a reusable notification preference model.

For each notification event support:

```text
Enabled
Email
In-App
Push
SMS
WhatsApp
```

Only channels configured and supported in the current deployment should become active.

This prepares the platform for future omnichannel notifications without redesigning the event system.

The broader platform architecture already defines Email, SMS, WhatsApp, Push and In-App communication channels, so this should be implemented in a reusable way rather than as a Guidewire-only special case.

---

# 15. NOTIFICATION DELIVERY LOG

Create persistent notification records.

Store:

```text
Notification ID
Event Type
Claim ID
Recipient
CC
BCC
Template
Subject
Provider
Status
Queued At
Sent At
Failed At
Retry Count
Provider Message ID
Error
Created At
```

Statuses should include at least:

```text
PENDING
QUEUED
SENDING
SENT
FAILED
RETRYING
CANCELLED
```

Do not store sensitive credentials.

---

# 16. EMAIL DELIVERY RETRY

Email failures must not silently disappear.

Implement:

```text
Attempt 1
 ↓
Failure
 ↓
Retry
 ↓
Failure
 ↓
Retry
 ↓
Final Failure
```

Use Celery/Redis for asynchronous processing.

Respect existing queue architecture.

Do not create an additional unnecessary queue system if Celery/Redis already provides the required infrastructure.

---

# 17. IDEMPOTENCY

Prevent duplicate emails.

For important events such as:

```text
GUIDEWIRE_ACTIVITY_CREATED
```

generate an idempotency key.

Example:

```text
GUIDEWIRE_ACTIVITY_CREATED:{claim_id}:{activity_id}
```

Before sending:

```text
Check whether notification already succeeded
```

If already sent:

```text
Do not send duplicate email.
```

This is especially important because Celery tasks may retry.

---

# 18. GUIDEWIRE FAILURE NOTIFICATION

If Guidewire fails:

```text
GUIDEWIRE_ACTIVITY_FAILED
```

should be emitted.

The notification should contain useful diagnostic information such as:

```text
Claim Number
Exposure Number
Failure Reason
HTTP Status
Correlation ID
Timestamp
```

Do not expose secrets or authorization tokens.

---

# 19. SCRAPER FAILURE NOTIFICATION

If a county scraper fails repeatedly, the notification engine should be able to emit:

```text
SCRAPER_FAILED
```

with:

```text
Claim
County
Portal
Bot
Error
Attempt
Duration
Timestamp
```

This should be configurable.

---

# 20. NO-MATCH NOTIFICATION

Do NOT automatically assume that "No Match Found" must generate an email.

Check V4 behavior first.

If V4 sends such an email, reproduce it.

If it does not, make it an optional configurable notification event.

---

# 21. BATCH / DIGEST MODE

To make the application faster and reduce unnecessary emails, support optional digest notifications.

For example:

```text
Immediate
Hourly Digest
Daily Digest
```

Do not use digest mode for critical notifications unless explicitly configured.

Example:

```text
Guidewire failure → Immediate

Successful Guidewire activities → Immediate or Digest
```

This should be configurable.

---

# 22. EMAIL TEMPLATE ADMINISTRATION

Provide an Admin UI for:

```text
Templates
Create
Edit
Duplicate
Enable/Disable
Preview
Test Send
Version
Variables
```

Templates should support:

```text
HTML
Plain Text
Subject
Body
```

The existing platform communication design already specifies a notification template manager with WYSIWYG/HTML editing and variable injection.

---

# 23. TEMPLATE PREVIEW

Provide:

```text
Preview
```

with sample data.

Example:

```text
Claim Number: 0100234567
Exposure Number: 1
Activity ID: SAMPLE-123
```

Never require a real Guidewire transaction just to preview an email.

---

# 24. TEST EMAIL

The Settings UI must provide:

```text
Send Test Email
```

Test must verify:

```text
Provider configuration
Authentication
Recipient
Template rendering
Queue
Worker
Delivery
```

Do not report "success" merely because the API accepted the request.

Where possible, display:

```text
Queued
Sent
Failed
```

and persist the result.

---

# 25. EMAIL HEALTH MONITORING

Add email health to the existing system health/engine monitoring.

Display:

```text
Email Service
CONNECTED
```

or:

```text
DEGRADED
```

or:

```text
FAILED
```

Metrics:

```text
Emails Sent
Emails Failed
Emails Pending
Emails Retrying
Last Successful Delivery
Last Failure
```

Do not make the monitoring page unnecessarily expensive.

Use aggregated queries and caching where appropriate.

---

# 26. EMAIL QUEUE PERFORMANCE

Email must not slow down:

```text
Queue ingestion
Scraping
Fuzzy matching
Guidewire
Claim processing
```

Use asynchronous Celery jobs.

Avoid:

```python
send_email()
```

directly inside the critical Guidewire/scraper request path unless absolutely required.

Preferred:

```text
Guidewire success
      ↓
Create notification event
      ↓
Commit transaction
      ↓
Queue email task
      ↓
Return/continue processing
      ↓
Email worker sends email
```

---

# 27. TRANSACTIONAL SAFETY

A successful Guidewire transaction must not be marked failed merely because an email provider is temporarily unavailable.

Example:

```text
Guidewire = SUCCESS
Email = FAILED
```

Overall claim/Guidewire business status should remain:

```text
SUCCESS
```

while notification status becomes:

```text
FAILED
```

and can retry independently.

This separation is extremely important.

---

# 28. EVENT-DRIVEN ARCHITECTURE

Create a reusable event model.

Examples:

```text
CLAIM_CREATED
CLAIM_PROCESSING_STARTED
CLAIM_PROCESSING_COMPLETED
CLAIM_PROCESSING_FAILED

SCRAPER_STARTED
SCRAPER_COMPLETED
SCRAPER_FAILED
NO_MATCH_FOUND
POSITIVE_MATCH_FOUND

FUZZY_MATCH_COMPLETED
FUZZY_MATCH_FAILED

GUIDEWIRE_ACTIVITY_CREATED
GUIDEWIRE_ACTIVITY_FAILED

QUEUE_ITEM_FAILED
QUEUE_ITEM_RETRIED

SYSTEM_ERROR
```

Email should subscribe to these events through notification rules.

Do not hardwire email logic into every business service.

---

# 29. AUDIT LOGGING

Every administrative change to:

```text
Email provider
Recipient configuration
Templates
Notification rules
Notification preferences
```

must be auditable.

Record:

```text
Who
What
When
Before
After
```

Never record passwords/API keys.

---

# 30. CURRENT SETTINGS MUST REMAIN THE SINGLE SOURCE OF TRUTH

Do not introduce separate configuration files for settings that already exist in the application.

The system must follow:

```text
Admin Settings
      ↓
Database/secure configuration
      ↓
Backend service
      ↓
Celery workers
      ↓
Email provider
```

Workers must load the latest effective configuration.

Do not require restarting the entire application simply because an administrator changes:

```text
Recipient
Template
Notification rule
Email enabled/disabled
```

where technically avoidable.

---

# 31. ENVIRONMENT VARIABLES

Environment variables may be used for:

```text
initial secrets
deployment-specific infrastructure
secret manager references
```

but ordinary operational configuration should be manageable through the Admin Settings UI where appropriate.

Do NOT require users to edit `.env` merely to change:

```text
notification email
recipient
template
notification rule
```

---

# 32. MULTI-TENANT SAFETY

If the current UAIC application is tenant-aware, notification data must respect the same tenant/claim security model.

Never allow:

```text
Tenant A
```

to receive:

```text
Tenant B
```

claim information.

Recipient resolution must be permission-aware.

---

# 33. EMAIL CONTENT SECURITY

Sanitize dynamic HTML values.

Prevent:

```text
HTML injection
script injection
template injection
unsafe links
```

Do not render arbitrary user-provided HTML without sanitization.

---

# 34. LINK SECURITY

If email contains links back to the application:

- use the configured application base URL
- do not hardcode localhost
- support deployment environments
- use HTTPS in production
- never place secrets in URLs
- use signed/expiring tokens where secure actions are required

---

# 35. LOCAL DEVELOPMENT

The existing local email testing infrastructure should remain usable.

If MailDev or another local mail server already exists:

```text
Development → local mail provider
Production → configured production provider
```

Do not break existing development behavior.

Add a clear Settings indicator:

```text
Development Mail
Production Mail
```

where appropriate.

---

# 36. NO HARDCODED EMAIL ADDRESSES

Search the entire project for hardcoded email addresses.

Check:

```text
Python
TypeScript
JSON
YAML
.env.example
seed files
tests
Celery tasks
Guidewire integration
notification service
Power Platform migration code
```

Replace operational hardcoding with configuration where appropriate.

Test fixtures may contain fake addresses, but production behavior must not depend on them.

---

# 37. DATABASE DESIGN

Inspect the current database before adding models.

Prefer normalized/reusable models such as:

```text
EmailProvider
NotificationTemplate
NotificationRule
NotificationRecipient
Notification
NotificationDelivery
NotificationPreference
```

Do not duplicate email fields across dozens of unrelated tables.

If the existing schema already has suitable models, extend them instead of creating duplicates.

---

# 38. API DESIGN

Provide clean APIs for:

```text
GET    /settings/email
PUT    /settings/email

POST   /settings/email/test

GET    /notifications/templates
POST   /notifications/templates
GET    /notifications/templates/:id
PUT    /notifications/templates/:id
DELETE /notifications/templates/:id

GET    /notifications
GET    /notifications/:id

GET    /notifications/rules
PUT    /notifications/rules
```

Use the project's existing API conventions.

Do not introduce a second API architecture.

---

# 39. FRONTEND REQUIREMENTS

The Settings UI must use the existing global design system.

Do NOT create a visually different email settings page.

It must support:

- light mode
- dark mode
- responsive desktop
- tablet
- mobile
- existing navigation
- existing cards
- existing buttons
- existing form controls
- existing validation
- existing loading states
- existing toast/feedback mechanism

No horizontal overflow.

---

# 40. NOTIFICATION HISTORY UI

Provide a notification history view.

Columns should include:

```text
Date
Event
Claim
Recipient
Subject
Provider
Status
Retry Count
Sent At
```

Support:

```text
Search
Filter
Sort
Pagination
```

Allow opening a notification for details.

Do not expose credentials.

---

# 41. ERROR HANDLING

If email fails:

```text
Log failure
Persist notification status
Retry if allowed
Show operational status
Do not crash unrelated claim processing
```

If all retries fail:

```text
FAILED
```

and provide enough diagnostic information for administrators to troubleshoot.

---

# 42. OBSERVABILITY

Add correlation IDs across:

```text
Claim
Queue
Scraper
Fuzzy Match
Guidewire
Notification
Email Delivery
```

Example:

```text
Claim ID
Queue ID
Guidewire Activity ID
Notification ID
Correlation ID
```

This must make it possible to trace:

```text
Claim
 ↓
Scraping
 ↓
Fuzzy Match
 ↓
Guidewire
 ↓
Email
```

from logs and UI.

---

# 43. DO NOT BREAK EXISTING FUNCTIONALITY

This is an enhancement.

Do NOT remove or regress:

- 8 county scrapers
- Florida/Texas routing
- Miami-Dade Florida classification
- queue processing
- automatic queue
- manual queue
- attended mode
- Chrome automation
- Anti-Captcha integration
- fuzzy matching
- Guidewire integration
- claim processing
- settings
- dashboard
- telemetry
- exports
- status handling
- existing authentication
- existing UI
- existing responsive behavior

Email implementation must integrate with the existing architecture.

---

# 44. POWER PLATFORM PARITY REPORT

Before completing the task, create an internal implementation report containing:

### V4 Email Findings

```text
Found:
Not Found:
Unclear:
```

### Existing Application

```text
Already Implemented:
Partially Implemented:
Missing:
Incorrect:
```

### Implemented Changes

```text
Backend:
Database:
Celery:
Redis:
Settings:
Frontend:
Guidewire:
Notifications:
Email:
Tests:
```

### Legacy Mapping

```text
Power Platform
      ↓
New Application
```

For example:

```text
notification_email
      ↓
Notification Recipient Configuration
```

Only make this mapping if confirmed by the actual source.

---

# 45. IMPORTANT — IF V4 DOES NOT CONTAIN EMAIL

If the actual V4 workflow does NOT contain a specific email operation, do not falsely claim parity.

Instead:

1. Document that V4 does not contain the behavior.
2. Search related Power Platform flows/subflows/connectors.
3. Search Dataverse fields/environment variables.
4. Search the complete exported solution.
5. Determine whether email behavior exists elsewhere.
6. If still absent, implement the recommended dynamic notification architecture because it is valuable for the new system.

The implementation must clearly distinguish:

```text
LEGACY PARITY
```

from:

```text
NEW RECOMMENDED ENHANCEMENT
```

---

# 46. TESTING — DO NOT STOP AT COMPILE SUCCESS

Perform actual end-to-end testing.

### Test 1 — Email Provider

```text
Configure provider
↓
Save
↓
Reload settings
↓
Verify persisted
```

### Test 2 — Test Email

```text
Send Test Email
↓
Queue
↓
Worker
↓
Provider
↓
Delivery
↓
Notification Log
```

### Test 3 — Guidewire Success

```text
Claim
↓
Scrapers
↓
Fuzzy Match
↓
Guidewire
↓
ActivityID
↓
Notification Event
↓
Email Queue
↓
Email
```

### Test 4 — Guidewire Failure

Verify:

```text
Guidewire Failed
↓
Notification Created
↓
Retry
↓
Final Status
```

### Test 5 — Duplicate Prevention

Run the same successful event twice.

Expected:

```text
Only one successful notification
```

unless explicit resend is requested.

### Test 6 — Provider Failure

Simulate email provider failure.

Expected:

```text
Guidewire remains successful
Email becomes retrying/failed
```

### Test 7 — Configuration Change

Change recipient in Settings.

Trigger another notification.

Expected:

```text
New recipient receives notification.
```

No code change or restart should be required where technically avoidable.

### Test 8 — Disable Notification

Disable Guidewire email notification.

Trigger successful Guidewire operation.

Expected:

```text
Guidewire succeeds
No email sent
```

### Test 9 — Template Variables

Verify all supported variables render correctly.

### Test 10 — Security

Verify:

```text
No credentials exposed
No cross-tenant notification
No secret in logs
No unsafe HTML
```

---

# 47. PERFORMANCE REQUIREMENT

The email system must improve overall application responsiveness rather than make it slower.

Use:

```text
Celery
Redis
Asynchronous delivery
Connection pooling where appropriate
Template caching
Configuration caching with safe invalidation
Batch/digest support
Indexed notification queries
```

Do not repeatedly query the database for the same configuration during every email.

Do not load the entire notification history when displaying a page.

Use pagination.

---

# 48. FINAL USER EXPERIENCE

The administrator should be able to go to:

```text
Settings
 → Email & Notifications
```

and clearly see:

```text
Email Service
    Enabled / Disabled
    Provider
    Connection Status

Sender
    From Name
    From Email
    Reply-To

Recipients
    To
    CC
    BCC

Notification Rules
    Guidewire Success
    Guidewire Failure
    Scraper Failure
    Claim Failure
    etc.

Templates
    Guidewire Activity Created
    Guidewire Failure
    Scraper Failure
    etc.

Testing
    Test Email

Monitoring
    Sent
    Failed
    Pending
    Retrying
```

The user must NOT need to edit source code or `.env` just to change a notification email address.

---

# 49. IMPORTANT — DO NOT OVERENGINEER UNNECESSARILY

Build a reusable architecture, but do not introduce unnecessary microservices or external infrastructure.

Use the existing:

```text
FastAPI/backend
PostgreSQL/SQLAlchemy
Celery
Redis
existing settings
existing authentication
existing logging
```

where applicable.

Prefer a modular monolith with clear services over unnecessary distributed infrastructure.

---

# 50. FINAL DEFINITION OF DONE

This task is complete only when ALL of the following are true:

- Actual V4 Power Platform workflow has been inspected.
- All related Power Platform email behavior has been identified.
- `notification_email` behavior has been traced to its real source.
- Existing application email implementation has been audited.
- Missing email functionality has been implemented.
- Guidewire notification behavior works.
- Email provider can be configured from Settings.
- Recipient email can be configured dynamically.
- Multiple recipients are supported.
- Email templates are configurable.
- Dynamic variables work.
- Notification rules are configurable.
- Email is asynchronous.
- Celery/Redis integration works.
- Retry works.
- Idempotency works.
- Delivery logs work.
- Email failures do not incorrectly fail Guidewire/claim processing.
- Audit logging works.
- Security controls work.
- Multi-tenant isolation works where applicable.
- Test email works.
- Local development email continues working.
- Production configuration is supported.
- No production email address is hardcoded.
- No secrets are exposed.
- Existing functionality remains intact.
- Existing UI/design system remains intact.
- Settings remain the central source of truth.
- Actual end-to-end tests pass.
- Email delivery is verified, not merely simulated.
- No compile-only or mock-only implementation is accepted.

---

# FINAL RULE

Do not say:

> "Email functionality has been implemented"

unless you have actually verified the complete flow:

```text
CONFIGURATION
    ↓
EVENT
    ↓
NOTIFICATION
    ↓
CELERY QUEUE
    ↓
EMAIL WORKER
    ↓
PROVIDER
    ↓
DELIVERY
    ↓
DATABASE LOG
    ↓
UI STATUS
```

The goal is:

**POWER PLATFORM EMAIL PARITY + ENTERPRISE-GRADE DYNAMIC EMAIL/NOTIFICATION SYSTEM + ZERO REGRESSION.**

Preserve all existing functionality and enhance the application rather than replacing working behavior.