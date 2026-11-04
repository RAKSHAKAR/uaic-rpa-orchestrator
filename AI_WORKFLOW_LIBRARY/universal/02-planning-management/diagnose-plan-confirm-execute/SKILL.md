---
name: diagnose-plan-confirm-execute
description: >-
  Universal AI Engineering Governance Skill: Understand -> Inspect -> Diagnose -> Plan -> Confirm -> Execute -> Verify. Enforces NO APPROVAL = NO IMPLEMENTATION.
---

# Diagnose Plan Confirm Execute

## 1. Purpose & Overview
Enforces the mandatory non-negotiable engineering lifecycle across all features, bug fixes, refactorings, and infrastructure modifications. Strictly forbids jumping from prompt to code without an approved plan.

---

## 2. When to Use & When NOT to Use

### When to Use
- ALL non-trivial engineering tasks, architectural changes, bug fixes, or database migrations.
- Any change that touches more than one file or alters system contracts.

### When NOT to Use
- Trivial questions where the user explicitly requests an immediate one-line text answer without modifying code.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- User request, relevant codebase files, test suites, and documentation history in `docs/`.

### Prerequisites
- Completed inspection of target modules and baseline test pass rates.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Understand & Inspect
Analyze the user prompt, inspect relevant code/configuration, review `README.md` and historical records in `docs/`.

### Step 2: Diagnose & Gap Analysis
Identify root causes with concrete evidence. Compare current state against expected requirements.

### Step 3: Detailed Implementation Plan Authoring
Author a comprehensive plan with Implementation ID (`IMP-YYYY-MMDD-NNN`), affected files, test plan, risks, and rollback steps. Save to `docs/` and create session artifact.

### Step 4: Confirmation Gate (Wait for Approval)
Present the plan to the user. Strictly wait for explicit human approval before touching any code. NO APPROVAL = NO IMPLEMENTATION.

### Step 5: Execute & Document
Implement approved changes following strict coding conventions. Update `README.md` and documentation.

### Step 6: Verify & Finalize
Run automated test suites (`pytest`, `tsc`, `ruff`, `ps1`). Record visual and log evidence. Finalize documentation.


---

## 5. Safety Considerations & Guardrails
- NEVER modify source code before presenting a plan and receiving explicit approval.
- Never fabricate test results, approvals, or deployment status.
- Do not mark documentation as Human Verified—only the human user can do that.

---

## 6. Expected Deliverables & Artifacts
- Formal Implementation Plan in `docs/YYYY-MM-DD_uaic_<feature>_implementation_plan_v<N>.md`.
- Interactive Plan Artifact in brain directory.
- Final Verified Record and Walkthrough Document.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Implementation plan approved explicitly by user before code modification.
- [ ] 100% of planned tests pass with verifiable automated evidence.
- [ ] `README.md` and related docs updated to reflect changes.

---

## 8. Error Recovery & Troubleshooting
- If user rejects the plan, return to Step 2, incorporate feedback, and author revised plan `_v2.md`.
- If unexpected errors occur during execution, pause, document the gap, and seek user confirmation if scope changes.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/diagnose-plan-confirm-execute` or follow the mandatory governance rule. | `CUSTOM SKILL` |
| **Cursor** | Select `@diagnose-plan-confirm-execute` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code: 'Follow the diagnose-plan-confirm-execute lifecycle.' | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Mandated by `AGENTS.md` in OpenAI Codex. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run diagnose-plan-confirm-execute`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt diagnose-plan-confirm-execute`. | `PROMPT FILE` |
| **Windsurf** | Activate `diagnose-plan-confirm-execute` rule in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `.agents/skills/diagnose-plan-confirm-execute/SKILL.md` (Authoritative Governance Skill)
- `AGENTS.md` - Section 8 (AI Agent Rules)
