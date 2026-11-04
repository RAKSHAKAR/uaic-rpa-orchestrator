---
name: api-documentation
description: >-
  Document REST endpoints, OpenAPI schemas, query parameters, authentication, and curl/Python invocation examples.
---

# Api Documentation

## 1. Purpose & Overview
Maintains exhaustive, developer-friendly REST API documentation, including OpenAPI schema descriptions, request/response examples, status codes, and curl snippets.

---

## 2. When to Use & When NOT to Use

### When to Use
- Exposing new REST endpoints or modifying request/response schemas in `app/api/v1/endpoints/`.
- Updating API reference guides (`docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`).

### When NOT to Use
- Internal helper functions not exposed over HTTP.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- FastAPI endpoint definitions, Pydantic schemas, and HTTP method parameters.

### Prerequisites
- FastAPI OpenAPI generator active.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Pydantic Schema Documentation
Add `Field(description=..., examples=[...])` annotations to all request and response schemas in `app/schemas/`.

### Step 2: FastAPI Route Docstrings
Add comprehensive docstrings to route functions with markdown summaries and status code descriptions.

### Step 3: API Guide Documentation
Document endpoint in `docs/APIS_AND_MATCHING_ENGINE_GUIDE.md` with curl example, Python `httpx` example, and JSON response payload.

### Step 4: OpenAPI Spec Generation & Validation
Verify `/docs` (Swagger UI) and `/openapi.json` render accurately without schema warnings.

### Step 5: API Table Synchronization
Update API Summary table in `AGENTS.md` and `README.md`.


---

## 5. Safety Considerations & Guardrails
- Never expose internal database passwords or tokens in API schema examples.
- Ensure documented status codes match actual endpoint behavior.

---

## 6. Expected Deliverables & Artifacts
- Updated OpenAPI schemas and Swagger documentation.
- Exhaustive REST API guide in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All endpoints have complete descriptions, request bodies, and typed responses in OpenAPI.
- [ ] Curl and Python invocation examples are tested and verified.
- [ ] `AGENTS.md` API summary table is fully synchronized.

---

## 8. Error Recovery & Troubleshooting
- If Swagger UI fails to render schema, inspect Pydantic models for cyclic references or invalid types.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/api-documentation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@api-documentation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `api-documentation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `api-documentation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run api-documentation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt api-documentation`. | `PROMPT FILE` |
| **Windsurf** | Activate `api-documentation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`
- `AGENTS.md` - Section 5 (API Endpoints Summary)
