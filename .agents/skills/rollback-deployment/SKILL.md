---
name: rollback-deployment
description: >-
  Restore a known-good release, database state, and configuration safely when deployment verification criteria fail.
---

# Rollback Deployment

## 1. Purpose & Overview
Executes a rapid, deterministic rollback procedure to revert failed code deployments, restore pre-deployment database snapshots, and restore stable service.

---

## 2. When to Use & When NOT to Use

### When to Use
- Post-deployment validation fails critical health checks.
- Severe unhandled errors or data corruption detected immediately following a release.

### When NOT to Use
- Routine feature deprecation.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Previous known-good release tag/commit, pre-deployment database backup, and rollback plan.

### Prerequisites
- Documented rollback procedure in Deployment Plan.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Rollback Decision & Incident Declaration
Confirm rollback criteria are met. Announce rollback initiation to stakeholders.

### Step 2: Service Traffic Drainage
Pause queue runner (`POST /api/v1/queue/pause`) and drain active tasks to prevent in-flight writes.

### Step 3: Code & Container Reversion
Checkout previous known-good git tag: `git checkout <prior_tag>`. Rebuild or deploy prior container images.

### Step 4: Database Downgrade or Restoration
Execute migration downgrade (`downgrade()`) or restore database from pre-deployment snapshot if schema changes were non-reversible.

### Step 5: Service Restart
Restart backend API, Celery workers, and frontend UI under prior release version.

### Step 6: Post-Rollback Health Pass
Verify `/api/v1/health/detailed` reports healthy status under the restored version.

### Step 7: Post-Mortem & Incident Logging
Document rollback cause, timeline, and actions taken in incident post-mortem report.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Always verify database backup integrity before overwriting live database with a snapshot.
- Never attempt unverified in-place code hotfixes during an active production deployment failure; roll back first.

---

## 6. Expected Deliverables & Artifacts
- Restored stable production environment.
- Deployment Rollback & Incident Post-Mortem Report.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] System restored to 100% operational status on known-good release.
- [ ] Database integrity verified with zero data corruption.
- [ ] Stakeholders notified of successful recovery.

---

## 8. Error Recovery & Troubleshooting
- If code rollback succeeds but database is corrupted, restore immediately from pre-deployment backup archive.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/rollback-deployment`. | `CUSTOM SKILL` |
| **Cursor** | Select `@rollback-deployment` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `rollback-deployment`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `rollback-deployment` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run rollback-deployment`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt rollback-deployment`. | `PROMPT FILE` |
| **Windsurf** | Activate `rollback-deployment` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `DEPLOYMENT.md`
- `docs/STORAGE_AND_EXPORTS_GUIDE.md`
