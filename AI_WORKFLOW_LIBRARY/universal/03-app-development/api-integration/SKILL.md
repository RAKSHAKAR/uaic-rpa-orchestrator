---
name: api-integration
description: >-
  Integrate internal and third-party APIs (e.g. Guidewire, SMTP) with resilient retry backoff, circuit breaking, and telemetry.
---

# Api Integration

## 1. Purpose & Overview
Provides patterns and safeguards for consuming external HTTP/REST APIs, managing authentication lifecycles (Bearer tokens, API keys, OAuth2), and handling downstream timeouts gracefully.

---

## 2. When to Use & When NOT to Use

### When to Use
- Connecting to external enterprise systems (Guidewire Insurance Cloud, AntiCaptcha, Twilio).
- Implementing external webhook consumers or outbound dispatchers.

### When NOT to Use
- Calling internal database queries or in-process services.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- External API documentation, authentication credentials, endpoint URLs, and payload specifications.

### Prerequisites
- Configured HTTP client library (`httpx`) with async connection pooling.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Client Architecture & Authentication
Create dedicated client class (e.g. `GuidewireClient`) encapsulating authentication headers, token refresh, and base URLs.

### Step 2: Payload Serializer & Contract Validation
Implement strict payload transformers formatting outgoing data to the exact external contract (e.g. 9-digit ClaimNumber '0' prefix).

### Step 3: Timeout & Connection Pool Configuration
Set explicit connect, read, and write timeouts (e.g. 30s timeout) to prevent hanging worker threads.

### Step 4: Retry Policy & Exponential Backoff
Implement exponential backoff with jitter for transient HTTP 429, 502, 503, 504 errors using Celery or tenacity.

### Step 5: Logging, Telemetry & Secret Masking
Log request timing, URL, and status codes while masking authorization tokens and customer PII.

### Step 6: Mock Test Suite Verification
Author comprehensive mock unit tests simulating external success, timeout, 401 unauthorized, and 500 error responses.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never log raw API authorization headers, Bearer tokens, or API keys.
- Always enforce strict timeout limits to prevent thread exhaustion in Celery workers.

---

## 6. Expected Deliverables & Artifacts
- Dedicated API Client class in `app/services/`.
- Mock-backed integration test suite covering success and failure modes.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] External calls adhere strictly to target third-party payload schemas.
- [ ] Transient network failures trigger retry with exponential backoff.
- [ ] Zero plain-text credentials leak into logs or telemetry.

---

## 8. Error Recovery & Troubleshooting
- If external API changes response format, capture error body in audit logs and update Pydantic client schema.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/api-integration`. | `CUSTOM SKILL` |
| **Cursor** | Select `@api-integration` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `api-integration`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `api-integration` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run api-integration`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt api-integration`. | `PROMPT FILE` |
| **Windsurf** | Activate `api-integration` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 11 (Guidewire Payload Contract)
- `backend/app/services/guidewire_client.py`
