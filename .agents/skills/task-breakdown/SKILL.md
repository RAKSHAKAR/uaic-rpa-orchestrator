---
name: task-breakdown
description: >-
  Split work packages or user stories into small, atomic, testable, and independently verifiable implementation tasks.
---

# Task Breakdown

## 1. Purpose & Overview
Converts broad feature objectives into atomic engineering tasks that can be implemented and verified within focused coding sessions without context loss.

---

## 2. When to Use & When NOT to Use

### When to Use
- Translating an approved implementation plan or WBS into executable steps.
- Prior to starting a complex coding turn.

### When NOT to Use
- When executing an already itemized task list.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved implementation plan or feature specification.

### Prerequisites
- Clear understanding of affected files and technical design.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Atomicity Scoping
Decompose work packages such that each task modifies 1-3 related files and takes < 2 hours of focused effort.

### Step 2: Sequential Dependency Ordering
Order tasks logically: Data Model/Migration -> Service/Business Logic -> API Endpoints -> Frontend UI -> E2E Tests.

### Step 3: Verification Command Assignment
Assign an exact automated test or verification command to each individual task.

### Step 4: Checkpoint & Commit Mapping
Define logical git commit points and state checkpoints between tasks.

### Step 5: Task Checklist Generation
Generate an interactive markdown task list (`- [ ] Task Description`).


---

## 5. Safety Considerations & Guardrails
- Never create tasks that leave the repository in a broken build state across checkpoints.
- Ensure database migrations are isolated into dedicated pre-deployment tasks.

---

## 6. Expected Deliverables & Artifacts
- Itemized Task Checklist with file paths and verification commands.
- Sequential Execution Roadmap.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Every task is atomic, testable, and assigned specific file targets.
- [ ] Each task includes an exact PowerShell verification command.
- [ ] Dependencies between tasks are strictly respected in ordering.

---

## 8. Error Recovery & Troubleshooting
- If a task proves too complex during implementation, pause and split it into two sub-tasks.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/task-breakdown`. | `CUSTOM SKILL` |
| **Cursor** | Select `@task-breakdown` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `task-breakdown`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `task-breakdown` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run task-breakdown`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt task-breakdown`. | `PROMPT FILE` |
| **Windsurf** | Activate `task-breakdown` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`
