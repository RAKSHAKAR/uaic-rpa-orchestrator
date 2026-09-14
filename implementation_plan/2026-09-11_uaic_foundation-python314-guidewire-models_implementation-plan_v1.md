# Implementation Plan

Implementation ID:   IMP-2026-0911-005
Project:             UAIC Claim & RPA Orchestrator
Module:              Foundation / Python 3.14.7 / Guidewire Persistence Models / Strict Task Completion Governance
Feature / Issue:     Prompt 01 — Foundation: Python 3.14.7, Environment & Strict Development Task Completion Rules
Document Type:       Implementation Plan
Version:             v1
Status:              Approved
Created:             2026-09-11
Last Updated:        2026-09-11
AI Agent:            Antigravity (Gemini 3.8 Flash High)
Approval Status:     Approved
Approved By:         User
Approval Date:       2026-09-11
AI Verification:     Pending

---

## 1. Problem Statement & Background

The objective of Prompt 01 is to establish the official platform foundation for the UAIC Claim & RPA Orchestrator:
1. **Target Python 3.14.7 Exclusively**:
   - Verify `python --version` returns 3.14.7.
   - Modernize and verify compatibility of all core backend libraries: FastAPI, Uvicorn, Pydantic, SQLAlchemy, Celery, Redis, Playwright, RapidFuzz.
   - Maintain asynchronous architecture for APIs and DB queries while strictly preserving synchronous browser automation where necessary for Anti-Captcha Manifest v3 extension stability.
2. **Mandatory Task Completion Rules**:
   - Codify non-negotiable rules:
     - Never consider a task complete just because code was written.
     - **No Error Left Behind**: Check browser Dev Console and Terminal for errors; fix root causes.
     - **Interruption Recovery**: In the event of crashes, timeouts, or context limits, perform gap analysis and resume from the last successful checkpoint without skipping.
     - **Definition of Done**: Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked.
3. **Technology Stack Documentation**:
   - Maintain a dedicated "Technology Stack & Documentation" section in `README.md` with official documentation links.
4. **Guidewire Integration & Case Filtering Database Entities**:
   - Implement the persistence layer models specified in the prompt ER diagram and SQLAlchemy implementation snippet:
     - `GuidewireActivity` (`guidewire_activities`): Audits all outbound payloads and inbound responses for Guidewire ClaimCenter.
     - `FilteredOutCase` (`filtered_out_cases`): Captures cases matched by Fuzzy Logic but excluded prior to Guidewire.
     - `AutomationSetting` (`automation_settings`): Tracks key/value configuration settings.
     - `SettingsAuditLog` (`settings_audit_logs`): Tracks setting modification audit trails.
     - Integrate relationships with `ClaimRecord` (aliased as `Claim`) and register all entities in `app.models` and `init_db()`.

---

## 2. Current State & Gap Analysis

| Component | Current State | Target State | Gap |
|---|---|---|---|
| **Python Runtime** | System and `.venv` both run `Python 3.14.7`. | Python 3.14.7 verified. | None — Already verified compliant. |
| **Dependencies** | All modern: FastAPI 0.141.1, Uvicorn 0.52.4, Pydantic 2.13.5, SQLAlchemy 2.0.52, Celery 5.6.3, Redis 5.3.1, Playwright 1.62.0, RapidFuzz 3.14.6. | 100% Python 3.14.7 compatible. | None — Fully audited and compatible. |
| **Task Completion Rules** | Documented in `AGENTS.md`, `.agents/skills/uaic-context/SKILL.md`, and `diagnose-plan-confirm-execute/SKILL.md`. | Permanently codified in skills and rules. | Re-verify rules adherence throughout task lifecycle. |
| **Technology Stack Docs** | Section 19 of `README.md` exists with 6 technology tables and official documentation links. | Dedicated Section 19 in `README.md`. | Verified complete and active. |
| **Guidewire & Filter Models** | `backend/app/models/guidewire.py` does NOT exist. `ClaimRecord` lacks `guidewire_activities` and `filtered_cases` relationships. | `GuidewireActivity`, `FilteredOutCase`, `AutomationSetting`, `SettingsAuditLog` implemented with dual SQLite/PostgreSQL compatibility, registered in `app.models`, with test suite. | **Active Gap to Implement**. |

---

## 3. Scope of Work

### In Scope
1. **Create `backend/app/models/guidewire.py`**:
   - `GuidewireActivity`:
     - `id`: UUID Primary Key
     - `claim_id`: UUID Foreign Key referencing `claim_records.id` with `ondelete="CASCADE"`
     - `transaction_id`: UUID Unique Key
     - `claim_number`: String(20), indexed
     - `exposure_number`: String(10), default "001"
     - `request_payload`: JSON / JSONB
     - `response_payload`: JSON / JSONB, nullable
     - `http_status`: Integer, nullable
     - `status`: String(30), default "PENDING", indexed
     - `guidewire_claim_id`: String(50), nullable
     - `guidewire_activity_id`: String(50), nullable, indexed
     - `error_details`: Text, nullable
     - `created_at`: DateTime(timezone=True)
     - `updated_at`: DateTime(timezone=True)
     - Relationship: `claim = relationship("ClaimRecord", back_populates="guidewire_activities")`
   - `FilteredOutCase`:
     - `id`: UUID Primary Key
     - `claim_id`: UUID Foreign Key referencing `claim_records.id` with `ondelete="CASCADE"`
     - `case_number`: String(100)
     - `case_style`: String(500)
     - `case_type`: String(100), nullable
     - `case_status`: String(100), nullable
     - `filing_date`: DateTime, nullable
     - `fuzzy_score`: Float
     - `exclusion_reasons`: JSON / JSONB
     - `created_at`: DateTime(timezone=True)
     - Relationship: `claim = relationship("ClaimRecord", back_populates="filtered_cases")`
   - `AutomationSetting` (`automation_settings`):
     - `key`: String(100) Primary Key
     - `value`: JSON / JSONB
     - `category`: String(50)
     - `updated_at`: DateTime(timezone=True)
     - Relationship: `audit_logs = relationship("SettingsAuditLog", back_populates="setting", cascade="all, delete-orphan")`
   - `SettingsAuditLog` (`settings_audit_logs`):
     - `id`: UUID Primary Key
     - `key`: String(100) Foreign Key referencing `automation_settings.key`
     - `old_value`: JSON / JSONB, nullable
     - `new_value`: JSON / JSONB
     - `updated_by`: String(100)
     - `created_at`: DateTime(timezone=True)
     - Relationship: `setting = relationship("AutomationSetting", back_populates="audit_logs")`
2. **Update `backend/app/models/claim.py`**:
   - Provide `Claim = ClaimRecord` alias for backwards and spec diagram compatibility.
   - Add back-populating relationships to `ClaimRecord`:
     - `guidewire_activities: Mapped[list["GuidewireActivity"]]`
     - `filtered_cases: Mapped[list["FilteredOutCase"]]`
3. **Update `backend/app/models/__init__.py`**:
   - Export `GuidewireActivity`, `FilteredOutCase`, `AutomationSetting`, `SettingsAuditLog`, and `Claim`.
4. **Update `backend/app/core/database.py`**:
   - Ensure `init_db()` registers and creates the new tables in SQLite/PostgreSQL.
5. **Add Automated Test Suite (`backend/tests/test_guidewire_models.py`)**:
   - Test `GuidewireActivity` persistence, transaction_id uniqueness, and relationship to claim.
   - Test `FilteredOutCase` persistence, exclusion_reasons JSON serialization, and cascade deletion.
   - Test `AutomationSetting` and `SettingsAuditLog` relationship and audit history.
   - Test dual SQLite and PostgreSQL JSON/UUID type compatibility.
6. **Execute Full Test & Verification Suite**:
   - `pytest` (270+ tests passing)
   - `ruff check app tests` (0 errors)
   - `npx tsc --noEmit` (0 errors)
   - `check_ps1_syntax.ps1` (0 errors)
   - `docker compose config` (0 errors)

### Out of Scope
- No changes to existing court scrapers or state routing matrices.
- No modifications to frontend claim table or navigation shell.
- No forced asynchronous refactoring of Playwright automation.

---

## 4. Files Expected to Change

| File Path | Action | Description |
|---|---|---|
| `backend/app/models/guidewire.py` | [NEW] | Implements `GuidewireActivity`, `FilteredOutCase`, `AutomationSetting`, and `SettingsAuditLog` models |
| `backend/app/models/claim.py` | [MODIFY] | Adds `Claim = ClaimRecord` alias and `guidewire_activities`, `filtered_cases` relationships |
| `backend/app/models/__init__.py` | [MODIFY] | Exports new models and `Claim` alias in `__all__` |
| `backend/app/core/database.py` | [MODIFY] | Ensures new tables are initialized during `init_db()` |
| `backend/tests/test_guidewire_models.py` | [NEW] | Comprehensive unit tests for all 4 new database entities |
| `README.md` | [MODIFY] | Document new database entities in Section 15 / 19 |

---

## 5. Verification Plan

### Automated Testing
```powershell
# 1. New Guidewire Models Test Suite
cd backend
.venv\Scripts\pytest tests/test_guidewire_models.py -v

# 2. Full Test Suite (270+ tests)
.venv\Scripts\pytest -ra -q

# 3. Backend Linter (0 errors)
.venv\Scripts\ruff check app tests

# 4. Frontend Typecheck (0 errors)
cd ..\frontend
npx tsc --noEmit

# 5. PowerShell AST Verification (0 errors)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"

# 6. Docker Compose Config Validation
docker compose config
```

### Acceptance Criteria
- [ ] `GuidewireActivity` persists outbound/inbound payloads, HTTP status, and activity IDs.
- [ ] `FilteredOutCase` persists cases excluded prior to Guidewire with fuzzy scores and exclusion reasons JSON.
- [ ] `AutomationSetting` and `SettingsAuditLog` persist configuration state and audit history.
- [ ] Deleting a parent `ClaimRecord` cascade-deletes related `GuidewireActivity` and `FilteredOutCase` records.
- [ ] 100% of automated tests pass without regressions.
- [ ] Zero lint, TypeScript, and PowerShell errors.

---

**No application code has been modified yet.**
**Plan saved to:** `implementation_plan/2026-09-11_uaic_foundation-python314-guidewire-models_implementation-plan_v1.md`
Please confirm if you approve this plan so I may begin execution.
