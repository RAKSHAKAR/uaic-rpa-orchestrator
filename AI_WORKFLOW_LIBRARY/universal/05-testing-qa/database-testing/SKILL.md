---
name: database-testing
description: >-
  Verify relational constraints, schema migrations, transactional atomicity, and data integrity under concurrent operations.
---

# Database Testing

## 1. Purpose & Overview
Tests database models and queries to prove that foreign key cascades function safely, unique constraints prevent duplicate records, and transactions roll back cleanly upon errors.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding or modifying SQLAlchemy models in `app/models/`.
- Validating database migration scripts (`upgrade()` and `downgrade()`).
- Testing soft-delete or enterprise data retention cleanup logic.

### When NOT to Use
- Testing pure frontend UI interactions.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- SQLAlchemy models, migration scripts, and test database connection.

### Prerequisites
- Async SQLite and PostgreSQL test runners.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Constraint & Index Verification
Test primary keys, unique constraints (e.g. claim number uniqueness), and non-null constraints by asserting database error raises.

### Step 2: Foreign Key & Cascade Verification
Verify relationship integrity: deleting a parent record correctly cascades or nullifies related records according to model rules.

### Step 3: Transaction Atomicity & Rollback
Simulate exceptions mid-transaction; verify that all intermediate database writes are rolled back cleanly.

### Step 4: Migration Upgrade/Downgrade Cycle
Execute migration upgrade and immediate downgrade on a populated test database. Verify zero data corruption.

### Step 5: Cleanup Service Testing
Execute enterprise data retention cleanups (`execute_enterprise_cleanup`) and verify targeted tables are pruned accurately.

### Step 6: Test Suite Pass
Run `pytest tests/test_database_models.py tests/test_enterprise_cleanup.py -q`.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never execute destructive database tests on production databases.
- Ensure all test transactions execute within isolated test sessions.

---

## 6. Expected Deliverables & Artifacts
- Database model and transaction test suite in `backend/tests/`.
- Test execution log confirming constraint and migration integrity.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Constraints prevent duplicate and invalid data insertion.
- [ ] Transaction rollback guarantees atomic all-or-nothing persistence.
- [ ] Enterprise cleanup prunes expired records while strictly preserving active claims.

---

## 8. Error Recovery & Troubleshooting
- If database locks occur during test teardown, verify all connections in the pool are cleanly closed.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/database-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@database-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `database-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `database-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run database-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt database-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `database-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/tests/test_database_models.py`
- `backend/tests/test_enterprise_cleanup.py`
