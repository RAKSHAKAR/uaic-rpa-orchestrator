---
name: authentication-authorization
description: >-
  Implement authentication, role-based authorization (RBAC), secure session cookies, API tokens, and access boundaries.
---

# Authentication Authorization

## 1. Purpose & Overview
Establishes multi-layer security controls protecting sensitive routes, APIs, and administrative functions from unauthorized access, privilege escalation, or session hijacking.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding authentication to unprotected endpoints or administrative control panels.
- Implementing role-based permissions (Admin, Operator, Read-Only Auditor).
- Hardening API token authentication for automated system clients.

### When NOT to Use
- Public health-check endpoints (`/health`).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- User identity models, role definitions, permission matrix, and token signing secrets.

### Prerequisites
- Cryptographic hashing library (e.g. `passlib`, `bcrypt`, `pyjwt`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Identity & Credential Modeling
Define User, Role, and Permission entities with hashed password storage (bcrypt/argon2).

### Step 2: Token & Session Management
Implement JWT or secure HTTP-only session cookie issuance with explicit expiration and rotation policies.

### Step 3: FastAPI Security Dependency Injection
Create security dependencies (`get_current_user`, `require_admin_role`) using FastAPI `Security` and `HTTPBearer`.

### Step 4: Role & Permission Matrix Enforcement
Enforce permission checks at endpoint boundaries. Block unauthorized requests with 401 Unauthorized or 403 Forbidden.

### Step 5: Frontend Auth State & Route Protection
Implement client-side authentication guards, token refresh interceptors, and login/logout state transitions.

### Step 6: Security Test Suite Execution
Write tests verifying that unauthenticated and unauthorized requests are rejected consistently.


---

## 5. Safety Considerations & Guardrails
- Never store plain-text passwords or secret keys in source code or repositories.
- Ensure session cookies specify `HttpOnly`, `Secure`, and `SameSite=Lax/Strict` attributes.

---

## 6. Expected Deliverables & Artifacts
- Authentication dependencies and role-based guards.
- Automated security tests verifying access control enforcement.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Protected endpoints reject unauthenticated requests with HTTP 401.
- [ ] Role restrictions reject unauthorized users with HTTP 403.
- [ ] Passwords are hashed with salt using modern cryptographic algorithms.

---

## 8. Error Recovery & Troubleshooting
- If token expiration causes UI loops, implement seamless refresh token handling in Axios interceptors.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/authentication-authorization`. | `CUSTOM SKILL` |
| **Cursor** | Select `@authentication-authorization` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `authentication-authorization`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `authentication-authorization` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run authentication-authorization`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt authentication-authorization`. | `PROMPT FILE` |
| **Windsurf** | Activate `authentication-authorization` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/core/config.py`
- `AGENTS.md` - Section 8
