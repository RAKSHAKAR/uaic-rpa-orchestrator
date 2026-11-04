---
name: infrastructure-as-code
description: >-
  Manage reproducible container definitions, Dockerfiles, network bridges, and volumes declaratively.
---

# Infrastructure As Code

## 1. Purpose & Overview
Enforces version-controlled, declarative configuration for all runtime containers, reverse proxies, and background worker infrastructure, eliminating configuration drift.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding new containerized services (e.g. PostgreSQL, Grafana, Nginx).
- Modifying container resource limits (CPU, memory), networks, or port bindings.

### When NOT to Use
- Local code editing within an existing container.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `docker-compose.yml`, Dockerfiles, and container environment variables.

### Prerequisites
- Docker and Docker Compose installed.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Declarative Definition Authoring
Define container services, build contexts, and environment bindings in `docker-compose.yml`.

### Step 2: Resource Limits & Health Check Specification
Specify CPU and memory limits (`deploy.resources.limits`) and explicit healthcheck probe commands.

### Step 3: Persistent Volume Mapping
Define named volumes for data persistence (`db_data`, `redis_data`, `export_data`).

### Step 4: Compose Configuration Validation
Validate syntax: `docker compose config` to verify zero YAML or schema errors.

### Step 5: Container Convergence Test
Run `docker compose up -d` and verify containers converge cleanly to the target state.

### Step 6: Documentation Update
Update `DEPLOYMENT_AND_HOSTING_GUIDE.md` detailing new container resources.


---

## 5. Safety Considerations & Guardrails
- Never hardcode secrets in Dockerfiles or commit unmasked production passwords to compose files.
- Ensure container definitions pin specific base image tags rather than using `:latest`.

---

## 6. Expected Deliverables & Artifacts
- Declarative `docker-compose.yml` and Dockerfiles.
- Updated infrastructure documentation.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] `docker compose config` validates with 0 errors.
- [ ] Containers build and launch deterministically from declarative files.
- [ ] Persistent data survives container teardown and recreation.

---

## 8. Error Recovery & Troubleshooting
- If volume permission errors occur on Linux containers, configure explicit UID/GID mapping in Dockerfiles.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/infrastructure-as-code`. | `CUSTOM SKILL` |
| **Cursor** | Select `@infrastructure-as-code` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `infrastructure-as-code`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `infrastructure-as-code` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run infrastructure-as-code`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt infrastructure-as-code`. | `PROMPT FILE` |
| **Windsurf** | Activate `infrastructure-as-code` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docker-compose.yml`
- `DEPLOYMENT_AND_HOSTING_GUIDE.md`
