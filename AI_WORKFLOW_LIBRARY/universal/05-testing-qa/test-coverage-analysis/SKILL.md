---
name: test-coverage-analysis
description: >-
  Find untested critical business paths, state transitions, and exception handlers; optimize for risk coverage, not mere percentage.
---

# Test Coverage Analysis

## 1. Purpose & Overview
Analyzes test execution coverage across critical business modules (fuzzy engine, state machine, Guidewire serializer), identifying blind spots where defects could escape to production.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pre-release quality audits.
- Auditing legacy modules before refactoring.
- Evaluating test suite thoroughness after major feature additions.

### When NOT to Use
- Chasing 100% code coverage on trivial boilerplate or auto-generated code.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `pytest-cov` coverage reports and repository source files.

### Prerequisites
- `pytest-cov` installed in `backend/.venv`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Coverage Instrumentation Execution
Execute backend test suite with coverage: `pytest --cov=app --cov-report=term-missing`.

### Step 2: Critical Path Coverage Audit
Inspect coverage specifically on high-risk modules: `fuzzy_engine.py`, `guidewire_client.py`, `queue_runner.py`, and `base.py`.

### Step 3: Branch & Exception Blind Spot Discovery
Identify unexecuted exception handlers (e.g. `CaptchaResolutionError`), fallback cascades, and retry branches.

### Step 4: Targeted Test Authoring
Write focused unit tests covering the discovered untested branches and edge cases.

### Step 5: Re-run & Verification
Re-run coverage instrumentation. Confirm critical business modules achieve $\ge 90\%$ branch coverage.

### Step 6: Coverage Report Synthesis
Publish the Test Coverage Audit Report in `docs/`.


---

## 5. Safety Considerations & Guardrails
- Do NOT write meaningless assertion-free tests merely to inflate coverage percentages.
- Focus coverage efforts on high-risk business logic and data persistence.

---

## 6. Expected Deliverables & Artifacts
- Test Coverage & Risk Gap Analysis Report.
- New targeted unit test cases covering previously untested branches.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Core business services (`fuzzy_engine`, `guidewire_client`) maintain $\ge 90\%$ branch coverage.
- [ ] All primary exception handling branches are verified by tests.
- [ ] Total test pass rate remains 100%.

---

## 8. Error Recovery & Troubleshooting
- If certain code branches cannot be triggered in unit tests, refactor to dependency-inject the error condition.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/test-coverage-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@test-coverage-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `test-coverage-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `test-coverage-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run test-coverage-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt test-coverage-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `test-coverage-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/tests/`
- `AGENTS.md` - Section 7
