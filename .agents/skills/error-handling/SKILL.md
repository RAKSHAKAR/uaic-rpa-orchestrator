---
name: error-handling
description: >-
  Implement consistent error hierarchies, typed exceptions, graceful degradation, and user-facing error banners.
---

# Error Handling

## 1. Purpose & Overview
Standardizes exception handling across the platform, preventing unhandled crashes, establishing clean error classification, and presenting actionable feedback to operators.

---

## 2. When to Use & When NOT to Use

### When to Use
- Authoring new service modules, scrapers, or API endpoints.
- Refactoring generic `except Exception:` blocks into typed exception handling.
- Standardizing frontend error banners and toast notifications.

### When NOT to Use
- Suppressing legitimate programming errors or syntax bugs.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target error scenarios, exception hierarchy definitions, and error schemas.

### Prerequisites
- Understanding of FastAPI exception handlers and React Error Boundaries.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Domain Exception Hierarchy Definition
Define typed exceptions in `app/core/exceptions.py` (e.g., `CaptchaResolutionError`, `PortalNavigationError`, `GuidewireDeliveryError`).

### Step 2: Specific Exception Handling
Replace catch-all `except Exception:` blocks with specific exception traps. Preserve stack traces with `raise ... from exc`.

### Step 3: FastAPI Exception Handlers
Register global exception handlers mapping domain exceptions to structured JSON responses (`status`, `error_code`, `message`, `details`).

### Step 4: Frontend Error Boundary & Toast Binding
Wrap React component trees in Error Boundaries. Display user-friendly error banners mapping API error codes.

### Step 5: Audit Logging & Screenshot Capture
Capture automated error screenshots (`ErrorScreenshot`) and audit log entries for all runtime scraper exceptions.

### Step 6: Error Scenario Testing
Write unit tests deliberately injecting failures and verifying structured error responses.


---

## 5. Safety Considerations & Guardrails
- NEVER silently swallow exceptions with bare `pass` blocks.
- Never expose internal database connection strings or stack traces to end-users in production.

---

## 6. Expected Deliverables & Artifacts
- Domain exception hierarchy and structured exception handlers.
- Automated test suite verifying error capture and response mapping.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero unhandled 500 errors returned for known failure modes.
- [ ] Scraper failures capture diagnostic error screenshots to `backend/screenshots/`.
- [ ] Frontend displays clear, actionable error banners without crashing the UI.

---

## 8. Error Recovery & Troubleshooting
- If an unknown exception occurs, log the complete traceback to audit logs and present a safe fallback UI.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/error-handling`. | `CUSTOM SKILL` |
| **Cursor** | Select `@error-handling` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `error-handling`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `error-handling` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run error-handling`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt error-handling`. | `PROMPT FILE` |
| **Windsurf** | Activate `error-handling` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/base.py` - `CaptchaResolutionError`
- `backend/app/models/error_screenshot.py`
