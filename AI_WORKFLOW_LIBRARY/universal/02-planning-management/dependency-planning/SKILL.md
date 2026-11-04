---
name: dependency-planning
description: >-
  Identify sequencing constraints, critical paths, blockers, and external dependencies before initiating development.
---

# Dependency Planning

## 1. Purpose & Overview
Prevents pipeline stalls, merge conflicts, and rework by mapping architectural and team dependencies before writing code.

---

## 2. When to Use & When NOT to Use

### When to Use
- Planning multi-service or cross-functional development sprints.
- Coordinating changes that touch shared database tables or core configuration.

### When NOT to Use
- Isolated tasks with zero external dependencies.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Task breakdown and architecture component map.

### Prerequisites
- Completed `task-breakdown`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Dependency Identification
For every task, enumerate mandatory prerequisites (e.g. Task C requires Task A DB migration and Task B API schema).

### Step 2: Dependency Graph Construction
Construct a directed acyclic graph (DAG) of task dependencies using Mermaid (`graph LR`).

### Step 3: Cycle Detection & Decoupling
Detect and resolve circular dependencies using interface abstraction or mock adapters.

### Step 4: Critical Path Identification
Highlight tasks on the critical path that directly impact final delivery date.

### Step 5: Parallel Workstream Tagging
Identify independent tasks that can be safely executed concurrently by parallel agents.


---

## 5. Safety Considerations & Guardrails
- Do NOT run tasks in parallel if they modify the same shared files.
- Ensure database schema changes are strictly sequenced before code that depends on new columns.

---

## 6. Expected Deliverables & Artifacts
- Task Dependency DAG & Critical Path Map.
- Parallel Workstream Matrix.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero circular dependencies exist in the execution plan.
- [ ] All parallel workstreams operate on strictly disjoint file sets.
- [ ] Prerequisites for every critical task are verified before execution begins.

---

## 8. Error Recovery & Troubleshooting
- If a blocking dependency is delayed, pivot to an independent workstream or implement a stub interface.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/dependency-planning`. | `CUSTOM SKILL` |
| **Cursor** | Select `@dependency-planning` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `dependency-planning`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `dependency-planning` in Codex prompt. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run dependency-planning`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt dependency-planning`. | `PROMPT FILE` |
| **Windsurf** | Activate `dependency-planning` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/DEVELOPMENT_WORKFLOW.md`
