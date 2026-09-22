# Implementation Plan: Unique Names API Tester Presets, Browser Mode Single Test Button, and One-Time Extension Setup Fix

**Implementation ID:** `IMP-2026-0917-006`  
**Date:** 2026-09-17  
**Author:** AI Agent (Antigravity)  
**Status:** Ready for Review  
**Lifecycle Stage:** Planned & Awaiting Confirmation  

---

## 1. Objectives & User Requirements

Based on user review and screenshot analysis:
1. **Unique Names API Live Tester Presets (`/api/v1/matches/unique-names`)**:
   - Add 3 preset buttons in the Settings page (`/settings`) for the Unique Names Live Tester, matching the 3 core deduplication scenarios provided in the user's table:
     - **Record 1 (All Same: 1 Unique)**:
       - Insured: `MARIA MARTINEZ`
       - Driver: `MARIA MARTINEZ`
       - Claimant: `MARIA MARTINEZ`
       - Expected: `1 unique target` (`MARIA MARTINEZ`)
     - **Record 2 (Insured=Driver: 2 Unique)**:
       - Insured: `ARMANDO FERNANDEZ HERNANDEZ`
       - Driver: `ARMANDO FERNANDEZ HERNANDEZ`
       - Claimant: `Jorge Bencomo Santana`
       - Expected: `2 unique targets` (`ARMANDO FERNANDEZ HERNANDEZ`, `Jorge Bencomo Santana`)
     - **Record 3 (All Different: 3 Unique)**:
       - Insured: `CORNELIUS BRIGHT`
       - Driver: `Aquaria Mitchell`
       - Claimant: `Felicia Mcmiller`
       - Expected: `3 unique targets` (`CORNELIUS BRIGHT`, `Aquaria Mitchell`, `Felicia Mcmiller`)
2. **Consolidate Browser Test Actions to a Single Dynamic Button**:
   - In Tab 3 ("Browser & CAPTCHA" / Automation), eliminate the two separate buttons `Test Attended (Visible GUI)` and `Test Headless`.
   - Replace with a **single dynamic test button** that executes whichever mode is currently selected in the execution mode cards (`settings.automation.headless_mode`).
3. **Re-order AntiCaptcha Extension Sub-Cards**:
   - In Tab 4 ("AntiCaptcha Extension"), move **Live Browser Launch Test** DOWN so that it appears **after** **One-Time Extension Toolbar Pinning & Persistent Profile Setup**.
4. **Make One-Time Extension Toolbar Pinning & Persistent Profile Setup Fully Functional**:
   - Resolve the schema field mismatch between backend `ExtensionSetupResponse` (`profile_dir`, `toolbar_action_verified`, `verified_at`) and frontend (`res.verified`, `res.persistent_profile_path`, `res.pinned_to_toolbar`, `res.timestamp`), which previously caused the frontend to misinterpret successful setups as red errors (`Target: • Pinned: undefined`).
   - Ensure the toolbar pinning status updates to `Pinned & Verified` (green) and properly displays the persistent profile path.

---

## 2. Proposed Technical Changes

### Component 1: Frontend Console (`frontend/src/app/settings/page.tsx`)

1. **Unique Names Presets**:
   - Define dynamic generator functions:
     - `getUniqueNamesPresetAllSame()`
     - `getUniqueNamesPresetInsuredDriverSame()`
     - `getUniqueNamesPresetAllDifferent()`
   - Add state: `const [selectedUniquePreset, setSelectedUniquePreset] = useState<"all_same" | "insured_driver_same" | "all_different">("all_same");`
   - Render the 3 preset buttons in the `Unique Names API Live Tester` header:
     - `Record 1: All Same (1 Unique)`
     - `Record 2: Insured=Driver (2 Unique)`
     - `Record 3: All Different (3 Unique)`
   - On click, update `selectedUniquePreset` and populate `testUniqueNamesPayload`.

2. **Single Dynamic Browser Test Button in Tab 3 ("Browser & CAPTCHA")**:
   - Replace the two buttons (`Test Attended (Visible GUI)` and `Test Headless`) with:
     ```tsx
     <button
       type="button"
       disabled={isTestingBrowser}
       onClick={() => handleTestBrowser(settings.automation.headless_mode)}
       className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50"
     >
       {isTestingBrowser ? (
         <RefreshCw className="w-3.5 h-3.5 animate-spin" />
       ) : !settings.automation.headless_mode ? (
         <Eye className="w-3.5 h-3.5" />
       ) : (
         <EyeOff className="w-3.5 h-3.5" />
       )}
       Launch Browser Test ({!settings.automation.headless_mode ? "Attended GUI" : "Headless"})
     </button>
     ```

3. **Re-ordering in Tab 4 ("AntiCaptcha Extension")**:
   - Place `One-Time Extension Toolbar Pinning & Persistent Profile Setup` as Step 4 (immediately after Extension Health Diagnostics).
   - Place `Live Browser Launch Test` as Step 5 (at the bottom, after profile setup).

4. **Extension Setup Handler & Display Fix**:
   - Update `handleSetupExtension`:
     - Inspect `res.verified || res.success` to determine success.
     - Extract `res.persistent_profile_path || res.profile_dir`.
     - Extract `res.timestamp || res.verified_at`.
     - Extract `res.pinned_to_toolbar ?? res.toolbar_action_verified`.
     - Set `settings.automation.extension_setup_verified = true` upon success.
   - Update result card rendering to properly display target profile directory and pinning status without `undefined`.

---

### Component 2: Backend API & Schemas (`backend/app/schemas/settings.py` & `backend/app/api/v1/endpoints/settings.py`)

1. **`backend/app/schemas/settings.py`**:
   - Update `ExtensionSetupResponse` to include both canonical and frontend compatibility fields:
     - `success: bool = True`
     - `status: str = "ok"`
     - `verified: bool = True`
     - `message: str`
     - `extension_id: str | None = "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"`
     - `toolbar_action_verified: bool = True`
     - `pinned_to_toolbar: bool = True`
     - `service_worker_active: bool = True`
     - `profile_dir: str`
     - `persistent_profile_path: str`
     - `verified_at: str`
     - `timestamp: str`
     - `latency_ms: float`

2. **`backend/app/api/v1/endpoints/settings.py`**:
   - In `setup_extension_endpoint`: Populate both canonical and backward-compatible fields in `ExtensionSetupResponse` so all frontend consumers and test suites receive the expected properties.

---

## 3. Verification Plan

### Automated Tests
1. **Unique Names Test Suite**:
   ```bash
   .venv\Scripts\pytest tests/test_imp_2026_0912_001.py -v
   ```
2. **Settings & Browser Automation Tests**:
   ```bash
   .venv\Scripts\pytest tests/test_fuzzymatch_api_parity.py -v
   ```
3. **Backend Linting**:
   ```bash
   .venv\Scripts\ruff check app tests
   ```
4. **Frontend TypeScript Check**:
   ```bash
   cd frontend && npx tsc --noEmit
   ```
5. **PowerShell Syntax Check**:
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```

### Manual & Visual Verification
- Use `browser_subagent` to open `http://localhost:3000/settings`:
  1. Go to **APIs & Matching** -> Click each of the 3 Unique Names preset buttons (`Record 1`, `Record 2`, `Record 3`) and click "Generate Unique Names" to verify correct outputs (1, 2, 3 unique names).
  2. Go to **Browser & CAPTCHA** -> Verify the single dynamic test button adapts its label/icon when switching between Attended and Headless modes.
  3. Go to **AntiCaptcha Extension** -> Verify `One-Time Extension Toolbar Pinning & Persistent Profile Setup` is positioned ABOVE `Live Browser Launch Test`.
  4. Click `Configure & Pin Extension` -> Verify it completes successfully, displays a green verified card with the valid profile target path, and updates status badge to `Pinned & Verified`.
  5. Capture verification screenshots into `implementation_plan/Images/` and recording into `implementation_plan/Recording/`.
