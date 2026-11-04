---
name: uaic-queue-management
description: >-
  Manage and validate Celery queues, worker prefetch, task states, automatic auto-queue runner, and retries.
---

# Uaic Queue Management

## 1. Purpose & Overview
Manages asynchronous Celery task execution across all 7 queues (`scrapers`, `matcher`, `guidewire`, `ingest`, `export`, `retry`, `notifications`), ensuring smooth sequential processing and auto-queue recovery.

---

## 2. When to Use & When NOT to Use

### When to Use
- Starting, pausing, or retriggering the queue via API (`/api/v1/queue/*`).
- Configuring Celery worker concurrency, prefetch multipliers, and task timeouts.
- Toggling auto-queue mode (`/api/v1/queue/auto-mode`).

### When NOT to Use
- Synchronous local script execution.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Celery application instance (`backend/app/core/celery_app.py`) and Redis broker connection.

### Prerequisites
- Active Redis server on port 6379.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Queue Status Inspection
Query `/api/v1/queue/status` or run `scripts/check_celery_workers.py`. Inspect active tasks, queue lengths, and worker PIDs.

### Step 2: Auto-Queue Loop Operation
Verify auto-queue runner (`queue_runner.py`) polls for claims in `READY` or `NEW` status, triggers automation sequentially, and throttles concurrency.

### Step 3: Worker Restart Reconciliation
Run `reconcile_worker_restart_claims_sync()` upon worker restart to detect orphan claims stuck in `RUNNING` and reset to `READY`.

### Step 4: Queue Pause & Drain
Test queue pause endpoint (`POST /api/v1/queue/pause`). Confirm in-flight tasks finish while pending tasks wait.

### Step 5: Failed Claim Retriggering
Trigger retrigger endpoint (`POST /api/v1/queue/retrigger`). Verify failed claims reset to `READY` with incremented retry count.


---

## 5. Safety Considerations & Guardrails
- Ensure worker reconciliation runs on every worker restart to prevent permanently orphaned claims.
- Do not allow prefetch multiplier > 1 on scraper queues to prevent worker hoarding.

---

## 6. Expected Deliverables & Artifacts
- Healthy, active Celery queue pipeline.
- Queue telemetry and worker reconciliation logs.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All 7 queues actively process tasks without stalling.
- [ ] Worker restart cleanly reconciles orphaned claims.
- [ ] Queue pause and retrigger endpoints operate reliably.

---

## 8. Error Recovery & Troubleshooting
- If Celery workers desynchronize from Redis, restart workers using `scripts/restart_celery.ps1`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-queue-management`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-queue-management` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-queue-management`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-queue-management` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-queue-management`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-queue-management`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-queue-management` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md`
- `backend/app/tasks/queue_runner.py`
