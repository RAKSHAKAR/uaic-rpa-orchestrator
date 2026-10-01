# Implementation Plan: Browser Engine Parity, Hillsborough Search Button Retargeting & Miami-Dade Authentication

**Implementation ID:** `IMP-2026-0926-001`  
**Date:** September 26, 2026  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Human Verification:** Pending  
**Author:** AI Pair Programmer  

---

## 1. Problem Statement & User Findings

The user identified three critical issues with visual evidence:

1. **Browser Engine Ignored (Google Chrome vs. Bundled Chromium):**  
   - In Settings, the user selected **Google Chrome (Attended GUI)** with executable `C:\Program Files\Google\Chrome\Application\chrome.exe`.  
   - However, the orchestrator started bundled **Chromium** (blue icon) rather than respecting the configured engine.  
   - **Requirement:** Playwright must strictly respect settings and seamlessly launch both **Google Chrome** and **Microsoft Edge** without defaulting to bundled Chromium.

2. **Hillsborough County Search Button Target (`https://hover.hillsclerk.com/`):**  
   - The bot was clicking the wrong search button (a top/header search button).  
   - **Requirement:** As shown in Screenshot 2, the bot must specifically click the **green Search button** located directly under the "Date Filed" section (`On or After` / `On or Before`) inside the Party search pane (`#nav-Party`).

3. **Miami-Dade County Clerk Login & Navbar Selection (`https://www2.miamidadeclerk.gov/ocs`):**  
   - The bot was skipping login entirely.  
   - **Requirement:** The bot must authenticate using configured credentials from Settings (`apoorvnigam07@gmail.com` / `Apoorv@12345` via `https://www2.miamidadeclerk.gov/usermanagementservices/Home/LoginOrRegister`), ensure session cookies are established, navigate to the OCS portal, and **always click "Party Name" in the navigation bar** before initiating searches.

---

## 2. Root Cause Analysis & Diagnostic Findings

### Issue 1: Browser Engine Resolution & Fallback to Chromium
- **`BaseCourtScraper` (`backend/app/automation/base.py`):** Lacks `browser_engine` and `chrome_binary_path` arguments. Only accepted `use_chrome: bool = True`. If `use_chrome` was False or `find_chrome_executable()` failed, `executable_path` and `channel` were both None, prompting Playwright to launch bundled Chromium. Edge was completely unsupported.
- **`scraper_tasks.py`:** When assembling `scraper_kw` (lines 200-211), `browser_engine` and `chrome_binary_path` were omitted, depriving individual scrapers of engine awareness.
- **`session_runner.py` (lines 260-267):** Evaluated `if self.chrome_binary_path and os.path.isfile(self.chrome_binary_path):` BEFORE checking `self.browser_engine`. If `chrome_binary_path` was populated in DB, selecting Edge was completely overridden.
- **`browser_manager.py` (line 893):** Checked `elif engine == "msedge":` but failed to match `"edge"`.
- **Playwright Channel Parity:** Playwright provides native channel detection (`channel="chrome"` and `channel="msedge"`). When configured for Chrome or Edge, passing channel ensures official browser binaries launch without falling back to Chromium.

### Issue 2: Hillsborough Search Button Selector Pollution
- In `backend/app/automation/florida/hillsborough.py`:
  ```python
  down_search_btn = page.locator(
      "#nav-Party #btnSubmitPartySearch, "
      "#btnSubmitPartySearch, "
      "#partySearchBtn, "
      "#nav-Party button[type='submit'], "
      "#nav-Party button.btn-success:has-text('Search'), "
      "#nav-Party button:has-text('Search'), "
      "button:has-text('Search'), "  # <-- BUGS HERE
      "form#partySearchForm button:has-text('Search')"
  )
  ```
- Because CSS selectors with commas are evaluated in document order, `"button:has-text('Search')"` matched the top navbar search button before reaching `#btnSubmitPartySearch` at the bottom of the party form.
- The green button under Date Filed in Screenshot 2 corresponds strictly to `#btnSubmitPartySearch` / `#nav-Party button.btn-success`.

### Issue 3: Miami-Dade False "Already Logged In" Detection
- In `backend/app/automation/florida/miami.py`:
  ```python
  is_logged_in = "welcome," in body_lower or "my desk" in body_lower ...
  ```
- Miami-Dade OCS portal's public landing page contains the text *"Welcome to the Miami-Dade County Clerk and Comptroller's Online Court Services..."*.
- Because `"welcome,"` was present on the public page, `ensure_authenticated()` falsely concluded the session was logged in and skipped authentication.
- Without authentication, the user was left on the public gateway where Party search is either unavailable or restricted.
- Furthermore, Miami-Dade requires explicitly clicking **"Party Name"** from the top navbar to reveal the party search input pane.

---

## 3. Detailed Proposed Changes

### Component 1: Unified Browser Engine Resolution (`session_runner.py`, `browser_manager.py`, `base.py`)
1. Create a centralized resolver `resolve_browser_launch_target(engine, custom_path)`:
   - For `engine in ("chrome", "google-chrome")`:
     - If `custom_path` exists and points to `chrome.exe`, use `executable_path=custom_path`.
     - Else if auto-detected via `find_chrome_executable()`, use `executable_path=detected_path`.
     - Else use `channel="chrome"`.
     - **Guarantee:** Never launch bundled Chromium when Chrome is chosen.
   - For `engine in ("edge", "msedge", "microsoft-edge")`:
     - If `custom_path` exists and points to `msedge.exe`, use `executable_path=custom_path`.
     - Else if auto-detected via `find_default_edge_executable()`, use `executable_path=detected_path`.
     - Else use `channel="msedge"`.
     - **Guarantee:** Never launch bundled Chromium when Edge is chosen.
   - For `engine == "chromium"`:
     - Use `executable_path=None, channel=None` (pure bundled Chromium).
2. Update `BaseCourtScraper.__init__` and `BaseCourtScraper.run()` in `base.py`:
   - Accept `browser_engine: str | None = None` and `chrome_binary_path: str | None = None`.
   - Use the unified resolver to guarantee Chrome and Edge parity in standalone scraper runs.
3. Update `backend/app/tasks/scraper_tasks.py`:
   - Pass `browser_engine` and `chrome_binary_path` into `scraper_kw`.

### Component 2: Hillsborough Green Search Button Retargeting (`hillsborough.py`)
1. In `HillsboroughScraper.search_by_party_name`:
   - Replace ambiguous selector with strict scoped selector targeting the green button under Date Filed:
     `#nav-Party #btnSubmitPartySearch, #btnSubmitPartySearch, #nav-Party button.btn-success, #nav-Party button.btn-success:has-text('Search')`.
   - Remove global un-scoped `"button:has-text('Search')"` from selector list.
   - Fallback click via DOM evaluation targeting `#nav-Party #btnSubmitPartySearch`.

### Component 3: Miami-Dade Authentication & Navbar Selection (`miami.py`)
1. Fix `ensure_authenticated()` in `MiamiDadeScraper`:
   - Eliminate weak substring checks (`"welcome,"`, `"my desk"`).
   - Check definitive authentication indicators:
     - Logged out if: `#lnkLogin, a:has-text('Register/Login'), a:has-text('Login')` is visible.
     - Logged in only if: `#lnkLogout, a:has-text('Logout'), a:has-text('Log Out')` is visible.
   - When login is needed:
     - Navigate to `https://www2.miamidadeclerk.gov/usermanagementservices/Home/LoginOrRegister`.
     - Fill User ID / Email: `#userName, input#txtUserName, input[name*='userName' i], #UserName`.
     - Fill Password: `#password, input#txtPassword, input[name*='password' i], #Password`.
     - Click Login: `input[type='submit'][value*='Login' i], #btnLogin, button:has-text('LOGIN')`.
     - Wait for navigation and verify redirect.
     - Navigate back to `https://www2.miamidadeclerk.gov/ocs/`.
2. Strengthen `select_party_search_tab()`:
   - Ensure the navbar link **"Party Name"** (`nav a:has-text('Party Name'), .navbar a:has-text('Party Name'), a.nav-link:has-text('Party Name')`) is clicked.
   - If navbar is in responsive collapsed mode, expand hamburger menu first.
   - Verify that `#txtLastName` and `#txtFirstName` inputs are visible and interactable before proceeding to data entry.

---

## 4. Verification & Testing Plan

### Automated Test Suites
1. **Backend Tests:**
   - Run `pytest --tb=short -q` across all 66 test suites (verify 100% pass rate).
   - Add/update unit tests in `tests/test_browser_matrix.py` for Chrome, Edge, and Chromium channel resolution.
   - Add unit test in `tests/test_hillsborough_portal.py` confirming the green submit button under Date Filed is clicked.
   - Add unit test in `tests/test_miami_portal.py` confirming login trigger and navbar "Party Name" click.
2. **Lint & Type Checks:**
   - Backend: `ruff check app tests` (0 errors).
   - Frontend: `npx tsc --noEmit` (0 errors).
   - PowerShell: `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (0 errors).

---

## 5. User Confirmation Gate

Per governance rules, code modifications will begin immediately upon your confirmation. Please review this plan and let me know if you approve or require adjustments.
