---
name: staging-deployment
description: >-
  Deploy and validate release candidates in staging environments mirroring production configurations.
---

# Staging Deployment

## 1. Purpose & Overview
Deploys release candidates to an isolated staging environment to conduct realistic pre-production qualification tests, portal reachability tests, and stakeholder demos.

---

## 2. When to Use & When NOT to Use

### When to Use
- Deploying release candidates for quality assurance and operator verification.
- Testing database migration rollback procedures on production-like data.

### When NOT to Use
- Local dev testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Release candidate branch or tag, staging server credentials, and staging `.env`.

### Prerequisites
- Configured staging server or staging container cluster.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Staging Environment Preparation
Ensure staging database is seeded with representative sanitized test claims.

### Step 2: Release Candidate Deployment
Deploy release candidate code to staging containers using Docker Compose or CI/CD runner.

### Step 3: Database Migration Pass
Run database migrations on staging. Verify schema changes succeed without data corruption.

### Step 4: Automated Qualification Suite
Run full Playwright E2E test suite and portal ping probes against staging endpoints.

### Step 5: Operator Acceptance Testing (UAT)
Provide staging URL to stakeholders for visual inspection and workflow review.

### Step 6: Staging Qualification Report
Publish Staging Qualification Report confirming readiness for production.


---

## 5. Safety Considerations & Guardrails
- Ensure staging environment uses isolated mock credentials for external services (Guidewire, SMTP) where appropriate.
- Never use unredacted customer PII in staging environments.

---

## 6. Expected Deliverables & Artifacts
- Deployed staging environment running release candidate.
- Staging Qualification Report with verified test passes.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All staging services operational and healthy.
- [ ] Full E2E test suite passes on staging environment.
- [ ] Operator acceptance sign-off obtained.

---

## 8. Error Recovery & Troubleshooting
- If staging reveals defects, fix issues on branch, rebuild release candidate, and redeploy to staging.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/staging-deployment`. | `CUSTOM SKILL` |
| **Cursor** | Select `@staging-deployment` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `staging-deployment`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `staging-deployment` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run staging-deployment`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt staging-deployment`. | `PROMPT FILE` |
| **Windsurf** | Activate `staging-deployment` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `DEPLOYMENT_AND_HOSTING_GUIDE.md`
