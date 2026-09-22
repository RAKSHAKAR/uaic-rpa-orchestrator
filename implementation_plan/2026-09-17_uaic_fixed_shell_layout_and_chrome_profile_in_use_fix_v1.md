# Implementation Plan: Fixed App Shell Layout & Chrome Profile-In-Use Fix

**Implementation ID:** `IMP-2026-0917-006`  
**Date:** 2026-09-17  
**Status:** In Review  

---

## 1. Goal Description

The user reported two critical requirements:
1. **Layout Governance:**
   "make sure left side, header and footer always be like this and when page is having large then show the scroll for body (rest of the part)."
   - Anchor the **Left Sidebar** (`<Sidebar />`) permanently to the left viewport.
   - Anchor the **Header** (`<Navbar />`) permanently at the top.
   - Anchor the **Footer** (`<Footer />`) permanently at the bottom.
   - Restrict scrolling strictly to the **Main Body** (`<main>` / page content area) so that when page content is large, only the body displays a vertical scrollbar (`overflow-y-auto min-h-0 flex-1`), preventing whole-window overflow and keeping navigation persistent at all times.
2. **Chrome Browser Launch Error (`exitCode=21`):**
   "Browser test failed in Attended (Visible GUI) mode: RuntimeError: Browser executable could not be launched for engine 'chrome': BrowserType.launch_persistent_context: Target page, context or browser has been closed ... exitCode=21"
   - Chromium exit code 21 represents `RESULT_CODE_PROFILE_IN_USE`. This occurs when Google Chrome is launched on a profile directory (`backend/data/browser_profile/chrome`) that is either locked by lingering orphan processes or stale lock files (`SingletonLock`, `SingletonCookie`, `SingletonSocket`).
   - Implement automated process sanitation and profile lock release in `ChromeSession` so any orphan processes or dead locks on the RPA profile are cleanly resolved before launch, preventing `exitCode=21`.

---

## 2. User Review Required

> [!IMPORTANT]
> **Layout Experience:** The viewport will be locked to `100vh` (`h-screen overflow-hidden`).
> - Left side (Navigation Sidebar) will be permanently fixed on the left.
> - Top bar (Navbar / Header) will be permanently fixed at the top.
> - Bottom bar (System Engine Footer) will be permanently fixed at the bottom.
> - Only the center body content will scroll vertically when content exceeds the screen height.

---

## 3. Open Questions

None. The user's instructions and screenshot clearly define the exact layout and error to solve.

---

## 4. Proposed Changes

### Frontend (App Shell & Page Layouts)

#### [MODIFY] [ResponsiveShell.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/components/ResponsiveShell.tsx)
- Set container to `h-screen max-h-screen overflow-hidden flex flex-col`.
- Structure left sidebar as full-height `h-full overflow-y-auto shrink-0`.
- Structure right column as `flex-1 h-full min-w-0 min-h-0 flex flex-col overflow-hidden relative`.
- Keep footer docked at bottom as `shrink-0 z-20 border-t border-slate-200 dark:border-slate-800`.
- Ensure `{children}` occupies `flex-1 min-h-0 flex flex-col overflow-hidden`.

#### [MODIFY] [layout.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/layout.tsx)
- Ensure `body` has `h-screen overflow-hidden flex w-full` so the window itself never scrolls.

#### [MODIFY] [settings/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)
- Ensure the page wrapper has `h-full min-h-0 flex-1 flex flex-col overflow-hidden`.
- Ensure `<Navbar />` is `shrink-0`.
- Ensure `<main>` has `flex-1 min-h-0 overflow-y-auto overflow-x-hidden`.

#### [MODIFY] [page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/page.tsx)
- Ensure the main dashboard wrapper and `<main>` have `flex-1 min-h-0 overflow-y-auto`.

#### [MODIFY] Other primary routes (`monitor`, `health`, `exceptions`, `upload`, `branding`, `audit`, `claims/[id]`)
- Ensure consistent `flex-1 min-h-0 overflow-y-auto` across all page `<main>` views.

---

### Backend (Process Sanitation & Profile In-Use Guard)

#### [MODIFY] [browser_manager.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py)
- Implement `clean_profile_locks_and_orphans(profile_dir)`:
  - Delete Chromium `SingletonLock`, `SingletonCookie`, `SingletonSocket`, `lockfile`.
  - On Windows, terminate any lingering orphan browser processes referencing that specific profile before `launch_persistent_context`.
- Call `clean_profile_locks_and_orphans(self.profile_to_use)` inside `ChromeSession.start()`.

---

## 5. Verification Plan

### Automated Tests
1. Backend test suite:
   ```bash
   backend\.venv\Scripts\pytest.exe backend\tests\test_browser_manager.py -q
   backend\.venv\Scripts\ruff.exe check backend
   ```
2. Frontend build & quality checks:
   ```bash
   cd frontend
   npx tsc --noEmit
   npm run lint
   ```
3. API Browser Launch verification:
   - Call `POST /api/v1/settings/test-browser` with `{"headless": false, "browser_engine": "chrome"}`.
   - Verify 200 OK and successful launch without `exitCode=21`.

### Live Subagent & Visual Verification
1. Open `/settings` in the browser subagent.
2. Verify:
   - Left sidebar is visible and docked.
   - Navbar header is visible and docked.
   - Footer is visible and docked at the bottom of the viewport.
   - Scrolling down scrolls ONLY the body, while sidebar, header, and footer remain anchored in place.
3. Trigger "Launch Browser Test" and confirm success.
4. Capture video recording in `implementation_plan/Recording/` and screenshot in `implementation_plan/Images/`.
