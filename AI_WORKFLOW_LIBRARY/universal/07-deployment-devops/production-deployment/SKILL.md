---
name: production-deployment
description: >-
  Execute controlled production deployments with mandatory backups, health verification, and rollback safeguards.
---

# Production Deployment

## 1. Purpose & Overview
Guides the live execution of an approved deployment plan, applying code updates, running database migrations, recycling containers, and validating production health.

---

## 2. When to Use & When NOT to Use

### When to Use
- Executing authorized production software releases during scheduled change windows.

### When NOT to Use
- Deploying unapproved, untested code directly to production servers.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved Deployment Plan, release tag, production SSH/terminal access, and backup tools.

### Prerequisites
- Completed `deployment-planning` and explicit stakeholder sign-off.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Pre-Deployment State & Backup Capture
Verify queue is drained. Take full database snapshot (`sqlite3 .backup` or `pg_dump`) and archive with release tag.

### Step 2: Code Pull & Dependency Build
Fetch approved release git tag. Install locked dependencies and compile frontend production build (`npm run build`).

### Step 3: Database Migration Execution
Execute database migration scripts. Verify schema integrity check passes.

### Step 4: Service Restart & Worker Recycling
Restart backend service, Celery workers, and Next.js frontend. Verify process uptime.

### Step 5: Post-Deployment Smoke Verification
Execute automated smoke test: check `/api/v1/health/detailed`, verify portal reachability, and monitor error logs.

### Step 6: Release Sign-Off & Status Finalization
Confirm successful deployment to stakeholders and archive deployment logs.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Stop deployment and initiate rollback immediately if database migrations fail or error rates spike.
- Never bypass pre-deployment database backups.

---

## 6. Expected Deliverables & Artifacts
- Deployed production release.
- Post-deployment verification log and backup archive.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Production services running updated release tag.
- [ ] `/api/v1/health/detailed` reports all 8 components healthy.
- [ ] Zero elevated error rates in operational logs.

---

## 8. Error Recovery & Troubleshooting
- If any smoke test fails, immediately invoke `rollback-deployment`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/production-deployment`. | `CUSTOM SKILL` |
| **Cursor** | Select `@production-deployment` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `production-deployment`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `production-deployment` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run production-deployment`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt production-deployment`. | `PROMPT FILE` |
| **Windsurf** | Activate `production-deployment` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `DEPLOYMENT.md`
- `Deploy-To-GitHub.ps1`
