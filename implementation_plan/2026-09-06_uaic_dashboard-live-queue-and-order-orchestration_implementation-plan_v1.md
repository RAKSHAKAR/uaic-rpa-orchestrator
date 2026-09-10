# Implementation Plan — Dashboard Live Queue Orchestrator & Sequential FIFO Pipeline

Implementation ID:   IMP-2026-0906-001  
Project:             UAIC Claim & RPA Orchestrator  
Module:              frontend / backend / queue / dashboard / automation  
Feature / Issue:     Dashboard Live Running Queue & Ordered Pending Items Visualization with Sequential Auto-Pick Orchestration  
Document Type:       Implementation Plan  
Version:             v1  
Status:              Awaiting Approval  
Created:             2026-09-06  
Last Updated:        2026-09-06  
AI Agent:            Antigravity  
Approval Status:     Pending  
Approved By:         Pending  
Approval Date:       Pending  
Verification Status: AI Generated — Awaiting Human Verification  
Primary Reference:   User Directive: Dashboard Improvement for Live Running Queue Items & Ordered Pending Queue with Sequential Next-Item Auto-Execution  
Authoritative Architectural Reference: `PowerAutomateSolutions/BotCreation_1_0_0_7/` (V4)  

---

## 1. Executive Summary & Objective

The user specifically requested:
> *"pls work on improvement of dashboard also... you can show live running queue items and pending items in order so that when item successfully runs it should pick the next item"*

Currently, the Main Dashboard (`/` or `frontend/src/app/page.tsx`) displays static lifecycle counts and an uncurated claims table. Operators have **zero live visibility** into:
1. Which claim is actively executing in the RPA browser/fuzzy matching pipeline right now.
2. The ordered list of pending queue items waiting in line to be picked next (FIFO priority order: #1 Next, #2 in Line, #3 in Line...).
3. Real-time visual feedback and state transitions as an item completes and the runner automatically advances to execute the next pending claim.
4. Quick queue controls on the Dashboard (Pause/Resume Auto-Queue, Run Next Claim, Start All Pending).

This implementation plan delivers a state-of-the-art **Live Queue & Sequential RPA Execution Console** integrated directly into the Main Dashboard, backed by a dedicated real-time backend API and auto-advancing queue runner.

---

## 2. Forensic Gap Analysis & Target Architecture

| Area | Current State | Root Cause | Target Solution |
|---|---|---|---|
| **Live Active Item** | Dashboard doesn't show what claim is currently being scraped | No live queue state endpoint; dashboard only loads initial 200 claims | Build `GET /api/v1/queue/live` returning `active_item` with live bot statuses, elapsed time, current portal/stage, and jurisdiction routing |
| **Ordered Pending Queue** | No visual queue pipeline; pending claims are scattered in the general table | Missing queue-order ranking query (`created_at ASC` where status = `NEW`) | Add `pending_items` to `GET /api/v1/queue/live` with explicit `queue_position` (#1 Next, #2, #3...), estimated bots (FL 3 / TX 5 / 8 cross-state), and FIFO priority |
| **Sequential Next Pick** | When a bot session encounters a browser crash/exception in `scraper_tasks.py`, auto-queue could hang | Scraper session exception handler did not reset `active_item_id` or dispatch `advance_auto_queue_task` | Add exception recovery in `scraper_tasks.py` to auto-clear active lock and trigger `advance_auto_queue_task` immediately |
| **Live UI Polling & Transitions** | Dashboard is static; requires manual refresh to see state changes | No reactive polling on `/` | Implement dynamic polling (every 3 seconds when queue is active/running) that smoothly animates the transition from Pending -> Active -> Completed |
| **Queue Controls on Dashboard** | Operator must navigate to `/monitor` or `/settings` to manage the queue | Missing dashboard orchestration toolbar | Add unified Auto-Queue toggle (`ACTIVE` / `PAUSED`), `Process Next Claim`, and `Start All Pending` buttons directly on Dashboard |
| **Top Metric Cards** | Dashboard still uses plain `<div>` containers instead of reusable `<StatCard />` | Pre-dates the reusable `<StatCard />` component | Upgrade all 6 Dashboard KPI cards to `<StatCard />` with active selection and click-to-filter support |

---

## 3. Detailed Proposed Changes

### Component A: Backend Queue Engine & Schemas
1. **[MODIFY] `backend/app/schemas/queue.py`**:
   - Add `LiveQueueItemResponse`:
     - `id: str`
     - `claim_number: str`
     - `insured_name: str | None`
     - `claimant_name: str | None`
     - `policy_state: str | None`
     - `loss_location_state: str | None`
     - `record_status: str`
     - `queue_position: int | None` (1 for next in line, 2, 3...)
     - `portals_to_run: list[str]`
     - `bot_statuses: dict[str, str]` (per-county status)
     - `total_duration_seconds: float | None`
     - `created_at: datetime`
   - Add `LiveQueueStateResponse`:
     - `auto_queue_enabled: bool`
     - `is_running: bool`
     - `active_item: LiveQueueItemResponse | None`
     - `pending_items: list[LiveQueueItemResponse]`
     - `recently_completed: list[LiveQueueItemResponse]`
     - `total_pending_count: int`
     - `total_in_progress_count: int`
     - `workers_online: int`

2. **[MODIFY] `backend/app/api/v1/endpoints/queue.py`**:
   - Add `@router.get("/live", response_model=LiveQueueStateResponse)`:
     - Queries Redis `active_item_id` and checks database for any currently scraping claim (`record_status in [SCRAPING_IN_PROGRESS, SEARCHING]`).
     - Queries `NEW` claims ordered by `created_at ASC` (FIFO queue) with calculated state routing (`portals_to_run`).
     - Queries recently completed claims (last 3).
     - Returns live structured queue state.
   - Add `@router.post("/run-next")`:
     - Dispatches `advance_auto_queue_task` to immediately pick and execute the #1 pending item in line.

3. **[MODIFY] `backend/app/tasks/scraper_tasks.py`**:
   - In `_async_orchestrate_scrapers` exception handler:
     - Clear `active_item_id` in Redis.
     - If `is_auto_queue_enabled()`, send `advance_auto_queue_task` to prevent queue stalling on browser crashes.

### Component B: Frontend API Client & Types
1. **[MODIFY] `frontend/src/types/index.ts`**:
   - Add `LiveQueueItem` and `LiveQueueState` interfaces matching backend schemas.
2. **[MODIFY] `frontend/src/lib/api.ts`**:
   - Add `api.getLiveQueue(): Promise<LiveQueueState>`.
   - Add `api.runNextQueueItem(): Promise<{ status: string; message: string }>`.

### Component C: Main Dashboard Redesign (`frontend/src/app/page.tsx`)
1. **Top KPI Metric Cards**:
   - Replace old card containers with `<StatCard />` components (Total Ingested, In Queue / Processing, Matches Confirmed, Manual Exceptions, Completed Scrapes, Failed/Retried) with click-to-filter support.
2. **Live Queue & RPA Execution Console (NEW)**:
   - **Header Bar**:
     - Status Indicator: `AUTO-QUEUE: ACTIVE (SEQUENTIAL FIFO)` with pulsing green radar vs. `PAUSED / MANUAL`.
     - Controls:
       - Auto-Queue Toggle switch (`Pause Queue` / `Resume Auto Queue`).
       - `Process Next Now` button (picks #1 claim immediately).
       - `Start All Pending` button.
       - Live Sync Radar with animated polling indicator.
   - **Two-Column Interactive Grid**:
     - **Left: Active Running Execution Card**:
       - When active: Glowing border, animated radar ping "BOT AUTOMATION ACTIVE".
       - Shows Claim Number, Insured, Claimant, Loss Location & Policy State.
       - Route badge: `FL 3 Portals` / `TX 5 Portals` / `Cross-State 8 Portals`.
       - Mini 8 Bots execution ribbon: live status pills (Spinning loader for In Progress, Check for Completed, Red X for Failed, Clock for Pending).
       - Live duration stopwatch / elapsed timer.
       - "Open Live Stages" button linking to claim inspector.
       - When idle: Clean standby card: "Orchestrator Idle — Ready for Next Ingestion".
     - **Right: Sequential Pending Queue Pipeline**:
       - Card list showing claims in exact execution order:
         - `#1 NEXT IN LINE` (highlighted emerald/indigo badge).
         - `#2 IN LINE`, `#3 IN LINE`, etc.
         - Shows Claim Number, Insured Name, State, Ingested Date/Time, and target portals.
         - Instant "Run This Now" action button.
   - **Reactive Transition Polling**:
     - Polls `/api/v1/queue/live` every 3 seconds while queue is active or items are in progress.
     - When the running claim finishes (scrapes + fuzzy match), the UI flashes a transition alert, advances the queue, and moves #1 into the Active box seamlessly!
3. **Dashboard Table Quick Tabs**:
   - `All Claims (N)`, `Live Running (N)`, `Pending Next (N)`, `Matches (N)`, `Exceptions (N)`, `Completed (N)`.

---

## 4. Verification & Testing Plan

### 4.1 Automated Backend & Quality Tests
```bash
# 1. Backend tests (verify live queue endpoint and runner)
cd backend
.venv\Scripts\pytest tests/test_queue.py tests/test_queue_runner.py -q
.venv\Scripts\pytest --tb=short -q

# 2. Ruff lint
.venv\Scripts\ruff check app tests

# 3. Frontend TypeScript
cd frontend
npx tsc --noEmit

# 4. Production Build
npm run build

# 5. PowerShell syntax
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"

# 6. Corporate domain safety
python scripts/find_uaic_emails.py
```

### 4.2 Browser End-to-End Verification
1. Open `http://localhost:3000/` in browser subagent.
2. Verify **Live Queue & RPA Execution Console** is visible at the top of the dashboard.
3. Verify top KPI cards use `<StatCard />`.
4. Trigger Auto-Queue or Run Next and verify the active item appears in the running card with live duration and portal pills.
5. Verify pending queue items are listed in order (`#1 Next`, `#2 in Line`, `#3 in Line`).
6. Observe item completion and verify the next pending item is picked automatically.
7. Capture browser recording and screenshots.

---

## 5. Governance & Constraints Compliance
- Strictly pure Light and Dark modes only, zero OS auto-detection.
- Zero corporate domain email leakage (`find_uaic_emails.py` 100% clean).
- All 5 protected user directories remain untouched.
- Single Source of Truth maintained in `implementation_plan/`.
