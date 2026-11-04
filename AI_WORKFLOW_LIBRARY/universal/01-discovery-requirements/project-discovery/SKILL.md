---
name: project-discovery
description: >-
  Understand the product purpose, users, repository structure, tech stack, and current baseline state before planning or writing code.
---

# Project Discovery

## 1. Purpose & Overview
Provides a systematic, non-invasive protocol to inspect an unknown or existing repository, understand its core business value, identify primary actors and users, catalogue root directories, detect technologies, and establish an operational baseline.

---

## 2. When to Use & When NOT to Use

### When to Use
- Initial onboarding onto a new codebase or unfamiliar repository.
- Starting a major new initiative or architectural review.
- Re-aligning project assumptions after major team or dependency updates.

### When NOT to Use
- Trivial single-line hotfixes where the codebase context is already thoroughly verified.
- Mid-flight execution of an already approved and ongoing implementation plan.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Access to workspace root directory.
- Read access to repository configuration files (`package.json`, `pyproject.toml`, `requirements.txt`, `docker-compose.yml`, `README.md`).

### Prerequisites
- Terminal read-only execution capabilities (directory listing, file reading).
- Zero destructive command authorization (strictly passive discovery).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Root Directory & Configuration Survey
Enumerate root-level files and directories. Inspect package descriptors (`package.json`, `requirements.txt`, `.env.example`, `docker-compose.yml`) to identify language runtimes, package managers, and core frameworks.

### Step 2: README & Documentation Review
Read the primary `README.md`, architecture manuals, and historical project docs. Extract stated project identity, business objectives, and supported environments.

### Step 3: Service & Entrypoint Mapping
Identify frontend entrypoints (e.g., Next.js `src/app/page.tsx`), backend entrypoints (e.g., FastAPI `app/main.py`), and background worker queues (e.g., Celery tasks).

### Step 4: Data Store & External Service Identification
Detect database engines (PostgreSQL, SQLite), caches/brokers (Redis), third-party APIs (Guidewire, SMTP), and integration endpoints.

### Step 5: Synthesis & Baseline Documentation
Synthesize findings into a structured discovery brief summarizing the project purpose, architecture, primary workflows, and operational state.


---

## 5. Safety Considerations & Guardrails
- Do NOT modify or delete any files during discovery.
- Do NOT run active mutation scripts or connect to external production services.
- Never expose unmasked credentials or tokens found in `.env` files.

---

## 6. Expected Deliverables & Artifacts
- Structured Project Discovery Brief in `docs/` or session artifact.
- High-level directory and service topology map.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Product identity, primary users, and core workflows are explicitly documented.
- [ ] Languages, frameworks, package managers, and runtimes are verified with exact versions.
- [ ] Database, queue, and external service touchpoints are identified.
- [ ] Zero project files modified during execution.

---

## 8. Error Recovery & Troubleshooting
- If package files are missing or malformed, search for lock files (`package-lock.json`, `poetry.lock`) or environment files.
- If project documentation is missing or outdated, rely directly on source code inspection and test files.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/project-discovery` or ask the agent to run project discovery. | `CUSTOM SKILL` |
| **Cursor** | Select `@project-discovery` rule in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Reference `project-discovery` skill in Claude Code prompt. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `project-discovery` workflow in Codex prompt. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run project-discovery` or GEMINI.md guideline. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt project-discovery`. | `PROMPT FILE` |
| **Windsurf** | Activate `project-discovery` workflow rule in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 1 (Project Identity) & Section 2 (Repository Layout)
- `README.md` - Master Architectural Booklet
