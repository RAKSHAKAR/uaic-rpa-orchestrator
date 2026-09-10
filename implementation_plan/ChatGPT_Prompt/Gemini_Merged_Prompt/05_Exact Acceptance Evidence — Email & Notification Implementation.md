# EXACT ACCEPTANCE EVIDENCE — EMAIL & NOTIFICATION SYSTEM

The implementation is **NOT accepted** based on source-code changes, successful compilation, unit tests alone, or a UI screenshot.

Every requirement below must have **verifiable evidence**.

For every acceptance item, provide:

1. **Evidence ID**
2. **Requirement**
3. **Implementation location**
4. **Test performed**
5. **Actual result**
6. **Expected result**
7. **PASS / FAIL**
8. **Evidence artifact** such as:
   - screenshot
   - API response
   - database record
   - application log
   - Celery task log
   - Redis/queue evidence
   - actual received email
   - test report
   - exported JSON/CSV
   - Power Platform source reference

Do not use statements such as "verified", "working", or "implemented" without evidence.

---

# A. POWER PLATFORM V4 SOURCE EVIDENCE

## AE-001 — V4 Workflow Identification

Provide evidence showing that the actual latest Power Platform workflow inspected is:

```text
UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A
```

Evidence must include:

- exact workflow name
- workflow ID if available
- export/file location
- version/date if available

**PASS requires actual V4 evidence.**

Do not substitute V2/V3.

---

## AE-002 — Complete Email Search

Provide search evidence showing the V4 export and related flows were searched for:

```text
notification_email
email
Send email
send an email
recipient
To
CC
BCC
subject
body
Outlook
Office 365
SMTP
Graph
notification
Guidewire
ActivityID
```

Evidence must identify:

```text
File / Flow
Location
Matched term
Relevant action/variable
```

---

## AE-003 — notification_email Trace

Provide a complete trace:

```text
notification_email
       ↓
SOURCE
       ↓
TRANSFORMATION
       ↓
CONSUMER
       ↓
EMAIL ACTION
       ↓
RECIPIENT
```

If `notification_email` does not exist in V4, provide explicit evidence that:

- V4 was searched
- related child flows were searched
- environment/configuration values were searched
- Dataverse fields were searched
- connectors/actions were searched

Then classify it as:

```text
LEGACY CONFIRMED
LEGACY NOT FOUND
LEGACY UNCERTAIN
NEW ENHANCEMENT
```

No unsupported assumption is acceptable.

---

# B. CURRENT APPLICATION EVIDENCE

## AE-004 — Existing Email Architecture Audit

Provide a list of all existing email/notification components:

```text
Backend files
Frontend files
Database models
API endpoints
Celery tasks
Redis queues
Settings
Environment variables
Notification services
Guidewire integration
```

For each, state:

```text
Existing
Partial
Missing
Incorrect
Replaced/duplicated
```

---

# C. SETTINGS ACCEPTANCE

## AE-005 — Email Settings Visible

Open the application and navigate to:

```text
Settings → Email & Notifications
```

Provide a screenshot showing the actual UI.

It must visibly contain, where applicable:

```text
Email Enabled
Provider
Provider Status
From Name
From Email
Reply-To
Recipients
To
CC
BCC
Notification Rules
Templates
Test Email
```

---

## AE-006 — Recipient Configuration

Change the configured notification recipient from:

```text
test1@example.com
```

to:

```text
test2@example.com
```

using the UI.

Save.

Reload the page.

Evidence must prove:

```text
Saved value = test2@example.com
```

No source-code modification or `.env` modification is allowed for this test.

---

## AE-007 — Multiple Recipients

Configure:

```text
To:
test1@example.com
test2@example.com

CC:
test3@example.com

BCC:
test4@example.com
```

Evidence must prove all recipients were persisted correctly.

---

# D. EMAIL PROVIDER EVIDENCE

## AE-008 — Provider Configuration

Configure the supported email provider.

Evidence must show:

```text
Provider configured
Configuration saved
Provider status
```

Passwords/API keys must be masked.

---

## AE-009 — Provider Secrets Security

Provide evidence that:

- password/API key is not returned by GET settings API
- password/API key is not rendered in frontend HTML
- password/API key does not appear in normal application logs
- password/API key does not appear in audit logs

Expected:

```text
secret = NEVER EXPOSED
```

---

# E. TEST EMAIL — REAL DELIVERY

## AE-010 — Test Email

Use:

```text
Settings → Email & Notifications → Send Test Email
```

Do NOT mock the email provider.

Evidence must show the complete chain:

```text
UI
 ↓
API
 ↓
Notification record
 ↓
Celery task
 ↓
Email provider
 ↓
Delivered email
```

Provide:

1. UI screenshot
2. API/log evidence
3. Celery task evidence
4. notification database record
5. actual received email screenshot

---

## AE-011 — Actual Email Content

The received email must be opened and verified.

Evidence must show:

```text
From
To
Subject
Body
```

and confirm that:

- sender is correct
- recipient is correct
- template rendered
- no unresolved `{{variable}}` remains
- HTML renders correctly if HTML email is enabled

---

# F. TEMPLATE ACCEPTANCE

## AE-012 — Template CRUD

Create a test template.

Verify:

```text
Create
Save
Reload
Edit
Save
Disable
Re-enable
```

Evidence must show every operation succeeded.

---

## AE-013 — Dynamic Variables

Create a template containing at least:

```text
{{claim_number}}
{{exposure_number}}
{{activity_id}}
{{case_number}}
{{case_style}}
{{county}}
{{suit_filed_date}}
```

Trigger a real notification.

The received email must contain the actual values.

Evidence must show:

```text
Template value
Actual event value
Received email value
```

---

## AE-014 — Invalid Variable

Create a template with an invalid variable such as:

```text
{{does_not_exist}}
```

Expected behavior must be defined and verified.

The system must NOT silently send a broken production email.

Evidence must show the validation/error behavior.

---

# G. GUIDEWIRE ACCEPTANCE

## AE-015 — Successful Guidewire Notification

Execute a real/testable successful Guidewire case-update flow.

Evidence must show:

```text
Claim
 ↓
Fuzzy Match
 ↓
Guidewire request
 ↓
Guidewire success
 ↓
ActivityID returned
 ↓
Notification event created
 ↓
Celery task queued
 ↓
Email sent
```

Provide correlation IDs where available.

---

## AE-016 — Guidewire Email Content

The received Guidewire email must contain the expected information from the legacy Power Platform behavior.

At minimum verify the fields actually used by V4.

Potential fields include:

```text
Claim Number
Exposure Number
Activity ID
Case Number
Case Style
County
Suit Filed Date
```

Do NOT claim fields are legacy behavior unless confirmed from V4.

---

## AE-017 — Guidewire Failure

Force/simulate a Guidewire failure in a controlled test environment.

Expected:

```text
Guidewire = FAILED
Notification = CREATED
Email = QUEUED/RETRYING/FAILED
```

Evidence must prove that the notification was generated.

---

## AE-018 — Email Failure Does Not Fail Guidewire

Simulate an email-provider failure after successful Guidewire processing.

Expected:

```text
Guidewire = SUCCESS
ActivityID = PRESENT
Email = FAILED/RETRYING
Claim processing = SUCCESS
```

This is a mandatory acceptance test.

---

# H. CELERY / REDIS EVIDENCE

## AE-019 — Asynchronous Email

Prove that email is not executed synchronously inside the critical Guidewire request.

Evidence must show:

```text
Notification created
       ↓
Celery task queued
       ↓
Worker received task
       ↓
Worker delivered email
```

Provide worker log evidence.

---

## AE-020 — Retry

Force an email delivery failure.

Verify:

```text
Attempt 1
Attempt 2
...
Final attempt
```

Evidence must show actual retry count.

Do not accept a configuration value alone as evidence.

---

# I. IDEMPOTENCY EVIDENCE

## AE-021 — Duplicate Event

Trigger the same Guidewire notification event twice using the same:

```text
Claim ID
Activity ID
Event Type
```

Expected:

```text
ONE successful email
```

Evidence must show:

```text
Event 1 → SENT
Event 2 → DUPLICATE/SKIPPED
```

No duplicate email may be delivered.

---

# J. NOTIFICATION DATABASE EVIDENCE

## AE-022 — Notification Record

After a successful email, query the database.

Provide the actual record showing:

```text
Notification ID
Event Type
Claim ID
Recipient
Subject
Provider
Status
Queued At
Sent At
Retry Count
Provider Message ID
```

Secrets must not appear.

---

## AE-023 — Failed Notification Record

After a controlled failure, database evidence must show:

```text
Status = FAILED
or
Status = RETRYING
```

with useful error information.

---

# K. NOTIFICATION HISTORY UI

## AE-024 — Notification History

Open the notification history UI.

Evidence must show:

```text
Date
Event
Claim
Recipient
Subject
Provider
Status
Retry Count
```

Verify:

```text
Search
Filter
Sort
Pagination
```

actually work.

---

# L. NOTIFICATION RULES

## AE-025 — Disable Guidewire Email

Disable:

```text
Guidewire Activity Created
```

Trigger successful Guidewire processing.

Expected:

```text
Guidewire = SUCCESS
Email = NOT SENT
```

Evidence must prove no email delivery occurred.

---

## AE-026 — Re-enable Guidewire Email

Re-enable the rule.

Trigger another successful event.

Expected:

```text
Email = SENT
```

---

## AE-027 — Failure Notification Rule

Enable:

```text
Guidewire Failed
```

Trigger controlled Guidewire failure.

Expected:

```text
Failure event
 ↓
Notification
 ↓
Email
```

---

# M. CONFIGURATION HOT-RELOAD EVIDENCE

## AE-028 — Recipient Change Without Code Change

Change:

```text
Recipient A
```

to:

```text
Recipient B
```

through Settings.

Do NOT restart the frontend/backend unless technically unavoidable and explicitly documented.

Trigger an event.

Expected:

```text
Recipient B receives email.
Recipient A does not.
```

Evidence must prove this.

---

# N. SECURITY EVIDENCE

## AE-029 — Log Security

Search application logs for:

```text
password
smtp_password
api_key
token
secret
authorization
```

Verify secrets are not exposed.

---

## AE-030 — API Security

Call the email-settings GET endpoint.

Evidence must show that secret fields are:

```text
masked
omitted
or represented safely
```

---

# O. RESPONSIVE UI EVIDENCE

## AE-031 — Desktop

Provide screenshot at:

```text
1920 × 1080
```

---

## AE-032 — Tablet

Provide screenshot around:

```text
768 × 1024
```

---

## AE-033 — Mobile

Provide screenshot around:

```text
390 × 844
```

Verify:

- no horizontal overflow
- all email settings usable
- buttons accessible
- forms usable
- tables transform appropriately
- navigation remains functional

---

# P. END-TO-END CORRELATION EVIDENCE

## AE-034 — Complete Trace

For one real/test claim, provide a correlation trace:

```text
Claim ID
 ↓
Queue ID
 ↓
Scraper execution
 ↓
Fuzzy Match
 ↓
Guidewire ActivityID
 ↓
Notification ID
 ↓
Celery Task ID
 ↓
Provider Message ID
 ↓
Email Delivery
```

All available identifiers should be connected.

This is one of the most important acceptance artifacts.

---

# Q. POWER PLATFORM PARITY REPORT

## AE-035 — Legacy vs New Matrix

Provide a final table:

| Behavior | Power Platform V4 | New Application | Evidence |
|---|---|---|---|
| notification_email | | | |
| Recipient | | | |
| CC | | | |
| BCC | | | |
| Subject | | | |
| Body | | | |
| Dynamic variables | | | |
| Guidewire success email | | | |
| Guidewire failure email | | | |
| Retry | | | |
| Failure handling | | | |
| Audit | | | |

Every row must have evidence.

---

# R. NEW ENHANCEMENT REPORT

## AE-036 — Clearly Separate New Features

Any functionality NOT found in Power Platform but intentionally added must be listed separately:

```text
NEW ENHANCEMENT
```

Examples:

```text
Dynamic templates
Notification rules
Multiple recipients
Idempotency
Delivery history
Provider abstraction
Digest mode
Health monitoring
```

For each:

```text
Why added
Benefit
Where implemented
How tested
```

Do not describe new functionality as "Power Platform parity."

---

# S. REGRESSION EVIDENCE

## AE-037 — Existing Functionality

After email implementation, verify that these still work:

```text
Claim creation
Claim edit
Queue
Automatic queue
Manual queue
8 county scrapers
Florida routing
Texas routing
Cross-state routing
Fuzzy matching
Guidewire
Telemetry
Dashboard
Settings
Exports
Authentication
Responsive navigation
```

No email implementation may regress these features.

---

# T. AUTOMATED TEST EVIDENCE

## AE-038 — Test Suite

Provide actual test output.

Must include:

```text
Unit tests
Integration tests
API tests
Notification tests
Email-service tests
Celery task tests
Idempotency tests
Template tests
```

Show:

```text
TOTAL
PASSED
FAILED
SKIPPED
```

Do not report only:

```text
npm run build = success
```

or:

```text
pytest = success
```

without demonstrating the relevant tests exist.

---

# U. REAL ARTIFACT REQUIREMENT

The final implementation report must include links/paths to actual generated evidence artifacts where supported:

```text
email_test_report
notification_delivery_report
powerplatform_parity_report
database_validation_report
celery_email_test_log
api_test_results
screenshots
```

If an artifact cannot be generated, explicitly state why.

Never fabricate evidence.

---

# V. FINAL ACCEPTANCE GATE

The feature is accepted ONLY if all mandatory items pass:

```text
AE-001
AE-002
AE-003
AE-005
AE-006
AE-010
AE-011
AE-012
AE-013
AE-015
AE-018
AE-019
AE-020
AE-021
AE-022
AE-024
AE-025
AE-028
AE-029
AE-034
AE-035
AE-036
AE-037
AE-038
```

Any mandatory item marked:

```text
FAIL
UNKNOWN
NOT TESTED
CANNOT VERIFY
```

means:

# NOT ACCEPTED

---

# FINAL REPORT FORMAT

End the implementation with this exact summary:

```text
EMAIL / NOTIFICATION ACCEPTANCE

Power Platform V4 inspected: PASS / FAIL
notification_email traced: PASS / FAIL / NOT FOUND
Legacy email behavior reproduced: PASS / FAIL / N/A
Dynamic recipient configuration: PASS / FAIL
Email provider configuration: PASS / FAIL
Real test email delivered: PASS / FAIL
Dynamic templates: PASS / FAIL
Guidewire success notification: PASS / FAIL
Guidewire failure notification: PASS / FAIL
Email failure isolation: PASS / FAIL
Celery asynchronous delivery: PASS / FAIL
Retry: PASS / FAIL
Idempotency: PASS / FAIL
Notification persistence: PASS / FAIL
Notification history UI: PASS / FAIL
Notification rules: PASS / FAIL
Security: PASS / FAIL
Responsive UI: PASS / FAIL
Regression testing: PASS / FAIL

TOTAL MANDATORY ACCEPTANCE ITEMS:
PASSED:
FAILED:
NOT TESTED:

FINAL STATUS:
ACCEPTED / NOT ACCEPTED
```

Do not mark `ACCEPTED` unless every mandatory acceptance item has concrete evidence.