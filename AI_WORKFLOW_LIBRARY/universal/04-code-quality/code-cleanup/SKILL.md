---
name: code-cleanup
description: >-
  Remove unnecessary artifacts, orphan files, debug statements, and commented-out code only after confirming zero references.
---

# Code Cleanup

## 1. Purpose & Overview
Safely purges stale files, temporary debug scripts, unused import statements, and commented-out blocks, reducing codebase clutter and technical debt.

---

## 2. When to Use & When NOT to Use

### When to Use
- Following completion of a major feature implementation.
- Pre-release repository hygiene passes.
- Cleaning up temporary diagnostic dumps or scratch files.

### When NOT to Use
- Removing code whose usage or downstream dependency is unverified.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Candidate cleanup targets, repository search tools, and test suites.

### Prerequisites
- Git status clean or committed baseline.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Target Candidate Identification
Identify candidate cleanup items: temporary scripts in `scripts/`, orphan components, unused imports, or leftover `print()`/`console.log()` statements.

### Step 2: Reference & Dependency Verification
Search the entire codebase for references to each candidate symbol or file. Check dynamic imports, settings strings, and documentation links.

### Step 3: Protected Directory Exclusions
Verify that no candidates belong to protected directories (`anticaptcha-plugin_v0.83`, `.agents`).

### Step 4: Safe Deletion or Pruning
Remove confirmed dead files or strip debugging code.

### Step 5: Full Test Suite Verification
Execute backend pytest suites and frontend TypeScript compile to prove zero broken imports.

### Step 6: Cleanup Report
Document all deleted files and purged lines of dead code.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never delete files from `anticaptcha-plugin_v0.83` or `.agents`.
- Do NOT delete loose `.xlsx` or `.csv` files that serve as client demo or test fixtures without explicit approval.

---

## 6. Expected Deliverables & Artifacts
- Cleaned codebase with reduced clutter.
- Cleanup audit log detailing removed artifacts and verification evidence.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero broken import statements or runtime missing file errors.
- [ ] `ruff check` reports zero unused imports (`F401`).
- [ ] All unit and integration tests continue passing.

---

## 8. Error Recovery & Troubleshooting
- If a deletion causes test failures, restore the file immediately using `git checkout`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/code-cleanup`. | `CUSTOM SKILL` |
| **Cursor** | Select `@code-cleanup` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `code-cleanup`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `code-cleanup` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run code-cleanup`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt code-cleanup`. | `PROMPT FILE` |
| **Windsurf** | Activate `code-cleanup` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 2 (Repository Layout) & Section 8 (Must Not Do)
