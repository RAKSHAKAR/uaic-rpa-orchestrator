---
name: code-refactoring
description: >-
  Improve internal code structure, readability, and modularity without changing externally observable behavior.
---

# Code Refactoring

## 1. Purpose & Overview
Restructures complex, coupled, or duplicated code into clean, maintainable abstractions while preserving 100% behavioral parity backed by automated regression tests.

---

## 2. When to Use & When NOT to Use

### When to Use
- Simplifying oversized functions or classes (e.g. monolithic scraper classes).
- Eliminating duplicated logic across Florida and Texas scrapers.
- Improving modularity and testability of backend services.

### When NOT to Use
- Adding new functional capabilities (keep refactoring and feature additions in separate turns).
- When test suites are broken or missing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target code module, existing test suites, and refactoring objectives.

### Prerequisites
- 100% passing test baseline for the target module before touching code.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Baseline Test Pass Verification
Execute existing test suites to confirm green baseline: `pytest` and `npx tsc --noEmit`.

### Step 2: Refactoring Strategy Formulation
Identify specific code smells (Long Method, Feature Envy, Duplicate Code). Plan incremental transformations (Extract Method, Introduce Parameter Object).

### Step 3: Incremental Atomic Transformation
Apply transformations one at a time. Keep public interfaces and signatures identical or provide backward-compatibility wrappers.

### Step 4: Continuous Test Re-execution
Rerun the test suite after every single transformation to guarantee zero behavioral regressions.

### Step 5: Lint & Type Checking
Run `ruff check` and `tsc --noEmit` to ensure pristine code quality.

### Step 6: Refactoring Summary
Document structural improvements, eliminated lines of code, and verified test results.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never change external API contracts or database schemas during a pure refactoring task.
- Never proceed to the next refactoring step if tests are failing.

---

## 6. Expected Deliverables & Artifacts
- Refactored source code files with improved readability and cohesion.
- Regression test report proving 100% behavioral equivalence.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All pre-existing tests pass with zero modifications to test assertions.
- [ ] Cyclomatic complexity and function line counts are reduced.
- [ ] Zero new linting or type-checking errors introduced.

---

## 8. Error Recovery & Troubleshooting
- If a refactoring step breaks behavioral tests, immediately revert the step via git and choose an alternative transformation.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/code-refactoring`. | `CUSTOM SKILL` |
| **Cursor** | Select `@code-refactoring` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `code-refactoring`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `code-refactoring` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run code-refactoring`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt code-refactoring`. | `PROMPT FILE` |
| **Windsurf** | Activate `code-refactoring` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/base.py`
- `AGENTS.md` - Section 8
