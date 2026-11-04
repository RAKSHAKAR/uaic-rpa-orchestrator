---
name: effort-estimation
description: >-
  Estimate engineering effort using structured three-point estimation (Optimistic, Most Likely, Pessimistic) with explicit assumptions.
---

# Effort Estimation

## 1. Purpose & Overview
Provides realistic, evidence-based effort estimates accounting for technical uncertainty, third-party dependencies, and testing overhead.

---

## 2. When to Use & When NOT to Use

### When to Use
- Scoping feature releases, sprint planning, or roadmap formulation.
- Evaluating architectural alternatives where development time is a primary constraint.

### When NOT to Use
- Simple operational commands or running pre-existing scripts.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved WBS or task breakdown.
- Historical velocity and technical complexity ratings.

### Prerequisites
- Completed `task-breakdown` or `wbs-creation`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Task Isolation & Complexity Rating
Review each atomic task. Rate complexity (Low, Medium, High, Extreme) based on dependencies and novelty.

### Step 2: Three-Point Estimation
For each task, estimate Optimistic (O), Most Likely (M), and Pessimistic (P) hours.

### Step 3: PERT Expected Value Calculation
Compute expected effort using PERT formula: $E = (O + 4M + P) / 6$, and standard deviation: $\sigma = (P - O) / 6$.

### Step 4: Assumption & Risk Listing
Explicitly record all assumptions (e.g., third-party API availability, mock server readiness) that underpin the estimates.

### Step 5: Estimation Report Synthesis
Produce an Effort Estimation Summary with total expected effort, confidence intervals, and contingency recommendations.


---

## 5. Safety Considerations & Guardrails
- Never present a single-point estimate for high-uncertainty tasks.
- Always include automated testing and documentation time in task estimates.

---

## 6. Expected Deliverables & Artifacts
- Three-Point Effort Estimation Table.
- Documented Technical Assumptions & Contingency Buffer.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All tasks in scope have O, M, and P estimates with calculated PERT values.
- [ ] Underlying assumptions are explicitly stated.
- [ ] Testing and verification effort is explicitly budgeted.

---

## 8. Error Recovery & Troubleshooting
- If an assumption is invalidated during implementation, re-estimate affected tasks immediately.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/effort-estimation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@effort-estimation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `effort-estimation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `effort-estimation` in Codex prompt. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run effort-estimation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt effort-estimation`. | `PROMPT FILE` |
| **Windsurf** | Activate `effort-estimation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/DEVELOPMENT_WORKFLOW.md`
