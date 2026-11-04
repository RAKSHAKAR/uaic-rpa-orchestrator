---
name: integration-testing
description: >-
  Verify interactions across database transactions, FastAPI endpoints, and Celery asynchronous task dispatch.
---

# Integration Testing

## 1. Purpose & Overview
Tests the integration boundaries between application services, verifying that database transactions commit cleanly, foreign keys cascade properly, and async tasks dispatch with correct payload arguments.

---

## 2. When to Use & When NOT to Use

### When to Use
- Testing API endpoints that persist data to SQLite or PostgreSQL.
- Verifying Celery task dispatch and worker state reconciliation.
- Testing Excel/CSV ingestion pipelines end-to-end.

### When NOT to Use
- Pure isolated unit logic with zero external interfaces.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Service interfaces, test database fixtures, and Celery task definitions.

### Prerequisites
- Configured async SQLAlchemy test session and Redis/memory broker.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Test Fixture Setup
Initialize isolated test database using `AsyncSessionLocal` fixture with automated rollback after each test.

### Step 2: API Endpoint Invocation
Execute requests against FastAPI app using `httpx.AsyncClient` and `ASGITransport`.

### Step 3: Database State Assertion
Query the database directly using SQLAlchemy `select()` to verify record creation, state mutation, and timestamps.

### Step 4: Task Dispatch Verification
Verify Celery task dispatch using task inspection or eager execution mode (`task_always_eager=True`).

### Step 5: Transaction Rollback & Cleanup
Confirm test database state is cleanly reset, ensuring test independence.

### Step 6: Test Suite Pass
Run `pytest tests/test_api.py -q`.


---

## 5. Safety Considerations & Guardrails
- NEVER run integration tests against production databases.
- Ensure tests do not leave lingering records that corrupt subsequent test runs.

---

## 6. Expected Deliverables & Artifacts
- Integration test suite in `backend/tests/`.
- Test execution log demonstrating verified database persistence.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Endpoints return expected HTTP status codes and persist correct data to database.
- [ ] Database constraints, unique indexes, and foreign keys are verified.
- [ ] Test database resets cleanly between runs.

---

## 8. Error Recovery & Troubleshooting
- If async transactions stall or deadlock, ensure all `AsyncSession` instances are cleanly closed in test teardown.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/integration-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@integration-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `integration-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `integration-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run integration-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt integration-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `integration-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/tests/test_api.py`
- `backend/tests/test_async_export.py`
