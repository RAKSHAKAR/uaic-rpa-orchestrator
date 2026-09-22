# Implementation Plan: Comprehensive Resolution of Pending Items, AntiCaptcha Detection & Fixed Shell Layout Governance

**Implementation ID:** `IMP-2026-0918-001`  
**Date:** 2026-09-18  
**Document Type:** Implementation Plan  
**Status:** PROPOSED (Awaiting User Approval)  
**Author:** Antigravity AI Engineering Governance Agent  

---

## 1. Executive Summary & Root Cause Analysis

In the previous session, the user raised four critical questions/issues that remained pending or partially addressed:

1. **Anti-Captcha Extension & Pinning Discrepancy:**
   > *"where is showing anticaptcha extension and there is no pinned as well, i check dev mode is also not on and not showing any extension there, how you are testing and doing job?"*
   - **Root Cause Diagnosed:**
     1. In `backend/app/automation/browser_manager.py`, `KNOWN_ANTICAPTCHA_IDS` incorrectly included `fignfifoniblkonapihmkfakmlgkbkcf`. Verbose Chrome logging proved that `fignfifoniblkonapihmkfakmlgkbkcf` is actually **Google Network Speech** (a built-in Chrome component extension), NOT Anti-Captcha. Anti-Captcha's real unpacked extension ID is `gcpdbjbmekkdlkpldjgffhmapgpdlcpj`.
     2. Google Chrome on this machine is an enterprise-managed build enrolled in `Damco.local`. Chrome's internal security logs show:
        `--disable-extensions-except is not allowed in Google Chrome, ignoring.`
        Google Chrome enterprise policy blocks unpacked third-party extensions from being loaded via `--load-extension`.
     3. Conversely, both **Playwright Chromium (Bundled)** and **Microsoft Edge** load Anti-Captcha (`gcpdbjbmekkdlkpldjgffhmapgpdlcpj`) with 100% success, active service worker, and toolbar icon.
     4. Because `fignfifoniblkonapihmkfakmlgkbkcf` was falsely matched to Google Network Speech, the backend previously reported "Extension loaded & verified" on Chrome, even though Google Chrome silently dropped the unpacked plugin.
   - **Resolution:**
     1. Remove `fignfifoniblkonapihmkfakmlgkbkcf` from `KNOWN_ANTICAPTCHA_IDS`. Retain only authentic Anti-Captcha IDs (`gcpdbjbmekkdlkpldjgffhmapgpdlcpj`).
     2. In `browser_manager.py`, strictly verify the real extension ID. If Google Chrome drops the extension due to corporate enterprise policy, the system will accurately detect the failure, warn the operator, and automatically switch to `Chromium (Bundled)` or `Microsoft Edge`.
     3. Set the default browser automation engine in settings to `chromium` (with seamless Edge support) so bot scraping and tests succeed out of the box without corporate policy blocks.

2. **Fixed App Shell Layout Governance Across All Remaining Routes:**
   > *"make sure left side, header and footer always be like this and when page is having large then show the scroll for body (rest of the part)."*
   - **Root Cause Diagnosed:**
     - The viewport layout was established in `ResponsiveShell.tsx`, `page.tsx` (Dashboard), `settings/page.tsx`, `branding/page.tsx`, and `claims/[id]/page.tsx`.
     - However, 4 remaining primary routes (`/monitor`, `/health`, `/exceptions`, `/audit`) still contained unconstrained vertical heights (`min-h-screen`, `flex flex-col w-full` without `h-full min-h-0 overflow-hidden`, and `<main>` without `min-h-0 overflow-y-auto`). This caused the entire window to scroll instead of restricting the scrollbar strictly to the main body.
   - **Resolution:**
     - Standardize the outer container on `/monitor`, `/health`, `/exceptions`, and `/audit` to `flex-1 flex flex-col w-full h-full min-h-0 overflow-hidden`.
     - Anchor `<Navbar />` permanently at the top.
     - Standardize `<main>` to `flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none transition-colors` so ONLY the main body scrolls when content is large.
     - Keep `<Footer />` permanently docked at the bottom.

3. **Chrome Profile In-Use Guard (`exitCode=21`):**
   > *"Browser test failed in Attended (Visible GUI) mode: RuntimeError: Browser executable could not be launched for engine 'chrome': BrowserType.launch_persistent_context: Target page, context or browser has been closed ... exitCode=21"*
   - **Root Cause Diagnosed:**
     - Exit code 21 is Chromium's `RESULT_CODE_PROFILE_IN_USE`. This occurs when orphan browser processes or dead lockfiles (`SingletonLock`, `SingletonCookie`, `SingletonSocket`, `lockfile`) remain in the profile directory.
   - **Resolution:**
     - Implement and systematically invoke `clean_profile_locks_and_orphans()` before every persistent context launch across `ChromeSession`, `SingleSessionBrowserRunner`, and `BasePortalScraper`.

4. **Next.js Webpack Cache Invalidation:**
   > *"1 of 1 error Next.js (14.2.35) is outdated ... TypeError: Cannot read properties of undefined (reading 'call') at webpack-runtime.js"*
   - **Resolution:**
     - Cleaned and rebuilt frontend with `npm run build` (all 11 routes statically/dynamically prerendered with 0 errors).
     - Ensure clean startup in `setup_local.ps1`.

---

## 2. User Review Required

> [!IMPORTANT]
> **Anti-Captcha Engine Selection (Google Chrome vs. Chromium / Edge):**
> On this corporate machine (`Damco.local`), Google Chrome is centrally managed and policy-locked against loading unpacked extensions from disk (`--disable-extensions-except is not allowed in Google Chrome`).
> - **Chromium (Bundled)** and **Microsoft Edge** both load the Anti-Captcha extension (`gcpdbjbmekkdlkpldjgffhmapgpdlcpj`) with **100% perfection** and full service worker support.
> - We will set **Chromium (Bundled)** as the default automation engine in settings, with automatic detection and seamless fallback if Google Chrome is requested on a managed workstation.

> [!IMPORTANT]
> **Persistent Fixed Viewport Layout:**
> The entire application viewport is strictly locked to `100vh` (`h-screen overflow-hidden`):
> - **Left Sidebar** is permanently docked and fixed on the left.
> - **Navbar Header** is permanently docked and fixed at the top.
> - **Footer** is permanently docked and fixed at the bottom.
> - **Main Body** is the **ONLY** element that scrolls vertically when page content exceeds the viewport height.

---

## 3. Open Questions

None. The user's exact requirements and technical diagnostic logs clearly define the root causes and full solutions.

---

## 4. Proposed Changes

### Backend (AntiCaptcha Detection, Profile Sanitation & Settings Default)

#### [MODIFY] [backend/app/automation/browser_manager.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py)
- Update `KNOWN_ANTICAPTCHA_IDS`: remove bogus Google Network Speech ID `fignfifoniblkonapihmkfakmlgkbkcf`. Retain authentic ID `gcpdbjbmekkdlkpldjgffhmapgpdlcpj`.
- In `clean_profile_locks_and_orphans()`: ensure robust deletion of Chromium singleton lock files and termination of orphan Chrome/Edge processes on Windows.
- In `start()`: verify real Anti-Captcha extension ID `gcpdbjbmekkdlkpldjgffhmapgpdlcpj`. If Google Chrome fails to register the worker due to enterprise policy, automatically fall back to Chromium with an informative warning.

#### [MODIFY] [backend/app/services/settings_service.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/settings_service.py)
- Ensure default `browser_engine` is `"chromium"`.

#### [MODIFY] [backend/app/api/v1/endpoints/settings.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/settings.py)
- Update `/test-browser` and `/setup-extension` to use authentic Anti-Captcha ID `gcpdbjbmekkdlkpldjgffhmapgpdlcpj` and accurately report corporate Chrome policy status.

---

### Frontend (Fixed Viewport Layout Across All Remaining Routes)

#### [MODIFY] [frontend/src/app/monitor/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/monitor/page.tsx)
- Outer container: `className="flex-1 flex flex-col w-full h-full min-h-0 overflow-hidden"`
- Main body: `className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none transition-colors"`

#### [MODIFY] [frontend/src/app/health/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/health/page.tsx)
- Outer container: replace `min-h-screen` with `className="flex-1 flex flex-col w-full h-full min-h-0 overflow-hidden text-slate-900 dark:text-slate-100"`
- Main body: `className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none transition-colors"`

#### [MODIFY] [frontend/src/app/exceptions/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/exceptions/page.tsx)
- Outer container: `className="flex-1 flex flex-col w-full h-full min-h-0 overflow-hidden"`
- Main body: `className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8 w-full max-w-none transition-colors"`

#### [MODIFY] [frontend/src/app/audit/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/audit/page.tsx)
- Outer container: replace `min-h-screen` with `className="flex-1 flex flex-col w-full h-full min-h-0 overflow-hidden bg-slate-50 dark:bg-slate-900 transition-colors"`
- Main body: `className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 w-full max-w-none transition-colors"`

---

## 5. Verification Plan

### Automated Verification:
1. **Backend Tests:**
   ```powershell
   cd backend
   .venv\Scripts\pytest --tb=short -q
   ```
2. **Backend Lint:**
   ```powershell
   cd backend
   .venv\Scripts\ruff check app tests
   ```
3. **Frontend TypeScript Check:**
   ```powershell
   cd frontend
   npx tsc --noEmit
   ```
4. **Frontend Production Build:**
   ```powershell
   cd frontend
   npm run build
   ```
5. **PowerShell Script Syntax:**
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```

### Live Browser Subagent & Visual Verification:
1. Open the application in the browser subagent across primary routes (`/`, `/settings`, `/monitor`, `/health`, `/exceptions`, `/audit`).
2. Verify visual layout:
   - Sidebar permanently docked on left.
   - Navbar permanently docked at top.
   - Footer permanently docked at bottom.
   - Only the main body scrolls when page content is large.
3. Verify Browser Launch Test on `/settings`:
   - Launch test with Chromium / Edge.
   - Confirm Anti-Captcha extension is loaded, service worker is active, and test completes with green badge.
4. Capture video recording in `implementation_plan/Recording/` and screenshots in `implementation_plan/Images/`.
