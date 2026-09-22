# UAIC Claim & RPA Orchestrator — Implementation Plan
## Multi-Engine Fleet Concurrency (1–10x) Across Chrome, Chromium & Edge with Pixel-Perfect UI/UX Alignment

**Implementation ID:** `IMP-2026-0918-009`  
**Date:** September 18, 2026  
**Status:** 🟡 **Awaiting User Approval (Governance Phase: Plan Review)**  
**Target Engines:** Google Chrome (`chrome`, default), Chromium (`chromium`), Microsoft Edge (`msedge`)  
**Fleet Concurrency Scope:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 Parallel Worker Instances  

---

## 1. Executive Summary & Root Cause Diagnosis

### A. Root Causes of Fleet Concurrency Failures
1. **HTTP 422 Schema Validation Failure on `timeout_seconds`:**
   - In `frontend/src/app/settings/page.tsx`, the timeout formula was `Math.max(45, 30 + concurrency * 12)`. For 10 workers, this submitted `150` seconds. The running backend Pydantic validator enforced `le: 120`, causing an immediate rejection:
     ```json
     {"detail":[{"type":"less_than_equal","loc":["body","timeout_seconds"],"msg":"Input should be less than or equal to 120","input":150,"ctx":{"le":120}}]}
     ```
2. **Public Internet Target URL Bottleneck (`https://example.com`):**
   - In `backend/app/api/v1/endpoints/settings.py` (`test_fleet_endpoint`), line 541 defaulted to `https://example.com`. Unlike `test_browser_endpoint` (which substituted the ultra-fast local mock page `http://127.0.0.1:8000/api/v1/settings/browser-test-page`), the fleet endpoint forced up to 10 parallel browser processes to make external DNS lookups and TLS handshakes simultaneously over the public internet, leading to socket contention and timeouts.
3. **Backend Service Schema Hot-Reload:**
   - The in-memory FastAPI process on port 8000 needs an explicit restart/reload to ensure updated Pydantic constraints (`le: 300`) and the local test URL fallback are active.

### B. Root Causes of UI/UX Misalignment in Step 3
1. **Range Slider Tick Misalignment:**
   - Range slider numbers (1 to 10) were arranged with `flex justify-between`. Because native HTML range sliders inset the thumb by its radius (~8px) on both ends, numbers 2 through 9 drifted away from the thumb positions.
2. **Incomplete Quick Presets & Blank Right Margin:**
   - Quick presets only offered values 1, 2, 3, 5, 8, and 10 (skipping 4, 6, 7, 9), leaving an awkward whitespace on the right side of the card (as shown in the user's screenshot).
3. **Lack of Visual Engine & Mode Indicators in Live Fleet Test Card:**
   - The test card lacked clear badge pills indicating the currently active engine (`CHROME`, `CHROMIUM`, `MSEDGE`), execution mode (`Attended` vs `Headless`), and concurrency level.

---

## 2. Proposed Architectural & UI/UX Changes

### Component 1: Backend Fleet Test Endpoint & Schema Alignment
- **File:** `backend/app/api/v1/endpoints/settings.py`
  - In `test_fleet_endpoint`:
    ```python
    test_url = (payload.test_url if payload and payload.test_url else "").strip()
    if not test_url or test_url == "https://example.com":
        test_url = "http://127.0.0.1:8000/api/v1/settings/browser-test-page"
    ```
  - In `_run_worker`: Increase navigation timeout from 15s to 25s to provide ample headroom during 10-worker parallel launch.
  - Dynamically scale server-side timeout: `min_required_timeout = 45 + (concurrency * 10)`.

- **File:** `backend/app/schemas/settings.py`
  - Enforce `timeout_seconds: int = Field(default=45, ge=5, le=300, description="Timeout in seconds per worker")`.

### Component 2: Frontend Settings Page Refinement & UX Alignment
- **File:** `frontend/src/app/settings/page.tsx`
  - **Payload Safety:** In `handleTestFleet`, cap outgoing `timeout_seconds: Math.min(120, Math.max(45, 30 + concurrency * 8))` and set `test_url: "http://127.0.0.1:8000/api/v1/settings/browser-test-page"`, ensuring zero 422 errors regardless of schema caching.
  - **Pixel-Perfect Tick Alignment:** Position tick marks using exact mathematical percentages matching the range slider thumb:
    `style={{ left: \`calc(8px + (100% - 16px) * \${(n - 1) / 9})\` }}` with `-translate-x-1/2`.
  - **Complete 10-Item Symmetrical Presets Grid:** Replace the gapped preset row with a full-width, 10-column segmented selector:
    - `1x (Sequential)`
    - `2x (Duo)`
    - `3x (Trio)`
    - `4x (Quad)`
    - `5x (Half Fleet)`
    - `6x (6-Worker)`
    - `7x (7-Worker)`
    - `8x (High Throughput)`
    - `9x (Ultra)`
    - `10x (Max Speed)`
    Each preset button features synchronized active states, hover transitions, and dark mode support.
  - **Enhanced Fleet Test Console Card:** Add badges for active Browser Engine (`Google Chrome` / `Chromium` / `Microsoft Edge`), Execution Mode (`Attended GUI` / `Headless`), and Worker Concurrency.

---

## 3. Comprehensive Verification Matrix

We will execute tests across all 10 fleet concurrency levels and all 3 browser engines:

| Engine | Concurrency Levels to Test | Modes | Expected Result |
|---|---|---|---|
| **Google Chrome (`chrome`)** | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 | Headless & Attended | 100% Workers OK, isolated profiles, <5ms page load |
| **Chromium (`chromium`)** | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 | Headless & Attended | 100% Workers OK, isolated profiles, <5ms page load |
| **Microsoft Edge (`msedge`)** | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 | Headless & Attended | 100% Workers OK, isolated profiles, <5ms page load |

### Automated Quality Gates
1. `backend/.venv/Scripts/pytest --tb=short -q` (All 453 tests must pass)
2. `backend/.venv/Scripts/ruff check app tests` (0 errors)
3. `frontend/npx tsc --noEmit` (0 errors)
4. `frontend/npm run lint` (0 errors)
5. `frontend/npm run build` (All 11 routes must compile cleanly)
6. `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (0 errors)
7. Browser subagent visual verification of Step 3 UI alignment with recordings and screenshots saved to `implementation_plan/Recording/` and `implementation_plan/Images/`.

---

## 4. Governance & Human Confirmation

In accordance with `.agents/skills/diagnose-plan-confirm-execute/SKILL.md`:
- **NO APPROVAL = NO IMPLEMENTATION.**
- No application code will be modified until explicit user confirmation is received.
