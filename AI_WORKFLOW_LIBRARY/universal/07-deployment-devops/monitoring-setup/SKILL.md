---
name: monitoring-setup
description: >-
  Configure health check endpoints (/health/detailed), queue depth monitoring, portal reachability pings, and operational alerts.
---

# Monitoring Setup

## 1. Purpose & Overview
Establishes real-time observability into application health, Celery queue processing rates, portal reachability latency, and worker error rates.

---

## 2. When to Use & When NOT to Use

### When to Use
- Configuring operational monitoring dashboards or uptime alert triggers.
- Extending `/api/v1/health/detailed` with new subsystem health probes.

### When NOT to Use
- Internal function unit testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target metrics to monitor, health check route definitions, and alert thresholds.

### Prerequisites
- FastAPI monitoring endpoints in `app/api/v1/endpoints/health.py`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Detailed Health Probe Implementation
Implement `/api/v1/health/detailed` querying status, latency, and connectivity across all 8 components and 8 portals.

### Step 2: Queue Depth Metric Extraction
Query Redis queue lengths and active worker counts in Celery inspection tasks.

### Step 3: Portal Reachability Pinger
Implement lightweight HTTP HEAD probe (`/api/v1/health/portals/{key}/ping`) testing court portal responsiveness.

### Step 4: Email & Notification Trigger Rules
Configure automated notification rules (`NotificationRule`) dispatching alerts on worker failure or queue stall.

### Step 5: Frontend Monitoring View Integration
Expose live health metrics on `/health` and real-time queue telemetry on `/monitor`.

### Step 6: Verification Pass
Simulate service failure (e.g. pause Redis) and verify monitoring endpoint accurately flags degraded status.


---

## 5. Safety Considerations & Guardrails
- Ensure health check endpoints execute with low overhead and short timeouts (< 5s) to prevent health check hangs.
- Never expose sensitive internal network topologies in public health checks.

---

## 6. Expected Deliverables & Artifacts
- Comprehensive health check and telemetry endpoints.
- Operational monitoring view on `/health` and `/monitor`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] `/api/v1/health/detailed` reports status for all components and portals.
- [ ] Queue depth and active worker metrics update in real time.
- [ ] Simulated failures trigger accurate degradation warnings.

---

## 8. Error Recovery & Troubleshooting
- If portal pings cause rate-limiting, cache portal health status with 60-second TTL.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/monitoring-setup`. | `CUSTOM SKILL` |
| **Cursor** | Select `@monitoring-setup` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `monitoring-setup`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `monitoring-setup` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run monitoring-setup`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt monitoring-setup`. | `PROMPT FILE` |
| **Windsurf** | Activate `monitoring-setup` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/api/v1/endpoints/health.py`
- `frontend/src/app/health/page.tsx`
