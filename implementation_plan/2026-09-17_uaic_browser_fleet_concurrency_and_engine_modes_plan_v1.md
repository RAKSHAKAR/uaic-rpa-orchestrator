# Implementation Plan: Browser Automation Fleet Concurrency & Multi-Browser Engine Execution

**Implementation ID:** `IMP-2026-0917-007`  
**Date:** 2026-09-17  
**Author:** AI Agent (Antigravity)  
**Status:** Awaiting User Approval  

---

## 1. Problem Statement & User Requirements

The user requested a complete validation and enhancement of the **Browser Automation & Fleet** tab in Settings (`/settings`):
> *"we have tab called Browser Automation & Fleet in setting page, pls make sure that all the funcaitonality must be properly working based on default selected browser and based on Attended and Hardless. Like- if we run 10 Parallel RPA Concurrency then it must open 10 diff browser to start execution in all parellel, etc..."*

### Key Requirements:
1. **Parallel RPA Fleet Concurrency (1 – 10 Parallel Browsers)**:
   - When concurrency is configured to $N$ (e.g., 2, 3, 5, or 10 parallel claims/workers), the system must be capable of launching $N$ separate, fully isolated browser instances simultaneously in parallel.
   - In **Attended (Visible GUI)** mode, $N$ real desktop browser windows must open on screen concurrently with operator banners indicating the worker index (e.g. `Worker #1/10`, `Worker #2/10`, etc.).
   - In **Headless (Background)** mode, $N$ silent background browser processes must execute simultaneously without window display.
2. **Profile Lock Elimination for Parallel Workers**:
   - When multiple Chrome/Chromium instances launch at the exact same time, Chromium's singleton directory lock (`SingletonLock`) prevents multiple instances from using the same user data directory.
   - Each concurrent worker must be given an isolated profile directory dynamically pre-seeded with the extension configuration and toolbar pinning preferences so all parallel instances run without lock collisions.
3. **Selected Browser Engine Consistency**:
   - Full support across **Chromium (Bundled)**, **Google Chrome (Installed)**, and **Microsoft Edge (Supported)** across both single-browser tests and multi-browser fleet concurrency executions.
4. **Interactive Fleet Concurrency Tester in Settings UI**:
   - Add a dedicated **"Test Parallel Fleet Launch"** action inside the *Parallel RPA Concurrency* card in Settings.
   - The button dynamically reflects the selected concurrency (e.g., `Test Fleet (3 Parallel Browsers)` or `Test Fleet (10 Parallel Browsers)`).
   - Shows live multi-worker status cards displaying individual worker latencies, engine used, attended/headless mode, and extension status.

---

## 2. Proposed Architectural & Code Changes

### Backend Architecture (`backend/app`)

#### 1. [MODIFY] [backend/app/automation/session_runner.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py)
- Update profile initialization in `SingleSessionBrowserRunner` to ensure complete parallel isolation:
  - For each session, create an isolated worker directory (e.g. `uaic_worker_profile_<unique_id>`).
  - Pre-seed the worker directory with preferences from `data/browser_profile` (or user-configured profile), including extension settings and toolbar pinning.
  - This guarantees that 10 parallel claim scrapers can execute at the exact same time without profile locking errors.
- Support `browser_engine` setting (`chrome`, `chromium`, `edge`/`msedge`) with proper executable path resolution and authentic engine user-agent.

#### 2. [MODIFY] [backend/app/schemas/settings.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/settings.py)
- Add schemas for Parallel Fleet Concurrency testing:
  ```python
  class FleetWorkerResult(BaseModel):
      worker_id: int
      browser_engine: str
      mode: str
      status: str
      duration_ms: float
      message: str
      extension_loaded: bool

  class FleetTestRequest(BaseModel):
      concurrency: int = Field(default=2, ge=1, le=10)
      headless: bool | None = None
      browser_engine: str | None = None
      timeout_seconds: int = 35

  class FleetTestResponse(BaseModel):
      success: bool
      concurrency_requested: int
      concurrency_succeeded: int
      browser_engine: str
      mode: str
      total_fleet_duration_ms: float
      workers: list[FleetWorkerResult]
      message: str
  ```

#### 3. [MODIFY] [backend/app/api/v1/endpoints/settings.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/settings.py)
- Implement `@router.post("/test-fleet", response_model=FleetTestResponse)`:
  - Takes `concurrency` (1 to 10), `headless`, and `browser_engine`.
  - Spawns $N$ independent `ChromeSession` instances concurrently using `asyncio.gather()`.
  - In Attended mode, each window positions itself with an offset and displays a visual banner:
    `"UAIC Fleet Worker #<ID>/<N> (<Engine> Attended)"`.
  - Each worker navigates, verifies extension readiness, and calculates worker latency.
  - Returns structured results for all $N$ workers.

---

### Frontend UI/UX (`frontend/src`)

#### 4. [MODIFY] [frontend/src/lib/api.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/lib/api.ts) & [frontend/src/types/index.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/types/index.ts)
- Add TypeScript types for `FleetTestRequest`, `FleetTestResponse`, and `FleetWorkerResult`.
- Add `testFleet(payload: FleetTestRequest): Promise<FleetTestResponse>` to `api`.

#### 5. [MODIFY] [frontend/src/app/settings/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)
- Inside the **Parallel RPA Concurrency** card:
  - Add a **"Test Parallel Fleet Launch"** action bar:
    - Displays `[ 🚀 Test Parallel Fleet Launch ({max_concurrent_claims} Parallel Browsers) ]` button.
    - Shows progress spinner during multi-browser execution.
  - Render a rich **Fleet Concurrency Results Matrix**:
    - Summary badge: `Concurrency: {N}x Parallel Workers • Total Fleet Time: {time}ms • Status: 100% Passed`.
    - Grid of worker cards (Worker #1, Worker #2, ... up to Worker #N) showing individual worker latencies, engine badge, mode badge, and status.
- Ensure all other controls in the tab (engine selection, attended/headless toggle, speed sliders, timeouts) are fully connected and synchronized with runtime settings.

---

## 3. Verification Plan

### Automated Tests
1. `pytest tests/test_imp_2026_0912_001.py` & new unit test for fleet concurrency.
2. `ruff check app tests` (0 errors).
3. `npx tsc --noEmit` (0 errors).
4. `npm run lint` (0 errors).
5. `scripts\check_ps1_syntax.ps1` (0 errors).

### Live Browser & Functional Verification
1. Open Settings -> Tab 3 (*Browser Automation & Fleet*).
2. Test Concurrency at **1 Worker (Sequential Default)**:
   - Click "Test Parallel Fleet Launch (1 Worker)".
   - Verify single browser launch and verification.
3. Test Concurrency at **3 Workers (Parallel Fleet)**:
   - Click "Test Parallel Fleet Launch (3 Parallel Workers)".
   - In Attended mode: verify 3 separate browser windows launch in parallel on screen.
   - In Headless mode: verify 3 headless background workers run in parallel.
4. Test Concurrency at **10 Workers (Max Concurrency Fleet)**:
   - Click "Test Parallel Fleet Launch (10 Parallel Workers)".
   - Verify 10 parallel instances execute with zero profile locking errors.
5. Capture screen recordings and screenshots of multi-browser fleet concurrency into `implementation_plan/Images/` and `implementation_plan/Recording/`.
