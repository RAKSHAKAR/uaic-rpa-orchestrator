---
name: security-testing
description: >-
  Test authentication boundaries, SQL injection resistance, secret leakage prevention, and CORS policies.
---

# Security Testing

## 1. Purpose & Overview
Executes active and passive security tests probing API endpoints for injection vulnerabilities, unauthorized access, broken object-level authorization, and secret leakage.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pre-release security validation.
- Adding file upload or user parameter parsing endpoints.
- Testing authentication and authorization controls.

### When NOT to Use
- Internal non-networked unit tests.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Security testing payloads (SQL injection strings, XSS scripts, path traversal strings).

### Prerequisites
- FastAPI application running in test mode.

---

## 4. Step-by-Step Execution Procedure

### Step 1: SQL Injection Probing
Inject SQL metacharacters (`' OR '1'='1`, `'; DROP TABLE;--`) into API search query parameters. Confirm ORM parameterized queries neutralize all attacks.

### Step 2: Path Traversal & File Upload Probing
Upload files with malicious filenames (`../../etc/passwd`, `test.exe`). Confirm server sanitizes filenames and restricts upload directories.

### Step 3: Cross-Site Scripting (XSS) Probing
Inject HTML/JavaScript payloads (`<script>alert(1)</script>`) into claim names and case styles. Confirm React properly escapes strings on rendering.

### Step 4: Broken Object-Level Authorization (BOLA)
Attempt to access, update, or delete claim records using non-owner credentials. Confirm 403 Forbidden is enforced.

### Step 5: Secret Redaction Verification
Trigger application errors deliberately. Verify stack traces and response bodies redact database passwords and API tokens.

### Step 6: Security Test Summary
Publish findings in a formal Security Verification Report.


---

## 5. Safety Considerations & Guardrails
- Never execute security tests against systems you do not own or have explicit authorization to test.
- Use benign test payloads that do not damage database integrity.

---

## 6. Expected Deliverables & Artifacts
- Automated Security Test Suite.
- Security Verification Report confirming zero exploitable vulnerabilities.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero SQL injection, XSS, or path traversal vulnerabilities detected.
- [ ] Unauthorized requests are consistently rejected.
- [ ] Zero secrets or sensitive credentials leak into responses or logs.

---

## 8. Error Recovery & Troubleshooting
- If any injection or authorization vulnerability is discovered, halt release immediately and patch the boundary.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/security-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@security-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `security-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `security-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run security-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt security-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `security-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8
- `backend/app/core/config.py`
