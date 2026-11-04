---
name: error-reproduction
description: >-
  Create a minimal, reliable, automated reproduction test case before attempting to implement any code fix.
---

# Error Reproduction

## 1. Purpose & Overview
Constructs minimal, deterministic reproduction scripts that reliably trigger reported bugs in isolation, providing a concrete verification baseline for fixes.

---

## 2. When to Use & When NOT to Use

### When to Use
- Prior to modifying code to fix any reported bug or unexpected failure.
- Investigating intermittent or hard-to-reproduce edge cases.

### When NOT to Use
- When a deterministic failing test already exists in the test suite.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Bug report symptoms, input parameters, and environment state.

### Prerequisites
- Access to pytest testing framework or scratch script runner.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Minimal Input Isolation
Strip away irrelevant inputs. Determine the minimal subset of data that reproduces the defect.

### Step 2: Reproduction Script Authoring
Write a minimal, isolated test in `backend/tests/` or scratch script in `scripts/` (e.g. `scripts/diag_claims.py`).

### Step 3: Deterministic Failure Verification
Execute the reproduction script. Verify it fails with the exact reported error and traceback.

### Step 4: State Isolation Check
Ensure the test does not depend on uncommitted local data or transient external conditions.

### Step 5: Baseline Failure Recording
Record the failing assertion or exception trace as the benchmark for successful fix verification.


---

## 5. Safety Considerations & Guardrails
- Do NOT modify application source code until the reproduction test is written and confirmed failing.
- Ensure reproduction scripts run against test databases.

---

## 6. Expected Deliverables & Artifacts
- Automated Reproduction Test Case in `backend/tests/`.
- Baseline failure execution log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Reproduction test fails reliably with 100% determinism under pre-fix code.
- [ ] Test contains zero extraneous dependencies or bloated setup logic.
- [ ] Test passes cleanly once the fix is applied.

---

## 8. Error Recovery & Troubleshooting
- If a defect cannot be reproduced locally, check for differences in environment variables, Python versions, or database fixtures.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/error-reproduction`. | `CUSTOM SKILL` |
| **Cursor** | Select `@error-reproduction` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `error-reproduction`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `error-reproduction` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run error-reproduction`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt error-reproduction`. | `PROMPT FILE` |
| **Windsurf** | Activate `error-reproduction` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/tests/`
- `scripts/`
