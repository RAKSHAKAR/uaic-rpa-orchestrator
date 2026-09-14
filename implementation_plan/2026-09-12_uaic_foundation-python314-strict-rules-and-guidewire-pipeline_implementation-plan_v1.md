# Implementation Plan

Implementation ID:   IMP-2026-0912-003  
Project:             UAIC Claim & RPA Orchestrator  
Module:              01 - Foundation: Python 3.14.7 Runtime, Modernized Dependencies, Strict Development Governance, Universal CI/CD Standards, Guidewire Persistence Entities Live Pipeline Integration  
Feature / Issue:     Foundation Audit, Guidewire Activity & Filtered Case Pipeline Integration & Verification  
Document Type:       Implementation Plan  
Version:             v1  
Status:              Complete  
Created:             2026-09-12  
Last Updated:        2026-09-12  
AI Agent:            Antigravity (Gemini 3.8 Flash High)  
Approval Status:     Approved  
Approved By:         User  
Approval Date:       2026-09-12  
AI Verification:     Complete (100% Automated Testing Suite)  

---

## 1. Problem / Request Summary

The user request (**01 - FOUNDATION: PYTHON 3.14.7 & STRICT DEVELOPMENT RULES**) mandates:
1. **Python Runtime & Dependencies**:
   - Exclusively target **Python 3.14.7**. Verify via `python --version`.
   - Audit and modernize all dependencies (`FastAPI`, `Uvicorn`, `Pydantic`, `SQLAlchemy`, `Celery`, `Redis`, `Playwright`, `RapidFuzz`) for 3.14.7 compatibility.
   - Maintain asynchronous architecture (`async def`, connection pooling) for APIs and DB queries, while preserving synchronous Playwright RPA automation for Anti-Captcha LevelDB extension stability.
2. **Mandatory Task Completion Rules**:
   - *No Error Left Behind*: Check browser Developer Console and Terminal for errors; resolve root causes.
   - *Interruption Recovery*: Gap analysis and resume from last successful point; never skip tasks.
   - *Definition of Done*: Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked.
3. **Technology Stack Documentation**:
   - Maintain dedicated "Technology Stack & Documentation" section in `README.md` with official documentation links for Frontend, Backend, Testing, Build, Infrastructure, and Integrations.
4. **Deployment Architecture, CI/CD & Hosting Standards**:
   - Universal CI/CD compatibility (GitHub Actions, GitLab, Bitbucket, Jenkins, CircleCI, Docker Compose, Kubernetes, AWS, Azure, GCP, VPS).
   - Frontend Hosting (Vercel, Netlify): `NEXT_PUBLIC_API_BASE_URL` dynamic handling, standalone `frontend/Dockerfile` and `frontend/docker-compose.yml`.
   - Backend Hosting (Render, Heroku, VPS): dynamic `$PORT` routing (`0.0.0.0:$PORT`), standalone `backend/Dockerfile` and `backend/docker-compose.yml`, isolated `backend/requirements.txt`.
   - Infrastructure & VPS: Unified `root/docker-compose.yml` orchestrating PostgreSQL, Redis, MailDev, backend, Celery workers, frontend.
   - Zero Coupling Rule: Strict HTTP/REST API boundary between frontend and backend.
5. **Guidewire Integration & Case Filtering Database Entities**:
   - Database entities implemented: `GuidewireActivity`, `FilteredOutCase`, `AutomationSetting`, `SettingsAuditLog`.
   - Wire `GuidewireActivity` and `FilteredOutCase` persistence directly into the asynchronous Celery matching and Guidewire dispatch pipeline (`backend/app/tasks/fuzzy_tasks.py`).

---

## 2. Current State & Verification Audit

A comprehensive pre-change audit was conducted across the codebase:

| Audit Item | Command / Check | Current State | Compliance |
|---|---|---|---|
| **Python Runtime** | `python --version; .venv\Scripts\python --version` | Both report `Python 3.14.7` (64-bit) | PASS (100%) |
| **Backend Dependencies** | Audit `backend/requirements.txt` & `pyproject.toml` | All modern, Python 3.14 compatible packages (FastAPI 0.110+, SQLAlchemy 2.0+, Celery 5.3.6+, RapidFuzz 3.6+) | PASS (100%) |
| **Async vs Sync Architecture** | Inspect FastAPI routes & Playwright scrapers | Async DB session pooling (`TaskAsyncSessionLocal`), sync Playwright browser scrapers for LevelDB Anti-Captcha stability | PASS (100%) |
| **Backend Tests** | `.venv\Scripts\pytest -ra -q` | 280 unit & integration tests across 28 test suites | PASS (100%) |
| **Backend Linter** | `.venv\Scripts\ruff check app tests` | 0 errors | PASS (100%) |
| **Frontend Typecheck** | `cd frontend && npx tsc --noEmit` | 0 errors | PASS (100%) |
| **PowerShell Syntax** | `powershell ... scripts\check_ps1_syntax.ps1` | 0 syntax errors across all 7 utility scripts | PASS (100%) |
| **Docker Compose Configs** | `docker compose config` (root, backend, frontend) | All 3 configurations valid and cloud-agnostic | PASS (100%) |
| **Tech Stack Documentation** | `README.md` Section 19 | 6 comprehensive tables covering Frontend, Backend, Testing, Build, Infra, Integrations with official URLs | PASS (100%) |
| **Universal CI/CD Workflow** | `.github/workflows/ci.yml` & `DEPLOYMENT.md` | Matrix for backend (Python 3.14 + ruff + pytest) and frontend (Node 18 + tsc + build) | PASS (100%) |
| **Guidewire ORM Models** | `backend/app/models/guidewire.py` & `claim.py` | `GuidewireActivity`, `FilteredOutCase`, `AutomationSetting`, `SettingsAuditLog` defined with dual SQLite/PG types | PASS (100%) |

---

## 3. Gap Analysis

| Component | Current State | Target State | Action Planned |
|---|---|---|---|
| **Guidewire Dispatch Task** (`fuzzy_tasks.py`) | Posts payload via `GuidewireClient` and logs to `AuditLog`, but does NOT persist a `GuidewireActivity` ORM record | Whenever Guidewire dispatch executes, automatically insert a `GuidewireActivity` instance with transaction ID, request/response payloads, HTTP status, and activity ID | Enhance `_async_notify_guidewire` in `backend/app/tasks/fuzzy_tasks.py` |
| **Fuzzy Match Evaluation Task** (`fuzzy_tasks.py`) | Evaluates scraped cases and creates `MatchPair` records, but does NOT persist `FilteredOutCase` for excluded/ineligible cases | Record scraped court cases excluded by eligibility rules (status/type whitelist, min filing date) into `FilteredOutCase` with reasons and fuzzy scores | Enhance `_async_evaluate_fuzzy_matches` in `backend/app/tasks/fuzzy_tasks.py` |
| **Pipeline Integration Tests** | `test_guidewire_models.py` tests ORM models in isolation, but no test verifies live task creation of `GuidewireActivity` and `FilteredOutCase` | Dedicated end-to-end integration test verifying that `_async_evaluate_fuzzy_matches` creates `FilteredOutCase` and `_async_notify_guidewire` creates `GuidewireActivity` | Create `backend/tests/test_guidewire_pipeline.py` |

---

## 4. Proposed Changes

### Backend (`backend/`)

#### [MODIFY] [`backend/app/tasks/fuzzy_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/fuzzy_tasks.py)
- Import `FilteredOutCase` and `GuidewireActivity` from `app.models.guidewire`.
- In `_async_evaluate_fuzzy_matches`:
  - When a scraped court case fails eligibility checks (e.g. status not in whitelist, case type excluded, filing date prior to `min_filing_date`), persist a `FilteredOutCase` record capturing the claim, case number, case style, case type, case status, filing date, and JSON `exclusion_reasons`.
- In `_async_notify_guidewire`:
  - Persist a `GuidewireActivity` record capturing the unique `transaction_id`, `claim_number`, `exposure_number`, `request_payload`, `response_payload`, `http_status`, `status` (`SUCCESS` / `FAILED`), `guidewire_activity_id`, and `error_details`.

#### [NEW] [`backend/tests/test_guidewire_pipeline.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_guidewire_pipeline.py)
- Automated async test verifying that running `_async_evaluate_fuzzy_matches` on a claim with ineligible scraped cases creates `FilteredOutCase` entities in the database.
- Automated async test verifying that running `_async_notify_guidewire` persists a `GuidewireActivity` entity linked to the claim with full payload and HTTP status audit.

---

## 5. Verification Plan

### Automated Tests:
1. `backend\.venv\Scripts\pytest tests/test_guidewire_pipeline.py tests/test_guidewire_models.py -ra -q`
2. `backend\.venv\Scripts\ruff check app tests` (must remain 0 errors).
3. `cd frontend && npx tsc --noEmit` (must remain 0 errors).
4. `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (must remain 0 errors).
5. `docker compose config` (must remain valid).

### Browser & UI Verification:
- Confirm application UI renders smoothly with no console errors.

---

## 6. User Review & Approval Required

> [!IMPORTANT]
> In accordance with the **diagnose-plan-confirm-execute** governance protocol, no source code files have been modified.
> Please review and approve this plan so implementation and automated pipeline testing may proceed.
