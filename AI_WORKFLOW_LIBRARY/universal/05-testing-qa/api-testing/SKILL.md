---
name: api-testing
description: >-
  Verify REST contracts, payload validation, status codes, query pagination, and error responses via automated tests.
---

# Api Testing

## 1. Purpose & Overview
Ensures all FastAPI endpoints conform strictly to OpenAPI specifications, validate input bounds, return typed JSON models, and handle error scenarios predictably.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding or modifying REST API endpoints in `app/api/v1/endpoints/`.
- Verifying pagination, sorting, and bulk operation endpoints.

### When NOT to Use
- Frontend-only styling changes.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- FastAPI endpoint definitions and Pydantic schemas.

### Prerequisites
- `httpx` async test client and test database fixtures.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Schema & Contract Assertion
Send valid request bodies and verify response status (200 OK / 201 Created) and JSON structure against Pydantic response models.

### Step 2: Validation Rejection Testing
Send malformed JSON, out-of-bounds parameters, and invalid types. Confirm 422 Unprocessable Entity with descriptive error arrays.

### Step 3: Pagination & Filtering Testing
Test query parameters (`skip=0&limit=10`, `status=NEW`). Verify returned records match filters and total counts are accurate.

### Step 4: Not Found & Edge Case Scenarios
Request non-existent resource IDs (e.g. UUIDs). Verify 404 Not Found is returned.

### Step 5: Security & Authorization Checks
Test unauthorized calls to protected endpoints. Confirm 401 or 403 responses.

### Step 6: Test Suite Pass
Run `pytest tests/test_api.py -q`.


---

## 5. Safety Considerations & Guardrails
- Never test endpoints by making mutating requests to live production environments.
- Ensure sensitive customer data is never used in automated test payloads.

---

## 6. Expected Deliverables & Artifacts
- Automated API contract test suite in `backend/tests/`.
- Test execution log demonstrating 100% pass rate.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All endpoints return valid JSON matching declared Pydantic schemas.
- [ ] 422 errors provide specific field error locations and messages.
- [ ] Pagination parameters are strictly validated and enforced.

---

## 8. Error Recovery & Troubleshooting
- If Pydantic serialization fails, check for unhandled SQLAlchemy model relationships or timezone-naive datetimes.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/api-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@api-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `api-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `api-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run api-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt api-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `api-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 5 (API Endpoints Summary)
- `backend/tests/test_api.py`
