---
name: debug-application
description: >-
  Trace a defect methodically through frontend React components, FastAPI APIs, and Celery worker runtimes.
---

# Debug Application

## 1. Purpose & Overview
Traces defect lifecycles across process boundaries, identifying where data contracts break down between frontend UI, backend routers, Celery task payloads, and external APIs.

---

## 2. When to Use & When NOT to Use

### When to Use
- Debugging multi-tier bugs where the failure symptom manifests far from the root cause.
- Tracing claim state transitions that stall or desynchronize.

### When NOT to Use
- Straightforward local compiler or syntax errors.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Reproduction claim ID or user journey steps.
- Access to running services and log streams.

### Prerequisites
- Local services running in debug mode.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Client-Side State Tracing
Trace user action from React click handler through `lib/api.ts` Axios call. Inspect outgoing network payload in DevTools.

### Step 2: API Endpoint Ingestion Tracing
Inspect incoming FastAPI handler parameters and Pydantic validation parsing in `app/api/v1/endpoints/`.

### Step 3: Celery Task Dispatch Inspection
Inspect task argument serialization and message publishing to Redis queue in `app/tasks/queue_runner.py`.

### Step 4: Worker Execution & Scraper Tracing
Trace Celery worker task execution, Playwright page lifecycle, and database persistence.

### Step 5: Response Roundtrip & UI State Mutation
Inspect backend response serialization and frontend state update (`useState`, React Query).

### Step 6: Bug Location Isolation
Pinpoint exact file, function, and line where execution diverged from expected behavior.


---

## 5. Safety Considerations & Guardrails
- Do NOT insert permanent debugging `print()` statements into production code; clean up all debug probes.
- Never expose sensitive credentials during debugging.

---

## 6. Expected Deliverables & Artifacts
- Execution Trace Map documenting exact divergence point.
- Targeted fix recommendation.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Execution path is traced step-by-step from UI trigger to terminal state.
- [ ] Exact location and mechanism of data corruption or failure is proven.
- [ ] Minimal, non-breaking fix proposed.

---

## 8. Error Recovery & Troubleshooting
- If async concurrency obscures debugging, reproduce the failure in an isolated synchronous test script.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/debug-application`. | `CUSTOM SKILL` |
| **Cursor** | Select `@debug-application` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `debug-application`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `debug-application` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run debug-application`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt debug-application`. | `PROMPT FILE` |
| **Windsurf** | Activate `debug-application` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/tasks/queue_runner.py`
- `frontend/src/lib/api.ts`
