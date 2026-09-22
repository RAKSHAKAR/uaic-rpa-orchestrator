# Implementation Plan: Settings Tab 4 Reorder & Attended Browser Test Launch Fix

**Implementation ID:** `IMP-2026-0917-006`  
**Date:** 2026-09-17  
**Author:** Antigravity AI Engineering Team  
**Status:** Ready for Review  

---

## 1. Problem Statement & User Requirement

The user requested two specific enhancements:
1. **Tab 4 (CAPTCHA Extension) Section Reordering:**
   > *"pls keep this section in last : Extension Health Diagnostics before Live Browser Launch Test."*
   Move `Extension Health Diagnostics` so that it is positioned immediately before `Live Browser Launch Test`, placing `One-Time Extension Toolbar Pinning & Persistent Profile Setup` first.

2. **Attended Browser Launch Visibility & Auto-Setup:**
   > *"also when i am testing via Live Browser Launch Test it showing attendent gui but i can't see anything is running. it must open th selected browser and do the required setup for anticaptcha and piined the anticaptcha in browser."*
   When running the live browser launch test in Attended GUI mode:
   - It must automatically run the required setup for Anti-Captcha (syncing credentials and pinning the extension to the toolbar).
   - It must visibly launch the selected browser (Google Chrome, Chromium, or Microsoft Edge) on the user's desktop, maximized in the foreground.
   - It must display an interactive verification page confirming Anti-Captcha status and showing the pinned toolbar icon, with sufficient inspection time (12s countdown) rather than instantly disappearing in 2.5 seconds.

---

## 2. Root Cause Analysis

1. **Section Sequence in Tab 4:**
   Currently in `frontend/src/app/settings/page.tsx`, `Extension Health Diagnostics` is placed above `One-Time Extension Toolbar Pinning & Persistent Profile Setup`. Swapping them puts the profile configuration first, followed by diagnostics, and concludes with the live launch test.

2. **Why the Attended Test Browser Was Not Visible to the Operator:**
   - **Blink-and-you-miss-it Timeout (2.5s):** In `backend/app/api/v1/endpoints/settings.py`, `_do_browser_test()` navigated to `https://example.com`, waited only 2,500ms, and then immediately invoked `await session.close()`. In Windows, when launching behind the user's active browser, 2.5 seconds was insufficient for the user to switch windows or see the browser before it closed.
   - **Conflicting Window Position Flags:** In `ChromeSession.start()`, `"--start-maximized"` was followed by an unconditional `f"--window-position={w_offset_x},{w_offset_y}"`, which canceled the maximized state in Chrome.
   - **Missing Pre-Setup in Test Launch:** `test_browser_launch` did not invoke `ChromeSession.configure_and_pin_profile()` prior to launching the session, leaving setup unperformed if the operator hadn't clicked the separate button first.
   - **Generic Blank Target URL:** Navigating to `https://example.com` showed no Anti-Captcha information or confirmation.

---

## 3. Proposed Changes

### Component 1: `frontend/src/app/settings/page.tsx`
- **Reorder Tab 4 Cards:**
  1. `One-Time Extension Toolbar Pinning & Persistent Profile Setup` (Top)
  2. `Extension Health Diagnostics` (Middle — right before Live Browser Launch Test)
  3. `Live Browser Launch Test` (Bottom / Final)
- Update step indicators and helper text to reflect the natural logical sequence: Pin & Configure Profile → Verify Health Diagnostics → Live Attended Browser Launch Test.
- Enhance the Live Browser Launch Test card with a visible status indicator letting the user know the selected browser is opening on their screen for inspection.

### Component 2: `backend/app/api/v1/endpoints/settings.py`
- **Serve Dedicated Test Verification Page (`GET /api/v1/settings/browser-test-page`):**
  Serve a rich, fast local HTML verification console displaying:
  - Selected Browser Engine (`Google Chrome`, `Chromium`, or `Microsoft Edge`)
  - Display Mode (`Attended (Visible GUI)`)
  - Anti-Captcha Plugin Status (`v0.83 Loaded & Solved`)
  - Toolbar Pinning Notice (`Look at the top-right toolbar for the pinned Anti-Captcha icon`)
  - Interactive countdown timer (12 seconds) with a `[Close Window]` button.
- **Auto-Setup & Pinning on Launch:**
  In `test_browser_launch`:
  - Automatically call `ChromeSession.configure_and_pin_profile(api_key=auto_cfg.anticaptcha_api_key, extension_path=ext_path)` at the start of the test.
  - Persist `extension_setup_verified = True` in DB settings.
  - Navigate to the local `browser-test-page` by default.
  - In Attended mode, provide a 12-second observation window with graceful early-exit if closed by the operator.

### Component 3: `backend/app/automation/browser_manager.py`
- In `ChromeSession.start()`:
  - Clean up launch arguments: ensure `--start-maximized` is preserved for single/test sessions without being overridden by `--window-position`.
  - Pass `--window-size=1920,1080` fallback.

---

## 4. Verification Plan

1. **Automated Unit Tests:**
   - Run `pytest tests/test_browser_manager.py tests/test_extension_pinning_and_setup.py tests/test_fleet_concurrency.py`.
   - Run `ruff check app tests` (0 errors).
   - Run `frontend` `npx tsc --noEmit` (0 errors).
   - Run `scripts/check_ps1_syntax.ps1` (0 errors).

2. **Automated Live Browser Verification:**
   - Execute test launch via Python script and verify that `browser-test-page` is loaded with Anti-Captcha active and pinned.
   - Run `browser_subagent` to test the reordered Settings UI Tab 4 and capture visual evidence.
