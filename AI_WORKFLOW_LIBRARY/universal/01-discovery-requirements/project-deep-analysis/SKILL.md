---
name: project-deep-analysis
description: >-
  Inspect the repository architecture, code entry points, database models, internal interfaces, test suites, and runtime behaviors in depth.
---

# Project Deep Analysis

## 1. Purpose & Overview
Performs exhaustive technical code-level analysis across frontend, backend, database layers, background queues, and test infrastructure to build an authoritative mental model of code paths and system state.

---

## 2. When to Use & When NOT to Use

### When to Use
- Prior to authoring complex, multi-service implementation plans.
- Diagnosing deep architectural regressions or elusive lifecycle bugs.
- Evaluating migration paths for frameworks, databases, or runtime environments.

### When NOT to Use
- High-level initial project discovery (use `project-discovery` instead).
- Isolated UI styling tweaks that do not touch state or backend services.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Full read access to source trees (`backend/app`, `frontend/src`, `e2e`, `tests`).
- Git log history to trace recent architectural changes.

### Prerequisites
- Completed `project-discovery` phase.
- Local environment tooling available for passive type-checking and test suite introspection.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Backend Architecture & Data Flow Inspection
Trace request flow from FastAPI routers (`app/api/v1/router.py`) through service layers (`app/services/`) to database models (`app/models/`). Inspect transaction lifecycles and session management.

### Step 2: Frontend State & Component Hierarchy Inspection
Analyze Next.js App Router layout (`layout.tsx`), client state providers (`BrandingContext`, React Query), API clients (`lib/api.ts`), and TypeScript contracts (`types/index.ts`).

### Step 3: Asynchronous Task & Worker Pipeline Inspection
Inspect Celery tasks (`app/tasks/`), queue routing configurations, broker bindings, retry mechanisms, and concurrency semaphores.

### Step 4: Test Coverage & Harness Audit
Analyze test suites in `tests/` and `e2e/`. Identify mocked vs. live integration tests, coverage gaps, and pre-existing skips.

### Step 5: Synthesis & Technical Deep Analysis Report
Produce an authoritative technical deep-analysis document highlighting architectural strengths, bottlenecks, and structural constraints.


---

## 5. Safety Considerations & Guardrails
- Strictly read-only; no code modifications permitted.
- Avoid running tests that perform live network calls or database truncations during deep analysis.

---

## 6. Expected Deliverables & Artifacts
- Deep Technical Architecture & Component Analysis Document.
- Detailed dataflow diagram and transaction boundary map.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Every primary API router, service layer, and database model is documented with line references.
- [ ] Async queue bindings and task lifecycles are mapped end-to-end.
- [ ] Current test coverage and harness limitations are explicitly quantified.

---

## 8. Error Recovery & Troubleshooting
- If circular imports or obfuscated logic are detected, trace execution starting from test files or FastAPI entrypoint.
- If dynamic imports obscure routing, check router inclusion statements in `app/api/v1/router.py`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/project-deep-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@project-deep-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `project-deep-analysis` guidelines. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `project-deep-analysis` in OpenAI Codex. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run project-deep-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt project-deep-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `project-deep-analysis` rule in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 2 (Repository Layout) & Section 5 (API Endpoints Summary)
- `docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`
