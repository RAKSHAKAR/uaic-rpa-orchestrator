# IMP-2026-0905-006: MailDev Local Email Tracking & Web Inspector Integration

> **Implementation ID:** `IMP-2026-0905-006`  
> **Status:** `PROPOSED (Awaiting User Confirmation)`  
> **Target Date:** 2026-09-05  
> **Author:** Antigravity AI Orchestrator  
> **Scope:** `docker-compose.yml`, `setup_local.ps1`, `backend/app/services/email_service.py`, `backend/app/schemas/settings.py`, `frontend/src/app/settings/page.tsx`, `frontend/src/types/index.ts`, `backend/tests/test_email_notifications.py`, `scripts/verify_email_system_e2e.py`

---

## 1. Executive Summary & Objective

The user requested:
> *"while we running this locally we can see those emails in maildev, so pls configure the maildev for locally to see and track the emails"*

This plan integrates **MailDev** as a first-class local email development, tracking, and visual inspection environment across the entire UAIC Orchestrator stack. MailDev provides a local zero-configuration SMTP server listening on port `1025` and an interactive browser-based web console listening on port `1080` (`http://localhost:1080`).

Whenever any email notification is triggered locally (automated claim activity alerts, scraper failures, or test email dispatches), developers and operators can inspect the rendered HTML, attachments, headers, and transmission receipts directly in the MailDev web UI in real-time.

---

## 2. Architectural Design

```
+----------------------------------------------------------------------------------------------------+
|                                    LOCAL DEVELOPMENT STACK                                         |
|                                                                                                    |
|  [FastAPI / Celery Worker]                                                                         |
|            |                                                                                       |
|            | (SMTP Port 1025, No Auth, Cleartext/TLS optional)                                     |
|            v                                                                                       |
|  [MailDev Server (uaic_maildev Docker / npx)] <------------------------------------+               |
|            |                                                                       |               |
|            | (Web UI Port 1080)                                                    |               |
|            v                                                                       |               |
|  [MailDev Web Inspector: http://localhost:1080]                                    |               |
|    - Live visual HTML email preview                                                |               |
|    - RFC 3798 & RFC 822 header inspection                                          |               |
|    - Instant search & raw MIME source                                              |               |
|                                                                                    |               |
|  [Settings Page: http://localhost:3000/settings] ----------------------------------+               |
|    - Provider Card: "MailDev Local Webbox" (SMTP:1025 / Web:1080)                  |               |
|    - "Open MailDev Webbox (http://localhost:1080)" One-Click Action                |               |
|    - Delivery Receipt Modal links directly to MailDev Web Inspector                |               |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Proposed Changes Grouped by Component

### Component A: Local Infrastructure & Orchestration Launchers

#### [MODIFY] [docker-compose.yml](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docker-compose.yml)
- Add `maildev` service definition using official `maildev/maildev:latest`:
  ```yaml
  maildev:
    image: maildev/maildev:latest
    container_name: uaic_maildev
    ports:
      - "1080:1080" # Web Inspector UI
      - "1025:1025" # SMTP Server
    restart: unless-stopped
  ```
- Expose ports `1080` and `1025` to host machine.

#### [MODIFY] [setup_local.ps1](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/setup_local.ps1)
- Add `Start-MailDevService` function:
  - Checks if port 1080/1025 is already listening.
  - If Docker is running, launches or starts `uaic_maildev` container (`docker start uaic_maildev` or `docker run -d --name uaic_maildev -p 1080:1080 -p 1025:1025 maildev/maildev:latest`).
  - If Docker is not running or fails, falls back gracefully to `Start-Process npx -ArgumentList "maildev --smtp 1025 --web 1080"`.
- Update `Invoke-KillAllServices` to release ports `1080` and `1025` and stop `uaic_maildev`.
- Update interactive console banner to display:
  `MailDev Webbox:  http://localhost:1080 (SMTP: 1025)`
- Add interactive menu option:
  `[M] Open / Launch MailDev Web Inspector (http://localhost:1080)`
- Include MailDev startup in `Invoke-StartAllServices`.

---

### Component B: Backend Email Engine & Settings Persistence

#### [MODIFY] [backend/app/schemas/settings.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/settings.py)
- Update `EmailSettings.provider` to include `"maildev"`.
- Add `maildev_web_url: str = Field(default="http://localhost:1080", description="URL for local MailDev web interface")`.

#### [MODIFY] [backend/app/services/email_service.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/email_service.py)
- Implement `MailDevEmailProvider(BaseEmailProvider)`:
  - Uses `smtp_host="localhost"` (or `os.getenv("MAILDEV_HOST", "localhost")`), `smtp_port=1025`, `encryption="none"`.
  - Sends email via RFC-5321 cleartext SMTP on port 1025 without authentication.
  - Emits RFC 3798 / RFC 822 receipt headers.
  - Returns `delivery_receipt` populated with:
    - `provider: "maildev"`
    - `gateway_host: "localhost:1025"`
    - `webbox_url: "http://localhost:1080"`
    - `server_response: "250 2.0.0 OK: message queued in MailDev"`
    - `message_id`
    - `duration_ms`
- In `get_email_provider`:
  - When `override_provider == "maildev"` or `settings.email.provider == "maildev"`, return an instance of `MailDevEmailProvider`.
- In `test_connection`:
  - Verify socket connection to `localhost:1025` and confirm MailDev SMTP banner.

---

### Component C: Frontend UI & Operator Dashboard

#### [MODIFY] [frontend/src/types/index.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/types/index.ts)
- Update `EmailSettings.provider` type union:
  `provider: "local_mock" | "maildev" | "direct_mx" | "smtp" | "graph" | "sendgrid" | "ses" | string;`
- Add `maildev_web_url?: string;` to `EmailSettings`.

#### [MODIFY] [frontend/src/app/settings/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)
- Add a dedicated **MailDev Local Sandbox & Visual Inspector** provider card:
  - Icon: `Inbox` / `Monitor`
  - Badges: `SMTP: 1025` • `Web: 1080` • `Local Dev`
  - Description: "Dispatches emails to local MailDev SMTP server on port 1025. All outgoing emails are captured with full HTML rendering and attachment inspection at http://localhost:1080."
  - Action button: **"Open MailDev Webbox (http://localhost:1080)"** with `ExternalLink` icon (opens in new tab).
  - Quick action: "Apply MailDev Defaults" sets host to `localhost`, port to `1025`, encryption to `none`.
- In **Send Test Email** Console:
  - When MailDev is active, show banner: *"Dispatched to MailDev! View live rendered message at [http://localhost:1080](http://localhost:1080)."*
- In **Delivery Receipt Modal**:
  - If provider is `maildev`, display a direct clickable link to `http://localhost:1080`.

---

### Component D: Automated Tests & Validation Suite

#### [MODIFY] [backend/tests/test_email_notifications.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_email_notifications.py)
- Add `test_maildev_provider_connection_automated`: tests `MailDevEmailProvider.test_connection()`.
- Add `test_maildev_provider_send_automated`: tests sending email to MailDev on port 1025, asserting `webbox_url` in receipt.

#### [MODIFY] [scripts/verify_email_system_e2e.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/scripts/verify_email_system_e2e.py)
- Add step for MailDev connectivity and verification if MailDev service is running on port 1025/1080.

---

## 4. Verification & Quality Gates

1. **MailDev Container / Service Launch**:
   - `docker-compose up -d maildev` launches `uaic_maildev` listening on ports 1080 and 1025.
   - HTTP GET `http://localhost:1080` returns 200 with MailDev web interface.
   - SMTP socket connect to `localhost:1025` returns `220` MailDev greeting.
2. **End-to-End Delivery to MailDev**:
   - Dispatch test email to `priyer@test.com` with `provider="maildev"`.
   - MailDev captures the email and lists it in its web interface.
   - Delivery receipt in orchestrator DB contains `webbox_url: "http://localhost:1080"` and `server_response`.
3. **Automated Quality Checks**:
   - `backend/.venv/Scripts/pytest -q` (100% pass)
   - `backend/.venv/Scripts/ruff check app tests` (0 errors)
   - `frontend/npx tsc --noEmit` (0 errors)
   - `frontend/npm run lint` & `npm run build` (0 errors)
   - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1` (0 errors)
   - `backend/.venv/Scripts/python.exe scripts/find_uaic_emails.py` (0 occurrences)
