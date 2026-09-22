# Implementation Plan: Subsystem Operator Manuals (County Portals, Email, Storage, Task Queue) & Media Path Normalization

**Implementation ID:** `IMP-2026-0918-004`  
**Target:** Subsystem Operator Manuals in `docs/`, Walkthrough Media Relative Links, and Master `README.md` Index  
**Status:** Ready for Review  
**Date:** 2026-09-18  

---

## 1. Problem Statement & Objectives

While the codebase has comprehensive manuals for [`docs/PROXY_NETWORK_GUIDE.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docs/PROXY_NETWORK_GUIDE.md) and [`docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docs/APIS_AND_MATCHING_ENGINE_GUIDE.md), several critical enterprise subsystems lack dedicated Tier-2 operator manuals in `docs/`:
1. **Public County Court Portals**: Operational architecture for all 8 Florida and Texas court scrapers, DOM selectors, anti-bot/CAPTCHA solver integration, schema rules (6 portals with `CaseType`, 2 portals strictly without `CaseType`), and error screenshot recovery.
2. **Enterprise Email & Notifications Engine**: 6 provider transports (SMTP, Direct MX, Microsoft Graph API, Amazon SES API, MailDev, Local Mock), master toggle dynamics, 5 granular event rules, idempotent dispatches, failure isolation, and HTML email template studio.
3. **Multi-Provider Storage & Async Exports**: Local disk and cloud object storage (AWS S3, Azure Blob, Google Cloud Storage) with zero-dependency local fallback, operator lightbox viewer, brand logo storage, and chunked streaming async exports (PDF, XLSX, CSV, JSON).
4. **Task Queue & Celery Orchestration Engine**: Celery 5.6+ distributed queues (`default`, `ingest`, `scrapers`, `matcher`, `notifications`), Redis 7 broker, Windows attended GUI `-P solo` vs. headless concurrency, automated queue runner, retry tasks, and selective portal retry (S66).
5. **Walkthrough Media Relative Links**: Update the 8 embedded image and video links in [`docs/WALKTHROUGH.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docs/WALKTHROUGH.md) to use clean relative paths (`./step1_upload_page_...`) instead of pointing to transient external brain paths.
6. **Master `README.md` Synchronization**: Update `README.md` Section 1 (Layout Tree) and Section 20 (Documentation Index) to reference all new guides.

---

## 2. Proposed Documentation Suite

### Document 1: [`docs/COURT_PORTALS_GUIDE.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docs/COURT_PORTALS_GUIDE.md)
- **Architecture Overview**: Playwright async browser automation, `BasePortalScraper` lifecycle, `ChromeSession` and `TabManager` integration.
- **Florida Court Portals (3)**:
  - **Broward County Clerk**: URL, party search inputs, docket table scraping, schema (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).
  - **Hillsborough County Clerk (Hover Portal)**: Dynamic hover dropdown navigation, docket grid extraction, schema.
  - **Miami-Dade County Clerk (OCS Portal)**: OCS portal authentication, search tabs, case detail extraction, schema.
- **Texas Court Portals (5)**:
  - **Dallas County (Odyssey Portal)**: Odyssey Smart Search navigation, party queries, docket modal parsing, schema.
  - **Travis County (Odyssey Portal)**: Travis portal interface, Odyssey table extraction, schema.
  - **Harris County Justice of the Peace (JP)**: JP court portal, **Strict Schema Rule: NO `CaseType`**.
  - **Harris County District Clerk (eDocs)**: eDocs search interface, document docket parsing, schema.
  - **Harris County Clerk (cclerk)**: County Clerk records, **Strict Schema Rule: NO `CaseType`**.
- **Anti-Bot & CAPTCHA Solver Integration**:
  - LevelDB API key injection for Manifest v3 AntiCaptcha extension (`kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj`).
  - 5-attempt retry loop, token detection (`g-recaptcha-response`, `h-captcha-response`), Cloudflare/WAF block detection (`SecurityBlockException`) with dynamic cooldowns.
- **Attended GUI vs. Unattended Headless Parity**: `--headless=new`, persistent profile sync, extension active worker verification.
- **Selective Portal Retry (S66)**: Re-running failed portals without creating duplicate case records.

### Document 2: [`docs/EMAIL_AND_NOTIFICATIONS_GUIDE.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docs/EMAIL_AND_NOTIFICATIONS_GUIDE.md)
- **Multi-Provider Transport Matrix**:
  - **Authenticated SMTP**: SSL/TLS (port 465), STARTTLS (ports 587/25).
  - **Corporate Direct MX**: DNS MX resolution with direct port 25 delivery without SMTP credentials.
  - **Microsoft Graph API**: OAuth2 Client Credentials grant (Azure AD App ID, Tenant ID, Client Secret).
  - **Amazon SES API**: AWS Cloud SDK (`boto3`) integration with IAM access keys.
  - **MailDev Webbox**: Local development sandbox (`http://localhost:1080`, SMTP `:1025`).
  - **Local Mock**: Air-gapped in-memory sandbox (`local_mock`) for automated testing.
- **Operational Rules & Toggles**:
  - Master toggle `email_notifications_enabled` (immediate zero-overhead mute).
  - Granular event rules: `guidewire_activity_created`, `guidewire_activity_failed`, `court_case_matched`, `scraper_failed`, `claim_failed`.
  - Idempotency key deduplication (prevents redundant emails on retry).
  - Transactional isolation: Email failures never block or fail the claim workflow.
- **Template Studio & Variable Interpolation**:
  - HTML email templates with dynamic tokens (`{{claim_number}}`, `{{county}}`, `{{case_number}}`, etc.).
  - Variable validation rejecting malformed tokens with HTTP 400.
  - Live dynamic HTML preview and test email dispatch endpoints.

### Document 3: [`docs/STORAGE_AND_EXPORTS_GUIDE.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docs/STORAGE_AND_EXPORTS_GUIDE.md)
- **Storage Provider Architecture**:
  - Local Disk (`backend/screenshots/`, `backend/exports/`, `backend/static/`).
  - AWS S3 (`boto3`), Azure Blob Storage (`azure-storage-blob`), Google Cloud Storage (`google-cloud-storage`).
  - Zero-Dependency Fallback: Fails over to local disk if cloud credentials fail.
- **Error Screenshot Capture & Lightbox**:
  - Automatic frame capture on scraper failure, linking `ErrorScreenshot` ORM model to claims and court portals.
  - Operator Lightbox zoom modal on `/claims/[id]` with metadata, URL, and stack trace.
- **Streaming Asynchronous Exports**:
  - Multi-format generation: Styled PDF dossiers, structured XLSX workbooks, raw CSV data, and JSON payloads.
  - Chunked streaming Celery tasks (`export_tasks.py`) with progress polling for massive datasets.
- **Brand Identity & Asset Management**:
  - Custom logo and favicon upload, validation, persistent disk storage, and HTTP streaming endpoint.

### Document 4: [`docs/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docs/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md)
- **Celery & Redis Architecture**:
  - Celery 5.6+ runtime with Redis 7 (`/0` broker, `/1` backend).
  - 5 Dedicated Queues: `default`, `ingest`, `scrapers`, `matcher`, `notifications`.
- **Concurrency & Process Management**:
  - Attended GUI mode: Windows `-P solo` avoiding subprocess GUI conflicts.
  - Headless Unattended mode: Parallel browser fleet concurrency (`test-fleet` worker pooling).
- **Sequential Queue Runner & Auto-Mode**:
  - Auto-queue sequential dispatch (`queue_runner.py`), pause/retrigger mechanics.
  - Automated retry worker (`retry_tasks.py`) for stalled or failed claims.
- **Observability & Health Probes**:
  - Real-time queue metrics on `/monitor` (8-portal execution matrix, latency telemetry).
  - Celery Flower monitoring dashboard at `http://localhost:5555`.

### Document 5: Walkthrough Media Link Normalization
- Update image/video paths in [`docs/WALKTHROUGH.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/docs/WALKTHROUGH.md) to use local relative references (`./step1_upload_page_...`), making all screenshots and videos render portably on GitHub or offline.

### Document 6: Master `README.md` Synchronization
- Update Section 1 (Layout Tree) and Section 20 (Master Documentation Index) to cross-reference all 6 comprehensive operator manuals in `docs/`.

---

## 3. Verification Plan

### Automated Checks
- PowerShell AST syntax check: `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"`
- Python code & lint check: `.venv\Scripts\ruff check app tests`
- Frontend TypeScript check: `npx tsc --noEmit`
- Targeted test suites: `pytest tests/test_fuzzymatch_api_parity.py tests/test_email_notifications.py tests/test_scrapers.py`

### Documentation Integrity Validation
- Validate all clickable markdown links (`file:///...` and relative `./...`).
- Verify zero dead links or broken file references.
