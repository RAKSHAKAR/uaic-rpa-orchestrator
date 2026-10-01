# UAIC Claim & RPA Orchestrator — Implementation Plan
## Automatic AntiCaptcha Toolbar Pinning & Configuration on Automation Startup & UI Cleanup

- **Implementation ID:** `IMP-2026-0930-006`
- **Document Type:** Implementation Plan
- **Date:** 2026-09-30
- **Author:** AI Engineering Assistant (Pair Programming with User)
- **Status:** Proposed — Awaiting User Approval
- **Target Version:** `v1`
- **Related Requirements / Prompts:** User request to remove manual "Configure & Pin" button and enforce automatic default AntiCaptcha configuration & toolbar pinning before every automation run.

---

## 1. Executive Summary & Problem Diagnosis

### 1.1 User Problem Statement
In the Settings page under the AntiCaptcha / Browser Automation tab, there was a dedicated card labeled **"Toolbar Pinning & Profile Setup"** featuring a manual **"Configure & Pin"** button (referencing `kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj` and `backend/data/browser_profile/chrome/`).

The user requested:
> *"remove this configured and pin options as it must be by default when automation started always check and do the pinned and confifured anticaptcha always before starting the automation awlyas"*

Requiring human operators to manually locate and click a "Configure & Pin" button before running county court scrapers contradicts the autonomous RPA principle of the orchestrator. If an operator starts a claim automation or the queue runner triggers scraping jobs without having clicked that button, the browser profile might lack modern Chromium toolbar pinning entries in `Default/Preferences`, potentially impairing the Anti-Captcha extension's visibility and operation.

### 1.2 Objective
1. **Remove the manual "Configure & Pin" button and setup action card** from the Settings UI in `frontend/src/app/settings/page.tsx`.
2. **Make AntiCaptcha configuration and toolbar pinning 100% automated by default**:
   - Whenever automation starts (via Celery `orchestrate_court_scrapers_task`, single bot trigger, or direct `SingleSessionBrowserRunner` / `ChromeSession`), the system must automatically verify the extension, synchronize the API key and plugin settings to `config_ac_api_key.js`, and inject modern toolbar pinning (`toolbar.pinned_actions` and `extensions.pinned_extensions`) into the persistent browser profiles across all engines before the browser opens.
   - Isolated multi-concurrency profiles must automatically inherit pinned toolbar preferences.
3. **Preserve full backward compatibility** for existing API endpoints (`POST /api/v1/settings/setup-extension`) and existing test suites (554 tests).

---

## 2. Gap Analysis

| Component | Current State | Required State | Action |
|---|---|---|---|
| **Settings UI** (`frontend/src/app/settings/page.tsx`) | Contains manual "Toolbar Pinning & Profile Setup" card with "Configure & Pin" button (`handleSetupExtension`). | Manual button removed; card replaced by a clean, automated status indicator ("Automated Pre-Flight Pinning: Active") or removed completely. | Remove manual button, update layout cleanly. |
| **Browser Runner** (`backend/app/automation/session_runner.py`) | Pins into profile's Preferences, but does not execute full `ChromeSession.configure_and_pin_profile` across canonical profiles and host profiles before launch. | Automatically calls `ChromeSession.configure_and_pin_profile` before starting Playwright persistent context or isolated worker profiles. | Add automated pre-flight hook in `SingleSessionBrowserRunner.__aenter__`. |
| **ChromeSession** (`backend/app/automation/browser_manager.py`) | Syncs API key to extension dir, but does not automatically write toolbar pinning preferences into `self.profile_to_use` on `start()`. | Automatically calls `self.configure_and_pin_profile` inside `start()` before persistent context launch. | Add automated pre-flight hook in `ChromeSession.start()`. |
| **Scraper Tasks** (`backend/app/tasks/scraper_tasks.py`) | Scraper task launches browser runner directly without logging pre-flight extension configuration. | Checks and records pre-flight automated extension pinning and logs audit event. | Add pre-flight logging & verification in `orchestrate_court_scrapers_task`. |
| **Backend API Contract** (`backend/app/api/v1/endpoints/settings.py`) | `POST /setup-extension` exists and is tested by `test_extension_pinning_and_setup.py`. | Retain endpoint unchanged for API stability and automated tests. | Keep endpoint intact. |

---

## 3. Detailed Technical Design & Implementation Steps

### Step 1: Frontend UI Cleanup (`frontend/src/app/settings/page.tsx`)
1. Remove `isSettingUpExtension` state and `handleSetupExtension` click action from the UI.
2. In the Extension tab grid (lines 3688–3776):
   - Replace the manual action card with an automated status card:
     - **Title:** `Automated Toolbar Pinning & Profile Setup` (with `<ShieldCheck className="w-3.5 h-3.5 text-indigo-500" />` or `<Pin className="w-3.5 h-3.5 text-indigo-500" />`)
     - **Status Badge:** `Auto-Pinned on Startup` (Emerald badge)
     - **Description:** *"AntiCaptcha is automatically verified, configured, and pinned to the browser toolbar before every automation launch."*
     - **Target Directory & Action ID display:** Shows the persistent profile path (`backend/data/browser_profile/...`) and extension action ID (`kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj`) for administrative visibility without requiring manual interaction.
   - NO manual buttons (`Configure & Pin` is completely removed).

### Step 2: Backend Automation Startup Hooks

#### Hook A: `SingleSessionBrowserRunner.__aenter__` (`backend/app/automation/session_runner.py`)
In `SingleSessionBrowserRunner.__aenter__`, immediately after determining `canonical_profile`:
```python
# Always check, configure, and pin AntiCaptcha to browser toolbar before starting automation
from app.automation.browser_manager import ChromeSession
try:
    ChromeSession.configure_and_pin_profile(
        profile_dir=Path(canonical_profile),
        api_key=self.anticaptcha_api_key,
        extension_path=Path(ext_norm) if ext_norm else None,
    )
    logger.info(
        f"[SingleSessionRunner] Pre-flight: AntiCaptcha extension automatically verified, "
        f"configured, and pinned to toolbar at {canonical_profile}"
    )
except Exception as e_pin:
    logger.warning(f"[SingleSessionRunner] Note auto-configuring/pinning extension profile: {e_pin}")
```
For isolated concurrency worker profiles (`self.is_temp_profile = True`):
Ensure `ChromeSession.pin_extension_in_preferences(Path(self.profile_to_use) / "Default" / "Preferences")` is also called so worker profiles are 100% guaranteed pinned.

#### Hook B: `ChromeSession.start()` (`backend/app/automation/browser_manager.py`)
In `ChromeSession.start()`, right after `self.profile_to_use` is resolved:
```python
# Always ensure AntiCaptcha extension is configured and pinned to toolbar BEFORE starting browser
try:
    self.configure_and_pin_profile(
        profile_dir=self.profile_to_use,
        api_key=self.anticaptcha_api_key,
        extension_path=self.extension_path,
    )
    logger.info(f"[ChromeSession] Pre-flight: AntiCaptcha extension automatically configured & pinned at {self.profile_to_use}")
except Exception as e_pin:
    logger.warning(f"[ChromeSession] Note auto-configuring/pinning extension profile: {e_pin}")
```

#### Hook C: `orchestrate_court_scrapers_task` (`backend/app/tasks/scraper_tasks.py`)
Add explicit pre-flight verification log in Celery task execution before browser spin-up:
```python
# Ensure AntiCaptcha is verified, configured, and pinned in profile before automation launches
try:
    from app.automation.browser_manager import ChromeSession, ExtensionManager
    ext_path = ExtensionManager.resolve_extension_path(auto_cfg.chrome_extension_dir)
    engine_key = (auto_cfg.browser_engine or "chrome").lower()
    persistent_dir = ChromeSession.get_persistent_profile_dir(engine_key)
    ChromeSession.configure_and_pin_profile(
        profile_dir=persistent_dir,
        api_key=auto_cfg.anticaptcha_api_key,
        extension_path=ext_path,
    )
    logger.info(f"Pre-flight automated AntiCaptcha setup & toolbar pinning verified for claim {claim.claim_number}")
except Exception as e_pre_ext:
    logger.warning(f"Note during automated pre-flight extension pinning: {e_pre_ext}")
```

---

## 4. Verification & Testing Strategy

1. **Automated Unit & Integration Tests:**
   - Execute `pytest tests/test_extension_pinning_and_setup.py` (ensure pinning into `Default/Preferences` works with 100% pass rate).
   - Execute full backend test suite: `.venv\Scripts\pytest --tb=short -q` (ensure all 554 tests pass).
2. **Code Quality & Linter Checks:**
   - Run Python linter: `.venv\Scripts\ruff check app tests` (0 errors).
   - Run TypeScript compiler: `npx tsc --noEmit` in `frontend` (0 errors).
   - Run PowerShell syntax validator: `scripts/check_ps1_syntax.ps1` (0 errors).
3. **Automated Verification Validation:**
   - Verify that when a browser session starts, `configure_and_pin_profile` executes automatically without any user interaction.
   - Verify that the Settings UI displays the automated status badge without the manual "Configure & Pin" button.
