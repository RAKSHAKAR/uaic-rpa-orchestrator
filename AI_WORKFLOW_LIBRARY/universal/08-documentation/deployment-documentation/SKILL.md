---
name: deployment-documentation
description: >-
  Document repeatable local setup, Docker deployment, and production hosting instructions step-by-step.
---

# Deployment Documentation

## 1. Purpose & Overview
Maintains comprehensive, copy-pasteable deployment guides covering Windows local development (`setup_local.ps1`), Docker container orchestration, and cloud hosting.

---

## 2. When to Use & When NOT to Use

### When to Use
- Updating deployment guides (`DEPLOYMENT.md`, `DEPLOYMENT_AND_HOSTING_GUIDE.md`).
- Changing port configurations, environment variables, or container definitions.

### When NOT to Use
- Daily coding.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Deployment scripts (`setup_local.ps1`, `docker-compose.yml`), environment prerequisites, and hosting configurations.

### Prerequisites
- Verified working deployment on local and containerized environments.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Local Windows Setup Instructions
Document exact PowerShell commands for cloning, virtualenv setup, dependency installation, and running `setup_local.ps1`.

### Step 2: Docker Deployment Instructions
Document `docker compose up -d` workflow, volume mappings, and container health check verification.

### Step 3: Production Hosting Architecture
Document production Linux hosting: Nginx reverse proxy, systemd service units, SSL certificates, and PostgreSQL migration.

### Step 4: Troubleshooting Section
Provide actionable troubleshooting guidance for port collisions, permission errors, and container crashes.

### Step 5: Review & Sync
Reconcile `DEPLOYMENT.md` with `README.md`.


---

## 5. Safety Considerations & Guardrails
- Test every documented command on a fresh workstation to confirm copy-paste accuracy.
- Never include production API keys or database passwords in deployment guides.

---

## 6. Expected Deliverables & Artifacts
- Updated `DEPLOYMENT.md` and `DEPLOYMENT_AND_HOSTING_GUIDE.md`.
- Verified setup runbooks.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Step-by-step commands allow a new developer to bring up the stack within 15 minutes.
- [ ] Local, Docker, and Production hosting modes are thoroughly covered.
- [ ] Troubleshooting section resolves common port and permission issues.

---

## 8. Error Recovery & Troubleshooting
- If a command fails on a clean machine, revise the script or document missing prerequisites.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/deployment-documentation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@deployment-documentation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `deployment-documentation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `deployment-documentation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run deployment-documentation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt deployment-documentation`. | `PROMPT FILE` |
| **Windsurf** | Activate `deployment-documentation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `DEPLOYMENT.md`
- `DEPLOYMENT_AND_HOSTING_GUIDE.md`
