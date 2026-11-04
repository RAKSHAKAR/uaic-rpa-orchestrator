---
name: milestone-planning
description: >-
  Define project milestones, sequencing constraints, critical paths, and unambiguous exit criteria for each development stage.
---

# Milestone Planning

## 1. Purpose & Overview
Establishes clear, objective checkpoint milestones along the development timeline to maintain momentum, validate progress, and catch regressions early.

---

## 2. When to Use & When NOT to Use

### When to Use
- Structuring multi-phase delivery cycles.
- Coordinating integration deadlines between frontend and backend teams.

### When NOT to Use
- Day-to-day atomic task execution.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- WBS, effort estimates, and external deadline constraints.

### Prerequisites
- Completed `wbs-creation` and `dependency-planning`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Milestone Identification
Define 3-5 major project milestones (e.g., M1: Core Engine & DB Verified, M2: APIs & Workers Operational, M3: Frontend & End-to-End Complete, M4: Release Ready).

### Step 2: Critical Path Mapping
Identify sequence of dependent tasks that determines the minimum total project duration.

### Step 3: Exit Criteria Formulation
Define measurable, non-negotiable exit criteria for each milestone (e.g., 100% unit tests pass, zero lint errors, verified staging run).

### Step 4: Sign-Off & Gatekeeper Definition
Assign verification authority (Human Operator, Automated Test Suite) for each milestone gate.

### Step 5: Milestone Schedule Synthesis
Publish the Milestone Schedule with target completion windows and dependency triggers.


---

## 5. Safety Considerations & Guardrails
- Never advance past a milestone if exit criteria are not 100% satisfied.
- Do not compress testing windows on the critical path to meet deadlines.

---

## 6. Expected Deliverables & Artifacts
- Project Milestone Schedule and Critical Path Map.
- Milestone Exit Verification Checklist.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All milestones have distinct, measurable technical exit criteria.
- [ ] Critical path dependencies are explicitly mapped.
- [ ] Gate review protocols are defined for each stage transition.

---

## 8. Error Recovery & Troubleshooting
- If a milestone gate fails, trigger an immediate diagnosis pass and adjust subsequent milestone schedules.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/milestone-planning`. | `CUSTOM SKILL` |
| **Cursor** | Select `@milestone-planning` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `milestone-planning`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `milestone-planning` in Codex prompt. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run milestone-planning`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt milestone-planning`. | `PROMPT FILE` |
| **Windsurf** | Activate `milestone-planning` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/DEVELOPMENT_WORKFLOW.md`
