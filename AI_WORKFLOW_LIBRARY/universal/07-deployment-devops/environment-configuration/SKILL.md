---
name: environment-configuration
description: >-
  Manage environment variables, Pydantic settings, secrets masking, and configuration drift securely.
---

# Environment Configuration

## 1. Purpose & Overview
Ensures runtime configuration is managed through Pydantic Settings models (`app/core/config.py`) and database-persisted settings (`SystemSettings`), preventing credential leakage and drift.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding new configuration settings (timeouts, thresholds, credentials).
- Configuring environment variables across development, test, and production.

### When NOT to Use
- Hardcoding credentials directly in source code.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Configuration requirements, default values, and environment files (`.env`, `.env.example`).

### Prerequisites
- Pydantic Settings model architecture.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Pydantic Settings Schema Extension
Define new setting in `app/core/config.py` with type annotation, default value, and description.

### Step 2: Database Persistence Model Binding
If setting is user-configurable at runtime, add field to `SystemSettings` schema in `app/schemas/settings.py`.

### Step 3: Environment Template Update
Add documented entry with placeholder value to `.env.example`.

### Step 4: Secret Masking Implementation
Ensure sensitive settings (passwords, API keys) are masked with `***` in API responses and logs.

### Step 5: Worker Synchronization Verification
Confirm that Celery workers reload updated settings dynamically via `get_system_settings_async()`.

### Step 6: Configuration Test Pass
Write pytest test in `tests/test_automation_runtime_settings.py` verifying settings persistence and masking.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never hardcode passwords, API keys, or database URLs in source code.
- Never commit `.env` containing live secrets to git.

---

## 6. Expected Deliverables & Artifacts
- Updated `app/core/config.py` and `app/schemas/settings.py`.
- Synchronized `.env.example` template.
- Automated settings persistence test.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All settings have default values and validation constraints.
- [ ] Settings persist to database and reload dynamically at runtime.
- [ ] All secrets are masked in API outputs.

---

## 8. Error Recovery & Troubleshooting
- If configuration values fail Pydantic validation on startup, check datatype casting and environment variable prefix.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/environment-configuration`. | `CUSTOM SKILL` |
| **Cursor** | Select `@environment-configuration` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `environment-configuration`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `environment-configuration` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run environment-configuration`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt environment-configuration`. | `PROMPT FILE` |
| **Windsurf** | Activate `environment-configuration` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/core/config.py`
- `backend/app/schemas/settings.py`
