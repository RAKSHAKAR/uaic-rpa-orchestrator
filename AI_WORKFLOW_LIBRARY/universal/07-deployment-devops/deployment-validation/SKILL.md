---
name: deployment-validation
description: >-
  Verify system health, critical workflows, logs, and configuration immediately following a software release.
---

# Deployment Validation

## 1. Purpose & Overview
Executes immediate post-deployment smoke tests verifying service availability, database connectivity, worker queue registration, and external portal reachability.

---

## 2. When to Use & When NOT to Use

### When to Use
- Immediately following any production or staging deployment.
- After server reboot or container infrastructure restart.

### When NOT to Use
- During code editing before deployment.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Deployed base URL (`http://localhost:8000` or production domain).

### Prerequisites
- Completed deployment execution.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Basic Health Probe
Send GET request to `/api/v1/health`. Confirm HTTP 200 and `status: ok`.

### Step 2: Detailed Component Health Probe
Send GET request to `/api/v1/health/detailed`. Verify all 8 components (FastAPI, SQLite/PG, Redis, Celery, Playwright, Extension, Settings, Exports) report healthy.

### Step 3: Portal Reachability Ping
Send POST request to `/api/v1/settings/test-portal` for Broward and Dallas. Confirm portal reachability latency is recorded.

### Step 4: Worker Queue Depth Verification
Query `/api/v1/queue/status`. Confirm queues are active and worker concurrency is available.

### Step 5: Frontend Smoke Verification
Navigate to frontend UI on port 3000. Verify dashboard loads with accurate stat card counts.

### Step 6: Deployment Sign-Off
Record validation outcome in deployment log.


---

## 5. Safety Considerations & Guardrails
- If detailed health checks fail any critical component, halt release and trigger rollback.
- Do not allow operational traffic until deployment validation passes 100%.

---

## 6. Expected Deliverables & Artifacts
- Post-Deployment Smoke Test Execution Report.
- Detailed Health JSON response snapshot.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] `/api/v1/health/detailed` reports 100% components healthy.
- [ ] Frontend UI loads cleanly without JavaScript errors.
- [ ] Worker queues report active worker processes.

---

## 8. Error Recovery & Troubleshooting
- If any component reports unhealthy, inspect specific error details in health response and restart failed container.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/deployment-validation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@deployment-validation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `deployment-validation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `deployment-validation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run deployment-validation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt deployment-validation`. | `PROMPT FILE` |
| **Windsurf** | Activate `deployment-validation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/api/v1/endpoints/health.py`
- `docs/STAGE_AND_STATUS_DEFINITIONS.md`
