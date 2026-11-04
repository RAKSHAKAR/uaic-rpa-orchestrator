---
name: fix-api-errors
description: >-
  Diagnose request, response, schema validation, and HTTP 4xx/5xx failures across REST endpoints.
---

# Fix Api Errors

## 1. Purpose & Overview
Isolates and resolves REST API contract failures, Pydantic serialization bugs, missing query parameters, and unexpected HTTP status codes.

---

## 2. When to Use & When NOT to Use

### When to Use
- API endpoints returning 400 Bad Request, 422 Unprocessable Entity, or 500 Server Error.
- Frontend Axios requests failing or receiving malformed payloads.

### When NOT to Use
- External third-party API integration timeouts (use `fix-integration-issues`).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- HTTP request URL, method, headers, request body, response status code, and response JSON.

### Prerequisites
- Access to FastAPI route definitions in `app/api/v1/endpoints/`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Request Payload Inspection
Compare incoming request body against Pydantic schema in `app/schemas/`. Check for missing required fields, type mismatches, or invalid formats.

### Step 2: Endpoint Handler Debugging
Inspect route logic in `app/api/v1/endpoints/`. Check database queries, foreign key validations, and error raises.

### Step 3: Pydantic Serialization Check
Ensure database model objects are correctly converted to Pydantic response models with `from_attributes=True`.

### Step 4: Status Code Alignment
Return explicit HTTP status codes: 200 (Success), 201 (Created), 400 (Bad Request), 404 (Not Found), 409 (Conflict), 422 (Validation Error).

### Step 5: Automated Regression Test Pass
Author a test in `tests/test_api.py` asserting the fix.

### Step 6: Endpoint Verification
Verify endpoint returns expected JSON using `AsyncClient`.


---

## 5. Safety Considerations & Guardrails
- Never expose internal database error details or SQL statements in API error messages.
- Ensure API contract fixes do not break existing frontend consumers.

---

## 6. Expected Deliverables & Artifacts
- Patched FastAPI endpoint handler or Pydantic schema.
- Automated test case in `backend/tests/test_api.py`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Endpoint returns expected 2xx response for valid inputs.
- [ ] Invalid inputs return structured 4xx responses with clear error messages.
- [ ] Zero 500 Internal Server Errors emitted.

---

## 8. Error Recovery & Troubleshooting
- If Pydantic fails to serialize datetime fields, ensure UTC ISO-8601 formatting is applied.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fix-api-errors`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fix-api-errors` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fix-api-errors`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fix-api-errors` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fix-api-errors`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fix-api-errors`. | `PROMPT FILE` |
| **Windsurf** | Activate `fix-api-errors` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/api/v1/endpoints/claims.py`
- `backend/tests/test_api.py`
