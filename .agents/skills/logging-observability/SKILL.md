---
name: logging-observability
description: >-
  Implement structured JSON logging, correlation IDs, execution telemetry, and health check diagnostics.
---

# Logging Observability

## 1. Purpose & Overview
Ensures the application emits rich, structured operational logs, metrics, and trace IDs enabling rapid root-cause diagnosis across distributed API and Celery workers.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding telemetry to asynchronous queue tasks, scrapers, or third-party integrations.
- Standardizing log output formats across backend and worker containers.

### When NOT to Use
- Adding temporary local `print()` statements for one-off debugging.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Logging configuration (`logging.config`), log level guidelines, and metric requirements.

### Prerequisites
- Python `logging` or `structlog` setup.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Structured Logger Configuration
Configure Python logging with structured JSON formatting, UTC ISO timestamps, and log level thresholds.

### Step 2: Correlation & Trace ID Injection
Generate unique correlation IDs (`X-Correlation-ID`) in FastAPI middleware; propagate IDs across Celery task headers.

### Step 3: Contextual Log Binding
Bind contextual metadata (`claim_id`, `portal`, `party_name`, `elapsed_ms`) to logger calls.

### Step 4: Audit Trail Integration
Persist significant operational milestones to `AuditLog` database table for permanent tracking.

### Step 5: Secret Masking Filter
Apply logging filter automatically redacting passwords, API keys, and customer SSN/PII.

### Step 6: Verification Pass
Inspect log output during a simulated claim workflow to verify correlation ID propagation and secret redaction.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never emit plain-text passwords, tokens, or credentials in log output.
- Avoid excessive debug logging in production that exhausts disk space.

---

## 6. Expected Deliverables & Artifacts
- Structured logging configuration and correlation middleware.
- Verified audit log records and secret masking filters.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All logs emit valid JSON with correlation ID and timestamp.
- [ ] All secrets and tokens are masked with `***`.
- [ ] Scraper execution timing is captured with millisecond accuracy.

---

## 8. Error Recovery & Troubleshooting
- If logging handlers throw disk-full or IO errors, fail safely to console stderr.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/logging-observability`. | `CUSTOM SKILL` |
| **Cursor** | Select `@logging-observability` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `logging-observability`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `logging-observability` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run logging-observability`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt logging-observability`. | `PROMPT FILE` |
| **Windsurf** | Activate `logging-observability` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/api/v1/endpoints/audit.py`
- `backend/app/models/audit_log.py`
