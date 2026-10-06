# Implementation Plan: County Court Portals Tab Full Verification & Hardening

**Implementation ID:** `IMP-2026-1003-001`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Settings (`/settings`) & County Court Scraper Portals  
**Feature / Issue:** County Court Portals tab full functionality testing & verification, test assertion alignment, and IDE problem resolution  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**Created:** 2026-10-03  
**Last Updated:** 2026-10-03  
**AI Agent:** Antigravity  
**Approval Status:** Approved  
**Approved By:** User  
**Approval Date:** 2026-10-03  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Problem Statement & User Request

The user requested:
> `@[current_problems]`  
> `[UAIC Orchestrator — RPA & Match Engine](http://localhost:3000/settings)`  
> `pls make sure "County Court Portals" tab functionality must be fully working and tested.`

The user recently launched the entire system via Docker Compose (`docker-compose.yml up -d --build`). We need to guarantee:
1. The **"County Court Portals"** tab on `http://localhost:3000/settings` is fully functioning across all interactive controls (8 portal cards, FL/TX state badges, enable/disable toggle switches, configurable search URLs, live HTTP ping tester, external portal launcher, Miami-Dade credentials section with password visibility toggle, login requirement toggle, and configuration persistence).
2. All 8 county court scrapers and their automated test suites pass with 100% compliance.
3. Resolve the cSpell info warnings reported in `@[current_problems]`.
4. Fix the single stale mock assertion in `test_hillsborough_portal.py` that did not account for the V4 single-session browser runner architecture.

---

## 2. Current State & Diagnostic Findings

### 2.1 "County Court Portals" Tab UI & Backend Connectivity
- The frontend route `http://localhost:3000/settings` renders the 7 unified settings tabs, including `{ id: "portals", label: "County Court Portals", icon: Globe }`.
- Under the Portals tab:
  - 8 County Court Scraper cards are dynamically rendered:
    1. Broward County Clerk of Courts (FL)
    2. Hillsborough County Clerk (HOVER Search) (FL)
    3. Miami-Dade County Clerk (OCS Portal) (FL)
    4. Travis County Odyssey Portal (TX)
    5. Dallas County Courts Portal (TX)
    6. Harris County Justice of the Peace (JP) (TX)
    7. Harris County Clerk WebSearch (TX)
    8. Harris County District Clerk (eDocs Search) (TX)
  - Interactive switches control individual bot enablement (`broward_enabled`, `hillsborough_enabled`, etc.).
  - Editable URL input fields update each scraper's base URL.
  - "Ping Portal" button issues an asynchronous POST request to `/api/v1/settings/test-portal`, displaying HTTP status (e.g. `200 OK`), round-trip latency in milliseconds, and error details if unreachable.
  - Miami-Dade specific credentials section provides Username, Password with interactive eye visibility toggle (`text` <-> `password`), and `miami_requires_login` toggle with validation alert.
  - Top "Save Configuration" button sends an atomic PUT/POST to `/api/v1/settings`, incrementing the settings revision number and invalidating cached settings across Celery workers.
- The automated verification script `scripts/verify_portals_tab.py` executed against the live system and passed 100% of end-to-end checks:
  - Tab navigation: PASS
  - 8 Portal cards + state badges: PASS
  - Dallas portal toggle test: PASS
  - Broward live ping test: PASS (`200 OK` | `1795.86 ms`)
  - Miami password visibility toggle: PASS
  - Save configuration: PASS (Settings saved as revision 493)
  - Backend API confirmation: PASS

### 2.2 Test Suite Audit
- Full run of the county court portal test suites (`test_settings_alignment.py`, `test_settings_durable_contract.py`, `test_broward_portal.py`, `test_hillsborough_portal.py`, `test_miami_portal.py`, `test_dallas_portal.py`, `test_travis_portal.py`, `test_harris_jp_portal.py`, `test_harris_cclerk_portal.py`, `test_harris_district_portal.py`):
  - 10 out of 10 test suites passed completely with 100% success rate.
  - Aligned `test_hillsborough_portal.py::test_hillsborough_sequential_unique_names_on_same_tab` to expect 1 pre-open + 1 tab call per unique name = 3 tab calls and 1 runner entry context, matching V4 architecture.

### 2.3 `@[current_problems]` Inspection & Resolution
- All 15 items in `@[current_problems]` were cSpell information messages (`llen`, `tmpl`, `selectinload`, `autouse`, `subflow`, `antigate`, `checkmark`, `CACE`, `maildev`, `nolisten`, `uvicorn`, `asyncpg`, `supersecretdevelopmentkeyfororchestrator`, `loglevel`, `Deduplicator`).
- Whitelisted in `.vscode/settings.json` under `"cSpell.words"`, resolving all 15 notices.

---

## 3. Scope of Work Executed

1. **Aligned `test_hillsborough_portal.py`**:
   - Updated lines 492-496 in `backend/tests/test_hillsborough_portal.py` to match `test_broward_portal.py` (`get_or_create_tab.await_count == 3`, `__aenter__.await_count == 1`).
2. **Configured Workspace Dictionary (`.vscode/settings.json`)**:
   - Added `"cSpell.words"` configuration covering all 15 technical domain terms.
3. **Automated Verification & Testing Executed**:
   - Pytest passed 100% across all 10 portal and settings test suites (171 tests).
   - `scripts/verify_portals_tab.py` passed 100% of end-to-end browser checks.
   - Browser subagent video recording saved to `docs/portals_tab_demo_verified.webp`.
   - Full-page verification screenshot saved to `docs/settings_county_portals_verified.png`.
   - `ruff check app tests` in `backend`: 0 errors.
   - `tsc --noEmit` in `frontend`: 0 errors.
   - `check_ps1_syntax.ps1`: 0 errors across 10 PowerShell scripts.

---

## 4. Verification & Acceptance Criteria Results

- [x] All 8 county court portal test suites pass with 100% success rate in pytest (`test_hillsborough_portal.py` included).
- [x] `scripts/verify_portals_tab.py` runs and verifies all 8 portals, switches, ping functionality, Miami credentials, and settings persistence.
- [x] `ruff check app tests` passes with 0 errors.
- [x] `tsc --noEmit` passes with 0 errors.
- [x] `powershell -File scripts\check_ps1_syntax.ps1` passes with 0 errors.
- [x] `@[current_problems]` resolved with 0 active problems.
- [x] Visual verification screenshots and video recording saved to `docs/`.
