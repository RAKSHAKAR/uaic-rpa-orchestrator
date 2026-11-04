---
name: local-setup
description: >-
  Validate local prerequisites, startup commands, persistent launcher scripts (setup_local.ps1), and health checks.
---

# Local Setup

## 1. Purpose & Overview
Maintains and executes the unified local launcher script (`setup_local.ps1`), launching FastAPI, Next.js, Redis, and Celery workers in coordinated, persistent terminal windows.

---

## 2. When to Use & When NOT to Use

### When to Use
- Starting up the local development stack for daily development.
- Updating launcher configuration or troubleshooting process startup failures.

### When NOT to Use
- Deploying to production Linux servers (use `docker-setup` or `production-deployment`).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `setup_local.ps1`, installed dependencies, and port availability.

### Prerequisites
- Completed `environment-setup`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Port Availability Pre-Flight Check
Verify ports 8000 (FastAPI), 3000 (Next.js), and 6379 (Redis) are free from stale orphan processes.

### Step 2: Launcher Syntax Validation
Run `scripts/check_ps1_syntax.ps1` to confirm `setup_local.ps1` syntax is 100% valid.

### Step 3: Persistent Stack Startup
Execute `powershell -ExecutionPolicy Bypass -File setup_local.ps1`. Verify interactive terminal remains persistent and does NOT auto-exit.

### Step 4: Component Health Check Verification
Wait for services to initialize. Query `http://localhost:8000/api/v1/health` and `http://localhost:3000`.

### Step 5: Celery Worker Registration Audit
Verify that Celery workers register all queues (`scrapers`, `matcher`, `guidewire`, `ingest`, `export`, `retry`, `notifications`).

### Step 6: Startup Summary Output
Display URLs for Dashboard (3000), API Swagger Docs (8000/docs), and Health Check.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: PowerShell launcher must NEVER auto-exit after launching services; it must remain persistent and interactive.
- Ensure launcher gracefully terminates child processes on Ctrl+C.

---

## 6. Expected Deliverables & Artifacts
- Active local running stack across all tiers.
- Verified health check response from all services.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] `setup_local.ps1` executes without errors and stays open.
- [ ] Both frontend (3000) and backend (8000) respond with HTTP 200.
- [ ] Celery workers actively consume tasks from Redis.

---

## 8. Error Recovery & Troubleshooting
- If launcher exits immediately, run `scripts/clean_stale_workers.py` to kill port collisions and retry.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/local-setup`. | `CUSTOM SKILL` |
| **Cursor** | Select `@local-setup` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `local-setup`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `local-setup` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run local-setup`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt local-setup`. | `PROMPT FILE` |
| **Windsurf** | Activate `local-setup` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `setup_local.ps1`
- `AGENTS.md` - Section 8 (Must Do)
