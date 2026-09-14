# UAIC Claim & RPA Orchestrator: Master Requirement & Functionality Inventory

**Implementation ID:** IMP-2026-0913-MASTER
**Date:** 2026-09-13
**Phase:** PART 0 - Baseline / Inventory / Gap Analysis

## Objective
Establish a single cumulative master requirement and functionality baseline before executing the phased sequence. This checklist will be continuously updated through Parts 1-6 to ensure NO requirement is lost, skipped, or forgotten.

---

## 1. Foundation & Environment (Part 1)

| Requirement / Feature | Source | Existing Status | V4 Status | Gap/Issue | Required Action | Impl. Status | Test Status | Regression | Final Verif. |
|---|---|---|---|---|---|---|---|---|---|
| Python 3.14.7 Pinning | 01_Foundation | Verified in pyproject | N/A | None | Audit & modernize dependencies | Pending | Pending | Pending | Pending |
| Mandatory Task Rules | 01_Foundation | N/A | N/A | AI Process Gap | Enforce No Error Left Behind & Interruption Recovery | Pending | Pending | Pending | Pending |
| CI/CD & Deployment Agnostic | 01_Foundation | Dockerfiles exist | N/A | Verify independence | Ensure zero tight coupling between frontend/backend | Pending | Pending | Pending | Pending |
| Guidewire DB Entities | 01_Foundation | Implemented | N/A | Verify schema accuracy | Audit `guidewire_activities`, `filtered_out_cases`, `settings_audit_log` | Pending | Pending | Pending | Pending |
| Preserve Sync Playwright | AGENTS.md | Async partially used? | Sync | Verify CAPTCHA stability | Ensure Playwright is sync if async breaks Anti-Captcha | Pending | Pending | Pending | Pending |

## 2. Enterprise Setup Console & Cleanup (Part 2)

| Requirement / Feature | Source | Existing Status | V4 Status | Gap/Issue | Required Action | Impl. Status | Test Status | Regression | Final Verif. |
|---|---|---|---|---|---|---|---|---|---|
| Console Options [1]-[9], [M] | 02_Setup_Console | Exists | N/A | Interactive launch, MailDev explicit stop missing | Refine `setup_local.ps1` to handle MailDev & browser selection | Pending | Pending | Pending | Pending |
| Dependency Purge [5] | 02_Setup_Console | Exists | N/A | Ensure safety | Safely purge `.venv`, `node_modules`, `.next` | Pending | Pending | Pending | Pending |
| Live Diagnostics & Monitor [7][9] | 02_Setup_Console | Exists | N/A | Suppressed exceptions | Fix `PytestUnraisableExceptionWarnings`, show real health | Pending | Pending | Pending | Pending |
| Enterprise Data Cleanup [3] | 02_Setup_Console | Basic exist | N/A | Missing time-scope, cascade | Implement Time-Based, Multi-select, Dry-Run, Cascade delete | Pending | Pending | Pending | Pending |

## 3. Architecture, UI/UX & Orchestrator (Part 3)

| Requirement / Feature | Source | Existing Status | V4 Status | Gap/Issue | Required Action | Impl. Status | Test Status | Regression | Final Verif. |
|---|---|---|---|---|---|---|---|---|---|
| Responsive UI & Full Viewport | 03_UI_UX / Manual | `max-w` constraints exist | N/A | Fixed widths present | Remove `max-w-7xl/6xl`, implement full width `max-w-none` | Pending | Pending | Pending | Pending |
| Mobile Navigation & Footer | 03_UI_UX | Standard nav | N/A | Missing mobile footer | Implement fixed bottom nav for mobile | Pending | Pending | Pending | Pending |
| Dark/Light Mode Parity | 03_UI_UX / Manual | Implemented | N/A | Contrast issues in tables | Audit visibility for all components | Pending | Pending | Pending | Pending |
| Page Specific Fixes (Audit, Monitor, Health) | ManualPrompt | Basic components | N/A | Missing sorting, filters, exports | Add multi-select, bg export popup, sort/filter to tables | Pending | Pending | Pending | Pending |
| Claim Detail (View Stages, Exports) | ManualPrompt | Buttons broken/mismatched | N/A | Incomplete CSV/Excel export | Fix stages, sync Top/Bottom export data, remove PDF from bottom | Pending | Pending | Pending | Pending |
| Deprecated Form Fields | 03_UI_UX / Manual | UI removed | N/A | Backend still maps | Remove `loss_location_city/county`, `garaging_city/state` from DB/Schemas | Pending | Pending | Pending | Pending |
| Scraped Cases Table Redesign | 03_UI_UX / Manual | Standard table | N/A | Grouping/Filing Date missing | Group by Portal Link, fix Filing Date capture, global search, max 500 | Pending | Pending | Pending | Pending |
| State Routing Logic | AGENTS.md / 03 | Hardcoded arrays | Exists | Strict routing required | FL=3, TX=5, Cross=8. Miami-Dade is FL. | Pending | Pending | Pending | Pending |

## 4. Master Scraping Engine & CAPTCHA (Part 4)

| Requirement / Feature | Source | Existing Status | V4 Status | Gap/Issue | Required Action | Impl. Status | Test Status | Regression | Final Verif. |
|---|---|---|---|---|---|---|---|---|---|
| Unique Name Extractor API | ManualPrompt | Power Automate logic | API exists | Exists but verify | Verify exact legacy parity | Pending | Pending | Pending | Pending |
| Strict Sequential Processing | 04_Scraping / Manual | Loops | V4 Loops | Needs exact name-by-name | Process ONE unique name across all applicable tabs sequentially | Pending | Pending | Pending | Pending |
| Default Portal URLs | 04_Scraping / Manual | Some out of date | V4 defined | URLs mismatch | Update exact base URLs for all 8 portals | Pending | Pending | Pending | Pending |
| Human-Like Navigation | ManualPrompt | Direct link? | Navigates from home | Direct API/Links used? | Ensure navigation starts from Portal Home page | Pending | Pending | Pending | Pending |
| CAPTCHA Resolution Wait | 04_Scraping / Manual | Basic wait | DOM Token Check | Missing/skipped wait logic | Implement strictly waiting for Anti-Captcha verification (120s max) | Pending | Pending | Pending | Pending |
| Extension One-Time Setup & Pin | Master Prompt | Reloads per run | Configured once | Not persisting / pinned | Dedicated setup workflow in Settings to configure and PIN extension | Pending | Pending | Pending | Pending |
| Non-Blocking / Error Screenshot | 04_Scraping / Manual | Throws error | Logs and continues | Stops workflow on error | Capture screenshot to `.\backend\screenshots`, log, and continue | Pending | Pending | Pending | Pending |
| Extract All Available Data | ManualPrompt / AGENTS | Extract basic | Extracts all | Missing fields (e.g. Filing Date) | Verify paginated scraping, grab all fields matching PowerAutomate | Pending | Pending | Pending | Pending |

## 5. Email & Notification Engine (Part 5)

| Requirement / Feature | Source | Existing Status | V4 Status | Gap/Issue | Required Action | Impl. Status | Test Status | Regression | Final Verif. |
|---|---|---|---|---|---|---|---|---|---|
| Celery/Redis Async Email | 05_Email | Sync sending | PowerAutomate send | Synchronous path | Implement async Celery task for `notification_email` | Pending | Pending | Pending | Pending |
| Config UI & Dynamic Templates | 05_Email / Manual | Backend `.env` | Env vars | Need UI exposure (no cleartext) | Add SMTP settings to UI, support variable substitution | Pending | Pending | Pending | Pending |
| Delivery Idempotency & DB Log | 05_Email / Manual | Logs to DB? | N/A | Duplicate emails / No history | Idempotency keys, Outbound Notification Delivery History in UI/DB | Pending | Pending | Pending | Pending |

## 6. End-to-End Validation & Documentation (Part 6)

| Requirement / Feature | Source | Existing Status | V4 Status | Gap/Issue | Required Action | Impl. Status | Test Status | Regression | Final Verif. |
|---|---|---|---|---|---|---|---|---|---|
| Attended vs Unattended Parity | 06_Validation | Headless default | Attended default | Modes behave differently | Ensure 100% parity; no reliance on active desktop sessions | Pending | Pending | Pending | Pending |
| All 8 Portal Tests | Master Prompt | Pinging | Full runs | Extraction unverified | Test live scraping workflows on all 8 portals | Pending | Pending | Pending | Pending |
| Full Doc Reconciliation | 06_Validation | Fragmented | N/A | Multiple loose files | Consolidate to `master-implementation-plan.md`, `master-gap-analysis.md`, `master-walkthrough.md`, `README.md` | Pending | Pending | Pending | Pending |
| Final Audit | Master Prompt | N/A | N/A | Ensure zero omissions | Cross-check this checklist against actual implementation | Pending | Pending | Pending | Pending |

---

## 7. Cumulative Execution Control

- **Pre-Flight (Completed):** PART 0 - Baseline Checklist Established.
- **Next Step:** PART 1 - Foundation & Environment. The next prompt must utilize this checklist to guide and record implementation.
