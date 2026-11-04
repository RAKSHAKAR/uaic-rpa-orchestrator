---
name: backend-development
description: >-
  Implement robust FastAPI endpoints, Pydantic schemas, business logic services, and Celery asynchronous workers.
---

# Backend Development

## 1. Purpose & Overview
Guides backend development adhering to clean architecture, asynchronous database querying (`asyncpg` / `aiosqlite`), structured logging, and resilient background task processing.

---

## 2. When to Use & When NOT to Use

### When to Use
- Developing new REST API endpoints, Celery workers, or core business services.
- Refactoring database queries and transactional boundaries.

### When NOT to Use
- Authoring frontend HTML/CSS components.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- API route specification, database schema models, and task execution parameters.

### Prerequisites
- Python 3.14.7 virtual environment with installed backend dependencies.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Pydantic Schema Definition
Define request, response, and query parameter models in `app/schemas/` with strict type annotations.

### Step 2: Service Layer Implementation
Author domain business logic in `app/services/` decoupled from HTTP routing logic.

### Step 3: FastAPI Endpoint Handlers
Implement async route handlers in `app/api/v1/endpoints/`. Inject `AsyncSession` dependencies and apply HTTP exception handling.

### Step 4: Router Registration
Register new router in `app/api/v1/router.py` with appropriate tags and prefixes.

### Step 5: Celery Task Authoring
Implement background workers in `app/tasks/` with explicit queue routing, retry policies, and error logging.

### Step 6: Unit & Integration Testing
Write comprehensive pytest suites in `tests/` using `AsyncClient` and `ASGITransport`.


---

## 5. Safety Considerations & Guardrails
- Never hold database transactions open across long-running external API calls or scraping cycles.
- Mask all secrets, passwords, and API tokens in logs and responses.

---

## 6. Expected Deliverables & Artifacts
- FastAPI endpoint handlers, Pydantic schemas, and Celery tasks.
- Comprehensive pytest integration tests with high assertion coverage.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All endpoints return appropriate HTTP status codes (200, 201, 400, 404, 422, 500).
- [ ] Ruff linting passes with 0 errors (`ruff check app tests`).
- [ ] Backend pytest suite passes without failures.

---

## 8. Error Recovery & Troubleshooting
- If async SQLAlchemy sessions encounter `PendingRollbackError`, ensure all exceptions trigger clean rollbacks in `finally` blocks.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/backend-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@backend-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `backend-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `backend-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run backend-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt backend-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `backend-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/main.py`
- `backend/app/api/v1/router.py`
