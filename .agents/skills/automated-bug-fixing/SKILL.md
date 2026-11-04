---
name: automated-bug-fixing
description: >-
  Implement bounded, surgical bug fixes and execute full regression test suites proving complete resolution.
---

# Automated Bug Fixing

## 1. Purpose & Overview
Guides the surgical implementation of bug fixes, ensuring fixes address root causes with minimal blast radius and are verified by both the reproduction test and the full regression suite.

---

## 2. When to Use & When NOT to Use

### When to Use
- Implementing a fix following successful diagnosis and reproduction test authoring.
- Resolving localized defects across API handlers, services, or UI components.

### When NOT to Use
- Attempting to fix bugs before diagnosing root cause or authoring a reproduction test.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Confirmed root cause, failing reproduction test, and target source files.

### Prerequisites
- Completed `diagnose-issue` and `error-reproduction`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Failing Test Baseline Confirmation
Run the reproduction test to confirm it currently fails: `pytest <repro_test> -q`.

### Step 2: Surgical Fix Implementation
Apply minimal, focused code modifications resolving the underlying defect. Avoid unrelated refactoring.

### Step 3: Reproduction Test Pass Verification
Rerun the reproduction test. Confirm it now passes cleanly: `pytest <repro_test> -q`.

### Step 4: Full Regression Test Suite Pass
Run the entire backend test suite: `pytest -q`. Confirm 556/556 tests pass with 0 regressions.

### Step 5: Frontend & Linting Pass
Run `npx tsc --noEmit` and `ruff check app tests`.

### Step 6: Fix Summary & Verification Documentation
Document the bug fix, root cause, changed lines, and passing test evidence in `docs/`.


---

## 5. Safety Considerations & Guardrails
- Never introduce broad, speculative refactoring in a bug fix task.
- Never bypass regression tests before declaring the bug fixed.

---

## 6. Expected Deliverables & Artifacts
- Surgically patched source code files.
- Passing reproduction test and full regression test log.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Reproduction test transitions from Red (Failing) to Green (Passing).
- [ ] Full regression suite passes with 100% success rate.
- [ ] Zero new linting or type-checking errors introduced.

---

## 8. Error Recovery & Troubleshooting
- If the fix causes regressions in adjacent test suites, revert the fix and re-analyze the blast radius.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/automated-bug-fixing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@automated-bug-fixing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `automated-bug-fixing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `automated-bug-fixing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run automated-bug-fixing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt automated-bug-fixing`. | `PROMPT FILE` |
| **Windsurf** | Activate `automated-bug-fixing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Definition of Done)
- `docs/` - Historical Fix Plans
