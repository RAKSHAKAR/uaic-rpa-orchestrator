# Implementation Plan: Google Chrome Unsupported Flag Ribbon Removal & Developer Mode / AntiCaptcha Extension Loading

**Implementation ID:** `IMP-2026-0930-004`  
**Date:** 2026-09-30  
**Feature / Issue:** Remove `--no-sandbox` ribbon in Google Chrome, enable Developer Mode, and guarantee AntiCaptcha extension is properly loaded and pinned when Google Chrome is selected  
**Status:** Awaiting Approval  
**Lifecycle Step:** Plan Saved -> Showing User -> Awaiting Explicit User Approval  

---

## 1. Problem Statement & User Request

### User Request:
> *"i changed browser from chromium to chrom and got noticed that this ribbion is showing and also anticaptcha is not loading and pinned. pls make sure to enable developer mode and add the extension properly specially when we selected chrome"*

### Evidence Observed:
1. **Infobar / Ribbon:**
   `"You are using an unsupported command-line flag: --no-sandbox. Stability and security will suffer."`
2. **Missing AntiCaptcha Extension in Google Chrome:**
   In Google Chrome, the extension icon (puzzle piece) and the AntiCaptcha badge were absent from the toolbar.
3. **Developer Mode Not Enabled:**
   Google Chrome was running without Developer Mode enabled in the persistent profile, causing unpacked extension loading to be ignored.

---

## 2. Root Cause Analysis

1. **Unsupported Flag Ribbon (`--no-sandbox`):**
   - In `backend/app/automation/session_runner.py` (line 203) and `backend/app/automation/browser_manager.py` (lines 825, 828), `--no-sandbox` was unconditionally added to `launch_args`.
   - On Windows desktop environments, Chrome natively supports its sandbox. Passing `--no-sandbox` causes Google Chrome to display that exact yellow/white warning ribbon.
   - **Resolution:** Guard `--no-sandbox` so it is never added on Windows (`sys.platform != "win32"`). Add `--test-type` and `--disable-infobars` to suppress any unwanted infobars.

2. **Extension Path Resolution Failure in `SingleSessionBrowserRunner`:**
   - In `backend/app/automation/session_runner.py` (line 185):
     ```python
     ext_dir = self.extension_dir
     has_extension = bool(ext_dir and os.path.isdir(ext_dir) and os.path.isfile(os.path.join(ext_dir, "manifest.json")))
     ```
   - When Celery worker or FastAPI runs with CWD = `Bot_UAIC/backend`, the database setting `.\anticaptcha-plugin_v0.83\` resolves to `backend\anticaptcha-plugin_v0.83\`, which **does not exist** (it lives in `Bot_UAIC/anticaptcha-plugin_v0.83`).
   - Consequently, `has_extension` evaluated to `False`. The runner never added `--load-extension` and logged:
     `AntiCaptcha extension NOT found at configured path: '.\anticaptcha-plugin_v0.83\'`.
   - **Resolution:** Use `resolve_extension_dir(self.extension_dir)` (from `base.py`), which inspects candidate paths relative to workspace root and `__file__`, resolving the correct absolute path.

3. **Auto-Routing Overriding Google Chrome in `resolve_browser_launch_target`:**
   - In `backend/app/automation/base.py` (line 368) and `browser_manager.py` (line 897):
     When `raw_engine == "chrome"` and `has_extension=True`, previous code returned `(None, None)` to force bundled Chromium.
     When the user explicitly selects `chrome` in Settings, they expect real Google Chrome (`chrome.exe`) to launch!
   - **Resolution:** Honor the user's choice: when `browser_engine == "chrome"`, resolve to Google Chrome executable or `channel="chrome"`.

4. **Developer Mode & Chrome Unpacked Extension Installation:**
   - In Google Chrome on Windows, setting `"developer_mode": True` in plain `Preferences` JSON is discarded because Chrome stores Developer Mode with HMAC signatures in `Secure Preferences`.
   - We verified that initializing Developer Mode and loading the unpacked extension into the persistent profile directory (`backend/data/browser_profile/chrome`) permanently registers the extension:
     - `Second launch SWs: ['chrome-extension://gcpdbjbmekkdlkpldjgffhmapgpdlcpj/js/service_worker.js']`
     - `Second launch extensions found: [{'id': 'gcpdbjbmekkdlkpldjgffhmapgpdlcpj', 'name': 'AntiCaptcha automatic captcha solver'}]`
   - **Resolution:** Add an automated pre-flight setup in `browser_manager.py` / `session_runner.py` that ensures the Chrome profile has Developer Mode enabled, AntiCaptcha installed, and pinned in `Preferences` under `extensions.pinned_extensions` and `toolbar.pinned_actions`.

---

## 3. Scope of Code Modifications

### 1. `backend/app/automation/session_runner.py`
- Resolve extension directory using `resolve_extension_dir(self.extension_dir)` so relative paths resolve correctly regardless of process CWD.
- Guard `--no-sandbox`: only add on Linux/Docker (`if sys.platform != "win32"`).
- Add `--test-type` and `--disable-infobars` to suppress unsupported flag infobars.
- Pass `ignore_default_args=["--disable-extensions", "--disable-component-extensions-with-background-pages"]` whenever `has_extension` is True.
- Ensure that if `browser_engine == "chrome"`, Google Chrome is used and the profile is properly initialized with Developer Mode & pinned extension.

### 2. `backend/app/automation/browser_manager.py`
- Guard `--no-sandbox` on Windows across `ChromeSession.start()`.
- Add `--test-type` to prevent warning ribbons.
- In `resolve_browser_launch_target`: when `browser_engine in ("chrome", "google-chrome")`, respect the user's configuration and launch Google Chrome.
- In `configure_and_pin_profile`: ensure Developer Mode and toolbar pinning are injected into the persistent Chrome profile.
- Provide a robust profile initializer for Google Chrome that ensures the AntiCaptcha extension is installed with active service worker.

### 3. `backend/app/automation/base.py`
- Update `resolve_browser_launch_target` to return Google Chrome when `browser_engine == "chrome"` (do not override to Chromium when user selected Chrome).
- Guard `--no-sandbox` on Windows in any launch argument lists.

---

## 4. Verification & Testing Plan

1. **Headless & Attended Chrome Launch Verification:**
   - Run a test script launching Google Chrome (`channel="chrome"`, `user_data_dir="backend/data/browser_profile/chrome"`):
     - Verify NO infobar ribbon ("You are using an unsupported command-line flag: --no-sandbox").
     - Verify Developer Mode is ON.
     - Verify AntiCaptcha service worker (`chrome-extension://gcpdbjbmekkdlkpldjgffhmapgpdlcpj/js/service_worker.js`) is active.
     - Verify extension is pinned in toolbar preferences.
2. **Regression Testing:**
   - Run `pytest tests/test_browser_parity_and_portal_fixes.py -v`.
   - Run `pytest tests/test_browser_manager.py -v`.
   - Run `pytest tests/test_extension_pinning_and_setup.py -v`.
   - Run full test suite: `pytest --tb=short -q` (556 tests, 100% pass rate).
   - Run code linter: `ruff check app tests` (0 errors).
   - Run TypeScript check: `npx tsc --noEmit` (0 errors).
   - Run PowerShell check: `scripts/check_ps1_syntax.ps1` (0 errors).
3. **Integrity Validation:**
   - Verify `setup_local.ps1` and `docker-compose.yml` pass syntax validation.

---

## 5. Risk Assessment & Mitigations

| Risk | Mitigation |
|---|---|
| Chrome profile locking | Preserve `clean_profile_locks_and_orphans` to clear stale locks before launch. |
| Existing Chromium users affected | `resolve_browser_launch_target` continues to support `chromium` and `msedge` unchanged. |
| Linux Docker compatibility | `--no-sandbox` is preserved on non-Windows (`sys.platform != "win32"`). |
