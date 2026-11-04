---
name: code-review
description: >-
  Review code changes for correctness, maintainability, security, performance, test coverage, and project conventions.
---

# Code Review

## 1. Purpose & Overview
Conducts a rigorous, objective code review against repository standards, detecting subtle logic flaws, unhandled exceptions, performance bottlenecks, and security vulnerabilities before merging.

---

## 2. When to Use & When NOT to Use

### When to Use
- Reviewing pull requests or local working tree diffs before committing.
- Auditing complex algorithmic changes or security-critical code.

### When NOT to Use
- Trivial documentation typo corrections.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Git diff or modified file paths, target requirements, and repository coding standards (`AGENTS.md`).

### Prerequisites
- Clean working tree or specific commit range to review.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Diff Scope & Context Inspection
Inspect git diff (`git diff HEAD~1` or working tree). Check which files were added, modified, or removed.

### Step 2: Correctness & Logic Verification
Verify that the code satisfies the stated requirements without off-by-one errors, unhandled nulls, or broken invariants.

### Step 3: Security & Data Protection Audit
Check for SQL injection, unescaped parameters, leaked credentials, hardcoded secrets, and unsafe deserialization.

### Step 4: Performance & Resource Management
Identify N+1 database queries, unclosed async sessions, memory leaks, unindexed query filters, or unbounded loops.

### Step 5: Style, Standards & Test Coverage Audit
Verify adherence to project formatting (Ruff, ESLint), TypeScript strictness, and automated test coverage.

### Step 6: Review Summary & Findings Synthesis
Produce a structured review report categorizing findings into: Critical Blockers, Improvements, and Commendations.


---

## 5. Safety Considerations & Guardrails
- Never approve code that breaks pre-existing unit or integration tests.
- Never overlook hardcoded API tokens or unmasked credentials.

---

## 6. Expected Deliverables & Artifacts
- Structured Code Review Report with line-specific findings and recommendations.
- Approved or Blocked status recommendation.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All changed files are reviewed line by line.
- [ ] Security, performance, and correctness issues are identified with code snippets.
- [ ] Review explicitly confirms whether automated test coverage is adequate.

---

## 8. Error Recovery & Troubleshooting
- If review findings reveal architectural defects, request redesign before further coding.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/code-review`. | `CUSTOM SKILL` |
| **Cursor** | Select `@code-review` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `code-review`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `code-review` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run code-review`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt code-review`. | `PROMPT FILE` |
| **Windsurf** | Activate `code-review` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Definition of Done & Must Do / Must Not Do)
- `ruff.toml`
