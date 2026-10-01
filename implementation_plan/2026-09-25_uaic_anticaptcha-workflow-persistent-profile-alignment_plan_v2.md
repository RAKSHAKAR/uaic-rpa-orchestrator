# Implementation Plan: Align Workflow Automation with Verified AntiCaptcha Master Profile

**Implementation ID:** `IMP-2026-0925-004`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** SingleSessionBrowserRunner, ChromeSession, Automation Settings, AntiCaptcha Persistence  
**Date:** 2026-09-25  
**Author:** Antigravity AI Engineering Assistant  
**Status:** Approved - Ready for Execution  
**AI Verification:** In Progress  
**Human Verification:** Pending Human Verification  

---

## 1. Problem Statement & User Directive

### 1.1 User Request
> *"from this i have configured the anticaptcha, pls use the same setting and same browser for workflow automation when browser launnches for workkflow tasks as here anticapcha is loaded and configured and this must be one time activity. so that anticaptcha loads always when workflow started for extraction because without anticapcha our system is useless"*

### 1.2 Identified Architectural Discrepancy
1. **Toolbar Pinning & Setup Profile:**
   - Under Settings > **Toolbar Pinning & Profile Setup**, the AntiCaptcha extension is configured, verified, and pinned in the persistent master profile:
     - Directory: `backend/data/browser_profile/chrome/`
     - Action ID: `kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj`
     - Pinned in: `Default/Preferences` (`pinned_extensions` & `toolbar.pinned_actions`)
     - Database flag: `extension_setup_verified = True`
2. **Workflow Automation Disconnect:**
   - When claims were scraped via `SingleSessionBrowserRunner` (`backend/app/automation/session_runner.py`), the runner unconditionally provisioned a fresh temporary directory (`tempfile.mkdtemp(prefix="uaic_worker_profile_")`) and marked `self.is_temp_profile = True`.
   - Consequently, the runner never used the configured master profile `backend/data/browser_profile/chrome/`, discarding the configured local storage, extension state, and persistent settings.
   - On exit, `__aexit__` deleted the temporary directory (`shutil.rmtree`), requiring re-setup on every launch.
3. **Built-in Service Worker Collision:**
   - In `session_runner.py` (`_scan_for_extension`):
     ```python
     if "anticaptcha" in url.lower() or "service_worker.js" in url.lower():
     ```
   - Google Chrome includes an internal built-in component: `chrome-extension://fignfifoniblkonapihmkfakmlgkbkcf/service_worker.js` (Google Network Speech).
   - Because of `or "service_worker.js" in url.lower()`, the runner selected `fignfifoniblkonapihmkfakmlgkbkcf` as the AntiCaptcha ID and attempted to navigate to its `popup_v3.html`, which failed (`ERR_FILE_NOT_FOUND`).
   - AntiCaptcha was never configured or verified, causing portal CAPTCHA solving to time out (154s in Broward County) and leaving subsequent portals pending.

---

## 2. Proposed Changes & Technical Architecture

### Component 1: Persistent Master Profile Alignment in `session_runner.py`
* **File:** [`backend/app/automation/session_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py)
* **Changes:**
  1. **Profile Resolution:**
     - Resolve `canonical_profile = target_user_dir if (target_user_dir and os.path.exists(target_user_dir)) else persistent_engine` (pointing to `backend/data/browser_profile/chrome`).
     - Run `ChromeSession.clean_profile_locks_and_orphans(canonical_profile, force_kill=False)`.
     - When `self.worker_id is None` (standard workflow claim execution) and not `self.isolated_profile` and not `ChromeSession.is_profile_locked(canonical_profile)`:
       - Set `self.profile_to_use = canonical_profile`
       - Set `self.is_temp_profile = False` (ensuring master profile is NEVER deleted on exit)
       - Pass `--disk-cache-dir` to optimize cache reuse
  2. **Worker Pre-Seeding (when concurrency > 1):**
     - If an isolated profile is needed (parallel concurrency), pre-seed all extension settings, state, and rules from `canonical_profile` (`Default/Preferences`, `Local State`, `Local Extension Settings`, `Sync Extension Settings`, `Extension State`, `Extensions`) and apply toolbar pinning.
  3. **Strict Extension Matching:**
     - Remove `or "service_worker.js" in url.lower()` from `_scan_for_extension()`.
     - Strictly match `KNOWN_ANTICAPTCHA_IDS` (`["gcpdbjbmekkdlkpldjgffhmapgpdlcpj"]`) or `"anticaptcha" in url.lower()`.
     - Use `sw.evaluate("() => chrome.storage.local.get(['account_key', 'enable'])")` to verify configuration directly without fragile popup navigations.
     - Add developerPrivate fallback probe if dormant.

### Component 2: Error Logging Hierarchy & Verification in `settings.py`
* **File:** [`backend/app/api/v1/endpoints/settings.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/settings.py)
* **Changes:**
  1. In `setup_extension_endpoint`:
     - Clean profile locks on `persistent_dir` before starting verification.
     - Increase verification timeout from 20.0s to 45.0s to allow reliable initialization under heavy Windows I/O.
     - Implement diagnostic error screenshot capture to `backend/screenshots/setup/` and structured logs to `backend/logs/setup/execution.log` per `ManualPrompt.txt` Note 1.

### Component 3: Scraper Tasks Concurrency & Slot Resilience
* **File:** [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py)
* **Changes:**
  1. Ensure `SingleSessionBrowserRunner` receives `worker_id` and correct parameters.
  2. Guarantee browser slot release on task completion, cancellation, and exceptions.

---

## 3. Step-by-Step Implementation Order

1. **Edit `backend/app/automation/session_runner.py`:**
   - Update profile resolution in `SingleSessionBrowserRunner.__aenter__`.
   - Update `_scan_for_extension` to remove the built-in service worker collision.
   - Implement direct service worker verification (`sw.evaluate`) and dormant probe.
2. **Edit `backend/app/api/v1/endpoints/settings.py`:**
   - Sanitize locks, increase timeout to 45s, and add error screenshot/log hierarchy.
3. **Automated Verification:**
   - Execute test scripts verifying persistent master profile launch.
   - Run backend test suite (`pytest`, `ruff`).
   - Run frontend type check (`tsc --noEmit`).
   - Run PowerShell syntax check.

---

## 4. Definition of Done (DoD)

- [ ] `SingleSessionBrowserRunner` uses `backend/data/browser_profile/chrome` as its master persistent profile when concurrency is 1.
- [ ] AntiCaptcha extension (`gcpdbjbmekkdlkpldjgffhmapgpdlcpj`) is detected and active without popup errors.
- [ ] No `ERR_FILE_NOT_FOUND` on built-in Chrome service workers.
- [ ] Master profile is preserved on session exit (`is_temp_profile=False`).
- [ ] 100% automated test suite passes (pytest, ruff, tsc, ps1).
