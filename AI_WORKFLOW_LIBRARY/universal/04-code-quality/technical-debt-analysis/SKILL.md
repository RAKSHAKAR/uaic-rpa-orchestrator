---
name: technical-debt-analysis
description: >-
  Catalog and prioritize technical debt by business risk, remediation effort, and operational impact.
---

# Technical Debt Analysis

## 1. Purpose & Overview
Provides a structured framework to inventory architectural shortcuts, deprecated dependencies, test skips, and workaround logic, formulating an actionable remediation roadmap.

---

## 2. When to Use & When NOT to Use

### When to Use
- Periodic engineering health reviews or roadmap planning.
- Inheriting legacy modules or preparing for production scaling.
- Auditing pre-existing test skips and temporary workarounds.

### When NOT to Use
- Triaging immediate active production outages (use `diagnose-issue`).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Codebase source files, test skip markers (`@pytest.mark.skip`), TODO comments, and issue trackers.

### Prerequisites
- Completed `project-deep-analysis`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Technical Debt Discovery
Grep codebase for `TODO`, `FIXME`, `HACK`, `WORKAROUND`, and `@pytest.mark.skip`. Identify deprecated library usage.

### Step 2: Categorization & Scoring
Categorize debt: Architectural, Code Quality, Test Coverage, Security, or Documentation. Score each item on Severity (1-5) and Remediation Effort (1-5).

### Step 3: Business Risk Analysis
Evaluate operational impact: data loss risk, performance degradation, maintenance slowdown, or compliance risk.

### Step 4: Prioritization Matrix
Rank debt items into Quick Wins (High Impact, Low Effort), Strategic Projects (High Impact, High Effort), and Deprioritized items.

### Step 5: Technical Debt Backlog Synthesis
Author a comprehensive Technical Debt Register with actionable remediation tickets.


---

## 5. Safety Considerations & Guardrails
- Do NOT arbitrarily remove working workarounds without understanding why they were introduced.
- Preserve pre-existing org-policy test skips documented in `AGENTS.md`.

---

## 6. Expected Deliverables & Artifacts
- Prioritized Technical Debt Register with risk scores and effort estimates.
- Remediation Roadmap linked to specific files and lines.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All TODO/FIXME markers and test skips are catalogued and evaluated.
- [ ] High-risk architectural bottlenecks are prioritized for remediation.
- [ ] Remediation tasks include explicit acceptance criteria.

---

## 8. Error Recovery & Troubleshooting
- If remediating a debt item introduces complex dependencies, break it down into an ADR and implementation plan.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/technical-debt-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@technical-debt-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `technical-debt-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `technical-debt-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run technical-debt-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt technical-debt-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `technical-debt-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 7 (Test Commands & Pre-existing Skips)
- `docs/`
