# Enterprise Email & Notifications Engine Operator Manual

> **Authoritative Technical Guide for UAIC RPA Event Notifications & Email Transport**  
> Covers Multi-Provider Architecture, SMTP/Graph/SES/MailDev Transports, Dynamic Template Studio, Idempotent Dispatches, and Power Platform Parity.

---

## 1. Executive Summary & Architectural Overview

The UAIC Notification Engine provides enterprise-grade event notifications for the claims RPA pipeline. It replicates and enhances the alert mechanisms originally handled by the legacy Power Automate Cloud Flow (`UAICBotCreationMainFlow-V4`), delivering real-time alerts to claims adjusters and RPA engineers.

```
+-------------------------------------------------------------------------------+
|                           Core Claim Processing Pipeline                      |
|                                                                               |
|   +-------------------+     +--------------------+     +------------------+   |
|   | Claim Ingestion / | --> | Scraper Execution/ | --> | Guidewire Cloud  |   |
|   | Retry Event       |     | RapidFuzz Match    |     | Activity Push    |   |
|   +-------------------+     +--------------------+     +------------------+   |
+---------------------------------------|---------------------------------------+
                                        | (Non-Blocking Celery Task Emit)
                                        v
+-------------------------------------------------------------------------------+
|                     Dedicated "notifications" Celery Queue                    |
|                                                                               |
|   +-----------------------------------------------------------------------+   |
|   | 1. Master Toggle Check (email_notifications_enabled)                  |   |
|   | 2. Event Rule Matrix (NotificationRule: is_enabled)                   |   |
|   | 3. Idempotency Key Verification (Strict Deduplication)                |   |
|   | 4. Template Interpolation & HTML Rendering (NotificationTemplate)     |   |
|   +-----------------------------------------------------------------------+   |
+---------------------------------------|---------------------------------------+
                                        | (Standardized Provider Interface)
                                        v
+-------------------------------------------------------------------------------+
|                      Multi-Provider Email Transports                          |
|                                                                               |
|   * Authenticated SMTP (SSL/TLS :465, STARTTLS :587)                          |
|   * Corporate Direct MX (DNS MX Resolution :25)                               |
|   * Microsoft Graph API (Azure AD OAuth2 App-Only)                            |
|   * Amazon SES API (AWS Cloud SDK / boto3)                                    |
|   * Local MailDev Webbox (Dev Inspector :1080, SMTP :1025)                    |
|   * Local Mock Sandbox (Air-Gapped In-Memory Testing)                         |
+-------------------------------------------------------------------------------+
```

---

## 2. The 6 Email Transport Providers

The system provides a pluggable transport layer via `BaseEmailProvider` in [`backend/app/services/email_service.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/email_service.py):

| Provider Key | Transport Type | Ports / Protocol | Authentication | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| **`smtp`** | Authenticated SMTP | 465 (SSL/TLS), 587/25 (STARTTLS) | Username + Password | Corporate mail relays, SendGrid, Mailgun |
| **`direct_mx`** | Direct MX Delivery | 25 (TCP direct) | None (SPF/DKIM/DNS) | Internal corporate intranets without SMTP auth |
| **`graph`** | Microsoft Graph API | 443 (HTTPS REST) | Azure AD OAuth2 Client Credentials | Office 365, Exchange Online enterprise tenants |
| **`ses`** | Amazon SES API | 443 (HTTPS SDK) | AWS Access Key + Secret Key | High-volume AWS cloud infrastructure |
| **`maildev`** | Local MailDev | 1025 (SMTP), 1080 (Web UI) | None | Local dev testing, visual email inspection |
| **`local_mock`** | Local Mock Sandbox | In-Memory (No Socket) | None | Air-gapped testing, automated Pytest CI/CD |

---

## 3. Master Toggle & Event Rule Matrix

### Master ON/OFF Switch
- **Setting Key**: `email_notifications_enabled` (Persisted in DB `SystemSettings`).
- **Behavior**: When toggled `FALSE`, all automated email dispatches are immediately muted with zero database write or Celery queue overhead.

### Granular Event Triggers
Each operational event has an independent toggle in `notification_rules`:

| Event Identifier | Trigger Condition | Default Recipients | Priority |
| :--- | :--- | :--- | :--- |
| **`GUIDEWIRE_ACTIVITY_CREATED`** | Outbound court docket successfully pushed to Guidewire ClaimCenter (HTTP 200/201). | Claims Adjusters, Operations | Normal |
| **`GUIDEWIRE_ACTIVITY_FAILED`** | Guidewire Cloud rejected claim update or timed out. | RPA Support, Tech Lead | **High** |
| **`COURT_CASE_MATCHED`** | Scraped docket evaluated above the auto-match similarity threshold. | Claims Examiner | Normal |
| **`SCRAPER_FAILED`** | Court portal exceeded CAPTCHA retry limit or blocked IP. | RPA DevOps Team | **High** |
| **`CLAIM_PROCESSING_FAILED`** | Full claim workflow failed across all assigned portals. | Engineering On-Call | **Urgent** |

---

## 4. Strict Idempotency & Fault Isolation

1. **Deterministic Idempotency Key**:
   ```python
   idempotency_key = f"{claim_id}_{event_type}_{activity_id or match_id}"
   ```
   If a Celery task retries or an operator re-triggers a failed claim, the database rejects duplicate `Notification` inserts with unique key collisions, ensuring recipients never receive duplicate emails.
2. **Transactional Pipeline Isolation**:
   Notification dispatch failures are strictly isolated within `notification_tasks.py`. An email failure (e.g., SMTP timeout) will **never** fail or interrupt the underlying court scraping or Guidewire claim execution.

---

## 5. Dynamic HTML Template Studio

The orchestrator includes responsive, dark-mode safe HTML templates managed via `/notifications`:

### Dynamic Placeholders

| Token | Description | Example Value |
| :--- | :--- | :--- |
| `{{claim_number}}` | 9- or 10-digit claim number | `100290914` |
| `{{activity_id}}` | Guidewire generated activity ID | `ACT-2026-90914` |
| `{{county}}` | County court jurisdiction | `Broward County (FL)` |
| `{{case_number}}` | Scraped Uniform Case Number | `COCE-22-014522` |
| `{{case_style}}` | Plaintiff vs Defendant docket title | `DOE VS PROGRESSIVE` |
| `{{suit_filed_date}}` | Date lawsuit was filed | `02/27/2022` |
| `{{error_message}}` | System diagnostic failure message | `CAPTCHA solver timeout` |
| `{{system_url}}` | Deep link to claim dossier | `http://localhost:3000/claims/:id` |

### Variable Token Validation
The template engine rigorously validates placeholder syntax before saving:
- Valid syntax: `{{variable_name}}`
- Malformed syntax (e.g. `{variable}` or `{{invalid token}}`) is rejected with **HTTP 400 Bad Request** to prevent broken production emails.

---

## 6. Operator Testing & Reachability Probes

1. **Test Provider Connection & Latency**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/settings/email/test-connection" \
     -H "Content-Type: application/json" \
     -d '{"provider": "smtp"}'
   ```
   *Returns handshake latency in milliseconds, TLS status, and server banner response.*

2. **Send Interactive Live Test Email**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/settings/email/test-send" \
     -H "Content-Type: application/json" \
     -d '{
       "recipient": "adjuster@uaic.com",
       "subject": "Test RPA Notification",
       "body_html": "<p>This is a live test from UAIC Orchestrator.</p>"
     }'
   ```

3. **Inspect Delivery History Log**:
   Query `GET /api/v1/notifications` or navigate to `/notifications` on the web console to view status badges (`SENT`, `FAILED`, `QUEUED`), duration latency, recipient arrays, and RFC-compliant delivery receipts.
