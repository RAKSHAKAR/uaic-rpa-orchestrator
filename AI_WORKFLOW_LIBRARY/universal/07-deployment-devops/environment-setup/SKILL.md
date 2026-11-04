---
name: environment-setup
description: >-
  Prepare documented development, test, and production-like environments with reproducible runtime dependencies.
---

# Environment Setup

## 1. Purpose & Overview
Guides the provisioning of clean, reproducible Python 3.14.7 virtual environments, Node.js runtimes, Redis brokers, and Playwright browser binaries across host systems.

---

## 2. When to Use & When NOT to Use

### When to Use
- Setting up a new development workstation or CI runner.
- Re-provisioning corrupted Python virtual environments or Node modules.

### When NOT to Use
- Day-to-day code editing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Installed Python 3.14.7, Node.js 18+, Redis, and repository source code.

### Prerequisites
- Operating system administrative privileges to install runtimes and browser drivers.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Python Runtime & Virtualenv Setup
Verify Python 3.14.7. Create virtualenv: `python -m venv backend/.venv`. Upgrade pip: `.venv\Scripts\python -m pip install --upgrade pip`.

### Step 2: Backend Dependency Installation
Install pinned backend dependencies: `.venv\Scripts\pip install -r backend/requirements.txt`.

### Step 3: Playwright Chromium Installation
Install Playwright browser binaries: `.venv\Scripts\playwright install chromium`.

### Step 4: Frontend Node Module Setup
Install frontend packages: `cd frontend && npm install`.

### Step 5: Environment Variable Initialization
Copy `.env.example` to `backend/.env` and `frontend/.env.local` if missing. Configure absolute database path and Redis URL.

### Step 6: Health Check Pass
Run `scripts/check_ps1_syntax.ps1` and test suite to confirm operational readiness.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Pin Python strictly to 3.14.7; avoid untested Python 3.15 alphas.
- Never commit active `.env` files containing live credentials.

---

## 6. Expected Deliverables & Artifacts
- Fully provisioned, healthy local development environment.
- Environment readiness verification log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Python 3.14.7 virtualenv runs `pytest` cleanly.
- [ ] Frontend `npm run build` succeeds.
- [ ] Redis broker is reachable on port 6379.

---

## 8. Error Recovery & Troubleshooting
- If virtualenv becomes corrupted, delete `backend/.venv` and recreate from scratch.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/environment-setup`. | `CUSTOM SKILL` |
| **Cursor** | Select `@environment-setup` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `environment-setup`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `environment-setup` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run environment-setup`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt environment-setup`. | `PROMPT FILE` |
| **Windsurf** | Activate `environment-setup` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/requirements.txt`
- `frontend/package.json`
- `setup_local.ps1`
