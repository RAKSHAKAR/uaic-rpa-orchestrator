---
name: fix-database-errors
description: >-
  Diagnose database locks, connection pool exhaustion, constraint violations, and schema migration errors.
---

# Fix Database Errors

## 1. Purpose & Overview
Resolves relational database locks (`database is locked`), duplicate key constraint violations, foreign key cascading errors, and transaction rollbacks.

---

## 2. When to Use & When NOT to Use

### When to Use
- SQLite throws `OperationalError: database is locked` during concurrent scraper runs.
- IntegrityError raised for duplicate unique keys.
- Database migrations fail or leave schema in an inconsistent state.

### When NOT to Use
- Frontend UI bugs.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Database error traceback, failed SQL query, and database connection settings.

### Prerequisites
- SQLAlchemy connection configuration and database inspection tools.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Lock & Concurrency Analysis
If encountering SQLite locks, inspect connection pooling in `backend/app/core/database.py`. Configure WAL (Write-Ahead Logging) mode and busy timeouts.

### Step 2: Constraint Violation Inspection
If encountering `IntegrityError`, identify which unique or foreign key constraint failed. Check input data uniqueness before inserting.

### Step 3: Transaction Scope Audit
Verify that `AsyncSession` transactions are kept as short as possible. Never hold a session open across network or scraper calls.

### Step 4: Migration Repair
If schema migration is stuck, inspect migration versions, resolve conflicts, and run migration repair script.

### Step 5: Database Integrity Verification
Run `PRAGMA integrity_check;` on SQLite or equivalent PostgreSQL validation to confirm zero corruption.

### Step 6: Regression Test Pass
Run `pytest tests/test_database_models.py -q`.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Always backup the database file before running low-level repair or migration commands.
- Never disable foreign key constraints to bypass validation errors.

---

## 6. Expected Deliverables & Artifacts
- Patched database engine configuration or model constraint logic.
- Verified database integrity test log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Database operations execute without lock timeouts or connection exhaustion.
- [ ] Constraint violations are prevented via pre-insert validation.
- [ ] Database integrity check passes with zero corruption.

---

## 8. Error Recovery & Troubleshooting
- If SQLite database file is locked by a dead process, cleanly terminate the lingering process holding the file handle.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fix-database-errors`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fix-database-errors` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fix-database-errors`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fix-database-errors` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fix-database-errors`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fix-database-errors`. | `PROMPT FILE` |
| **Windsurf** | Activate `fix-database-errors` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/core/database.py`
- `backend/tests/test_database_models.py`
