---
name: unit-testing
description: >-
  Create and run isolated, high-speed unit tests with mocked external dependencies using pytest.
---

# Unit Testing

## 1. Purpose & Overview
Authors focused, deterministic unit tests validating pure business logic, fuzzy matching algorithms, date conversions, and data parsing in sub-millisecond execution times.

---

## 2. When to Use & When NOT to Use

### When to Use
- Implementing or modifying business logic functions, algorithms, or utility classes.
- Verifying date conversion, string normalization, or search count calculations.

### When NOT to Use
- Testing full database persistence or multi-service browser workflows.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target function/module to test and specification of expected inputs/outputs.

### Prerequisites
- Configured pytest test runner in `backend/.venv`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Test Case Identification
Enumerate happy path, boundary values, null inputs, invalid formats, and exception cases.

### Step 2: Mocking & Isolation Setup
Mock all external dependencies (network, database, filesystem) using `unittest.mock.MagicMock` or `AsyncMock`.

### Step 3: Test Implementation
Author pytest functions following Arrange-Act-Assert pattern in `backend/tests/`.

### Step 4: Parameterized Testing
Use `@pytest.mark.parametrize` for tabular test matrices (e.g. DualSearch/TripleSearch party combinations).

### Step 5: Test Execution & Assertion Verification
Execute tests using `.venv\Scripts\pytest <test_file> -q`. Confirm fast, green execution.

### Step 6: Coverage Verification
Verify that target functions achieve 100% branch coverage.


---

## 5. Safety Considerations & Guardrails
- Never make live network or database calls in unit tests.
- Do not assert on non-deterministic values (e.g. dynamic current time) without time-freezing fixtures.

---

## 6. Expected Deliverables & Artifacts
- Unit test file in `backend/tests/` with high assertion density.
- Test execution log demonstrating 100% pass rate.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All unit tests execute in under 100ms per test.
- [ ] Happy path, edge cases, and exception states are thoroughly asserted.
- [ ] Test suite passes cleanly with zero warnings or failures.

---

## 8. Error Recovery & Troubleshooting
- If tests fail due to mock leakage, verify mocks are cleanly reset between test runs using fixtures.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/unit-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@unit-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `unit-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `unit-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run unit-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt unit-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `unit-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/tests/test_v4_parity.py`
- `backend/tests/test_fuzzy_matching.py`
