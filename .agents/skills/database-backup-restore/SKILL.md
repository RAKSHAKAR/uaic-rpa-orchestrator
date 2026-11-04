---
name: database-backup-restore
description: >-
  Validate database backup integrity, automated snapshot creation, and deterministic restoration procedures.
---

# Database Backup Restore

## 1. Purpose & Overview
Establishes reliable, automated database backup procedures and regularly verifies that backups can be restored cleanly with zero data loss.

---

## 2. When to Use & When NOT to Use

### When to Use
- Prior to executing major schema migrations or bulk data deletions.
- Establishing automated scheduled daily/weekly backup routines.
- Testing disaster recovery preparedness.

### When NOT to Use
- Routine read-only queries.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Active database path (`orchestrator.db` or PostgreSQL URL) and backup destination directory.

### Prerequisites
- Filesystem write access to backup storage.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Online Backup Execution
For SQLite: execute online vacuum backup `sqlite3 orchestrator.db ".backup 'orchestrator_backup_YYYYMMDD.db'"` to ensure atomic snapshot without table locking. For PostgreSQL: run `pg_dump`.

### Step 2: Backup Integrity Verification
Verify backup file exists, is non-zero in size, and passes `PRAGMA integrity_check;` on SQLite.

### Step 3: Restoration Simulation on Isolated Target
Restore backup file to an isolated test directory (`test_restore.db`).

### Step 4: Data Fidelity & Count Verification
Query restored database: compare row counts of `claims`, `court_cases`, `match_results`, and `system_settings` against original database.

### Step 5: Backup Archival & Retention
Compress verified backup (`gzip`) and apply retention policy (prune backups older than 30 days).

### Step 6: Disaster Recovery Runbook Update
Document backup location and restoration commands in `docs/STORAGE_AND_EXPORTS_GUIDE.md`.


---

## 5. Safety Considerations & Guardrails
- Never copy an active SQLite database file directly while writers are active; always use the SQLite online backup API (`.backup`).
- Store backup files on storage physically separate from the active database disk.

---

## 6. Expected Deliverables & Artifacts
- Verified, compressed database backup archive.
- Restoration verification report confirming row count parity.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Backup passes database integrity checks cleanly.
- [ ] Restoration simulation restores 100% of records with zero corruption.
- [ ] Restoration procedures are fully documented and executable.

---

## 8. Error Recovery & Troubleshooting
- If backup verification fails integrity check, immediately take a fresh backup and investigate disk IO errors.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/database-backup-restore`. | `CUSTOM SKILL` |
| **Cursor** | Select `@database-backup-restore` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `database-backup-restore`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `database-backup-restore` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run database-backup-restore`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt database-backup-restore`. | `PROMPT FILE` |
| **Windsurf** | Activate `database-backup-restore` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/STORAGE_AND_EXPORTS_GUIDE.md`
- `scripts/sync_sqlite_to_postgres.py`
