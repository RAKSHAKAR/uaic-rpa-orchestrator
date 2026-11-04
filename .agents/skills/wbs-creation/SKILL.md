---
name: wbs-creation
description: >-
  Create a hierarchical, deliverable-oriented Work Breakdown Structure decomposing complex projects into manageable work packages.
---

# Wbs Creation

## 1. Purpose & Overview
Structures complex initiatives into discrete, mutually exclusive work packages (100% Rule), establishing ownership boundaries and deliverable gates.

---

## 2. When to Use & When NOT to Use

### When to Use
- Initiating large multi-week features, platform migrations, or new microservices.
- Coordinating complex multi-stage tasks across frontend, backend, and DevOps.

### When NOT to Use
- Single-file bug fixes or straightforward routine maintenance.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved project scope, functional requirements, and target architecture.

### Prerequisites
- Completed `requirement-analysis` and `architecture-analysis`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Top-Level Phase Partitioning
Partition total scope into primary chronological or architectural phases (e.g., Phase 1: Database, Phase 2: Backend API, Phase 3: Frontend UI, Phase 4: E2E Testing).

### Step 2: Work Package Decomposition
Decompose each phase into discrete Work Packages (WP-01, WP-02, ...), adhering to the 100% Rule (encompassing total scope with zero overlap).

### Step 3: Deliverable & Milestone Definition
Assign concrete, verifiable deliverables and completion gates to each work package.

### Step 4: Traceability Mapping
Cross-reference each work package with specific functional requirement IDs from the Requirements Traceability Matrix.

### Step 5: WBS Document Generation
Generate a structured WBS tabular breakdown and visual tree diagram (`graph TD`).


---

## 5. Safety Considerations & Guardrails
- Ensure zero work packages are defined without concrete, verifiable acceptance criteria.
- Do not allow overlapping or ambiguous scope between work packages.

---

## 6. Expected Deliverables & Artifacts
- Formal Work Breakdown Structure Document.
- Mermaid WBS Tree Diagram.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 100% of project requirements are mapped to at least one work package.
- [ ] Every work package has an unambiguous deliverable and objective acceptance gate.
- [ ] Dependencies between packages are clearly identified.

---

## 8. Error Recovery & Troubleshooting
- If scope creeps or changes during development, revise the WBS document and update package IDs.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/wbs-creation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@wbs-creation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `wbs-creation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `wbs-creation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run wbs-creation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt wbs-creation`. | `PROMPT FILE` |
| **Windsurf** | Activate `wbs-creation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/DEVELOPMENT_WORKFLOW.md`
