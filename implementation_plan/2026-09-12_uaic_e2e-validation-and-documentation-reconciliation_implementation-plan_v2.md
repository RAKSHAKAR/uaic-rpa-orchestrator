# Implementation Plan — 06: End-to-End Validation & Documentation Reconciliation

```text
========================================================================================
Implementation ID:   IMP-2026-0912-002
Project:             UAIC Claim & RPA Orchestrator
Module:              E2E Automation Parity / Forensic Documentation Reconciliation
Document Type:       Detailed Implementation Plan
Version:             v2.0
Status:              Approved
Created Date:        2026-09-12
Last Updated:        2026-09-12
AI Agent:            Antigravity (Google DeepMind)
Approval Status:     Approved
Approved By:         User
Approval Date:       2026-09-12
Governing Skill:     .agents/skills/diagnose-plan-confirm-execute/SKILL.md
Working Directory:   implementation_plan/
========================================================================================
```

---

## 1. Executive Summary & Problem Statement

The user has requested the complete execution of **06 - End-to-End Validation & Documentation Reconciliation**:
1. **Attended vs. Unattended Parity (E2E Testing)**:
   - Execute a complete mock claim workflow in **Attended Mode** (visible system default browser GUI). Ensure the Anti-Captcha extension loads and resolves challenges visibly/correctly.
   - Execute the exact same workflow in **Unattended Mode** (Headless).
   - **Absolute Rule**: Everything that successfully works in Attended Mode MUST work in Unattended Mode. Automation cannot rely on manual clicks, active desktop sessions, or pre-opened browsers.
   - Verify all 8 county scrapers extract data, paginate correctly, generate accurate fuzzy matches, and submit correctly formatted payloads to Guidewire.
2. **Forensic Documentation Reconciliation**:
   - Perform a full forensic reconciliation of all project documentation without blindly deleting historical documentation. Compare Original Prompts -> Historical Docs -> Actual Code.
   - Consolidate all implementation data into three authoritative files:
     1. `master-implementation-plan.md` (v3.0)
     2. `master-gap-analysis.md` (v3.0)
     3. `master-walkthrough.md` (v3.0)
   - Ensure `README.md` acts as the living technical booklet covering the full stack, routing, APIs, workflows, and operations.
   - Validate `.gitignore` files to ensure `.env`, `.venv`, `node_modules`, `__pycache__`, etc., are excluded safely.

---

## 2. Current State vs. Expected State

| Capability / Subsystem | Current State | Target Expected State | Status / Gap |
|---|---|---|---|
| **Browser Runner Headless Extensions** | `browser_manager.py` implements `--headless=new` with `context_headless=False` for service worker activation. However, `session_runner.py` and `base.py` pass `headless=is_headless`, which in Playwright invokes legacy `--headless` and disables extensions. | Standardize `session_runner.py` and `base.py` to use `context_headless = False` with `--headless=new` whenever headless mode is requested with an active extension, guaranteeing 100% headless extension loading parity across all runners. | **ENHANCEMENT REQUIRED** |
| **Attended vs. Unattended E2E Test** | `scripts/verify_attended_unattended_parity_e2e.py` and backend test `test_attended_unattended_parity.py` verify parity across state routing, schema, fuzzy cascade, and Guidewire payloads. | Execute and record live end-to-end workflow verification in both Attended and Unattended modes, validating that extracted cases, fuzzy scores, and Guidewire payloads are 100% identical. | **VERIFICATION READY** |
| **8 County Scrapers & Strict Schemas** | All 8 scrapers implemented in `backend/app/automation/florida/` and `texas/`. Harris JP and Harris Clerk strictly omit `CaseType`. | Re-verify that all 8 scrapers enforce strict output schemas and pagination across both Attended and Unattended modes. | **VALIDATED** |
| **Documentation Consolidation** | `master-implementation-plan.md`, `master-gap-analysis.md`, and `master-walkthrough.md` reflect state up to 2026-09-11 (v2.0). | Update to v3.0 (2026-09-12), incorporating recent features: Dynamic Email & Notification Engine (AE-01 to AE-38), Human Navigation & Captcha Compliance, test suite expansion (280 tests), and complete requirement traceability. | **RECONCILIATION REQUIRED** |
| **README Technical Booklet** | `README.md` has 869 lines covering architecture and routes, but requires updates for recent notification templates/rules endpoints, test counts, and attended/unattended parity guarantees. | Update `README.md` comprehensively to preserve all existing detail and add new architectural guarantees. | **BOOKLET UPDATE REQUIRED** |
| **.GitIgnore Validation** | Root `.gitignore`, `backend/.gitignore`, and `frontend/.gitignore` exist. | Run `git check-ignore` and verify that all secrets, `.env`, `.venv`, caches, and build artifacts are excluded cleanly. | **VALIDATION READY** |

---

## 3. Scope of Work

### In Scope
1. **Runner Headless Extension Parity**:
   - Update `SingleSessionBrowserRunner` in `backend/app/automation/session_runner.py` to ensure `context_headless = False` with `launch_args.append("--headless=new")` when `is_headless and has_extension`.
   - Update `BaseCourtScraper.run_search` in `backend/app/automation/base.py` with the same logic.
2. **Attended vs. Unattended E2E Parity Execution**:
   - Run `scripts/verify_attended_unattended_parity_e2e.py` and capture execution evidence.
   - Verify 1:1 parity between Attended Mode and Unattended Mode across all 8 portals.
3. **Forensic Documentation Reconciliation**:
   - Update `implementation_plan/master-implementation-plan.md` to v3.0.
   - Update `implementation_plan/master-gap-analysis.md` to v3.0.
   - Update `implementation_plan/master-walkthrough.md` to v3.0.
4. **README.md Synchronization**:
   - Update `README.md` with complete documentation on Attended vs. Unattended parity, notification engine endpoints, templates, rules, and updated test suite telemetry.
5. **.GitIgnore Verification**:
   - Audit `.gitignore`, `backend/.gitignore`, and `frontend/.gitignore` against all files in the repository.
6. **Full Automated Test Suite**:
   - Run pytest (280+ tests), ruff check, tsc, and powershell syntax validator.

### Out of Scope
- No modification of existing database schemas or table keys (`fl_jsonbody_*`, `te_jsonbody_*`).
- No modification of the business logic (state routing, 1899-12-30 serial dates, 9-digit Guidewire claim number prefix).
- No deletion of historical documentation in `implementation_plan/`.

---

## 4. File-Level Action Plan

### [MODIFY] `backend/app/automation/session_runner.py`
- **Change**: In `SingleSessionBrowserRunner.__aenter__`, when `is_headless and has_extension`: set `context_headless = False` while appending `--headless=new` to `launch_args`, and pass `context_headless` to `launch_persistent_context`.
- **Reason**: Playwright internally enforces legacy `--headless` if `headless=True` is passed to `launch_persistent_context`, which strips unpacked Chrome extensions. Using `--headless=new` with `headless=False` allows the browser process to run silently in the background (unattended) with full unpacked extension and service worker support.

### [MODIFY] `backend/app/automation/base.py`
- **Change**: In `BaseCourtScraper.run_search`, adopt the same `context_headless = False` pattern when `is_headless and has_extension`.
- **Reason**: Ensures standalone portal tests in headless mode have 100% extension parity with attended mode.

### [MODIFY] `implementation_plan/master-implementation-plan.md`
- **Change**: Upgrade to v3.0. Reconcile all requirements from prompts 01 through 06, incorporating recent dynamic email notification engine capabilities, 8 county portal human navigation & CAPTCHA compliance, attended vs unattended parity, and 280-test verification matrix.
- **Reason**: Mandated by prompt 06 as the authoritative master implementation document.

### [MODIFY] `implementation_plan/master-gap-analysis.md`
- **Change**: Upgrade to v3.0. Reconcile all gaps from GAP-01 through GAP-28, documenting recent resolutions (AE-01 through AE-38, email delivery receipts, headless extension parity) and remaining external infrastructure provisioning items.
- **Reason**: Mandated by prompt 06 as the authoritative master gap analysis document.

### [MODIFY] `implementation_plan/master-walkthrough.md`
- **Change**: Upgrade to v3.0. Document end-to-end user experience, interactive operations console, browser execution modes, and full claim lifecycle.
- **Reason**: Mandated by prompt 06 as the authoritative master walkthrough document.

### [MODIFY] `README.md`
- **Change**: Update with latest test counts (280 tests), email engine API routes, and attended vs unattended parity guarantees.
- **Reason**: Keeps README as the authoritative living technical booklet of the entire project.

---

## 5. Verification Plan

### Automated Tests
1. **Parity Harness**:
   ```bash
   backend\.venv\Scripts\python scripts\verify_attended_unattended_parity_e2e.py
   ```
2. **Backend Unit & Integration Tests**:
   ```bash
   cd backend && .venv\Scripts\pytest --tb=short -q
   ```
3. **Backend Linter**:
   ```bash
   cd backend && .venv\Scripts\ruff check app tests
   ```
4. **Frontend TypeScript**:
   ```bash
   cd frontend && npx tsc --noEmit
   ```
5. **PowerShell AST Syntax**:
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```
6. **GitIgnore Validation**:
   ```bash
   git status --ignored
   ```

---

## 6. Acceptance Criteria

- [ ] Complete mock claim workflow executed in Attended Mode with Anti-Captcha extension loaded.
- [ ] Exact same workflow executed in Unattended Mode (Headless) with Anti-Captcha extension loaded.
- [ ] 1:1 Parity verified across all 8 county scrapers, pagination, fuzzy matches, and Guidewire payloads (0 discrepancies).
- [ ] `master-implementation-plan.md` updated to v3.0 with complete requirement traceability.
- [ ] `master-gap-analysis.md` updated to v3.0 with full historical gap audit.
- [ ] `master-walkthrough.md` updated to v3.0 with comprehensive system walkthrough.
- [ ] `README.md` updated as the living technical booklet.
- [ ] `.gitignore` files validated to ensure `.env`, `.venv`, `node_modules`, `__pycache__`, etc., are safely excluded.
- [ ] Full automated testing suite passing (280+ tests, 0 ruff errors, 0 tsc errors, 0 ps1 errors).
