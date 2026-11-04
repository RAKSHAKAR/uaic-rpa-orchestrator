---
name: full-stack-development
description: >-
  Implement frontend, backend, database models, and background task processing end-to-end with seamless contract alignment.
---

# Full Stack Development

## 1. Purpose & Overview
Coordinates vertical slice development connecting database models, migrations, FastAPI endpoints, Celery workers, and Next.js frontend components in lockstep.

---

## 2. When to Use & When NOT to Use

### When to Use
- Implementing vertical business features touching database, API, and UI simultaneously.
- Refactoring end-to-end data pipelines from user submission to Guidewire delivery.

### When NOT to Use
- Purely frontend cosmetic styling changes.
- Backend performance tuning with no UI impact.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- End-to-end feature requirements, entity models, and UI wireframes.

### Prerequisites
- Active local development stack (`setup_local.ps1` or Docker).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Database Layer Implementation
Create or update SQLAlchemy async models (`app/models/`), table schemas, constraints, and migrations.

### Step 2: Backend Service & Queue Tasks
Implement business logic services (`app/services/`) and Celery background tasks (`app/tasks/`).

### Step 3: FastAPI Endpoint & Schema Exposure
Create REST API handlers (`app/api/v1/endpoints/`), Pydantic validation schemas, and register routes in `router.py`.

### Step 4: Frontend Type & Client Generation
Add TypeScript types to `frontend/src/types/index.ts` and API methods to `frontend/src/lib/api.ts`.

### Step 5: Frontend Component & Page Development
Build Next.js pages and components consuming the new API endpoints.

### Step 6: End-to-End Integration Verification
Execute backend pytest suites and frontend Playwright E2E tests to verify full workflow.


---

## 5. Safety Considerations & Guardrails
- Never hold database transactions open during asynchronous browser automation.
- Ensure backend Pydantic schemas and frontend TypeScript types remain 100% synchronized.

---

## 6. Expected Deliverables & Artifacts
- Full-stack code changes across backend and frontend repositories.
- Automated integration test suite passing with 100% success rate.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Data roundtrips cleanly from frontend submission through API to database and UI display.
- [ ] Backend `pytest` and frontend `tsc --noEmit` pass with zero errors.
- [ ] Audit logging and error telemetry capture feature events.

---

## 8. Error Recovery & Troubleshooting
- If API contract mismatches cause frontend crashes, inspect browser Developer Console and update TypeScript definitions.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/full-stack-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@full-stack-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `full-stack-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `full-stack-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run full-stack-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt full-stack-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `full-stack-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 2 (Repository Layout) & Section 5 (API Endpoints Summary)
- `docs/DEVELOPMENT_WORKFLOW.md`
