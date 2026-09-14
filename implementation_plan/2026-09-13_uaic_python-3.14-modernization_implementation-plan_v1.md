# Implementation Record

Implementation ID:   IMP-2026-0913-001
Project:             UAIC Claim & RPA Orchestrator
Module:              Backend / Automation
Feature / Issue:     Python 3.14.7 Modernization & Performance Pass
Document Type:       Implementation Plan
Version:             v1
Status:              Approved
Created:             2026-09-13
Last Updated:        2026-09-13
AI Agent:            Antigravity
Approval Status:     Approved
Approved By:         User
Approval Date:       2026-09-13
AI Verification:     Pending

---

# Problem / Request
The backend was developed using modern patterns but requires a comprehensive upgrade and optimization pass specifically targeting **Python 3.14.7**. This involves dependency modernization, leveraging new Python 3.14 features (e.g., enhanced typing, `StrEnum`), optimizing async IO and connection pooling, tuning browser automation startup, and ensuring all database queries are efficient. 

Crucially, **Playwright browser automation must retain its synchronous architecture** where required for Anti-Captcha stability, while other components move to pure async non-blocking operations.

## User Review Required
> [!IMPORTANT]
> - **Dependency Constraints**: We are bumping several dependencies to their latest stable 3.14-compatible versions (e.g., FastAPI, Pydantic, SQLAlchemy). Please confirm you have no restrictions against upgrading these minor/patch versions.
> - **Playwright Sync Requirement**: The plan assumes Playwright automation stays synchronous (in Celery workers) specifically to accommodate the AntiCaptcha extension. We will not force async Playwright.

## Open Questions
> [!WARNING]
> 1. Are there any specific database tables that have grown large in production and require new compound indices beyond the standard `status` and `claim_number` fields?
> 2. Do you want to enforce `uv` over `pip` in the `setup_local.ps1` for significantly faster Python 3.14.7 dependency installations, or stick strictly to standard `pip`?

---

# Gap Analysis & Current State
1. **Python Versioning**: The virtual environment and scripts (`setup_local.ps1`) might be defaulting to any generic `python` command instead of strictly enforcing `py -3.14` or `python3.14`.
2. **Connection Pooling**: `guidewire_client.py` uses `httpx`, but needs to ensure an application-scoped `httpx.AsyncClient` pool rather than instantiating per-request.
3. **Database Performance**: Check for missing indices on high-churn fields like `queue_status`, `updated_at`, and `state`.
4. **Code Modernization**: Transitioning remaining legacy type hints to modern `dict[str, Any]` and utilizing `async context managers` universally.

---

# Dependency Compatibility Matrix

| Library | Current Version | Python 3.14 Compatible? | Latest Suitable Version | Action |
|---|---:|---|---:|---|
| FastAPI | >=0.110.0 | ✅ Yes | >=0.115.0,<1.0.0 | Update safely |
| Uvicorn | >=0.28.0 | ✅ Yes | >=0.30.0,<1.0.0 | Update safely |
| Pydantic | >=2.6.4 | ✅ Yes | >=2.9.0,<3.0.0 | Update safely |
| SQLAlchemy | >=2.0.28 | ✅ Yes | >=2.0.35,<3.0.0 | Update safely |
| Playwright | >=1.42.0 | ✅ Yes | >=1.48.0,<2.0.0 | Update safely |
| httpx | >=0.27.0 | ✅ Yes | >=0.27.2,<1.0.0 | Update safely |
| Pandas | >=2.2.1 | ✅ Yes | >=2.2.3,<3.0.0 | Update safely |
| openpyxl | >=3.1.2 | ✅ Yes | >=3.1.5,<4.0.0 | Update safely |
| Pytest | >=8.0.2 | ✅ Yes | >=8.3.3,<9.0.0 | Update safely |
| Ruff | >=0.3.0 | ✅ Yes | >=0.6.9,<1.0.0 | Update safely |

---

# Proposed Changes

### Configuration & Tooling
#### [MODIFY] `backend/requirements.txt`
- Update dependency constraints to match the compatibility matrix above.
- Ensure `rapidfuzz` and `aiosqlite` are correctly constrained for 3.14.

#### [MODIFY] `setup_local.ps1` & `backend/pyproject.toml`
- Ensure `py -3.14 -m venv .venv` is explicitly invoked on Windows.
- Update `target-version = "py314"` in the Ruff configuration.

---

### Backend Core & Services
#### [MODIFY] `backend/app/services/guidewire_client.py`
- Refactor to accept an injected `httpx.AsyncClient` from an application-level connection pool, rather than creating client sessions ad-hoc, to prevent socket exhaustion and improve throughput.

#### [MODIFY] `backend/app/core/database.py`
- Review the SQLAlchemy async engine creation parameters to ensure `pool_size`, `max_overflow`, and `pool_pre_ping` are appropriately configured for high-concurrency 3.14 environments.

#### [MODIFY] `backend/app/main.py`
- Implement FastAPI lifespan context managers for global initialization of `httpx.AsyncClient` pools and Database connection pools.

---

### Automation & Task Workers
#### [MODIFY] `backend/app/automation/browser_manager.py` (and related adapters)
- Audit tab reuse logic: ensure Chrome is launched *once* per record and tabs are recycled across Florida/Texas site adapters.
- Validate CAPTCHA retry loops use condition-based waiting instead of hard `time.sleep()`.

---

# Verification Plan

### Automated Tests
```powershell
cd backend
.venv\Scripts\pytest -ra -q
.venv\Scripts\ruff check app tests
```

### Manual Verification
1. Verify the API starts and `/api/v1/health/detailed` reports all components green.
2. Execute a single claim push to Guidewire to ensure the HTTP pool functions correctly.
3. Observe Celery logs to ensure browser automation launches successfully with the AntiCaptcha extension and processes a record sequentially.
4. Verify Python environment explicitly reports `3.14.7`.
