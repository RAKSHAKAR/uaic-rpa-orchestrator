---
name: agent-self-review
description: >-
  Require an independent, objective self-audit of code changes against requirements prior to presenting results to the user.
---

# Agent Self Review

## 1. Purpose & Overview
Mandates that AI agents audit their own code modifications against the approved plan and requirements before presenting completion, catching omitted edge cases and unintended side-effects.

---

## 2. When to Use & When NOT to Use

### When to Use
- Immediately following code implementation and before notifying the user of completion.
- Prior to submitting an implementation plan for review.

### When NOT to Use
- During initial discovery before code exists.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved implementation plan, requirements checklist, git working tree diff, and test outputs.

### Prerequisites
- Completed code modifications.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Working Tree Diff Audit
Run `git diff` or inspect all modified files. Verify every changed line is intentional and directly related to the approved plan.

### Step 2: Requirements Cross-Check
Step through the approved plan's acceptance criteria one by one. Confirm concrete implementation and test evidence for each.

### Step 3: Unintended Modification Check
Check for accidental whitespace bloat, unintended file renames, or modifications to untouched legacy code.

### Step 4: Error Left Behind Audit
Check browser console, terminal logs, and linter output. Confirm zero unhandled errors or warnings remain.

### Step 5: Self-Correction Pass
If any omission or discrepancy is detected, correct it immediately before user presentation.

### Step 6: Self-Review Certification
Certify in the final response that the self-audit passed with 100% verification evidence.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never declare completion without verified test evidence.
- Do NOT conceal unverified items; explicitly report known limitations.

---

## 6. Expected Deliverables & Artifacts
- Self-Review Audit Checklist with verified assertions.
- Clean git diff matching approved scope exactly.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 100% of approved plan requirements are verified in code.
- [ ] Git diff contains zero extraneous or accidental modifications.
- [ ] All linters and test suites report clean green status.

---

## 8. Error Recovery & Troubleshooting
- If self-review reveals an unfulfilled requirement, complete it before presenting work to the user.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/agent-self-review`. | `CUSTOM SKILL` |
| **Cursor** | Select `@agent-self-review` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code: 'Conduct an objective self-review of your changes.' | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `agent-self-review` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run agent-self-review`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt agent-self-review`. | `PROMPT FILE` |
| **Windsurf** | Activate `agent-self-review` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Definition of Done & AI Agent Rules)
