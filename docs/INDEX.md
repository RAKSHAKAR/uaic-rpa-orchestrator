# UAIC Documentation Index & Navigation Map

> **Implementation ID:** `IMP-2026-1031-002`  
> **Authoritative Root Booklet:** [`../README.md`](file:///d:/scratch/Bot_UAIC/README.md)  
> **Status:** Final & Verified  

---

## 1. Core Subsystem Operator Manuals

Located in [`Core Subsystem Operator Manuals/`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/):

| Manual | Description | Link |
|---|---|---|
| **Stage & Status Definitions** | Authoritative lifecycle process states, handoffs, and terminal conditions | [`STAGE_AND_STATUS_DEFINITIONS.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/STAGE_AND_STATUS_DEFINITIONS.md) |
| **Court Portals Guide** | Deep-dive technical specifications for all 8 Florida & Texas court scrapers | [`COURT_PORTALS_GUIDE.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/COURT_PORTALS_GUIDE.md) |
| **Task Queue & Orchestrator** | Celery queues, worker prefetch, task lifecycle, and Auto-Queue runner | [`TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md) |
| **Storage & Retention Guide** | SQLite database schema, retention policies, and asynchronous CSV/Excel exports | [`STORAGE_AND_EXPORTS_GUIDE.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/STORAGE_AND_EXPORTS_GUIDE.md) |
| **APIs & Matching Engine Guide**| REST endpoint contracts, Pydantic schemas, and RapidFuzz matching cascade | [`APIS_AND_MATCHING_ENGINE_GUIDE.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/APIS_AND_MATCHING_ENGINE_GUIDE.md) |
| **Email & Notifications Guide**| SMTP dispatch, dynamic email templates, and automated event trigger matrix | [`EMAIL_AND_NOTIFICATIONS_GUIDE.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/EMAIL_AND_NOTIFICATIONS_GUIDE.md) |
| **Proxy Network Guide** | Residential proxy rotation, latency monitoring, and IP pool management | [`PROXY_NETWORK_GUIDE.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/PROXY_NETWORK_GUIDE.md) |
| **Deployment & Hosting Guide**| Windows local launcher (`setup_local.ps1`) and Docker compose production hosting | [`DEPLOYMENT_AND_HOSTING_GUIDE.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/DEPLOYMENT_AND_HOSTING_GUIDE.md) |
| **Multi-Platform Deployment**| Cloud-agnostic CI/CD standards (Vercel, Render, AWS, Azure, GCP, K8s) | [`DEPLOYMENT.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/DEPLOYMENT.md) |
| **Development Workflow** | Developer onboarding, testing commands, quality gates, and git workflow | [`DEVELOPMENT_WORKFLOW.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/DEVELOPMENT_WORKFLOW.md) |
| **Visual Walkthrough Guide** | Step-by-step visual demonstration linking images and WebP execution recordings | [`WALKTHROUGH.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/WALKTHROUGH.md) |
| **Client Demo Walkthrough** | Curated end-to-end demo flow for business stakeholders and claim operators | [`CLIENT_DEMO_VERIFICATION_WALKTHROUGH.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/CLIENT_DEMO_VERIFICATION_WALKTHROUGH.md) |
| **All 8 Bots Attended Manual**| Step-by-step operator runbook for running attended execution across all 8 bots | [`UAIC_ALL_8BOTS_ATTENDED_EXECUTION_STEP_BY_STEP_MANUAL_V1.md`](file:///d:/scratch/Bot_UAIC/docs/Core%20Subsystem%20Operator%20Manuals/UAIC_ALL_8BOTS_ATTENDED_EXECUTION_STEP_BY_STEP_MANUAL_V1.md) |

---

## 2. Implementation Reports (`IMP-2026-1031-002`)

Located in [`Implementation Reports/`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/):

| No. | Report Title | Subject & Coverage | Link |
|---|---|---|---|
| 1 | **Historical Benchmark Analysis** | Pre-remediation benchmarks vs target metrics; evolution from Power Automate V4 | [`HISTORICAL_BENCHMARK_ANALYSIS.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/HISTORICAL_BENCHMARK_ANALYSIS.md) |
| 2 | **Pre-Remediation System Audit** | Comprehensive baseline audit of entire repository and discovered defects | [`PRE_REMEDIATION_SYSTEM_AUDIT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/PRE_REMEDIATION_SYSTEM_AUDIT.md) |
| 3 | **Repository Architecture & Cleanup** | Inventory of deleted duplicates, consolidated assets, and canonical directory taxonomy | [`REPOSITORY_ARCHITECTURE_AND_CLEANUP_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/REPOSITORY_ARCHITECTURE_AND_CLEANUP_REPORT.md) |
| 4 | **Documentation Consolidation Report** | Documentation taxonomy, structural consolidation, and reference reorganization | [`DOCUMENTATION_CONSOLIDATION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/DOCUMENTATION_CONSOLIDATION_REPORT.md) |
| 5 | **Browser Automation Verification** | Chrome flags, multi-tab single-session orchestration across all 8 bots, and human pacing | [`BROWSER_AUTOMATION_VERIFICATION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/BROWSER_AUTOMATION_VERIFICATION_REPORT.md) |
| 6 | **AntiCaptcha Extension & Config** | Manifest v3 architecture, automated key injection, toolbar pinning, and CAPTCHA workflows | [`ANTICAPTCHA_EXTENSION_AND_CONFIGURATION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/ANTICAPTCHA_EXTENSION_AND_CONFIGURATION_REPORT.md) |
| 7 | **Attended GUI Mode Verification** | Local desktop Chrome and Docker in-browser noVNC (`:6080`) parity verification | [`ATTENDED_GUI_MODE_VERIFICATION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/ATTENDED_GUI_MODE_VERIFICATION_REPORT.md) |
| 8 | **Eight-Portal Execution Report** | Detailed audit and execution logs of all 8 individual bots (3 searches per bot) | [`EIGHT_PORTAL_EXECUTION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/EIGHT_PORTAL_EXECUTION_REPORT.md) |
| 9 | **Combined Eight-Bot Execution Report**| Multi-tab single-session orchestration of all 8 bots together (24 searches total) | [`COMBINED_EIGHT_BOT_EXECUTION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/COMBINED_EIGHT_BOT_EXECUTION_REPORT.md) |
| 10 | **Fuzzy Matching Validation Report** | RapidFuzz 3-tier cascade, unique names deduplication, and confidence scoring | [`FUZZY_MATCHING_VALIDATION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/FUZZY_MATCHING_VALIDATION_REPORT.md) |
| 11 | **Guidewire Integration Verification** | Guidewire payload contract, 9-digit '0' prefix, and retry resilience | [`GUIDEWIRE_INTEGRATION_VERIFICATION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/GUIDEWIRE_INTEGRATION_VERIFICATION_REPORT.md) |
| 12 | **E2E Testing Report** | Unified PowerShell E2E test harness (`run_all_e2e_tests.ps1`), JSON & HTML reports | [`E2E_TESTING_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/E2E_TESTING_REPORT.md) |
| 13 | **Error & Exception Handling Report** | Systematic analysis of 15 failure modes and graceful degradation lifecycles | [`ERROR_AND_EXCEPTION_HANDLING_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/ERROR_AND_EXCEPTION_HANDLING_REPORT.md) |
| 14 | **Performance & Resource Utilization**| System resource utilization, memory limits, and Celery queue throughput | [`PERFORMANCE_AND_RESOURCE_UTILIZATION_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/PERFORMANCE_AND_RESOURCE_UTILIZATION_REPORT.md) |
| 15 | **Post-Remediation Benchmark** | Direct pre vs post remediation benchmark comparison and 100% test sign-off | [`POST_REMEDIATION_BENCHMARK_AND_VERIFICATION.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/POST_REMEDIATION_BENCHMARK_AND_VERIFICATION.md) |
| 16 | **Final Release Readiness Report** | Executive release readiness summary and production deployment sign-off | [`FINAL_RELEASE_READINESS_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/FINAL_RELEASE_READINESS_REPORT.md) |
| 17 | **CAPTCHA Throttling Analysis (v2)**| Advanced WAF challenge mitigation, token injection latencies, and proxy rotation | [`UAIC_CAPTCHA_THROTTLING_ANALYSIS_REPORT_V2.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/UAIC_CAPTCHA_THROTTLING_ANALYSIS_REPORT_V2.md) |
| 18 | **Eight-Portal CAPTCHA Assessment Report** | Comprehensive assessment of CAPTCHA handling, rate limiting, and WAF mitigation across all 8 portals | [`UAIC_EIGHT_PORTAL_CAPTCHA_ASSESSMENT_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Implementation%20Reports/UAIC_EIGHT_PORTAL_CAPTCHA_ASSESSMENT_REPORT.md) / [`Reports/CAPTCHA_ASSESSMENT_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Reports/CAPTCHA_ASSESSMENT_REPORT.md) |

---

## 3. Historical Implementation (Functional Consolidated Records)

Located in [`Historical Implementation/`](file:///d:/scratch/Bot_UAIC/docs/Historical%20Implementation/):

| Area | Functionality & Engineering Work | Link |
|---|---|---|
| **Court Scrapers & Portals** | Multi-party search loops, Power Automate V4 Robin flow alignment, selectors, and schemas | [`PORTAL_AUTOMATION_AND_SCRAPERS_HISTORY.md`](file:///d:/scratch/Bot_UAIC/docs/Historical%20Implementation/PORTAL_AUTOMATION_AND_SCRAPERS_HISTORY.md) |
| **CAPTCHA & Browser Engine** | Anti-Captcha MV3 integration, automatic key injection, toolbar pinning, and multi-solver hooks | [`CAPTCHA_RESOLUTION_AND_BROWSER_ENGINE_HISTORY.md`](file:///d:/scratch/Bot_UAIC/docs/Historical%20Implementation/CAPTCHA_RESOLUTION_AND_BROWSER_ENGINE_HISTORY.md) |
| **Execution Modes & Parity** | Attended visible GUI vs Unattended headless, setup_local.ps1 fix, Docker noVNC (:6080) parity | [`EXECUTION_MODES_AND_ENVIRONMENT_PARITY_HISTORY.md`](file:///d:/scratch/Bot_UAIC/docs/Historical%20Implementation/EXECUTION_MODES_AND_ENVIRONMENT_PARITY_HISTORY.md) |
| **Matching & Guidewire Cloud**| RapidFuzz 3-tier cascade (0.60), 3-column unique names matrix, 1899 DOL base, 9-digit '0' prefix | [`DEDUPLICATION_FUZZY_MATCHING_AND_GUIDEWIRE_HISTORY.md`](file:///d:/scratch/Bot_UAIC/docs/Historical%20Implementation/DEDUPLICATION_FUZZY_MATCHING_AND_GUIDEWIRE_HISTORY.md) |
| **Celery Queue & Telemetry** | 4 isolated queues, auto-queue sequential daemon, failure re-triggering, async streaming exports | [`QUEUE_CELERY_AND_TELEMETRY_PIPELINE_HISTORY.md`](file:///d:/scratch/Bot_UAIC/docs/Historical%20Implementation/QUEUE_CELERY_AND_TELEMETRY_PIPELINE_HISTORY.md) |
| **Frontend UI & Settings** | Next.js 14 App Router, dual-theme tokens (zero OS auto-detect), DB-backed SystemSettings | [`FRONTEND_DASHBOARD_AND_SETTINGS_SYSTEM_HISTORY.md`](file:///d:/scratch/Bot_UAIC/docs/Historical%20Implementation/FRONTEND_DASHBOARD_AND_SETTINGS_SYSTEM_HISTORY.md) |

---

## 4. End-to-End Testing Documentation

- **Manual E2E Testing Guide**: [`../e2e/MANUAL_E2E_TESTING_GUIDE.md`](file:///d:/scratch/Bot_UAIC/e2e/MANUAL_E2E_TESTING_GUIDE.md) — 21-Section comprehensive manual testing protocol.
- **Automated Test Runner**: [`../e2e/run_all_e2e_tests.ps1`](file:///d:/scratch/Bot_UAIC/e2e/run_all_e2e_tests.ps1) — Master test script with HTML & JSON reports.
- **Latest HTML Test Report**: [`../e2e/reports/e2e_test_report.html`](file:///d:/scratch/Bot_UAIC/e2e/reports/e2e_test_report.html) (62 Passed / 0 Failed).

---

## 5. Canonical Media Directories (Untouched)

- **Execution Recordings**: [`recordings/`](file:///d:/scratch/Bot_UAIC/docs/recordings/) — All 9 canonical WebP recordings.
- **Screenshots & Frames**: [`frames/`](file:///d:/scratch/Bot_UAIC/docs/frames/) — Video frames and diagnostic captures.
- **Visual Images**: [`images/`](file:///d:/scratch/Bot_UAIC/docs/images/) — Permanent visual UI diagrams and charts.

---

## 6. Hygiene, CAPTCHA & Performance Reports (`IMP-2026-1102-001`)

- **Code Hygiene, Spell Check Remediation & Performance Optimization Verified Report**: [`2026-11-02_uaic_code_hygiene_spelling_cleanup_and_performance_optimization_verified_report_v1.md`](file:///d:/scratch/Bot_UAIC/docs/2026-11-02_uaic_code_hygiene_spelling_cleanup_and_performance_optimization_verified_report_v1.md)
- **Code Hygiene & Performance Implementation Plan**: [`2026-11-02_uaic_code_hygiene_spelling_cleanup_and_performance_optimization_plan_v1.md`](file:///d:/scratch/Bot_UAIC/docs/2026-11-02_uaic_code_hygiene_spelling_cleanup_and_performance_optimization_plan_v1.md)
- **Authoritative 8-Portal CAPTCHA Assessment Report**: [`Reports/CAPTCHA_ASSESSMENT_REPORT.md`](file:///d:/scratch/Bot_UAIC/docs/Reports/CAPTCHA_ASSESSMENT_REPORT.md)

