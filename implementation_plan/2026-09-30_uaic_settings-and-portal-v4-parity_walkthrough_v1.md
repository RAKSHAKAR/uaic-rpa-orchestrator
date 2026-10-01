# Walkthrough: Settings Full Functionality & Power Automate V4 Court Portals Parity

Implementation ID:   IMP-2026-0930-001  
Project:             UAIC Claim & RPA Orchestrator  
Module:              Settings Engine & Browser RPA Fleet (`frontend/src/app/settings/`, `backend/app/automation/`, `backend/app/tasks/`)  
Document Type:       Walkthrough  
Version:             v1  
Status:              Complete  
Created:             2026-09-30  
Last Updated:        2026-10-01  
AI Agent:            Antigravity  
AI Verification:     Complete (100% Automated Testing Suite)  

---

## 1. Overview & Purpose

This walkthrough details how the UAIC Claim & RPA Orchestrator achieves full runtime functional alignment with `http://localhost:3000/settings` and exact operational parity with the Power Automate Desktop V4 RPA complete solution across all 8 supported Florida and Texas county court portals.

---

## 2. Settings Functionality & Dynamic Runtime Propagation

### 2.1 Settings Management on `/settings`
1. **Dynamic Fetching & Persistence**:
   - The settings console at `http://localhost:3000/settings` communicates with `GET /api/v1/settings` and `POST /api/v1/settings`.
   - Settings are persisted into Redis key `uaic:system:settings:v4` by `settings_service.py` with local fallback.
   - When Celery workers scrape claims, `scraper_tasks.py` calls `await get_system_settings_async()` to retrieve active configuration dynamically.

2. **Validation Bounds Alignment**:
   - `captcha_wait_seconds` numeric input configured with `min="5"`, `max="300"`, and default `120s`.
   - Prevents FastAPI HTTP 422 errors and allows the full 5-minute timeout range supported by backend Pydantic models.

3. **Runtime Automation Parameters (`scraper_kw`)**:
   - Every scraper instance receives:
     - `captcha_wait_seconds` (Max CAPTCHA timeout)
     - `max_attempts` (Max retry attempts with page reload)
     - `reload_backoff_seconds` (Cooldown before reload)
     - `timeout_ms` (Page navigation timeout)
     - `browser_engine` (`chrome`, `chromium`, `msedge`)
     - `chrome_binary_path`
     - `chrome_extension_dir` & `anticaptcha_api_key`
     - `typing_speed_mode` (`turbo`, `fast`, `balanced`, `cautious`)
     - `typing_delay_ms`, `action_pacing_ms`, and `stealth_clicks`

---

## 3. CAPTCHA Resolution Wait & Immediate Submit Execution Contract

### 3.1 Maximum Wait Timeout (Not a Fixed Wait)
- In `backend/app/automation/base.py`, `detect_and_handle_captcha` runs an active polling loop up to `wait_sec` (default 120s):
  ```python
  poll_intervals = max(int(wait_sec * 2), 10)
  for it in range(poll_intervals):
      await _safe_wait_timeout(page, 500)
      frames_to_poll = [page] + [f for f in getattr(page, "frames", []) if f is not page]
  ```
- In each 500ms interval, both the root document (`page`) and all child frames are inspected for:
  1. AntiCaptcha solver status badge (`.antigate_solver`, `.solved_flag`, `data-status="solved"`).
  2. reCAPTCHA token (`textarea[name="g-recaptcha-response"]`).
  3. Cloudflare Turnstile token (`input[name*="turnstile"]`, `window.turnstile.getResponse()`, `window.__turnstileInitParameters`).
  4. hCaptcha token (`textarea[name="h-captcha-response"]`).
- **Immediate Return**: The exact millisecond any token or solved indicator is found, `detect_and_handle_captcha` logs success and immediately returns `True`. It does **not** linger or wait out the remaining time.

### 3.2 Immediate Search Submission
- Across all 8 portal scrapers (`broward.py`, `hillsborough.py`, `miami.py`, `dallas.py`, `travis.py`, `harris_jp.py`, `harris_cclerk.py`, `harris_district.py`):
  - When `captcha_ok` is returned, the loop breaks immediately.
  - The submit button is clicked using dual Playwright click and direct DOM JavaScript click dispatch (`focus()` + `click()`).

### 3.3 CAPTCHA Timeout & Retry Workflow
- If the CAPTCHA is not resolved within `captcha_wait_seconds` (120s):
  1. Current attempt stops.
  2. Page reloads (`page.reload(...)`).
  3. Cooldown delay `reload_backoff_seconds` is observed.
  4. Automation restarts from the required beginning point (e.g. Party Name tab or search form).
  5. Search data is re-entered.
  6. The loop continues up to `max_attempts`. If all attempts fail, the bot logs failure and resets tab state cleanly.

---

## 4. Power Automate V4 County Court Portals Exact Parity

### 4.1 Florida Portals (3 Sites)
1. **Broward County (`broward.py`)**:
   - Navigation: Base URL `/Web2` ➔ Case Search ECA.
   - Selectors: `#personSearchForm`, `#lastName`, `#firstName`, `#filingDateOnOrAfterP`.
   - Submit: `#PersonSearchResults`.
   - Session Timeout: Pop-up `button:has-text('Continue session')` handled automatically.
   - Glossary rows: Excluded.
   - Output Schema: 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).

2. **Hillsborough County (`hillsborough.py`)**:
   - Navigation: `/html/case/caseSearch.html#nav-Party-tab`.
   - Selectors: `#nav-Party-tab`, `#spFirstName`, `#spLastName`, `#spDateFiledAfter` (readonly attribute stripped for standard entry).
   - Submit: `#btnSubmitPartySearch`.
   - Search Criteria Modal: Closed automatically via `#messageClose`.
   - Output Schema: 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).

3. **Miami-Dade County (`miami.py`)**:
   - Navigation: User Management login redirect handled; credentials filled from settings; transitions to OCS portal.
   - Selectors: `#txtFirstName`, `#txtLastName`, `#filingDateFrom`.
   - Table View: Verified and enabled via `#btnTableView`.
   - Output Schema: 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).

### 4.2 Texas Portals (5 Sites)
4. **Dallas County (`dallas.py`)**:
   - Odyssey Smart Search: `#caseCriteria_SearchCriteria`.
   - Submit: `#btnSSSubmit`.
   - CaseStyle: Standardized.
   - Output Schema: 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).

5. **Travis County (`travis.py`)**:
   - Odyssey Smart Search: `#caseCriteria_SearchCriteria`.
   - Submit: `#btnSSSubmit`.
   - Output Schema: 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).

6. **Harris County JP (`harris_jp.py`)**:
   - Odyssey Smart Search: `#caseCriteria_SearchCriteria`.
   - Submit: `#btnSSSubmit`.
   - **STRICT SCHEMA RULE**: Output dictionary contains strictly 4 fields: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`. **NO `CaseType`**.

7. **Harris County Clerk (`harris_cclerk.py`)**:
   - Menu navigation: Courts ➔ County Civil (`CourtSearch.aspx?CaseType=Civil`).
   - Selectors: `txtLastName`, `txtFirstName`, `txtFrom2` (DOL date).
   - Submit: `btnSearch`.
   - **STRICT SCHEMA RULE**: Output dictionary contains strictly 4 fields: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`. **NO `CaseType`**.

8. **Harris District Clerk (`harris_district.py`)**:
   - Navigation: Search Our Records (`Search.aspx`).
   - Selectors: `txtPartyName` / `partyLastName`, `txtPartyStartDate`, `txtPartyEndDate`.
   - Submit: `btnPartySearch`.
   - Output Schema: 5 Fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`).

---

## 5. Verification Commands

```bash
# Backend Automated Tests (100% Pass)
cd backend && .venv\Scripts\pytest --tb=short -q

# Backend Linter (0 errors)
cd backend && .venv\Scripts\ruff check app tests

# Frontend TypeScript (0 errors)
cd frontend && npx tsc --noEmit

# PowerShell Scripts AST Syntax (0 errors)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```
