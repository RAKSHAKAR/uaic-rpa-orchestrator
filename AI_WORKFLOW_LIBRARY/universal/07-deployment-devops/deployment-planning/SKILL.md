---
name: deployment-planning
description: >-
  Define pre-release checklists, downtime requirements, stakeholder sign-offs, and step-by-step rollback procedures.
---

# Deployment Planning

## 1. Purpose & Overview
Authors comprehensive, risk-managed deployment plans detailing change windows, prerequisite backups, deployment sequencing, verification smoke tests, and rollback triggers.

---

## 2. When to Use & When NOT to Use

### When to Use
- Preparing major production releases, database schema migrations, or infrastructure cutovers.
- Coordinating scheduled release windows with business operators.

### When NOT to Use
- Routine local development builds.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Release scope, database migrations, affected services, and target deployment date/time.

### Prerequisites
- All release candidate code merged and verified by CI.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Release Scope & Window Definition
Define release version, scheduled change window, expected downtime (if any), and release coordinator.

### Step 2: Pre-Deployment Checklist
Specify mandatory pre-flight checks: verified database backup, active queue drained, secret keys verified, and rollback branch tagged.

### Step 3: Sequential Deployment Steps
Enumerate ordered deployment commands: maintenance banner on -> stop worker -> migrate database -> start backend -> deploy frontend -> restart worker -> maintenance banner off.

### Step 4: Smoke Test & Verification Protocol
Define explicit post-deployment tests: `/health` detailed check, single portal ping, and live test claim execution.

### Step 5: Rollback Triggers & Protocol
Specify exact failure conditions that trigger immediate rollback (e.g. database migration failure, > 5% error rate on health checks) and step-by-step rollback commands.

### Step 6: Plan Publication & Sign-Off
Publish Deployment Plan in `docs/` and obtain stakeholder sign-off.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never execute a production deployment without a verified, pre-tested rollback procedure.
- Ensure release windows minimize disruption to operational claim discovery.

---

## 6. Expected Deliverables & Artifacts
- Formal Deployment Plan Document (`docs/YYYY-MM-DD_deployment_plan_v<N>.md`).
- Signed pre-deployment checklist.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Deployment plan details exact commands, owners, and time estimates.
- [ ] Rollback procedure is verified and documented.
- [ ] Smoke test protocol covers all critical business paths.

---

## 8. Error Recovery & Troubleshooting
- If sign-off conditions are not met, postpone the release window until blockers are resolved.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/deployment-planning`. | `CUSTOM SKILL` |
| **Cursor** | Select `@deployment-planning` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `deployment-planning`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `deployment-planning` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run deployment-planning`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt deployment-planning`. | `PROMPT FILE` |
| **Windsurf** | Activate `deployment-planning` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `DEPLOYMENT.md`
- `DEPLOYMENT_AND_HOSTING_GUIDE.md`
