---
name: security-audit
description: >-
  Review application security risks, OWASP Top 10 vulnerabilities, credential leakage, and authorization boundaries.
---

# Security Audit

## 1. Purpose & Overview
Conducts systematic security evaluations across source code, dependencies, database queries, and network configurations to eliminate vulnerabilities and enforce defensive coding.

---

## 2. When to Use & When NOT to Use

### When to Use
- Prior to production releases or major architectural milestones.
- Adding authentication, user input parsing, or file upload endpoints.
- Auditing credential storage and environment variable handling.

### When NOT to Use
- Non-security documentation edits.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Full codebase access, configuration files, and API endpoint definitions.

### Prerequisites
- Knowledge of OWASP Top 10 vulnerabilities (Injection, Broken Auth, SSRF, XSS).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Credential Leakage & Secret Audit
Scan repository for unmasked secrets, hardcoded API keys, private keys, or credentials using pattern detection.

### Step 2: Injection & SQL Safety Review
Audit database queries. Confirm 100% usage of parameterized ORM queries (`select(Model).where(...)`); verify zero raw string interpolation.

### Step 3: Input Validation & File Upload Security
Inspect file upload endpoints (`/api/v1/ingest/upload`). Verify file type validation, size limits, and safe storage paths.

### Step 4: CORS & Security Headers Audit
Check FastAPI CORS middleware settings (`allow_origins`), Content-Security-Policy, and cookie security attributes.

### Step 5: Authorization & RBAC Enforcement
Verify that all mutating endpoints (`POST`, `PUT`, `DELETE`) require authorization.

### Step 6: Security Audit Report Synthesis
Publish a comprehensive Security Audit Report categorizing findings by CVSS severity with remediation steps.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never commit detected secrets or private keys to version control during auditing.
- Immediately rotate any credential discovered in plain-text.

---

## 6. Expected Deliverables & Artifacts
- Comprehensive Security Audit Report.
- Prioritized Remediation Backlog for identified security gaps.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero plain-text credentials or API keys found in codebase.
- [ ] 100% of database queries use parameterized ORM statements.
- [ ] File upload handlers enforce strict extension and size boundaries.

---

## 8. Error Recovery & Troubleshooting
- If an active secret is found in git history, initiate git secret purge and rotate the key immediately.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/security-audit`. | `CUSTOM SKILL` |
| **Cursor** | Select `@security-audit` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `security-audit`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `security-audit` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run security-audit`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt security-audit`. | `PROMPT FILE` |
| **Windsurf** | Activate `security-audit` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Must Not Do)
- `backend/app/core/config.py`
