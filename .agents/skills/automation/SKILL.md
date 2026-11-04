---
name: automation
description: >-
  Design, schedule, and validate recurring automated background jobs, Celery beats, and cron schedules safely.
---

# Automation

## 1. Purpose & Overview
Guides the authoring and monitoring of scheduled background tasks, recurring cron routines, and automated queue runners with safeguards against runaway loops and data corruption.

---

## 2. When to Use & When NOT to Use

### When to Use
- Configuring recurring queue runners (`queue_runner.py`), retry monitors, or periodic cleanup tasks.
- Responding to `/schedule` or `/automation` slash commands.

### When NOT to Use
- One-time interactive commands.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Task function, schedule interval/cron expression, concurrency limits, and retry policy.

### Prerequisites
- Celery Beat or scheduler capability.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Schedule Specification
Define execution cadence using cron syntax or interval (e.g. `schedule(CronExpression='*/5 * * * *')`). Avoid shell sleep commands.

### Step 2: Idempotency & Lock Guard
Implement distributed Redis lock (`redis.lock`) ensuring only one instance of the automated task runs at any time.

### Step 3: Task Implementation
Implement async task in `backend/app/tasks/` with bounded execution timeouts and structured logging.

### Step 4: Failure & Retry Handling
Configure exponential backoff and maximum retry limits (`max_retries=3`). Route dead-letter items to alert queue.

### Step 5: Monitoring & Telemetry
Expose automation health status on `/api/v1/queue/auto-mode` and `/health`.

### Step 6: Verification Pass
Simulate schedule execution; verify task executes, acquires lock, commits state, and releases lock.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never use shell `sleep` loops as long-running schedulers.
- Always enforce distributed locks to prevent overlapping duplicate runs of automated tasks.

---

## 6. Expected Deliverables & Artifacts
- Scheduled automation task with distributed lock protection.
- Schedule configuration in Celery Beat or scheduler service.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Task triggers reliably at configured interval.
- [ ] Distributed locks prevent concurrent duplicate execution.
- [ ] Failure handling and alert dispatch function predictably.

---

## 8. Error Recovery & Troubleshooting
- If automated task stalls, release stale Redis lock after TTL expiration and log timeout error.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke native slash command `/schedule` or `/automation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@automation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `automation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `automation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run automation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt automation`. | `PROMPT FILE` |
| **Windsurf** | Activate `automation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/tasks/queue_runner.py`
- `backend/app/core/celery_app.py`
