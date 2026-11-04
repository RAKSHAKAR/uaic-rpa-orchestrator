---
name: multi-tenant-development
description: >-
  Enforce strict tenant, organization, or carrier data isolation across database queries, caching, and background workers.
---

# Multi Tenant Development

## 1. Purpose & Overview
Guarantees complete data segregation between different business tenants or carriers, preventing cross-tenant data leakage in multi-tenant SaaS environments.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding multi-carrier or multi-organization support to the platform.
- Auditing database queries and cache keys for data leakage risks.

### When NOT to Use
- Single-tenant dedicated local installations.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Tenant entity definitions, tenant identification headers/tokens, and database isolation strategy (row-level, schema-level, or DB-level).

### Prerequisites
- Understanding of tenant context propagation in async Python and Next.js.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Tenant Context Extraction
Extract tenant identity from incoming requests (subdomain, JWT claim, or `X-Tenant-ID` header) via middleware.

### Step 2: Context Variable Binding
Bind active tenant ID to Python `contextvars.ContextVar` or request state for thread-safe access.

### Step 3: ORM Query Filtering Enforcement
Ensure all database queries automatically filter by `tenant_id` using SQLAlchemy event listeners or base queries.

### Step 4: Cache & Task Partitioning
Prefix all Redis cache keys and Celery task payload arguments with the active `tenant_id`.

### Step 5: Tenant Isolation Test Pass
Write automated tests creating records under Tenant A and proving Tenant B cannot query or mutate them.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never execute unfiltered queries (`select(Model)`) without tenant scoping in a multi-tenant environment.
- Ensure shared background workers do not leak tenant state across tasks.

---

## 6. Expected Deliverables & Artifacts
- Tenant middleware, context handlers, and auto-filtering query hooks.
- Multi-tenant isolation verification test suite.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All queries are strictly partitioned by tenant ID.
- [ ] Cross-tenant data access attempts return 404 or 403.
- [ ] Cache keys and background queues maintain clean tenant namespaces.

---

## 8. Error Recovery & Troubleshooting
- If an un-scoped query is detected, patch the repository layer to mandate tenant parameters.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/multi-tenant-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@multi-tenant-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `multi-tenant-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `multi-tenant-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run multi-tenant-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt multi-tenant-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `multi-tenant-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/core/database.py`
