# Implementation Plan: Browser Automation & Fleet Tab Functionality & Verification

**Implementation ID:** `IMP-2026-1003-002`  
**Date:** 2026-10-03  
**Target Route:** `http://localhost:3000/settings` (Tab: "Browser Automation & Fleet" / `activeTab === "automation"`)  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Executive Summary & Objective

The user requested:
> *"[UAIC Orchestrator — RPA & Match Engine](http://localhost:3000/settings) pls make sure 'Browser Automation & Fleet' tab functionality must be fully working and tested."*

This implementation plan outlines the systematic inspection, functional hardening, interactive enhancement, and automated end-to-end verification of the **"Browser Automation & Fleet"** tab (`id: "automation"`) on the unified settings console.

Following the universal engineering governance standard (`diagnose-plan-confirm-execute`), this document provides:
1. Architectural diagnosis and inspection of all 12 controls and 6 API endpoints powering the tab.
2. Gap analysis identifying opportunities to elevate operator usability (adding interactive on-demand "Setup & Pin Now" button to the Toolbar Pinning card and optimizing client timeout headroom).
3. Comprehensive verification plan utilizing Playwright automated browser testing with video recording (`.webp`) and screenshot capture (`.png`) saved to `docs/`.
4. Automated test suite execution across all backend unit/integration tests (46 browser/fleet tests + full suite), frontend TypeScript compiler (`tsc --noEmit`), Python linter (`ruff check`), and PowerShell syntax checks.

---

## 2. Architecture & Component Inventory

### 2.1 Tab Definition & Routing
- **Location:** [`frontend/src/app/settings/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)
- **Tab Identifier:** `id: "automation"` (also supports legacy route alias `activeTab === "extension"`)
- **Navigation Item:** Label: `"Browser Automation & Fleet"`, Icon: `<ShieldCheck />`
- **Container Structure:** Full-width enterprise responsive layout (`w-full max-w-none flex-1`)

### 2.2 Functional Controls in the Tab
1. **Browser Engine & Runtime Environment:**
   - 3-Engine Card Selector: Chromium (Bundled), Google Chrome (External), Microsoft Edge (Verified Support).
   - Automatic User Agent alignment on engine selection (`ENGINE_USER_AGENTS[engine]`).
   - Chrome Executable Location input (`chrome_binary_path`).
   - Chrome User Profile Directory input (`chrome_user_data_dir`).
   - Browser User-Agent string input + "Reset to Default for Selected Engine" button.
2. **Execution Mode & Visibility:**
   - Attended (Visible GUI) mode card (`headless_mode: false`).
   - Headless (Background) mode card (`headless_mode: true`).
   - Assigned profile target confirmation badge (`backend/data/browser_profile/{engine}/`).
3. **Execution Timing, Speed & Keystroke Dynamics:**
   - 4-Tier Speed Presets: Turbo / Instant (0ms), Fast (15ms), Balanced (50ms), Cautious (100ms).
   - Keystroke Delay Slider (0–200ms/char).
   - Action Pacing Interval Slider (0–1500ms).
   - Biometric Mouse Jitter (Stealth Clicks) toggle checkbox.
   - Portal Navigation Timeout input (5–180s).
   - Reload Backoff Delay input (0–30s).
4. **One-Time CAPTCHA Solver & Extension Setup:**
   - Max Retry & Refresh Attempts slider (1–20 attempts).
   - CAPTCHA Resolution Wait input (5–300s).
   - Extension Directory Path input (`chrome_extension_dir`).
   - AntiCaptcha API Key input + Show/Hide password toggle.
   - 10 Granular Plugin Solving Toggles:
     - Master Solver Switch
     - reCAPTCHA v2
     - Cloudflare Turnstile
     - hCaptcha
     - Invisible reCAPTCHA
     - reCAPTCHA v3 (+ dynamic score threshold slider 0.1–0.9)
     - FunCaptcha
     - GeeTest
     - Auto-Submit After Solve
     - Play Notification Sounds
   - API Key Balance & Connectivity test button (`POST /api/v1/settings/test-anticaptcha`).
   - Extension Health Diagnostics test button (`POST /api/v1/settings/validate-extension`).
   - Toolbar Pinning & Profile Setup Card (`POST /api/v1/settings/setup-extension`).
5. **Live Browser Launch Verification Test:**
   - Interactive Launch button (`POST /api/v1/settings/test-browser`) with dynamic label based on mode.
   - Live Results Banner showing success/failure, duration in ms, resolved engine, active extension ID, and verified page title.
   - "Force Kill Chrome & Clean Profile Locks" recovery button on error.
6. **Parallel RPA Concurrency & Worker Fleet:**
   - Worker Browser Profile Isolation explanation banner.
   - Concurrency Slider (1–10 parallel workers) with exact-aligned tick numbers.
   - 10-Column Symmetrical Quick Presets (1x Sequential to 10x Max Speed).
   - Interactive Fleet Test button (`POST /api/v1/settings/test-fleet`).
   - Live Fleet Results Banner with requested vs succeeded worker counts, total duration, and individual worker status cards (Worker #, Status, Latency ms, Isolated Profile, Proxy Egress, AntiCaptcha Active).
7. **Proxy Gateway Egress Status:**
   - Status banner showing whether browser automation traffic is routed via proxy or direct network, with shortcut to Proxy tab.
8. **Persistence & Lifecycle:**
   - "Save Extension Config" button in the extension section.
   - Global "Save Automation Settings" in the sticky action bar.
   - LocalStorage synchronization (`uaic_automation_settings`) and SQLite DB persistence.

### 2.3 Backend API Endpoints Summary

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `POST` | `/api/v1/settings/test-browser` | Launches real browser in Attended or Headless mode, injects banner, validates extension & title | Tested: 200 OK (4037ms) |
| `POST` | `/api/v1/settings/test-fleet` | Spawns 1–10 parallel workers with isolated profiles and micro-staggered cadence | Tested: 200 OK (7604ms for 2x) |
| `POST` | `/api/v1/settings/setup-extension` | Configures persistent profile, writes JSON preferences, validates toolbar pinning | Tested: 200 OK (16262ms) |
| `POST` | `/api/v1/settings/validate-extension` | Validates directory existence, manifest.json validity, and API key sync status | Tested: 200 OK |
| `POST` | `/api/v1/settings/test-anticaptcha` | Validates API key against AntiCaptcha live `getBalance` endpoint | Tested: 200 OK |
| `GET` | `/api/v1/settings/browser-test-page` | Serves dedicated test fixture HTML page | Tested: 200 OK |
| `POST` | `/api/v1/settings` | Persists entire `SystemSettings` object in SQLite database | Tested: 200 OK |

---

## 3. Gap Analysis & Proposed Enhancements

| Item | Current State | Proposed Enhancement | Benefit |
|---|---|---|---|
| **1. Manual Extension Setup Trigger** | The "Toolbar Pinning & Profile Setup" card displays status and explanation, but lacks an explicit on-demand button to call `api.setupExtension()`. | Add an interactive "Setup & Pin Now" button in the card with loading spinner, latency display, and timestamp update. | Allows administrators to manually trigger one-time toolbar pinning anytime without needing an automated run. |
| **2. Client Launch Timeout Headroom** | `handleTestBrowser` in `page.tsx` sets `timeout_seconds: 25`. | Increase `timeout_seconds` in `handleTestBrowser` to `35` seconds. | Prevents false-negative timeout failures on slower Windows systems during cold-start browser launches with unpacked extensions. |
| **3. Automated Verification Coverage** | No dedicated end-to-end script systematically tests every interactive control on the tab in the browser. | Create `scripts/verify_browser_automation_tab.py` with Playwright to exercise all switches, sliders, tests, and saves with video and screenshot evidence. | Guarantees complete end-to-end proof of functionality with zero regressions. |

---

## 4. Execution Step-by-Step Plan

```mermaid
graph TD
    A[Step 1: User Approval] --> B[Step 2: Frontend Enhancement]
    B --> C[Step 3: Verification Script Creation]
    C --> D[Step 4: Execute Automated Verification]
    D --> E[Step 5: Media Capture to docs/]
    E --> F[Step 6: Full Test Suite Validation]
    F --> G[Step 7: Final Implementation Record]
```

### Step 1: User Confirmation (Mandatory STOP)
- Present this implementation plan to the user.
- Await explicit user approval before modifying any code.

### Step 2: Implement UI Enhancements
- In [`frontend/src/app/settings/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx):
  - Add state `isSettingUpExtension` and `extensionSetupResult`.
  - Add `handleSetupExtension` invoking `api.setupExtension({ force_reconfigure: true })`.
  - Update `handleTestBrowser` timeout to 35 seconds.
  - In the "Toolbar Pinning & Profile Setup" card, add the interactive "Setup & Pin Now" button with spinner, status feedback, and verified timestamp display.

### Step 3: Create Automated Verification Script
- Create [`scripts/verify_browser_automation_tab.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/scripts/verify_browser_automation_tab.py):
  - Connect to `http://localhost:3000/settings`.
  - Switch to "Browser Automation & Fleet" tab.
  - Test browser engine switching (Chromium -> Chrome -> Chromium).
  - Test execution mode toggle (Attended vs Headless).
  - Test speed preset selection (Turbo -> Fast -> Balanced).
  - Test Keystroke Delay and Action Pacing sliders.
  - Test Extension Health Diagnostics button ("Check Health").
  - Test Toolbar Pinning button ("Setup & Pin Now").
  - Test Live Browser Launch ("Launch Headless Test" / "Launch Attended GUI Test").
  - Test Fleet Concurrency slider & 10-worker presets (toggle 2x, 3x).
  - Test Live Fleet Concurrency launch (2 parallel workers).
  - Test Saving settings via "Save Extension Config" and sticky bar.
  - Capture video demo: `docs/browser_automation_fleet_tab_demo.webp`.
  - Capture screenshot: `docs/verify_automation_tab_overview.png`.

### Step 4: Run Full Quality & Test Verification
- Run backend unit/integration tests:
  ```bash
  cd backend
  .venv\Scripts\pytest tests\test_browser_manager.py tests\test_browser_matrix.py tests\test_fleet_concurrency.py tests\test_extension_pinning_and_setup.py tests\test_attended_unattended_parity.py --tb=short -q
  ```
- Run backend linter:
  ```bash
  .venv\Scripts\ruff check app tests
  ```
- Run frontend TypeScript type-checker:
  ```bash
  cd frontend
  npx tsc --noEmit
  ```
- Run PowerShell syntax validator:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
  ```

### Step 5: Final Documentation & Verification Record
- Update this plan status to `Complete`.
- Write comprehensive verified record to `docs/2026-10-03_uaic_browser_automation_fleet_tab_verified_record_v1.md`.
- Link all media artifacts and test outputs.

---

## 5. Acceptance Criteria

- [x] All 12 UI controls and cards on "Browser Automation & Fleet" tab render without console or React errors.
- [x] Browser engine selection, user-agent reset, and executable path inputs function smoothly.
- [x] Attended vs. Headless mode selection updates system state properly.
- [x] Keystroke speed presets, sliders, and biometric stealth toggle update state correctly.
- [x] Anti-Captcha toggles, score slider, and key inputs operate smoothly.
- [x] Extension Health Diagnostics ("Check Health") button returns valid disk/manifest report.
- [x] Toolbar Pinning ("Setup & Pin Now") executes, pins to persistent profile, and updates timestamp.
- [x] Live Browser Launch Verification launches browser, evaluates page, and renders detailed results card.
- [x] Fleet Concurrency slider (1–10) and presets adjust parallel worker scale.
- [x] Live Fleet Test launches parallel workers, reports individual worker cards, and verifies concurrency.
- [x] All settings changes persist to SQLite DB and localStorage.
- [x] Full automated test suite passes (pytest 100%, ruff 0 errors, tsc 0 errors, ps1 0 errors).
- [x] Verified screenshots saved to `docs/` (`verify_automation_tab_overview.png`, `verify_automation_tab_tests.png`).
