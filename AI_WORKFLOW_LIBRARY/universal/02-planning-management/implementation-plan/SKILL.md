---
name: implementation-plan
description: >-
  Produce structured technical implementation plans with affected files, explicit code diff previews, test strategies, and rollback plans.
---

# Implementation Plan

## 1. Purpose & Overview
Creates high-fidelity technical design documents that allow engineers and users to make informed, risk-aware decisions before any code changes occur.

---

## 2. When to Use & When NOT to Use

### When to Use
- Directly following diagnosis and requirements analysis for any significant feature or bug fix.
- When responding to `/plan` slash command.

### When NOT to Use
- Executing pre-approved code changes.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Diagnosis findings, requirements specification, and target file paths.

### Prerequisites
- Verified root cause and confirmed requirements.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Metadata & Header Initialization
Assign Implementation ID (`IMP-YYYY-MMDD-NNN`), author, date, status (Awaiting Approval), and target repository.

### Step 2: Goal & Background Description
State the core problem, context, and expected business outcome concisely.

### Step 3: Proposed File Changes & Diffs
Group proposed changes by component. Explicitly label files as `[NEW]`, `[MODIFY]`, or `[DELETE]`. Provide exact diff previews.

### Step 4: Verification Plan Specification
Define exact automated test commands (`pytest`, `tsc`, `ruff`, Playwright) and manual verification steps.

### Step 5: Risk Analysis & Rollback Strategy
Detail potential failure modes, mitigation steps, and an unambiguous rollback protocol.

### Step 6: Document Archival
Save plan to `docs/` and generate the user-facing interactive artifact.


---

## 5. Safety Considerations & Guardrails
- Always include diff previews for critical business logic to prevent subtle regressions.
- Never omit the rollback strategy.

---

## 6. Expected Deliverables & Artifacts
- Standardized Implementation Plan Document in `docs/`.
- Session Plan Artifact with `request_feedback: true`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Plan contains all required sections (Goal, Review Required, Proposed Changes, Verification, Risks, Rollback).
- [ ] Every affected file is categorized and accompanied by explicit diff or code snippets.
- [ ] Automated test commands are exact and executable directly in PowerShell.

---

## 8. Error Recovery & Troubleshooting
- If user requests modifications to the plan, update the document with incremented version (`_v2.md`).

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via `/plan` or `/implementation-plan`. | `CUSTOM SKILL` |
| **Cursor** | Select `@implementation-plan` in Cursor. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code: 'Create a formal implementation plan.' | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `implementation-plan` in Codex. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run implementation-plan`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt implementation-plan`. | `PROMPT FILE` |
| **Windsurf** | Activate `implementation-plan` workflow in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`
- `AGENTS.md` - Section 8
