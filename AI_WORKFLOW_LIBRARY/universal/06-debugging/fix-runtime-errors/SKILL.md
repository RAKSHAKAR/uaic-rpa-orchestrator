---
name: fix-runtime-errors
description: >-
  Resolve Python runtime exceptions, unhandled crashes, async deadlocks, and worker task failures.
---

# Fix Runtime Errors

## 1. Purpose & Overview
Diagnoses and fixes runtime exceptions (`AttributeError`, `KeyError`, `ValueError`, `TypeError`) and async task failures in backend services and Celery workers.

---

## 2. When to Use & When NOT to Use

### When to Use
- FastAPI returns HTTP 500 Internal Server Error.
- Celery tasks crash with unhandled tracebacks.
- Scrapers encounter unexpected DOM structure changes.

### When NOT to Use
- Frontend-only CSS or visual styling issues.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Exception traceback, error log, input arguments, and reproduction conditions.

### Prerequisites
- Backend Python virtual environment.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Traceback Analysis
Analyze the complete Python traceback. Identify the exact file, function, line, and exception class.

### Step 2: Input State & Null Safety Check
Inspect variables at point of failure. Check for `None` values, missing dictionary keys, or mismatched datatypes.

### Step 3: Defensive Guard & Fallback Implementation
Implement defensive checks (e.g. `dict.get()`, null checks, try/except blocks) with sensible defaults.

### Step 4: Reproduction Test Authoring
Write an automated unit test reproducing the exact input conditions that triggered the crash.

### Step 5: Regression Verification
Execute `pytest` across all test suites to confirm the fix works and breaks zero adjacent logic.

### Step 6: Lint Check
Run `ruff check app tests` to verify clean code formatting.


---

## 5. Safety Considerations & Guardrails
- Never use bare `except:` blocks that swallow keyboard interrupts or system exits.
- Ensure fixes preserve core business rules (e.g. 1899-12-30 date conversion, 9-digit ClaimNumber prefix).

---

## 6. Expected Deliverables & Artifacts
- Patched Python source files with robust error handling.
- Automated regression test verifying the fix.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Runtime exception no longer occurs under reproduction inputs.
- [ ] New regression test passes cleanly.
- [ ] All 556 backend tests continue passing.

---

## 8. Error Recovery & Troubleshooting
- If an async deadlock occurs in SQLAlchemy, ensure database sessions are cleanly closed with async context managers.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fix-runtime-errors`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fix-runtime-errors` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fix-runtime-errors`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fix-runtime-errors` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fix-runtime-errors`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fix-runtime-errors`. | `PROMPT FILE` |
| **Windsurf** | Activate `fix-runtime-errors` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/main.py`
- `backend/app/tasks/scraper_tasks.py`
