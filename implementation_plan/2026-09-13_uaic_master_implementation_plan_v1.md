# Master Implementation Plan: UAIC Claim & RPA Orchestrator Finalization

**Implementation ID:** IMP-2026-0913-001
**Date:** 2026-09-13

## 1. Overview
This plan dictates the final actions required to bring the UAIC Claim & RPA Orchestrator codebase into 100% compliance with the provided Prompt Sequence, resolving the gaps identified in the Master Gap Analysis.

## 2. Open Questions / User Review Required
None. The required actions are explicit bug fixes and cleanup tasks mandated by the prompts.

## 3. Proposed Changes

### 3.1 Backend: Remove Deprecated Location Fields
The fields `loss_location_city`, `loss_location_county`, `garaging_city`, and `garaging_state` will be entirely purged from the backend:

- **`backend/app/models/claim.py`**: Remove the four SQLAlchemy columns.
- **`backend/app/schemas/claim.py`**: Remove the fields from Pydantic schemas.
- **`backend/app/schemas/queue.py`**: Remove the fields from queue schemas.
- **`backend/app/api/v1/endpoints/claims.py` & `queue.py`**: Remove references during creation, updates, and CSV export.
- **`backend/app/services/excel_parser.py` & `backend/app/tasks/ingest_tasks.py`**: Remove mapping fallback logic for these fields.
- **`backend/seed_*.py`**: Remove these fields from synthetic test data seeders.

### 3.2 Automated Testing & E2E Validation
Execute the full 5-tier diagnostic suite to ensure parity and stability:
- **Pytest**: `pytest --tb=short -q` (Must pass all 300+ tests).
- **Ruff**: `ruff check app tests` (Must yield 0 errors).
- **TypeScript**: `npx tsc --noEmit` (Must yield 0 errors).
- **PowerShell AST**: `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (Must yield 0 errors).

### 3.3 Master Documentation Consolidation
- Update `README.md` to reflect any final architectural tweaks.
- Generate `master-walkthrough.md` capturing test results and final deployment readiness.

## 4. Verification Plan
We will rely on the comprehensive Pytest suite. Since we are removing fields from the Database model, we will verify that the SQLite database migrations (or auto-creation) execute without error, and all API endpoints respond with 200 OK without referencing the deprecated keys.
