---
name: test-strategy
description: >-
  Define multi-level testing strategies, scope, test environments, mock fixtures, and exit gates across the pyramid.
---

# Test Strategy

## 1. Purpose & Overview
Establishes a cohesive testing strategy balancing fast unit tests, integrated service tests, and end-to-end browser verification, ensuring high defect detection at minimal CI cost.

---

## 2. When to Use & When NOT to Use

### When to Use
- Initiating a new feature stream, subsystem, or platform migration.
- Auditing and upgrading project test infrastructure.

### When NOT to Use
- Writing a single unit test function.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- System architecture, critical risk paths, and SLA requirements.

### Prerequisites
- Completed `architecture-analysis`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Test Pyramid Partitioning
Allocate testing efforts: 70% Unit Tests (fast, isolated), 20% Integration Tests (database, API, queues), 10% E2E Browser Tests (Playwright user journeys).

### Step 2: Environment & Fixture Strategy
Define test fixtures (`conftest.py`), SQLite in-memory databases, and mock strategies for external services (Guidewire, SMTP).

### Step 3: Gate Criteria Formulation
Establish non-negotiable PR gates: 100% test pass rate, 0 lint errors, and 0 TypeScript errors.

### Step 4: Flaky Test Prevention Policy
Establish policies for deterministic tests: fixed clocks, explicit locators, and zero arbitrary sleep statements.

### Step 5: Test Strategy Document Synthesis
Publish the formal Test Strategy Document in `docs/`.


---

## 5. Safety Considerations & Guardrails
- Never rely exclusively on E2E tests for logic that can be tested in fast unit tests.
- Never allow flaky tests to be permanently ignored.

---

## 6. Expected Deliverables & Artifacts
- Formal Test Strategy Document in `docs/`.
- Test Pyramid Coverage Plan.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Test levels, tooling, and responsibilities are explicitly defined.
- [ ] Mocking boundaries for third-party systems are established.
- [ ] Automated quality gates are documented with exact commands.

---

## 8. Error Recovery & Troubleshooting
- If CI execution times become prohibitive, shift slow integration tests to nightly runs or parallelize.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/test-strategy`. | `CUSTOM SKILL` |
| **Cursor** | Select `@test-strategy` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `test-strategy`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `test-strategy` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run test-strategy`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt test-strategy`. | `PROMPT FILE` |
| **Windsurf** | Activate `test-strategy` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 7 (Test Commands)
- `backend/tests/conftest.py`
