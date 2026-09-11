# UAIC Claim & RPA Orchestrator — Enterprise Project Booklet

> **Production-grade replacement for legacy Microsoft Power Automate Desktop RPA bots.**
> Automates court-case discovery across 8 Florida & Texas county court portals, performs RapidFuzz deduplication cascade, and delivers validated claim dossiers to Guidewire Insurance Cloud.

---

## 1. Complete Repository Layout & Directory Structure

```
Bot_UAIC/
+-- setup.ps1                            # Root PowerShell setup launcher (delegates to setup_local.ps1)
+-- setup_local.ps1                      # Enterprise Operations & Orchestration Console (interactive menu [0]-[9])
+-- docker-compose.yml                   # Docker multi-container stack (Postgres 16, Redis 7, Flower, etc.)
+-- AGENTS.md                            # Universal AI assistant context, engineering rules & guidelines
+-- README.md                            # Definitive project booklet, architecture, and operations manual
+-- logs/                                # Standardized operational log directory (setup_YYYY-MM-DD_HHmmss.log, setup_latest.log)
+-- Microsoft.VisualStudio.Services.VSIXPackage # Google Gemini Code Assist v2.98.0 VS Code / IDE extension offline bundle (187MB)
|
+-- scripts/                             # Standalone utility & developer diagnostic tools
|   +-- test_setup_console.ps1           # Automated non-interactive test harness for setup console
|   +-- clean_run_history.bat            # Standalone batch file to purge Redis queues & reset DB records
|   +-- start_worker.bat                 # Standalone batch file to start Celery worker in Attended GUI mode
|   +-- run_visible_test.bat             # Standalone batch file to run live GUI court scrape test
|   +-- live_visible_scrape.py           # Hillsborough County live GUI scrape test with real Chrome
|   +-- setup.py                         # Legacy Python environment diagnostics and CLI
|   +-- debug_xlsx.py                    # Excel 1899-12-30 serial date & column parser diagnostic tool
|   +-- inspect_and_render_exports.py    # Verification script for PDF, XLSX, CSV, JSON export packages
|   +-- scratch_test_exports.py          # Scratch export generator test utility
|   +-- verify_export_files.py           # MIME-type and payload integrity validator for exports
|   +-- verify_attended_unattended_parity_e2e.py # Standalone E2E verification of Attended GUI vs Unattended Headless 1:1 parity
|   +-- test_mapping_import.csv          # Column-mapping test dataset (CSV format)
|   +-- test_mapping_import.xlsx         # Column-mapping test dataset (Excel format)
|   +-- orchestrator_historical.db       # Archived SQLite database from initial development
|
+-- backend/                             # Python 3.14 + FastAPI + Celery + SQLAlchemy Async
|   +-- app/
|   |   +-- main.py                      # FastAPI application factory, CORS, static routes & lifespan
|   |   +-- api/v1/endpoints/            # FastAPI REST route handlers
|   |   |   +-- audit.py                 # /audit ^ High-resolution audit log queries & JSON event viewer
|   |   |   +-- claims.py                # All claim CRUD, bulk operations, async Celery export & PDF download
|   |   |   +-- health.py                # /health, /health/detailed (8 components + 8 portals), portal ping
|   |   |   +-- ingest.py                # Drag-and-drop Excel/CSV upload, column mapping & preview
|   |   |   +-- matches.py               # Fuzzy match review, approve/reject endpoints
|   |   |   +-- notifications.py         # Notification history, preview, rules & interactive test email
|   |   |   +-- queue.py                 # Sequential queue runner, auto-queue toggle, pause/retrigger
|   |   |   +-- settings.py              # System settings CRUD, Guidewire/Portal reachability/Chrome test
|   |   +-- automation/                  # Playwright browser automation engine
|   |   |   +-- base.py                  # BasePortalScraper abstract class + CAPTCHA handling
|   |   |   +-- browser_manager.py       # ChromeSession, TabManager, ExtensionManager (LevelDB sync)
|   |   |   +-- session_runner.py        # Orchestrates multi-tab single-window Chrome session
|   |   |   +-- florida/                 # Florida county court scraper implementations
|   |   |   |   +-- broward.py           # Broward County Clerk of Court scraper
|   |   |   |   +-- hillsborough.py      # Hillsborough County Clerk (Hover portal) scraper
|   |   |   |   +-- miami.py             # Miami-Dade County Clerk (OCS portal) scraper
|   |   |   +-- texas/                   # Texas county court scraper implementations
|   |   |       +-- dallas.py            # Dallas County Odyssey portal scraper
|   |   |       +-- travis.py            # Travis County Odyssey portal scraper
|   |   |       +-- harris_jp.py         # Harris County Justice of the Peace scraper (No CaseType)
|   |   |       +-- harris_district.py   # Harris County District Clerk (eDocs) scraper
|   |   |       +-- harris_cclerk.py     # Harris County Clerk scraper (No CaseType)
|   |   +-- core/                        # Core configuration & application singletons
|   |   |   +-- config.py                # Pydantic Settings (reads from backend/.env)
|   |   |   +-- database.py              # Async SQLAlchemy engine, session maker & Base model
|   |   |   +-- celery_app.py            # Celery application instance & task queue definitions
|   |   +-- models/                      # SQLAlchemy ORM database models
|   |   |   +-- audit_log.py             # AuditLog model (event timestamps, severity, metadata)
|   |   |   +-- claim.py                 # ClaimRecord model (claim info, status, state routing)
|   |   |   +-- court_case.py            # ScrapedCourtCase model (portal results, docket data)
|   |   |   +-- error_screenshot.py      # ErrorScreenshot model (links failure frames to claims/portals)
|   |   |   +-- match_result.py          # FuzzyMatchResult model (score, matched party, review state)
|   |   |   +-- notification.py          # NotificationDelivery, Template & EventRule models
|   |   +-- schemas/                     # Pydantic validation schemas
|   |   |   +-- audit.py                 # Audit log query and display schemas
|   |   |   +-- claim.py                 # Claim create, update, filter schemas
|   |   |   +-- court_case.py            # Scraped court case schemas
|   |   |   +-- match.py                 # Match review & approval schemas
|   |   |   +-- notification.py          # Notification delivery, rules, preview & template schemas
|   |   |   +-- queue.py                 # Queue status & item schemas
|   |   |   +-- settings.py              # System settings & credential schemas
|   |   +-- scripts/                     # Internal backend utility scripts
|   |   |   +-- clean_history.py         # Purges Redis queues & clears DB tables (called by setup_local)
|   |   |   +-- generate_sample_files.py # Generates synthetic Excel/CSV test claims with serial dates
|   |   +-- services/                    # Business logic & external integration services
|   |   |   +-- audit_service.py         # High-resolution audit logger for all bot & match actions
|   |   |   +-- email_service.py         # Multi-provider email engine (SMTP, Direct MX, SES, Graph, Mock)
|   |   |   +-- excel_parser.py          # Excel/CSV parser (handles 1899-12-30 serial dates)
|   |   |   +-- export_service.py        # Dossier generator for PDF, XLSX, CSV, JSON formats
|   |   |   +-- fuzzy_engine.py          # RapidFuzz partial_ratio cascade (Claimant>Insured>Driver)
|   |   |   +-- guidewire_client.py      # Guidewire Insurance Cloud client (Bearer/ApiKey/OAuth2)
|   |   |   +-- notification_service.py  # Asynchronous event notification dispatcher & template engine
|   |   |   +-- settings_service.py      # DB-persisted SystemSettings with Redis caching
|   |   |   +-- storage_service.py       # File system storage manager for logos, exports, and uploads
|   |   +-- static/                      # Mounted static web directory for brand logos and assets
|   |   +-- tasks/                       # Celery distributed task definitions
|   |       +-- export_tasks.py          # Celery async streaming export task for massive datasets
|   |       +-- fuzzy_tasks.py           # Celery tasks for fuzzy match cascade & Guidewire push
|   |       +-- ingest_tasks.py          # Celery background tasks for bulk file ingestion
|   |       +-- notification_tasks.py    # Celery async dispatch tasks for email alerts & notifications
|   |       +-- queue_runner.py          # Sequential automated queue processor
|   |       +-- retry_tasks.py           # Automated retry runner for failed or stuck claims
|   |       +-- scraper_tasks.py         # Celery tasks for multi-tab browser court automation
|   +-- cache/                           # Scraper cache storage (downloaded JS bundles)
|   +-- data/                            # Persistent runtime storage for browser cache
|   +-- exports/                         # Generated asynchronous export downloads (XLSX, CSV, PDF)
|   +-- screenshots/                     # Automatic scraper error capture screenshots
|   +-- uploads/                         # Backend uploaded import spreadsheets
|   +-- tests/                           # Comprehensive backend test suite (270 tests across 27 test suites, 100% pass rate)
|   +-- live_e2e_verification.py         # Direct end-to-end integration test against live backend
|   +-- seed_demo_claim.py               # Seed script creating realistic demonstration claims
|   +-- seed_rich_data.py                # Database population script with rich multi-portal test claims
|   +-- seed_user_claim.py               # Seeds customized user test cases
|   +-- orchestrator.db                  # Active SQLite database file in development
|   +-- orchestrator.db.bak              # Pre-migration backup of development database
|   +-- pyproject.toml                   # Python project metadata, dependencies & pytest configuration
|   +-- requirements.txt                 # Pinned Python package dependencies
|   +-- Dockerfile                       # Container definition for backend API & Celery worker
|   +-- .env                             # Local backend environment variables (DATABASE_URL, REDIS_URL)
|   +-- .env.example                     # Example environment configuration template
|
+-- frontend/                            # Next.js 14 App Router + React 18 + Tailwind CSS
|   +-- src/
|   |   +-- app/                         # App Router pages & route layouts
|   |   |   +-- page.tsx                 # Claims Dashboard (table, filter presets, bulk ops, async export)
|   |   |   +-- layout.tsx               # Root application layout with theme & branding context
|   |   |   +-- globals.css              # Global styles, Tailwind directives & CSS variable tokens
|   |   |   +-- claims/[id]/page.tsx     # Claim Detail dossier view (portal cards, match cascade, GW push)
|   |   |   +-- monitor/page.tsx         # Queue Monitor (live metrics, auto-queue, 8-portal matrix)
|   |   |   +-- health/page.tsx          # System Health (8 components, 8 portals, RPA Health Panel)
|   |   |   +-- upload/page.tsx          # Ingestion Console (drag-and-drop, column mapping, preview)
|   |   |   +-- exceptions/page.tsx      # Fuzzy Match Review (approve/reject borderline matches)
|   |   |   +-- settings/page.tsx        # Automation & Robot Configuration (Guidewire, Portals, Browser)
|   |   |   +-- branding/page.tsx        # Brand & Identity Management Console (logo, titles, theme palette)
|   |   |   +-- audit/page.tsx           # Enterprise Audit Trail Console (event timeline, JSON inspector)
|   |   |   +-- notifications/page.tsx   # Dynamic Email & Notification Console (history, templates, rules)
|   |   +-- components/                  # Reusable enterprise UI components
|   |   |   +-- AsyncExportModal.tsx     # Background Celery streaming export modal with progress UI
|   |   |   +-- BrandingContext.tsx      # Theme & brand state context provider
|   |   |   +-- CommandPalette.tsx       # Global Ctrl+K command palette
|   |   |   +-- FileUploader.tsx         # Drag-and-drop file uploader with column mapper
|   |   |   +-- FilterPresetManager.tsx  # Preset manager with system & localStorage custom presets
|   |   |   +-- Footer.tsx               # Global brand footer with copyright & versioning
|   |   |   +-- MobileBottomNav.tsx      # Responsive mobile bottom navigation bar
|   |   |   +-- MobileDrawer.tsx         # Slide-out navigation drawer for mobile viewports
|   |   |   +-- MultiSelectDropdown.tsx  # Reusable multi-select filter dropdown component
|   |   |   +-- Navbar.tsx               # Enterprise top navigation bar with live branding
|   |   |   +-- NavigationContext.tsx    # Mobile drawer and navigation state provider
|   |   |   +-- ResponsiveShell.tsx      # Full-width adaptive shell container
|   |   |   +-- Sidebar.tsx              # Desktop collapsible navigation sidebar
|   |   |   +-- StatusBadge.tsx          # Status badge indicator for claims and bots
|   |   |   +-- ThemeProvider.tsx        # Dynamic theme and color palette provider
|   |   +-- lib/
|   |   |   +-- api.ts                   # Fully-typed Axios API client for all backend endpoints
|   |   +-- types/
|   |       +-- index.ts                 # TypeScript type definitions for claims, portals, settings, etc.
|   +-- public/                          # Static public web assets (favicons, logos)
|   +-- next.config.js                   # Next.js build configuration & asset prefixing
|   +-- package.json                     # Frontend dependencies and scripts
|   +-- postcss.config.js                # PostCSS configuration for Tailwind CSS
|   +-- tailwind.config.js               # Tailwind CSS theme configuration and custom utility classes
|   +-- tsconfig.json                    # TypeScript compiler options
|   +-- Dockerfile                       # Container definition for frontend Next.js app
|
+-- uploads/                             # Staged file upload directory for batch Excel/CSV imports
+-- frames/                              # 91 extracted video frames from PowerAutomate execution recordings
+-- tests/                               # Root-level integration and end-to-end verification scripts
|
+-- [PROTECTED USER DIRECTORIES - NEVER DELETE]
    +-- implementation_plan/             # Authoritative master documentation & original prompts
    |   +-- ChatGPT_Prompt/              # Original foundational requirements (5 ChatGPT prompts + Recon)
    |   +-- 2026-09-05_uaic_master-implementation-plan_v1.md # Master authoritative implementation plan (Human Verified)
    |   +-- 2026-09-05_uaic_master-gap-analysis_v1.md        # Master authoritative gap analysis (Human Verified)
    |   +-- 2026-09-05_uaic_master-walkthrough_v1.md         # Master authoritative system walkthrough (Human Verified)
    |   +-- 2026-09-05_uaic_pending-items-resolution_implementation-record_v1.md # Consolidated forensic record (Human Verified)
    |   +-- implementation_plan.md       # Current active implementation plan (Human Verified)
    |   +-- walkthrough.md               # Current active walkthrough (Human Verified)
    |   +-- README.md                    # Documentation system & governance guide
    +-- PowerAutomateSolutions/          # Authoritative legacy Power Automate reference (V4 Robin flows)
    |   +-- BotCreation_1_0_0_7/         # Solution package containing customizations.xml & desktopflowbinaries
    |   +-- BRD ClaimAutomation_UAIC.pdf # Business Requirements Document
    |   +-- Recording 2026-09-02 *.mp4   # Execution screen recordings of legacy RPA bot runs
    |   +-- fuzzy-match-api.zip          # Legacy fuzzy matching cloud service archive
    +-- Testing files/                   # User-supplied court benchmark spreadsheets and test datasets
    |   +-- sample_claims.xlsx           # Standard test claim records
    |   +-- sample_claims - Florida.xlsx # Florida-specific benchmark claims
    |   +-- sample_claims - Taxes.xlsx   # Texas-specific benchmark claims
    |   +-- ProdRecords1-500.xlsx        # 500 production claim stress-test dataset
    +-- anticaptcha-plugin_v0.83/        # Chrome Manifest v3 AntiCaptcha extension source
    |   +-- manifest.json                # Chrome extension manifest v3 configuration
    |   +-- popup_v3.html                # AntiCaptcha status popup
    |   +-- AntiCaptcha-Key.txt          # Default plugin API key configuration
    |   +-- js/                          # Solver background workers and content scripts
    +-- .agents/                         # AI engineering skills, rules, and governance protocols
        +-- skills/
            +-- diagnose-plan-confirm-execute/ # Mandatory governance lifecycle (Diagnose>Plan>Confirm>Execute)
            +-- theme-system/            # Mandatory Global Light & Dark Theme System governance
            +-- uaic-context/            # Comprehensive repository architectural knowledge & rules
```

---

## 2. Protected User Directories (Mandatory Safety Policy)

The following 5 folders are strictly protected. No cleanup script, purge routine, or automated command may delete or modify them:

1. **`implementation_plan/`**: Contains architectural gap analyses, design roadmaps, and phase-by-phase implementation plans.
2. **`PowerAutomateSolutions/`**: Contains the authoritative legacy Power Automate solutions (`BotCreation_1_0_0_7`), customizations XML, and Robin desktop flow definitions.
3. **`Testing files/`**: Contains client-provided test spreadsheets (`sample_claims.xlsx`, `ProdRecords1-500.xlsx`, etc.).
4. **`anticaptcha-plugin_v0.83/`**: Contains the active Manifest v3 AntiCaptcha solver extension loaded into Google Chrome.
5. **`.agents/`**: Contains reusable AI assistant skills, rules, and engineering governance guidelines (`diagnose-plan-confirm-execute`, `theme-system`, `uaic-context`).

---

## 3. Technology Stack & Modern Architecture

```
 Next.js 14 Web Application (React 18, TypeScript, Tailwind CSS)
                       |
                       | REST API Calls (Axios Typed Client)
                       v
       FastAPI 0.141+ REST Backend (Python 3.14.7, Uvicorn)
         |                                       |
         v                                       v
 SQLAlchemy 2.0 Async               Celery 5.6+ Task Queue Broker
 (SQLite dev / PostgreSQL prod)            (Redis 7 Alpine)
                                                 |
                                 +---------------+---------------+
                                 v                               v
                         Ingest Worker                   Fuzzy Match Worker
                                                         (RapidFuzz Engine)
                                                                 |
                                                                 v
                                                        Scraper Task Worker
                                                                 |
                                                       Playwright Browser
                                                                 |
                                                         Google Chrome
                                                                 |
                                                    AntiCaptcha Plugin v0.83
```

| Layer | Technology |
|---|---|
| **Frontend UI** | Next.js 14 App Router, React 18, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend API** | FastAPI 0.141+, Python 3.14.7, Pydantic v2, Uvicorn 0.52+ |
| **Task Queue & Broker** | Celery 5.6+, Redis 7 Alpine, Celery Beat, Celery Flower |
| **Database & ORM** | SQLAlchemy 2.0 Async, SQLite (Local Dev) / PostgreSQL 16 (Production) |
| **Browser RPA Automation** | Playwright 1.62+, Real Google Chrome, AntiCaptcha Extension v0.83 |
| **Fuzzy Matching** | RapidFuzz 3.14+ (C-accelerated partial_ratio string distance cascade) |
| **Insurance Cloud Integration**| Guidewire Cloud REST API (Bearer, ApiKey, Basic, OAuth2) |
| **Verification & Quality** | Pytest 9.1+ (270 test cases across 27 test suites, 100% pass), Ruff 0.16+, TypeScript Compiler |

---

## 4. Power Automate > Modern Platform Mapping

The **V4** Robin desktop flow definitions inside [`PowerAutomateSolutions/BotCreation_1_0_0_7/`](./PowerAutomateSolutions/BotCreation_1_0_0_7/) serve as the authoritative behavioral reference for court automation.

| Legacy Power Automate Component | Modern Python / Next.js Implementation | Key V4 Enhancements Retained |
|---|---|---|
| `Import_ExcelData_To_Dataverse.json` | `backend/app/services/excel_parser.py` + `/api/v1/ingest/upload` | 1899-12-30 serial date base preserved without timezone drift. |
| `PA_FuzzyMatch_ActivityCreation_v1_Main.json` | `backend/app/services/fuzzy_engine.py` + `tasks/fuzzy_tasks.py` | RapidFuzz partial_ratio cascade (Claimant>Insured>Driver). |
| `AddItemstoWorkQueue.json` | Celery Queues (`ingest`, `scrapers`, `matcher`, `notifications`) | Distributed Redis broker with automated priority queues. |
| `RetriggerFailedCases.json` | `backend/app/tasks/retry_tasks.py` + Celery Beat | Automatic retry of failed court portals with configurable limits. |
| `Broward_`, `Hillsborough_`, `Miami_` | `backend/app/automation/florida/` (Playwright) | Multi-tab session re-use; no aggressive Chrome termination. |
| `Travis_`, `Dallas_`, `Harris_`, `CClerk_`, `HCDistrict_` | `backend/app/automation/texas/` (Playwright) | Strict schema alignment: Harris JP & Harris Clerk have NO CaseType. |
| Power Apps Model-Driven Forms | Next.js 14 Full Dashboard & Health Console | Real-time queue telemetry, live portal matrix, and branding console. |

---

## 5. Operations & Orchestration Console (`setup.ps1` & `setup_local.ps1`)

The repository includes a unified, interactive operations console built in PowerShell for Windows local development and Attended RPA operation.

### Launching the Console
```powershell
# Interactive Menu:
.\setup.ps1

# Non-interactive CLI switches:
.\setup.ps1 -StartAll -Mode Attended -NoPrompt    # Start all 5 service windows in Attended GUI mode
.\setup.ps1 -StopAll -NoPrompt                   # Stop all running processes and containers
.\setup.ps1 -CleanHistory -NoPrompt              # Purge queue history and all bytecode/test caches
.\setup.ps1 -RunTests -NoPrompt                  # Run full 4-tier diagnostics (Pytest, Ruff, TS, Docker)
.\setup.ps1 -InstallDeps -NoPrompt               # Verify/reinstall Python .venv and NPM dependencies
```

### Menu Options Overview (`setup_local.ps1`)

```
=======================================================================
                  Enterprise Operations & Orchestration Console
 Active RPA Engine Mode: [Attended (GUI)]
 Log File: C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\setup.log
=======================================================================
 [1] Start All Application Services (Interactive Launch with Mode Select)
 [2] Stop / Kill All Running Services (Ports 3000, 8000, 5555, Celery)
 [3] Clean Run History, Logs & Scraper Caches
 [4] Install / Update Dependencies (Python venv, Playwright, NPM)
 [5] Purge / Delete All Dependency Folders (.venv, node_modules, .next)
 [6] Configure RPA Execution Mode (Attended GUI vs Unattended Headless)
 [7] Run Full Diagnostics & Test Suite (Pytest, Ruff, TypeScript)
 [8] Docker Container & Infrastructure Console (PostgreSQL & Redis)
 [9] Live Service Status Monitor (Quick Controls: [R/K/M/Q])
 [0] Exit Console
=======================================================================
```

| Option | Function | Execution Details |
|---|---|---|
| **`[1]` Start All Services** | Launches stack in 5 separate persistent consoles | Spawns FastAPI (`:8000`), Next.js (`:3000`), Celery Worker (`-P solo`), Celery Beat, and Flower (`:5555`). Prompts for Attended GUI or Unattended Headless mode. |
| **`[2]` Stop All Services** | Complete termination of all processes & containers | Kills listening processes on ports 3000, 8000, and 5555; terminates Celery worker; stops Redis (`6379`) and PostgreSQL (`5432`) containers. |
| **`[3]` Clean Run History & Caches** | Deep cache, queue, and database cleanup | Clears `setup.log`, resets Celery beat schedule, empties temporary scraper media, purges Redis queues and database records via `clean_history.py`, and recursively purges `__pycache__`, `.pyc`, `.pytest_cache`, `.ruff_cache`, and `.next/cache` while strictly safeguarding `.venv` and protected folders. |
| **`[4]` Install Dependencies** | Automated dependency manager | Creates Python 3.14 `.venv`, installs `requirements.txt`, installs Playwright Chromium browser binaries, and runs `npm install`. |
| **`[5]` Purge Dependency Folders** | Clean-slate reset | Safely deletes `.venv`, `node_modules`, and `.next` after user confirmation, preserving all 5 protected folders. |
| **`[6]` Configure RPA Mode** | Hot-swaps browser execution mode | Updates `PLAYWRIGHT_HEADLESS=false` (Attended GUI) or `PLAYWRIGHT_HEADLESS=true` (Unattended Headless) in `backend/.env`. |
| **`[7]` Run Diagnostics & Tests** | 4-tier automated test runner | Executes Backend Pytest (270 tests across 27 suites), Ruff Linter, Frontend TypeScript (`tsc --noEmit`), and Docker Compose validation. |
| **`[8]` Docker Infrastructure Console** | Manage Redis & PostgreSQL containers | Supports `docker compose` (v2) and `docker-compose` (v1) with actions: Up `[U]`, Down `[D]`, Restart infrastructure only `[R]`, and Status `[S]`. |
| **`[9]` Live Status Monitor** | Real-time port listener status | Displays live listening status for ports 3000, 8000, 5555, 6379, and 5432 with hotkey actions: `[R]` Refresh, `[K]` Stop Services, `[M]` Main Menu, `[Q]` Exit. |
| **`[0]` Exit** | Clean exit | Closes the console with exit code 0. |

---

## 6. Standalone Utility Scripts (`scripts/`)

All standalone and diagnostic scripts are organized in [`scripts/`](./scripts/):

| Script | Purpose & Description | Handled in `setup_local.ps1`? |
|---|---|---|
| **`clean_run_history.bat`** | Standalone batch file to reset SQLite database tables and purge Redis queues without the menu. | **Yes** — Handled directly via Option `[3]` and `setup.ps1 -CleanHistory`. |
| **`start_worker.bat`** | Standalone batch file to launch only the Celery worker in Attended mode. | **Yes** — Handled directly via Option `[1]` in `setup_local.ps1`. |
| **`run_visible_test.bat`** | Standalone batch runner that triggers `live_visible_scrape.py`. | **Yes** — Handled directly via the visible GUI test button in the `/health` UI and Option `[7]`. |
| **`live_visible_scrape.py`** | Standalone Python script that launches Chrome in visible GUI mode and searches Hillsborough County Court portal for 'JOHN DOE'. | **Yes** — Fully incorporated into the RPA Health Panel on `/health`. |
| **`verify_attended_unattended_parity_e2e.py`** | Standalone Python validation harness verifying 1:1 functional parity between Attended GUI and Unattended Headless automation. | **Yes** — Validated directly and via Pytest suite `tests/test_attended_unattended_parity.py`. |
| **`setup.py`** | Legacy Python CLI diagnostic tool for environment inspection. | **Yes** — Replaced and superseded by `setup.ps1` and `setup_local.ps1`. |
| **`debug_xlsx.py`** | Diagnostic script to test 1899-12-30 Excel serial date conversions and pandas column parsing. | Standalone diagnostic tool for testing custom client Excel files. |
| **`inspect_and_render_exports.py`** | Utility to validate generated PDF, CSV, Excel, and JSON claim export packages. | Standalone test tool. |
| **`verify_export_files.py`** | Verifies file integrity and MIME types for exported claim dossiers. | Standalone test tool. |
| **`test_mapping_import.csv`** & **`.xlsx`** | Sample datasets for testing custom column-mapping ingestion. | Standalone test assets. |
| **`orchestrator_historical.db`** | Archived SQLite database snapshot from early development. | Archived reference. The active database is in `backend/orchestrator.db`. |

---

## 7. Cache & Temporary Storage Management

### Why are caches generated?
- **Python Bytecode (`__pycache__`, `*.pyc`)**: Generated automatically by the Python interpreter during unit testing, backend startup, or Celery task execution to speed up module imports.
- **Test & Linter Caches (`.pytest_cache`, `.ruff_cache`)**: Generated by `pytest` and `ruff` to track file hashes and accelerate subsequent test passes.
- **Frontend Build Caches (`.next/cache`)**: Generated by Next.js during compilation to optimize incremental page rendering.
- **Temporary Media Storage (`.tempmediaStorage`)**: Generated during browser scraping sessions to capture error screenshots and debug snapshots.

### How to purge all caches?
Execute Option `[3]` in `setup_local.ps1` or run:
```powershell
.\setup.ps1 -CleanHistory -NoPrompt
```
This performs a deep clean across all project directories:
1. Deletes all `__pycache__` folders and `.pyc`/`.pyo` files across root, `backend/`, and `tests/` (while safeguarding `.venv` packages).
2. Purges `.pytest_cache` and `.ruff_cache`.
3. Clears Next.js `.next/cache`.
4. Empties `.tempmediaStorage` and removes scratch test export files.
5. Purges Redis Celery broker queues and resets database run history.

---

## 8. Docker Infrastructure & Container Stack

The project uses `docker-compose.yml` to orchestrate services:

| Container | Image | Ports | Role |
|---|---|---|---|
| **`uaic_postgres`** | `postgres:16-alpine` | `5432:5432` | Production PostgreSQL relational database with health check and persistent volume `postgres_data`. |
| **`uaic_redis`** | `redis:7-alpine` | `6379:6379` | High-throughput in-memory Celery task broker, result backend, and system settings cache with persistent volume `redis_data`. |
| **`uaic_backend`** | Custom Python 3.14 | `8000:8000` | FastAPI REST API container (used in all-in-one container deployments). |
| **`uaic_celery_worker`** | Custom Python 3.14 | - | Headless background worker for cloud/container deployments. |
| **`uaic_flower`** | Custom Python 3.14 | `5555:5555` | Celery Flower real-time task observability dashboard. |
| **`uaic_frontend`** | Custom Node.js 20 | `3000:3000` | Next.js 14 web application. |

### Hybrid Local Development Workflow
In local Windows development with real Google Chrome and the AntiCaptcha extension:
1. Run Docker Compose in infrastructure mode to launch Redis (`6379`) and PostgreSQL (`5432`):
   ```bash
   docker compose up -d postgres redis
   ```
2. Run `setup_local.ps1` to launch the backend, frontend, and Celery worker on the Windows host OS so Playwright can launch a real visible Google Chrome browser window on your desktop.

---

## 9. Database Storage Keys

When court case scrapers complete execution, their results are stored in the database under standardized JSON payload keys:

| Portal | Storage Key | Output Schema |
|---|---|---|
| **Broward County (FL)** | `fl_jsonbody_broward` | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Hillsborough County (FL)** | `fl_jsonbody_hillsborough` | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Miami-Dade County (FL)** | `fl_jsonbody_miami` | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Harris County Clerk (TX)** | `te_jsonbody_cclerk` | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO CaseType**) |
| **Dallas County (TX)** | `te_jsonbody_dallas` | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Harris County JP (TX)** | `te_jsonbody_harris` | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO CaseType**) |
| **Harris District Clerk (TX)**| `te_jsonbody_hcdistrict`| `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |
| **Travis County (TX)** | `te_jsonbody_travis` | `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType` |

---

## 10. Frontend Application Routes

| Route | Component | Description |
|---|---|---|
| **`/`** | `app/page.tsx` | Claims Dashboard — Search, filter presets, bulk operations, async export trigger. |
| **`/claims/:id`** | `app/claims/[id]/page.tsx` | Claim Detail — Dossier view, 8-portal results, fuzzy match cascade, Guidewire push. |
| **`/upload`** | `app/upload/page.tsx` | Ingestion — Drag-and-drop Excel/CSV file upload with column mapping & preview. |
| **`/monitor`** | `app/monitor/page.tsx` | Queue Monitor — Real-time queue metrics, auto-queue, expandable 8-portal matrix with single bot triggers. |
| **`/health`** | `app/health/page.tsx` | System Health — 8 component health checks, 8 portal pings, and RPA Browser & Automation Health Panel. |
| **`/exceptions`** | `app/exceptions/page.tsx` | Fuzzy Match Review — Review and approve/reject borderline court matches. |
| **`/settings`** | `app/settings/page.tsx` | Automation & Robot Configuration — Guidewire API, Portals, Browser/Extension settings. |
| **`/branding`** | `app/branding/page.tsx` | Brand & Identity Console — Customize portal title, logo, themes, and styles. |
| **`/audit`** | `app/audit/page.tsx` | Enterprise Audit Trail Console — High-resolution operational audit logging across all scraper and matching runs. |
| **`/notifications`** | `app/notifications/page.tsx` | Dynamic Email & Notification Console — Delivery history log, HTML template manager & live preview, event notification rules matrix. |

**Global Command Palette (`Ctrl+K`)**: Instant search and navigation across all claims, queue triggers, and settings.

---

## 11. Theme & Branding Configuration

The platform includes a dedicated **Brand & Identity Management Console** at [`/branding`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/branding/page.tsx) and persistent context via [`BrandingContext.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/components/BrandingContext.tsx):

- **Live Branding Customization**: Update application title, navigation subtitle, copyright footer, and company logo in real-time.
- **Custom Logo Drag-and-Drop Dropzone**: Upload PNG, JPEG, or SVG logos directly to `/api/v1/settings/branding/logo`.
- **Dynamic CSS Variable Theming**: Configure primary brand colors, accent gradients, and dark/light mode appearance.
- **Instant Propagation**: All changes sync immediately to the sidebar, navbar, command palette, and PDF export templates.

---

## 12. Backend API Endpoints Summary

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Basic health check |
| `GET` | `/api/v1/health/detailed` | Full system observability (8 components + 8 court portals) |
| `GET/POST` | `/api/v1/health/portals/{key}/ping` | Portal reachability and latency ping |
| `GET` | `/api/v1/claims` | List claims (paginated, filterable, sortable) |
| `POST` | `/api/v1/claims` | Create claim |
| `GET` | `/api/v1/claims/{id}` | Claim detail dossier |
| `PUT` | `/api/v1/claims/{id}` | Update claim details |
| `DELETE`| `/api/v1/claims/{id}` | Delete claim record |
| `POST` | `/api/v1/claims/{id}/start` | Start court discovery automation for claim |
| `POST` | `/api/v1/claims/{id}/stop` | Cancel in-flight claim automation |
| `POST` | `/api/v1/claims/{id}/push-guidewire` | Push validated matches to Guidewire |
| `POST` | `/api/v1/claims/{id}/run-bot/{key}` | Trigger single portal scraper on demand |
| `POST` | `/api/v1/claims/{id}/retry-failed` | Retry only failed court portals for single claim (S66) |
| `GET` | `/api/v1/claims/{id}/audit-logs` | Retrieve chronological audit provenance for claim |
| `GET` | `/api/v1/claims/{id}/screenshots` | List failure error screenshots for claim |
| `GET` | `/api/v1/claims/{id}/screenshots/{id}/image` | Stream binary failure screenshot directly to browser |
| `GET` | `/api/v1/claims/{id}/export` | Export single claim dossier (XLSX, CSV, JSON, PDF) |
| `GET` | `/api/v1/claims/stats` | Aggregate dashboard statistics |
| `GET` | `/api/v1/claims/export` | Synchronous bulk export |
| `POST` | `/api/v1/claims/export-async` | Celery background chunked streaming export for large datasets (S55) |
| `GET` | `/api/v1/claims/export-async/{task_id}/status` | Check status and progress of async export task |
| `GET` | `/api/v1/claims/export-async/download/{filename}` | Download generated async export file |
| `POST` | `/api/v1/claims/bulk-delete` | Bulk delete selected claims |
| `POST` | `/api/v1/claims/bulk-start` | Bulk start court automation |
| `POST` | `/api/v1/claims/bulk-retry` | Bulk retry failed claims (supports `failed_portals_only`) |
| `POST` | `/api/v1/claims/bulk-status` | Bulk update status |
| `POST` | `/api/v1/claims/clean` | Clear claim records (preserves audit log provenance) |
| `POST` | `/api/v1/ingest/upload` | Upload and ingest Excel/CSV dataset |
| `POST` | `/api/v1/ingest/preview` | Preview file structure and auto-detect columns |
| `POST` | `/api/v1/ingest/validate` | Validate user column mapping & sample data preview (S56) |
| `GET` | `/api/v1/ingest/batches/{batch_id}` | Retrieve ingestion batch status and counts |
| `GET` | `/api/v1/ingest/batches/{batch_id}/failed-rows` | Export invalid rows as downloadable CSV |
| `GET` | `/api/v1/ingest/sample/excel` | Download sample Excel template |
| `GET` | `/api/v1/ingest/sample/csv` | Download sample CSV template |
| `GET` | `/api/v1/matches/pending` | Get pending fuzzy match reviews |
| `POST` | `/api/v1/matches/{id}/review` | Approve or reject a fuzzy match candidate |
| `GET` | `/api/v1/queue/status` | Real-time queue metrics and worker health |
| `POST` | `/api/v1/queue/start-all` | Start sequential queue processor |
| `POST` | `/api/v1/queue/pause` | Pause queue processing |
| `POST` | `/api/v1/queue/retrigger` | Retrigger failed queue items |
| `GET/POST`| `/api/v1/queue/auto-mode` | Get or toggle auto-queue processing mode |
| `GET` | `/api/v1/settings` | Get system settings (passwords masked) |
| `POST` | `/api/v1/settings` | Save system settings |
| `POST` | `/api/v1/settings/reset` | Reset system settings to clean defaults |
| `POST` | `/api/v1/settings/test-guidewire` | Test Guidewire connection with custom payload |
| `POST` | `/api/v1/settings/test-portal` | Test portal reachability |
| `POST` | `/api/v1/settings/test-browser` | Launch live Chrome test (Attended GUI vs Headless) |
| `POST` | `/api/v1/settings/validate-extension` | Validate AntiCaptcha extension directory, manifest, and engine |
| `POST` | `/api/v1/settings/test-storage` | Test storage provider connectivity (Local, S3, Azure, GCS) |
| `POST` | `/api/v1/settings/email/test-connection` | Test SMTP/Mock email provider connectivity & latency |
| `POST` | `/api/v1/settings/email/test-send` | Send interactive live test email |
| `GET/POST`| `/api/v1/settings/branding` | Get or update branding configuration |
| `POST` | `/api/v1/settings/branding/reset`| Reset branding to system defaults |
| `POST` | `/api/v1/settings/upload-logo` | Upload brand logo image |
| `GET` | `/api/v1/settings/logo/{filename}` | Stream uploaded logo image (HTTP 200 OK) |
| `GET` | `/api/v1/notifications` | Paginated notification delivery history log |
| `GET` | `/api/v1/notifications/{id}` | Retrieve single notification record details |
| `GET` | `/api/v1/notifications/templates` | List notification email templates |
| `GET` | `/api/v1/notifications/templates/{id}/preview` | Dynamic HTML preview of notification template |
| `GET` | `/api/v1/notifications/rules` | List event trigger rules & recipient matrix |
| `PUT` | `/api/v1/notifications/rules` | Update event notification rules |
| `GET` | `/api/v1/audit-logs` | Query paginated audit events with filters (S73) |
| `GET` | `/api/v1/audit-logs/stats` | Aggregate audit event KPI statistics |
| `GET` | `/api/v1/audit-logs/export` | Stream full compliance audit logs (CSV or JSON) |
| `GET` | `/api/v1/audit-logs/{id}` | Retrieve single audit event details |

---

## 13. Enterprise Subsystem Architecture

### A. Multi-Provider Error Screenshot Storage
- **Supported Providers**: Local Disk (`backend/screenshots/`), AWS S3, Azure Blob Storage, and Google Cloud Storage (GCS).
- **Zero-Dependency Fallback**: Automatically fails over to local storage if cloud credentials fail.
- **Operator Lightbox**: High-resolution zoom modal on `/claims/[id]` showing URL, title, attempt number, and exception diagnostics.
- **Master Toggle**: Configurable in `/settings` to conserve storage space.

### B. Selective Error Recovery (S66)
- **Portal-Level Granularity**: `POST /api/v1/claims/{id}/retry-failed` re-runs only portals in `FAILED` status.
- **Deduplication Safeguard**: Deletes existing cases for only the retried county before re-inserting, strictly avoiding duplicate rows.
- **Auto-Cascade**: Automatically triggers RapidFuzz matching across accumulated cases upon retry completion.

### C. Immutable Audit Log & Zero Credential Leakage (S73)
- **Provenance Recording**: Logs all claims operations, settings changes, ingestion batches, and Guidewire dispatches with client IP (`x-forwarded-for`) and operator email.
- **Zero-Leakage Sanitizer**: Recursively traverses payloads and masks sensitive keys (`password`, `token`, `secret`, `api_key`, `key`) with `[REDACTED]`.
- **Audit Console (`/audit`)**: Full-width console with 6 KPI cards, multi-dimensional filters, payload viewer, and CSV/JSON export.

### D. 5-Step Column Mapping Ingestion Wizard (S56)
- **Step-by-Step Flow**: Upload > Mapping > Validation & Preview > Import > Summary.
- **Fuzzy Header Match**: Automatically pairs uploaded column names with internal fields with manual override dropdowns.
- **Invalid Row Download**: Direct button to export rejected rows as CSV for user correction.

### E. 8-Portal Execution Matrix on Queue Monitor (S61)
- **Expandable Matrix**: Accordion rows on `/monitor` reveal an 8-portal grid for Broward, Hillsborough, Miami, Travis, Dallas, Harris JP, Harris Clerk, and Harris District.
- **Real-Time Visibility**: Live status pills, case counts, latency timing, and per-portal "Run Bot" triggers.

### F. Filter Preset Manager (S83)
- **System & Custom Presets**: `<FilterPresetManager />` provides built-in filters (*All Claims*, *Needs Review*, *Failed Portals*, *Texas*, *Florida*) and saves custom user filters to `localStorage` (`uaic_filter_presets_v1`).

### G. Power Platform Parity & Enterprise Notification Engine (S74)
- **Power Platform Parity**: Replicates and enhances the notification capabilities of the legacy Power Automate Cloud Flow (`UAICBotCreationMainFlow-V4`).
- **Master ON/OFF Switch**: Global toggle (`email_notifications_enabled`) immediately mutes all automatic event notification dispatches with zero Celery task or database overhead.
- **Provider Agnostic**: Seamlessly switches between live SMTP (SSL/TLS/STARTTLS with connection testing) and local mock delivery (`local_mock`) for air-gapped development and testing.
- **Granular Event Triggers**: Per-event rule toggles for `guidewire_activity_created`, `guidewire_activity_failed`, `scraper_failed`, and `claim_failed`.
- **Responsive HTML Templates**: Dark-mode safe, table-based HTML email templates with dynamic variable interpolation and live preview in `/settings`.
- **Non-Blocking Dedicated Queue**: Dispatches notifications over an isolated `"notifications"` Celery queue with exponential retry backoff, fully decoupled from claim execution.
- **Interactive Operator Testing & History**: 1-click SMTP connectivity test, live interactive test email sender, and a real-time delivery history log table in `/settings`.

### H. Enterprise Setup & Operations Console (Options 1–9 & M)
- **Centralized Management (`setup_local.ps1` / `setup.ps1`)**: Interactive menu backed by real Windows process management (`Get-CimInstance Win32_Process`) rather than blind script execution.
- **[1] Start All Services**: Interactive choice of Attended GUI vs Unattended Headless, with automated pre-flight port conflict checking (`3000`, `8000`, `5555`, `6379`, `5432`, `1080`, `1025`).
- **[2] Stop All Services**: Targeted termination of application workers (`uvicorn`, `celery`, `flower`, `maildev`, `next dev`), leaving unrelated system processes untouched. Explicitly frees MailDev ports (`1080` and `1025`).
- **[3] Clean Run History & Enterprise Data Cleanup**: Invokes time-scoped multi-category cleanup engine with dry-run preview and cascade deletion.
- **[4] Install Dependencies**: Dynamic browser matrix detection. **Bypasses bundled Chromium download** when host Google Chrome or Microsoft Edge is detected or configured.
- **[5] Purge Folders**: Cleans `.venv`, `node_modules`, `.next`, `.turbo`, and pytest/ruff build caches while strictly guarding the 5 protected user directories (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`), source code, and credentials.
- **[6] RPA Mode**: Interactive toggle between Attended GUI (visible browser with AntiCaptcha inspection) and Unattended Headless (Docker/CI), immediately persisted and honored by backend `ChromeSession`.
- **[7] Diagnostics Suite**: Comprehensive 5-pass runner: Backend Pytest, Python Ruff linter, Frontend TypeScript (`tsc --noEmit`), Docker Compose configuration, and PowerShell AST syntax validation.
- **[8] Docker Infrastructure**: Multi-container stack orchestration with host-exposed ports (`5432:5432` PostgreSQL, `6379:6379` Redis, `1080:1080` & `1025:1025` MailDev).
- **[9] Live Monitor**: Dynamic HTTP and TCP probes displaying status, latency, and endpoints across all stack components.
- **[M] MailDev**: Quick launch of MailDev Web Inspector (`http://localhost:1080`) with SMTP/HTTP health checks.

### I. Enterprise Time-Based Multi-Select Data Cleanup Engine
- **9 Independent Categories**: `claims`, `queue`, `court_cases`, `matches`, `guidewire`, `notifications`, `telemetry`, `logs`, `caches`.
- **Dynamic Time Scoping**: `current_month` (1st of current month `00:00:00` to current moment), `1_day`, `7_days`, `14_days`, `30_days`, `90_days`, `6_months`, `1_year`, `all_time`, or custom date ranges (`YYYY-MM-DD`).
- **Dry-Run Preview & Explicit Confirmation**: Simulates deletions without writing to database; requires explicit confirmation before executing destructive operations.
- **Transactional Cascade Integrity**: Deleting claims automatically cascades to court cases, fuzzy matches, screenshots, and notification history records, eliminating orphaned data.
- **Redis & Dashboard Invalidation**: Purges cached statistics (`cache:*`, `metrics:*`, `stats:*`, `dashboard:*`) with safe socket timeouts (1.0s) ensuring zero worker deadlocks when Redis is offline.
- **Dual Interface**: Accessible via CLI (`python -m app.scripts.clean_history`) and REST API (`POST /api/v1/claims/clean`).

### J. Attended vs. Unattended RPA 1:1 Parity Validation
- **100% Behavioral Parity**: Every workflow that executes in Attended Mode (visible desktop Google Chrome GUI) executes with identical results in Unattended Mode (headless).
- **Modern Headless Extension Loading**: Playwright initializes Chromium with `--headless=new` and extension flags (`--load-extension`, `--disable-extensions-except`), enabling Manifest v3 AntiCaptcha extension loading even in headless environments (`ExtLoaded=True`, active service workers verified).
- **Zero Desktop Session Reliance**: Scraper automation does not rely on active desktop sessions, pre-opened browser windows, focus state, or manual clicks.
- **Full End-to-End Equivalence**: Verified 1:1 extraction across all 8 court scrapers, pagination handling, strict schema compliance (NO `CaseType` on Harris JP and Harris Clerk), RapidFuzz 3-tier cascade, and Guidewire Cloud payload formatting.
- **Automated Parity Test Harness**: Standalone runner `scripts/verify_attended_unattended_parity_e2e.py` and dedicated Pytest test suite `backend/tests/test_attended_unattended_parity.py`.

---

## 14. Critical Business Rules (Authoritative)

### State Routing Logic
- **`policy_state == loss_location_state == 'FL'`**: Scrape Florida portals (`broward`, `hillsborough`, `miami`).
- **`policy_state == loss_location_state == 'TX'`**: Scrape Texas portals (`harris_cclerk`, `dallas`, `harris_jp`, `harris_district`, `travis`).
- **Cross-State (`policy_state != loss_location_state`)**: Scrape **all 8 court portals**.

### DOL Date Conversion
Excel serial dates must use the **1899-12-30** base and be formatted as `MM/dd/yyyy` without timezone shifts.

### Guidewire Claim Number Rule
If `len(claim_number) == 9`, prepend a leading `"0"` (applied only to the Guidewire outbound JSON payload).

### Fuzzy Match Cascade (RapidFuzz `partial_ratio`, threshold=0.6)
1. Claimant (First + Last) > CaseStyle
2. Insured (First + Last) > CaseStyle
3. Driver (First + Last) > CaseStyle
Minimum filing date: `>= 2010-01-01` (configurable in Settings).

### Search Count Derivation (DualSearch / TripleSearch)
| Scenario | DualSearch | TripleSearch |
|---|---|---|
| All parties same | 1 | 1 |
| Insured = Driver, Claimant = | 1 | 3 |
| Insured = Claimant, Driver = | 2 | 1 |
| Driver = Claimant, Insured = | 2 | 1 |
| All parties different | 2 | 3 |

### Portal Output Schema
- Broward, Hillsborough, Miami, Dallas, Travis, Harris District: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`.
- **Harris JP** and **Harris County Clerk**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO `CaseType`**).

---

## 15. Guidewire Integration Contract

Outbound Guidewire JSON payload specification:
```json
{
  "ClaimNumber": "0123456789",
  "ExposureNumber": "001",
  "CaseItems": [
    {
      "CaseNumber": "2024-CA-001234",
      "CaseStyle": "JOHN DOE VS JANE SMITH",
      "CountyWebsite": "https://hover.hillsclerk.com",
      "SuitFiledDate": "01/15/2024"
    }
  ]
}
```

---

## 16. Chrome & AntiCaptcha Setup

1. Install **Google Chrome** on the Windows host machine.
2. The AntiCaptcha extension is located in [`anticaptcha-plugin_v0.83/`](./anticaptcha-plugin_v0.83/).
3. In **Settings > Browser & CAPTCHA**:
   - Set AntiCaptcha API Key (masked in UI).
   - Verify Chrome Extension Directory (`anticaptcha-plugin_v0.83/`).
   - Choose Browser Execution Mode: `Attended (Visible GUI)` for desktop visibility or `Unattended (Headless)` for background runs.
4. The system automatically synchronizes the API key to both `chrome.storage.local` and `chrome.storage.sync` LevelDB backing files, ensuring the plugin icon turns green and solves reCAPTCHA / hCaptcha automatically.

---

## 17. Court Portal Endpoints

| Portal | State | Default Base URL | Deep Search Endpoint |
|---|---|---|---|
| **Broward County Clerk** | FL | `https://www.browardclerk.org/` | `https://www.browardclerk.org/Web2` |
| **Hillsborough County Clerk** | FL | `https://hover.hillsclerk.com/` | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` |
| **Miami-Dade County Clerk** | FL | `https://www2.miamidadeclerk.gov/ocs` | `https://www2.miamidadeclerk.gov/ocs` |
| **Travis County** | TX | `https://odysseyweb.traviscountytx.gov/Portal/` | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` |
| **Dallas County** | TX | `https://courtsportal.dallascounty.org/DALLASPROD/Home/` | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` |
| **Harris County JP** | TX | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/` | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` |
| **Harris County Clerk** | TX | `https://www.cclerk.hctx.net/Applications/WebSearch/` | `https://www.cclerk.hctx.net/Applications/WebSearch/` |
| **Harris District Clerk** | TX | `https://www.hcdistrictclerk.com/` | `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` |

---

## 18. Automated Verification Commands

```powershell
# Enterprise Setup Console Full Automated Test Harness (AST, Ports, StopAll, CleanHistory, RunTests)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\test_setup_console.ps1"

# Backend Automated Unit & Integration Tests (270 tests across 27 test suites, 100% pass rate)
cd backend
.venv\Scripts\pytest -ra -q

# Attended vs. Unattended 1:1 Parity Test Suite (6 tests, 100% pass rate)
.venv\Scripts\pytest tests/test_attended_unattended_parity.py -v

# Standalone E2E Attended vs. Unattended Parity Live Verification Harness
.venv\Scripts\python ..\scripts\verify_attended_unattended_parity_e2e.py

# Setup Console Specific Process & Matrix Test Suite (11 tests, 100% pass rate)
.venv\Scripts\pytest tests/test_setup_console.py -v

# Enterprise Time-Based Multi-Select Data Cleanup Test Suite (12 tests, 100% pass rate)
.venv\Scripts\pytest tests/test_enterprise_cleanup.py -v

# Dynamic Browser Matrix Test Suite (10 tests, 100% pass rate)
.venv\Scripts\pytest tests/test_browser_matrix.py -v

# Backend Code Quality & Linter (0 errors)
.venv\Scripts\ruff check app tests

# Frontend TypeScript Typecheck (0 errors)
cd ..\frontend
npx tsc --noEmit

# Frontend Production Build (All routes compile cleanly)
npm run build

# PowerShell Syntax & AST Parser Verification (0 errors across all 6 scripts)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"

# Enterprise Cleanup CLI Syntax Examples
python -m app.scripts.clean_history --categories all_operational --time-scope current_month --dry-run
python -m app.scripts.clean_history --categories claims,notifications --time-scope 30_days --confirm
```

---

## 19. Technology Stack & Documentation

Complete technology reference for the UAIC Claim & RPA Orchestrator. Every technology listed here is actively used in production. Official documentation links are provided for onboarding new developers.

### Frontend

| Technology | Role in This Solution | How We Use It | Official Documentation |
|---|---|---|---|
| **Next.js 14** | Full-stack React framework with App Router | Server-side rendering, file-based routing for all 8 app pages (`/`, `/claims/:id`, `/upload`, `/monitor`, `/health`, `/exceptions`, `/settings`, `/branding`, `/audit`) | [nextjs.org/docs](https://nextjs.org/docs) |
| **React 18** | UI component library | Functional components, hooks (`useState`, `useEffect`, `useContext`, `useCallback`), concurrent features | [react.dev](https://react.dev) |
| **TypeScript** | Static typing for JavaScript | All `.tsx` / `.ts` source files; strict type-checking via `tsc --noEmit` in CI | [typescriptlang.org/docs](https://www.typescriptlang.org/docs/) |
| **Tailwind CSS 3** | Utility-first CSS framework | Layout, spacing, color, dark/light mode tokens; extends default theme in `tailwind.config.js` | [tailwindcss.com/docs](https://tailwindcss.com/docs) |
| **Radix UI** | Accessible headless component primitives | Dialog, AlertDialog, DropdownMenu, Select, Tabs, Toast, Tooltip, Switch, Checkbox, Progress | [radix-ui.com/primitives/docs](https://www.radix-ui.com/primitives/docs/overview/introduction) |
| **@tanstack/react-query v5** | Async server-state management | Fetching, caching, refetching claims, queue status, health checks; `useQuery` / `useMutation` | [tanstack.com/query/latest/docs](https://tanstack.com/query/latest/docs/framework/react/overview) |
| **@tanstack/react-table v8** | Headless table engine | Claims dashboard table with column sorting, multi-row selection, pagination, and filter presets | [tanstack.com/table/latest/docs](https://tanstack.com/table/latest/docs/introduction) |
| **Axios** | HTTP client | Typed `api.ts` client for all 45+ backend endpoints; interceptors for base URL and error handling | [axios-http.com/docs](https://axios-http.com/docs/intro) |
| **React Hook Form** | Form state management | Settings forms, ingest column-mapping wizard, and Guidewire connection test panels | [react-hook-form.com/docs](https://react-hook-form.com/docs) |
| **Zod** | Runtime schema validation | Validates form inputs and API response shapes via `@hookform/resolvers/zod` | [zod.dev](https://zod.dev) |
| **Lucide React** | Icon library | Navigation icons, status indicators, action buttons across all pages | [lucide.dev](https://lucide.dev/guide/) |
| **date-fns** | Date utility library | Formatting `FilingDate`, `created_at`, and `updated_at` timestamps in the UI | [date-fns.org/docs](https://date-fns.org/docs/Getting-Started) |
| **react-dropzone** | File drag-and-drop | Excel/CSV import dropzone on `/upload` ingestion console | [react-dropzone.js.org](https://react-dropzone.js.org/) |
| **tailwindcss-animate** | Tailwind animation plugin | CSS animations for dialogs, toasts, command palette, and dropdown overlays | [github: jamiebuilds/tailwindcss-animate](https://github.com/jamiebuilds/tailwindcss-animate) |
| **class-variance-authority** | Typed variant CSS | Consistent button, badge, and input component variants | [cva.style/docs](https://cva.style/docs) |
| **clsx** | Class name utility | Conditional CSS class merging for dynamic status badges, buttons, and theme classes | [github: lukeed/clsx](https://github.com/lukeed/clsx) |
| **tailwind-merge** | Tailwind class deduplication | Resolves Tailwind CSS class conflicts safely in the `cn` helper utility | [github: dcastil/tailwind-merge](https://github.com/dcastil/tailwind-merge) |

---

### Backend

| Technology | Role in This Solution | How We Use It | Official Documentation |
|---|---|---|---|
| **Python 3.14.7** | Primary backend runtime | All backend services, scrapers, tasks, and tests run under Python 3.14.7 (`.venv` targeting `>=3.14`) | [docs.python.org/3.14](https://docs.python.org/3.14/) |
| **FastAPI 0.141+** | Async REST API framework | 45+ REST endpoints across 7 routers (`claims`, `health`, `ingest`, `matches`, `queue`, `settings`, `audit`); lifespan-managed startup/shutdown | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| **Uvicorn** | ASGI server | Serves FastAPI; `--reload` in development, `--workers` in production; standard extras (websockets, watchfiles) | [uvicorn.org](https://www.uvicorn.org) |
| **Pydantic v2** | Data validation & serialization | Request/response schemas, settings models, environment variable parsing; strict mode for API contracts | [docs.pydantic.dev/latest](https://docs.pydantic.dev/latest/) |
| **pydantic-settings** | Settings management | `Settings` class reads from `backend/.env` with full type validation; supports Redis-cached override layer | [docs.pydantic.dev/latest/concepts/pydantic_settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| **SQLAlchemy 2.0 (async)** | ORM & database abstraction | Async engine + session factory for all CRUD; 5 ORM models (`ClaimRecord`, `ScrapedCourtCase`, `FuzzyMatchResult`, `AuditLog`, `ErrorScreenshot`) | [docs.sqlalchemy.org/en/20](https://docs.sqlalchemy.org/en/20/) |
| **aiosqlite** | Async SQLite driver | Default local development database (`orchestrator.db`) via `sqlite+aiosqlite:///./orchestrator.db` | [github: omnilib/aiosqlite](https://github.com/omnilib/aiosqlite) |
| **asyncpg** | Async PostgreSQL driver | Production PostgreSQL via `postgresql+asyncpg://` URL in Docker/cloud deployments | [magicstack.github.io/asyncpg](https://magicstack.github.io/asyncpg/current/) |
| **Alembic** | Database migrations | Schema versioning; auto-generates migration scripts from SQLAlchemy model changes | [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org/en/latest/) |
| **Celery 5.6+** | Distributed task queue | 4 named queues: `ingest`, `scrapers`, `matcher`, `notifications`; `-P solo` for Windows attended mode | [docs.celeryq.dev](https://docs.celeryq.dev/en/stable/) |
| **Redis 5+** | Message broker & result backend | Celery broker (`/0`), Celery result backend (`/1`), Redis-cached system settings; persistent Docker volume | [redis.io/docs](https://redis.io/docs/latest/) |
| **Celery Flower** | Task monitoring UI | Real-time Celery worker observability dashboard at `:5555`; task history, rates, and worker health | [flower.readthedocs.io](https://flower.readthedocs.io/en/latest/) |
| **Celery Beat** | Scheduled task runner | Periodic retry of failed/stuck claims via `retry_tasks.py` | [docs.celeryq.dev/en/stable/userguide/periodic-tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html) |
| **Playwright for Python** | Browser RPA automation | Launches real Google Chrome with AntiCaptcha extension; automates 8 county court portals | [playwright.dev/python/docs](https://playwright.dev/python/docs/intro) |
| **playwright-stealth** | Bot detection evasion | Applies stealth patches to Playwright page context to bypass portal bot-detection headers | [github: AtuboDad/playwright_stealth](https://github.com/AtuboDad/playwright_stealth) |
| **RapidFuzz** | Fuzzy string matching | C-accelerated `partial_ratio` cascade (Claimant > Insured > Driver) against CaseStyle; threshold=0.6 | [rapidfuzz.github.io/RapidFuzz](https://rapidfuzz.github.io/RapidFuzz/) |
| **pandas** | Data processing | Excel/CSV ingestion, column normalization, 1899-12-30 serial date conversion | [pandas.pydata.org/docs](https://pandas.pydata.org/docs/) |
| **openpyxl** | Excel read/write | Reading uploaded `.xlsx` claim files; writing XLSX export dossiers | [openpyxl.readthedocs.io](https://openpyxl.readthedocs.io/en/stable/) |
| **httpx** | Async HTTP client | Guidewire Insurance Cloud API calls (Bearer/ApiKey/OAuth2); portal reachability pings; async HTTP pooling | [www.python-httpx.org/docs](https://www.python-httpx.org/) |
| **python-multipart** | Form/file upload parsing | Multipart form data parsing for Excel/CSV file uploads in FastAPI endpoints | [github: Kludex/python-multipart](https://github.com/Kludex/python-multipart) |
| **aiofiles** | Async file I/O | Non-blocking file reads/writes for export generation, logo uploads, and scraper cache | [github: Tinche/aiofiles](https://github.com/Tinche/aiofiles) |
| **python-dotenv** | `.env` file loading | Loads `backend/.env` environment variables into process environment on startup | [saurabh-kumar.com/python-dotenv](https://saurabh-kumar.com/python-dotenv/) |

---

### Testing

| Technology | Role in This Solution | How We Use It | Official Documentation |
|---|---|---|---|
| **pytest** | Test runner & framework | 270 unit + integration tests across `backend/tests/` (27 test suites); auto-discovery, parametrize, fixtures | [docs.pytest.org](https://docs.pytest.org/en/stable/) |
| **pytest-asyncio** | Async test support | `asyncio-mode=auto` in `pyproject.toml`; enables `async def test_*` functions and async fixtures | [pytest-asyncio.readthedocs.io](https://pytest-asyncio.readthedocs.io/en/latest/) |
| **pytest-mock** | Mock utilities | `mocker` fixture for patching Playwright, Celery tasks, and external HTTP calls in isolation | [pytest-mock.readthedocs.io](https://pytest-mock.readthedocs.io/en/latest/) |

---

### Build & Development Tools

| Technology | Role in This Solution | How We Use It | Official Documentation |
|---|---|---|---|
| **Ruff** | Python linter & formatter | `ruff check app tests` enforced in CI; selects E, F, W, I, UP rule sets; `0 errors` required | [docs.astral.sh/ruff](https://docs.astral.sh/ruff/) |
| **npm** | Frontend package manager | Manages all Next.js dependencies; `npm install` / `npm run dev` / `npm run build` | [docs.npmjs.com](https://docs.npmjs.com/) |
| **ESLint** | JavaScript/TypeScript linter | `next lint` checks all `.tsx` source files against Next.js recommended rules | [eslint.org/docs](https://eslint.org/docs/latest/) |
| **PostCSS** | CSS transformation | Processes Tailwind CSS directives during `npm run build` | [postcss.org](https://postcss.org/) |
| **Autoprefixer** | CSS vendor prefixing | PostCSS plugin that adds vendor prefixes for cross-browser CSS compatibility | [github: postcss/autoprefixer](https://github.com/postcss/autoprefixer) |
| **PowerShell 5+** | Windows automation shell | `setup.ps1` / `setup_local.ps1` operations console; all 9 menu options including start/stop/test | [learn.microsoft.com/powershell](https://learn.microsoft.com/en-us/powershell/) |

---

### Infrastructure & Deployment

| Technology | Role in This Solution | How We Use It | Official Documentation |
|---|---|---|---|
| **Docker** | Container runtime | `docker-compose.yml` orchestrates PostgreSQL 16, Redis 7, backend API, Celery worker, Flower, Next.js frontend | [docs.docker.com](https://docs.docker.com/) |
| **Docker Compose** | Multi-container orchestration | Hybrid dev mode: `docker compose up -d postgres redis` for infra; Windows host runs API + Celery + Next.js natively | [docs.docker.com/compose](https://docs.docker.com/compose/) |
| **PostgreSQL 16** | Production relational database | All 5 ORM models; `postgresql+asyncpg://` connection string in production; persistent Docker volume | [postgresql.org/docs/16](https://www.postgresql.org/docs/16/) |
| **Redis 7** | In-memory broker & cache | Celery broker (`/0`), result backend (`/1`), system settings cache; persistent Docker volume | [redis.io/docs/latest](https://redis.io/docs/latest/) |

---

### Integrations

| Technology | Role in This Solution | How We Use It | Official Documentation |
|---|---|---|---|
| **Guidewire Insurance Cloud** | Downstream claim management system | `GuidewireClient` in `guidewire_client.py` pushes validated court matches via REST (`Bearer`, `ApiKey`, `Basic`, `OAuth2` auth modes) | [docs.guidewire.com](https://docs.guidewire.com/) |
| **AntiCaptcha Extension v0.83** | CAPTCHA solver | Chrome Manifest v3 extension loaded via `--load-extension` flag; API key synced to LevelDB; solves reCAPTCHA / hCaptcha on court portals | [anti-captcha.com/apidoc](https://anti-captcha.com/apidoc) |
| **Google Chrome** | Browser for RPA automation | Launched via Playwright in Attended (visible) or Unattended (headless) mode; required by Anti-Captcha extension architecture | [developer.chrome.com/docs](https://developer.chrome.com/docs/) |
| **SMTP Email** | Notification delivery | `smtplib` / configurable provider (SSL/TLS/STARTTLS or `local_mock`); sends event notifications for claim failures, Guidewire dispatches, scraper errors | [docs.python.org/3/library/smtplib](https://docs.python.org/3/library/smtplib.html) |
