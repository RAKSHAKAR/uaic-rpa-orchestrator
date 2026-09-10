# 05 - DYNAMIC EMAIL, NOTIFICATION ENGINE & ACCEPTANCE EVIDENCE

## 1. POWER PLATFORM PARITY & ARCHITECTURE
- Inspect `UAICBotCreationMainFlow-V4...` and trace the legacy `notification_email` behavior. Reproduce this exact behavior.
- Implement a centralized, asynchronous email service using Celery and Redis. Do NOT send emails synchronously within critical Guidewire or scraping request paths

## 2. CONFIGURATION & TEMPLATES
- Add an Email Configuration section to the Admin Settings (SMTP/Graph/SES, From, To, CC, BCC, Retry limits). NEVER expose passwords/API keys in the logs but must show in UI with visible eye icon.
- Support dynamic email templates with variable substitution (e.g., `{{claim_number}}`, `{{activity_id}}`, `{{county}}`).

## 3. BEHAVIOR, IDEMPOTENCY, DELIVERY, IDEMPOTENCY & RULES
- Trigger notifications on specific events like `GUIDEWIRE_ACTIVITY_CREATED` and `GUIDEWIRE_ACTIVITY_FAILED`.
- Implement idempotency keys to prevent duplicate emails.
- **Transactional Safety:** An email delivery failure must NOT mark the underlying Guidewire claim processing as failed.

## 4. ACCEPTANCE EVIDENCE REQUIRED
Before declaring completion, verify and generate evidence for:
- AE-005/006: Email settings visible and recipients configurable without `.env` changes.
- AE-010/011: Real test email delivered via UI trigger.
- AE-022/024: Outbound Notification Delivery History populates correctly in the DB and UI.
- Ensure the "Outbound Notification Delivery History" UI correctly displays queued, sent, and failed logs.


Supporting Docs you can ref:
    1) Complete Power Platform Email & Notification Implementation Prompt.md
    2) Exact Acceptance Evidence — Email & Notification Implementation.md
Note: Most of them are already implemented, test before making any changes.