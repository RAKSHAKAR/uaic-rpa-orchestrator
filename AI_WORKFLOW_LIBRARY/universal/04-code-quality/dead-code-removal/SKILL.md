---
name: dead-code-removal
description: >-
  Prove code is completely unreferenced before safely removing it from the repository.
---

# Dead Code Removal

## 1. Purpose & Overview
Enforces a strict, evidence-based verification protocol before deleting deprecated functions, unused variables, orphan components, or obsolete scripts.

---

## 2. When to Use & When NOT to Use

### When to Use
- Retiring deprecated API endpoints or legacy utility scripts.
- Cleaning up unused components after refactoring.

### When NOT to Use
- Speculative code deletions without exhaustive reference checking.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Candidate symbol or file path proposed for removal.
- Full repository search tools.

### Prerequisites
- Clean git working tree.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Static Reference Search
Search all source files, tests, configuration, scripts, and documentation for references to the candidate symbol.

### Step 2: Dynamic & Reflection Check
Verify symbol is not referenced dynamically (e.g. `getattr()`, Celery task name strings, dynamic router imports).

### Step 3: Test Suite Validation Pass
Run full test suite (`pytest`, `tsc`) before deletion to establish green baseline.

### Step 4: Removal Execution
Remove the unreferenced code cleanly.

### Step 5: Post-Removal Verification
Rerun full test suite to prove zero broken imports or side effects.

### Step 6: Documentation Update
Remove references from documentation and changelog.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never delete code merely because it looks unused; prove zero references with concrete evidence.
- Never remove protected directories (`anticaptcha-plugin_v0.83`, `.agents`).

---

## 6. Expected Deliverables & Artifacts
- Deleted code commit with reference verification evidence.
- Verification test report confirming zero regressions.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero references to the deleted symbol exist anywhere in the repository.
- [ ] All unit and integration tests pass without failures.
- [ ] Documentation updated to reflect removal.

---

## 8. Error Recovery & Troubleshooting
- If post-removal tests fail, immediately revert the deletion and investigate the hidden dependency.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/dead-code-removal`. | `CUSTOM SKILL` |
| **Cursor** | Select `@dead-code-removal` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `dead-code-removal`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `dead-code-removal` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run dead-code-removal`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt dead-code-removal`. | `PROMPT FILE` |
| **Windsurf** | Activate `dead-code-removal` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Preserve Existing Functionality)
