---
name: technical-feasibility
description: >-
  Compare feasible implementation approaches, technical constraints, performance trade-offs, and risks before choosing a path.
---

# Technical Feasibility

## 1. Purpose & Overview
Conducts comparative technical trade-off analysis between 2 or more architecture/implementation candidates, evaluating performance, maintainability, risk, and delivery effort.

---

## 2. When to Use & When NOT to Use

### When to Use
- Choosing between competing third-party libraries, architectural patterns, or database technologies.
- Designing complex features with multiple viable designs (e.g., synchronous vs asynchronous scraping).
- Resolving major architectural blockers.

### When NOT to Use
- Implementing standard boilerplate with established project patterns.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Problem statement and functional requirements.
- Candidate technical approaches.

### Prerequisites
- Understanding of project performance targets and infrastructure constraints.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Candidate Approach Formulation
Define at least 2 distinct technical approaches (e.g. Option A: Synchronous In-Process Playwright vs Option B: Remote CDP WebSocket Worker).

### Step 2: Evaluation Criteria Definition
Establish objective evaluation criteria: Performance & Latency, Memory Overhead, Reliability, Implementation Complexity, and Maintenance Cost.

### Step 3: Comparative Scoring & Trade-Off Analysis
Score each candidate against criteria with documented technical rationale and benchmark evidence.

### Step 4: Risk & Failure Mode Analysis
Identify edge-case failure modes for each approach (e.g. extension crashes, zombie processes, memory leaks).

### Step 5: Recommendation & Decision Matrix
Select the optimal approach with justified rationale and draft a recommended adoption roadmap.


---

## 5. Safety Considerations & Guardrails
- Never select an approach that violates project non-negotiables (e.g. AntiCaptcha MV3 stability, Python 3.14 compatibility).
- Do not optimize prematurely for hypothetical scale at the expense of current stability.

---

## 6. Expected Deliverables & Artifacts
- Technical Feasibility & Trade-Off Assessment Document.
- Candidate Comparison Matrix with final architectural recommendation.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] At least 2 viable approaches are rigorously evaluated across objective criteria.
- [ ] Constraints, risks, and failure modes are explicitly identified for each option.
- [ ] The recommended approach is directly aligned with project business rules.

---

## 8. Error Recovery & Troubleshooting
- If trade-off scores are tied, prioritize the approach with lower implementation complexity and lower blast radius.
- If uncertain about external library behavior, run a lightweight spike script in `scripts/`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/technical-feasibility`. | `CUSTOM SKILL` |
| **Cursor** | Select `@technical-feasibility` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `technical-feasibility`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `technical-feasibility` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run technical-feasibility`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt technical-feasibility`. | `PROMPT FILE` |
| **Windsurf** | Activate `technical-feasibility` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Must Do / Must Not Do)
- `docs/DEVELOPMENT_WORKFLOW.md`
