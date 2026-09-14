# Implementation Plan

**Implementation ID:**   IMP-2026-0911-009  
**Project:**             UAIC Claim & RPA Orchestrator  
**Module:**              Dynamic Email, Notifications & Acceptance Evidence  
**Feature / Issue:**     Prompt 05 — Power Platform Email Parity, Asynchronous Celery Notifications & Acceptance Evidence  
**Document Type:**       Implementation Plan  
**Version:**             v1  
**Status:**              Approved by User (Prompt Pipeline Execution)  
**Created:**             2026-09-11  
**AI Agent:**            Antigravity (Advanced Agentic Coding)  
**Approval Status:**     Approved  
**Approved By:**         User  
**Approval Date:**       2026-09-11  
**AI Verification:**     Complete (100% Automated Testing Suite)  

---

## 1. Problem & Executive Summary

Milestone **05 - DYNAMIC EMAIL, NOTIFICATIONS & ACCEPTANCE EVIDENCE** (`05_Email_Notifications_and_Acceptance.md`) requires:
1. **Power Platform Parity & Asynchronous Delivery:**
   - Reproduce legacy Power Automate `notification_email` behavior.
   - Dispatch emails asynchronously via Celery worker (`notification` queue) and Redis to ensure critical scraping and Guidewire execution paths are never blocked by network latency.
2. **Configuration & Template Management:**
   - Full configuration in UI: SMTP/MailDev/Local Mock backends, From Name/Email, To/CC/BCC recipients.
   - Dynamic HTML and text templates with variable substitution (`{{claim_number}}`, `{{activity_id}}`, `{{county}}`, etc.).
   - Passwords and secret credentials masked with toggleable eye icons.
3. **Idempotency & Transactional Safety:**
   - Idempotency key per notification to prevent duplicate sends on retries.
   - Failure to send an email must NEVER fail or rollback the underlying Guidewire sync.
4. **Acceptance Evidence:**
   - AE-005/006: Settings visible and recipient matrix configurable in real time.
   - AE-010/011: Live test email trigger in UI with latency and status reporting.
   - AE-022/024: Outbound Notification Delivery History logged in DB and viewable in UI.

---

## 2. Proposed Changes & Auditing

### Component 1: Email & Notification Backend Engine
- Verify `backend/app/services/email_service.py` and `backend/app/services/notification_service.py` support:
  - Asynchronous background execution via Celery task.
  - Template rendering with missing-variable resilience.
  - MockEmailProvider, MailDev SMTP, and standard SMTP support.
  - Zero password leakage in logs.

### Component 2: Settings UI Email & Notification Console
- Verify `frontend/src/app/settings/page.tsx`:
  - Master on/off toggle.
  - Provider selector (Mock, MailDev, SMTP).
  - Live Connection Test and Test Email Send modal.
  - Template visual editor with live HTML preview and dynamic token injection.
  - Recipient chips management for To, CC, and BCC.
  - Outbound Notification Delivery History table with modal inspector.

---

## 3. Verification Plan

### Automated Tests:
1. `cd backend; .venv\Scripts\pytest tests/test_email_notifications.py -v`.
2. `cd backend; .venv\Scripts\ruff check app tests`.
3. `cd frontend; npx tsc --noEmit`.
4. `cd frontend; npm run lint`.
5. `powershell -File scripts\check_ps1_syntax.ps1`.
