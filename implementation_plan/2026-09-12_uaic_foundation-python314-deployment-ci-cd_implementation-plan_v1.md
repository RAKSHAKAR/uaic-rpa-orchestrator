# Implementation Plan

Implementation ID:   IMP-2026-0912-002  
Project:             UAIC Claim & RPA Orchestrator  
Module:              01 - Foundation: Python 3.14.7 Runtime, Modernized Dependencies, Strict Development Governance, Universal CI/CD & Deployment Standards, Guidewire Persistence Entities  
Feature / Issue:     Prompt 01 Verification, Modernization & Universal CI/CD Pipeline Standards  
Document Type:       Implementation Plan  
Version:             v1  
Status:              Awaiting Approval  
Created:             2026-09-12  
Last Updated:        2026-09-12  
AI Agent:            Antigravity (Gemini 3.8 Flash High)  
Approval Status:     Pending  
Approved By:         Pending  
Approval Date:       Pending  
AI Verification:     Complete (100% Automated Testing Suite)  

---

## 1. Problem / Request Summary

The user request (**01 - FOUNDATION: PYTHON 3.14.7 & STRICT DEVELOPMENT RULES**) demands:
1. **Python Runtime & Dependencies**:
   - Verify and exclusively target **Python 3.14.7**.
   - Audit and modernize all dependencies (`FastAPI`, `Uvicorn`, `Pydantic`, `SQLAlchemy`, `Celery`, `Redis`, `Playwright`, `RapidFuzz`) for 3.14.7 compatibility.
   - Preserve asynchronous architecture for APIs and DB queries while maintaining synchronous Playwright RPA execution for Anti-Captcha LevelDB extension stability.
2. **Mandatory Task Completion Rules**:
   - *No Error Left Behind*: Dev Console and Terminal inspections, fixing root causes.
   - *Interruption Recovery*: Gap analysis and resume from last checkpoint.
   - *Definition of Done*: Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked.
3. **Technology Stack Documentation**:
   - Dedicated "Technology Stack & Documentation" section in `README.md` with official documentation links for Frontend, Backend, Testing, Build, Infrastructure, and Integrations.
4. **Deployment Architecture, CI/CD & Hosting Standards**:
   - Universal CI/CD & deployment compatibility (GitHub Actions, GitLab CI/CD, Bitbucket, Jenkins, CircleCI, Docker Compose, Swarm, Kubernetes, AWS, Azure, GCP, DigitalOcean, VPS).
   - Frontend Hosting (Vercel, Netlify): `NEXT_PUBLIC_API_BASE_URL` dynamic handling, standalone `frontend/Dockerfile` and `frontend/docker-compose.yml`.
   - Backend Hosting (Render, Heroku, VPS): dynamic `$PORT` routing (`0.0.0.0:$PORT`), standalone `backend/Dockerfile` and `backend/docker-compose.yml`, isolated `backend/requirements.txt`.
   - Infrastructure & VPS: Unified `root/docker-compose.yml` orchestrating PostgreSQL, Redis, MailDev, backend, Celery workers, frontend.
   - Zero Coupling Rule: Strict HTTP/REST API boundary between frontend and backend.
5. **Guidewire Integration & Case Filtering Database Entities**:
   - Verify existing implementations of `GuidewireActivity`, `FilteredOutCase`, `AutomationSetting`, and `SettingsAuditLog` models in `backend/app/models/guidewire.py`, their relationships in `backend/app/models/claim.py`, and ER diagram in `README.md`.

---

## 2. Current State & Verification Audit

Before preparing this plan, a comprehensive read-only audit of the existing codebase was conducted:

| Audit Item | Command / Check | Result | Compliance |
|---|---|---|---|
| **Python Runtime** | `python --version; .venv\Scripts\python --version` | `Python 3.14.7` (both system and virtualenv) | PASS (100%) |
| **Backend Dependencies** | Audit `backend/requirements.txt` & `backend/pyproject.toml` | All modern 3.14 compatible packages (FastAPI 0.110+, SQLAlchemy 2.0+, Celery 5.3.6+, RapidFuzz 3.6+) | PASS (100%) |
| **Backend Unit Tests** | `.venv\Scripts\pytest -ra -q` | 280 passed across 28 test suites in 276.85s (0 failures) | PASS (100%) |
| **Backend Linter** | `.venv\Scripts\ruff check app tests` | All checks passed (0 errors) | PASS (100%) |
| **Frontend Typecheck** | `npx tsc --noEmit` | Clean exit (0 errors) | PASS (100%) |
| **Frontend Production Build** | `npm run build` | 11 routes compiled, static and dynamic prerendered cleanly | PASS (100%) |
| **PowerShell Syntax** | `scripts\check_ps1_syntax.ps1` | 0 syntax errors across all 7 `.ps1` scripts | PASS (100%) |
| **Root Docker Compose** | `docker compose config` | Valid configuration (PostgreSQL, Redis, MailDev, Backend, Celery, Frontend) | PASS (100%) |
| **Browser Dev Console** | Subagent inspection at `http://localhost:3000/` | Zero fatal React/client runtime errors | PASS (100%) |
| **Guidewire Persistence Models** | `backend/app/models/guidewire.py` | `GuidewireActivity`, `FilteredOutCase`, `AutomationSetting`, `SettingsAuditLog` fully implemented with dual SQLite/Postgres types | PASS (100%) |

---

## 3. Gap Analysis

While the foundation is overwhelmingly complete and passing all 280 tests, the following targeted enhancements will elevate the project to production perfection:

1. **Direct Backend Execution Fallback**:
   - `backend/app/main.py` currently lacks a standard `if __name__ == "__main__":` entrypoint that honors `$PORT` and `$HOST` when someone executes `python -m app.main` directly outside uvicorn CLI or container entrypoints.
2. **Frontend Environment Variable Documentation Template**:
   - `frontend/.env.example` is missing. Adding it explicitly defines `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_API_URL` for Vercel/Netlify developers.
3. **Universal CI/CD Automation Pipeline**:
   - `.github/workflows/ci.yml` is missing. Creating a clean, cloud-agnostic GitHub Actions CI workflow provides automated continuous integration (backend linting with ruff, unit testing with pytest, frontend type-checking with tsc, and production build verification) across standard Ubuntu runners.
4. **Universal Deployment Documentation in `DEPLOYMENT.md`**:
   - Expand `DEPLOYMENT.md` to detail multi-cloud provider compatibility (AWS EC2/ECS/EKS, Azure App Service/AKS, GCP Cloud Run/GKE, DigitalOcean, Kubernetes manifests, and Docker Swarm) alongside CI/CD matrices.

---

## 4. Proposed Changes

### Backend (`backend/`)
#### [MODIFY] [`backend/app/main.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/main.py)
- Add `if __name__ == "__main__":` block dynamically binding to `os.environ.get("PORT", settings.PORT)` and `os.environ.get("HOST", settings.HOST)` using `uvicorn.run`.

### Frontend (`frontend/`)
#### [NEW] [`frontend/.env.example`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/.env.example)
- Provide standard template with `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1` and `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`.

### CI/CD & Deployment (`.github/`, root)
#### [NEW] [`.github/workflows/ci.yml`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/.github/workflows/ci.yml)
- Universal GitHub Actions CI workflow executing:
  - Job 1: `backend-ci` (Python 3.14, install requirements, run `ruff check`, run `pytest -ra -q`)
  - Job 2: `frontend-ci` (Node.js 18, npm install, `npx tsc --noEmit`, `npm run build`)
#### [MODIFY] [`DEPLOYMENT.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/DEPLOYMENT.md)
- Detail the Universal CI/CD matrix and cloud-agnostic hosting across AWS, Azure, GCP, DigitalOcean, Kubernetes, Docker Swarm, and Vercel/Render.

---

## 5. Verification Plan

### Automated Verification:
1. `backend/.venv\Scripts\ruff check app tests` (must pass with 0 errors).
2. `backend/.venv\Scripts\pytest -ra -q` (all 280 tests must pass).
3. `cd frontend && npx tsc --noEmit` (must pass with 0 errors).
4. `cd frontend && npm run build` (must compile cleanly).
5. `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (0 syntax errors).
6. `docker compose config` (valid composition).
7. Standalone backend launch verification: `python -m app.main --help` or dry-run.

---

## 6. User Review & Approval Required

> [!IMPORTANT]
> In strict compliance with the **Diagnose-Plan-Confirm-Execute Governance Skill**, no source code modifications will be executed until the user explicitly reviews and confirms this implementation plan.
