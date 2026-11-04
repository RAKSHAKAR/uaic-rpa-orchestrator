---
name: api-development
description: >-
  Design and implement OpenAPI-compliant, versioned REST endpoints with strict validation, pagination, and error handling.
---

# Api Development

## 1. Purpose & Overview
Enforces best practices for authoring resilient, discoverable, and performant REST APIs using FastAPI, Pydantic v2, and OpenAPI specifications.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding new API resources or endpoints in `app/api/v1/endpoints/`.
- Standardizing error responses, pagination query parameters, and sorting logic.

### When NOT to Use
- Internal helper functions that are not exposed over HTTP.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Resource specifications, HTTP method requirements, path parameters, and query schemas.

### Prerequisites
- FastAPI application routing setup (`app/api/v1/router.py`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Endpoint Path & Method Design
Design RESTful URI adhering to resource naming conventions (e.g. `GET /api/v1/claims`, `POST /api/v1/claims/{id}/start`).

### Step 2: Request & Response Schema Binding
Define input body schemas and output response models with Pydantic `Field` descriptions, examples, and constraints.

### Step 3: Query Parameter & Pagination Standardization
Implement standardized pagination parameters (`skip`, `limit`, `sort_by`, `sort_order`).

### Step 4: Service Delegation & Dependency Injection
Delegate business operations to service layer functions; inject `AsyncSession` and authenticated user context.

### Step 5: Error Handling & Status Codes
Raise typed `HTTPException` with informative error detail objects for 400, 404, 409, 422 conditions.

### Step 6: Automated Contract Testing
Write pytest tests verifying status codes, schema validation rejections, and edge cases.


---

## 5. Safety Considerations & Guardrails
- Never return unhandled 500 Internal Server Errors; wrap unexpected exceptions in structured error responses.
- Ensure sensitive credentials and tokens are excluded from response schemas.

---

## 6. Expected Deliverables & Artifacts
- FastAPI endpoint module registered in `router.py`.
- OpenAPI documentation auto-generated and verified at `/docs`.
- Comprehensive pytest contract tests.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All endpoints return typed Pydantic responses with appropriate HTTP status codes.
- [ ] Malformed inputs trigger descriptive 422 Unprocessable Entity errors.
- [ ] API appears in OpenAPI `/docs` with detailed summary and schema examples.

---

## 8. Error Recovery & Troubleshooting
- If FastAPI validation fails unexpectedly, inspect Pydantic field validators and serialization modes.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/api-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@api-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `api-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `api-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run api-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt api-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `api-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 5 (API Endpoints Summary)
- `backend/app/api/v1/endpoints/claims.py`
