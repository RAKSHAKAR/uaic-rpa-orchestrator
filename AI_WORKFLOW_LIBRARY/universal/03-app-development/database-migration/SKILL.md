---
name: database-migration
description: >-
  Create safe, idempotent, forward-compatible schema migrations with validated rollback procedures and zero downtime.
---

# Database Migration

## 1. Purpose & Overview
Guides the authoring, testing, and execution of database schema migrations, ensuring existing production data is preserved, column transformations are reversible, and locks are minimized.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding, altering, or dropping database columns, tables, or constraints.
- Backfilling historical data following schema transformations.

### When NOT to Use
- Initial database creation during fresh test fixture setup.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target model changes in `app/models/` and target database connection string.

### Prerequisites
- Verified database backup or snapshot.
- Understanding of Alembic or programmatic migration scripts.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Pre-Migration Snapshot & Backup
Verify that an automated snapshot or file backup (`orchestrator.db.bak`) exists before migration execution.

### Step 2: Migration Script Generation
Author the forward migration (`upgrade()`) and corresponding backward rollback (`downgrade()`) script.

### Step 3: Backward Compatibility & Non-Destructive Column Additions
Add new columns as `nullable=True` or with server defaults to prevent deployment locking.

### Step 4: Data Backfill & Transformation Pass
If populating new columns from existing data, write an idempotent batch script updating records in chunks.

### Step 5: Dry-Run & Rollback Verification
Test `upgrade()` and immediate `downgrade()` on an isolated test database to verify reversibility.

### Step 6: Live Migration Execution & Schema Integrity Check
Execute migration and verify column presence and index creation via database introspection.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never execute `DROP COLUMN` or `DROP TABLE` without explicit user approval and a verified backup.
- Avoid table-locking operations on high-volume tables during business hours.

---

## 6. Expected Deliverables & Artifacts
- Idempotent migration script with verified `upgrade` and `downgrade` methods.
- Migration execution and verification log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Migration executes cleanly without errors on both fresh and populated databases.
- [ ] Downgrade rollback restores exact prior schema without data loss.
- [ ] Existing application queries continue functioning seamlessly.

---

## 8. Error Recovery & Troubleshooting
- If migration fails mid-execution, execute the rollback script immediately and restore from the pre-migration snapshot.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/database-migration`. | `CUSTOM SKILL` |
| **Cursor** | Select `@database-migration` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `database-migration`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `database-migration` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run database-migration`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt database-migration`. | `PROMPT FILE` |
| **Windsurf** | Activate `database-migration` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/core/database.py`
- `scripts/sync_sqlite_to_postgres.py`
