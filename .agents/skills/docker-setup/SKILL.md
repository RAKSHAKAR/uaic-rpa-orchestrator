---
name: docker-setup
description: >-
  Create, repair, and orchestrate containerized environments using docker-compose.yml, volume mounts, and health checks.
---

# Docker Setup

## 1. Purpose & Overview
Manages full-stack containerization via Docker and Docker Compose, configuring isolated containers for Backend, Celery Workers, Frontend, Redis, and PostgreSQL with persistent volumes.

---

## 2. When to Use & When NOT to Use

### When to Use
- Deploying the platform via Docker containers.
- Troubleshooting container networking, volume mounts, or health check failures.

### When NOT to Use
- Attended GUI browser scraping requiring local Windows Chrome desktop sessions.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `docker-compose.yml`, Dockerfiles, and environment variables.

### Prerequisites
- Docker Desktop or Docker Engine installed and running.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Configuration Audit
Inspect `docker-compose.yml`. Verify service definitions: `backend`, `frontend`, `redis`, `celery_worker`.

### Step 2: Volume & Network Configuration
Configure persistent named volumes for database data, uploads (`uploads/`), and exports (`exports/`). Ensure shared bridge network.

### Step 3: Container Build Pass
Build images using `docker compose build --no-cache` to ensure clean package resolution.

### Step 4: Container Startup
Start container stack: `docker compose up -d`.

### Step 5: Health Check Probing
Monitor container health status (`docker compose ps`). Verify each service transitions from starting to healthy.

### Step 6: Log Telemetry Inspection
Inspect combined container logs (`docker compose logs -f --tail=100`) for startup warnings or database connection errors.


---

## 5. Safety Considerations & Guardrails
- Ensure container volumes map to persistent storage so database state is not lost upon container destruction.
- Do not expose Redis or database ports directly to public untrusted networks without authentication.

---

## 6. Expected Deliverables & Artifacts
- Production-ready `docker-compose.yml` and Dockerfiles.
- Healthy, running container stack.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All services (`backend`, `frontend`, `redis`, `celery_worker`) report healthy status.
- [ ] Frontend at `http://localhost:3000` successfully queries backend via internal Docker network.
- [ ] Container restarts preserve database records.

---

## 8. Error Recovery & Troubleshooting
- If backend fails to connect to Redis, verify container service name matches `REDIS_URL` hostname.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/docker-setup`. | `CUSTOM SKILL` |
| **Cursor** | Select `@docker-setup` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `docker-setup`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `docker-setup` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run docker-setup`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt docker-setup`. | `PROMPT FILE` |
| **Windsurf** | Activate `docker-setup` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docker-compose.yml`
- `DEPLOYMENT_AND_HOSTING_GUIDE.md`
