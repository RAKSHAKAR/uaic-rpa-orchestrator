---
name: regression-testing
description: >-
  Execute comprehensive regression suites to guarantee that existing supported features remain completely functional after changes.
---

# Regression Testing

## 1. Purpose & Overview
Executes full test suites across unit, integration, and E2E suites to detect unintended side-effects or regressions introduced by new features or bug fixes.

---

## 2. When to Use & When NOT to Use

### When to Use
- Following ANY code modification before declaring a task complete.
- Pre-release qualification passes.
- After upgrading dependencies or refactoring core architecture.

### When NOT to Use
- Initial exploratory spikes in throwaway scratch files.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Full repository test suites across backend, frontend, and shell scripts.

### Prerequisites
- Passing test baseline established prior to changes.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Backend Test Suite Execution
Run `backend\.venv\Scripts\pytest -q` across all 67 test suites. Confirm all 556 tests pass (with 2 pre-existing skips).

### Step 2: Backend E2E Suite Execution
Run `backend\.venv\Scripts\pytest e2e/backend -o pythonpath=backend -q`. Confirm 17/17 tests pass.

### Step 3: Frontend TypeScript Compile
Run `cd frontend && npx tsc --noEmit`. Confirm 0 TypeScript compilation errors.

### Step 4: Backend Linting Check
Run `cd backend && .venv\Scripts\ruff check app tests`. Confirm 0 errors.

### Step 5: PowerShell Syntax Check
Run `powershell -File scripts/check_ps1_syntax.ps1`. Confirm 0 syntax errors across all 13 scripts.

### Step 6: Regression Pass Log Synthesis
Document all test execution counts, pass rates, and execution times.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never declare completion if any pre-existing test begins failing.
- Do NOT modify existing test assertions merely to make failing tests pass.

---

## 6. Expected Deliverables & Artifacts
- Full Regression Test Execution Report.
- Verified green status across all test suites.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 556 backend unit/integration tests pass with 100% success rate.
- [ ] 17 backend E2E tests pass with 100% success rate.
- [ ] Frontend TypeScript compiles with 0 errors.
- [ ] PowerShell scripts pass with 0 syntax errors.

---

## 8. Error Recovery & Troubleshooting
- If any regression is detected, immediately diagnose the root cause and resolve it before proceeding.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/regression-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@regression-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `regression-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `regression-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run regression-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt regression-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `regression-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 7 (Test Commands)
- `scripts/check_ps1_syntax.ps1`
