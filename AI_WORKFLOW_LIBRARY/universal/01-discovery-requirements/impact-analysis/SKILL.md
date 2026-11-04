---
name: impact-analysis
description: >-
  Trace affected modules, data models, API endpoints, background tasks, tests, and users for any proposed code or architectural change.
---

# Impact Analysis

## 1. Purpose & Overview
Calculates the blast radius of a planned change before execution, ensuring that all upstream and downstream ramifications are understood, tested, and accounted for.

---

## 2. When to Use & When NOT to Use

### When to Use
- Modifying database schemas, columns, or relationship constraints.
- Refactoring shared API response schemas or frontend typed models.
- Altering Celery task signatures, queue names, or scheduling intervals.

### When NOT to Use
- Adding isolated documentation or standalone diagnostic scripts.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Description or diff of the proposed change.
- Repository source tree and test files.

### Prerequisites
- Completed `existing-system-assessment`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Scope & Target Identification
Identify the primary files, functions, schemas, or models proposed for modification.

### Step 2: Static Dependency Traversal
Trace all direct and indirect references to the target symbols across backend APIs, Celery tasks, and frontend components.

### Step 3: Data Model & Persistence Impact
Determine if database tables, migrations, serialized JSON bodies, or cache keys are affected.

### Step 4: API Contract & Client Impact
Determine if frontend Axios endpoints, TypeScript types (`types/index.ts`), or external API payloads (Guidewire) are altered.

### Step 5: Test Suite & Harness Impact
Identify all unit, integration, and E2E tests that exercise the affected paths and must be updated or re-verified.

### Step 6: Impact Matrix Formulation
Construct an Impact Matrix detailing affected components, risk severity, required test suites, and rollback considerations.


---

## 5. Safety Considerations & Guardrails
- Flag any change that modifies database schemas without backward compatibility as High/Critical risk.
- Ensure external third-party contracts (Guidewire payload schema) remain strictly backward-compatible.

---

## 6. Expected Deliverables & Artifacts
- Impact & Blast Radius Matrix.
- Mandatory Test Verification Checklist for the proposed change.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Every affected backend module, frontend page, database table, and test suite is enumerated.
- [ ] Breaking change risks are classified and mitigation strategies documented.
- [ ] Explicit test commands are listed for post-implementation verification.

---

## 8. Error Recovery & Troubleshooting
- If blast radius is unexpectedly large, recommend refactoring using the Strangler Fig or adapter pattern to isolate the change.
- If downstream callers cannot be safely updated at once, maintain dual-mode support during migration.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/impact-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@impact-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `impact-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `impact-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run impact-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt impact-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `impact-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 3 (Critical Business Rules) & Section 11 (Guidewire Contract)
- `backend/app/schemas/settings.py`
