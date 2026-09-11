# Implementation Plan — Dynamic Email, Notification Engine & Acceptance Evidence

```text
========================================================================================
Implementation ID:   IMP-2026-0911-001
Project:             UAIC Claim & RPA Orchestrator
Module:              Notification Engine / Email Service / Admin Settings / Audit History
Feature / Issue:     05 - Dynamic Email, Notification Engine & Acceptance Evidence:
                     Power Platform V4 Parity, Centralized Asynchronous Delivery (Celery/Redis),
                     Dynamic Templates ({{claim_number}}, {{activity_id}}, etc.),
                     Granular Event Triggers, Idempotency Deduplication, Transactional
                     Decoupling from Guidewire, and Outbound Delivery History UI Verification.
Document Type:       Implementation Plan
Version:             v1.0
Status:              Approved
Created Date:        2026-09-11
Last Updated:        2026-09-11
AI Agent:            Antigravity (Gemini 3.8 Flash / Claude Sonnet 4.6 Thinking)
Approval Status:     Approved
Approved By:         User
Approval Date:       2026-09-11
Verification Status: Approved — In Execution
========================================================================================
```

---

## 1. Executive Summary & Problem Context

The user request specifies completing **Module 05: Dynamic Email, Notification Engine & Acceptance Evidence**:
1. **Power Platform Parity & Architecture**:
   - Trace legacy `notification_email` behavior in `UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A`.
   - Implement/verify centralized asynchronous email service using Celery (`"notifications"` queue) and Redis. Decouple from scraping and Guidewire request paths so email issues never fail claim processing.
2. **Configuration & Templates**:
   - Email configuration section in Admin Settings (`/settings` Email tab) supporting multiple providers (`local_mock`, `maildev`, `direct_mx`, `smtp`, `graph`, `ses`), sender fields (`From`, `To`, `CC`, `BCC`), and retry limits.
   - Mask passwords/API keys in logs and API, but provide a visible eye icon (`<Eye />` / `<EyeOff />`) in the UI.
   - Dynamic email templates supporting token substitution (`{{claim_number}}`, `{{activity_id}}`, `{{county}}`, etc.).
3. **Behavior, Idempotency, Delivery & Rules**:
   - Trigger notifications on specific events: `GUIDEWIRE_ACTIVITY_CREATED`, `GUIDEWIRE_ACTIVITY_FAILED`, `SCRAPER_FAILED`, `CLAIM_FAILED`, and `TEST_EMAIL`.
   - Idempotency keys to prevent duplicate email dispatch.
   - Transactional safety: email delivery failure must NOT mark underlying Guidewire claim processing as failed.
4. **Acceptance Evidence Required**:
   - **AE-005/006**: Email settings visible and recipients configurable without `.env` changes.
   - **AE-010/011**: Real test email delivered via UI trigger.
   - **AE-022/024**: Outbound Notification Delivery History populates correctly in DB and UI with queued, sent, and failed logs.

---

## 2. Current State & Forensic Inspection

### 2.1 Power Platform Legacy Inspection
- **Workflow Analyzed**: `PowerAutomateSolutions/BotCreation_1_0_0_7/Workflows/UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A.json`
- **Robin Desktop Binary**: In `customizations.xml`, V4 calls `Subflow_SendErrorNotification` upon browser crash/timeout.
- **Cloud Orchestration Flows**: `PA_FuzzyMatch_ActivityCreation_v1_Main` handles Guidewire push and alerts `notification_email` on failure.
- **Classification**:
  - `notification_email`: **LEGACY CONFIRMED** (Guidewire failure alert recipient) & **NEW ENHANCEMENT** (Expanded into a full multi-provider, dynamic templating notification engine).

### 2.2 Existing Implementation Audit
- **Backend Models (`backend/app/models/notification.py`)**:
  - `Notification`: Records `id`, `event_type`, `claim_id`, `recipient`, `cc`, `bcc`, `subject`, `body_html`, `body_text`, `provider`, `status` (`PENDING`, `QUEUED`, `SENDING`, `SENT`, `FAILED`, `RETRYING`, `SKIPPED`), `idempotency_key`, `delivery_receipt`, and timestamps.
  - `NotificationTemplate`: Database-stored template models with custom subject/HTML bodies.
  - `NotificationRule`: Per-event toggle configuration.
- **Backend Email Service (`backend/app/services/email_service.py`)**:
  - Implements `BaseEmailProvider`, `MockEmailProvider`, `MailDevEmailProvider` (localhost:1025/1080), `DirectMxEmailProvider` (port 25 STARTTLS), and `SmtpEmailProvider`.
  - Implements `TemplateRenderer` supporting token regex substitution (`{{token}}`) with fallback defaults.
- **Notification Service (`backend/app/services/notification_service.py`)**:
  - Master switch guard: When `email_notifications_enabled` is `False`, returns `None` immediately.
  - Rule guard: Checks per-event rule enablement.
  - Idempotency guard: Checks `idempotency_key` unique constraint; returns existing if already active/sent.
  - Asynchronous dispatch: Queues task to Celery `"notifications"` queue.
- **Decoupled Guidewire Hook (`backend/app/tasks/fuzzy_tasks.py`)**:
  - Success: Emits `GUIDEWIRE_ACTIVITY_CREATED` with idempotency key `GUIDEWIRE_ACTIVITY_CREATED:{claim.id}:{claim.activity_id}`. Wrapped in `try...except` so claim completion is never blocked.
  - Failure: Emits `GUIDEWIRE_ACTIVITY_FAILED`. Wrapped in `try...except`.
- **Admin Settings UI (`frontend/src/app/settings/page.tsx`)**:
  - Master toggle switch with real-time status banner.
  - Provider selector cards (`local_mock`, `maildev`, `direct_mx`, `smtp`).
  - Smtp password field with visible eye icon toggle (`showSmtpPassword` / `<Eye />` / `<EyeOff />`).
  - Dynamic recipient chip management (`To`, `CC`, `BCC`).
  - Granular event toggles and match notification strategy selector.
  - Interactive Test Email Console with instant dispatch button.
  - Dynamic Template Studio previewer.
  - Outbound Notification Delivery History table with status badges (`SENT`, `FAILED`, `QUEUED`, `SKIPPED`) and cryptographic Delivery Proof receipt modal.

---

## 3. Gap Analysis

| Requirement | Current Status | Identified Gap | Action in Plan |
|---|---|---|---|
| **V4 Parity & Trace** | Complete | Needs consolidated acceptance evidence document mapping V4 flow references | Document in acceptance evidence report |
| **Centralized Async Service** | Complete | Celery `"notifications"` queue operational; requires Redis container up for live broker | Verified: Redis container re-created with port 6379; 15/15 tests pass |
| **Settings UI & Eye Icon** | Complete | Eye icon present on line 3180 in `settings/page.tsx`; password never exposed in API/logs | Document and capture UI evidence |
| **Dynamic Templates** | Complete | `TemplateRenderer` supports all required tokens (`claim_number`, `activity_id`, etc.) | Verified across all 4 templates |
| **Idempotency & Decoupled Failure** | Complete | Handled in `NotificationService` and `fuzzy_tasks.py` | Validated in automated test suite |
| **Automated E2E Verification Script** | Minor Defect | `scripts/verify_email_system_e2e.py` used `priyer@test.com` for Direct MX (no MX record) and referenced `.error_message` instead of `.error` | Fix `scripts/verify_email_system_e2e.py` to use `damcogroup.com` for Direct MX and correct `.error` attribute |
| **Acceptance Evidence Artifacts** | Missing Doc | Comprehensive AE-001 to AE-034 report needed for Module 05 signoff | Create formal Acceptance Evidence Report in `implementation_plan/` |

---

## 4. Proposed Changes

### [MODIFY] `scripts/verify_email_system_e2e.py`
- Line 115: Use `priyer@damcogroup.com` for Direct MX step so real MX DNS resolution against `damcogroup-com.mail.protection.outlook.com` succeeds.
- Line 156: Change `mx_send_res.error_message` to `mx_send_res.error`.

### [NEW] `implementation_plan/2026-09-11_uaic_dynamic-email-and-notification-engine_acceptance-evidence_v1.md`
- Compile full acceptance evidence covering AE-001 through AE-034 with actual test results, database queries, Celery queue proofs, MailDev receipts, and API responses.

### [NEW] Visual Evidence Capture
- Capture UI screenshots of `/settings` Email tab showing:
  1. Master switch & provider configuration with password eye icon.
  2. Outbound Notification Delivery History table with queued, sent, and failed records.
  3. Delivery Proof modal with cryptographic RFC 3798 receipt.
- Store visual artifacts in `implementation_plan/Images/`.

---

## 5. Verification Plan

### 5.1 Automated Tests
```bash
# 1. Email notification test suite (15 tests)
cd backend && .venv\Scripts\pytest tests\test_email_notifications.py -v

# 2. Automated E2E verification script
.venv\Scripts\python scripts\verify_email_system_e2e.py

# 3. Linter & Type checking
.venv\Scripts\ruff check app tests
cd ..\frontend && npx tsc --noEmit
```

### 5.2 Browser & UI Verification
- Use `browser_subagent` to navigate to `http://localhost:3000/settings`, switch to the **Email & Notifications** tab, trigger test email, open delivery history, inspect proof modal, and capture full visual evidence.

---

## 6. User Review Required

> [!IMPORTANT]
> **No source code has been modified yet.**
> All 15 unit tests in `tests/test_email_notifications.py` are passing.
> The proposed work will:
> 1. Correct two minor script bugs in `scripts/verify_email_system_e2e.py` (target domain for MX and attribute name).
> 2. Run the end-to-end verification script and browser visual tests.
> 3. Generate the formal Acceptance Evidence report for Module 05.
>
> Please confirm if you approve this plan to proceed with execution.
