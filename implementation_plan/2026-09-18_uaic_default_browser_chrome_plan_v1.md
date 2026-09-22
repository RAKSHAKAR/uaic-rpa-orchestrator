# Implementation Plan: Universal Default Browser Engine Standardization to Google Chrome

**Implementation ID:** `IMP-2026-0918-007`  
**Target:** Standardize default browser engine from Chromium to Google Chrome (`chrome`) across backend schemas, services, automation session runners, frontend UI defaults, and database persistence  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Date:** 2026-09-18  

---

## 1. Executive Summary & Problem Definition

### User Directive
> *"default browser always be chrome not charomium or edge"*

Previously, the orchestrator defaulted to `"chromium"` across Pydantic schemas, runtime service initialization, browser manager constructors, and frontend fallbacks. Although the orchestrator supports Google Chrome, Chromium, and Microsoft Edge, the default out-of-the-box configuration across all layers should strictly be **Google Chrome** (`"chrome"`).

---

## 2. Scope of Changes

### A. Backend Settings Schemas (`backend/app/schemas/settings.py`)
- In `AutomationSettings`:
  - Change `browser_engine: str = Field(default="chrome", description="Browser engine: chrome (Google Chrome, default), chromium (Playwright bundled), or msedge")`.
- In `BrowserTestRequest` & `BrowserTestResponse`:
  - Change `browser_engine: str | None = "chrome"`
  - Change `browser_engine: str = "chrome"`
- In `FleetTestRequest`:
  - Change `browser_engine: str | None = Field(default="chrome", description="Browser engine override (chrome, chromium, msedge)")`

### B. Settings Service & Default Configuration (`backend/app/services/settings_service.py`)
- In `get_default_settings()`:
  - Change `browser_engine="chrome"` (was `"chromium"`).
- Update current runtime settings in Redis / SQLite database from `"chromium"` to `"chrome"` so the running orchestrator immediately adopts Chrome.

### C. Automation Session Constructors (`backend/app/automation/`)
- In `browser_manager.py`:
  - `ChromeSession.__init__`: Change default `browser_engine: str = "chrome"`.
  - Line 408: Fallback changed from `(browser_engine or "chromium")` to `(browser_engine or "chrome")`.
  - `ExtensionManager.configure_extension_in_profile`: Change default `browser_engine: str = "chrome"`.
- In `session_runner.py`:
  - `SingleSessionBrowserRunner.__init__`: Fallback changed to `(browser_engine or "chrome")`.

### D. Settings API Endpoints (`backend/app/api/v1/endpoints/settings.py`)
- Update fallback expressions:
  - `getattr(auto_cfg, "browser_engine", "chrome")` in `test_browser_endpoint` (line 370).
  - `getattr(auto_cfg, "browser_engine", "chrome")` in `test_fleet_endpoint` (line 539).
  - `auto_cfg.browser_engine or "chrome"` in `setup_extension_endpoint` (line 762).
  - `auto_cfg.browser_engine or "chrome"` in `check_extension_endpoint` (line 804).

### E. Frontend UI & Types (`frontend/`)
- In `frontend/src/app/settings/page.tsx`:
  - Update all UI fallback expressions from `settings.automation.browser_engine || "chromium"` to `settings.automation.browser_engine || "chrome"`.
  - Update display labels, initial state, and test payload defaults to `"chrome"`.
- In `frontend/src/types/index.ts`:
  - Ensure type definitions and default comments reflect `"chrome"` as the primary default.

### F. Backend Test Suite Adjustments (`backend/tests/`)
- Update `tests/test_settings_alignment.py`:
  - Update `assert reset_settings.automation.browser_engine == "chrome"` (was `"chromium"`).
- Update `tests/test_browser_manager.py`:
  - Update `session_default = ChromeSession(); assert session_default.browser_engine == "chrome"` (was `"chromium"`).

---

## 3. Verification Plan

### Automated Test Suites
1. `cd backend; .venv\Scripts\pytest tests/test_settings_alignment.py tests/test_browser_manager.py tests/test_browser_matrix.py tests/test_fleet_concurrency.py -q`
2. Full backend regression: `cd backend; .venv\Scripts\pytest --tb=short -q` (all 453 tests)
3. Python lint: `cd backend; .venv\Scripts\ruff check app tests`
4. TypeScript check: `cd frontend; npx tsc --noEmit`
5. Frontend lint: `cd frontend; npm run lint`
6. PowerShell syntax: `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"`

### Visual & Browser Verification
- Launch browser subagent to verify `http://localhost:3000/settings` Tab 3 displays **Google Chrome** as the pre-selected radio option by default.
- Capture visual verification screenshot in `implementation_plan/Images/`.
